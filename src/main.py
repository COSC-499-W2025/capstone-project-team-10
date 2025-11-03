import sys
from gui.gui_app import run_gui
from cli.cli_app import run_cli

def main():

    if len(sys.argv) > 1 and sys.argv.__contains__("--cli"):
        run_cli(sys.argv)  
    else:
        run_gui()

if __name__ == "__main__":
    main()