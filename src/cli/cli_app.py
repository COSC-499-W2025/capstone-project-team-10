import argparse
import builtins
import sys
from pathlib import Path

import src.fss.fss as fss
import src.log.log as log
import src.param.param as param
import src.zip.zip_app as zip
from src.showcase.showcase import generate_portfolio, generate_resume


def prompt_file_perms():
    print("This application requires access to system files")
    response = input("Do you wish to continue? (Y/N): ")
    if response.lower() != "y":
        print("Permission denied. Exiting.")
        sys.exit(1)


def extract_chosen_zip(zip_file_path: str) -> Path | None:
    file_path = zip.extract_zip(zip_file_path)
    print(f"File unzipped at: {file_path}")
    return file_path


def add_cli_args(parser: argparse.ArgumentParser):
    parser.add_argument(
        "file_path", nargs="?", help="Path to start search at or zip file to extract."
    )
    parser.add_argument("--zip", help="Extract the specified zip file.")
    parser.add_argument(
        "--exclude-paths",
        nargs="+",
        help="Paths to exclude from search (space separated).",
    )
    parser.add_argument(
        "--file-types", nargs="+", help="File types to include (space separated)."
    )
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Automatically grant file access permission.",
    )
    parser.add_argument(
        "-r",
        "--resume_entries",
        nargs="?",
        const=True,
        default=None,
        help="Output a pdf with resume project insights. Optional: Include a directory path to change where the result is saved",
    )
    parser.add_argument(
        "-p",
        "--portfolio_entries",
        nargs="?",
        const=True,
        default=None,
        help="Output a web portfolio with project descriptions. Optional: Include a directory path to change where the result is saved",
    )
    parser.add_argument(
        "-c",
        "--clean",
        action="store_true",
        help="Start a new log file instead of resuming the last one.",
    )
    # Flags
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress output.")


def run_cli():
    # Setup supported CLI args
    parser = argparse.ArgumentParser(
        description="CLI for file system scanning and zip extraction."
    )
    add_cli_args(parser)

    args = parser.parse_args()

    if not args.yes:
        prompt_file_perms()

    _original_print = builtins.print
    if args.quiet:
        builtins.print = lambda *a, **k: None

    file_path = ""
    if args.zip:
        print("Processing Zip File")
        file_path = extract_chosen_zip(args.zip)
    elif args.file_path:
        file_path = args.file_path
    else:
        print("No starting file_path provided.")
        parser.print_help()
        sys.exit(1)
    # Start a new log if clean flag is set
    if args.clean:
        log.open_log_file()
    else:
        log.resume_log_file()

    path_exclusions = set(args.exclude_paths or param.get("excluded_paths") or [])
    file_types = set(args.file_types or param.get("supported_file_types") or [])
    param.set("excluded_paths", list(path_exclusions))
    param.set("supported_file_types", list(file_types))

    print(f"Scanning file path: {file_path}")
    print(f"Excluding paths: {path_exclusions}")
    print(f"Supported file types: {file_types}")

    fss.search(file_path, path_exclusions)

    print("Scan complete.")
    print(f"Log file located at:{param.get('logging.current_log_file')}")

    if args.resume_entries:
        # check that the included path is valid
        if (
            isinstance(args.resume_entries, str)
            and Path(args.resume_entries).exists()
            and Path(args.resume_entries).is_dir()
        ):
            param.export_folder_path = args.resume_entries
        print("Generating Resume PDF...")
        file_path = generate_resume()
        if file_path:
            print(f"Resume generated at: {file_path}")
        else:
            print("Resume generation failed.")

    if args.portfolio_entries:
        # check that the included path is valid
        if (
            isinstance(args.portfolio_entries, str)
            and Path(args.portfolio_entries).exists()
            and Path(args.portfolio_entries).is_dir()
        ):
            param.export_folder_path = args.portfolio_entries
        print("Generating Portfolio Website...")
        file_path = generate_portfolio()
        if file_path:
            print(f"Portfolio generated at: {file_path}")
        else:
            print("Portfolio generation failed.")

    if args.quiet:
        builtins.print = _original_print
        print(param.get("logging.current_log_file"))
    print("Processing Complete!")
