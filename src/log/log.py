import csv
import json
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
current_projects = set()
initialized_log = ""


def initialize_log() -> None:
    global current_log_file
    global current_projects
    global initialized_log
    global log_lock
    with log_lock:
        current_projects.clear()
        with open(current_log_file, "r", encoding="utf-8", newline="") as log_file:
            reader = csv.reader(log_file)
            header = next(reader, None)
            if header is None:
                return

            project_id_col = header.index("Project id")

            for row in reader:
                if len(row) > project_id_col:
                    current_projects.add(row[project_id_col])
        initialized_log = current_log_file


# resumes the last log file used
# This is the default, we will want to force open a log file when --clean is used
def resume_log_file() -> None:
    global current_log_file
    global initialized_log
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
    if initialized_log != current_log_file:
        initialize_log()


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
    initialize_log()


def create_row(fileAnalysis: FileAnalysis) -> list:
    if fileAnalysis.extra_data is not None and not isinstance(
        fileAnalysis.extra_data, str
    ):
        extra_data_str = json.dumps(fileAnalysis.extra_data)
    else:
        extra_data_str = (
            fileAnalysis.extra_data if fileAnalysis.extra_data is not None else ""
        )
    return [
        fileAnalysis.file_path,
        fileAnalysis.file_name,
        fileAnalysis.file_type,
        fileAnalysis.last_modified,
        fileAnalysis.created_time,
        extra_data_str,
        fileAnalysis.importance,
        fileAnalysis.customized,
        fileAnalysis.project_id,
        fileAnalysis.file_hash,
    ]


def parse_row(line: list) -> Optional[FileAnalysis]:
    if len(line) < 10:
        print(f"Skipping malformed log line: {line}")
        return None
    try:
        # Parse extra_data if it's a JSON string
        extra_data = line[5]
        if isinstance(extra_data, str):
            try:
                extra_data = json.loads(extra_data)
            except json.JSONDecodeError:
                print(f"Warning: extra_data is not valid JSON: {extra_data}")
                # Optionally, set extra_data = None or leave as string

        fa = FileAnalysis(
            file_path=line[0],
            file_name=line[1],
            file_type=line[2],
            last_modified=line[3],
            created_time=line[4],
            extra_data=extra_data,
            importance=float(line[6]) if line[6] else 0.0,
            customized=line[7].strip().lower() == "true",
            project_id=line[8],
            file_hash=line[9],
        )
        return fa
    except Exception as e:
        print(f"Error parsing log line into FileAnalysis: {e}")
        return None


def check_project_id_exists(project_id: str) -> bool:
    global current_log_file
    global initialized_log
    global current_projects
    if current_log_file == "" or not Path(current_log_file).exists():
        resume_log_file()

    if initialized_log != current_log_file:
        initialize_log()

    if project_id in current_projects:
        return True

    return False


def write(fileAnalysis: FileAnalysis) -> None:
    global current_log_file
    global initialized_log
    if current_log_file == "" or not Path(current_log_file).exists():
        resume_log_file()

    if initialized_log != current_log_file:
        initialize_log()

    with (
        log_lock,
        open(current_log_file, "a", encoding="utf-8", newline="") as log_file,
    ):
        writer = csv.writer(log_file)
        if (
            fileAnalysis.project_id is not None
            and fileAnalysis.project_id not in current_projects
        ):
            # Create project entry
            project = FileAnalysis(
                file_path=fileAnalysis.project_id,
                file_name=fileAnalysis.project_id,
                file_type="Project",
                last_modified="",
                created_time="",
                extra_data={"description": ""},
                importance=0.0,
                customized=False,
                project_id=fileAnalysis.project_id,
                file_hash="",
            )
            writer.writerow(create_row(project))
            current_projects.add(fileAnalysis.project_id)

        writer.writerow(create_row(fileAnalysis))


# This can be optimized by changing how logs are stored, say as a database or serialized object.
# But because our log files will be relatively small compared to the total number of files on a system, this should be sufficient for now.
def update(fileAnalysis: FileAnalysis, forceUpdate: bool = False) -> None:
    global current_log_file
    global initialized_log
    if current_log_file == "" or not Path(current_log_file).exists():
        resume_log_file()

    if initialized_log != current_log_file:
        initialize_log()

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
                        writer.writerow(create_row(fileAnalysis))
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
    wait_for_new: bool = True,
    return_file_analysis: bool = False,
):
    """
    Generator that yields log lines as they appear in the file.
    Polls the file and waits for new lines to be added.
    Stops when a line containing stop_signal is encountered.
    Now uses csv.reader for proper CSV parsing.
    """
    import csv

    global current_log_file

    if file_path is None:
        if current_log_file == "" or not Path(current_log_file).exists():
            resume_log_file()
        file_path = current_log_file

    with open(file_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        if not include_header:
            next(reader, None)  # skip header row

        while True:
            row = None
            with log_lock:
                try:
                    row = next(reader)
                except StopIteration:
                    row = None
            if row is not None:
                line = ",".join(row)
                if return_file_analysis:
                    fa = parse_row(row)
                    if fa is None:
                        continue
                    yield fa
                else:
                    yield line
                if any(stop_signal in field for field in row):
                    break
            else:
                if not wait_for_new:
                    break
                time.sleep(poll_interval)


# Binding, blocks all reads and writes
def get_project(project_id):
    """
    Get all log entries for a given project id, as FileAnalysis objects.
    """
    entries = []
    for log_file in _get_all_log_files():
        try:
            with log_lock:
                with open(log_file, "r", encoding="utf-8", newline="") as f:
                    reader = csv.reader(f)
                    header = next(reader, None)
                    if header is None:
                        continue

                    project_id_col = header.index("Project id")

                    for row in reader:
                        if (
                            len(row) > project_id_col
                            and row[project_id_col] == project_id
                        ):
                            entries.append(parse_row(row))

        except Exception as e:
            print(f"Warning: Could not read log file {log_file}: {e}")
            continue
    return entries


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
                        return parse_row(row)
        except Exception as e:
            print(f"Warning: Could not read log file {log_file}: {e}")
            continue

    return None
