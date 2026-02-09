from pathlib import Path
from unittest.mock import patch

import pytest

import src.param.param as param
import src.zip.zip_app as zip

path_to_test_zip = "tests/testdata/test_zip/testScanFolder.zip"


class TestZip:
    def test_zip_parse_zip(self):
        result = zip.extract_zip(path_to_test_zip)
        base_path = Path(param.program_file_path) / "zip"
        assert result is not None
        assert result.parent == base_path
        assert result.name.startswith("zip_")
        assert result.exists()
        assert zip.extract_zip("lalala") == None
        assert zip.extract_zip("tests/testdata") == None
        # TODO: update with zip response expected for a successful extract, currently uses the fss to scan and verify the file count, this verifies that the file is findable and contains the proper files
