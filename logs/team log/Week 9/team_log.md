# Sprint for 10/26/25 -> 11/02/25
## Milestone Goals

Completed:
- https://github.com/COSC-499-W2025/capstone-project-team-10/issues/69 - Implement time-span filtering for the FSS
- https://github.com/COSC-499-W2025/capstone-project-team-10/issues/64 - Create Module for analysis of image formats
- https://github.com/COSC-499-W2025/capstone-project-team-10/issues/59 - Create Module for analysis of Microsoft Word files
- https://github.com/COSC-499-W2025/capstone-project-team-10/issues/58 - Create Module for analysis of Microsoft Excel files
- https://github.com/COSC-499-W2025/capstone-project-team-10/issues/51 - Create analysis module to identify programming files and extract frameworks/libraries
- https://github.com/COSC-499-W2025/capstone-project-team-10/issues/48 - Create Module to manage the storage of log output

## Burnup Chart
![Burn up](screenshots/burn_up_w9.png)

## Completed Tasks
![Completed](screenshots/done_w9.png)

## In-Progress
![In-Progress](screenshots/in_progress_w9.png)
> Note that these are tasks that are being moved to development right before this Team Log screenshot

## Test Report
<details>
  <summary>Initialization</summary>
    <img width="1842" height="211" alt="test_report_1_w9" src="https://github.com/user-attachments/assets/229f5f30-c034-4e06-8361-a1ab32813cd6" />
    <img width="1840" height="404" alt="test_report_2_w9" src="https://github.com/user-attachments/assets/b937a641-7378-4529-a718-7e93b2a27d28" />
</details>

<details>
  <summary>Runnable tests</summary>
    <img width="1433" height="331" alt="test_report_3_w9" src="https://github.com/user-attachments/assets/661905d2-567b-4848-a2bf-e49400962a30" />
    <img width="1434" height="457" alt="test_report_4_w9" src="https://github.com/user-attachments/assets/a40a00bd-f138-4be5-8afd-d40b4efb32f7" />
    <img width="1434" height="357" alt="test_report_5_w9" src="https://github.com/user-attachments/assets/8d1723c2-052e-41a1-a1db-cfa6e7a43f30" />

</details>

## Reflection / Additional Context
- Week 9 is another active week for the group members - as before, every member was assigned equally of tasks, and pluck away alot of issues directly related to core functionality.
- The progress will continue to be so, focusing on pluck away from the core functionalities, filling out more of the core functionality that is listed with Milestone 1.
- Now, to address test reports - we suspect that the test errors arises from the fact that our testing library (pytest) is having troubles synchronizing between src paths, when being ran in a global environment (as it can't recognize src/ where the main program functionality lies - refer to Initialization) but it can correctly executes many of the tests if ran individually (also refer to Runnable Tests section above) - therefore, a team meeting will be arranged for next week in order to:
  - __Update standardnization__ and
  - __Refactor the tests and the testing module__ to properly recognize paths (an issue will be added within the Kanban to reflect this within the team meetings)
