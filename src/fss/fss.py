import csv
import os
from datetime import date, datetime
from pathlib import Path

import src.fas.fas as fas
import src.log.log as log
from src.fss.fss_helper import file_type_check, time_check


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


def search(search: FSS_Search):
    exclude_flag = True
    num_of_files_scanned = 0
    excluded_set = set()

    if not os.path.exists(search.input_path):
        # invalid returns -1
        return -1

    search.input_path = os.path.abspath(search.input_path)

    if exclude_flag:
        # ensures that the excluded paths input is a set
        if isinstance(search.excluded_path, set):
            for e_path in search.excluded_path:
                e_path = os.path.abspath(e_path)
                excluded_set.add(e_path)

                # if exclusion includes a dir, it will add all files within the dir to exclusion
                if os.path.isdir(e_path):
                    for root, dirs, files in os.walk(e_path):
                        for file in files:
                            excluded_set.add(os.path.join(root, file))
            search.excluded_path = excluded_set
        else:
            exclude_flag = False
            search.excluded_path = set()

    # Scan files from the previous log
    current_log: Path = Path(log.current_log_file)
    if current_log.exists() and current_log.is_file():
        with open(current_log, "r", encoding="utf-8") as log_file:
            reader = csv.reader(log_file)
            next(reader)  # Skip header
            for file_details in reader:
                file_analysis: fas.FileAnalysis = fas.FileAnalysis(
                    file_details[0],
                    file_details[1],
                    file_details[2],
                    file_details[3],
                    file_details[4],
                    file_details[5],
                    float(file_details[6].strip()),
                )
                file = Path(file_analysis.file_path)
                if file.exists():
                    if file_analysis.file_path in search.excluded_path:
                        continue
                    if datetime.fromtimestamp(
                        file.stat().st_mtime
                    ) <= datetime.fromisoformat(file_analysis.last_modified):
                        exclude_flag = True
                        search.excluded_path.add(file_analysis.file_path)
                        continue
                    print(f"Scanning previously found file: {file_analysis.file_path}")
                    new_file_result = fas.run_fas(file_analysis.file_path)
                    if new_file_result:
                        num_of_files_scanned += 1
                        log.update(new_file_result)
                        exclude_flag = True
                        search.excluded_path.add(file_analysis.file_path)

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
