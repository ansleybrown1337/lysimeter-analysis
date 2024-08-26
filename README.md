# lysimeter-data-2023
 This is a private repository made to improve the data processing of Arkansas Valley Research Center lysimeter raw data and subsequent analysis.

 Created by:<br/>
 A.J. Brown<br/>
 Agricultural Data Scientist<br/>
 Colorado State Univeristy<br/>
 Ansley.Brown@colostate.edu <br/>
 5 April 2024

 ![Lysimeter](figs/lysimeter.PNG)

 > [!NOTE]
 > Please note that the data are NOT found in this repository, and only the code, which will not inform users of any data insights as a standalone. To view the data, you must have it yourself already or recieve it with special permission from Colorado State University.  Please contact me if you have a data request.


## Proposed Workflow
```mermaid
graph TD
    %% Define subgraph for data collection
    subgraph 1[Data Collection]
    lysimeter[Raw Data from Lysimeter]
    weather[Weather Data from METS]
    nse[Manual Non-Standard Events]
    end

    %% Define subgraph for utils.py
    subgraph 2[utils.py]
    2A[export_csv]
    2B[AWAT Filter]
    end

    %% Define subgraph for dat_file_merger.py
    subgraph A[dat_file_merger.py]
    A1[Load Data]
    A2[Clean Data]
    A3[Calibrate Data]
    end

    %% Define subgraph for non_standard_events.py
    subgraph B[non_standard_events.py]
    B1[Detect NSEs]
    B2[Plot NSEs]
    end

    %% Define subgraph for load_cell_calibration.py
    subgraph C[load_cell_calibration.py]
    C1[Set Calibration Parameters]
    end

    %% Define subgraph for water_balance.py
    subgraph D[water_balance.py]
    D1[Calculate ETa]
    D2[Interpolate ETa]
    D3[Calculate Cumulative ETa]
    D4[Plot ETa with NSEs]
    D5[Plot Cumulative ETa]
    end

    %% Define subgraph for report_generator.py
    subgraph E[report_generator.py]
    E1[Create Analysis Report]
    end

    %% Define the flow between the functions
    lysimeter --> A1
    weather --> A1
    nse --> B1
    A1 --> A2 --> A3 --> B1 --> C1 --> D1 --> D2 --> D3
    D3 --> D4 
    D3 --> D5

    %% Final export of results
    B2 --> F[Export Results]
    E1 --> F[Export Results]
    D3 --> F[Export Results]
    D4 --> F[Export Results]
    D5 --> F[Export Results]

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
- ~~Calculate ETc for NSE events~~
    - Option 1 (selected): linearly interpolate between ET values at start and end of NSE events
    - Option 2 (for later invesitgation): Use PyFAO56 (or code my own?) to estimate ASCE PM ETc for all NSE flagged rows from METS weather data
- ~~Change everything to use 5min data instead of 15min data, or at least give the user an option.  Note: METS only has 5 and 60 min data~~
- ~~Create a report generator that reports NSE detection, ETc calibration parameters, load cell calibration parameters, and any other warnings or errors worth noting~~
- ~~Import weather data, calculate reference ETr, and compare to lysimeter ETc so that a crop coefficient is calculated (Kc = ETc / ETr), then fit a polynomial curve to the Kc values for a seasonal trend.~~
- ~~create a function in utils.py that allows users to aggregate data to a different time interval (e.g., 5min to 15min to 1hr to daily etc.) and output results in that selected interval.~~
    - ~~create error if user selects timestep that is smaller than input data timestep~~
- Add simulated data to put in github repo for public use, and make readme more public friendly
- ~~Add weather data script that calculates reference ETr and Kc values~~
    - ~~Double check that pyfao56 is working correctly~~
    - ~~manually calculate dewpoint for asce pm equation~~
- ~~add ETa and ETc comparison plots as output~~
- ~~add Kc timeseries plot as output~~
    - ~~fit with polynomial curve~~
- refine NSE detection algorithm to be more accurate
    - use AWAT filter to smooth smaller NSE events due to wind and other noise that aren't explicity irrigations, rains, etc.
- remove cumulative lines on Kc and instantaneous ET plots
- Add weather data info to report generator
- Perform analysis for 2022 data and compare to Lane's analysis results!
- ~~Add manual NSE detection to report generator~~
- Make NSE dots colored by NSE Type, and HoverTool to show NSE Type in plotly


## References
 - Thorp, K. R., DeJonge, K. C., Pokoski, T., Gulati, D., Kukal, M., Farag, F., Hashem, A., Erismann, G., Baumgartner, T., Holzkaemper, A., 2024. Version 1.3.0 - pyfao56: FAO-56 evapotranspiration in Python. SoftwareX. In review.