# Summary:
This document shows users how to install and run the code in this repository.  The code is designed to process lysimeter data from the Arkansas Valley Research Center in Rocky Ford, Colorado.  The code will process the data, detect non-standard events (NSEs), and save the results in a specified output directory.  Additionally, it will save time series plots with NSEs highlighted.

## Navigate to Project Directory:
```
cd {insert file path here}
```

Example:
```
cd C:\Users\AJ-CPU\Documents\GitHub\lysimeter-data-2023\code
```

## Install Package in Editable Mode:
> [!IMPORTANT]
> Don't forget the period at the end of the command!

```
pip install -e .
```

## Execute ```run_analysis.py``` Script

Here is the generic format for the command (notice that there are no line breaks, whereas the examples look like they have line breaks due to page size):
```python
python scripts/run_analysis.py <data_directory> <output_directory> <calibration_file> <input_timescale> [--frequency <aggregation_frequency>] [--lysimeter_type <lysimeter_type>] [--custom_alpha <custom_alpha>] [--custom_beta <custom_beta>] [--threshold <threshold_value>]

```
Where:
- **`<data_directory>`**: The directory containing the data files to process.
- **`<output_directory>`**: The directory where the output files will be saved.
- **`<calibration_file>`**: The path to the calibration coefficients CSV file.
- **`<input timescale>`**: The timescale to search for in the filenames (e.g., 'Min5', 'Min15', 'Min60').
- **`[--frequency <aggregation_frequency>]`**: (Optional) The frequency to aggregate the data to.
    - Options: 'T' (minute), 'H' (hour), 'D' (day), 'W' (week), 'M' (month), 'Q' (quarter), 'A' (year)
    - Examples: '15T' - 15 minutes, '2H' - 2 hours, '3D' - 3 days
- **`[--lysimeter_type <lysimeter_type>]`**: (Optional) The type of lysimeter ('SL', 'LL', or 'custom'). Use this if you want to apply the default calibration for these lysimeters.
- **`[--custom_alpha <custom_alpha>]`**: (Optional) Custom alpha value for load cell calibration (kg/mV/V).
- **`[--custom_beta <custom_beta>]`**: (Optional) Custom beta value for load cell calibration (surface area in m²).
- **`[--threshold <threshold_value>]`**: (Optional) Threshold for detecting non-standard events (NSEs). Defaults to 0.0034 mV / V.
- **`[--weather_file_path <weather file path>]`**: (Optional) Path to the weather data file for ETr calculation using ASCE PM daily method ONLY.

> [!NOTE]
> If you don't designate a lysimeter type, it will default to values used for the LL


Example for test, SL, and LL data:

*for test data:*
```
python scripts/run_analysis.py C:\Users\AJ-CPU\Documents\GitHub\lysimeter-data-2023\private_test_data C:\Users\AJ-CPU\Documents\GitHub\lysimeter-data-2023\private_test_output C:\Users\AJ-CPU\Documents\GitHub\lysimeter-data-2023\code\coefficients.csv Min15 --frequency D --lysimeter_type LL --custom_alpha 684.694 --custom_beta 9.181 --threshold 0.0034 --weather_file_path C:\Users\AJ-CPU\Documents\GitHub\lysimeter-data-2023\private_METS_data\METS_Daily_2022.dat
```

*for SL data:*
```
python scripts/run_analysis.py C:\Users\AJ-CPU\Documents\GitHub\lysimeter-data-2023\private_SL_data C:\Users\AJ-CPU\Documents\GitHub\lysimeter-data-2023\private_SL_output C:\Users\AJ-CPU\Documents\GitHub\lysimeter-data-2023\code\SL_coefficients.csv  Min15 --lysimeter_type SL
```

*for LL data:*
```
python scripts/run_analysis.py C:\Users\AJ-CPU\Documents\GitHub\lysimeter-data-2023\private_LL_data C:\Users\AJ-CPU\Documents\GitHub\lysimeter-data-2023\private_LL_output C:\Users\AJ-CPU\Documents\GitHub\lysimeter-data-2023\code\LL_coefficients.csv Min15 --lysimeter_type LL
```

This should execute the analysis, process the data, detect non-standard events (NSEs), and save the results in the specified output directory. 

Additionally, it will save the time series plots with NSEs highlighted as a static image **and** an interactive plotly graph in the output directory.  The interactive plotly graph will be saved as an html file in the output directory, **and is far easier to use for data exploration than the static image.**