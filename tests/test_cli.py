import pytest
import src.cli.cli_app as cli
from unittest.mock import patch
class TestCli:
    def test_cli_start(self):
        with patch('builtins.print') as mock_print:
            cli.run_cli()
            mock_print.assert_called_with("Hello from CLI!")

