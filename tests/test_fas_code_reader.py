import pytest
import os
import src.fas.fas_code_reader as progr
from unittest.mock import patch

TEST_DATA_DIR = os.path.join("tests", "testdata", "test_fas_code_reader")

class TestCodeReader:

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            progr.CodeReader(os.path.join("C:", "badpath.py"))

    def test_file_not_Code(self):
        with pytest.raises(ValueError):
            progr.CodeReader(os.path.join(TEST_DATA_DIR, "sample.txt"))

    def test_unknown_file_extension(self):
        with pytest.raises(ValueError):
            progr.CodeReader(os.path.join(TEST_DATA_DIR, "sample.xyz"))

    def test_python_extract_imports(self):
        pr = progr.CodeReader(os.path.join(TEST_DATA_DIR, "sample.py"))
        pr.extract()
        assert pr.filetype == 'python'
        assert len(pr.libraries) > 0
        assert pr.libraries == ['os', 'sys', 'json', 'pandas', 'requests']

    def test_javascript_extract_imports(self):
        pr = progr.CodeReader(os.path.join(TEST_DATA_DIR, "sample.js"))
        pr.extract()
        assert pr.filetype == 'javascript'
        assert len(pr.libraries) > 0
        assert pr.libraries == ['fs', 'http', 'express', 'axios', 'moment', 'react']

    def test_c_extract_imports(self):
        pr = progr.CodeReader(os.path.join(TEST_DATA_DIR, "sample.c"))
        pr.extract()
        assert pr.filetype == 'c'
        assert len(pr.libraries) > 0
        assert pr.libraries == ['stdio.h', 'stdlib.h', 'string.h', 'math.h']

    def test_cpp_extract_imports(self):
        pr = progr.CodeReader(os.path.join(TEST_DATA_DIR, "sample.cpp"))
        pr.extract()
        assert pr.filetype == 'cpp'
        assert len(pr.libraries) > 0
        assert pr.libraries == ['iostream', 'string', 'my_utility.h']

    def test_java_extract_imports(self):
        pr = progr.CodeReader(os.path.join(TEST_DATA_DIR, "sample.java"))
        pr.extract()
        assert pr.filetype == 'java'
        assert len(pr.libraries) > 0
        assert pr.libraries == ['java.io.BufferedReader', 'java.io.FileReader', 'java.io.IOException', 'java.net.URI', 'com.google.gson.Gson']

    def test_typescript_extract_imports(self):
        pr = progr.CodeReader(os.path.join(TEST_DATA_DIR, "sample.ts"))
        pr.extract()
        assert pr.filetype == 'typescript'
        assert len(pr.libraries) > 0
        assert pr.libraries == ['fs', 'events', 'axios', 'date-fns', 'typeorm']

    def test_go_extract_imports(self):
        pr = progr.CodeReader(os.path.join(TEST_DATA_DIR, "sample.go"))
        pr.extract()
        assert pr.filetype == 'go'
        assert len(pr.libraries) > 0
        assert pr.libraries == ['fmt', 'net/http', 'encoding/json', './local/package', 'github.com/gorilla/mux']