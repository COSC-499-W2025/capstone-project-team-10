import datetime
import pytest
import src.fas.fas_odt as fas

rtf_file_path = "tests/testdata/test_fas/fas_odt_data.odt"

class TestFasRtf:
    def test_odt_content(self):
        result = fas.extract_odt_data(rtf_file_path)
        assert result["author"] == "testAuthor"
        assert result["title"] == "odtTitle"
        assert result["subject"] == "odt"
        assert result["created"] == datetime.datetime(2025, 11, 3, 0, 38, tzinfo=datetime.timezone.utc)
        assert result["modified"] == datetime.datetime(2025, 11, 3, 2, 41, tzinfo=datetime.timezone.utc)
        assert result["num_paragraphs"] == 5
        assert result["num_chars"] == 77
        assert result["num_words"] == 14

    def test_invalid_odt_file(self):
        result = fas.extract_odt_data("tests/testdata/test_fas/fas_docx_test.docx")
        assert "error" in result
        assert isinstance(result["error"], str)