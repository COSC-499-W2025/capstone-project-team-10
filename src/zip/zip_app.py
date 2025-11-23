import re
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

import src.param.param as param


def extract_zip(origin_path: str | Path):
    origin_path = Path(origin_path)
    base_destination_path = Path(param.program_file_path) / "zip"

    if not origin_path.exists():
        print("Error: File not found")
        return None
    if not zipfile.is_zipfile(origin_path):
        print("Error: The provided file is not a valid ZIP file.")
        return None

    # gets current date and time for the tag
    time_tag = datetime.now().strftime("%Y%m%d-%H%M%S-%f")[:-3]
    # sends the zip file to its designated folder in the zipfolders folder
    # the the name "zip_########-######-###" where the digits are the current date and time
    destination_path = base_destination_path / f"zip_{time_tag}"

    try:  # extracts zip
        with zipfile.ZipFile(origin_path, "r") as zip_ref:
            zip_ref.extractall(destination_path)

    except zipfile.BadZipFile:
        print("Error: The provided file is not a valid ZIP file.")
        return None

    except FileNotFoundError:
        print("Error: ZIP file not found")
        return None

    # sets the pattern to "zip_########-######-###" in order to match
    # with the folders later and delete the oldest one
    filename_pattern = re.compile(rf"^zip_\d{{8}}-\d{{6}}-\d{{3}}$")
    # finds all files in zipfolder which match the naming pattern
    # and sorts them in reverse
    zipFolders = [
        files
        for files in base_destination_path.iterdir()
        if files.is_dir() and filename_pattern.match(files.name)
    ]
    zipFolders.sort(key=lambda file: file.name, reverse=True)

    # the newest 5 folders are kept and the rest are deleted
    for old_Files in zipFolders[5:]:
        shutil.rmtree(old_Files, ignore_errors=True)

    return base_destination_path
