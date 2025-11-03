import sys
from gui.gui_app import run_gui
from cli.cli_app import run_cli
import param.param as param


def main():
    # Intiialize Params
    param.init()
    if len(sys.argv) > 1 and sys.argv.__contains__("--cli"):
        run_cli(sys.argv)
    else:
        run_gui()
    # After execution save any changed params
    param.save_additional_params()


if __name__ == "__main__":
    main()