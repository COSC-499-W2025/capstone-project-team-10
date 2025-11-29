import datetime
import pytest
import os
import src.fas.fas_odt as fas

odt_file_path = os.path.join("tests", "testdata", "test_fas","fas_odt_data.odt")

class TestFasRtf:
    def test_odt_content(self):
        result = fas.extract_odt_data(odt_file_path)
        assert result["author"] == "testAuthor"
        assert result["title"] == "odtTitle"
        assert result["subject"] == "odt"
        assert result["created"] == datetime.datetime(2025, 11, 3, 0, 38, tzinfo=datetime.timezone.utc)
        assert result["modified"] == datetime.datetime(2025, 11, 3, 2, 41, tzinfo=datetime.timezone.utc)
        assert result["num_paragraphs"] == 5
        assert result["num_chars"] == 77
        assert result["num_words"] == 14
        assert result["filtered_word_count"] == 8
        assert result["unique_words"] == 8
        assert result["sentence_count"] == 1
        assert result["lexical_diversity"] == 1.0
        assert result["top_keywords"] == [("test", 1), ("labeeskneez", 1), ("wawaweewa", 1), ("lorem", 1), ("ipsum", 1), ("got", 1), ("games", 1), ("phone", 1)]
        assert result["sentiment"] == "neutral"
        assert result["sentiment_score"] == 0.0
        assert result["named_entities"] == [('Labeeskneez Wawaweewa Lorem', 'PERSON')]
        assert result["summary"] == "This is a test\nLabeeskneez\nWawaweewa\nLorem ipsum\nYou got games on your phone?"
        assert result["complexity"] == 'High - Advanced vocabulary, excellent vocabulary, varied and diverse word choices.'
        assert result["depth"] == 'Consider adding more detail to fully develop your ideas.' 
        assert result["structure"] == 'Consider combining related ideas for better flow.'
        assert result["sentiment_insight"] == 'Overall neutral sentiment within your writing. Professional standard sentiment of writing, if you are aiming for a more positive or negative sentiment consider changing your word choices.'

    def test_invalid_odt_file(self):
        result = fas.extract_odt_data("tests/testdata/test_fas/fas_docx_test.docx")
        assert "error" in result
        assert isinstance(result["error"], str)