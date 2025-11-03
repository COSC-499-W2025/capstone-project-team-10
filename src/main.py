import sys
#from gui.gui_app import run_gui
from cli.cli_app import run_cli
from fas.fas_docx import extract_docx_data
from fas.fas_rtf import extract_rtf_data

def main():

    if len(sys.argv) > 1 and sys.argv.__contains__("--cli"):
        run_cli(sys.argv)  
    else:
        run_gui()

if __name__ == "__main__":
    #main()
    extract_rtf_data("/Users/sfjalexander/Desktop/COSC 499/capstone-project-team-10/tests/testdata/test_fas/fas_rtf_data.rtf")
