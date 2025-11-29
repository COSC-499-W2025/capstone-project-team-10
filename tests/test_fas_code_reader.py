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
        assert pr.filetype == 'python'
        assert len(pr.libraries) > 0
        assert pr.libraries == ['os', 'sys', 'json', 'pandas', 'requests']
        assert len(pr.complexity) > 0
        assert pr.complexity['estimated'] == 'O(n^3)'
        assert len(pr.oop) > 0
        assert 'helper' in [f['name'] for f in pr.oop['functions']]
 
    def test_javascript_extract_imports(self):
        pr = progr.CodeReader(os.path.join(TEST_DATA_DIR, "sample.js"))
        assert pr.filetype == 'javascript'
        assert len(pr.libraries) > 0
        assert pr.libraries == ['fs', 'http', 'express', 'axios', 'moment', 'react']
        assert len(pr.complexity) > 0
        assert pr.complexity['estimated'] == 'O(n^2)'
        assert len(pr.oop) > 0
        assert 'helper' in [f['name'] for f in pr.oop['functions']]

    def test_c_extract_imports(self):
        pr = progr.CodeReader(os.path.join(TEST_DATA_DIR, "sample.c"))
        assert pr.filetype == 'c'
        assert len(pr.libraries) > 0
        assert pr.libraries == ['stdio.h', 'stdlib.h', 'string.h', 'math.h']
        assert len(pr.complexity) > 0
        assert pr.complexity['estimated'] == 'O(n^2)'
        assert pr.oop['classes'] == []
        assert 'helper' in [f['name'] for f in pr.oop['functions']]

    def test_cpp_extract_imports(self):
        pr = progr.CodeReader(os.path.join(TEST_DATA_DIR, "sample.cpp"))
        assert pr.filetype == 'cpp'
        assert len(pr.libraries) > 0
        assert pr.libraries == ['iostream', 'string', 'my_utility.h']
        assert len(pr.complexity) > 0
        assert pr.complexity['estimated'] == 'O(n^2)'
        assert len(pr.oop) > 0
        assert 'Animal' in [c['name'] for c in pr.oop['classes']]
        assert 'helper' in [f['name'] for f in pr.oop['functions']]

    def test_java_extract_imports(self):
        pr = progr.CodeReader(os.path.join(TEST_DATA_DIR, "sample.java"))
        assert pr.filetype == 'java'
        assert len(pr.libraries) > 0
        assert pr.libraries == ['java.io.BufferedReader', 'java.io.FileReader', 'java.io.IOException', 'java.net.URI', 'com.google.gson.Gson']
        assert len(pr.complexity) > 0
        assert pr.complexity['estimated'] == 'O(n^3)'
        assert len(pr.oop) > 0
        assert 'helper' in [f['name'] for f in pr.oop['functions']]

    def test_typescript_extract_imports(self):
        pr = progr.CodeReader(os.path.join(TEST_DATA_DIR, "sample.ts"))
        assert pr.filetype == 'typescript'
        assert len(pr.libraries) > 0
        assert pr.libraries == ['fs', 'events', 'axios', 'date-fns', 'typeorm']
        assert len(pr.complexity) > 0
        assert pr.complexity['estimated'] == 'O(n^2)'
        assert len(pr.oop) > 0
        assert 'helper' in [f['name'] for f in pr.oop['functions']]

    def test_go_extract_imports(self):
        pr = progr.CodeReader(os.path.join(TEST_DATA_DIR, "sample.go"))
        assert pr.filetype == 'go'
        assert len(pr.libraries) > 0
        assert pr.libraries == ['fmt', 'net/http', 'encoding/json', './local/package', 'github.com/gorilla/mux']
        assert len(pr.complexity) > 0
        assert pr.complexity['estimated'] == 'O(n^2)'
        assert pr.oop['classes'] == []
        assert 'helper' in [f['name'] for f in pr.oop['functions']]

    def test_rust_extract_imports(self):
        pr = progr.CodeReader(os.path.join(TEST_DATA_DIR, "sample.rs"))
        assert pr.filetype == 'rust'
        assert len(pr.libraries) > 0
        assert pr.libraries == ['std::collections::HashMap', 'std::io::Result', 'tokio::runtime::Runtime', 'crate::internal::module', 'self::local_function', 'super::parent_module', 'super::super::grandparent']
        assert len(pr.complexity) > 0
        assert pr.complexity['estimated'] == 'O(n^2)'
        assert len(pr.oop) > 0
        assert 'helper' in [f['name'] for f in pr.oop['functions']]