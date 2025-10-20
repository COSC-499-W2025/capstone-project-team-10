import sys
from gui.gui_app import run_gui
from cli.cli_app import run_cli

def main():

    if len(sys.argv) > 1 and sys.argv.__contains__("--cli"):
        if not sys.argv.__contains__("-y"):
            
            # Request User Permission to Access Files
            print("This application requires access to system files")
            response = input("Do wish to continue? (Y/N): ")
            if response.lower() != 'y':
                sys.exit(1)

        run_cli()
        
    else:
        run_gui()

if __name__ == "__main__":
    main()
