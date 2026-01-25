import pytest
import pandas as pd
from pathlib import Path
from src.gui.log_iterator_addor import LogIteratorAddor

class TestLogIteratorAddor:

    # Mock file - basic .log (CSV) with two rows
    @pytest.fixture
    def sample_log(self, tmp_path):
        data = [
            {
                "File path analyzed": r"C:\repo\file1.py",
                "File name": "file1.py",
                "File type": "py",
                "Last modified": "2024-01-01T00:00:00",
                "Created time": "2024-01-01T00:00:00",
                "Extra data": "{}",
                "Importance": 10.0,
            },
            {
                "File path analyzed": r"C:\repo\file2.js",
                "File name": "file2.js",
                "File type": "js",
                "Last modified": "2024-01-02T00:00:00",
                "Created time": "2024-01-02T00:00:00",
                "Extra data": "{}",
                "Importance": 7.5,
            },
        ]
        path = tmp_path / "sample.log"
        pd.DataFrame(data).to_csv(path, index=False)
        return path

    # Test iteration (__iter__ / __next__)
    def test_iteration(self, sample_log):
        log = LogIteratorAddor(sample_log)
        rows = list(log)
        assert len(rows) == 2
        assert rows[0]["File name"] == "file1.py"
        assert rows[1]["File name"] == "file2.js"
        # iterator resets on re-iteration
        assert [r["File name"] for r in log] == ["file1.py", "file2.js"]

    # Test add_row appends and updates length
    def test_add_row(self, sample_log):
        log = LogIteratorAddor(sample_log)
        before = len(log)
        log.add_row(
            {
                "File path analyzed": r"C:\repo\new.py",
                "File name": "new.py",
                "File type": "py",
                "Last modified": "2024-01-03T00:00:00",
                "Created time": "2024-01-03T00:00:00",
                "Extra data": "{}",
                "Importance": 9.0,
            }
        )
        assert len(log) == before + 1
        assert log[-1]["File name"] == "new.py"

    # Test add_rows appends multiple
    def test_add_rows(self, sample_log):
        log = LogIteratorAddor(sample_log)
        log.add_rows(
            [
                {
                    "File path analyzed": r"C:\repo\a.py",
                    "File name": "a.py",
                    "File type": "py",
                    "Last modified": "2024-01-04T00:00:00",
                    "Created time": "2024-01-04T00:00:00",
                    "Extra data": "{}",
                    "Importance": 8.0,
                },
                {
                    "File path analyzed": r"C:\repo\b.ts",
                    "File name": "b.ts",
                    "File type": "ts",
                    "Last modified": "2024-01-05T00:00:00",
                    "Created time": "2024-01-05T00:00:00",
                    "Extra data": "{}",
                    "Importance": 11.0,
                },
            ]
        )
        assert len(log) == 4
        assert log[-2]["File name"] == "a.py"
        assert log[-1]["File name"] == "b.ts"

    # Test __getitem__ supports positive/negative indices
    def test_getitem_indices(self, sample_log):
        log = LogIteratorAddor(sample_log)
        assert log[0]["File name"] == "file1.py"
        assert log[-1]["File name"] == "file2.js"

    # Test save writes updated content
    def test_save_persists_changes(self, sample_log, tmp_path):
        log = LogIteratorAddor(sample_log)
        log.add_row(
            {
                "File path analyzed": r"C:\repo\saved.py",
                "File name": "saved.py",
                "File type": "py",
                "Last modified": "2024-01-06T00:00:00",
                "Created time": "2024-01-06T00:00:00",
                "Extra data": "{}",
                "Importance": 6.5,
            }
        )
        out_path = tmp_path / "out.log"
        log.save(out_path)

        reloaded = pd.read_csv(out_path)
        assert len(reloaded) == 3
        assert reloaded.iloc[-1]["File name"] == "saved.py"