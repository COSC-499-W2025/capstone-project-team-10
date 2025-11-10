# Sprint for 11/03/25 -> 11/09/25


## Milestone Goals

Completed:
- https://github.com/COSC-499-W2025/capstone-project-team-10/issues/60 - Create module for analysis of .md files
- https://github.com/COSC-499-W2025/capstone-project-team-10/issues/62 - Create module for processing analysis results into projects (Grouping files by .git)
- https://github.com/COSC-499-W2025/capstone-project-team-10/issues/63 - Create module for analysis of Photoshops related files
- https://github.com/COSC-499-W2025/capstone-project-team-10/issues/39 - Create configuration system for storing and parsing user settings
- https://github.com/COSC-499-W2025/capstone-project-team-10/issues/84 - Create module for analysis of raw text blocks

## Burnup Chart
![Burn up](screenshots/burn_up_w10.png)

## Completed Tasks
![Completed](screenshots/done_w10.png)
<img width="982" height="149" alt="things" src="https://github.com/user-attachments/assets/7212f6fd-698c-41af-87ca-5a7eec7bbda1" />
> Below are the issues that were being in-review

## In-Progress
![In-Progress](screenshots/in_progress_w10.png)

## Test Report
<details>
  <summary>Initialization (less errored tests from before)</summary>
    <img width="1835" height="478" alt="test1" src="https://github.com/user-attachments/assets/dd81efde-7237-42c1-b93a-e801479ce670" />
</details>

<details>
  <summary>Compiler dependency</summary>
    <img width="726" height="688" alt="test2" src="https://github.com/user-attachments/assets/65dd7419-ac25-446f-a4f0-3e5bf1994c87" />
</details>

<details>
  <summary>Ghost files are being mentioned within the test suite - possible typo?</summary>
    <img width="379" height="337" alt="test3" src="https://github.com/user-attachments/assets/c4d0bfa5-480d-4131-833b-4f6f948d6990" />
</details>

## Reflection / Additional Context
- Week 10 successfully accomplished the tasks of knocking out file types analyzing - basically, FAS is readily to be "sew" together, into an actual master service.
- Bugs from tests are being culled, as stated. But, problems of appearing ghost files within the test suite (please refer to the screenshot) is being investigated - but different parts of everybody's PR are guaranteed to have ran, and pass succesfully, as before
- We will now proceed to works towards:
    - Stabilizing the repo, making the tests runnable and more compatible
    - Integrating the modules into an actual program
    - Shifting gears towards the "output" bulk of the program
- And we would have to update the .readme for more requirements (this time, the psd-tools needs another compiler)
