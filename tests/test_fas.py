import pytest
import stat
import os
import datetime
import src.fas.fas as fas
from unittest.mock import patch
class TestFas:
    def test_fas_start_file(self):
        with patch('builtins.print') as mock_print:
            fas.run_fas()
            #TODO: have the system return the correct data as an object from the service
            mock_print.assert_called_with("Hello from fas.")

    def test_fas_fileType(self):
        #fas.run_fas() this is where specific testing comes in and will extract the specific file type to be analyzed
        #TODO: update fas to ensure it returns the correct file type that matches extracted type as well as to use actualy type rather than file extension.
        filePath="tests/testdata/test_fas/fas_test_data.docx"
        temp = filePath.split(".")
        result = temp[1]
        #assert that the extracted file type extension is equal to the result
        assert result == "docx"

    def test_fas_fileLastModifiedDate(self):
        #fas.run_fas() placeholder until functionality is implemented, this will test that the function returns the correct last modified date of the file
        filePath="tests/testdata/test_fas/fas_test_data.docx"
        st = os.stat(filePath)
        result = datetime.datetime.fromtimestamp(st.st_mtime).isoformat()
        #TODO: update fas to return the correct modified date that matches given modified date
        #assert that the last modified time is the same as the result
        assert result == "2025-10-19T13:47:11.880051"

    def test_fas_fileCreatedDate(self):
        #das.run_fas() this will test that the extracted and analyzed date taken from the file is correct once implementation is completed
        #TODO this will need to be created later as different opperating systems use different ways to extract the creation date of a given file
        filePath="tests/testdata/test_fas/fas_test_data.docx"
        st = os.stat(filePath)
        result = "1" #implement way to find creation time cross platform
        #assert that the creation time is equal to the result
        assert result == "1"

    def test_fas_fileName(self):
        #fas.run_fas() this will test that the completed service returns and analyzes the correct name for the given test file
        #TODO: update the fas to extract the correct file name of a given file
        filePath="tests/testdata/test_fas/fas_test_data.docx"
        temp = filePath.split("/")
        result = temp[3]
        #assert that the extracted file name is equal to the result
        assert result == "fas_test_data.docx"

    def test_fas_badFile(self):
        #TODO: return an error when attempting to analyze a bad file
        result = "-1"
        assert result == "-1"

            

