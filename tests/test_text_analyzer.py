import pytest
import os
import src.fas.fas_text_analysis as ta
from unittest.mock import patch

TESTFILE1 = os.path.join("tests", "testdata", "test_utils", "Report.pdf")

class TestTextAnalyzer:

    def test_text_summary_initialization(self):
        # Read a real file to pass text content to TextSummary
        with open(TESTFILE1, 'r', encoding = 'utf-8', errors = 'replace') as f:
            content = f.read()
        summary = ta.TextSummary(content)
        assert summary.text == content
        assert isinstance(summary.sentences, list)
        assert isinstance(summary.words, list)

    def test_empty_string(self):
        ts = ta.TextSummary("")
        assert ts.getCommonWords(5) == []
        assert ts.getNamedEntities() == set()

        sentiment = ts.getSentiment()
        assert sentiment['sentiment'] == 'neutral'
        assert sentiment['compound_score'] == 0.0

        assert ts.getSummary(5) == ""

        stats = ts.getStatistics()
        assert stats['word_count'] == 0
        assert stats['unique_words'] == 0
        assert stats['sentence_count'] == 0
        assert stats['lexical_diversity'] == 0

    def test_common_words(self):
        text = "Cat dog cat bird."
        ts = ta.TextSummary(text)
        top_words = ts.getCommonWords(2)
        assert top_words[0][0] == "cat"
        assert top_words[0][1] == 2
    
    def test_sentiment(self):
        text = "I love sunny days. I hate rain."
        ts = ta.TextSummary(text)
        sentiment = ts.getSentiment()
        assert sentiment['sentiment'] in {"positive", "negative", "neutral"}

    def test_summary(self):
        text = "Hello world. This is a test sentence. Another sentence."
        ts = ta.TextSummary(text)
        summary = ts.getSummary(2)
        assert isinstance(summary, str)
        assert len(summary) > 0

    def test_named_entities(self):
        text = "Barry went to Waxville."
        ts = ta.TextSummary(text)
        entities = ts.getNamedEntities()

        # Basic assertions: both PERSON and GPE should appear
        entity_names = {name for name, _type in entities}
        entity_types = {_type for name, _type in entities}

        assert "Barry" in entity_names
        assert "Waxville" in entity_names
        assert "PERSON" in entity_types
        assert "GPE" in entity_types