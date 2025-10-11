# Team 10 Capstone
## Authors

- Adam Badry
- Abdalla Abbas
- Bao Pham
- Brett Hardy
- Sam Alexander
- Toby Nguyen

## Project Conventions and Guide for Contribution

### Naming Conventions

#### Variables & Functions:
Use snake_case (lowercase, words separated by underscores).
Example: user_name, calculate_total()

#### Classes:
Use PascalCase (capitalize each word, no underscores).
Example: UserProfile, DataProcessor

#### Constants:
Use UPPER_CASE with underscores.
Example: MAX_RETRIES, DEFAULT_TIMEOUT

#### Modules & Files:
Use snake_case.
Example: data_loader.py, utils.py

#### Private Members:
Prefix with a single underscore.
Example: _internal_method, _hidden_variable

### Readable Code Practices

#### Type Systems

- Each declaration shall have a explicit type hint for any variables, as well as function return types 
Example:
```python
def numbers_equal(number_1: int, number_2: int) -> bool:
    return number_1 == number_2
```

#### Indentation:
- Tab size shall be 4 spaces per indentation level.

#### Line Length:
- Avoid Text wrap where possible

#### Whitespace:
- Use blank lines to separate functions, classes, and logical sections.

#### Comments:
- Avoid descriptive comments where necessary to avoid comment drift. 
    Code should be easily readable and understandable independent of comments

#### Descriptive Names:
- Use meaningful names that describe the purpose of the variable, function, or class.

#### NO Magic Numbers:
- Assign numbers to meaningfully named constants (no using i or j for loops)

### Pull requests

#### Link a ticket being closed
Each PR shall have in its description "closes #XX" Where #XX is the ticket the PR addresses.
This links the PR to the issue and automatically closes the issue when the PR is approved

#### PRs require at least two reviewers to close and merge. 
at least two reviewers must leave comments on a PR before merging

## Setup

### WARNING: USE PYTHON 3.12.X OR NEWER
1. Clone the repo:
   git clone <repo-url>
   cd capstone-project-team-10

2. Create and activate a virtual environment:
   python3 -m venv venv
   source venv/bin/activate

3. Install dependencies:
   pip install -r requirements.txt

4. Run the app or tests as needed.

## Running the app

### With CLI
``` sh
python src/main.py --cli 

``` 

### With GUI

``` sh
python src/main.py

``` 
## Testing

### Writing Unit tests

All test files shall start with "test_"
and follow the formatting below
```python
import unittest

class test_example(unittest.TestCase):
    def test_example(self):
        # Test Content
    def test_example2(self):
        # Test Content

if __name__ == '__main__':
    unittest.main()
```

Each component under test shall have its own "test_" file to make readability and searching for tests easier

### Running the Unit tests

```sh
python -m unittest discover tests

```

## Building

This Project uses pyinstaller for its build path. This should have been installed if you ran the setup correctly

### Building the app

The following command will need to be run on each operating system the app will be compiled for when releasing
The resulting app is packaged with the python interpretter making the end user experience very clean. It also makes the file size abnormally large

```sh
pyinstaller --onefile --add-data "resources:resources" src/main.py --windowed

```


## Other Notes
