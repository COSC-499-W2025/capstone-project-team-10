import os
from pathlib import Path
from unittest.mock import patch
import src.param.param as param
import src.log.log as log
import src.fas.fas as fas

import pytest

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

    try:
        log_folder = str(param.result_log_folder_path)
    except Exception:
        print("oopsie")
    if os.path.exists(log_folder):
        shutil.rmtree(log_folder)
    os.makedirs(log_folder)

def setup_log_tests():
    param.init()
    clean_log_folder()

class TestFSS:
    def test_fss_single_file(self):
        setup_log_tests()
        # TODO: update this function call according to implementation
        result = fss.search(fss.FSS_Search(path_to_test_file))
        # Assert that the number of files searched is equal to the expect value
        assert result == 1
        clean_log_folder()
        
    def test_fss_folder(self):
        setup_log_tests()
        # TODO: update this function call according to implementation
        result = fss.search(fss.FSS_Search(path_to_entire_test_folder))
        # Assert that the number of files searched is equal to the expect value
        assert result == 3
        clean_log_folder()

    def test_fss_excluded_file(self):
        setup_log_tests()
        # TODO: update this function call according to implementation
        result = fss.search(
            fss.FSS_Search(path_to_entire_test_folder, set([path_to_excluded_file]))
        )
        assert result == 2
        clean_log_folder()

    def test_fss_excluded_folder(self):
        setup_log_tests()
        # TODO: update this function call according to implementation
        result = fss.search(
            fss.FSS_Search(path_to_test_folder, set([path_to_excluded_folder]))
        )
        assert result == 1
        clean_log_folder()

    def test_fss_invalid_path(self):
        setup_log_tests()
        # TODO: update this function call according to implementation
        result = fss.search(fss.FSS_Search(path_to_invalid_folder))
        # update this result according to implementation
        assert result == -1
        clean_log_folder()

    def test_delta_scan(self):
        param.init()
        log.resume_log_file()

        result1 = fss.search(fss.FSS_Search(path_to_test_file))
        assert result1 == 1

        fa = fas.analyze_file(path_to_test_file)
        assert fa is not None
        log.write(fa)

        result2 = fss.search(fss.FSS_Search(path_to_test_file))
        assert result2 == 0

        with open(path_to_test_file, "a") as f:
            f.write("\nmodified lol")

        result3 = fss.search(fss.FSS_Search(path_to_test_file))
        assert result3 == 1
        clean_log_folder()