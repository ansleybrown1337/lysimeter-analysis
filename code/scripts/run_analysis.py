# scripts/run_analysis.py

import os
import sys
from lysimeter_analysis.dat_file_merger import DatFileMerger
from lysimeter_analysis.non_standard_events import NonStandardEvents
from lysimeter_analysis.utils import export_to_csv
from lysimeter_analysis.water_balance import WaterBalance

def main(data_directory, output_directory, calibration_file, timescale):
    
    # Load, merge, and calibrate data
    merger = DatFileMerger()
    merger.set_data_directory(data_directory)
    merger.set_output_directory(output_directory)
    merger.set_calibration_file(calibration_file)
    merger.set_timescale(timescale)
    calibrated_df = merger.clean_and_calibrated_data()

    # Identify Non-Standard Events (NSE)
    nse_detector = NonStandardEvents()
    nse_detector.set_dataframe(calibrated_df)
    possible_columns = [
        'SM50_1_Avg', 'SM50_2_Avg',
        'SM25_1_Avg', 'SM25_2_Avg'
    ]
    nse_detector.set_possible_columns(possible_columns)
    nse_detector.set_output_directory(output_directory)
    nse_detector.set_threshold(0.0004)
    nse_df = nse_detector.run_nse_detection()

    # Calculate Water Balance
    water_balance = WaterBalance()
    water_balance.set_dataframe(nse_df)
    water_balance.set_output_directory(output_directory)
    
    # Set lysimeter type or custom calibration factor
    water_balance.set_lysimeter_type("SL")  # or use water_balance.set_custom_calibration_factor(157.43)
    
    eta_df = water_balance.calculate_eta()

    # Export the final dataframe including NSE columns and ETa
    export_to_csv(eta_df, output_directory)

if __name__ == "__main__":
    data_directory = sys.argv[1]
    output_directory = sys.argv[2]
    calibration_file = sys.argv[3]
    timescale = sys.argv[4]
    main(data_directory, output_directory, calibration_file, timescale)
