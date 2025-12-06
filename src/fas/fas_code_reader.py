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
        "loop_nodes": ["for_statement", "while_statement"],
        "class_nodes": ["class_definition"],
        "function_nodes": ["function_definition"],
    },
    "javascript": {
        "import_nodes": ["import_statement", "call_expression"],
        "name_children": ["string"],
        "clean": strip_quotes,
        "validate": is_import_call(["require"]),
        "loop_nodes": ["for_statement", "for_in_statement", "while_statement", "do_statement"],
        "class_nodes": ["class_declaration"],
        "function_nodes": ["function_declaration", "arrow_function"],
    },
    "c": {
        "import_nodes": ["preproc_include"],
        "name_children": ["string_literal", "system_lib_string"],
        "clean": strip_quotes_and_brackets,
        "validate": None,
        "loop_nodes": ["for_statement", "while_statement", "do_statement"],
        "class_nodes": [],
        "function_nodes": ["function_definition"],
    },
    "cpp": {
        "import_nodes": ["preproc_include"],
        "name_children": ["string_literal", "system_lib_string"],
        "clean": strip_quotes_and_brackets,
        "validate": None,
        "loop_nodes": ["for_statement", "while_statement", "do_statement", "for_range_loop"],
        "class_nodes": ["class_specifier"],
        "function_nodes": ["function_definition"],
    },
    "java": {
        "import_nodes": ["import_declaration"],
        "name_children": ["scoped_identifier"],
        "clean": None,
        "validate": None,
        "loop_nodes": ["for_statement", "enhanced_for_statement", "while_statement", "do_statement"],
        "class_nodes": ["class_declaration"],
        "function_nodes": ["method_declaration"],
    },
    "typescript": {
        "import_nodes": ["import_statement", "call_expression"],
        "name_children": ["string"],
        "clean": strip_quotes,
        "validate": is_import_call(["require"]),
        "loop_nodes": ["for_statement", "for_in_statement", "while_statement", "do_statement"],
        "class_nodes": ["class_declaration"],
        "function_nodes": ["function_declaration", "arrow_function"],
    },
    "go": {
        "import_nodes": ["import_spec"],
        "name_children": ["interpreted_string_literal"],
        "clean": strip_quotes,
        "validate": None,
        "loop_nodes": ["for_statement"],
        "class_nodes": [],
        "function_nodes": ["function_declaration", "method_declaration"],
    },
    "rust": {
        "import_nodes": ["use_declaration"],
        "name_children": ["scoped_identifier", "identifier"],
        "clean": None,
        "validate": None,
        "loop_nodes": ["for_expression", "while_expression", "loop_expression"],
        "class_nodes": ["struct_item", "impl_item"],
        "function_nodes": ["function_item"],
    },
}

class CodeReader:
    """
    Detects the file type of code files and extracts any libraries, functions, loops, complexities, and oop.
    Supports multiple languages and uses tree_sitter and parsing.
    """
    def __init__(self, filepath) -> None:
        self.filepath = filepath
        self.filetype = None
        self.libraries = []
        self.complexity = {}
        self.oop = {}

        # Checks if the filepath exists
        if not os.path.isfile(self.filepath):
            raise FileNotFoundError(f"File not found: {self.filepath}")

        # Calls extract method to populate file type and libraries 
        self.extract()

    def extract_file_type(self):
        """
        Identifies the file type using file extensions or pygments line as a fallback.
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
        
        # if self.filetype not in LANGUAGE_MAP:
        #     raise ValueError(f"Error! Unsupported language '{self.filetype}' for file '{self.filepath}'")
        return
            

    def parse_file(self):
        """Creates Parser for specific coding language"""
        if self.filetype not in LANGUAGE_MAP:
            # raise ValueError(f"Language does not support deep analysis: {self.filetype}")
            return None
            
        
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
        """Extracts libraries and packages using language specific keyword detection."""
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
        """Extracts loops and time complexities from nested loops."""
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
        """Collects all loops starting from node."""
        loops = []
        
        if node.type in loop_types:
            loops.append({
                "type": node.type,
                "line": node.start_point[0] + 1,
                "depth": depth,
            })
            depth += 1
        
        for child in node.children:
            loops.extend(self._collect_loops(child, loop_types, depth))
        
        return loops

    def _depth_to_complexity(self, depth):
        """Transforms depth value into Big O notation."""
        if depth == 0:
            return "O(1)"
        elif depth == 1:
            return "O(n)"
        else:
            return f"O(n^{depth})"

    def extract_oop(self, root_node):
        """Extracts OOP structures: classes and standalone functions."""
        if not self.filetype:
            return {}
        
        config = LANGUAGE_CONFIGS.get(self.filetype)
        
        if not config:
            return {}
        
        classes = []
        functions = []
        
        class_types = config.get("class_nodes", [])
        function_types = config.get("function_nodes", [])
        
        if class_types:
            class_nodes = self.find_nodes(root_node, class_types)
            for node in class_nodes:
                classes.append(self._extract_class_info(node, function_types))
        
        # Find standalone functions (not inside classes)
        if function_types:
            functions = self._find_standalone_functions(root_node, class_types, function_types)
        
        return {
            "classes": classes,
            "functions": functions,
        }

    def _extract_class_info(self, class_node, function_types):
        """Extracts information from a class node."""
        name = None
        methods = []
        has_inheritance = False
        
        for child in class_node.children:
            # Get class name
            if child.type in ["identifier", "name", "type_identifier"]:
                name = child.text.decode("utf-8")
            
            # Check for inheritance
            if child.type in ["argument_list", "superclass", "class_heritage", "base_class_clause"]:
                has_inheritance = True
        
        # Find methods inside the class
        method_nodes = self.find_nodes(class_node, function_types)
        for method_node in method_nodes:
            method_name = self._get_function_name(method_node)
            if method_name:
                methods.append(method_name)
        
        return {
            "name": name,
            "line": class_node.start_point[0] + 1,
            "methods": methods,
            "has_inheritance": has_inheritance,
        }

    def _find_standalone_functions(self, root_node, class_types, function_types):
        """Finds functions that are not inside classes."""
        functions = []
        
        for child in root_node.children:
            if child.type in function_types:
                name = self._get_function_name(child)
                if name:
                    functions.append({
                        "name": name,
                        "line": child.start_point[0] + 1,
                    })
            elif child.type not in class_types:
                # Recurse into non-class nodes (e.g., modules, namespaces)
                functions.extend(self._find_standalone_functions(child, class_types, function_types))
        
        return functions

    def _get_function_name(self, func_node):
        """Extracts the function name from a function node."""
        for child in func_node.children:
            if child.type in ["identifier", "name", "property_identifier"]:
                return child.text.decode("utf-8")
            if child.type in ["function_declarator", "declarator"]:
                for subchild in child.children:
                    if subchild.type == "identifier":
                        return subchild.text.decode("utf-8")
        return None

    def extract(self):
        self.extract_file_type()
        tree = self.parse_file()
        if tree is None:
            # Unsupported language
            self.libraries = []
            self.complexity = {}
            self.oop = {}
            return
        self.libraries = self.extract_imports(tree.root_node)
        self.complexity = self.extract_complexity(tree.root_node)
        self.oop = self.extract_oop(tree.root_node)

    def extract_data_from_code_file(self):
        """Returns all extracted data as a single dictionary."""
        return {
            "filetype": self.filetype,
            "libraries": self.libraries,
            "complexity": self.complexity,
            "oop": self.oop
        }