# Work Breakdown Structure (WBS)

# Mining Digital Work Artifacts Application

## 1.0 Project Management, Setup & Architecture

### 1.1 Project Planning & Environment Setup

#### 1.1.1 Finalize WBS and initial Gantt chart/schedule.

#### 1.1.2 Establish code repository (Git) and branching strategy.

#### 1.1.3 Define core system architecture (modules, data flow).

#### 1.1.4 Select technology stack (language, GUI framework, database).

## 2.0 Data Acquisition & Preprocessing (Scanning Engine)

This phase focuses on the core scanning logic, file system traversal, and data extraction.

### 2.1 Scan Scope & Exclusion Logic

#### 2.1.1 Develop user interface component for selecting scan scope (folders, disks, file types) (Req 1.1).

#### 2.1.2 Implement core logic for excluding sensitive folders (SSH keys, OS files) (Req 2.4).

#### 2.1.3 Implement logic for excluding specific file extensions (.env) (Req 2.4).

#### 2.1.4 Implement exclusion/inclusion list management for file types and domains (Req 2.3).

### 2.2 Scan Mode Implementation

#### 2.2.1 Implement All Files (thorough) scan mode (Req 1.2).

#### 2.2.2 Implement Quick Scan (lightweight/faster) mode (Req 1.2).

#### 2.2.3 Implement Custom Scan mode (user-specified paths/types) (Req 1.2).

#### 2.2.4 Implement Incremental Scan logic (change detection since last scan) (Req 1.2).

#### 2.2.5 Implement Timespan Filtering logic (creation/modification dates) (Req 6.2).

### 2.3 Artifact Parsing & Metadata Extraction

#### 2.3.1 Develop parsers for Code Artifacts (Git/repository analysis, commits, branches) (Req 2.1).

#### 2.3.2 Develop parsers for Document Artifacts (Word, PDF, Markdown, Excel, etc.) (Req 2.1).

#### 2.3.3 Develop parsers for Media Artifacts (images, video, audio) (Req 2.1).

#### 2.3.4 Develop parsers for Archive Artifacts (ZIP) (Req 2.1).

#### 2.3.5 Implement extraction of core file metadata (name, size, timestamps, type) (Req 2.2).

#### 2.3.6 Implement extraction of document properties (Req 2.2).

## 3.0 Data Analysis & Grouping

This phase focuses on transforming raw scanned data into meaningful metrics and insights.

### 3.1 Insight Computation

#### 3.1.1 Implement calculation for project metrics (number of projects, project types) (Req 3.1).

#### 3.1.2 Implement calculation for code metrics (LoC, language usage, README detection) (Req 3.1).

#### 3.1.3 Implement computation of work timeline/project evolution (Req 3.1).

#### 3.1.4 Implement analysis of contribution details (Git frequency, authorship) (Req 2.2, 3.1).

#### 3.1.5 Implement media/design file usage frequency analysis (Req 3.1).

#### 3.1.6 Implement calculation for document word counts (Req 3.1).

#### 3.2 Project Grouping & Management

#### 3.2.1 Develop algorithm for automatic project grouping based on file clusters (Req 3.2).

#### 3.2.2 Implement user interface to mark ambiguous files as belonging to a project (Req 3.2).

## 4.0 User Interfaces (GUI & CLI)

This phase delivers the interface components for user interaction and visualization.

### 4.1 Graphical User Interface (GUI)

#### 4.1.1 Develop the primary GUI framework and navigation (Req 4.1).

#### 4.1.2 Develop Scan Progress Visualization screen (time estimate, file counts) (Req 4.3).

#### 4.1.3 Develop Post-Scan Dashboard layout (Req 4.3).

#### 4.1.4 Implement Insight Visualization (charts, graphs, statistical summaries) (Req 6.3).

#### 4.1.5 Implement functionality to open project folders directly from the dashboard (Req 4.3).

#### 4.1.6 Implement Error Reporting UI (with probable causes) (Req 4.3).

#### 4.1.7 Implement user settings persistence module (Req 6.1).

### 4.2 Command Line Interface (CLI)

#### 4.2.1 Design and develop the CLI execution entry point (Req 4.2).

#### 4.2.2 Implement CLI flags for core functionality (scan mode, path, output format).

## 5.0 Reporting & Persistence

This phase handles the storage and export capabilities of the analyzed data.

### 5.1 Scan Result Storage

#### 5.1.1 Design the data schema for storing scan results (Req 5.1).

#### 5.1.2 Implement the persistent storage mechanism (.csv file) for previous scans (Req 5.1).

### 5.2 Export Engine

#### 5.2.1 Implement export function for CSV format (Req 5.2).

#### 5.2.2 Implement export function for JSON format (Req 5.2).

#### 5.2.3 Implement export function for PDF format (Req 5.2).

#### 5.2.4 Implement export function for Markdown format (Req 5.2).

#### 5.2.5 Develop Export Preview customization feature (Req 5.3).


## 6.0 Testing & Deployment

This phase ensures quality control and the final delivery of the executable application.


### 6.1 Quality Assurance

#### 6.1.1 Unit tests for all core scanning and analysis functions.

#### 6.1.2 Integration tests for GUI interaction and data flow.

#### 6.1.3 Performance tests for Quick vs. All Files scan modes.


## 7.0 Additional Features

These are features to be developed if time and resources allow, acting as stretch goals.

### 7.1 AI/Chatbot Assistant (Bonus)

#### 7.1.1 Research and design the AI assistant integration point (Req 7.1).

#### 7.1.2 Implement basic chat interface for interacting with summaries (Req 7.1).

### 7.2 Enhancement Features (Bonus)

#### 7.2.1 Implement scan entertainment features (mini-game/music playback) (Req 7.2).

#### 7.2.2 Develop basic IDE/Extension integration concept and proof-of-concept (Req 7.3).