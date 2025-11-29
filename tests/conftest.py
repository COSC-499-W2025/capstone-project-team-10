import sys
from pathlib import Path
# This file is needed for pytest to be able to run tests that are between separate folders like a fas module that calls a fss module by defining the structure and allowing for the use of relative imports.
# Add src directory to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))