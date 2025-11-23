import pytest
import datetime
import src.fas.fas_docx as fas

docx_file_path = "tests/testdata/test_fas/fas_docx_test.docx"

class TestFasDocx:
    def test_docx_content(self):
        result = fas.extract_docx_data(docx_file_path)
        assert result["author"] == "testAuthor"
        assert result["title"] == "This is a title"
        assert result["subject"] == "test"
        assert result["created"] == datetime.datetime(2025, 11, 2, 21, 10, tzinfo=datetime.timezone.utc)
        assert result["modified"] == datetime.datetime(2025, 11, 2, 21, 43, tzinfo=datetime.timezone.utc)
        assert result['keywords'] == ''
        assert result['category'] == ''
        assert result['comments'] == '' 
        assert result["num_paragraphs"] == 6
        assert result['num_tables'] == 0
        assert result["num_chars"] == 25
        assert result["num_words"] == 9
        assert result['filtered_word_count'] == 3
        assert result['unique_words'] == 3
        assert result['sentence_count'] == 1
        assert result['lexical_diversity'] == 1.0
        assert result['top_keywords'] == [('title', 1), ('b', 1), ('c', 1)]
        assert result['sentiment'] == 'neutral'
        assert result['sentiment_score'] == 0.0
        assert result['named_entities'] == []
        assert result['summary'] == 'This is a title\nA\nB\nC\nD\n6'

    def test_invalid_docx_file(self):
        result = fas.extract_docx_data("tests/testdata/test_fas/fas_rtf_data.rtf")
        assert "error" in result
        assert isinstance(result["error"], str)
           

