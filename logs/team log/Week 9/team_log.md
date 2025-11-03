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
- Week 9 was another active week for the group. As before, every member was assigned an equal share of tasks and resolved many issues directly related to the core functionality.
- The progress will continue in this manner, focusing on resolving remaining core functionality issues and completing more of the core features listed under Milestone 1.
- Regarding the test reports, we suspect that the test errors arise from our testing library (pytest) having trouble synchronizing with the src paths when run in a global environment. Specifically, it cannot recognize the src/ directory, where the main program functionality resides (see Initialization), but it can correctly execute many tests when run individually (see Runnable Tests section above). Therefore, a team meeting will be arranged for next week to:
  - __Update standardnization__ and
  - __Refactor the tests and the testing module__ to properly recognize paths.
(An issue will be added to the Kanban board to reflect this for the upcoming team meeting.)
