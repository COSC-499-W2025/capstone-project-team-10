from asyncio.tasks import sleep
from pathlib import Path
from unittest.mock import patch

import pytest

import src.fss.fss as fss
import src.log.log as log
import src.param.param as param
from src.fas.fas import FileAnalysis, compute_file_hash

path_to_test_folder = str(Path("tests/testdata/test_fss/testScanFolder"))
path_to_entire_test_folder = str(Path("tests/testdata/test_fss/"))
path_to_test_file = str(Path("tests/testdata/test_fss/testScanFile"))
path_to_excluded_file = str(
    Path("tests/testdata/test_fss/testScanFolder/nestedFolder/nestedFile2")
)
path_to_excluded_folder = str(
    Path("tests/testdata/test_fss/testScanFolder/nestedFolder")
)
path_to_invalid_folder = str(Path("/DUMMMMMMMMMY/DUMMY/DUMB/DUMMY"))
path_to_test_zip = str(Path("tests/testdata/test_fss_zip/testzip.zip"))


@pytest.fixture(autouse=True, scope="function")
def setup():
    param.init()
    log.open_log_file()
    yield
    log_folder = Path(param.result_log_folder_path)
    if log_folder.exists() and log_folder.is_dir():
        for file in log_folder.iterdir():
            if file.is_file():
                file.unlink()


class TestFSS:
    def test_fss_single_file(self):
        # TODO: update this function call according to implementation
        result = fss.search(fss.FSS_Search(path_to_test_file))
        # Assert that the number of files searched is equal to the expect value
        assert result == 1

    def test_fss_folder(self):
        # TODO: update this function call according to implementation
        result = fss.search(fss.FSS_Search(path_to_entire_test_folder))
        # Assert that the number of files searched is equal to the expect value
        assert result == 3

    def test_fss_excluded_file(self):
        # TODO: update this function call according to implementation
        result = fss.search(
            fss.FSS_Search(path_to_entire_test_folder, set([path_to_excluded_file]))
        )
        assert result == 2

    def test_fss_excluded_folder(self):
        # TODO: update this function call according to implementation
        result = fss.search(
            fss.FSS_Search(path_to_test_folder, set([path_to_excluded_folder]))
        )
        assert result == 1

    def test_fss_invalid_path(self):
        # TODO: update this function call according to implementation
        result = fss.search(fss.FSS_Search(path_to_invalid_folder))
        # update this result according to implementation
        assert result == -1

    def test_fss_delta_scan_no_change(self):
        print(f"Current log file: {log.current_log_file}")
        # First scan to populate log
        result_1 = fss.search(fss.FSS_Search(path_to_entire_test_folder))
        assert result_1 == 3
        # Second scan should scan and skip previously scanned files
        result_2 = fss.search(fss.FSS_Search(path_to_entire_test_folder))
        assert result_2 == 0

    def test_fss_delta_scan(self):
        # First scan to populate log
        result_1 = fss.search(fss.FSS_Search(path_to_test_folder))
        assert result_1 == 2
        # Second scan should scan and skip previously scanned files
        result_2 = fss.search(fss.FSS_Search(path_to_entire_test_folder))
        assert result_2 == 1
        # Modify a file to force a re-scan
        test_file_path = Path(path_to_test_file)
        with open(test_file_path, "a", encoding="utf-8") as test_file:
            test_file.write("\nAdding a new line to force modification.")
        # test scan again
        result_3 = fss.search(fss.FSS_Search(path_to_entire_test_folder))
        assert result_3 == 1
        # remove change
        with open(test_file_path, "r", encoding="utf-8") as test_file:
            lines = test_file.readlines()
        with open(test_file_path, "w", encoding="utf-8") as test_file:
            test_file.writelines(lines[:-2])

    def test_get_duplicate_from_log(self, tmp_path):

        test_file = tmp_path / "test.txt"
        test_file.write_text("hello world")

        file_hash = compute_file_hash(test_file)

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
        file_hash=file_hash,
        )

        log.write(test_file_analysis)
        result = fss.get_duplicate_from_log(test_file)
        assert result is not None
        assert result.file_hash == test_file_analysis.file_hash

    def test_get_duplicate_from_log_non_duplicate(self, tmp_path):
        test_file = tmp_path / "hashdupe.txt"
        test_file.write_text("does not exist")

        result = fss.get_duplicate_from_log(str(test_file))
        assert result is None
    def test_fss_zip_file(self):
        """Test that search can extract and scan files from a zip archive."""
        result = fss.search(fss.FSS_Search(path_to_test_zip))
        assert result == 3

    def test_fss_zip_with_txt_filter(self):
        """Test that .txt filter works inside zip files."""
        result = fss.search(fss.FSS_Search(
            path_to_test_zip,
            file_types={"txt"}
        ))
        assert result == 1

    def test_fss_zip_with_multiple_filters(self):
        """Test that multiple file type filters work inside zip files."""
        result = fss.search(fss.FSS_Search(
            path_to_test_zip,
            file_types={"txt","md"}
        ))
        assert result == 2
