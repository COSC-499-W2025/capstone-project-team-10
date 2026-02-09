import json
import pytest

from src.fas.fas_extra_data import get_file_extra_data


class TestFasUnknownFileType:
    # ------------------------------------------------------------
    # Unknown file type handling
    # ------------------------------------------------------------

    def test_unknown_filetype_returns_generic_metadata(self, tmp_path):
        """
        Unknown file extensions (e.g. .hello) should still return
        safe, generic metadata instead of None or crashing.
        """
        test_file = tmp_path / "example.hello"
        test_file.write_text("Some random content\nAnother line")

        data = get_file_extra_data(str(test_file), "hello")

        assert data is not None
        assert isinstance(data, dict)
        assert len(data) > 0   # generic metadata exists

    def test_unknown_filetype_empty_file(self, tmp_path):
        """
        Empty unknown files should still return metadata
        with zero-length content.
        """
        test_file = tmp_path / "empty.hello"
        test_file.write_text("")

        data = get_file_extra_data(str(test_file), "hello")

        assert data is not None
        assert isinstance(data, dict)

    def test_unknown_filetype_binary_safe(self, tmp_path):
        """
        Binary-like content should not raise exceptions.
        """
        test_file = tmp_path / "binary.hello"
        test_file.write_bytes(b"\x00\xFF\x00\xFF")

        data = get_file_extra_data(str(test_file), "hello")

        assert data is not None
        assert isinstance(data, dict)

    # ------------------------------------------------------------
    # JSON serializability
    # ------------------------------------------------------------

    def test_unknown_filetype_is_json_serializable(self, tmp_path):
        """
        Extra data for unknown file types must be JSON serializable
        to safely store in DB or send via API.
        """
        test_file = tmp_path / "example.hello"
        test_file.write_text("Hello world")

        data = get_file_extra_data(str(test_file), "hello")

        try:
            json.dumps(data)
        except (TypeError, ValueError) as e:
            pytest.fail(f"Unknown filetype extra_data is not JSON serializable: {e}")
