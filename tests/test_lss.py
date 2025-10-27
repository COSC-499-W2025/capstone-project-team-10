import pytest
import src.lss.lss_app as lss
from unittest.mock import patch
file_one = "tests/testdata/test_lss/testStoreFileOne.txt"
file_two = "tests/testdata/test_lss/testStoreFileTwo.txt"

class TestLss:
    def test_storage_write(self):
        #TODO: update log storage service to update and write an initial storage log.
        with patch('builtins.print') as mock_print:
            lss.lss_store(file_one)
            # response shall be that a specific log was stored.
            mock_print.assert_called_with(file_one + " stored.")

    def test_storage_overwrite(self):
        #TODO: update log storage service to update and overwrite an initial storage with another log.
        with patch('builtins.print') as mock_print:
            lss.lss_store(file_one)
            lss.lss_store(file_two)
            # response shall be that the second specific log was stored.
            mock_print.assert_called_with(file_two + " stored.")

    def test_storage_noChange(self):
        #TODO: update log storage service to not change when given the same file.
        with patch('builtins.print') as mock_print:
            lss.lss_store(file_one)
            resultOne = mock_print(file_one + " stored.")
            lss.lss_store(file_one)
            resultTwo = mock_print(file_one + " stored.")
            # response shall be that the two logs return the same response.
            assert resultOne == resultTwo