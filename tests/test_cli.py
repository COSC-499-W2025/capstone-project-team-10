import pytest
import src.cli.cli_app as cli
from unittest.mock import patch

path_to_test_zip = "tests/testdata/test_cli/testScanFolder.zip"
class TestCli:
    def test_cli_start_no_file(self):
        pos_test_args = ["--cli", "-y"]
        with patch('builtins.print') as mock_print:
            cli.run_cli(pos_test_args)
            #TODO: update with cli response from no file passed in
            mock_print.assert_called_with("Hello from CLI!")

    def test_cli_start_no_y(self):
        neg_test_args = ["--cli"]
        with patch('builtins.print') as mock_print:
            cli.run_cli(neg_test_args)
            #TODO: update with expected cli response from no -y flag
            mock_print.assert_called_with("Hello from CLI!")

    def test_cli_parse_zip(self):
        pos_test_args = ["--cli", "-y", "--zip ${path_to_test_zip}"]
        with patch('builtins.print') as mock_print:
            cli.run_cli(pos_test_args)
            #TODO: update with cli response expected for a successful parse, currently uses the file count parsed
            mock_print.assert_called_with("2")