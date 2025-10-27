import sys
#from zip.zip import zip
#from fss.fss import fss
import builtins

def prompt_file_perms():
    # Request User Permission to Access Files
    print("This application requires access to system files")
    response = input("Do wish to continue? (Y/N): ")
    if response.lower() != 'y':
        sys.exit(1)

def extract_chosen_zip(zip_file_path: str):
    #TODO: Link fss call here to assign the result to file_path
    file_path = zip.zip_extract(zip_file_path) 
    print("File unzipped at: " + file_path)
    return file_path

def get_param_body(args: list[str], indx: int) -> str:
    if indx < len(args) and not args[indx].startswith("-"):
        return args[indx]
    else:
        return ""

def run_cli(cli_args: list[str]):
    quiet: bool = ("--quiet" in cli_args) or ("-q" in cli_args)
    if quiet:
        _original_print = builtins.print
        builtins.print = lambda *a, **k: None

    if "-y" not in cli_args:
        prompt_file_perms()

    path_exclusions: set = set()
    file_path: str = ""

    if "--zip" in cli_args:
        print("Processing Zip File")
        zip_file: str = get_param_body(cli_args, cli_args.index("--zip") + 1)
        if zip_file == "":
            print("Expected File path following --zip")
            sys.exit(1)
        file_path = extract_chosen_zip(zip_file)
    else:
        #TODO: Get folder to start search at.
        file_path = get_param_body(cli_args, len(cli_args)-1)
    if(file_path == ""):
        print("No starting file_path")
        sys.exit(1)
    print("Scanning file path: " + file_path)
    #TODO: Link fss call here with completed path
    fss.search(file_path, path_exclusions)

    #Reactivate prints if turned off
    if quiet:
        builtins.print = _original_print

    #TODO: get most recent log file and print it for consumption
