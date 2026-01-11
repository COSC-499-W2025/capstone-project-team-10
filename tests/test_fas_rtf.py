import datetime
import pytest
import os
import src.fas.fas_rtf as fas

rtf_file_path = os.path.join("tests", "testdata", "test_fas","fas_rtf_data.rtf")

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

    def test_rtf_content(self):
        result = fas.extract_rtf_data(rtf_file_path)
        assert result["author"] == "testAuthor"
        assert result["title"] == "rtfData"
        assert result["subject"] == "rtf"
        assert result["created"] == datetime.datetime(2025, 11, 2, 14, 55)
        assert result["modified"] == datetime.datetime(2025, 11, 2, 15, 3)
        assert result["num_chars"] == 43
        assert result["num_words"] == 9
        assert result["num_paragraphs"] == 3
        assert result["filtered_word_count"] == 5
        assert result["unique_words"] == 5
        assert result["sentence_count"] == 1
        assert result["lexical_diversity"] == 1.0
        assert result["top_keywords"] == [("rtf", 1), ("file", 1), ("thumbs", 1), ("cat", 1), ("emoji", 1)]
        assert result["sentiment"] == "neutral"
        assert result["sentiment_score"] == 0.0
        assert len(result["named_entities"]) == 2
        assert result["summary"] == "This is an RTF file\n\nThumbs up\n\nCat emoji."
        assert result["complexity"] == 'High - Advanced vocabulary, excellent vocabulary, varied and diverse word choices.'
        assert result["depth"] == 'Consider adding more detail to fully develop your ideas.'
        assert result["structure"] == 'Consider combining related ideas for better flow.'
        assert result["sentiment_insight"] == 'Overall neutral sentiment within your writing. Professional standard sentiment of writing, if you are aiming for a more positive or negative sentiment consider changing your word choices.'

    def test_invalid_rtf_file(self):
        result = fas.extract_rtf_data("notaRealpath")
        assert "error" in result
        assert isinstance(result["error"], str)