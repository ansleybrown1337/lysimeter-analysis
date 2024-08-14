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
python scripts/run_analysis.py <data_directory> <output_directory> <calibration_file> <timescale>
```

Example for test, SL, and LL data:

*for test data:*
```
python scripts/run_analysis.py C:\Users\AJ-CPU\Documents\GitHub\lysimeter-data-2023\private_test_data C:\Users\AJ-CPU\Documents\GitHub\lysimeter-data-2023\private_test_output C:\Users\AJ-CPU\Documents\GitHub\lysimeter-data-2023\code\coefficients.csv Min15
```

*for SL data:*
```
python scripts/run_analysis.py C:\Users\AJ-CPU\Documents\GitHub\lysimeter-data-2023\private_SL_data C:\Users\AJ-CPU\Documents\GitHub\lysimeter-data-2023\private_SL_output C:\Users\AJ-CPU\Documents\GitHub\lysimeter-data-2023\code\SL_coefficients.csv Min15
```

*for LL data:*
```
python scripts/run_analysis.py C:\Users\AJ-CPU\Documents\GitHub\lysimeter-data-2023\private_LL_data C:\Users\AJ-CPU\Documents\GitHub\lysimeter-data-2023\private_LL_output C:\Users\AJ-CPU\Documents\GitHub\lysimeter-data-2023\code\LL_coefficients.csv Min15
```

This should execute the analysis, process the data, detect non-standard events (NSEs), and save the results in the specified output directory. 

Additionally, it will save the time series plots with NSEs highlighted as a static image **and** an interactive plotly graph in the output directory.  The interactive plotly graph will be saved as an html file in the output directory, **and is far easier to use for data exploration than the static image.**