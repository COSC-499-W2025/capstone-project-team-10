import unittest
import src.cli.cli_app as cli

class test_cli(unittest.TestCase):
    def test_cli_start(self):
        from unittest.mock import patch
        with patch('builtins.print') as mock_print:
            cli.run_cli()
            mock_print.assert_called_with("Hello from CLI!")

if __name__ == '__main__':
    unittest.main()