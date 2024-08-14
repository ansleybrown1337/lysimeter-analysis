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
>![WARNING]
>Don't forget the period at the end of the command!

```
pip install -e .
```

## Execute ```run_analysis.py``` Script

Here is the generic format for the command (notice that there are no line breaks, whereas the examples look like they have line breaks due to page size):
```python
python scripts/run_analysis.py <data_directory> <output_directory> <calibration_file> <timescale> [lysimeter_type] [custom_alpha] [custom_beta]

```
Where:
- **`<data_directory>`**: The directory containing the data files to process.
- **`<output_directory>`**: The directory where the output files will be saved.
- **`<calibration_file>`**: The path to the calibration coefficients CSV file.
- **`<timescale>`**: The timescale to search for in the filenames (e.g., 'Min5', 'Min15', 'Min60').
- **`[lysimeter_type]`**: *(Optional)* The type of lysimeter ('SL' or 'LL' or 'custom'). Use this if you want to apply the default calibration for these lysimeters. 
- **`[custom_alpha]`**: *(Optional)* Custom alpha value for load cell calibration (kg/mV/V).
- **`[custom_beta]`**: *(Optional)* Custom beta value for load cell calibration (surface area in m²).

>![WARNING] 
>If you want to pass custom alpha/beta values, you have to type something in the `[lysimeter_type]` variable space (e.g., "custom") as a placeholder.

>![NOTE]
>If you don't designate a lysimeter type, it will default to values used for the LL


Example for test, SL, and LL data:

*for test data:*
```
python scripts/run_analysis.py C:\Users\AJ-CPU\Documents\GitHub\lysimeter-data-2023\private_SL_data C:\Users\AJ-CPU\Documents\GitHub\lysimeter-data-2023\private_SL_output C:\Users\AJ-CPU\Documents\GitHub\lysimeter-data-2023\code\SL_coefficients.csv Min15 custom 800 2.5
```

*for SL data:*
```
python scripts/run_analysis.py C:\Users\AJ-CPU\Documents\GitHub\lysimeter-data-2023\private_test_data C:\Users\AJ-CPU\Documents\GitHub\lysimeter-data-2023\private_test_output C:\Users\AJ-CPU\Documents\GitHub\lysimeter-data-2023\code\coefficients.csv Min15 SL
```

*for LL data:*
```
python scripts/run_analysis.py C:\Users\AJ-CPU\Documents\GitHub\lysimeter-data-2023\private_LL_data C:\Users\AJ-CPU\Documents\GitHub\lysimeter-data-2023\private_LL_output C:\Users\AJ-CPU\Documents\GitHub\lysimeter-data-2023\code\LL_coefficients.csv Min15 LL
```

This should execute the analysis, process the data, detect non-standard events (NSEs), and save the results in the specified output directory. 

Additionally, it will save the time series plots with NSEs highlighted as a static image **and** an interactive plotly graph in the output directory.  The interactive plotly graph will be saved as an html file in the output directory, **and is far easier to use for data exploration than the static image.**