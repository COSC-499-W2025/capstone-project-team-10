from pathlib import Path
import csv
import re

import src.param.param as param
from src.fas.fas import FileAnalysis

# Newest Log is always max count after maximum logs are being stored
current_log_file: str = ""


# resumes the last log file used
# This is the default, we will want to force open a log file when --clean is used
def resume_log_file() -> None:
    global current_log_file

    current_logs = {}
    current_log_file = ""

    # Set to max int value
    newest_log_number: int = -1
    oldest_log_number: int = param.log_max_count + 1
    if Path(param.result_log_folder_path).exists():
        for file in Path(param.result_log_folder_path).iterdir():
            if file.is_file():
                log_number: int = int(
                    re.search(param.log_file_naming_regex, file.name).group(1)
                )
                print(f"Found log file: {file.name} with number: {log_number}")
                if log_number > newest_log_number:
                    newest_log_number = log_number
                if log_number < oldest_log_number:
                    oldest_log_number = log_number

                current_logs[log_number] = file.absolute()
        if newest_log_number != -1:
            print(f"Resuming log file: {newest_log_number}.log")
            current_log_file = str(
                Path(param.result_log_folder_path) / f"{newest_log_number}.log"
            )
        else:
            open_log_file()
    else:
        open_log_file()


# Oldest log file is the
def open_log_file() -> None:
    global current_log_file

    current_logs = {}
    current_log_file = ""
    # Set to max int value
    newest_log_number: int = -1
    oldest_log_number: int = param.log_max_count + 1
    Path(param.result_log_folder_path).mkdir(parents=True, exist_ok=True)
    for file in Path(param.result_log_folder_path).iterdir():
        if file.is_file:
            log_number: int = int(
                re.search(param.log_file_naming_regex, file.name).group(1)
            )
            if log_number > newest_log_number:
                newest_log_number = log_number
            if log_number < oldest_log_number:
                oldest_log_number = log_number

            current_logs[log_number] = file.absolute()

    if len(current_logs) >= param.log_max_count:
        # Delete oldest log file until we are under the max
        while len(current_logs) >= param.log_max_count:
            try:
                Path(current_logs[oldest_log_number]).unlink()
            except Exception as e:
                print(f"Log file sequence corrupted, clearing log directory: {e}")
                # Fallback: delete all files in the directory
                for file in Path(param.result_log_folder_path).iterdir():
                    if file.is_file():
                        try:
                            file.unlink()
                            print(f"{file} deleted.")
                        except Exception as err:
                            print(f"Failed to delete {file}: {err}")
                # Reset log tracking
                current_logs.clear()
                newest_log_number = -1
                break

            current_logs.pop(oldest_log_number)
            # add 1 to oldest log number for next oldest log
            oldest_log_number += 1

    # Create new log file with index 0
    # from pathlib import Path

    current_log_file = str(
        Path(param.result_log_folder_path) / f"{(newest_log_number + 1)}.log"
    )

    # create the log file, overwriting if it exists
    with open(current_log_file, "w") as log_file:
        writer = csv.writer(log_file)
        writer.writerows(
            [
                [
                    "File path analyzed",
                    "File name",
                    "File type",
                    "Last modified",
                    "Created time",
                    "Extra data",
                ]
            ]
        )


def write(fileAnalysis: FileAnalysis) -> None:
    global current_log_file
    if current_log_file == "":
        resume_log_file()
    with open(current_log_file, "a") as log_file:
        print("Logging to filepath" + current_log_file)
        writer = csv.writer(log_file)
        writer.writerow(
            [
                fileAnalysis.file_path,
                fileAnalysis.file_name,
                fileAnalysis.file_type,
                fileAnalysis.last_modified,
                fileAnalysis.created_time,
                fileAnalysis.extra_data,
            ]
        )
