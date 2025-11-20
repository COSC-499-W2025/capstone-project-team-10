import pytest
import os
import src.log.log as log
from src.fas.fas import FileAnalysis
import src.param.param as param

path_to_test_zip = "tests/testdata/test_cli/testScanFolder.zip"
path_to_test_folder = "tests/testdata/test_cli/testScanFolder"


def clean_log_folder():
    import shutil

    log_folder = str(param.result_log_folder_path)
    if os.path.exists(log_folder):
        shutil.rmtree(log_folder)
    os.makedirs(log_folder)


def setup_log_tests():
    param.init()


def clean_up_log_tests():
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
        return False


test_file_analysis: FileAnalysis = FileAnalysis(
    file_path="tests/testdata/fakeTestFile/file1.txt",
    file_name="file1.txt",
    file_type="txt",
    last_modified="2023-10-01T12:00:00",
    created_time="2023-09-30T11:00:00",
    extra_data="EXTRA EXTRA DATA",
)
expectedHeader: str = (
    "File path analyzed,File name,File type,Last modified,Created time,Extra data,Importance"
)
expectedBody: str = "tests/testdata/fakeTestFile/file1.txt,file1.txt,txt,2023-10-01T12:00:00,2023-09-30T11:00:00,EXTRA EXTRA DATA,0.0"


class TestLog:
    def test_log_start(self):
        setup_log_tests()
        global test_file_analysis
        log.write(test_file_analysis)
        # Read the produced file, check that the lines are written
        log_file_path = str(os.path.join(param.result_log_folder_path, "0.log"))
        print("Checking: " + log_file_path)
        assert checkLogOutput(log_file_path)
        clean_up_log_tests()

    def test_log_append(self):
        setup_log_tests()
        log.open_log_file()
        global test_file_analysis
        log.write(test_file_analysis)
        # Read the produced file, check that the lines are written
        log_file_path = str(os.path.join(param.result_log_folder_path, "0.log"))
        assert checkLogOutput(log_file_path)
        clean_up_log_tests()

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
        log_file_path = str(os.path.join(param.result_log_folder_path, "1.log"))
        assert checkLogOutput(log_file_path)
        clean_up_log_tests()

    def test_log_no_available_continue(self):
        setup_log_tests()
        # Call resume without any existing logs, should create 0.log
        log.resume_log_file()
        global test_file_analysis
        log.write(test_file_analysis)
        # Read the produced file, check that the lines are written
        log_file_path = str(os.path.join(param.result_log_folder_path, "0.log"))
        assert checkLogOutput(log_file_path)
        clean_up_log_tests()

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
        log_file_path = str(
            os.path.join(param.result_log_folder_path, f"{param.log_max_count}.log")
        )

        assert checkLogOutput(log_file_path)
        # Check that 0.log has been deleted
        log_0_path = str(os.path.join(param.result_log_folder_path, "0.log"))
        assert not os.path.exists(log_0_path)
        clean_up_log_tests()

    def test_log_update_existing(self):
        setup_log_tests()
        log.open_log_file()
        global test_file_analysis
        log.write(test_file_analysis)
        # Update the test data
        modified_test_file_analysis = FileAnalysis(
            file_path=test_file_analysis.file_path,
            file_name=test_file_analysis.file_name,
            file_type=test_file_analysis.file_type,
            last_modified=test_file_analysis.last_modified,
            created_time=test_file_analysis.created_time,
            extra_data="UPDATED EXTRA DATA",
        )
        log.update(modified_test_file_analysis)
        # Read the produced file, check that the last line is updated
        log_file_path = str(os.path.join(param.result_log_folder_path, "0.log"))
        with open(log_file_path, "r") as log_file:
            lines = log_file.readlines()
            print("Log file contents after update:")
            for line in lines:
                print(line, end="")

            assert len(lines) == 2  # Header + one entry
            assert lines[0].strip() == expectedHeader
            expected_updated_body = "tests/testdata/fakeTestFile/file1.txt,file1.txt,txt,2023-10-01T12:00:00,2023-09-30T11:00:00,UPDATED EXTRA DATA,0.0"
            assert lines[1].strip() == expected_updated_body
        clean_up_log_tests()

    def test_log_update_no_file(self):
        setup_log_tests()
        global test_file_analysis
        log.update(test_file_analysis)
        # Read the produced file, check that the lines are written
        log_file_path = str(os.path.join(param.result_log_folder_path, "0.log"))
        print("Checking: " + log_file_path)
        assert checkLogOutput(log_file_path)
        clean_up_log_tests()
