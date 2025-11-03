from utils.extension_mappings import CODING_FILE_EXTENSIONS as em
from utils.extension_mappings import SHEBANG_MAPPINGS as sm
from utils.programming_regex import LANGUAGE_PATTERNS
import os
import re
import ast

class ProgrammingReader:
    """
    Detects the file type of programming files and extracts any imported libraries.
    Supports multiple languages and uses language-specific regex patterns and parsing.
    """

    def __init__(self, filepath) -> None:
        self.filepath = filepath
        self.filetype = None
        self.libraries = []

        # Checks if the filepath exists
        if not os.path.isfile(self.filepath):
            raise FileNotFoundError(f"File not found: {self.filepath}")

        # Calls extract method to populate file type and libraries 
        self.extract()

    def extract_with_pattern(self, pattern) -> list[str]:
        """
        Finds import and library lines of code using a given regex pattern. 
        Returns a list of all the matches from the file with the given regex pattern
        """
        matches = []
        try:
            with open(self.filepath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

                # Finds all matches to the pattern in the file, including matches across newlines
                for match in re.finditer(pattern, content, re.MULTILINE | re.DOTALL):
                    # Stores all the individual groups from the larger match
                    groups = match.groups()
                    # Loops through each individual group and adds to the matches if the group is not None
                    for group in groups:
                        if group:
                            matches.append(group)
        except Exception as e:
            raise Exception(f"Error analyzing file: {str(e)}")
        return matches

    def extract_file_type(self):
        """
        Identifies the file type using file extensions or shebang line as a fallback.
        Raises a value error if the file can't be identified.
        """
        _, extension = os.path.splitext(self.filepath)
        
        # Maps the extension to the extension_mappings.py dictionary
        self.filetype = em.get(extension.lower())

        # If the extension check fails tries using shebang instead
        if self.filetype is None:
            try:
                with open(self.filepath, 'r', encoding='utf-8', errors="replace") as f:
                    first_line = f.readline().strip()
                
                # Checks if shebang exists and maps the shebang to the extension_mappings.py dictionary
                if first_line.startswith('#!'):
                    shebang_lower = first_line.lower()
                    for keyword, filetype in sm.items():
                        if keyword in shebang_lower:
                            self.filetype = filetype
                            break
                            
            except Exception as e:
                raise Exception(f"Error analyzing file '{self.filepath}': {e}")
            
        # Checks if a file type was found and returns an error if no type could be identified
        if not self.filetype:
            raise ValueError(f"File is not a recognized coding file: {self.filepath}")

    def extract_generic_libraries(self):
        """
        Generic extraction for languages that don't need special filtering.
        """
        if self.filetype not in LANGUAGE_PATTERNS:
            return
        
        # Maps the regex pattern from programming_regex.py to the file type 
        patterns = LANGUAGE_PATTERNS[self.filetype]

        # Checks if the filetype has multiple regex patterns or just one
        if not isinstance(patterns, list):
            patterns = [patterns]
        
        matches = []
        # Uses all possible regex patterns for a file type and stores them in matches
        for pattern in patterns:
            matches.extend(self.extract_with_pattern(pattern))
        
        # Assigns the libraries variable to a unique list of the matches
        self.libraries = list(set(matches))

    def extract_python_libraries(self):
        """
        Extract libraries using python's AST for improved accuracy.
        """
        libraries = set()
        try:
            with open(self.filepath, "r", encoding="utf-8", errors="replace") as f:
                tree = ast.parse(f.read())

            # Walks through each node in the abstract syntax tree (ast) looking for imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    # Adds imported modules to libraries
                    for alias in node.names:
                        libraries.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    # Adds non-relative imports to libraries
                    if node.module and node.level == 0:
                        libraries.add(node.module)
        except SyntaxError:
            pass

        self.libraries = list(libraries)

    def extract_rust_libraries(self):
        """
        Extract external crate references from Rust files.
        """
        pattern = LANGUAGE_PATTERNS['rust']
        matches = self.extract_with_pattern(pattern)
        # Excludes rust's internal crate references (crate::, self::, super::)
        cleaned = []
        for m in matches:
            if any(skip in m for skip in ["crate::", "self::", "super::"]):
                continue
            # Trims module paths
            cleaned.append(m.split("::{")[0])
        self.libraries = list(set(cleaned))

    def extract_go_libraries(self):
        """
        Extract imported packages from Go files.
        """
        pattern = LANGUAGE_PATTERNS['go']
        matches = self.extract_with_pattern(pattern)
        # Excludes go's relative imports (./utils)
        cleaned = [m for m in matches if not m.startswith(".")]
        self.libraries = list(set(cleaned))

    def extract_php_libraries(self):
        """
        Extract imported and required modules from PHP files.
        """
        patterns = LANGUAGE_PATTERNS['php']
        matches = []
        for pattern in patterns:
            matches.extend(self.extract_with_pattern(pattern))
        # Excludes php's relative imports and requires (./ or ../)
        cleaned = [m for m in matches if not m.startswith(("./", "../"))]
        self.libraries = list(set(cleaned))

    def extract_ruby_libraries(self):
        """
        Extract required libraries from Ruby files.
        """
        pattern = LANGUAGE_PATTERNS['ruby']
        matches = self.extract_with_pattern(pattern)
        # Filter out relative paths
        cleaned = [m for m in matches if not m.startswith(("./", "../"))]
        self.libraries = list(set(cleaned))

    def extract_perl_libraries(self):
        """
        Extract modules from Perl files, excluding the built in pragmas.
        """
        pattern = LANGUAGE_PATTERNS['perl']
        matches = self.extract_with_pattern(pattern)
        # Filter out common pragmas
        cleaned = [m for m in matches if m not in ["strict", "warnings", "vars", "constant"]]
        self.libraries = list(set(cleaned))

    def extract_pascal_libraries(self):
        """
        Extract imported units from Pascal files.
        """
        pattern = LANGUAGE_PATTERNS['pascal']
        matches = self.extract_with_pattern(pattern)
        # Split comma-separated imports into individual imports (use SysUtils, Classes)
        cleaned = []
        for m in matches:
            units = [u.strip() for u in m.split(",") if u.strip()]
            cleaned.extend(units)
        self.libraries = list(set(cleaned))

    def extract_libraries(self):
        """
        Calls the method using the filetype if it exists. Otherwise calls the extract_generic_libraries() method
        """
        if not self.filetype:
            return
        
        method_name = f"extract_{self.filetype}_libraries"
        if hasattr(self, method_name):
            getattr(self, method_name)()
        else:
            self.extract_generic_libraries()

    def extract(self):
        """
        Performs the extraction of file type and libraries. Is called by the __init__ method.
        """
        self.extract_file_type()
        self.extract_libraries()