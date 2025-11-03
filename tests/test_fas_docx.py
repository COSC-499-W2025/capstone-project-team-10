import pytest
import datetime
import src.fas.fas_docx as fas
from unittest.mock import patch

docx_file_path = "tests/testdata/test_fas/fas_docx_test.docx"

class TestFasDocx:
    def test_docx_content(self):
        result = fas.extract_docx_data(docx_file_path)
        assert result["author"] == "testAuthor"
        assert result["title"] == "This is a title"
        assert result["subject"] == "test"
        assert result["created"] == datetime.datetime(2025, 11, 2, 21, 10, tzinfo=datetime.timezone.utc)
        assert result["modified"] == datetime.datetime(2025, 11, 2, 21, 43, tzinfo=datetime.timezone.utc)
        assert result["num_paragraphs"] == 6
        assert result["num_chars"] == 25
        assert result["num_words"] == 9
           

