"""
Utility module for library/framework coding patterns
"""

LANGUAGE_PATTERNS = {
    'java': r'^\s*import\s+(?:static\s+)?([a-zA-Z_][\w.]+)\s*;',
    'javascript': [
        r"import\s+(?:type\s+)?(?:(?:\{[^}]+\}|\*\s+as\s+\w+|\w+)(?:\s*,\s*\{[^}]+\})?)\s+from\s+['\"]([^'\"]+)['\"]",
        r"require\s*\(\s*['\"]([^'\"]+)['\"]\s*\)"
    ],
    'typescript': [
        r"import\s+(?:type\s+)?(?:(?:\{[^}]+\}|\*\s+as\s+\w+|\w+)(?:\s*,\s*\{[^}]+\})?)\s+from\s+['\"]([^'\"]+)['\"]",
        r"require\s*\(\s*['\"]([^'\"]+)['\"]\s*\)"
    ],
    'rust': r'^\s*use\s+([a-zA-Z_][\w:]+)',
    'go': r'import\s+"([^"]+)"|^\s+"([^"]+)"',
    'csharp': r'^\s*using\s+(?:static\s+)?([a-zA-Z_][\w.]+)\s*;',
    'c': r'^\s*#include\s*[<"]([^>"]+)[>"]',
    'cpp': r'^\s*#include\s*[<"]([^>"]+)[>"]',
    'php': [
        r"(?:require|include)(?:_once)?\s*[(\s]+['\"]([^'\"]+)['\"]",
        r'^\s*use\s+([a-zA-Z_\\][\w\\]+)(?:\s+as\s+\w+)?;'
    ],
    'ruby': r"(?:^|[^\w])require(?!_relative)\s*[(\s]*['\"]([^'\"]+)['\"]",
    'swift': r'^\s*(?:@testable\s+)?import\s+([a-zA-Z_][\w.]*)',
    'r': r'(?:library|require)\s*\(\s*["\']?([a-zA-Z_][\w.]*)["\']?\s*\)',
    'fortran': r'^\s*[Uu][Ss][Ee]\s+([a-zA-Z_][\w]*)',
    'perl': r'^\s*use\s+([a-zA-Z_][\w:]+)\s*;',
    'pascal': r'^\s*[Uu][Ss][Ee][Ss]\s+(.*?);',
    'vb': r'^\s*[Ii][Mm][Pp][Oo][Rr][Tt][Ss]\s+([a-zA-Z_][\w.]+)'
}