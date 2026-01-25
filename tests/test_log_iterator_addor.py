import pandas as pd
from pathlib import Path
from src.gui.log_iterator_addor import LogIteratorAddor


def _make_sample_log(tmp_path: Path) -> Path:
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
    log_path = tmp_path / "sample.log"
    pd.DataFrame(data).to_csv(log_path, index=False)
    return log_path


def test_iteration_yields_rows_in_order(tmp_path):
    log_path = _make_sample_log(tmp_path)
    log = LogIteratorAddor(log_path)

    rows = list(log)  # uses __iter__ / __next__
    assert len(rows) == 2
    assert rows[0]["File name"] == "file1.py"
    assert rows[1]["File name"] == "file2.js"

    # iterator resets correctly on re-iteration
    rows_again = [r["File name"] for r in log]
    assert rows_again == ["file1.py", "file2.js"]


def test_add_row_appends_and_len_updates(tmp_path):
    log_path = _make_sample_log(tmp_path)
    log = LogIteratorAddor(log_path)

    original_len = len(log)
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

    assert len(log) == original_len + 1
    assert log[-1]["File name"] == "new.py"


def test_add_rows_appends_multiple(tmp_path):
    log_path = _make_sample_log(tmp_path)
    log = LogIteratorAddor(log_path)

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


def test_getitem_supports_positive_and_negative_indices(tmp_path):
    log_path = _make_sample_log(tmp_path)
    log = LogIteratorAddor(log_path)

    assert log[0]["File name"] == "file1.py"
    assert log[-1]["File name"] == "file2.js"


def test_save_writes_updated_content(tmp_path):
    log_path = _make_sample_log(tmp_path)
    log = LogIteratorAddor(log_path)

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