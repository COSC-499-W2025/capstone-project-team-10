import os
import platform

# For Builds and Versioning
project_version = "1.0.0"
project_name = "Capstone Project Team 10"

program_file_path: str = ""
log_max_count: int = 10
log_file_naming_regex: str = r"(\d+)\.log"
result_log_folder_path: str = ""
optional_parameters_path: str = ""


def set_program_constants() -> None:
    # Detect Operating System to set program file path
    global program_file_path, result_log_folder_path
    os_name = platform.system()
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
    # TODO : Load additional parameters from JSON file if it exists


def save_additional_params() -> None:
    global optional_parameters_path
    # TODO : Save additional parameters to JSON file


# Use this function to set configuration specific values
def init() -> None:
    set_program_constants()
    load_additional_params()


def get_constant_state() -> dict:
    return {
        "program_file_path": program_file_path,
        "project_version": project_version,
        "project_name": project_name,
    }
