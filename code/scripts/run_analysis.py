# lysimeter_analysis/run_analysis.py
import argparse
from colorama import Fore, Style
from datetime import datetime
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
    """
    Run the lysimeter analysis process, which includes data merging, calibration,
    NSE detection, ETa calculation, water balance analysis, and optional comparison
    with weather data.

    Parameters:
    -----------
    data_directory : str
        The directory containing the lysimeter data files (.dat) to process.
    output_directory : str
        The directory where the output files will be saved.
    calibration_file : str
        The path to the calibration coefficients CSV file.
    input_timescale : str
        The timescale of the input data (e.g., Min15).
    manual_nse_file_path : str, optional
        Path to the CSV file containing manually defined NSEs (default is None).
    frequency : str, optional
        The frequency to aggregate the data (e.g., H for hourly, D for daily).
    lysimeter_type : str, optional
        The type of lysimeter (SL or LL). If not provided, defaults to using custom 
        values or LL.
    custom_alpha : float, optional
        Custom alpha value for load cell calibration (kg/mV/V) (default is None).
    custom_beta : float, optional
        Custom beta value for load cell calibration (surface area in m²) (default is 
        None).
    threshold : float, optional
        Threshold for detecting non-standard events (NSEs) (default is 0.0034).
    weather_file_path : str, optional
        Path to the weather data file for ETr calculation (default is None).
    planting_date : str, optional
        The lysimeter crop planting date in the format 'MM-DD-YYYY' (default is 
        '05-15-2022').
    harvest_date : str, optional
        The lysimeter crop harvest date in the format 'MM-DD-YYYY' (default is 
        '10-15-2022').
    elevation : float, optional
        The elevation of the lysimeter site in meters (default is 1274.064).
    latitude : float, optional
        The latitude of the lysimeter site in decimal degrees (default is 38.0385).

    Returns:
    --------
    eta_df : pd.DataFrame
        The final dataframe containing NSE columns, ETa, ETr, and Kc if applicable.
    nse_fig : plotly.graph_objects.Figure
        The Plotly figure object of NSE detection results.
    eta_fig : plotly.graph_objects.Figure
        The Plotly figure object of ETa timeseries with NSEs highlighted.
    cumulative_eta_fig : plotly.graph_objects.Figure
        The Plotly figure object of cumulative ETa over time.
    etr_vs_eta_fig : plotly.graph_objects.Figure or None
        The Plotly figure object of ETa vs ETr comparison, or None if not applicable.
    kc_with_fit_fig : plotly.graph_objects.Figure or None
        The Plotly figure object of Kc values with polynomial fit, or None if not 
        applicable.
    report_str : str
        The run report as a single string.

    Notes:
    ------
    This function orchestrates the entire lysimeter analysis process, including data 
    merging,
    NSE detection, ETa and water balance calculations, and optional weather data 
    comparison.
    It generates and saves relevant plots and returns them for further use.
    """
    # Start report timer
    report_generator = ly.report_generator.ReportGenerator()
    report_generator.start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Load, merge, and calibrate data
    merger = ly.dat_file_merger.DatFileMerger()
    merger.set_data_directory(data_directory)
    merger.set_output_directory(output_directory)
    if calibration_file:
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
    nse_fig = nse_detector.plot_nse()

    # Set up Load Cell Calibration
    calibration = ly.load_cell_calibration.LoadCellCalibration()

    # Check if custom alpha and beta values are provided
    custom_values_provided = custom_alpha is not None and custom_beta is not None

    # Set custom alpha and beta if provided, otherwise use the lysimeter type defaults
    if custom_values_provided:
        calibration.set_alpha(custom_alpha)
        calibration.set_beta(custom_beta)
    else:
        if lysimeter_type:
            calibration.get_calibration_factor(lysimeter_type)
        else:
            calibration.get_calibration_factor() # defaults to 'LL'


    # Calculate Water Balance
    water_balance = ly.water_balance.WaterBalance()
    water_balance.set_dataframe(nse_df)
    water_balance.set_output_directory(output_directory)
    water_balance.set_custom_calibration_factor(calibration.calibration_factor)
    eta_df = water_balance.calculate_eta()
    eta_fig = water_balance.plot_eta_with_nse()
    cumulative_eta_fig = water_balance.plot_cumulative_eta()

    # Aggregate data if frequency is specified
    if frequency:
        eta_df = ly.utils.aggregate_data(
            eta_df, 
            frequency, 
            timestamp_col='TIMESTAMP', 
            input_timescale=input_timescale
            )

    # Compare ETa to ASCE PM ETr via local weather data (daily for now)
    ## initialize figs to be None if weather data is not provided
    etr_vs_eta_fig = None
    kc_with_fit_fig = None
    if frequency == 'D' and weather_file_path:
        weather_etr = ly.weather.WeatherETR()
        weather_etr.set_latitude(latitude)
        weather_etr.set_elevation(elevation)
        weather_etr.set_output_directory(output_directory)
        weather_etr.load_data(weather_file_path)
        weather_etr.preprocess_data()
        weather_etr.calculate_daily_etr()

        # Merge ETr with ETa Data
        eta_df = eta_df.merge(weather_etr.df[['TIMESTAMP', 'ETr']], 
                              on='TIMESTAMP', 
                              how='left'
                              )

        
        # Ensure the weather data object has the updated dataframe with ETa and ETr
        weather_etr.df = eta_df

        # Calculate Kc values
        weather_etr.calculate_kc()

        # Update eta_df with the Kc values
        eta_df = weather_etr.df

        # Plot and save ETa vs ETr
        etr_vs_eta_fig = weather_etr.plot_etr_vs_eta()

        # Plot and save Kc with 2nd order polynomial fit
        weather_etr.set_planting_date(planting_date)
        weather_etr.set_harvest_date(harvest_date)
        kc_with_fit_fig = weather_etr.plot_kc_with_fit()
    
    elif frequency != 'D' and weather_file_path:
        print(
            Fore.YELLOW + 
            "Warning: Weather data comparison is skipped because the lysimeter data "
            "is not aggregated to a daily timescale." + 
            Style.RESET_ALL
        )

    elif frequency == 'D' and not weather_file_path:
        print(
            Fore.YELLOW + 
            "Warning: Weather data comparison is skipped because the weather data "
            "file path is not provided." + 
            Style.RESET_ALL
        )


    # Generate and export the report
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
    report_str = report_generator.merge_report()
    report_generator.export_report(output_directory)

    # Export the final dataframe including NSE columns, ETa, ETr, and Kc if applicable
    ly.utils.export_to_csv(eta_df, output_directory)

    return (
    eta_df, 
    nse_fig, 
    eta_fig, 
    cumulative_eta_fig, 
    etr_vs_eta_fig, 
    kc_with_fit_fig, 
    report_str
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the lysimeter analysis.')

    parser.add_argument(
        '--data_directory', type=str, required=True, 
        help='The directory containing the lysimeter data files (.dat) to process.'
    )
    parser.add_argument(
        '--output_directory', type=str, required=True, 
        help='The directory where the output files will be saved.'
    )
    parser.add_argument(
        '--calibration_file', type=str, 
        help='The path to the calibration coefficients CSV file.', default=None
    )
    parser.add_argument(
        '--input_timescale', type=str, required=True, 
        help='The timescale of the input data (e.g., Min15).'
    )
    parser.add_argument(
        '--manual_nse_file_path', type=str, 
        help='Path to the CSV file containing manually defined NSEs.', default=None
    )
    parser.add_argument(
        '--frequency', type=str, 
        help='The frequency to aggregate the data (e.g., H for hourly, D for daily).', 
        default=None
    )
    parser.add_argument(
        '--lysimeter_type', type=str, 
        help='The type of lysimeter (SL or LL).', default=None
    )
    parser.add_argument(
        '--custom_alpha', type=float, 
        help='Custom alpha value for load cell calibration (kg/mV/V).', default=None
    )
    parser.add_argument(
        '--custom_beta', type=float, 
        help='Custom beta value for load cell calibration (surface area in m²).', 
        default=None
    )
    parser.add_argument(
        '--threshold', type=float, 
        help='Threshold for detecting non-standard events (NSEs). Defaults to 0.0034.', 
        default=0.0034
    )
    parser.add_argument(
        '--weather_file_path', type=str, 
        help='Path to the weather data file for ETr calculation.', default=None
    )
    parser.add_argument(
        '--planting_date', type=str, 
        help='The lysimeter crop planting date in the format MM-DD.', default=None
    )
    parser.add_argument(
        '--harvest_date', type=str, 
        help='The lysimeter crop harvest date in the format MM-DD.', default=None
    )
    parser.add_argument(
        '--latitude', type=float, 
        help='The latitude of the lysimeter site.', default=38.0385
    )
    parser.add_argument(
        '--elevation', type=float, 
        help='The elevation of the lysimeter site.', default=1274.064
    )

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