# Capstone project requirements
## Consolidated Requirements for Mining Digital Work Artifacts App
### 1. Core Functionality
#### 1.1 - The program shall allow the user to choose what to scan (folders, disks, file types) for privacy reasons.
#### 1.2 - The program shall support multiple scan modes:
    - All files (thorough search)
    - Quick scan (faster, lightweight)
    - Custom scan (user specifies paths or file types)
    - Incremental scan (only scan files changed since last scan)
#### 1.3 - The program shall be compiled for cross-platform execution (Windows, macOS, Linux).
#### 1.4 - The program shall run locally without an internet connection (though optional online features may be added).
#### 1.5 - The program shall handle different types of links at different level depths.
### 2. File and Metadata Handling
#### 2.1 - The program shall scan and analyze the following artifact types:
    - Code: Git commits, repositories, languages used, version history, branch information
    - Docs: Word, PDFs, markdown, notes, excel sheets, presentations
    - Media: images, design sketches, video files, audio files
    - Archives: ZIP, RAR, TAR files with nested content analysis
#### 2.2 - The program shall read metadata from files, including:
    - File name, type, size, timestamps (creation, modified, last accessed)
    - Contribution details (e.g., Git commit frequency, authorship)
    - Document properties (title, word count, page count, custom properties)
#### 2.3 - The program shall allow the user to exclude sensitive file types or domains (with warnings when selecting risky sources).
#### 2.4 - The program shall avoid scanning common folders known to contain sensitive information such as 
    - Folders known to contain SSH keys
    - all files with a .env extension
    - all operating system files and program files
### 3. Analysis and Insights
#### 3.1 - The program shall analyze scanned results to compute:
    - Number of projects and project types
    - Timeline of work/project evolution
    - Lines of code, languages used, README.md files from project folders
    - Document word counts
    - Media/design file usage frequency
    - Insights into contributions for version controlled projects
#### 3.2 - The program shall group files into potential projects and allow users to:
    - Mark files as belonging to a project
    - Mark ambiguous files for further analysis
### 4. User Interface
#### 4.1 - The program shall have a graphical user interface (GUI) for general users.
#### 4.2 - The program shall also be executable from the command line for advanced users.
#### 4.3 - The GUI shall include:
    - Scan progress visualization (with time estimate,discovered/ignored/excluded/minable files)
    - Post-scan dashboard showing:
        - Number of files/projects scanned
        - Timeline of projects and productivity
        - Skills worked on and improvements
        - Highlights (big projects, top repos, longest docs, most collaborators, etc.)
    - Ability to open folders containing chosen projects directly.
    - Error reporting with probable causes when scans fail.
### 5. Reporting and Export
#### 5.1 - The program shall store results from previous scans.
#### 5.2 - The program shall allow export of insights in common formats:
    - CSV
    - JSON
    - PDF
    - Markdown
#### 5.3 - The program shall allow customization and preview before exporting.
### 6. Usability and Enhancements
#### 6.1 - The program shall maintain user settings between sessions.
#### 6.2 - The program shall allow timespan filtering (scan only files created/modified within a set period).
#### 6.3 - The program shall present insights in both visual (charts, graphs) and statistical (numeric summaries) formats.
### 7. Optional / Bonus Features
#### 7.1 - AI chatbot assistant for interacting with summaries and answering user questions about their projects.
#### 7.2 - Entertainment features during scans (e.g., mini game or music playback).
#### 7.3 - IDE/extension integration (e.g., GitHub, VSCode) for real-time updates.