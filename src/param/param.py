import copy
import json
import os
import platform

# For Builds and Versioning
project_name = "Capstone Project Team 10"
project_version = "1.0.0"
program_file_path: str = ""
log_max_count: int = 10
log_file_naming_regex: str = r"(\d+)\.log$"
result_log_folder_path: str = ""
export_folder_path: str = ""
optional_parameters_path: str = ""

params = {}


# Use this function to set system configuration specific values
def set_program_constants() -> None:
    # Detect Operating System to set program file path
    global \
        program_file_path, \
        result_log_folder_path, \
        optional_parameters_path, \
        export_folder_path
    os_name = platform.system()
    export_folder_path = os.path.join(os.path.expanduser("~"), "Downloads")
    match os_name:
        case "Windows":
            appdata = os.getenv("APPDATA")
            if appdata is not None:
                program_file_path = os.path.join(appdata, project_name)
            else:
                program_file_path = os.path.join(os.path.expanduser("~"), project_name)
        case "Darwin":  # macOS
            program_file_path = os.path.join(
                os.path.expanduser("~"), "Library", "Application Support", project_name
            )
        case "Linux":
            program_file_path = os.path.join(
                os.path.expanduser("~"), f".{project_name}"
            )
        case _:
            program_file_path = os.path.join(os.path.expanduser("~"), project_name)

    result_log_folder_path = os.path.join(program_file_path, "logs")
    optional_parameters_path = os.path.join(program_file_path, "params.json")


def load_additional_params() -> None:
    global optional_parameters_path
    global params
    try:
        with open(optional_parameters_path, "r") as param_file:
            params = json.load(param_file)
    except FileNotFoundError:
        print("No additional parameters file found. Using default parameters.")
        load_defaults()
    except json.JSONDecodeError:
        print("Error decoding JSON from the parameters file. Using default parameters.")
        load_defaults()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        load_defaults()


def save_additional_params() -> None:
    global optional_parameters_path
    global params
    try:
        with open(optional_parameters_path, "w") as param_file:
            json.dump(params, param_file, indent=4)
    except OSError as e:
        print(f"Failed to Save Parameters: {e}")


def get(key: str):
    global params
    path = key.split(".")

    current_level = params
    for part in path[:-1]:
        if part not in current_level or not isinstance(current_level[part], dict):
            return None
        current_level = current_level[part]
    if path[-1] not in current_level:
        return None
    return current_level[path[-1]]


def set(key: str, value) -> bool:
    global params
    path = key.split(".")

    current_level = params
    for part in path[:-1]:
        if part not in current_level or not isinstance(current_level[part], dict):
            return False
        current_level = current_level[part]
    if path[-1] not in current_level:
        return False
    current_level[path[-1]] = value
    save_additional_params()
    return True


def remove(key: str) -> bool:
    return set(key, None)


def clear() -> None:
    global optional_parameters_path
    global params
    try:
        os.unlink(optional_parameters_path)
    except FileNotFoundError:
        # win-win
        pass
    params.clear()
    load_defaults()
    save_additional_params()


def load_defaults() -> None:
    global params, file, project_name, project_version
    params.clear()
    with open("src/param/param_defaults.json", "r") as default_params:
        params.update(json.load(default_params))
    project_name = get("config.project_name")
    project_version = get("config.config_info")


def init() -> None:
    set_program_constants()
    load_additional_params()
