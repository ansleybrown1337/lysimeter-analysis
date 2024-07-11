# scripts/run_analysis.py

import os
import sys
import pandas as pd
from colorama import Fore, Style, init
from lysimeter_analysis.dat_file_merger import DatFileMerger
from lysimeter_analysis.non_standard_events import NonStandardEvents

# Initialize colorama for Windows (allows colored print statements)
init()

def main(data_directory, output_directory, calibration_file):
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Create DatFileMerger instance
    merger = DatFileMerger(data_directory, output_directory, calibration_file)
    
    # Load and process data files
    merger.load_dat_files()
    merged_df = merger.merge_dataframes()

    # Calibrate data and handle any missing columns
    calibrated_df = merger.calibrate_data(merged_df)

    # Determine the columns to check for NSEs
    possible_columns = {
        'SM50_1_Avg': 'SM25_1_Avg',
        'SM50_2_Avg': 'SM25_2_Avg'
    }

    columns_to_check = []
    for old_col, new_col in possible_columns.items():
        if old_col in calibrated_df.columns:
            columns_to_check.append(old_col)
        elif new_col in calibrated_df.columns:
            columns_to_check.append(new_col)
    
    if not columns_to_check:
        print("Error: None of the expected columns for NSE detection were found.")
        return
    
    # Create NonStandardEvents instance
    nse_detector = NonStandardEvents(calibrated_df)
    
    # Detect NSEs
    # Define an appropriate difference threshold for detecting NSEs in mV/V units
    # 0.0004 came from a manually identified NSE on 3/6/2022 at 10:15AM
    threshold = 0.0004  
    nse_df = nse_detector.detect_nse(columns_to_check, threshold)

    # Summarize NSEs
    summary = nse_detector.summarize_nse()
    print(summary)

    # Plot NSEs
    nse_detector.plot_nse(columns_to_check, output_directory)

    # Export to CSV including NSE columns
    merger.export_to_csv(nse_df)

if __name__ == "__main__":
    data_directory = sys.argv[1]
    output_directory = sys.argv[2]
    calibration_file = sys.argv[3]
    main(data_directory, output_directory, calibration_file)
