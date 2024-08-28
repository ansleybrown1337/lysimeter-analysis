# lysimeter_analysis/run_analysis.py
import argparse
import os
import sys
from colorama import Fore, Style, init
import lysimeter_analysis as ly

def run_analysis(
    data_directory,
    output_directory, 
    calibration_file, 
    input_timescale, 
    manual_nse_file_path=None, 
    frequency=None, 
    lysimeter_type=None, 
    custom_alpha=None, 
    custom_beta=None, 
    threshold=0.0034, 
    weather_file_path=None,
    planting_date='05-15-2022',
    harvest_date='10-15-2022',
    elevation=1274.064,
    latitude=38.0385
    ):
    
    # Load, merge, and calibrate data
    merger = ly.dat_file_merger.DatFileMerger()
    merger.set_data_directory(data_directory)
    merger.set_output_directory(output_directory)
    merger.set_calibration_file(calibration_file)
    merger.set_timescale(input_timescale)
    calibrated_df = merger.clean_and_calibrated_data()

    # Identify Non-Standard Events (NSE)
    nse_detector = ly.non_standard_events.NonStandardEvents()
    nse_detector.set_dataframe(calibrated_df)
    possible_columns = [
        'SM50_1_Avg', 'SM50_2_Avg',
        'SM25_1_Avg', 'SM25_2_Avg'
    ]
    nse_detector.set_possible_columns(possible_columns)
    nse_detector.set_output_directory(output_directory)
    nse_detector.set_threshold(threshold)

    ## Load and integrate manually defined NSEs if provided
    if manual_nse_file_path:
        nse_detector.load_manual_nse(manual_nse_file_path)
    
    ## Detect NSEs using the automatic method
    nse_df = nse_detector.detect_nse()
    
    ## Plot NSEs after integrating manual NSEs
    nse_detector.plot_nse()

    # Aggregate data if frequency is specified
    if frequency:
        nse_df = ly.utils.aggregate_data(nse_df, frequency, timestamp_col='TIMESTAMP', input_timescale=input_timescale)

    # Set up Load Cell Calibration
    calibration = ly.load_cell_calibration.LoadCellCalibration()

    if lysimeter_type:
        calibration.get_calibration_factor(lysimeter_type)
    else:
        calibration.get_calibration_factor()

    # Calculate Water Balance
    water_balance = ly.water_balance.WaterBalance()
    water_balance.set_dataframe(nse_df)
    water_balance.set_output_directory(output_directory)
    water_balance.set_custom_calibration_factor(calibration.calibration_factor)
    eta_df = water_balance.calculate_eta()
    water_balance.plot_eta_with_nse()
    water_balance.plot_cumulative_eta()

    # Compare ETa to ASCE PM ETr via local weather data (daily for now)
    if frequency == 'D' and weather_file_path:
        weather_etr = ly.weather.WeatherETR()
        weather_etr.set_latitude(latitude)
        weather_etr.set_elevation(elevation)
        weather_etr.set_output_directory(output_directory)
        weather_etr.load_data(weather_file_path)
        weather_etr.preprocess_data()
        weather_etr.calculate_daily_etr()

        # Merge ETr with ETa Data
        eta_df = eta_df.merge(weather_etr.df[['TIMESTAMP', 'ETr']], on='TIMESTAMP', how='left')

        # Calculate Kc
        weather_etr.df = eta_df  # Ensure the weather data object has the updated dataframe with ETa and ETr
        weather_etr.calculate_kc()

        # Update eta_df with the Kc values
        eta_df = weather_etr.df

        # Plot and save ETa vs ETr
        weather_etr.plot_etr_vs_eta()

        # Plot and save Kc with 2nd order polynomial fit
        weather_etr.set_planting_date(planting_date)
        weather_etr.set_harvest_date(harvest_date)
        weather_etr.plot_kc_with_fit()
    
    elif frequency != 'D' and weather_file_path:
        print(Fore.YELLOW + "Warning: Weather data comparison is skipped because the lysimeter data is not aggregated to a daily timescale." + Style.RESET_ALL)
    
    elif frequency == 'D' and not weather_file_path:
        print(Fore.YELLOW + "Warning: Weather data comparison is skipped because the weather data file path is not provided." + Style.RESET_ALL)

    # Generate and export the report
    report_generator = ly.report_generator.ReportGenerator()
    report_generator.add_file_info(merger.get_merged_files())
    report_generator.add_nse_summary(nse_detector.NSEcount, threshold=threshold)
    report_generator.add_timescale_info(input_timescale, frequency)
    report_generator.add_calibration_info(
        lysimeter_type=calibration.lysimeter_type,
        calibration_factor=calibration.calibration_factor,
        alpha=calibration.alpha,
        beta=calibration.beta
    )
    report_generator.add_ETa_Kc_info(planting_date, harvest_date)
    report_generator.export_report(output_directory)

    # Export the final dataframe including NSE columns, ETa, ETr, and Kc if applicable
    ly.utils.export_to_csv(eta_df, output_directory)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the lysimeter analysis.')

    parser.add_argument('--data_directory', type=str, required=True, help='The directory containing the lysimeter data files (.dat) to process.')
    parser.add_argument('--output_directory', type=str, required=True, help='The directory where the output files will be saved.')
    parser.add_argument('--calibration_file', type=str, required=True, help='The path to the calibration coefficients CSV file.')
    parser.add_argument('--input_timescale', type=str, required=True, help='The timescale of the input data (e.g., Min15).')
    parser.add_argument('--manual_nse_file_path', type=str, help='Path to the CSV file containing manually defined NSEs.', default=None)
    parser.add_argument('--frequency', type=str, help='The frequency to aggregate the data (e.g., H for hourly, D for daily).', default=None)
    parser.add_argument('--lysimeter_type', type=str, help='The type of lysimeter (SL or LL).', default=None)
    parser.add_argument('--custom_alpha', type=float, help='Custom alpha value for load cell calibration (kg/mV/V).', default=None)
    parser.add_argument('--custom_beta', type=float, help='Custom beta value for load cell calibration (surface area in m²).', default=None)
    parser.add_argument('--threshold', type=float, help='Threshold for detecting non-standard events (NSEs). Defaults to 0.0034.', default=0.0034)
    parser.add_argument('--weather_file_path', type=str, help='Path to the weather data file for ETr calculation.', default=None)
    parser.add_argument('--planting_date', type=str, help='The lysimeter crop planting date in the format MM-DD.', default=None)
    parser.add_argument('--harvest_date', type=str, help='The lysimeter crop harvest date in the format MM-DD.', default=None)
    parser.add_argument('--latitude', type=float, help='The latitude of the lysimeter site.', default=38.0385)
    parser.add_argument('--elevation', type=float, help='The elevation of the lysimeter site.', default=1274.064)

    args = parser.parse_args()

    run_analysis(
        data_directory=args.data_directory,
        output_directory=args.output_directory,
        calibration_file=args.calibration_file,
        input_timescale=args.input_timescale,
        frequency=args.frequency,
        lysimeter_type=args.lysimeter_type,
        custom_alpha=args.custom_alpha,
        custom_beta=args.custom_beta,
        threshold=args.threshold,
        weather_file_path=args.weather_file_path,
        manual_nse_file_path=args.manual_nse_file_path,
        planting_date=args.planting_date,
        harvest_date=args.harvest_date,
        latitude=args.latitude,
        elevation=args.elevation
    )
