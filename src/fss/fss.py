import csv
import os
from datetime import date, datetime
from pathlib import Path
import zipfile
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


def search(search_params: FSS_Search):
    exclude_flag = True
    num_of_files_scanned = 0
    excluded_set = set()

    if not os.path.exists(search_params.input_path):
        # invalid returns -1
        return -1

    search_params.input_path = os.path.abspath(search_params.input_path)

    # Checks if file path is a zip folder and recursively calls search with the extracted folder
    if zipfile.is_zipfile(search_params.input_path):
        from src.zip.zip_app import extract_zip
        extracted_path = extract_zip(search_params.input_path)
        if not extracted_path:
            return -1
        print(f"File unzipped at: {extracted_path}")
        temp_search = FSS_Search(
            input_path=str(extracted_path),
            excluded_path=search_params.excluded_path,
            file_types=search_params.file_types,
            time_lower_bound=search_params.time_lower_bound,
            time_upper_bound=search_params.time_upper_bound,
        )
        return search(temp_search)

    if exclude_flag:
        # ensures that the excluded paths input is a set
        if isinstance(search_params.excluded_path, set):
            for e_path in search_params.excluded_path:
                e_path = os.path.abspath(e_path)
                excluded_set.add(e_path)

                # if exclusion includes a dir, it will add all files within the dir to exclusion
                if os.path.isdir(e_path):
                    for root, dirs, files in os.walk(e_path):
                        for file in files:
                            excluded_set.add(os.path.join(root, file))
            search_params.excluded_path = excluded_set
        else:
            exclude_flag = False
            search_params.excluded_path = set()

    # Scan files from the previous log
    current_log: Path = Path(log.current_log_file)
    if current_log.exists() and current_log.is_file():
        log_entries = []
        with open(current_log, "r", encoding="utf-8") as log_file:
            reader = csv.reader(log_file)
            next(reader)  # Skip header
            for file_details in reader:
                log_entries.append(file_details)
                
        # Update log details after closing file
        for file_details in log_entries:
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
                if file_analysis.file_path in search_params.excluded_path:
                    continue
                if datetime.fromtimestamp(
                    file.stat().st_mtime
                ) <= datetime.fromisoformat(file_analysis.last_modified):
                    exclude_flag = True
                    search_params.excluded_path.add(file_analysis.file_path)
                    continue
                print(f"Scanning previously found file: {file_analysis.file_path}")
                new_file_result = fas.run_fas(file_analysis.file_path)
                if new_file_result:
                    num_of_files_scanned += 1
                    log.update(new_file_result)
                    exclude_flag = True
                    search_params.excluded_path.add(file_analysis.file_path)

    if os.path.isfile(search_params.input_path):
        if not search_params.excluded_path:
            # TODO add in FAS and return value, pass in file and set of repo paths for grouping
            # single file with no exclusion
            return 1
        elif search_params.input_path not in search_params.excluded_path:
            # TODO add in FAS and return value, pass in file and set of repo paths for grouping
            # single file accounting for exclusion
            return 1
        else:
            return 0

    for root, dirs, files in os.walk(search_params.input_path, topdown=True):
        root_abs = os.path.abspath(root)

        # Skip this directory entirely if it is under an excluded path
        if any(root_abs.startswith(excluded) for excluded in excluded_set):
            continue

        # Remove dirs that are under excluded paths
        dirs[:] = [d for d in dirs if not any(os.path.abspath(os.path.join(root_abs, d)).startswith(excluded) for excluded in excluded_set)]

        # Remove files under excluded paths
        files[:] = [f for f in files if not any(os.path.abspath(os.path.join(root_abs, f)).startswith(excluded) for excluded in excluded_set)]

        # Now process remaining files
        for file in files:
            if file.startswith(".") and file != ".gitignore":
                continue
            file_path = os.path.join(root_abs, file)

            if search_params.file_types and not file_type_check(file_path, search_params.file_types):
                continue

            if (search_params.time_lower_bound or search_params.time_upper_bound) and not time_check(
                [search_params.time_lower_bound, search_params.time_upper_bound],
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
