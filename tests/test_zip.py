from pathlib import Path
import pytest
import src.zip.zip_app as zip
import src.fss.fss as fss
from unittest.mock import patch

path_to_test_zip = "tests/testdata/test_zip/testScanFolder.zip"


class TestZip:
    def test_zip_parse_zip(self):
        result = zip.extract_zip(path_to_test_zip)
        assert result == Path("src/zip/zipfolders")
        assert zip.extract_zip("lalala") == None
        assert zip.extract_zip("tests/testdata") == None
        # TODO: update with zip response expected for a successful extract, currently uses the fss to scan and verify the file count, this verifies that the file is findable and contains the proper files    
        #assert fss.search(result) == 2
