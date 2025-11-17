import pytest
import os
import src.fss.fss as fss
from unittest.mock import patch

path_to_test_folder = "tests/testdata/test_fss/testScanFolder"
path_to_entire_test_folder = "tests/testdata/test_fss/"
path_to_test_file = "tests/testdata/test_fss/testScanFile"
path_to_excluded_file = (
    "tests/testdata/test_fss/testScanFolder/nestedFolder/nestedFile2"
)
path_to_excluded_folder = "tests/testdata/test_fss/testScanFolder/nestedFolder"
path_to_invalid_folder = "/DUMMMMMMMMMY/DUMMY/DUMB/DUMMY"


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
        fss.clear_cache()

        result1 = fss.search(path_to_test_file, None)
        assert result1 == 1

        assert os.path.exists(fss.CACHE_PATH)

        result2 = fss.search(path_to_test_file, None)
        assert result2 == 0

        with open(path_to_test_file, "a") as f:
            f.write("\nmodified lol")

        result3 = fss.search(path_to_test_file, None)
        assert result3 == 1