# Peer testing Heuristic Evaluation Plan

There will be 3 machines set up with the terminal open and with the python virtual enviroment activated. The directory will be set to `capstone-project-team-10` and we'll have the help menu preloaded so that the user can look at the list of possible commands to be used by running `python -m src.main --cli --help`.

### Introduction

> "Today you are testing a command-line prototype that scans code projects to generate a resume, portfolio, or a timeline of skills identified in those projects. We have chosen some tasks that we're going to ask you to fulfill, you will be typing commands into this terminal to interact with the software. We are testing the tool, not your coding skills. If you get stuck, try refering to the help menu."

### Tasks

- **Simple Zip Scan:**

> "you have a  zip folder at `"tests\testdata\test_peer_testing\testScanFolder.zip"`, can you use the cli to scan it?"
>
> **Command: (For group members conducting the evaluation)**  
`python -m src.main --zip "tests\testdata\test_peer_testing\testScanFolder.zip"`

- **Simple Resume Scan:**

> "Now run a scan and generate a Resume PDF from the folder `tests\testdata\test_peer_testing` and check the output file".
>
> **Command:**  
 `python -m src.main "tests\testdata\test_peer_testing" --cli -r -c` or  
`python -m src.main "tests\testdata\test_peer_testing" --cli -y -r -c`

- **Specific File type scan:**

> "Run the same scan you just did for a resume, except this time filter it to only use .java files."  
>
> **Command:**  
`python -m src.main "tests\testdata\test_peer_testing" --cli --file-types java -r -c` or  
`python -m src.main "tests\testdata\test_peer_testing" --cli --file-types java -y -r -c` or any variation that generates a valid file.

- **Checking output:**

> "Now open the output file and compare to see if the filter worked and there's only .java files"  

- **Time Filter scan:**

> "Run a scan to generate a portfolio from the folder `tests\testdata\test_peer_testing` and filter it to only go through files created after April 2025."  
>
> **Command:**  
`python -m src.main "tests\testdata\test_peer_testing" --cli -y -p --after 2025-04-01 -c` or  
`python -m src.main "tests\testdata\test_peer_testing" --cli -y -p -a 2025-04-01 -c`

- **Super Detailed Scan:**

> "generate a skills timeline of files created before February 2026 and exclude the file at `./sample-folder/pathToBeExcluded` and only scan git commits from the user `JohnDoe`" (Placeholder git user).
>
>**Command:**  
`python -m src.main "tests\testdata\test_peer_testing" --cli -y -c -t -b 2026-02-01 --exclude-paths "tests\testdata\test_peer_testing\sample.txt" -g JohnDoe`  

### Notes

- The commands are just for reference, as the testers can achieve the desired result in many ways, but it will most likely look something like the commands above.
- The sample folders, zip files, github user etc. are only placeholders for now until we make the the sample test folders containing the files the testers will use.
- We could potentially provide the testers with a piece of paper containing the exact folder names and paths to make it easier and less tedious for them when writing.

### Things to note when reporting

- Try focusing on which parts testers get stuck in, and which commands they seem to struggle with the most.
- Note if they are using `-y` for ease or if they completely overlooked it.
- Note if they are writing `.` when using `--file-types`. For example writing `--file-types .py`.

### Questionnaire

These questions will be asked in a google form after testing is done.

1. How comfortable are you generally with using Command Line Interfaces (CLI)?  
[ ] 1 - Uncomfortable  
[ ] 2  
[ ] 3  
[ ] 4  
[ ] 5 - Comfortable

2. On a scale of 1-5, how easy was it to figure out the correct commands (flags)?  
[ ] 1 - Very Difficult (I had to guess constantly)  
[ ] 2  
[ ] 3  
[ ] 4  
[ ] 5 - Very Easy (The help menu explained everything)  

3. When you made a mistake (or if you had), how helpful would the error messages have been?  
[ ] 1 - Not helpful (Cryptic or no error message)  
[ ] 2  
[ ] 3  
[ ] 4  
[ ] 5 - Very helpful (Told me exactly how to fix it)  

4. How easy was it to locate the final Resume/Portfolio file on your computer?  
[ ] 1 - Very Difficult (I had to search my folders to find it)  
[ ] 2  
[ ] 3  
[ ] 4  
[ ] 5 - Very Easy (I knew exactly where to look)