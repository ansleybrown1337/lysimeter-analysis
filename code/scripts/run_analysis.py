import os
import sys
from colorama import Fore, Style, init
from lysimeter_analysis.dat_file_merger import DatFileMerger
from lysimeter_analysis.non_standard_events import NonStandardEvents
from lysimeter_analysis.utils import export_to_csv
from lysimeter_analysis.water_balance import WaterBalance
from lysimeter_analysis.report_generator import ReportGenerator
from lysimeter_analysis.load_cell_calibration import LoadCellCalibration

def main(data_directory, output_directory, calibration_file, timescale, lysimeter_type=None, custom_alpha=None, custom_beta=None):
    
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
    nse_detector.set_threshold(0.0034)
    nse_df = nse_detector.run_nse_detection()

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
    data_directory = sys.argv[1]
    output_directory = sys.argv[2]
    calibration_file = sys.argv[3]
    timescale = sys.argv[4]
    lysimeter_type = sys.argv[5] if len(sys.argv) > 5 and sys.argv[5] in ['SL', 'LL'] else None
    custom_alpha = float(sys.argv[6]) if len(sys.argv) > 6 else None
    custom_beta = float(sys.argv[7]) if len(sys.argv) > 7 else None

    main(data_directory, output_directory, calibration_file, timescale, lysimeter_type, custom_alpha, custom_beta)
