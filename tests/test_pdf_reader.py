import unittest
import src.fas.pdf_reader as pdfr

class test_pdf_reader(unittest.TestCase):
    def test_pdf_version(self):
        from unittest.mock import patch
        with patch('builtins.print') as mock_print:
            pdfr
            mock_print.assert_called_with("Hello from CLI!")

if __name__ == '__main__':
    unittest.main()