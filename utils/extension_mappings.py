"""
Utility module for file extensions
"""

CODING_FILE_EXTENSIONS = {
    # Python
    '.py': 'python',
    '.pyw': 'python',
    '.pyx': 'python',
    '.pyi': 'python',
    
    # JavaScript/TypeScript
    '.js': 'javascript',
    '.jsx': 'javascript',
    '.mjs': 'javascript',
    '.cjs': 'javascript',
    '.ts': 'typescript',
    '.tsx': 'typescript',
    
    # Java/JVM Languages
    '.java': 'java',
    '.kt': 'kotlin',
    '.kts': 'kotlin',
    '.scala': 'scala',
    '.groovy': 'groovy',
    '.gvy': 'groovy',
    '.clj': 'clojure',
    '.cljs': 'clojurescript',
    
    # C/C++
    '.c': 'c',
    '.h': 'c',
    '.cpp': 'cpp',
    '.cc': 'cpp',
    '.cxx': 'cpp',
    '.c++': 'cpp',
    '.hpp': 'cpp',
    '.hh': 'cpp',
    '.hxx': 'cpp',
    '.h++': 'cpp',
    
    # C#/.NET
    '.cs': 'csharp',
    '.vb': 'vb',
    '.fs': 'fsharp',
    '.fsi': 'fsharp',
    '.fsx': 'fsharp',
    
    # Web Backend
    '.php': 'php',
    '.phtml': 'php',
    '.rb': 'ruby',
    '.rake': 'ruby',
    '.go': 'go',
    '.rs': 'rust',
    '.swift': 'swift',
    
    # Scripting
    '.sh': 'shell',
    '.bash': 'bash',
    '.zsh': 'zsh',
    '.ksh': 'ksh',
    '.csh': 'csh',
    '.fish': 'fish',
    '.pl': 'perl',
    '.pm': 'perl',
    '.lua': 'lua',
    '.tcl': 'tcl',
    
    # Functional/Other
    '.hs': 'haskell',
    '.lhs': 'haskell',
    '.ml': 'ocaml',
    '.mli': 'ocaml',
    '.erl': 'erlang',
    '.hrl': 'erlang',
    '.ex': 'elixir',
    '.exs': 'elixir',
    '.elm': 'elm',
    '.jl': 'julia',
    
    # Data Science/Statistical
    '.r': 'r',
    '.R': 'r',
    '.m': 'matlab',
    
    # Systems/Low-level
    '.asm': 'assembly',
    '.s': 'assembly',
    '.v': 'verilog',
    '.vh': 'verilog',
    '.vhd': 'vhdl',
    '.vhdl': 'vhdl',
    
    # Mobile
    '.dart': 'dart',
    
    # Other
    '.sql': 'sql',
    '.nim': 'nim',
    '.cr': 'crystal',
    '.d': 'd',
    '.pas': 'pascal',
    '.pp': 'pascal',
    '.f': 'fortran',
    '.for': 'fortran',
    '.f90': 'fortran',
    '.cob': 'cobol',
    '.cbl': 'cobol',
    '.ada': 'ada',
    '.adb': 'ada',
    '.ads': 'ada',
}

SHEBANG_MAPPINGS = {
    'python': 'python',
    'bash': 'bash',
    'sh': 'shell',
    'node': 'javascript',
    'ruby': 'ruby',
    'perl': 'perl',
}
