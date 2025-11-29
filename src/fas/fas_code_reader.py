from utils.extension_mappings import CODING_FILE_EXTENSIONS as em
from pygments.lexers import get_lexer_for_filename
from tree_sitter import Language, Parser
import os

import tree_sitter_python
import tree_sitter_javascript
import tree_sitter_c
import tree_sitter_cpp
import tree_sitter_java
import tree_sitter_typescript
import tree_sitter_go
import tree_sitter_rust

def strip_quotes(text):
    return text.strip("'\"")

def strip_brackets(text):
    return text.strip("<>")

def strip_quotes_and_brackets(text):
    return text.strip("'\"<>")

def is_import_call(valid_names):
    """Factory that creates a validator for specific function names."""
    def validator(node):
        if node.type != "call_expression":
            return True
        for child in node.children:
            if child.type == "identifier" and child.text.decode("utf-8") in valid_names:
                return True
        return False
    return validator

LANGUAGE_MAP = {
    "python": tree_sitter_python.language(),
    "javascript": tree_sitter_javascript.language(),
    "c": tree_sitter_c.language(),
    "cpp": tree_sitter_cpp.language(),
    "java": tree_sitter_java.language(),
    "typescript": tree_sitter_typescript.language_typescript(),
    "go": tree_sitter_go.language(),
    "rust": tree_sitter_rust.language()
}

LANGUAGE_CONFIGS = {
    "python": {
        "import_nodes": ["import_statement", "import_from_statement"],
        "name_children": ["dotted_name", "module_name"],
        "clean": None,
        "validate": None,
        "loop_nodes": ["for_statement", "while_statement"]
    },
    "javascript": {
        "import_nodes": ["import_statement", "call_expression"],
        "name_children": ["string"],
        "clean": strip_quotes,
        "validate": is_import_call(["require"]),
        "loop_nodes": ["for_statement", "for_in_statement", "while_statement", "do_statement"]
    },
    "c": {
        "import_nodes": ["preproc_include"],
        "name_children": ["string_literal", "system_lib_string"],
        "clean": strip_quotes_and_brackets,
        "validate": None,
        "loop_nodes": ["for_statement", "while_statement", "do_statement"]
    },
    "cpp": {
        "import_nodes": ["preproc_include"],
        "name_children": ["string_literal", "system_lib_string"],
        "clean": strip_quotes_and_brackets,
        "validate": None,
        "loop_nodes": ["for_statement", "while_statement", "do_statement", "for_range_loop"]
    },
    "java": {
        "import_nodes": ["import_declaration"],
        "name_children": ["scoped_identifier"],
        "clean": None,
        "validate": None,
        "loop_nodes": ["for_statement", "enhanced_for_statement", "while_statement", "do_statement"]
    },
    "typescript": {
        "import_nodes": ["import_statement", "call_expression"],
        "name_children": ["string"],
        "clean": strip_quotes,
        "validate": is_import_call(["require"]),
        "loop_nodes": ["for_statement", "for_in_statement", "while_statement", "do_statement"]
    },
    "go": {
        "import_nodes": ["import_spec"],
        "name_children": ["interpreted_string_literal"],
        "clean": strip_quotes,
        "validate": None,
        "loop_nodes": ["for_statement"]
    },
    "rust": {
        "import_nodes": ["use_declaration"],
        "name_children": ["scoped_identifier", "identifier"],
        "clean": None,
        "validate": None,
        "loop_nodes": ["for_expression", "while_expression", "loop_expression"]
    }
}

class CodeReader:
    """
    Detects the file type of code files and extracts any imported libraries.
    Supports multiple languages and uses language-specific regex patterns and parsing.
    """

    def __init__(self, filepath) -> None:
        self.filepath = filepath
        self.filetype = None
        self.libraries = []
        self.complexity = {}

        # Checks if the filepath exists
        if not os.path.isfile(self.filepath):
            raise FileNotFoundError(f"File not found: {self.filepath}")

        # Calls extract method to populate file type and libraries 
        self.extract()

    def extract_file_type(self):
        """
        Identifies the file type using file extensions or shebang line as a fallback.
        Raises a value error if the file can't be identified.
        """
        _, extension = os.path.splitext(self.filepath)
        
        # Maps the extension to the extension_mappings.py dictionary
        self.filetype = em.get(extension.lower(), None)
            
        # If extension check fails use pygments instead
        if self.filetype is None:
            try:
                with open(self.filepath, 'rb') as f:
                    content = f.read()

                lexer = get_lexer_for_filename(self.filepath, content)
                self.filetype = lexer.name.lower()
                
            except Exception as e:
                raise ValueError(f"Error! Pygments failed to analyze file '{self.filepath}': {e}")
        
        if not self.filetype:
            raise ValueError(f"Error! File is not a programmming file '{self.filepath}'")
        
        if self.filetype not in LANGUAGE_MAP:
            raise ValueError(f"Error! Unsupported language '{self.filetype}' for file '{self.filepath}'")

    def parse_file(self):
        if self.filetype not in LANGUAGE_MAP:
            raise ValueError(f"Language does not support deep analysis: {self.filetype}")
        
        parser = Parser(Language(LANGUAGE_MAP[self.filetype]))
        
        with open(self.filepath, "rb") as f:
            content = f.read()
        
        return parser.parse(content)

    def find_nodes(self, node, node_types: list):
        results = []
    
        if node.type in node_types:
            results.append(node)
        
        for child in node.children:
            results.extend(self.find_nodes(child, node_types))
        
        return results

    def extract_imports(self, root_node):
        if not self.filetype:
            return []

        config = LANGUAGE_CONFIGS.get(self.filetype)

        if not config:
            return []
        
        imports = []
        import_nodes = self.find_nodes(root_node, config["import_nodes"])
        
        for node in import_nodes:
            # Validate node if validator exists
            if config.get("validate") and not config["validate"](node):
                continue
            
            # Search recursively within the import node
            name_nodes = self.find_nodes(node, config["name_children"])
            
            if name_nodes:
                lib_name = name_nodes[0].text.decode("utf-8")
                
                if config["clean"]:
                    lib_name = config["clean"](lib_name)
                
                imports.append(lib_name)
        
        return imports
    
    def extract_complexity(self, root_node):
        if not self.filetype:
            return {}
        
        config = LANGUAGE_CONFIGS.get(self.filetype)
        
        if not config or "loop_nodes" not in config:
            return {}
        
        loop_types = config["loop_nodes"]
        top_level_loops = self._find_top_level_loops(root_node, loop_types)
        
        loop_structures = []
        max_depth = 0
        
        for loop_node in top_level_loops:
            loops = self._collect_loops(loop_node, loop_types, 1)
            structure_depth = max(loop["depth"] for loop in loops)
            max_depth = max(max_depth, structure_depth)
            loop_structures.append({
                "complexity": self._depth_to_complexity(structure_depth),
                "loops": loops,
            })
        
        return {
            "max_depth": max_depth,
            "estimated": self._depth_to_complexity(max_depth),
            "loop_structures": loop_structures,
        }


    def _find_top_level_loops(self, node, loop_types):
        """Finds loops that aren't nested inside other loops."""
        if node.type in loop_types:
            return [node]
        
        results = []
        for child in node.children:
            results.extend(self._find_top_level_loops(child, loop_types))
        return results


    def _collect_loops(self, node, loop_types, depth):
        """Collects a loop and all nested loops within it."""
        loops = [{
            "type": node.type,
            "line": node.start_point[0] + 1,
            "depth": depth,
        }]
        
        for child in node.children:
            if child.type in loop_types:
                loops.extend(self._collect_loops(child, loop_types, depth + 1))
            else:
                loops.extend(self._search_for_loops(child, loop_types, depth + 1))
        
        return loops


    def _search_for_loops(self, node, loop_types, depth):
        """Searches non-loop nodes for nested loops."""
        loops = []
        for child in node.children:
            if child.type in loop_types:
                loops.extend(self._collect_loops(child, loop_types, depth))
            else:
                loops.extend(self._search_for_loops(child, loop_types, depth))
        return loops


    def _depth_to_complexity(self, depth):
        if depth == 0:
            return "O(1)"
        elif depth == 1:
            return "O(n)"
        else:
            return f"O(n^{depth})"

    def extract(self):
        self.extract_file_type()
        
        if self.filetype in LANGUAGE_MAP:
            tree = self.parse_file()
            self.libraries = self.extract_imports(tree.root_node)
            self.complexity = self.extract_complexity(tree.root_node)