from pathlib import Path
from datetime import datetime, timedelta

"""
These are the files for storing helper methods for fss - the sole job of the fss is to only
govern the sole loop - by separating the inline methods from the fss, the fss can focus on delegating,
while this method library can constantly be tinkered, added and fix without much disruption of
fss.py
"""

def str_path_converter(path):
    """
        Converts a string path to a string path and ensures the casting of Path obj.

        Inputs:
            (str) or (Path) obj

        Outputs:
            (Path) obj
    """
    if not isinstance(path, Path):
        file_path = Path(path)
    else:
        file_path = path
    return file_path

def get_creation_time(path):
    """
        Retrieves the creation time of a file.

        Inputs:
            (Path) obj - the path of the obj.

        Outputs:
            (datetime) obj representing the creation time of the file.
    """
    file_path = str_path_converter(path)
    stat = file_path.stat()
    creation_time = getattr(stat, "st_birthtime", stat.st_ctime)
    return datetime.fromtimestamp(creation_time)

def get_mod_time(path):
    """
        Retrieves the latest modification time of a file.

        Inputs:
            (Path) obj - the path of the obj.

        Outputs:
            (datetime) obj representing the latest modification time of the file.
    """
    file_path = str_path_converter(path)
    return datetime.fromtimestamp(file_path.stat().st_mtime)

def time_check(time_criteria, path, arg):
    """
        Checks whether a time criteria is met or not by the given path to the obj.

        Inputs:
            (List (datetime, datetime)) a list of 2 datetime obj, indicating the lower / upper bound of time chosen by the user
            (Path) obj - the path of the obj.
            (str) arg - the arguments that indicates whether we are checking for the:
                - "mod" - modification time or
                - anything else for the creation time.

        Outputs:
            Returns a True if the time criteria is met (within the range given), and False otherwise.
    """
    file_path = str_path_converter(path)

    lower_time, upper_time = time_criteria

    # Validate types if not None
    if lower_time is not None and not isinstance(lower_time, datetime):
        raise TypeError("Start bound must be a datetime or None.")
    if upper_time is not None and not isinstance(upper_time, datetime):
        raise TypeError("End bound must be a datetime or None.")

    if arg == "mod":
        file_time = get_mod_time(file_path)
    else:
        file_time = get_creation_time(file_path)

    # Case if 1 bound is missing
    if lower_time is None and upper_time is None:
        return True  # No bounds at all
    if lower_time is None:
        return file_time <= upper_time  # Only upper bound
    if upper_time is None:
        return file_time >= lower_time  # Only lower bound

    # Both bounds present
    return lower_time <= file_time <= upper_time