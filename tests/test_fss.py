import os
from pathlib import Path
from unittest.mock import patch
from src.fas.fas import analyze_file
import src.log.log as log
import pytest
import src.param.param as param
import src.fss.fss as fss

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

def clean_log_folder():
    import shutil

    log_folder = str(param.result_log_folder_path)
    if os.path.exists(log_folder):
        shutil.rmtree(log_folder)
    os.makedirs(log_folder)
class TestFSS:
    def test_fss_single_file(self):
        # TODO: update this function call according to implementation
        result = fss.search(path_to_test_file, None, True)
        # Assert that the number of files searched is equal to the expect value
        assert result == 1

    def test_fss_folder(self):
        # TODO: update this function call according to implementation
        result = fss.search(path_to_entire_test_folder, None, True)
        # Assert that the number of files searched is equal to the expect value
        assert result == 3

    def test_fss_excluded_file(self):
        # TODO: update this function call according to implementation
        result = fss.search(path_to_entire_test_folder, path_to_excluded_file, True)
        assert result == 2

    def test_fss_excluded_folder(self):
        # TODO: update this function call according to implementation
        result = fss.search(path_to_test_folder, path_to_excluded_folder, True)
        assert result == 1

    def test_fss_invalid_path(self):
        # TODO: update this function call according to implementation
        result = fss.search(path_to_invalid_folder, None, True)
        # update this result according to implementation
        assert result == -1

    def test_delta_scan(self):
        param.init()

        logs_dir = Path(param.result_log_folder_path)
        if logs_dir.exists():
            for f in logs_dir.iterdir():
                if f.is_file:
                    f.unlink
        else:
            logs_dir.mkdir(parents=True, exist_ok=True)
        
        print(logs_dir)
        log.resume_log_file()

        result1 = fss.search(path_to_test_file, None)
        assert result1 == 1

        assert any(logs_dir.iterdir())
        fa = analyze_file(path_to_test_file)
        assert fa is not None
        log.write(fa)

        result2 = fss.search(path_to_test_file, None)
        assert result2 == 0

        with open(path_to_test_file, "a") as f:
            f.write("\nmodified lol")

        result3 = fss.search(path_to_test_file, None)
        assert result3 == 1
        clean_log_folder()
