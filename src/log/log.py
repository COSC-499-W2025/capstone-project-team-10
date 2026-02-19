import csv
import re
import threading
import time
from pathlib import Path
from typing import Optional

import src.param.param as param
from src.fas.fas import FileAnalysis

# TODO: if multithreading is needed add locks around file write operations

# Newest Log is always max count after maximum logs are being stored
current_log_file: str = ""
log_lock = threading.RLock()


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
                match = re.search(param.log_file_naming_regex, file.name)
                if not match:
                    continue
                log_number: int = int(match.group(1))
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
            param.set("logging.current_log_file", current_log_file)
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
            match = re.search(param.log_file_naming_regex, file.name)
            if not match:
                continue
            log_number: int = int(match.group(1))
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
    with open(current_log_file, "w", encoding="utf-8", newline="") as log_file:
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
                    "Importance",
                    "Customized",
                    "Project id",
                    "File hash",
                ]
            ]
        )
        param.set("logging.current_log_file", current_log_file)


def write(fileAnalysis: FileAnalysis) -> None:
    global current_log_file
    if current_log_file == "" or not Path(current_log_file).exists():
        resume_log_file()
    with (
        log_lock,
        open(current_log_file, "a", encoding="utf-8", newline="") as log_file,
    ):
        writer = csv.writer(log_file)
        writer.writerow(
            [
                fileAnalysis.file_path,
                fileAnalysis.file_name,
                fileAnalysis.file_type,
                fileAnalysis.last_modified,
                fileAnalysis.created_time,
                fileAnalysis.extra_data,
                fileAnalysis.importance,
                fileAnalysis.customized,
                fileAnalysis.project_id,
                fileAnalysis.file_hash,
            ]
        )


# This can be optimized by changing how logs are stored, say as a database or serialized object.
# But because our log files will be relatively small compared to the total number of files on a system, this should be sufficient for now.
def update(fileAnalysis: FileAnalysis, forceUpdate: bool = False) -> None:
    global current_log_file
    if current_log_file == "" or not Path(current_log_file).exists():
        resume_log_file()
    temp_path = str(Path(param.result_log_folder_path) / "log.tmp")
    updated = False

    with log_lock:
        with (
            open(current_log_file, "r", newline="") as current_log,
            open(temp_path, "w", newline="") as temp_log,
        ):
            reader = csv.reader(current_log)
            writer = csv.writer(temp_log)

            header = next(reader)
            writer.writerow(header)

            for row in reader:
                if row[0] == fileAnalysis.file_path:
                    # Write updated row
                    if row[7] == "False" or forceUpdate:
                        writer.writerow(
                            [
                                fileAnalysis.file_path,
                                fileAnalysis.file_name,
                                fileAnalysis.file_type,
                                fileAnalysis.last_modified,
                                fileAnalysis.created_time,
                                fileAnalysis.extra_data,
                                fileAnalysis.importance,
                                fileAnalysis.customized,
                                fileAnalysis.project_id,
                                fileAnalysis.file_hash,
                            ]
                        )
                    else:
                        # Keep original row if customized is True and not forcing update
                        writer.writerow(row)
                    updated = True
                else:
                    # Write original row
                    writer.writerow(row)

        if not updated:
            # remove temp file if no update was made
            Path(temp_path).unlink()
            # write the line to file if no update can be made
            write(fileAnalysis)
        else:
            # Replace original file with updated file
            Path(temp_path).replace(current_log_file)


def follow_log(
    file_path: str | None = None,
    include_header: bool = False,
    poll_interval: float = 0.5,
    stop_signal: str = "!close!",
):
    """
    Generator that yields log lines as they appear in the file.
    Polls the file and waits for new lines to be added.
    Stops when a line containing stop_signal is encountered.
    """
    global current_log_file

    if file_path is None:
        if current_log_file == "" or not Path(current_log_file).exists():
            resume_log_file()
        file_path = current_log_file

    with open(file_path, "r", encoding="utf-8", newline="") as f:
        if not include_header:
            f.readline()  # skip header line

        while True:
            line = ""
            with log_lock:
                line = f.readline()
            if line:
                stripped = line.rstrip("\r\n")
                yield stripped
                if stop_signal in stripped:
                    break
            else:
                time.sleep(poll_interval)


def _get_all_log_files() -> list[Path]:
    """
    Returns a list of all log files in the log folder,
    matched by the log file naming regex.
    """
    log_folder = Path(param.result_log_folder_path)
    if not log_folder.exists():
        return []

    log_files = []
    for file in log_folder.iterdir():
        if file.is_file():
            match = re.search(param.log_file_naming_regex, file.name)
            if match:
                log_files.append(file)
    return log_files


def find_existing_analysis(file_hash: str) -> Optional[FileAnalysis]:
    """
    Searches all log files for a row matching the given file hash.
    If found, reconstructs and returns the FileAnalysis from that row.
    Returns None if no match is found.
    """
    if file_hash is None:
        return None

    for log_file in _get_all_log_files():
        try:
            with open(log_file, "r", encoding="utf-8", newline="") as f:
                reader = csv.reader(f)
                header = next(reader, None)
                if header is None:
                    continue

                hash_col = header.index("File hash")

                for row in reader:
                    if len(row) > hash_col and row[hash_col] == file_hash:
                        return FileAnalysis(
                            file_path=row[0],
                            file_name=row[1],
                            file_type=row[2],
                            last_modified=row[3],
                            created_time=row[4],
                            extra_data=row[5],
                            importance=float(row[6]) if row[6] else 0.0,
                            customized=row[7].strip().lower() == "true",
                            project_id=row[8],
                            file_hash=row[hash_col],
                        )
        except Exception as e:
            print(f"Warning: Could not read log file {log_file}: {e}")
            continue

    return None
