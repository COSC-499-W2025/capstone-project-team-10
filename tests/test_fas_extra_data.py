import os
import json
import pytest
from unittest.mock import MagicMock, patch

from src.fas.fas_extra_data import (
    get_file_extra_data,
    feedback_to_skill,
)


class TestFasExtraData:
    # ------------------------------------------------------------
    # feedback_to_skill
    # ------------------------------------------------------------

    @pytest.mark.parametrize(
        "feedback, expected",
        [
            ("High - Advanced Vocabulary detected", "Advanced Vocabulary"),
            ("Medium - Standard Vocabulary", "Strong Vocabulary"),
            ("Low - Simple Vocabulary", "Basic Vocabulary"),
            ("Overall positive sentiment", "Positive Tone"),
            ("Overall neutral sentiment", "Professional Tone"),
            ("Overall negative sentiment", "Emotive Writing"),
            ("Breaking up complex sentences recommended", "Complex Sentence Structure"),
            ("Unknown feedback", None),
            ("", None),
            (None, None),
        ],
    )
    def test_feedback_to_skill(self, feedback, expected):
        assert feedback_to_skill(feedback) == expected

    # ------------------------------------------------------------
    # Code file handling
    # ------------------------------------------------------------

    def test_code_file_extra_data(self, tmp_path, monkeypatch):
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")

        class MockCodeReader:
            def __init__(self, path):
                self.filetype = "python"
                self.libraries = ["numpy"]
                self.complexity = {"estimated": "O(n)"}
                self.oop = {"classes": True, "functions": True}

        monkeypatch.setattr(
            "src.fas.fas_extra_data.CodeReader",
            MockCodeReader,
        )

        data = get_file_extra_data(str(test_file), "py")

        assert data is not None
        assert data["language"] == "python"
        assert "numpy" in data["libraries"]
        assert "Object-oriented programming (OOP)" in data["key_skills"]
        assert "Algorithmic complexity analysis" in data["key_skills"]

    # ------------------------------------------------------------
    # Markdown handling
    # ------------------------------------------------------------

    def test_markdown_extra_data(self, tmp_path, monkeypatch):
        test_file = tmp_path / "test.md"
        test_file.write_text("# Header\n\nSome text")

        class MockMarkdown:
            def __init__(self, path):
                pass

            def get_headers(self):
                return ["Header"]

            def get_header_hierarchy(self):
                return {"Header": []}

            def get_word_counts(self):
                return 3

            def get_code_blocks(self):
                return []

            def get_paragraphs(self):
                return ["Some text"]

        monkeypatch.setattr(
            "src.fas.fas_extra_data.Markdown",
            MockMarkdown,
            raising=False,
        )

        data = get_file_extra_data(str(test_file), "md")

        assert data is not None
        assert "Header" in data["headers"]
        assert data["word_count"] == 4
        assert "paragraphs" in data

    # ------------------------------------------------------------
    # PDF / DOCX-style metadata post-processing
    # ------------------------------------------------------------

    def test_text_metadata_skill_extraction_and_summary_cleanup(self, tmp_path):
        test_file = tmp_path / "test.pdf"
        test_file.write_text("fake pdf")

        fake_metadata = {
            "summary": "Line 1\nLine 2",
            "complexity": "High - Advanced Vocabulary",
            "sentiment_insight": "Overall positive sentiment",
        }

        with patch(
            "src.fas.fas_pdf.extract_pdf_data",
            return_value=fake_metadata.copy(),
        ):
            data = get_file_extra_data(str(test_file), "pdf")

        assert data is not None
        assert "\n" not in data["summary"]
        assert "Advanced Vocabulary" in data["key_skills"]
        assert "Positive Tone" in data["key_skills"]



    # ------------------------------------------------------------
    # Unsupported file types
    # ------------------------------------------------------------

    def test_unsupported_file_type_returns_none(self, tmp_path):
        test_file = tmp_path / "file.xyz"
        test_file.write_text("data")

        data = get_file_extra_data(str(test_file), "xyz")
        assert data is None

    # ------------------------------------------------------------
    # JSON serializability
    # ------------------------------------------------------------

    def test_extra_data_is_json_serializable(self, tmp_path, monkeypatch):
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")

        class MockCodeReader:
            def __init__(self, path):
                self.filetype = "python"
                self.libraries = []
                self.complexity = {}
                self.oop = {}

        monkeypatch.setattr(
            "src.fas.fas_extra_data.CodeReader",
            MockCodeReader,
        )

        data = get_file_extra_data(str(test_file), "py")

        try:
            json.dumps(data)
        except (TypeError, ValueError) as e:
            pytest.fail(f"extra_data is not JSON serializable: {e}")
