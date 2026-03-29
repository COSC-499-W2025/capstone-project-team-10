import sys
from pathlib import Path
# This file is needed for pytest to be able to run tests that are between separate folders like a fas module that calls a fss module by defining the structure and allowing for the use of relative imports.
# Add repository root and src directory to Python path.
repo_root = Path(__file__).resolve().parent.parent
src_path = repo_root / "src"
if str(repo_root) not in sys.path:
	sys.path.insert(0, str(repo_root))
if str(src_path) not in sys.path:
	sys.path.insert(0, str(src_path))