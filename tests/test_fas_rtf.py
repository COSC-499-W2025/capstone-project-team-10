import datetime
import pytest
import fas.fas_rtf as fas

rtf_file_path = "tests/testdata/test_fas/fas_rtf_data.rtf"

class TestFasRtf:
    def test_extract_datetime(self):
        rtf = r"{\creatim\yr2025\mo11\dy2\hr14\min55}"
        dt = fas.extract_datetime(rtf, "creatim")
        assert dt == datetime.datetime(2025, 11, 2, 14, 55)

    def test_extract_no_datetime(self):
        rtf = r"{\rtf1 This has no datetime block }"
        dt = fas.extract_datetime(rtf, "creatim")
        assert dt is None

    def test_extract_specific_data(self):
        rtf = r"{\title rtfData}"
        value = fas.extract_specific_data(rtf, "title")
        assert value == "rtfData"

    def test_extract_specific_no_data(self):
        rtf = r"{\rtf1 }"
        value = fas.extract_specific_data(rtf, "title")
        assert value is None

    def test_docx_content(self):
        result = fas.extract_rtf_data(rtf_file_path)
        assert result["author"] == "testAuthor"
        assert result["title"] == "rtfData"
        assert result["subject"] == "rtf"
        assert result["created"] == datetime.datetime(2025, 11, 2, 14, 55)
        assert result["modified"] == datetime.datetime(2025, 11, 2, 15, 3)
        assert result["num_chars"] == 43
        assert result["num_words"] == 9
        assert result["num_paragraphs"] == 3

    def test_invalid_rtf_file(self):
        result = fas.extract_rtf_data("tests/testdata/test_fas/fas_docx_test.docx")
        assert "error" in result
        assert isinstance(result["error"], str)