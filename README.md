# lysimeter-data-2023
 This is a private repository made to improve the data processing of Arkansas Valley Research Center lysimeter raw data and subsequent analysis.

 Created by:<br/>
 A.J. Brown<br/>
 Agricultural Data Scientist<br/>
 Colorado State Univeristy<br/>
 Ansley.Brown@colostate.edu <br/>
 5 April 2024

 ![Lysimeter](figs/lysimeter.png)

 > [!NOTE]
 > Please note that the data are NOT found in this repository, and only the code, which will not inform users of any data insights as a standalone. To view the data, you must have it yourself already or recieve it with special permission from Colorado State University.  Please contact me if you have a data request.


## Proposed Workflow
```mermaid
graph TD
    %% Main Workflow
    A[Start] --> B[dat_file_merger.py: Load Data]
    B --> C[dat_file_merger.py: Clean and Calibrate Data]
    C --> D[non_standard_events.py: Detect NSEs]
    D --> E[load_cell_calibration.py: Set Up Load Cell Calibration]
    E --> F[water_balance.py: Calculate ETa]
    F --> G[water_balance.py: Interpolate ETa for NSEs]
    G --> H[water_balance.py: Calculate Cumulative ETa]
    H --> I[report_generator.py: Generate and Export Reports]
    I --> J[water_balance.py: Plot ETa with NSEs Highlighted]
    I --> K[water_balance.py: Plot Cumulative ETa]
    K --> L[Export Results]
    J --> L
    L --> M[End]

    %% Additional Information Integrated
    B --> B1([Loads, merges, and calibrates data files]):::info
    C --> C1([Cleans data, identifies and removes outliers]):::info
    D --> D1([Detects Non-Standard Events NSEs to find anomalies]):::info
    E --> E1([Sets calibration parameters for load cells based on lysimeter type]):::info
    F --> F1([Calculates ETa using calibration factor and raw data]):::info
    G --> G1([Interpolates ETa values during NSE periods using neighboring values]):::info
    H --> H1([Generates cumulative ETa values over time]):::info
    I --> I1([Creates and exports reports with analysis and results]):::info
    J --> J1([Plots ETa timeseries with NSEs highlighted]):::info
    K --> K1([Plots cumulative ETa over the period of analysis]):::info

    %% Styles
    classDef info fill:#f0f0f0,stroke:#333,stroke-width:1px,font-size:12px;
    style A fill:#f9f,stroke:#333,stroke-width:2px;
    style M fill:#f9f,stroke:#333,stroke-width:2px;

```
**Objective 1: Process 2023 data**
- AJ develop code using 2022 data where non-standard days are known, verifying that it works
- AJ apply verified code on 2023 data
- Check it against what Jeff has done so far in 2023 to validate
- If 2023 checks well, run it on remaining 2023 data that Jeff hasn't verified yet due to time constraints
- 2023 data is processed

**Objective 2: Automate the process**
- Take code and make it automated
- Idea 1: Create an .exe
    - make an .exe file that identifies and merges all .dat files in the .exe file location and exports as a csv with datetime in file name
Use windows to schedule that .exe to run at a given period (e.g., 12 hours)
- Idea 2: Use google colab
    - create a google colab notebook that does the same thing as the .exe, but has GUI components for easier user interaction
    - also prevents users from needing to download any large files

## Data Flow
**Currently**
1. Raw data files are collected from the lysimeter
2. Raw data are manually merged into single excel file
3. Data are put as raw into a data processing spreadsheet where values can be calculated
4. Non-standard events (NSEs) are identified and flagged manually upon visual inspection
5. ASCE PM ETc is estimated at the start and end of each NSE, then interpolated between those datetimes via linear model

**Proposed**
1. Raw data files are collected from the lysimeter
2. Python code merges and processes the data:
    - Finds all .dat files in the folder and merges them, then exports that as .csv with datetime for user reference
    - uses dataframe created after merge to create calculated value columns as previously done in the excel spreadsheet
    - exports the processed data as a .csv with datetime in file name
3. Identify non-standard events (NSEs) and subsequent non-standard days (NSDs) automatically
    - using guidelines provided in the documentation folder from Lane Simmons
    - create a new column in the processed data that flags NSE's and NSD's
    - it appears that identifying NSE's is more optimal than NSD's (see Lane's description in the documentation folder), so the code will be written to identify NSE's and NSD's will be investigated later if needed.
    - create graphics for manual QAQC
4. Interpolate ETc for NSEs
    - Use [PyFAO56 module from USDA ARS](https://github.com/kthorp/pyfao56/tree/main) to estimate ASCE PM ETc for all NSE flagged rows OR
    - Create a linear model to estimate ETc for NSE's by estimating ETc at the start and end of each NSE, then interpolating between those datetimes
        - this method may be optimal when the lysimeter weather station is not able to be above canopy, as the ASCE PM equation requires
5. Use lysimeter weights and ETc estimates to create a water balance

## TODO
- refine NSE detection algorithm to be more accurate
- refine NSE detection algorithm to count NSE's and define whole events
- add new ET column for NSE's using METS data
    - Option 1: use ET data found within METS dataframe inherently
    - Option 2: Use PyFAO56 (or code my own?) to estimate ASCE PM ETc for all NSE flagged rows from METS weather data
- Change everything to use 5min data instead of 15min data, or at least give the user an option.  Note: METS on ly has 5 and 60 min data
- Create water balance using lysimeter weights and ETc estimates