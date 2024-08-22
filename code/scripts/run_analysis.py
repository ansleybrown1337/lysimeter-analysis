# lysimeter_analysis/run_analysis.py
import argparse
import os
import sys
from colorama import Fore, Style, init
from lysimeter_analysis.dat_file_merger import DatFileMerger
from lysimeter_analysis.non_standard_events import NonStandardEvents
from lysimeter_analysis.utils import export_to_csv, aggregate_data
from lysimeter_analysis.water_balance import WaterBalance
from lysimeter_analysis.report_generator import ReportGenerator
from lysimeter_analysis.load_cell_calibration import LoadCellCalibration

def main(data_directory, output_directory, calibration_file, input_timescale, frequency=None, lysimeter_type=None, custom_alpha=None, custom_beta=None):
    
    # Load, merge, and calibrate data
    merger = DatFileMerger()
    merger.set_data_directory(data_directory)
    merger.set_output_directory(output_directory)
    merger.set_calibration_file(calibration_file)
    merger.set_timescale(input_timescale)
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
    nse_detector.set_threshold(0.0034) # i.e., 0.01" of water, as per the tipping bucket rain gauge smallest measurable precip
    nse_df = nse_detector.run_nse_detection()

    # Aggregate data if frequency is specified
    if frequency:
        nse_df = aggregate_data(nse_df, frequency, timestamp_col='TIMESTAMP', input_timescale=input_timescale)

    # Set up Load Cell Calibration
    calibration = LoadCellCalibration()
    
    if lysimeter_type:
        calibration.get_calibration_factor(lysimeter_type)
    else:
        if custom_alpha is not None and custom_beta is not None:
            calibration.set_alpha(custom_alpha)
            calibration.set_beta(custom_beta)
        else:
            # If neither lysimeter type nor custom values are provided, warn and use default.
            # TODO: move this warning into the load_cell_calibration.py file instead of here.
            print(Fore.YELLOW + "Warning: No lysimeter type or custom alpha/beta values provided. Default values are being used. Please see the report for details." + Style.RESET_ALL)

    # Calculate Water Balance
    water_balance = WaterBalance()
    water_balance.set_dataframe(nse_df)
    water_balance.set_output_directory(output_directory)
    water_balance.set_custom_calibration_factor(calibration.calibration_factor)
    
    eta_df = water_balance.calculate_eta()

    # Generate and export the report
    report_generator = ReportGenerator()
    report_generator.add_file_info(merger.get_merged_files())
    report_generator.add_nse_summary(nse_detector.NSEcount)
    report_generator.add_timescale_info(input_timescale, frequency)
    report_generator.add_calibration_info(
        lysimeter_type=calibration.lysimeter_type,
        calibration_factor=calibration.calibration_factor,
        alpha=calibration.alpha,
        beta=calibration.beta
    )
    report_generator.export_report(output_directory)

    # Export the final dataframe including NSE columns and ETa
    export_to_csv(eta_df, output_directory)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the lysimeter analysis.')

    parser.add_argument('data_directory', type=str, help='The directory containing the lysimeter data files (.dat) to process.')
    parser.add_argument('output_directory', type=str, help='The directory where the output files will be saved.')
    parser.add_argument('calibration_file', type=str, help='The path to the calibration coefficients CSV file.')
    parser.add_argument('input_timescale', type=str, help='The timescale of the input data (e.g., Min15).')
    parser.add_argument('--frequency', type=str, help='The frequency to aggregate the data (e.g., H for hourly, D for daily).', default=None)
    parser.add_argument('--lysimeter_type', type=str, help='The type of lysimeter (SL or LL).', default=None)
    parser.add_argument('--custom_alpha', type=float, help='Custom alpha value for load cell calibration (kg/mV/V).', default=None)
    parser.add_argument('--custom_beta', type=float, help='Custom beta value for load cell calibration (surface area in m²).', default=None)

    args = parser.parse_args()

    main(
        data_directory=args.data_directory,
        output_directory=args.output_directory,
        calibration_file=args.calibration_file,
        input_timescale=args.input_timescale,
        frequency=args.frequency,
        lysimeter_type=args.lysimeter_type,
        custom_alpha=args.custom_alpha,
        custom_beta=args.custom_beta
    )
