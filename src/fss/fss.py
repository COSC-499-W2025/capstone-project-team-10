import csv
import os
from datetime import date, datetime
from pathlib import Path
import re
from typing import Dict

import src.fas.fas as fas
import src.log.log as log
import src.param.param as param
from src.fss.fss_helper import file_type_check, time_check
from src.fas.fas import get_last_modified_time


class FSS_Search:
    def __init__(
        self,
        input_path,
        excluded_path: set = set(),
        file_types: set = set(),
        time_lower_bound: datetime | None = None,
        time_upper_bound: datetime | None = None,
    ):
        self.input_path = input_path
        self.excluded_path = excluded_path
        self.file_types = file_types
        self.time_lower_bound = time_lower_bound
        self.time_upper_bound = time_upper_bound

def load_cache() -> Dict[str, str]:
    # Loads and reads the cache file
    # It returns a dictionary of  [absolute file path: (modified time, size)]
    cache: Dict[str, str]  = {}
    
    logs_folder = Path(param.result_log_folder_path)
    if not logs_folder.exists():
        return cache
    
    pattern = re.compile(param.log_file_naming_regex)
    latest_log = None
    latest_idx = -1

    for log_file in logs_folder.iterdir():
        if not log_file.is_file():
            continue
        match = pattern.match(log_file.name)
        if not match:
            continue

        try:
            index = int(match.group(1))
        except ValueError:
            continue

        if index > latest_idx:
            latest_log = log_file
            latest_idx = index

    if latest_log is None:
        return cache
    
    with latest_log.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            file_path = row.get("File path analyzed")
            last_modified = row.get("Last modified")
            if file_path and last_modified:
                cache[file_path] = last_modified
    return cache

def should_process(path, cache) -> bool:
    last_modified_cached = cache.get(path)
    if last_modified_cached is None:
        return True
    return get_last_modified_time(path) != last_modified_cached

def search(search: FSS_Search):
    exclude_flag = True
    num_of_files_scanned = 0
    excluded_set = set()
    cache = load_cache()

    for cached_path in cache.keys():
        if not should_process(cached_path, cache):
            excluded_set.add(os.path.abspath(cached_path))

    if not search.excluded_path and not excluded_set:
        # If there is not included exclusion, the flag will be set to false to skip comparisons
        exclude_flag = False

    if not os.path.exists(search.input_path):
        # invalid returns -1
        return -1

    search.input_path = os.path.abspath(search.input_path)

    if exclude_flag:
        # ensures that the excluded paths input is a set
        for e_path in search.excluded_path:
            e_path = os.path.abspath(e_path)
            excluded_set.add(e_path)

            # if exclusion includes a dir, it will add all files within the dir to exclusion
            if os.path.isdir(e_path):
                for root, dirs, files in os.walk(e_path):
                    for file in files:
                        excluded_set.add(os.path.join(root, file))
        search.excluded_path = excluded_set

    if os.path.isfile(search.input_path):
        if not search.excluded_path:
            # TODO add in FAS and return value, pass in file and set of repo paths for grouping
            # single file with no exclusion
            return 1
        elif search.input_path not in search.excluded_path:
            # TODO add in FAS and return value, pass in file and set of repo paths for grouping
            # single file accounting for exclusion
            return 1
        else:
            return 0

    for root, dirs, files in os.walk(search.input_path, topdown=True):
        # Remove excluded dirs
        dirs[:] = [d for d in dirs if os.path.join(root, d) not in search.excluded_path]

        for dir in dirs[:]:
            dir_path = os.path.join(root, dir)
            if exclude_flag and dir_path in search.excluded_path:
                continue
            if dir == ".git":
                git_file_result: fas.FileAnalysis | None = fas.run_fas(dir_path)
                print(f"Scanning .git directory at: {dir_path}")
                if git_file_result:
                    log.write(git_file_result)
                    num_of_files_scanned += 1
                dirs.remove(dir)

        for file in files:
            if file.startswith(".") and file != ".gitignore":
                continue  # Skip hidden files
            file_path = os.path.join(root, file)
            # Check conditions
            if exclude_flag and file_path in search.excluded_path:
                continue
            if search.file_types and not file_type_check(file_path, search.file_types):
                continue

            if (search.time_lower_bound or search.time_upper_bound) and not time_check(
                list([search.time_lower_bound, search.time_upper_bound]),
                Path(file_path),
                "create",
            ):
                continue

            # TODO add in FAS and return value, pass in file and set of repo paths for grouping
            # Given no exclusion this is where details about scanned files can be extracted.
            file_result: fas.FileAnalysis | None = fas.run_fas(file_path)
            # Pass file result to log module for logging
            if file_result:
                log.write(file_result)
                # Pass file result to GUI/CLI if necessary
            num_of_files_scanned += 1

    return num_of_files_scanned
