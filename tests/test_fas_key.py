import os
import datetime
import pytest
from src.fas import fas

TEST_FILE = "tests/testdata/test_fas/fas_test_data.docx"

class TestFasKey:

    def test_run_fas_returns_file_analysis(self):
        # run_fas should return a FileAnalysis object for a valid file
        result = fas.run_fas(TEST_FILE)
        assert result is not None
        assert isinstance(result, fas.FileAnalysis)

    def test_file_name(self):
        # Check that the correct file name is extracted
        result = fas.run_fas(TEST_FILE)
        assert result.file_name == "fas_test_data.docx"

    def test_file_type(self):
        # Check that the file type is correct (from extension)
        result = fas.run_fas(TEST_FILE)
        assert result.file_type == "docx"

    
