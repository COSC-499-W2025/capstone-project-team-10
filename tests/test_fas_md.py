from pathlib import Path
from unittest.mock import MagicMock, patch
import os

import pytest

from src.fas.fas_md import Markdown

md_path = os.path.join("tests", "testdata", "test_md", "test_markdown.md")

class TestMarkdown:
    @pytest.fixture(scope="module")
    def md(self):
        return Markdown(Path(md_path))

    @pytest.fixture
    def mock_text_summary(self):
        # Avoid expensive NLP calls in unit tests while keeping behavior checks.
        with patch("src.fas.fas_md.TextSummary") as mock_summary, patch(
            "src.fas.fas_md._extract_text_skills"
        ) as mock_extract:
            summary_instance = MagicMock()
            summary_instance.generate_text_analysis_data.return_value = {
                "complexity": "medium",
                "depth": "high",
                "structure": "clear",
                "sentiment_insight": "neutral",
            }
            mock_summary.return_value = summary_instance
            mock_extract.return_value = ["python", "analysis", "documentation"]
            yield

    # Test for headers
    def test_headers(self, md):
        headers = md.get_headers()["Header"]
        assert isinstance(headers, list)
        assert any(h["text"] == "Project Overview" for h in headers)
        assert any(h["text"] == "Data Description" for h in headers)
        assert any(h["level"] == 4 for h in headers)

    # Test for header hierarchy
    def test_header_hierarchy(self, md):
        header = md.get_header()
        assert isinstance(header, list)
        assert "Project Overview" in header
        assert all(isinstance(h, str) for h in header)

    # Test for wordcount
    def test_word_counts(self, md):
        count = md.get_word_counts()
        assert isinstance(count, int)
        assert count > 100  # reasonable sanity check

    # Tests that coding languages used is returned
    def test_code_blocks(self, md):
        languages = md.get_code_blocks()
        assert isinstance(languages, set)
        assert "python" in languages
        assert "r" in languages

    # Tests paragraphs, either a list of skills displayed.
    def test_paragraphs(self, md, mock_text_summary):
        skills = md.get_paragraphs()
        assert isinstance(skills, list)
        assert all(isinstance(skill, str) for skill in skills)

    # Test to ensure data is returned in the correct format
    def test_integration_structure(self, md, mock_text_summary):
        assert isinstance(md.get_headers(), dict)
        assert isinstance(md.get_header(), list) 
        assert isinstance(md.get_code_blocks(), set)
        paras = md.get_paragraphs()
        assert paras is None or isinstance(paras, list)
        assert isinstance(md.get_word_counts(), int)