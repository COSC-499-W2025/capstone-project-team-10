import os
from datetime import date, datetime

import src.fas.fas as fas
import src.log.log as log
from src.fss.fss_helper import file_type_check, time_check

# User's settings for modification + creation time - for now, dummies variable
# It should be the fss intaker responsibility to control if these values are valid (lower << upper, only 2 values in a list, etc.)
create_time_crit = [None, None]
mod_time_crit = [None, None]


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

    if not search.excluded_path:
        # If there is not included exclusion, the flag will be set to false to skip comparisons
        exclude_flag = False

    if not os.path.exists(search.input_path):
        # invalid returns -1
        return -1

    search.input_path = os.path.abspath(search.input_path)

    if exclude_flag:
        # ensures that the excluded paths input is a set
        excluded_set = set()
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
        for file in files:
            if file.startswith(".") and file != ".gitignore":
                continue  # Skip hidden files
            file_path = os.path.join(root, file)
            print(file_path)
            if exclude_flag and file_path in search.excluded_path:
                # TODO add in FAS and return value, pass in file and set of repo paths for grouping
                # This is where specifics of files can be extracted.
                continue
            if not file_type_check(file_path, search.file_types):
                continue

            if not time_check(
                [search.time_lower_bound, search.time_upper_bound],
                file_path,
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
