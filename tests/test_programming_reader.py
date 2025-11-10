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

    def test_javascript_sample_file(self):
        """Test that all libraries are extracted from sample JS file"""
        programReader = progr.ProgrammingReader(r"tests\testdata\test_fas_programming_reader\sampleJavaScriptFile.js")
        
        assert programReader.filetype == 'javascript'
        
        # Should extract all require() statements
        assert 'fs' in programReader.libraries
        assert 'http' in programReader.libraries
        assert 'express' in programReader.libraries
        assert 'axios' in programReader.libraries
        assert 'moment' in programReader.libraries
        
        # Should extract ES6 import statement (even multi-line)
        assert 'react' in programReader.libraries
        
        # Should have exactly 6 libraries total
        assert len(programReader.libraries) == 6

    def test_pascal_files(self):
        """Test Pascal extracts comma-separated units correctly"""
        programReader = progr.ProgrammingReader(r"tests\testdata\test_fas_programming_reader\samplePascalFile.pp")
        
        assert programReader.filetype == 'pascal'
        
        # Should extract all comma-separated units
        assert 'SysUtils' in programReader.libraries
        assert 'Classes' in programReader.libraries
        assert 'Graphics' in programReader.libraries
        assert 'Forms' in programReader.libraries
        assert 'Dialogs' in programReader.libraries
        assert 'StdCtrls' in programReader.libraries
        assert 'Controls' in programReader.libraries
        assert 'ExtCtrls' in programReader.libraries
        
        # Should have split all 8 units
        assert len(programReader.libraries) == 8


    def test_perl_files(self):
        """Test Perl extracts modules and filters pragmas"""
        programReader = progr.ProgrammingReader(r"tests\testdata\test_fas_programming_reader\samplePerlFile.pl")
        
        assert programReader.filetype == 'perl'
        
        # Should extract actual modules
        assert 'LWP::UserAgent' in programReader.libraries
        assert 'JSON' in programReader.libraries
        assert 'DBI' in programReader.libraries
        assert 'Data::Dumper' in programReader.libraries
        
        # Should NOT contain pragmas
        assert 'strict' not in programReader.libraries
        assert 'warnings' not in programReader.libraries
        assert 'vars' not in programReader.libraries
        assert 'constant' not in programReader.libraries


    def test_Python_files(self):
        programReader = progr.ProgrammingReader(r"tests\testdata\test_fas_programming_reader\samplePythonFile.py")
        assert programReader.filetype == 'python'
        assert len(programReader.libraries) > 0

    def test_go_files(self):
        """Test Go extracts standard/external packages and filters relative imports"""
        programReader = progr.ProgrammingReader(r"tests\testdata\test_fas_programming_reader\sampleGoFile.go")
        
        assert programReader.filetype == 'go'
        
        # Should extract standard and external packages
        assert 'fmt' in programReader.libraries
        assert 'net/http' in programReader.libraries
        assert 'encoding/json' in programReader.libraries
        assert 'github.com/gorilla/mux' in programReader.libraries
        
        # Should NOT contain relative imports
        assert './local/package' not in programReader.libraries
        assert '../parent/package' not in programReader.libraries
        assert not any(lib.startswith('.') for lib in programReader.libraries)

    def test_php_files(self):
        """Test PHP extracts use statements and filters relative paths"""
        programReader = progr.ProgrammingReader(r"tests\testdata\test_fas_programming_reader\samplePHPFile.php")
        
        assert programReader.filetype == 'php'
        
        # Should extract use statements and vendor paths
        assert 'Symfony\\Component\\HttpFoundation\\Request' in programReader.libraries
        assert 'Symfony\\Component\\HttpFoundation\\Response' in programReader.libraries
        assert 'Doctrine\\ORM\\EntityManager' in programReader.libraries
        assert 'vendor/autoload.php' in programReader.libraries
        
        # Should NOT contain relative paths
        assert './local/helper.php' not in programReader.libraries
        assert '../parent/config.php' not in programReader.libraries
        assert not any(lib.startswith(('./','../')) for lib in programReader.libraries)

    def test_rust_files(self):
        """Test Rust extracts external crates and filters internal references"""
        programReader = progr.ProgrammingReader(r"tests\testdata\test_fas_programming_reader\sampleRustFile.rs")
        
        assert programReader.filetype == 'rust'
        
        # Should extract external crates
        assert 'std' in programReader.libraries or any('std' in lib for lib in programReader.libraries)
        assert 'serde' in programReader.libraries or any('serde' in lib for lib in programReader.libraries)
        assert 'tokio' in programReader.libraries or any('tokio' in lib for lib in programReader.libraries)
        
        # Should NOT contain internal references
        assert not any('crate::' in lib for lib in programReader.libraries)
        assert not any('self::' in lib for lib in programReader.libraries)
        assert not any('super::' in lib for lib in programReader.libraries)

    def test_ruby_files(self):
        """Test Ruby extracts require and filters require_relative and relative paths"""
        programReader = progr.ProgrammingReader(r"tests\testdata\test_fas_programming_reader\sampleRubyFile.rb")
        
        assert programReader.filetype == 'ruby'
        
        # Should extract gem requires
        assert 'rails' in programReader.libraries
        assert 'activerecord' in programReader.libraries
        assert 'sinatra' in programReader.libraries
        
        # Should NOT contain require_relative or relative paths
        assert 'helper' not in programReader.libraries
        assert './local/config' not in programReader.libraries
        assert '../parent/module' not in programReader.libraries
        assert not any(lib.startswith(('./','../')) for lib in programReader.libraries)

    def test_typescript_files(self):
        programReader = progr.ProgrammingReader(r"tests\testdata\test_fas_programming_reader\sampleTypeScriptFile.ts")
        assert programReader.filetype == 'typescript'
        assert len(programReader.libraries) > 0


    def test_visualbasic_files(self):
        programReader = progr.ProgrammingReader(r"tests\testdata\test_fas_programming_reader\sampleVisualBasicFile.vb")
        assert programReader.filetype == 'vb'
        assert len(programReader.libraries) > 0

