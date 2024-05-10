# lysimeter-data-2023
 This is a private repository made to improve the data processing of Arkansas Valley Research Center lysimeter raw data and subsequent analysis.

 Created by:<br/>
 A.J. Brown<br/>
 Agricultural Data Scientist<br/>
 Colorado State Univeristy<br/>
 Ansley.Brown@colostate.edu <br/>
 5 April 2024

 Please note that the data are NOT found in this repository, and only the code, which will not inform users of any data insights as a standalone.

 To view the data, you must have it yourself already or recieve it with special permission from Colorado State University.  Please contact me if you have a data request.

## Proposed Workflow
**Objective 1: Process 2023 data**
- AJ develop code using 2022 data where non-standard days are known, verifying that it works
- AJ apply verified code on 2023 data
- Check it against what Jeff has done so far in 2023 to validate
- If 2023 checks well, run it on remaining 2023 data that Jeff hasn't verified yet due to time constraints
- 2023 data is processed

**Objective 2: Automate the process**
- Take code and make it automated
- Idea 1: 
    - make an .exe file that identifies and merges all .dat files in the .exe file location and exports as a csv with datetime in file name
Use windows to schedule that .exe to run at a given period (e.g., 12 hours)

## Data Flow
**Currently**
1. Raw data files are collected from the lysimeter
2. Raw data are manually merged into single excel file
3. Data are put as raw into a data processing spreadsheet where values can be calculated
4. Non-standard days are identified and flagged manually upon visual inspection

**Proposed**
1. Raw data files are collected from the lysimeter
2. Python code merges and processes the data:
    - Finds all .dat files in the folder and merges them, then exports that as .csv with datetime for user reference
    - uses dataframe created after merge to create calculated value columns as previously done in the excel spreadsheet
    - uses given criteria to identify non-standard days and flag them
    - exports the processed data as a .csv with datetime in file name, dropping the non-standard days from the dataset
    - (optional goal) create and save graphs currently generated in the spreadsheet as .png files for user QAQC