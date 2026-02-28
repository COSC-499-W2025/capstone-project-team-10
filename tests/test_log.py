import os

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


def checkLogOutput(file_path: str, expected_rows: list[str]) -> bool:
    with open(file_path, "r") as log_file:
        lines = [line.strip() for line in log_file.readlines()]
        print("Log file contents:")
        for line in lines:
            print(line)
        if len(lines) != len(expected_rows):
            print(f"Expected {len(expected_rows)} rows, got {len(lines)}")
            return False
        for expected, actual in zip(expected_rows, lines):
            if expected != actual:
                print(f"Expected: {expected}")
                print(f"Actual:   {actual}")
                return False
        return True


test_file_analysis: FileAnalysis = FileAnalysis(
    file_path="tests/testdata/fakeTestFile/file1.txt",
    file_name="file1.txt",
    file_type="txt",
    last_modified="2023-10-01T12:00:00",
    created_time="2023-09-30T11:00:00",
    extra_data={"description": "EXTRA EXTRA DATA"},
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
    extra_data={"description": "EXTRA EXTRA DATA"},
    importance=0.0,
    customized=True,
    project_id="ID-2",
    file_hash="x",
)

import json

expectedHeader: str = "File path analyzed,File name,File type,Last modified,Created time,Extra data,Importance,Customized,Project id,File hash"
expectedProjectRow: str = (
    'ID-1,ID-1,Project,,,"{""description"": """"}",0.0,False,ID-1,'
)
expectedBody: str = 'tests/testdata/fakeTestFile/file1.txt,file1.txt,txt,2023-10-01T12:00:00,2023-09-30T11:00:00,"{""description"": ""EXTRA EXTRA DATA""}",0.0,False,ID-1,x'
expectedBodyCustomized: str = 'tests/testdata/fakeTestFile/file1.txt,file1.txt,txt,2023-10-01T12:00:00,2023-09-30T11:00:00,"{""description"": ""EXTRA EXTRA DATA""}",0.0,True,ID-2,x'


class TestLog:
    def test_log_start(self):
        setup_log_tests()
        log.open_log_file()
        global test_file_analysis
        log.write(test_file_analysis)
        log_file_path = str(os.path.join(param.result_log_folder_path, "0.log"))
        expected_rows = [
            expectedHeader,
            expectedProjectRow,
            expectedBody,
        ]
        assert checkLogOutput(log_file_path, expected_rows)
        clean_up_log_tests()

    def test_log_append(self):
        setup_log_tests()
        global test_file_analysis
        log.write(test_file_analysis)
        log_file_path = str(os.path.join(param.result_log_folder_path, "0.log"))
        expected_rows = [
            expectedHeader,
            expectedProjectRow,
            expectedBody,
        ]
        assert checkLogOutput(log_file_path, expected_rows)
        clean_up_log_tests()

    def test_log_continue(self):
        setup_log_tests()
        log.open_log_file()
        log.open_log_file()
        log.resume_log_file()
        global test_file_analysis
        log.write(test_file_analysis)
        log_file_path = str(os.path.join(param.result_log_folder_path, "1.log"))
        expected_rows = [
            expectedHeader,
            expectedProjectRow,
            expectedBody,
        ]
        assert checkLogOutput(log_file_path, expected_rows)
        clean_up_log_tests()

    def test_log_no_available_continue(self):
        setup_log_tests()
        log.resume_log_file()
        global test_file_analysis
        log.write(test_file_analysis)
        log_file_path = str(os.path.join(param.result_log_folder_path, "0.log"))
        expected_rows = [
            expectedHeader,
            expectedProjectRow,
            expectedBody,
        ]
        assert checkLogOutput(log_file_path, expected_rows)
        clean_up_log_tests()

    def test_log_max_logs(self):
        setup_log_tests()
        for _ in range(param.log_max_count):
            log.open_log_file()
        log.open_log_file()
        global test_file_analysis
        log.write(test_file_analysis)
        log_file_path = str(
            os.path.join(param.result_log_folder_path, f"{param.log_max_count}.log")
        )
        expected_rows = [
            expectedHeader,
            expectedProjectRow,
            expectedBody,
        ]
        assert checkLogOutput(log_file_path, expected_rows)
        log_0_path = str(os.path.join(param.result_log_folder_path, "0.log"))
        assert not os.path.exists(log_0_path)
        clean_up_log_tests()

    def test_log_update_existing(self):
        setup_log_tests()
        log.open_log_file()
        global test_file_analysis
        log.write(test_file_analysis)
        modified_test_file_analysis = FileAnalysis(
            file_path=test_file_analysis.file_path,
            file_name=test_file_analysis.file_name,
            file_type=test_file_analysis.file_type,
            last_modified=test_file_analysis.last_modified,
            created_time=test_file_analysis.created_time,
            extra_data={"description": "UPDATED EXTRA DATA"},
            importance=0.0,
            customized=False,
            project_id=test_file_analysis.project_id,
            file_hash=test_file_analysis.file_hash,
        )
        log.update(modified_test_file_analysis)
        log_file_path = str(os.path.join(param.result_log_folder_path, "0.log"))
        with open(log_file_path, "r") as log_file:
            lines = [line.strip() for line in log_file.readlines()]
            print("Log file contents after update:")
            for line in lines:
                print(line)
            assert len(lines) == 3  # Header + project + one entry
            assert lines[0] == expectedHeader
            assert lines[1] == expectedProjectRow
            expected_updated_body = 'tests/testdata/fakeTestFile/file1.txt,file1.txt,txt,2023-10-01T12:00:00,2023-09-30T11:00:00,"{""description"": ""UPDATED EXTRA DATA""}",0.0,False,ID-1,x'
            assert lines[2] == expected_updated_body
        clean_up_log_tests()

    def test_log_update_no_file(self):
        setup_log_tests()
        global test_file_analysis
        log.update(test_file_analysis)
        log_file_path = str(os.path.join(param.result_log_folder_path, "0.log"))
        expected_rows = [
            expectedHeader,
            expectedProjectRow,
            expectedBody,
        ]
        assert checkLogOutput(log_file_path, expected_rows)
        clean_up_log_tests()

    def test_follow_log_reads_and_stops(self):
        """Test that follow_log reads existing lines and stops on !close! signal"""
        import threading
        import time

        setup_log_tests()
        log.open_log_file()
        global test_file_analysis
        log.write(test_file_analysis)
        log.write(test_file_analysis)

        log_file_path = str(os.path.join(param.result_log_folder_path, "0.log"))
        lines = []

        def append_lines_and_close():
            time.sleep(0.3)
            log.write(test_file_analysis)
            with open(log_file_path, "a", encoding="utf-8") as f:
                f.write("!close!\n")

        thread = threading.Thread(target=append_lines_and_close)
        thread.start()

        for line in log.follow_log(log_file_path, include_header=False):
            lines.append(line)

        thread.join()

        # Should have project row + 3 data rows + 1 close signal
        assert len(lines) == 5
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

        def send_close_signal():
            time.sleep(0.2)
            with open(log_file_path, "a", encoding="utf-8") as f:
                f.write("!close!\n")

        thread = threading.Thread(target=send_close_signal)
        thread.start()

        for line in log.follow_log(log_file_path, include_header=True):
            lines.append(line)

        thread.join()

        assert lines[0].startswith("File path analyzed")
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
            extra_data={"description": "SHOULD NOT UPDATE"},
            importance=0.0,
            customized=True,
            project_id=test_file_analysis_customized.project_id,
            file_hash=test_file_analysis_customized.file_hash,
        )
        log.update(modified_test_file_analysis)
        log_file_path = str(os.path.join(param.result_log_folder_path, "0.log"))
        with open(log_file_path, "r") as log_file:
            lines = [line.strip() for line in log_file.readlines()]
            print("Log file contents after blocked update:")
            for line in lines:
                print(line)
            assert len(lines) == 3  # Header + project + one entry
            assert lines[0] == expectedHeader
            assert (
                lines[1]
                == 'ID-2,ID-2,Project,,,"{""description"": """"}",0.0,False,ID-2,'
            )
            assert lines[2] == expectedBodyCustomized
        clean_up_log_tests()

    def test_get_all_log_files(self):
        setup_log_tests()
        log.open_log_file()
        log.write(test_file_analysis)
        log.open_log_file()
        log.write(test_file_analysis_customized)

        log_files = log._get_all_log_files()
        assert len(log_files) == 2

    def test_find_existing_analysis(self):
        setup_log_tests()
        log.open_log_file()
        log.write(test_file_analysis)

        fa = log.find_existing_analysis("x")
        assert fa is not None
        assert fa.file_name == "file1.txt"
        assert fa.file_hash == "x"
        clean_up_log_tests()


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
            extra_data={"description": f"DATA {idx}"},
            importance=0.0,
            customized=False,
            project_id=f"ID-{idx}",
            file_hash=f"hash{idx}",
        )
        log.write(entry)
        entry.extra_data = {"description": f"UPDATED DATA {idx}"}
        log.update(entry)

    def reader():
        time.sleep(0.1)
        with open(log_file_path, "r") as f:
            lines = f.readlines()
            read_results.append(lines)

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

    write_count = 10
    lines_written = []

    def writer(idx):
        entry = FileAnalysis(
            file_path=f"tests/testdata/fakeTestFile/file{idx}.txt",
            file_name=f"file{idx}.txt",
            file_type="txt",
            last_modified="2023-10-01T12:00:00",
            created_time="2023-09-30T11:00:00",
            extra_data={"description": f"DATA {idx}"},
            importance=0.0,
            customized=False,
            project_id=f"ID-{idx}",
            file_hash=f"hash{idx}",
        )
        log.write(entry)
        lines_written.append(entry)

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
    time.sleep(0.1)
    for w in writer_threads:
        w.start()
    for w in writer_threads:
        w.join()
    reader_thread.join(timeout=2)

    assert len(read_lines) == write_count
    for line in read_lines:
        parts = line.strip().split(",")
        assert len(parts) == 10  # Should match FileAnalysis fields

    clean_up_log_tests()


def test_get_project():
    setup_log_tests()
    log.open_log_file()

    entry1 = FileAnalysis(
        file_path="tests/testdata/fakeTestFile/fileA.txt",
        file_name="fileA.txt",
        file_type="txt",
        last_modified="2023-10-01T12:00:00",
        created_time="2023-09-30T11:00:00",
        extra_data={"description": "DATA A"},
        importance=0.0,
        customized=False,
        project_id="PROJECT-1",
        file_hash="hashA",
    )
    entry2 = FileAnalysis(
        file_path="tests/testdata/fakeTestFile/fileB.txt",
        file_name="fileB.txt",
        file_type="txt",
        last_modified="2023-10-02T12:00:00",
        created_time="2023-09-29T11:00:00",
        extra_data={"description": "DATA B"},
        importance=0.0,
        customized=False,
        project_id="PROJECT-2",
        file_hash="hashB",
    )
    log.write(entry1)
    log.write(entry2)

    project_entries = [
        e for e in log.get_project("PROJECT-1") if e.file_type != "Project"
    ]
    assert len(project_entries) == 1
    assert isinstance(project_entries[0], FileAnalysis)
    assert project_entries[0].file_name == "fileA.txt"
    assert project_entries[0].project_id == "PROJECT-1"

    project_entries = [
        e for e in log.get_project("PROJECT-2") if e.file_type != "Project"
    ]
    assert len(project_entries) == 1
    assert isinstance(project_entries[0], FileAnalysis)
    assert project_entries[0].file_name == "fileB.txt"
    assert project_entries[0].project_id == "PROJECT-2"

    clean_up_log_tests()
