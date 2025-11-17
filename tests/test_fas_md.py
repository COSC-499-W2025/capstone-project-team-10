import pytest
from src.fas.fas_md import Markdown
from unittest.mock import patch, MagicMock
from pathlib import Path

class TestMarkdown:
    @pytest.fixture(scope="module")
    def md(self):
        return Markdown("../tests/testdata/test_md/test_markdown.md")


    def test_headers(self, md):
        headers = md.get_headers()["Header"]
        # should find all headers (#, ##, ###, ####)
        assert isinstance(headers, list)
        assert any(h["text"] == "Project Overview" for h in headers)
        assert any(h["text"] == "Data Description" for h in headers)
        assert any(h["level"] == 4 for h in headers)  # Preprocessing Steps is ####


    def test_header_hierarchy(self, md):
        hierarchy = md.get_header_hierarchy()
        assert isinstance(hierarchy, list)
        # top-level header
        assert hierarchy[0]["title"] == "Project Overview"
        # nested under Introduction → Background
        intro = next(node for node in hierarchy[0]["children"] if node["title"] == "Introduction")
        background = next(child for child in intro["children"] if child["title"] == "Background")
        assert background["children"] == []


    def test_word_counts(self, md):
        count = md.get_word_counts()
        assert isinstance(count, int)
        assert count > 100  # reasonable sanity check


    def test_code_blocks(self, md):
        blocks = md.get_code_blocks()["Code block"]
        assert isinstance(blocks, list)
        assert any(b["language"] == "python" for b in blocks)
        assert any(b["language"] == "r" for b in blocks)
        # confirm expected snippet content appears
        python_block = next(b for b in blocks if b["language"] == "python")
        assert "pd.read_csv" in python_block["content"]


    def test_paragraphs(self, md):
        paras = md.get_paragraphs()["Paragraph"]
        assert isinstance(paras, list)
        assert any("**mrkdown-analysis**" in p for p in paras)
        assert any("![Chart Example]" in p for p in paras)


    def test_integration_structure(self, md):
        # full integration: all parts return valid structured data
        assert isinstance(md.get_headers(), dict)
        assert isinstance(md.get_header_hierarchy(), list)
        assert isinstance(md.get_code_blocks(), dict)
        assert isinstance(md.get_paragraphs(), dict)
        assert isinstance(md.get_word_counts(), int)