import argparse
import builtins
import sys
from pathlib import Path

import pytest

import src.cli.cli_app as cli
import src.param.param as param


# Mocks for dependencies
class DummyLog:
    def open_log_file(self):
        pass

    def resume_log_file(self):
        pass


class DummyParam:
    export_folder_path = "/tmp"

    def get(self, key):
        return []

    def set(self, key, value):
        pass


class DummyFSS:
    class FSS_Search:
        def __init__(self, *a, **kw):
            pass

    def search(self, search_obj):
        pass


class DummyZip:
    def extract_zip(self, zip_file_path):
        return Path("/tmp/unzipped")


class DummyShowcase:
    def generate_resume(self):
        return Path("/tmp/resume.pdf")

    def generate_portfolio(self):
        return Path("/tmp/portfolio.zip")


@pytest.fixture(autouse=True)
def patch_dependencies(monkeypatch):
    monkeypatch.setattr(cli, "log", DummyLog())
    monkeypatch.setattr(cli, "param", DummyParam())
    monkeypatch.setattr(cli, "fss", DummyFSS())
    monkeypatch.setattr(cli, "zip", DummyZip())
    monkeypatch.setattr(cli, "generate_resume", DummyShowcase().generate_resume)
    monkeypatch.setattr(cli, "generate_portfolio", DummyShowcase().generate_portfolio)


def test_prompt_file_perms_yes(monkeypatch):
    monkeypatch.setattr(builtins, "input", lambda _: "y")
    cli.prompt_file_perms()  # Should not exit


def test_prompt_file_perms_no(monkeypatch):
    monkeypatch.setattr(builtins, "input", lambda _: "n")
    with pytest.raises(SystemExit):
        cli.prompt_file_perms()


def test_extract_chosen_zip():
    result = cli.extract_chosen_zip("dummy.zip")
    assert result == Path("/tmp/unzipped")


def test_add_cli_args():
    parser = argparse.ArgumentParser()
    cli.add_cli_args(parser)
    args = parser.parse_args(
        [
            "/tmp/file",
            "--zip",
            "dummy.zip",
            "--exclude-paths",
            "foo",
            "bar",
            "--file-types",
            "txt",
            "md",
        ]
    )
    assert args.file_path == "/tmp/file"
    assert args.zip == "dummy.zip"
    assert args.exclude_paths == ["foo", "bar"]
    assert args.file_types == ["txt", "md"]


def test_run_cli(monkeypatch):
    # Simulate CLI args
    test_args = [
        "cli_app.py",
        "/tmp/file",
        "--zip",
        "dummy.zip",
        "--exclude-paths",
        "foo",
        "bar",
        "--file-types",
        "txt",
        "md",
        "--resume_entries",
        "/tmp",
        "--portfolio_entries",
        "/tmp",
        "--clean",
        "--before",
        "2023-01-01",
        "--after",
        "2022-01-01",
        "--yes",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    # Patch print to capture output
    output = []
    original_print = builtins.print
    monkeypatch.setattr(builtins, "print", lambda *a, **k: output.append(a))
    cli.run_cli()
    # Restore print for debugging
    monkeypatch.setattr(builtins, "print", original_print)

    # Flatten output for easier assertions
    flat_output = [str(item) for line in output for item in line]
    all_output = " ".join(flat_output)
    print(all_output)  # For debugging

    # Check excluded paths are in output (order-agnostic)
    assert "foo" in all_output
    assert "bar" in all_output
    assert "Excluding paths:" in all_output

    # Check file types are in output (order-agnostic)
    assert "txt" in all_output
    assert "md" in all_output
    assert "Filtering by file types:" in all_output

    # Check Resume is created
    assert "resume.pdf" in all_output
    assert "Resume generated at:" in all_output

    # Check Portfolio is created
    assert "portfolio.zip" in all_output
    assert "Portfolio generated at:" in all_output

    # Check that the bounds string is correct
    assert "2022-01-01" in all_output
    assert "2023-01-01" in all_output

    # Check that the zip extraction message is present
    assert "unzipped" in all_output
    assert "File unzipped at:" in all_output

    # Check that the log file location is printed
    assert "Log file located at:" in all_output

    # Check scan complete and processing complete
    assert "Scan complete." in all_output
    assert "Processing Complete!" in all_output


def test_run_cli_quiet(monkeypatch):
    # Simulate CLI args
    test_args = [
        "cli_app.py",
        "/tmp/file",
        "--zip",
        "dummy.zip",
        "--exclude-paths",
        "foo",
        "bar",
        "--file-types",
        "txt",
        "md",
        "--resume_entries",
        "/tmp",
        "--portfolio_entries",
        "/tmp",
        "--clean",
        "--before",
        "2023-01-01",
        "--after",
        "2022-01-01",
        "--yes",
        "-q",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    # Patch print to capture output
    output = []
    original_print = builtins.print
    monkeypatch.setattr(builtins, "print", lambda *a, **k: output.append(a))
    param.set("logging.current_log_file", "log.log")
    cli.run_cli()
    # Restore print for debugging
    monkeypatch.setattr(builtins, "print", original_print)

    # Flatten output for easier assertions
    flat_output = [str(item) for line in output for item in line]
    all_output = " ".join(flat_output)
    print(all_output)  # For debugging

    # Check excluded paths are in output (order-agnostic)
    assert "foo" not in all_output
    assert "bar" not in all_output
    assert "Excluding paths:" not in all_output

    # Check file types are in output (order-agnostic)
    assert "txt" not in all_output
    assert "md" not in all_output
    assert "Filtering by file types:" not in all_output

    # Check Resume is created
    assert "resume.pdf" not in all_output
    assert "Resume generated at:" not in all_output

    # Check Portfolio is created
    assert "portfolio.zip" not in all_output
    assert "Portfolio generated at:" not in all_output

    # Check that the bounds string is correct
    assert "2022-01-01" not in all_output
    assert "2023-01-01" not in all_output

    # Check that the zip extraction message is present
    assert "unzipped" not in all_output
    assert "File unzipped at:" not in all_output

    # Check that the log file location is printed
    assert "Log file located at:" not in all_output

    # Check scan complete and processing complete
    assert "Scan complete." not in all_output
    assert "Processing Complete!" not in all_output
