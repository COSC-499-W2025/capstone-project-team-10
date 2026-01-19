from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.fas.fas_md import Markdown


class TestMarkdown:
    @pytest.fixture(scope="module")
    def md(self):
        return Markdown(Path("tests/testdata/test_md/test_markdown.md"))

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

    # Tests that coding languages used is returned
    def test_code_blocks(self, md):
        languages = md.get_code_blocks()
        assert isinstance(languages, set)
        assert "python" in languages
        assert "r" in languages

    # Tests paragraphs, either a list of skills displayed.
    def test_paragraphs(self, md):
        skills = md.get_paragraphs()
        assert isinstance(skills, list)
        assert all(isinstance(skill, str) for skill in skills)

    # Test to ensure data is returned in the correct format
    def test_integration_structure(self, md):
        assert isinstance(md.get_headers(), dict)
        assert isinstance(md.get_header(), list) 
        assert isinstance(md.get_code_blocks(), set)
        paras = md.get_paragraphs()
        assert paras is None or isinstance(paras, list)
        assert isinstance(md.get_word_counts(), int)

    # Tests to make sure that only the top level header is output
    def test_header_top_level_only(self, md):
        header = md.get_header()
        assert len(header) >= 1
        assert all(isinstance(h, str) for h in header)