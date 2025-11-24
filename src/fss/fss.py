import os
import re
from pathlib import Path
import csv
from src.fss.fss_helper import *
from typing import Dict, Tuple
from src.param import param
from src.fas.fas import get_last_modified_time

# User's settings for modification + creation time - for now, dummies variable
# It should be the fss intaker responsibility to control if these values are valid (lower << upper, only 2 values in a list, etc.)
create_time_crit = [None, None]
mod_time_crit = [None, None]

# Cache Helpers

def load_cache() -> Dict[str, str]:
    # Loads and reads the cache file
    # It returns a dictionary of  [absolute file path: (modified time, size)]
    cache: Dict[str, str]  = {}

    logs_folder = Path(param.result_log_folder_path)
    if not logs_folder.exists():
        return cache
    
    pattern = re.compile(param.log_file_naming_regex)

    for log_file in logs_folder.iterdir():
        if not log_file.is_file():
            continue
        if not pattern.match(log_file.name):
            continue

    with log_file.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            file_path = row.get("File path analyzed")
            last_modified = row.get("Last modified")
            if file_path and last_modified:
                cache[file_path] = last_modified
    return cache

# Main search

def search(input_path, excluded_path, clean: bool = False):

    exclude_flag = True
    num_of_files_scanned = 0

    if not excluded_path:
        # If there is not included exclusion, the flag will be set to false to skip comparisons
        exclude_flag = False

    if not os.path.exists(input_path):
        # invalid returns -1
        return -1

    input_path = os.path.abspath(input_path)

    if exclude_flag:
        # ensures that the excluded paths input is a set
        if isinstance(excluded_path, str):
            excluded_path = {excluded_path}
        else:
            excluded_path = set(excluded_path)

        excluded_set = set()
        for e_path in excluded_path:
            e_path = os.path.abspath(e_path)
            excluded_set.add(e_path)

            # if exclusion includes a dir, it will add all files within the dir to exclusion
            if os.path.isdir(e_path):
                for root, dirs, files in os.walk(e_path):
                    for file in files:
                        excluded_set.add(os.path.join(root, file))

        excluded_path = excluded_set

    prev_cache: Dict[str, str] = {} if clean else load_cache()

    def should_process(file_path_abs: str) -> bool:
        # Checks if file should be processed or not
        # by checking if signature matches with the one in the cache (if the file is in cache)
        # or if clean flag has been passed
        if not os.path.isfile(file_path_abs):
            return False
        if clean:
            return True
        
        current_last_modified = get_last_modified_time(file_path_abs)
        last_modified_logged = prev_cache.get(file_path_abs)

        return last_modified_logged != current_last_modified

    if os.path.isfile(input_path):
        if not excluded_path or input_path not in excluded_path:
            #single file with no exclusion
            if should_process(input_path):
                #This is where specifics of files can be extracted.
                return 1
            else:
                return 0
        else:
            return 0

    for root, dirs, files in os.walk(input_path, topdown=True):
        for file in files:
            if file.startswith(".") and file != ".gitignore":
                continue  # Skip hidden files
            file_path = os.path.join(root, file)
            file_path = os.path.abspath(file_path)
            print(file_path)

            if exclude_flag:
                if file_path not in excluded_path and time_check(create_time_crit, file_path, "create") and time_check(mod_time_crit, file_path, "mod"): # Added time checkers to abide criteria here
                    if should_process(file_path):
                    #This is where specifics of files can be extracted.
                        num_of_files_scanned += 1
            else:
                if should_process(file_path):
                #Given no exclusion this is where details about scanned files can be extracted.
                    num_of_files_scanned += 1
    return num_of_files_scanned
