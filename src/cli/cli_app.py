import builtins
import sys

import src.fss.fss as fss
import src.param.param as param
import src.zip.zip_app as zip


def prompt_file_perms():
    # Request User Permission to Access Files
    print("This application requires access to system files")
    response = input("Do wish to continue? (Y/N): ")
    if response.lower() != "y":
        sys.exit(1)


def extract_chosen_zip(zip_file_path: str):
    # TODO: Link fss call here to assign the result to file_path
    file_path = zip.extract_zip(zip_file_path)
    print("File unzipped at: " + str(file_path))
    return file_path


def get_param_body(args: list[str], indx: int) -> str:
    if indx < len(args) and not args[indx].startswith("-"):
        return args[indx]
    else:
        return ""


def get_multi_argument(args: list[str], indx: int) -> set[str]:
    multi_argument_set: set[str] = set()
    indx += 1  # Start after the flag itself
    while indx < len(args):
        arg = args[indx]
        multi_argument_set.add(arg.rstrip(","))
        if not args[indx].endswith(","):
            break
        indx += 1
    return multi_argument_set


def run_cli(cli_args: list[str]):
    quiet: bool = ("--quiet" in cli_args) or ("-q" in cli_args)
    _original_print = builtins.print
    if quiet:
        builtins.print = lambda *a, **k: None

    if "-y" not in cli_args:
        prompt_file_perms()

    path_exclusions: set = set()
    file_types: set = set()
    file_path: str = ""

    if "--zip" in cli_args:
        print("Processing Zip File")
        zip_file: str = get_param_body(cli_args, cli_args.index("--zip") + 1)
        if zip_file == "":
            print("Expected File path following --zip")
            sys.exit(1)
        file_path = str(zip.extract_zip(zip_file))
    else:
        # TODO: Get folder to start search at.
        file_path = get_param_body(cli_args, len(cli_args) - 1)
    if file_path == "":
        print("No starting file_path")
        sys.exit(1)
    if "--exclude-paths" in cli_args:
        path_exclusions.clear()
        path_exclusions.update(
            get_multi_argument(cli_args, cli_args.index("--exclude-paths"))
        )
        param.set(
            "excluded_paths",
            list(path_exclusions),
        )
    else:
        temp = param.get("excluded_paths")
        if temp is not None and isinstance(temp, list):
            path_exclusions.clear()
            path_exclusions.update(temp)

    if "--file-types" in cli_args:
        file_types.clear()
        file_types.update(get_multi_argument(cli_args, cli_args.index("--file-types")))
        param.set(
            "supported_file_types",
            list(file_types),
        )
    else:
        temp = param.get("supported_file_types")
        if temp is not None and isinstance(temp, list):
            file_types.clear()
            file_types.update(temp)

    print("Scanning file path: " + file_path)
    # TODO: Link fss call here with completed path
    fss.search(file_path, path_exclusions)

    # Reactivate prints if turned off
    if quiet:
        builtins.print = _original_print

    # TODO: get most recent log file and print it for consumption
