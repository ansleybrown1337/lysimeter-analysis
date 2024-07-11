# Summary:
This document shows users how to install and run the code in this repository.  The code is designed to process lysimeter data from the Arkansas Valley Research Center in Rocky Ford, Colorado.  The code will process the data, detect non-standard events (NSEs), and save the results in a specified output directory.  Additionally, it will save time series plots with NSEs highlighted.

Navigate to Project Directory:

```
cd C:\Users\AJ-CPU\Documents\GitHub\lysimeter-data-2023\code
```

Install Package in Editable Mode:
>![WARNING]
>Don't forget the period at the end of the command!

```
pip install -e .
```

Run Analysis Script (Example on AJ's Computer, adjust your file paths accordingly):

*for test data:*
```
python scripts/run_analysis.py C:\Users\AJ-CPU\Documents\GitHub\lysimeter-data-2023\private_test_data C:\Users\AJ-CPU\Documents\GitHub\lysimeter-data-2023\private_test_ouptut C:\Users\AJ-CPU\Documents\GitHub\lysimeter-data-2023\code\coefficients.csv
```

*for SL data:*
```
python scripts/run_analysis.py C:\Users\AJ-CPU\Documents\GitHub\lysimeter-data-2023\private_SL_data C:\Users\AJ-CPU\Documents\GitHub\lysimeter-data-2023\private_SL_ouptut C:\Users\AJ-CPU\Documents\GitHub\lysimeter-data-2023\code\SL_coefficients.csv
```

*for LL data:*
```
python scripts/run_analysis.py C:\Users\AJ-CPU\Documents\GitHub\lysimeter-data-2023\private_LL_data C:\Users\AJ-CPU\Documents\GitHub\lysimeter-data-2023\private_LL_ouptut C:\Users\AJ-CPU\Documents\GitHub\lysimeter-data-2023\code\LL_coefficients.csv
```

This should execute the analysis, process the data, detect non-standard events (NSEs), and save the results in the specified output directory. 

Additionally, it will save the time series plots with NSEs highlighted as a static image **and** an interactive plotly graph in the output directory.  The interactive plotly graph will be saved as an html file in the output directory, **and is far easier to use for data exploration than the static image.**