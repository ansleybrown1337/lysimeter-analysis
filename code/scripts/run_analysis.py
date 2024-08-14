import os
import sys
from lysimeter_analysis.dat_file_merger import DatFileMerger
from lysimeter_analysis.non_standard_events import NonStandardEvents
from lysimeter_analysis.utils import export_to_csv
from lysimeter_analysis.water_balance import WaterBalance
from lysimeter_analysis.report_generator import ReportGenerator
from lysimeter_analysis.load_cell_calibration import LoadCellCalibration

def main(data_directory, output_directory, calibration_file, timescale, lysimeter_type=None, custom_alpha=None, custom_beta=None):
    
    # Initialize ReportGenerator
    report_generator = ReportGenerator()
    
    # Load, merge, and calibrate data
    merger = DatFileMerger()
    merger.set_data_directory(data_directory)
    merger.set_output_directory(output_directory)
    merger.set_calibration_file(calibration_file)
    merger.set_timescale(timescale)
    calibrated_df = merger.clean_and_calibrated_data()

    # Add merged file information to the report
    report_generator.add_file_info(merger.get_merged_files())

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

    # Add NSE summary to the report
    nse_summary = nse_detector._summarize_nse()
    report_generator.add_nse_summary(nse_summary)

    # Set up Load Cell Calibration
    calibration = LoadCellCalibration()
    
    if lysimeter_type:
        if lysimeter_type not in ['SL', 'LL']:
            raise ValueError(f"Invalid lysimeter type: '{lysimeter_type}'. Valid options are 'SL' or 'LL'.")
        calibration_factor = calibration.get_calibration_factor(lysimeter_type)
        report_generator.add_parameter("Lysimeter Type", lysimeter_type)
    elif custom_alpha is not None and custom_beta is not None:
        calibration.set_alpha(custom_alpha)
        calibration.set_beta(custom_beta)
        calibration_factor = calibration.calculate_calibration_factor()
        report_generator.add_parameter("Custom Alpha", custom_alpha)
        report_generator.add_parameter("Custom Beta", custom_beta)
    else:
        raise ValueError("Either a valid lysimeter type or custom calibration parameters (alpha, beta) must be provided.")
    
    report_generator.add_calibration_info({
        'Calibration Factor': calibration_factor
    })

    # Calculate Water Balance
    water_balance = WaterBalance()
    water_balance.set_dataframe(nse_df)
    water_balance.set_output_directory(output_directory)
    water_balance.set_custom_calibration_factor(calibration_factor)
    
    eta_df = water_balance.calculate_eta()

    # Export the final dataframe including NSE columns and ETa
    export_to_csv(eta_df, output_directory)

    # Export the report to the output directory
    report_generator.export_report(output_directory)

if __name__ == "__main__":
    data_directory = sys.argv[1]
    output_directory = sys.argv[2]
    calibration_file = sys.argv[3]
    timescale = sys.argv[4]
    lysimeter_type = sys.argv[5] if len(sys.argv) > 5 else None
    custom_alpha = float(sys.argv[6]) if len(sys.argv) > 6 else None
    custom_beta = float(sys.argv[7]) if len(sys.argv) > 7 else None

    main(data_directory, output_directory, calibration_file, timescale, lysimeter_type, custom_alpha, custom_beta)
