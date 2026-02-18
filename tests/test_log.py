import os
from posixpath import curdir

import pytest

import src.log.log as log
import src.param.param as param
from src.fas.fas import FileAnalysis

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
    clean_log_folder()


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
    importance=0.0,
    customized=False,
    project_id="ID-1",
    file_hash="x",
)

test_file_analysis_customized: FileAnalysis = FileAnalysis(
    file_path="tests/testdata/fakeTestFile/file1.txt",
    file_name="file1.txt",
    file_type="txt",
    last_modified="2023-10-01T12:00:00",
    created_time="2023-09-30T11:00:00",
    extra_data="EXTRA EXTRA DATA",
    importance=0.0,
    customized=True,
    project_id="ID-2",
    file_hash="x",
)

expectedHeader: str = "File path analyzed,File name,File type,Last modified,Created time,Extra data,Importance,Customized,Project id,File hash"
expectedBody: str = "tests/testdata/fakeTestFile/file1.txt,file1.txt,txt,2023-10-01T12:00:00,2023-09-30T11:00:00,EXTRA EXTRA DATA,0.0,False,ID-1,x"


class TestLog:
    def test_log_start(self):
        setup_log_tests()
        log.open_log_file()
        global test_file_analysis
        log.write(test_file_analysis)
        # Read the produced file, check that the lines are written
        log_file_path = str(os.path.join(param.result_log_folder_path, "0.log"))
        print("Checking: " + log_file_path)
        assert checkLogOutput(log_file_path)
        clean_up_log_tests()

    def test_log_append(self):
        setup_log_tests()
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
            project_id=test_file_analysis.project_id,
            file_hash=test_file_analysis.file_hash,
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
            expected_updated_body = "tests/testdata/fakeTestFile/file1.txt,file1.txt,txt,2023-10-01T12:00:00,2023-09-30T11:00:00,UPDATED EXTRA DATA,0.0,False,ID-1,x"
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

    def test_follow_log_reads_and_stops(self):
        """Test that follow_log reads existing lines and stops on !close! signal"""
        import threading
        import time

        setup_log_tests()
        log.open_log_file()

        # Write initial entries
        global test_file_analysis
        log.write(test_file_analysis)
        log.write(test_file_analysis)

        log_file_path = str(os.path.join(param.result_log_folder_path, "0.log"))
        lines = []

        def append_lines_and_close():
            """Append new lines after a delay, then send close signal"""
            time.sleep(0.3)
            log.write(test_file_analysis)  # Append a new entry
            with open(log_file_path, "a", encoding="utf-8") as f:
                f.write("!close!\n")  # Append stop signal

        # Start thread that appends lines
        thread = threading.Thread(target=append_lines_and_close)
        thread.start()

        # Follow and collect lines (skip header)
        for line in log.follow_log(log_file_path, include_header=False):
            lines.append(line)

        thread.join()

        # Should have 3 data rows + 1 close signal
        assert len(lines) == 4
        assert lines[-1] == "!close!"
        clean_up_log_tests()

    def test_follow_log_with_header(self):
        """Test that follow_log can include the header line"""
        import threading
        import time

        setup_log_tests()
        log.open_log_file()

        global test_file_analysis
        log.write(test_file_analysis)

        log_file_path = str(os.path.join(param.result_log_folder_path, "0.log"))
        lines = []
        count = 0

        def send_close_signal():
            time.sleep(0.2)
            with open(log_file_path, "a", encoding="utf-8") as f:
                f.write("!close!\n")

        thread = threading.Thread(target=send_close_signal)
        thread.start()

        for line in log.follow_log(log_file_path, include_header=True):
            lines.append(line)

        thread.join()

        assert lines[0].startswith("File path analyzed")  # Header
        assert "!close!" in lines[-1]

    def test_log_update_blocked(self):
        setup_log_tests()
        log.open_log_file()
        global test_file_analysis_customized
        log.write(test_file_analysis_customized)
        modified_test_file_analysis = FileAnalysis(
            file_path=test_file_analysis_customized.file_path,
            file_name=test_file_analysis_customized.file_name,
            file_type=test_file_analysis_customized.file_type,
            last_modified=test_file_analysis_customized.last_modified,
            created_time=test_file_analysis_customized.created_time,
            extra_data="SHOULD NOT UPDATE",
            customized=True,
            project_id=test_file_analysis_customized.project_id,
            file_hash=test_file_analysis_customized.file_hash,
        )
        log.update(modified_test_file_analysis)
        # Read the produced file, check that the last line is NOT updated
        log_file_path = str(os.path.join(param.result_log_folder_path, "0.log"))
        with open(log_file_path, "r") as log_file:
            lines = log_file.readlines()
            print("Log file contents after blocked update:")
            for line in lines:
                print(line, end="")

            assert len(lines) == 2  # Header + one entry
            assert lines[0].strip() == expectedHeader
            assert (
                lines[1].strip()
                == "tests/testdata/fakeTestFile/file1.txt,file1.txt,txt,2023-10-01T12:00:00,2023-09-30T11:00:00,EXTRA EXTRA DATA,0.0,True,ID-2,x"
            )
        # Should be unchanged
        clean_up_log_tests()

    def test_get_all_log_files(self):
        # Create two logs and check if the correct number of files are returned
        setup_log_tests()
        log.open_log_file()
        log.write(test_file_analysis)
        log.open_log_file()
        log.write(test_file_analysis_customized)

        log_files = log._get_all_log_files()
        assert len(log_files) == 2

    def test_find_existing_analysis(self):
        # Creates a log with 'x' as file hash and uses function to retreive the analysis from the hash
        setup_log_tests()
        log.open_log_file()
        log.write(test_file_analysis)

        fa = log.find_existing_analysis("x")
        assert fa is not None
        assert fa.file_name == "file1.txt"
        assert fa.file_hash == "x"


def test_log_thread_safety():
    """
    Test that log outputs are not broken when logs are updated and read from multiple threads.
    """
    import threading
    import time

    setup_log_tests()
    log.open_log_file()
    log_file_path = str(os.path.join(param.result_log_folder_path, "0.log"))

    global test_file_analysis

    write_count = 10
    read_results = []

    def writer(idx):
        entry = FileAnalysis(
            file_path=f"tests/testdata/fakeTestFile/file{idx}.txt",
            file_name=f"file{idx}.txt",
            file_type="txt",
            last_modified="2023-10-01T12:00:00",
            created_time="2023-09-30T11:00:00",
            extra_data=f"DATA {idx}",
            importance=0.0,
            customized=False,
            project_id=f"ID-{idx}",
            file_hash=f"hash{idx}",
        )
        log.write(entry)
        # Simulate update
        entry.extra_data = f"UPDATED DATA {idx}"
        log.update(entry)

    def reader():
        time.sleep(0.1)
        with open(log_file_path, "r") as f:
            lines = f.readlines()
            read_results.append(lines)

    # Start writer threads
    writers = [threading.Thread(target=writer, args=(i,)) for i in range(write_count)]
    readers = [threading.Thread(target=reader) for _ in range(3)]

    for w in writers:
        w.start()
    for r in readers:
        r.start()
    for w in writers:
        w.join()
    for r in readers:
        r.join()

    # Check that all log lines are well-formed and not broken
    for lines in read_results:
        for line in lines[1:]:  # skip header
            parts = line.strip().split(",")
            assert len(parts) == 10  # Should match the number of fields in FileAnalysis

    clean_up_log_tests()


def test_follow_log_multithreaded():
    """
    Test that follow_log yields all lines correctly when the log is updated from multiple threads.
    """
    import threading
    import time

    setup_log_tests()
    log.open_log_file()
    log_file_path = str(os.path.join(param.result_log_folder_path, "0.log"))

    global test_file_analysis

    write_count = 8
    lines_written = []

    def writer(idx):
        entry = FileAnalysis(
            file_path=f"tests/testdata/fakeTestFile/file{idx}.txt",
            file_name=f"file{idx}.txt",
            file_type="txt",
            last_modified="2023-10-01T12:00:00",
            created_time="2023-09-30T11:00:00",
            extra_data=f"DATA {idx}",
            importance=0.0,
            customized=False,
            project_id=f"ID-{idx}",
            file_hash=f"hash{idx}",
        )
        log.write(entry)
        lines_written.append(entry)

    # Start the follow_log reader in a thread
    read_lines = []

    def reader():
        for line in log.follow_log(log_file_path, include_header=False):
            read_lines.append(line)
            if len(read_lines) == write_count:
                break

    reader_thread = threading.Thread(target=reader)
    writer_threads = [
        threading.Thread(target=writer, args=(i,)) for i in range(write_count)
    ]

    reader_thread.start()
    # Give the reader a moment to start
    time.sleep(0.1)
    for w in writer_threads:
        w.start()
    for w in writer_threads:
        w.join()
    reader_thread.join(timeout=2)

    # Check that all lines were read and are well-formed
    assert len(read_lines) == write_count
    for line in read_lines:
        parts = line.strip().split(",")
        assert len(parts) == 10  # Should match FileAnalysis fields

    clean_up_log_tests()
