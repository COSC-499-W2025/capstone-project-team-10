from utils.extension_mappings import CODING_FILE_EXTENSIONS as em
from utils.extension_mappings import SHEBANG_MAPPINGS as sm
from utils.programming_regex import LANGUAGE_PATTERNS
import os
import re
import ast

class ProgrammingReader:
    """
    Extracts type of programming file as well as any imports, frameworks, and libraries used.
    """

    def __init__(self, filepath) -> None:
        self.filepath = filepath
        self.filetype = None
        self.libraries = []

        if not os.path.isfile(self.filepath):
            raise FileNotFoundError(f"File not found: {self.filepath}")

        self.extract()

    def extract_with_pattern(self, pattern):
        """
        Run regex line-by-line and return all captured groups from matches.
        
        Args:
            pattern: Regex pattern to match
        """
        matches = []
        try:
            with open(self.filepath, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    match = re.search(pattern, line)
                    if match:
                        groups = match.groups()
                        for group in groups:
                            if group:
                                matches.append(group)
        except Exception as e:
                raise Exception(f"Error analyzing file: {str(e)}")
        return matches

    def extract_file_type(self):
        """Detect file type from extension or shebang."""
        _, extension = os.path.splitext(self.filepath)
        self.filetype = em.get(extension.lower())

        if self.filetype is None:
            try:
                with open(self.filepath, 'r', encoding='utf-8', errors="replace") as f:
                    first_line = f.readline().strip()
                    
                if first_line.startswith('#!'):
                    shebang_lower = first_line.lower()
                    for keyword, filetype in sm.items():
                        if keyword in shebang_lower:
                            self.filetype = filetype
                            break
                            
            except Exception as e:
                raise Exception(f"Error analyzing file: {str(e)}")
            
        if not self.filetype:
            raise ValueError(f"File is not a recognized coding file: {self.filepath}")

    def extract_python_libraries(self):
        """Extract imports using AST for accuracy."""
        libraries = set()
        try:
            with open(self.filepath, "r", encoding="utf-8", errors="replace") as f:
                tree = ast.parse(f.read())

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        libraries.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module and node.level == 0:
                        libraries.add(node.module)
        except SyntaxError:
            pass
        self.libraries = list(libraries)

    def extract_java_libraries(self):
        """Extract libraries and frameworks from Java files."""
        pattern = LANGUAGE_PATTERNS['java']
        matches = self.extract_with_pattern(pattern)
        self.libraries = list(set(matches))

    def extract_javascript_libraries(self):
        """Extract libraries and frameworks from JavaScript files."""
        patterns = LANGUAGE_PATTERNS['javascript']
        matches = []
        for pattern in patterns:
            matches.extend(self.extract_with_pattern(pattern))
        self.libraries = list(set(matches))

    def extract_typescript_libraries(self):
        """Extract libraries and frameworks from TypeScript files."""
        patterns = LANGUAGE_PATTERNS['typescript']
        matches = []
        for pattern in patterns:
            matches.extend(self.extract_with_pattern(pattern))
        self.libraries = list(set(matches))

    def extract_rust_libraries(self):
        """Extract libraries and frameworks from Rust files."""
        pattern = LANGUAGE_PATTERNS['rust']
        matches = self.extract_with_pattern(pattern)
        # Filter out internal crate references
        cleaned = []
        for m in matches:
            if any(skip in m for skip in ["crate::", "self::", "super::"]):
                continue
            cleaned.append(m.split("::{")[0])
        self.libraries = list(set(cleaned))

    def extract_go_libraries(self):
        """Extract libraries and frameworks from Go files."""
        pattern = LANGUAGE_PATTERNS['go']
        matches = self.extract_with_pattern(pattern)
        # Filter out relative imports
        cleaned = [m for m in matches if not m.startswith(".")]
        self.libraries = list(set(cleaned))

    def extract_csharp_libraries(self):
        """Extract libraries and frameworks from C# files."""
        pattern = LANGUAGE_PATTERNS['csharp']
        matches = self.extract_with_pattern(pattern)
        self.libraries = list(set(matches))

    def extract_c_libraries(self):
        """Extract libraries and frameworks from C files."""
        pattern = LANGUAGE_PATTERNS['c']
        matches = self.extract_with_pattern(pattern)
        self.libraries = list(set(matches))

    def extract_cpp_libraries(self):
        """Extract libraries and frameworks from C++ files."""
        pattern = LANGUAGE_PATTERNS['cpp']
        matches = self.extract_with_pattern(pattern)
        self.libraries = list(set(matches))

    def extract_php_libraries(self):
        """Extract libraries and frameworks from PHP files."""
        patterns = LANGUAGE_PATTERNS['php']
        matches = []
        for pattern in patterns:
            matches.extend(self.extract_with_pattern(pattern))
        # Filter out relative paths
        cleaned = [m for m in matches if not m.startswith(("./", "../"))]
        self.libraries = list(set(cleaned))

    def extract_ruby_libraries(self):
        """Extract libraries and frameworks from Ruby files."""
        pattern = LANGUAGE_PATTERNS['ruby']
        matches = self.extract_with_pattern(pattern)
        # Filter out relative paths
        cleaned = [m for m in matches if not m.startswith(("./", "../"))]
        self.libraries = list(set(cleaned))

    def extract_swift_libraries(self):
        """Extract libraries and frameworks from Swift files."""
        pattern = LANGUAGE_PATTERNS['swift']
        matches = self.extract_with_pattern(pattern)
        self.libraries = list(set(matches))

    def extract_r_libraries(self):
        """Extract libraries and frameworks from R files."""
        pattern = LANGUAGE_PATTERNS['r']
        matches = self.extract_with_pattern(pattern)
        self.libraries = list(set(matches))

    def extract_fortran_libraries(self):
        """Extract libraries and frameworks from Fortran files."""
        pattern = LANGUAGE_PATTERNS['fortran']
        matches = self.extract_with_pattern(pattern)
        self.libraries = list(set(matches))

    def extract_perl_libraries(self):
        """Extract libraries and frameworks from Perl files."""
        pattern = LANGUAGE_PATTERNS['perl']
        matches = self.extract_with_pattern(pattern)
        # Filter out common pragmas
        cleaned = [m for m in matches if m not in ["strict", "warnings", "vars", "constant"]]
        self.libraries = list(set(cleaned))

    def extract_pascal_libraries(self):
        """Extract libraries and frameworks from Pascal files."""
        pattern = LANGUAGE_PATTERNS['pascal']
        matches = self.extract_with_pattern(pattern)
        # Split comma-separated units
        cleaned = []
        for m in matches:
            units = [u.strip() for u in m.split(",") if u.strip()]
            cleaned.extend(units)
        self.libraries = list(set(cleaned))

    def extract_vb_libraries(self):
        """Extract libraries and frameworks from Visual Basic files."""
        pattern = LANGUAGE_PATTERNS['vb']
        matches = self.extract_with_pattern(pattern)
        self.libraries = list(set(matches))

    def extract_libraries(self):
        """
        Extract libraries based on detected file type.
        Automatically routes to the appropriate extraction method.
        """
        if not self.filetype:
            return
        
        method_name = f"extract_{self.filetype}_libraries"
        if hasattr(self, method_name):
            getattr(self, method_name)()

    def extract(self):
        """
        Perform complete analysis: detect file type and extract libraries.
        This is the main public API method.
        """
        self.extract_file_type()
        self.extract_libraries()