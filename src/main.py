import sys

import src.param.param as param
from src.cli.cli_app import run_cli
from src.gui.gui_app import run_gui


def main():
    # Intiialize Params
    param.init()
    if len(sys.argv) > 1 and sys.argv.__contains__("--cli"):
        run_cli()
    else:
        run_gui()
    # After execution save any changed params
    param.save_additional_params()


if __name__ == "__main__":
    main()
