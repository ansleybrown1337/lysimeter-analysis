# Summary:
This document shows users how to install and run the code in this repository.  The code will process the data, detect non-standard events (NSEs), and save the results in a specified output directory.  Additionally, it will save time series plots with NSEs highlighted.

To run online instead use the streamlit app: 

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://csu-lysimeter-analysis.streamlit.app/)


To run locally on your terminal, continue with the instructions below:

## Prepare Data
- require data: 
    - lsyimeteter raw load cell data in mV/V (.dat file)
- optional data:
    - CSV with manual non-standard events (NSEs) identified (see example)
    - local daily weather station data sufficient for calculating ASCE PM reference ET (.dat file).
    - CSV with calibration coefficients for environmental sensors found with lysimeter raw data

The data schema for each input file type can be found in its respective guide in this repository folder:
- [Lysimeter Data](./Lysimeter%20Input%20Data%20Formatting.md)
- [Weather Data](./Weather%20Input%20Data%20Formatting.md)
- [Manual NSE Data](./Manual%20NSE%20Event%20File%20Formatting.md)
- [Sensor Coefficients](./Sensor%20Coefficients%20Formatting.md)

## Navigate to Project Directory:
```
cd {insert file path here}
```

Example:
```
cd C:\Users\AJ-CPU\Documents\GitHub\lysimeter-analysis\code
```

## Install Package in Editable Mode:
> [!IMPORTANT]
> Don't forget the period at the end of the command!

```
pip install -e .
```

## Execute ```run_analysis.py``` Script

Here is the generic format for the command:
```bash
python scripts/run_analysis.py --data_directory <data_directory> --output_directory <output_directory> --calibration_file <calibration_file> --input_timescale <input_timescale> --frequency <aggregation_frequency> --lysimeter_type <lysimeter_type> --custom_alpha <custom_alpha> --custom_beta <custom_beta> --threshold <threshold_value>

```
Where:
*Required parameters:*
- **`--data_directory <data_directory>`**: The directory containing the data files to process.
- **`--output_directory <output_directory>`**: The directory where the output files will be saved.
- **`--input_timescale <input timescale>`**: The timescale to search for in the filenames 
    - Available Options: 'Min5', 'Min15', 'Min60', 'Daily'
    - You **must** have one of these text options in the input data file name
*Optional parameters:*
- **`[--calibration_file <calibration_file>]`**: The path to the calibration coefficients CSV file.
- **`[--manual_nse_file_path <manual_nse_file_path>]`**: (Optional) Path to a CSV file containing manually identified non-standard events (NSEs). The file should have columns 'Event Type', 'Start Datetime', 'Stop Datetime', and 'Notes' with the start and end times of the NSEs in the format 'MM/DD/YYY HH:MM:SS'. Please also ensure that the 'Event Type' column contains consistent naming conventions for the NSEs. For example, the CSU lysimeters in Rocky Ford, CO, U.S.A use 'Rain', 'Drain', 'Irrigation', 'Fertilizer', 'Unknown'
- **`[--frequency <aggregation_frequency>]`**: (Optional) The frequency to aggregate the data to.
    - Options: 'T' (minute), 'H' (hour), 'D' (day), 'W' (week), 'M' (month), 'Q' (quarter), 'A' (year)
    - Examples: '15T' - 15 minutes, '2H' - 2 hours, '3D' - 3 days
- **`[--lysimeter_type <lysimeter_type>]`**: (Optional) The type of lysimeter ('SL', 'LL', or 'custom'). Use this if you want to apply the default calibration for these lysimeters.
- **`[--custom_alpha <custom_alpha>]`**: (Optional) Custom alpha value for load cell calibration (kg/mV/V).
- **`[--custom_beta <custom_beta>]`**: (Optional) Custom beta value for load cell calibration (surface area in m²).
- **`[--threshold <threshold_value>]`**: (Optional) Threshold for detecting non-standard events (NSEs). Defaults to 0.0034 mV / V.
- **`[--weather_file_path <weather file path>]`**: (Optional) Path to the weather data file for ETr calculation using ASCE PM daily method ONLY.
- **`[--planting_date <planting_date>]`**: (Optional) Lysimeter crop planting date in the format 'MM-DD-YYYY'.
- **`[--harvest_date <harvest_date>]`**: (Optional) Lysimeter crop harvest date in the format 'MM-DD-YYYY'.

> [!NOTE]
> If you don't designate a lysimeter type, it will default to values used for the LL

### Example command for script execution using run_analysis.py:
Relative pathways can be used for easy copy/paste execution of the run_analysis.py script, and make the command more legible/understandable. Just make sure you're executing the command after ensuring that the current working directory is the root of the repository code (i.e., `lysimeter-analysis/code`).

Here is an example command for running the script with the provided example data:
```batch
python scripts\run_analysis.py ^
    --data_directory ..\public_data ^
    --output_directory ..\public_output ^
    --calibration_file ..\public_data\coefficients.csv ^
    --manual_nse_file_path ..\public_data\manual_nse_events.csv ^
    --input_timescale Min15 ^
    --frequency D ^
    --lysimeter_type LL ^
    --custom_alpha 684.694 ^
    --custom_beta 9.181 ^
    --threshold 0.0034 ^
    --weather_file_path ..\public_data\example_weather_data.dat
    --planting_date 05-15-2022 ^
    --harvest_date 10-15-2022 ^
    --latitude 38.0385 ^
    --elevation 1274.064
```
> [!TIP]
> The caret (`^`) symbol is used to break the command into multiple lines for readability, else you can just simply separate inputs use a space character instead. If you are using a Unix-based system, you can remove the caret and put the entire command on one line, or use a backslash (`\`) to break the command into multiple lines instead.

Copy/paste friendly version with spaces instead:
```batch
python scripts\run_analysis.py --data_directory ..\public_data --output_directory ..\public_output --calibration_file ..\public_data\coefficients.csv --manual_nse_file_path ..\public_data\manual_nse_events.csv --input_timescale Min15 --frequency D --lysimeter_type LL --custom_alpha 684.694 --custom_beta 9.181 --threshold 0.0034 --weather_file_path ..\public_data\example_weather_data.dat
```

This should execute the analysis, process the data, detect non-standard events (NSEs), and save the results in the specified output directory. 

Additionally, it will save the time series plots with NSEs highlighted as a static image **and** an interactive plotly graph in the output directory.  The interactive plotly graph will be saved as an html file in the output directory, **and is far easier to use for data exploration than the static image.**

<!--
For the private test data on AJ's computer:
```batch
python scripts\run_analysis.py --data_directory ..\private_test_data --output_directory ..\private_test_output --calibration_file ..\private_test_data\coefficients.csv --manual_nse_file_path ..\private_test_data\manual_nse_events.csv --input_timescale Min15 --frequency D --lysimeter_type LL --custom_alpha 684.694 --custom_beta 9.181 --threshold 0.0034 --weather_file_path ..\private_METS_data\METS_Daily_2022.dat --planting_date 05-15-2022 --harvest_date 10-15-2022 --latitude 38.0385 --elevation 1274.064
```
-->

## Review Results
After running the analysis, check the output directory for results, including visualizations and reports.