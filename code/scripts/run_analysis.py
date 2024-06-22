# scripts/run_analysis.py

from lysimeter_analysis import DatFileMerger, NonStandardEvents
import os
from datetime import datetime

def main(data_directory, output_directory, calibration_file):
    # Step 1: Data Processing
    merger = DatFileMerger(data_directory, output_directory, calibration_file)
    
    merger.load_dat_files()
    merged_df = merger.merge_dataframes()
    calibrated_df = merger.calibrate_data(merged_df)
    merger.export_to_csv(calibrated_df)
    
    # Step 2: Non-Standard Event Detection
    nse_detector = NonStandardEvents(calibrated_df)
    
    # Detect NSEs in 'SM50_1_Avg' and 'SM50_2_Avg' with a specified threshold
    nse_df_1 = nse_detector.detect_nse('SM50_1_Avg', threshold=0.05)
    nse_df_2 = nse_detector.detect_nse('SM50_2_Avg', threshold=0.05)
    
    # Summarize NSEs
    summary_df_1 = nse_detector.summarize_nse()
    summary_df_2 = nse_detector.summarize_nse()
    
    # Print summaries
    print(summary_df_1)
    print(summary_df_2)
    
    # Plot NSEs and save the plots
    nse_detector.plot_nse('SM50_1_Avg', output_directory)
    nse_detector.plot_nse('SM50_2_Avg', output_directory)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run full lysimeter data analysis.")
    parser.add_argument("data_directory", type=str, help="Directory containing .dat files.")
    parser.add_argument("output_directory", type=str, help="Directory to save the output CSV file.")
    parser.add_argument("calibration_file", type=str, help="File path for the calibration coefficients CSV file.")
    args = parser.parse_args()
    
    main(args.data_directory, args.output_directory, args.calibration_file)
