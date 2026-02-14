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

4. Install nltk
   Run the python script at utils/setup_nltk_data.py
   This will install all dependencies for the nltk library

5. Run the app or tests as needed, the app must be run as a module.

## Running the app

### With CLI

```sh
python src/main.py --cli

```

```sh

python -m src.main <file_path> [command-line-options] --cli

```

- `<file_path>`: Path to start scanning, or a zip file to extract.

---

#### Options

| Option                           | Description                                                                                                                     | Example                                         |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------- |
| `<filepath>`                     | Extract the specified directory or file and scan its contents.                                                                  | `myprojects.zip`                                |
| `--exclude-paths <paths>`        | Space-separated list of absolute paths to exclude from the scan.                                                                | `--exclude-paths /path/to/folder /path/to/file` |
| `--file-types <types>`           | Space-separated list of file types to include (by extension, e.g. `py`, `md`, `pdf`).                                           | `--file-types py md pdf`                        |
| `-y`, `--yes`                    | Automatically grant file access permission (skip interactive prompt).                                                           | `-y`                                            |
| `-r`, `--resume_entries`         | Generate a PDF resume from scanned projects. Optionally specify a directory to save the result.                                 | `-r` or `-r /path/to/save`                      |
| `-p`, `--portfolio_entries`      | Generate a web portfolio from scanned projects. Optionally specify a directory to save the result.                              | `-p` or `-p /path/to/save`                      |
| `-t`, `--skill_timeline_entries` | Generate a PDF of key skills from scanned projects, ordered chronologically. Optionally specify a directory to save the result. | `-t` or `-t /path/to/save`                      |
| `-i`, `--no_image`               | Disable rendering of project images when generating resumes and portfolio pages. Enabled by default. Only use with -r or -p     | `-i -r` or `-p -i`                              |
| `-c`, `--clean`                  | Start a new log file instead of resuming the last one.                                                                          | `-c`                                            |
| `-s`, `--sort`                   | Indicates to prompt the sort after a log creation                                                                               | `python -m src.main /path/to/save -s --cli`     |
| `-b`, `--before <date>`          | Only include files created before the specified date (`YYYY-MM-DD`).                                                            | `-b 2023-01-01`                                 |
| `-a`, `--after <date>`           | Only include files created after the specified date (`YYYY-MM-DD`).                                                             | `-a 2022-01-01`                                 |
| `-q`, `--quiet`                  | Suppress output (except for log file location).                                                                                 | `-q`                                            |
| `-g`, `--github_username`        | When scanning git repos only scan commits related to this username.                                                             | `-g username`                                   |

---

#### Examples

##### Scan a Directory

```sh
python -m src.main /path/to/projects
```

##### Scan and Exclude Paths

```sh
python -m src.main /path/to/projects --exclude-paths /path/to/sub/projects /path/to/sub/projects2
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

Use the following command to run the test suite

```sh
python -m pytest -q
```

## Building (Incomplete)

This Project uses pyinstaller for its build path. This should have been installed if you ran the setup correctly

### Building the app (Incomplete)

The following command will need to be run on each operating system the app will be compiled for when releasing
The resulting app is packaged with the python interpretter making the end user experience very clean. It also makes the file size abnormally large

```sh
pyinstaller --onefile --add-data "resources:resources" src/main.py --windowed

```

## Other Notes

To run the text_analysis.py make sure you run setup_nltk_data.py first.

## Milestone 1 Compliance

### - [X] Require the user to give consent for data access before proceeding

    - The User must indicate consent via the CLI flag `-y` or `--yes` to proceed without prompt
    - if the user does not include the -y flag they will be prompted to give consent before proceeding

### - [X] Parse a specified zipped folder containing nested folders and files

    - The CLI flag `--zip <zipfile>` allows the user to specify a zip file to extract and scan

### - [X] Return an error if the specified file is in the wrong format

    - If the specified file is not a zip file an error message is returned and the program exits

### - [X] Request user permission before using external services (e.g., LLM) and provide implications on data privacy about the user's data

    - There are no external services used in Milestone 1

### - [X] Have alternative analyses in place if sending data to an external service is not permitted

    - All analyses are done locally in Milestone 1

### - [X] Store user configurations for future use

    - User configurations are stored using the param system, and stored in json format

### - [X] Distinguish individual projects from collaborative projects

    - Collaborative projects are identified by the presence of multiple authors in git commit history
    - Users can filter out their own commits using the -g flag to set their own username

### - [X] For a coding project, identify the programming language and framework used

    - Programming languages are identified by file extension
    - frameworks/libraries are identified by the imports used in the code files

### - [X] Extrapolate individual contributions for a given collaboration project

    - An individuals contributions to git projects are distinguished from othe contributors in the project such as
        - number of commits,
        - lines added/removed,
        - and commit objectives

### - [X] Extract key contribution metrics in a project, displaying information about the duration of the project and activity type contribution frequency (e.g., code vs test vs design vs document), and other important information

    - Contribution metrics are extracted from git commit history, including number of commits, lines added/removed, and commit objectives
    - Files tracked by the git project that were worked on by the user are scanned and included as skill indicators.

### - [X] Extract key skills from a given project

    - Skills are extracted using a combination of Natural Language processing and keyword matching from a predefined skill set (For programming libraries and frameworks)

### - [X] Output all the key information for a project

    - Key information is saved to a log file in csv for further processing

### - [X] Store project information into a database

    - Project information is stored in a local csv log that are managed by the log service. This acts as a simple database for storing project information

### - [X] Retrieve previously generated portfolio information

    - Previously generated portfolios are saved to the users drive, and may be retrieved by the user
    - Portfolio may be regenerated from previous logs

### - [X] Retrieve previously generated résumé item

    - Previously generated resumes are saved to the users drive, and may be retrieved by the user
    - Resumes may be generated from previous logs

### - [X] Rank importance of each project based on user's contributions

    - Git projects receive an importance based on the users contributions

### - [X] Summarize the top ranked projects

    - Projects can be sorted and displayed by importance

### - [X] Delete previously generated insights and ensure files that are shared across multiple reports do not get affected

    - The user may start a new log file using the -c or --clean flag, this will create a new log file and not affect any previously generated insights, or allow previous results to affect the current scan

### - [X] Produce a chronological list of projects

    - The user may generate a chronological list of projects using the -t or --skill_timeline_entries flag

### - [X] Produce a chronological list of skills exercised

    - The user may generate a chronological list of projects using the -t or --skill_timeline_entries flag

#### Tickets for "Functional Requirements" Have been closed if they have been met by current functionality

## Milestone 2 Compliance:

### "API" Compliance

Because of how our project design differs from other groups its very important that we highlight the seperation of the Backend functionality and the front-end processing. To fulfill this requirement we are required to use singular functions with arguments as entry points for functionality.

Good examples of this are the FSS and FAS usage, calling the function with arguments gives a single output that is usable by the GUI

Since we are not using a web-app we do not have to fulfill requirement #31 "Use a FastAPI to faciliate the communication between the backend and the frontend"

The API requirements we must fulfil are

#### POST /projects/upload:

- [x] the FSS must be reworked to call the zip extractor itself

Fulfilled by PR: https://github.com/COSC-499-W2025/capstone-project-team-10/pull/221

#### POST /privacy-consent

- [x] Fulfilled by the GUI call to display the privacy prompt

Fulfilled by PR: https://github.com/COSC-499-W2025/capstone-project-team-10/pull/177

#### GET /projects

- [x] Fulfilled by having the GUI access lines from the log file through the log API

Fulfilled by PR: https://github.com/COSC-499-W2025/capstone-project-team-10/pull/200

#### GET /projects/{id}

- [x] Fulfilled by having the GUI access lines from the log file through the log API and the showcase page

Fulfilled by PR: TODO

#### GET /skills

Some additional work may need to be completed for this feature, as we could create a different log to store extracted skills but this may require a
non-trivial amount of rework for the CLI

- [ ] I highly recommend that this be completed in order to abide by the requirements, even though it is not strictly necessary from a
      functionality perspective

Fulfilled by PR: TODO

#### GET /resume/{id}

- [x] A new resume API is needed to fulfill this requirement, making the program store created resumes in application storage

Fulfilled by PR: https://github.com/COSC-499-W2025/capstone-project-team-10/pull/219

#### POST /resume/generate

- [x] Fulfilled by Showcase functionality

#### POST /resume/{id}/edit

- [x] New Showcase functionality is needed to facilitate the editing of resume objects

Fullfilled by PRs:

- https://github.com/COSC-499-W2025/capstone-project-team-10/pull/220
- https://github.com/COSC-499-W2025/capstone-project-team-10/pull/207

#### GET /portfolio/{id}

- [ ] A new portfolio API is needed to fulfill this requirement, making the program store created portfolios in application storage

Fulfilled by PR: TODO

#### POST /portfolio/generate

- [x] Fulfilled by Showcase functionality

#### POST /portfolio/{id}/edit

- [x] New Showcase functionality is needed to facilitate the editing of portfolio objects

Fullfilled by Log edit API and PR:

- https://github.com/COSC-499-W2025/capstone-project-team-10/pull/207

### Other Milestone 2 requirements

#### - [X] Allow incremental information by adding another zipped folder of files for the same portfolio or résumé that incorporates additional information at a later point in time

Logs allow for incremental scans.

#### - [X] Recognize duplicate files and maintains only one in the system

System does not maintain files from user-space in its own database

#### - [X] Allow users to choose which information is represented (e.g., re-ranking of projects, corrections to chronology, attributes for project comparison, skills to highlight, projects selected for showcase)

Fulfilled by PRs:

- https://github.com/COSC-499-W2025/capstone-project-team-10/pull/193
- https://github.com/COSC-499-W2025/capstone-project-team-10/pull/197

#### - [X] Incorporate a key role of the user in a given project

Uncertain what this means, but we do create user specific skills and outcomes for collaborative projects.

#### - [X] Incorporate evidence of success (e.g., metrics, feedback, evaluation) for a given project

Users measures of success (amount of contributions, and skills contributed) are recorded for collaborative projects

#### - [ ] Allow user to associate a portfolio image for a given project to use as the thumbnail

TODO: https://github.com/COSC-499-W2025/capstone-project-team-10/issues/226

#### - [X] Customize and save information about a portfolio showcase project

Fulfilled by PR's:

- https://github.com/COSC-499-W2025/capstone-project-team-10/pull/197
- https://github.com/COSC-499-W2025/capstone-project-team-10/pull/193

#### - [X] Customize and save the wording of a project used for a résumé item

Fulfilled by PR's:

- https://github.com/COSC-499-W2025/capstone-project-team-10/pull/197
- https://github.com/COSC-499-W2025/capstone-project-team-10/pull/193

#### - [X] Display textual information about a project as a portfolio showcase

Fulfilled by PR: https://github.com/COSC-499-W2025/capstone-project-team-10/pull/207

#### - [X] Display textual information about a project as a résumé item

Fulfilled by PR: https://github.com/COSC-499-W2025/capstone-project-team-10/pull/207

#### - [X] You need to provide at least two zipped test data files for the same project, one as a snapshot at an earlier point in time, and another as a snapshot later in time that could have additional/modified files, with the following directory structure:

test-data.zip:
./code_collab_proj/app/
./code_collab_proj/test/
./code_collab_proj/doc/
etc.

PR: https://github.com/COSC-499-W2025/capstone-project-team-10/pull/205

#### - [X] You need to provide at least one zipped test data file that has multiple projects, showcasing individual and collaborative projects. If you have code and non-code projects, be sure to provide test data for those too. The directory structure should resemble the following:

test-data.zip:
./code_indiv_proj/
./code_collab_proj/
./text_indiv_proj/
./image_indiv_proj/
etc.

PR: https://github.com/COSC-499-W2025/capstone-project-team-10/pull/205

#### - [X] Your API endpoints must be tested as if they are being called over HTTP but without running a real server, ensuring the correct status code and expected data.

Unclear how this applies to us, but our Unit tests do check outputs from their function calls

#### - [X] Your system must have clear documentation for all of the API endpoints

Completed in the API Documentation section of this README

### Notes and Rework Required After Assessment:

After carefully combing over the functionality it appears that the main areas that require rewrites are:

#### - [X] FSS

- Rework the function calls to be more API like
- Make the FSS responsible for processing zipped folders

Completed in PR: https://github.com/COSC-499-W2025/capstone-project-team-10/pull/202

#### - [X] Project Grouping rewrites

- Grouping will have to be rewritten to allow for customized project grouping

Completed in PR: https://github.com/COSC-499-W2025/capstone-project-team-10/pull/203

#### - [X] Logging and FAS rewrites

- We may require rewriting how the logs/FileAnalysis objects are structured to allow for customized project grouping
  shift away from logging individual files and logging "Projects" that contain files. the file analysis can remain but must be encapsulated.
  Where this encapsulation happens is up to the developer, I do suggest moving it into the FAS though to keep the logging dynamic
- May require rewrites to support attaching an image to a project.

Completed in PR's:

- https://github.com/COSC-499-W2025/capstone-project-team-10/pull/197
- https://github.com/COSC-499-W2025/capstone-project-team-10/pull/193

#### - [X] Showcase rewrites

- Showcase may have to have its own logging system to allow for modification, without influencing the scan logs, or being overwritten by future updates. this depends on how modification is implemented, and can change. Two birds can be killed with one stone by implementing the versioning and saving of generated outputs inside the application data. This may have adverse effects on the user if saving lots of info, so I suggest implementing a hard ceiling of 10 resumes to persist, any new ones generated delete the oldest one. We can have this parameterized for user control.
- We are also going to have to make it more "resume" like with fields for the user to enter other information about themselves

#### - [X] All backend functionality

- Ensure that "backend" functions are API like in nature, every class shall only have one function that can be called by the GUI/CLI
- Ensure that "backend" functions are documented like an API, with inputs, and expected outputs defined. Specifically focus on
    - Success -> Output
    - Failure -> Output

Status:

- [x] FAS
- [x] FSS
- [x] Log
- [x] Showcase
- [x] Zip

### GUI Development:

The GUI development/planning shall begin when the design is finalized

## API Documentation

### POST /projects/upload

To upload a project simply call the FSS search function. The FSS search function takes in an FSS_Search object that can be configured with the following parameters:

- input_path: Which contains the file path of the zip/directory meant to be scanned, this is the only required parameter for the FSS search function, all other parameters have default values that can be used if the user does not wish to configure them.

- excluded_path: This is a set of file paths that the user wishes to exclude from the scan, this can be used to exclude files that may contain sensitive information, or files that the user does not wish to be included in the analysis. This is an optional parameter and defaults to an empty set.

- file_types: This is a set of file types that the user wishes to include in the scan, this can be used to only include certain types of files that may be relevant to the analysis. This is an optional parameter and defaults to an empty set, which means that all file types will be included in the scan.

- time_lower_bound: datetime | None = None, This is a datetime object that represents the lower bound of the time range for the files to be included in the scan. This can be used to only include files that were created or modified after a certain date. This is an optional parameter and defaults to None, which means that there is no lower bound on the time range for the files to be included in the scan.

- time_upper_bound: datetime | None = None, This is a datetime object that represents the upper bound of the time range for the files to be included in the scan. This can be used to only include files that were created or modified before a certain date. This is an optional parameter and defaults to None, which means that there is no upper bound on the time range for the files to be included in the scan.

### POST /privacy-consent

- Privacy consent is handled by the GUI and CLI, requiring user consent before proceeding with any file access or analysis. The user can provide consent via the CLI flag `-y` or `--yes` to proceed without prompt, or they will be prompted to give consent before proceeding if the flag is not used. In the GUI, a privacy consent prompt is displayed to the user, and they must provide consent before proceeding with any file access or analysis.

### GET /projects -> log.follow_log()

- Project information is retrieved from the log file through the logging API, which acts as a simple database for storing project information. The GUI can access lines from the log file through the log API to display project information to the user.

### GET /projects/{id} -> TODO

- TODO: This is currently fulfilled by the GUI accessing lines from the log file through the log API and the showcase page, but we may want to implement a specific API endpoint for this functionality to better separate concerns and make it more API like. https://github.com/COSC-499-W2025/capstone-project-team-10/issues/229

### GET /skills -> showcase.generate_skill_timeline()

- This is currently fulfilled by calling the generate_skill_timeline function in the showcase. This takes the current active log and translates it into a skill timeline, which is a chronological list of skills exercised in the projects. This is then saved to the users parameter for offload, and can be accessed by the GUI to display the skill timeline to the user.

### GET /resume/{id} -> resume_manager.get()

- This is fulfilled by calling the get function from the resume_manager with the resume id, the resume manager will then return the resume object with a matching ID.

### POST /resume/generate -> showcase.generate_resume()

- This is fullfilled by a call to the generate_resume() function in the showcase module, which generates a resume PDF from the scanned projects. The generated resume is saved to the user's parameter for offload "showcase_export_path". This path defaults to the users downloads folder but can be changed by the user..

### POST /resume/{id}/edit -> log.update()

- Using the log update function with the line you would like to write, the logs are updated and then showcase items can be regenerated by calling their respective function to reflect the changes made by the user. This allows for a more dynamic and interactive experience for the user when editing their resume information. the update function takes in a FileAnalysis type object.

The FileAnalysis object has the following parameters:

- file_path: str,
- file_name: str,
- file_type: str,
- last_modified: str,
- created_time: str,
- extra_data: Optional[Any] = None,
- importance: float = 0.0,
- customized: bool = False,
- project_id: Optional[str] = None,

### GET /portfolio/{id} -> TODO

- TODO: https://github.com/COSC-499-W2025/capstone-project-team-10/issues/225

### POST /portfolio/generate showcase.generate_portfolio()

- this is fullfilled by a call to the generate_portfolio() function in the showcase module, which generates a portfolio website from the scanned projects. The generated portfolio is saved to the user's parameter for offload "showcase_export_path". This path defaults to the users downloads folder but can be changed by the user.

### POST /portfolio/{id}/edit -> log.update()

- Using the log update function with the line you would like to write, the logs are updated and then showcase items can be regenerated by calling their respective function to reflect the changes made by the user. This allows for a more dynamic and interactive experience for the user when editing their resume information. the update function takes in a FileAnalysis type object.

The FileAnalysis object has the following parameters:

- file_path: str,
- file_name: str,
- file_type: str,
- last_modified: str,
- created_time: str,
- extra_data: Optional[Any] = None,
- importance: float = 0.0,
- customized: bool = False,
- project_id: Optional[str] = None,

## API Testing

API testing is currently done through unit tests, which test the functionality of the API endpoints by calling the respective functions and checking their outputs.

Our testing suite can be run using the following command:

```sh
python -m pytest -q
```

for more verbose output, simply remove the -q flag:

```sh
python -m pytest
```

All tests are stored in the src/tests folder, and are organized by API. Each test file starts with "test\_" and contains a class that also starts with "Test\_" followed by the name of the API being tested. Each test function within the class starts with "test\_" and tests a specific functionality of the API.
