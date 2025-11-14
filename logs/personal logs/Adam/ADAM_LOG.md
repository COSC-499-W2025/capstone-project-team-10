# Week 11 (11/9/2025 - 11/16/2025) -> Reading Week
## Completed tasks
#### In Review will be moved to completed after team review. I am writing this log ahead of time
![Week 11 Tasks completed](Week11/image-1.png)
## Features

![Week 11 Tasks In-progress](Week11/image.png)
## Recap

#### PR: https://github.com/COSC-499-W2025/capstone-project-team-10/pull/96

- Created Functions for printing harvested file context
- Created Functions for creating a PDF with possible resume entries for a scan log
- Created Functions for creating a ZIP file containing a web portfolio for a scan log
- Created Param for default output location in the users Downloads folder. This is not a persistent param but is modifiable if the GUI would like to add the functionality
- Updated Readme with documentation for how to use the showcase module

### Planned Future Expansion Opportunities:
- Make more specific file type parsing to create more unique sections.
- Possible parsing of Photoshop files to produce an image to be included
- Split .git file extra data to be parsed more deeply, outlining outputs in a much cleaner way (The git parse is currently being rewritten)


### For next week:

For the next few weeks I will be coordinating our full implementation and tying together all the teams work into a final presentation as well as doing manual integration testing. I am trying to coordinate rewrites in the file analysis modules as lots of them dont produce very usable outputs, especially the .git analysis. I may be doing this rewrite myself if the team requires help. 

My Primary task will be the consolidation of the CLI and related modules

#### Tickets
- https://github.com/COSC-499-W2025/capstone-project-team-10/issues/97


## Additional Context

No problems with my work, however attempting to direct the team in the right direction is difficult and consumes most of my time. 

## Team Survey:

Team survey completed.

# Week 10 (11/2/2025 - 11/9/2025)

![Week 10 Tasks completed](Week10/image-1.png)

## Features

![Week 10 Tasks In-progress](Week10/image.png)

## Recap

I spent most of my week implementing the parameter functionality for our different modules to use. This module will manage the parameters being passed to different modules and ensure that they are persistent and globally available.

- Created param module
- Created param parsing for new parameters
- Created tests for param module
- Updated Readme with Param usage guide
- Created param_defaults.json with default parameter values to be loaded at runtime, or as a backup when user parameters are corrupted/missing

I also updated the CLI to be able to accept these parameters from the user in multi part parameters.

- Created tests for cli param parsing
- Updated Readme with new CLI flags

PR: https://github.com/COSC-499-W2025/capstone-project-team-10/pull/85

For the next week I will be working on the Portfolio and Resume exports for scan results

## Additional Context

The Team is working great together, the next phase of our project is the itegration of all our features into our commandline interface, as doing robust manual testing to iron out how we can improve product usability and functionality. as well as implementing the Resume and web portfolio exports

## Team Survey:

Team survey completed.

# Week 9 (10/26/2025 - 11/2/2025)

![Week 9 Tasks completed](Week9/image-1.png)

## Features

![Week 9 Tasks In-progress](Week9/image.png)

## Recap

I spent most of my week implementing the logging functionality for our File analysis to write to. This module manages the log files being written to and handling for log management.

The desire for this module is that our File Export service and eventually our GUI can extract any key insights about projects and such from the resulting logs in order to display/export them for the user.

## Additional Context

No additional notes

## Team Survey:

Team survey completed.

# Week 8 (10/19/2025 - 10/26/2025)

![Week 8 Tasks completed](Week8/image-1.png)

## Features

![Week 8 Tasks In-progress](Week8/image.png)

## Recap

I Spent most of my week planning out github tickets and adding flags to the CLI for implemented features

In the next sprint I will primarily be tackling designing and implementing our log output for each file search, as well as various project planning activities and coordinating implementation/integration

## Additional Context

No additional notes

## Team Survey:

Team survey completed.

# Week 7 (10/12/2025 - 10/19/2025)

![Week 7 Tasks completed](Week7/image-1.png)

## Features

![Week 7 Tasks In-progress](Week7/image.png)

## Recap

I Spent most of my week outlining the path for our group forward, creating tickets, managing requirements, and developing draft test cases for developers to fill in as the features get fully developed, this allows us to have good expectations for what our inputs and outputs for our features should be, and the tests just require adaptation to the developers specific implementation. I also completed our teams WBS.

In the next sprint I will primarily be tackling project planning and documentation, as well as adding the flags and process to our CLI to allow for zip file processing.

## Additional Context

No additional notes

## Team Survey:

Team survey completed.

# Week 6 (10/05/2025 - 10/12/2025)

![Week 6 Tasks completed](Week6/image-1.png)

## Features

![Week 6 Tasks In-progress](Week6/image.png)

## Recap

I rewrote our application in Python minus the multithreading. Wrote the README with instructions for

- Running, Packaging, and Testing the Base app
  - Using PyQt5 for GUI
  - Using pyinstaller for build process
  - Using python unittest for testing framework
- Writing Tests
- Coding Conventions to be practiced
- Best Practices for submitting PRs
- Setting up python virtual environment,
- Writing unit tests, running the app, and building the app executable

In the next sprint I will primarily be tackling the drafting of test cases as well as reworking the testing library to use PyTest at the recommendation of our team member with lots of python experience

## Additional Context

## Team Survey:

![alt text](Week6/image-2.png)
![alt text](Week6/image-3.png)
![alt text](Week6/image-4.png)

# Week 5 (9/28/2025 - 10/05/2025)

![Week 5 Tasks completed](Week5/image-1.png)

## Features

![Week 5 Tasks In-progress](Week5/image.png)

## Recap

Group collaboration on Data Flow Diagram.
I began working on the framework for our multithreaded Rust application, Familiarizing myself with Rust's concurrency model and setting up the project structure according to our DFD.

Began Work on DFD, System Architecture Diagram, Project proposal, and Requirement Documents require updating, Requirements shall also be codified into github issues

## Additional Context

## Team Survey:

![alt text](Week5/image-2.png)
![alt text](Week5/image-3.png)
![alt text](Week5/image-4.png)

# Week 4 (9/21/2025 - 9/28/2025)

![Week 4 Tasks completed](Week4/image.png)

## Features

![Week 4 Tasks In-progress](Week4/image-1.png)

## Recap

Group collaboration on System Architecture diagram, and Project proposal with no individual tasks assigned. Completed documents and created starter code for Rust EGUI development. Beginning work on Data Flow Diagram

## Additional Context

## Team Survey:

![alt text](Week4/image-2.png)
![alt text](Week4/image-3.png)
![alt text](Week4/image-4.png)

# Week 3 (9/14/2025 - 9/21/2025)

![Week 3 Tasks](Week3/image-3.png)

## Features

![Week 3 Kanban](Week3/image-4.png)

## Recap

Group collaboration on project requirements with no individual tasks assigned. Completed requirements document and researched technology options (Rust, Python, Java, C/C#). Leaning toward Rust but waiting for final project requirements before committing.

https://github.com/COSC-499-W2025/capstone-project-team-10/pull/3

## Additional Context

## Team Survey:

![alt text](Week3/image.png)
![alt text](Week3/image-1.png)
![alt text](Week3/image-2.png)
