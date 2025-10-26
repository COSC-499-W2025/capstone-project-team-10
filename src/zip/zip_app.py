import zipfile
from pathlib import Path
from datetime import datetime
import re
import shutil

def extract_zip(origin_path: str | Path):
    
    origin_path = Path(origin_path)
    base_destination_path = Path("src/zip/zipfolders")

    if not origin_path.exists():
        print("Error: File not found")
        return None
    if not zipfile.is_zipfile(origin_path):
        print("Error: The provided file is not a valid ZIP file.")
        return None
    
    time_tag = datetime.now().strftime("%Y%m%d-%H%M%S-%f")[:-3] #gets current date and time for the tag
    destination_path = base_destination_path / f"zip_{time_tag}"

    try:
        with zipfile.ZipFile(origin_path, 'r') as zip_ref:
            zip_ref.extractall(destination_path)

    except zipfile.BadZipFile:
        print("Error: The provided file is not a valid ZIP file.")
        return None

    except FileNotFoundError:
        print("Error: ZIP file not found")
        return None
    
    filename_pattern = re.compile(rf"^zip_\d{{8}}-\d{{6}}-\d{{3}}$")
    
    zipFolders = [files for files in base_destination_path.iterdir() if files.is_dir() and filename_pattern.match(files.name)]
    zipFolders.sort(key=lambda file: file.name, reverse=True)
    for oldFiles in zipFolders[5:]: 
        shutil.rmtree(oldFiles, ignore_errors=True)
    
    return base_destination_path