import pytest
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
        result = fss.search(path_to_test_file, None)
        # Assert that the number of files searched is equal to the expect value
        assert result == 1

    def test_fss_folder(self):
        # TODO: update this function call according to implementation
        result = fss.search(path_to_entire_test_folder, None)
        # Assert that the number of files searched is equal to the expect value
        assert result == 3

    def test_fss_excluded_file(self):
        # TODO: update this function call according to implementation
        result = fss.search(path_to_entire_test_folder, path_to_excluded_file)
        assert result == 2

    def test_fss_excluded_folder(self):
        # TODO: update this function call according to implementation
        result = fss.search(path_to_test_folder, path_to_excluded_folder)
        assert result == 1

    def test_fss_invalid_path(self):
        # TODO: update this function call according to implementation
        result = fss.search(path_to_invalid_folder, None)
        # update this result according to implementation
        assert result == -1
