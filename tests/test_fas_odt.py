import datetime
import pytest
import fas.fas_odt as fas

rtf_file_path = "tests/testdata/test_fas/fas_odt_data.odt"

class TestFasRtf:
    def test_invalid_odt_file(self):
        result = fas.extract_odt_data("tests/testdata/test_fas/fas_docx_test.docx")
        assert "error" in result
        assert isinstance(result["error"], str)