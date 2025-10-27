import pytest
import src.param.param as param
from unittest.mock import patch
test_param_file = "tests/testdata/test_param/testconfig.json"
invalid_param_file = "tests/testdata/test_param/invalidconfig.json"
path_to_invalid_folder = "/DUMMMMMMMMMY/DUMMY/DUMB/DUMMY"

class TestParam:
    def test_param_invalid_parse(self):
        with patch('builtins.print') as mock_print:
            param.parse_param(invalid_param_file)
            #TODO: update with param response
            # response shall be invalid params or a failed parse. 
            mock_print.assert_called_with("Hello from param!")

    def test_param_parse(self):
        with patch('builtins.print') as mock_print:
            param.parse_param(test_param_file)
            #TODO: update with param response
            #response shall indicate success
            mock_print.assert_called_with("Hello from param!")

    def test_param_save(self):
        with patch('builtins.print') as mock_print:
            param.save_param(test_param_file)
            #TODO: update with param response
            #Param save shall create a file identical to test_param_file
            mock_print.assert_called_with("Hello from param!")

    
