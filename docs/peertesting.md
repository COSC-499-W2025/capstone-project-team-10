# Peer testing Heuristic Evaluation Plan

There will be 3 machines set up with the terminal open and with the python virtual enviroment activated. The directory will be set to `capstone-project-team-10` and we'll have the help menu preloaded so that the user can look at the list of possible commands to be used by running `python -m src.main --cli --help`.

### Introduction

> "Today you are testing a command-line prototype that scans code projects to generate a resume, portfolio, or a timeline of skills identified in those projects. We have chosen some tasks that we're going to ask you to fulfill, you will be typing commands into this terminal to interact with the software. We are testing the tool, not your coding skills. If you get stuck, try refering to the help menu."

### Tasks:

- **Simple Zip Scan:** Scan the zip folder at `./sample-folder2/zipfolder.zip`  
**Command: (For group members conducting the evaluation)**  
`python -m src.main --zip "./sample-folder2/zipfolder.zip"`
- **Simple Resume Scan:** Run a scan and generate a Resume pdf from the folder `./sample-folder` (we will determine the name and contents of the folder later on).  
**Command:**  
 `python -m src.main "./sample-folder" --cli -r` or  
`python -m src.main "./sample-folder" --cli -y -r`

- **Specific File type scan:** Run the same scan for a resume, except this time filter it to only use .java files.  
**Command:**  
`python -m src.main "./sample-folder" --cli --file-types java -r` or  
`python -m src.main "./sample-folder" --cli --file-types java -y -r` or any variation that generates a valid file.

- **Time Filter scan:** Run a scan to generate a portfolio from `./sample-folder` and filter it to only use files created after April 2025.  
**Command:**  
`python -m src.main "./sample-folder" --cli -y -p --after 2025-04-01` or  
`python -m src.main "./sample-folder" --cli -y -p -a 2025-04-01`

- **Super Detailed Scan:** generate a skills timeline of files created before December 2025 and exclude the file at `./sample-folder/pathToBeExcluded` and only scan git commits from the user `JohnDoe` (Placeholder).  
**Command:**  
`python -m src.main "./sample-folder" --cli -y -t -b 2025-12-01 --exclude-paths "./sample-folder/pathToBeExcluded" -g JohnDoe`  

### Notes:

- The commands are just for reference, as the testers can achieve the desired result in many ways, but it will most likely look something like the commands above.
- The sample folders, zip files, github user etc. are only placeholders for now until we make the the sample test folders containing the files the testers will use.
- We could potentially provide the testers with a piece of paper containing the exact folder names and paths to make it easier and less tedious for them when writing.

### Things to note when reporting:

- Try focusing on which parts testers get stuck in, and which commands they seem to struggle with the most.
- Note if they are using `-y` for ease or if they completely overlooked it.
- Note if they are writing `.` when using `--file-types`. For example writing `--file-types .py`.