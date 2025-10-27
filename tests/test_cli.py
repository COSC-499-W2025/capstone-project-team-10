import pytest
import src.cli.cli_app as cli
from unittest.mock import patch

path_to_test_zip = "tests/testdata/test_cli/testScanFolder.zip"
path_to_test_folder = "tests/testdata/test_cli/testScanFolder"
class TestCli:
    def test_cli_start_no_file(self):
        pos_test_args = ["--cli", "-y"]
        with pytest.raises(SystemExit) as exc_info:
            cli.run_cli(pos_test_args)
        # Check the exit code
        assert exc_info.value.code == 1

    def test_cli_user_response(self):
        pos_test_args = ["--cli" , path_to_test_folder]
        with patch('builtins.input', return_value="Y"), patch('builtins.print') as mock_print:
            cli.run_cli(pos_test_args)
            # Check the exit code
            mock_print.assert_called_with("Scanning file path: " + path_to_test_folder)

    def test_cli_user_response_no(self):
        pos_test_args = ["--cli", path_to_test_folder]
        with patch('builtins.input', return_value="N"), patch('builtins.print') as mock_print:
            with pytest.raises(SystemExit) as exc_info:
                cli.run_cli(pos_test_args)
            # Check the exit code
            assert exc_info.value.code == 1

    def test_cli_parse_zip(self):
        pos_test_args = ["--cli", "-y", "--zip", path_to_test_zip]
        result: str = cli.get_param_body(pos_test_args, pos_test_args.index("--zip") + 1)
        assert result == path_to_test_zip

    def test_cli_parse_zip_missing_path(self):
        pos_test_args = ["--cli", "--zip", "-y", path_to_test_folder]
        result: str = cli.get_param_body(pos_test_args, pos_test_args.index("--zip") + 1)
        assert result != path_to_test_zip