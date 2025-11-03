import pytest
import src.fas.fas_programming_reader as progr
from unittest.mock import patch

class TestProgrammingReader:
    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            progr.ProgrammingReader(r"C:\badpath.py")

    def test_file_not_code(self):
        with pytest.raises(ValueError):
            progr.ProgrammingReader(r"tests\testdata\test_fas_programming_reader\sampleText1.txt")

    def test_unknown_file_extension(self):
        with pytest.raises(ValueError):
            progr.ProgrammingReader(r"tests\testdata\test_fas_programming_reader\sampleUnkownExtension.xyz")

    def test_empty_file(self):
        programReader = progr.ProgrammingReader(r"tests\testdata\test_fas_programming_reader\sampleEmptyFile.py")
        assert programReader.filetype == 'python'
        assert programReader.libraries == []

    def test_file_with_no_imports(self):
        programReader = progr.ProgrammingReader(r"tests\testdata\test_fas_programming_reader\sampleNoImports.py")
        assert programReader.filetype == 'python'
        assert programReader.libraries == []

    def test_java_files(self):
        programReader = progr.ProgrammingReader(r"tests\testdata\test_fas_programming_reader\sampleJavaFile.java")
        assert programReader.filetype == 'java'
        assert len(programReader.libraries) > 0

    def test_javascript_files(self):
        programReader = progr.ProgrammingReader(r"tests\testdata\test_fas_programming_reader\sampleJavaScriptFile.js")
        assert programReader.filetype == 'javascript'
        assert len(programReader.libraries) > 0

    def test_pascal_files(self):
        programReader = progr.ProgrammingReader(r"tests\testdata\test_fas_programming_reader\samplePascalFile.pp")
        assert programReader.filetype == 'pascal'
        assert len(programReader.libraries) > 0


    def test_perl_files(self):
        programReader = progr.ProgrammingReader(r"tests\testdata\test_fas_programming_reader\samplePerlFile.pl")
        assert programReader.filetype == 'perl'
        assert len(programReader.libraries) > 0


    def test_Python_files(self):
        programReader = progr.ProgrammingReader(r"tests\testdata\test_fas_programming_reader\samplePythonFile.py")
        assert programReader.filetype == 'python'
        assert len(programReader.libraries) > 0


    def test_rust_files(self):
        programReader = progr.ProgrammingReader(r"tests\testdata\test_fas_programming_reader\sampleRustFile.rs")
        assert programReader.filetype == 'rust'
        assert len(programReader.libraries) > 0


    def test_typescript_files(self):
        programReader = progr.ProgrammingReader(r"tests\testdata\test_fas_programming_reader\sampleTypeScriptFile.ts")
        assert programReader.filetype == 'typescript'
        assert len(programReader.libraries) > 0


    def test_visualbasic_files(self):
        programReader = progr.ProgrammingReader(r"tests\testdata\test_fas_programming_reader\sampleVisualBasicFile.vb")
        assert programReader.filetype == 'vb'
        assert len(programReader.libraries) > 0

