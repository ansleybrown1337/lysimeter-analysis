# scripts/run_analysis.py

import os
import sys
from lysimeter_analysis.dat_file_merger import DatFileMerger
from lysimeter_analysis.non_standard_events import NonStandardEvents
from lysimeter_analysis.utils import export_to_csv

def main(data_directory, output_directory, calibration_file, timescale):
    # Create DatFileMerger instance and set attributes
    merger = DatFileMerger()
    merger.set_data_directory(data_directory)
    merger.set_output_directory(output_directory)
    merger.set_calibration_file(calibration_file)
    merger.set_timescale(timescale)
    
    # Load, merge, and calibrate data
    calibrated_df = merger.clean_and_calibrated_data()

    # Define possible columns for NSE detection
    possible_columns = [
        'SM50_1_Avg', 'SM50_2_Avg',
        'SM25_1_Avg', 'SM25_2_Avg'
    ]
    
    # Create NonStandardEvents instance and set attributes
    nse_detector = NonStandardEvents()
    nse_detector.set_dataframe(calibrated_df)
    nse_detector.set_possible_columns(possible_columns)
    nse_detector.set_output_directory(output_directory)
    
    # Run NSE detection
    nse_df = nse_detector.run_nse_detection()

    # Export to CSV including NSE columns
    export_to_csv(nse_df, output_directory)

if __name__ == "__main__":
    data_directory = sys.argv[1]
    output_directory = sys.argv[2]
    calibration_file = sys.argv[3]
    timescale = sys.argv[4]
    main(data_directory, output_directory, calibration_file, timescale)
