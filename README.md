# Team 10 Capstone

## Authors

- Adam Badry
- Abdalla Abbas
- Bao Pham
- Brett Hardy
- Samuel Alexander
- Toby Nguyen

## Project Design Documents

- [System Architecture Diagram](docs/System%20Architecture%20Diagram.pdf)
  Outlines the structure of our project, highlighting the different services and processes and the relationships between them. The SAD shows how UI, File search, Analysis, and File export services communicate and interact with one another to mine and display file data.
- [Data Flow Diagram](docs/Data%20Flow%20Diagram.pdf) Illustrates the flow of data throughout the project components and data stores. The DFD shows where information is gathered from and the processes and data stores it flows through. The DFD includes data from user input, data gathered from user selected files, and formated and polished data ready to be displayed to the user.

- [Work Breakdown Structure](docs/Work%20Breakdown%20Structure.md)

our work breakdown structure is managed by our github issues. We start with our base requirements that are blocked by all tasks required to complete them. when all tasks underneath are completed the requirement may be marked as completed. this also means that when bugs are discovered we can mark the requirement as uncompleted and blocked by the new bug. this lets us clearly mark which bugs affect which requirements, and the steps needed to fulfill the high level requirements.

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
Example: \_internal_method, \_hidden_variable

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

```sh
python src/main.py --cli

```

```sh

python -m src.main <file_path> [options]

```

- `<file_path>`: Path to start scanning, or a zip file to extract.

---

#### Options

| Option                            | Description                                                                                                                     | Example                                         |
| --------------------------------- | --------------------------------------------------------------------------------------------------------------------------------| ----------------------------------------------- |
| `--zip <zipfile>`                 | Extract the specified zip file and scan its contents.                                                                           | `--zip myprojects.zip`                          |
| `--exclude-paths <paths>`         | Space-separated list of absolute paths to exclude from the scan.                                                                | `--exclude-paths /path/to/folder /path/to/file` |
| `--file-types <types>`            | Space-separated list of file types to include (by extension, e.g. `py`, `md`, `pdf`).                                           | `--file-types py md pdf`                        |
| `-y`, `--yes`                     | Automatically grant file access permission (skip interactive prompt).                                                           | `-y`                                            |
| `-r`, `--resume_entries`          | Generate a PDF resume from scanned projects. Optionally specify a directory to save the result.                                 | `-r` or `-r /path/to/save`                      |
| `-p`, `--portfolio_entries`       | Generate a web portfolio from scanned projects. Optionally specify a directory to save the result.                              | `-p` or `-p /path/to/save`                      |
| `-t`, `--skill_timeline_entries`  | Generate a PDF of key skills from scanned projects, ordered chronologically. Optionally specify a directory to save the result. | `-t` or `-t /path/to/save`                      |
| `-i`, `--no_image`             | Disable rendering of project images when generating resumes and portfolio pages. Disabled by default. Only use with -r or -p      | `-i -r` or `-p -i`                                    |
| `-c`, `--clean`                   | Start a new log file instead of resuming the last one.                                                                          | `-c`                                            |
| `-b`, `--before <date>`           | Only include files created before the specified date (`YYYY-MM-DD`).                                                            | `-b 2023-01-01`                                 |
| `-a`, `--after <date>`            | Only include files created after the specified date (`YYYY-MM-DD`).                                                             | `-a 2022-01-01`                                 |
| `-q`, `--quiet`                   | Suppress output (except for log file location).                                                                                 | `-q`                                            |
| `-g`, `--github_username`         | When scanning git repos only scan commits related to this username.                                                             | `-g username`                                   |

---

#### Examples

##### Scan a Directory

```sh
python -m src.main /path/to/projects
```

##### Scan and Exclude Paths

```sh
python -m src.main /path/to/projects --exclude-paths .git node_modules
```

##### Scan Only Python and Markdown Files

```sh
python -m src.main /path/to/projects --file-types py md
```

##### Scan Files Created After a Certain Date

```sh
python -m src.main /path/to/projects --after 2022-01-01
```

##### Extract a Zip File and Scan

```sh
python -m src.main --zip myprojects.zip
```

##### Generate Resume PDF

```sh
python -m src.main /path/to/projects -r
```

Or specify a directory to save the resume:

```sh
python -m src.main /path/to/projects -r /path/to/save
```

##### Generate Portfolio Website

```sh
python -m src.main /path/to/projects -p
```

Or specify a directory to save the portfolio:

```sh
python -m src.main /path/to/projects -p /path/to/save
```

##### Generate Key Skills

```sh
python -m src.main /path/to/projects -t
```

Or specify a directory to save key skills:

```sh
python -m src.main /path/to/projects -t /path/to/save
```

##### Suppress Output

```sh
python -m src.main /path/to/projects -q
```

---

#### Notes

- If you do not use `-y`/`--yes`, you will be prompted for file access permission.
- The log file location will be printed at the end of the scan.
- Resume and portfolio generation require valid output directories, the default storage location is set by the params. The users downloads folder is the current default.

---

#### Troubleshooting

- No output? Use `-q` only if you want minimal output.
- Permission denied? Use `-y` to skip the prompt.
- Date filters not working? Ensure dates are in `YYYY-MM-DD` format.
- File types not filtering? Use extensions without the dot (e.g., `py`, not `.py`).

### With GUI

```sh
python src/main.py

```

## Parameters

The parameter service works by keeping a JSON object to parse and read from during operation.
To add new parameters they must be added to the param_defaults.json file located in the param folder(src/param/param_defaults.json)

To new parameters must fall under a category as layed out in the param_defaults.json file, new categories may be added to the root of the JSON object as needed.

parameters may be read and written using the provided functions in the param.py file located in the param folder(src/param/param.py)
The Key string is delimited by periods to indicate category levels.
For example to read the "project_name" parameter under the "config" object can be addressed by config.project_name

### Functions

get(key: str)
set(key: str, value: Any)
remove(key: str)
clear()
load_defaults()

## Resume and Portfolio Outputs

the resume and web portfolio are managed by the showcase.py Modules.
They are saved to the users downloads folder by default, but that can be changed by changing the export_folder_path global variable in the params. This is done so that the export folder defaults back to downloads on start up but can be changed during runtime, according to the users preference.

either a resume or portfolio can be generated by calling the generate_resume() or generate_portfolio() functions in the showcase.py module.

This should only be called after Analysis is complete and the results have been post processed(sorted, ranked, etc). It just does a line by line output of the final results to build the resume and portfolio. so garbage in the analysis results will lead to garbage in the resume and portfolio outputs.

## Testing

### Writing Unit tests

Testing framework is pytest
All test files shall start with "test\_"
and follow the formatting below

```python
class TestExample:
    def test_example(self):
        # Test Content
    def test_example2(self):
        # Test Content
```

Each component under test shall have its own "test\_" file to make readability and searching for tests easier

### Running the Unit tests

```sh
python -m pytest -q
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

To run the text_analysis.py make sure you run setup_nltk_data.py first.
