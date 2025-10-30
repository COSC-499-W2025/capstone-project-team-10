import pytest

import src.log.log as log
from src.fas.fas import FileAnalysis
import src.param.param as param

path_to_test_zip = "tests/testdata/test_cli/testScanFolder.zip"
path_to_test_folder = "tests/testdata/test_cli/testScanFolder"


def clean_log_folder():
    import os
    import shutil

    log_folder = param.program_file_path + "/logs/"
    if os.path.exists(log_folder):
        shutil.rmtree(log_folder)
    os.makedirs(log_folder)


def setup_log_tests():
    param.init()
    clean_log_folder()


def checkLogOutput(file_path: str) -> bool:
    global expectedHeader
    global expectedBody
    with open(file_path, "r") as log_file:
        lines = log_file.readlines()
        print("Log file contents:")
        for line in lines:
            print(line, end="")

        if len(lines) == 2:  # Header + one entry
            if lines[0].strip() == expectedHeader:
                if lines[1].strip() == expectedBody:
                    return True


test_file_analysis: FileAnalysis = FileAnalysis(
    file_path="tests/testdata/fakeTestFile/file1.txt",
    file_name="file1.txt",
    file_type="txt",
    last_modified="2023-10-01T12:00:00",
    created_time="2023-09-30T11:00:00",
    extra_data="EXTRA EXTRA DATA",
)
expectedHeader: str = (
    "File path analyzed,File name,File type,Last modified,Created time,Extra data"
)
expectedBody: str = "tests/testdata/fakeTestFile/file1.txt,file1.txt,txt,2023-10-01T12:00:00,2023-09-30T11:00:00,EXTRA EXTRA DATA"


class TestLog:
    def test_log_start(self):
        setup_log_tests()
        global test_file_analysis
        print("Checking: " + param.program_file_path + "/logs/0.log")
        log.write(test_file_analysis)
        # Read the produced file, check that the lines are written
        log_file_path = param.result_log_folder_path + "0.log"
        assert checkLogOutput(log_file_path)

    def test_log_append(self):
        setup_log_tests()
        log.open_log_file()
        global test_file_analysis
        log.write(test_file_analysis)
        # Read the produced file, check that the lines are written
        log_file_path = param.result_log_folder_path + "0.log"
        assert checkLogOutput(log_file_path)

    def test_log_continue(self):
        setup_log_tests()
        # Open two files to simulate existing log files
        log.open_log_file()
        log.open_log_file()
        # Now resume logging, which should use log 1.log
        log.resume_log_file()
        global test_file_analysis
        log.write(test_file_analysis)
        # Read the produced file, check that the lines are written
        log_file_path = param.result_log_folder_path + "1.log"
        assert checkLogOutput(log_file_path)

    def test_log_no_available_continue(self):
        setup_log_tests()
        # Call resume without any existing logs, should create 0.log
        log.resume_log_file()
        global test_file_analysis
        log.write(test_file_analysis)
        # Read the produced file, check that the lines are written
        log_file_path = param.result_log_folder_path + "0.log"
        assert checkLogOutput(log_file_path)

    def test_log_max_logs(self):
        setup_log_tests()
        # Create max logs
        for _ in range(param.log_max_count):
            log.open_log_file()
        # Now open one more, which should delete the oldest (0.log) and create a new one
        log.open_log_file()
        global test_file_analysis
        log.write(test_file_analysis)
        # Read the produced file, check that the lines are written
        log_file_path = param.result_log_folder_path + f"{param.log_max_count}.log"
        assert checkLogOutput(log_file_path)
        # Check that 0.log has been deleted
        import os

        log_0_path = param.result_log_folder_path + "0.log"
        assert not os.path.exists(log_0_path)
