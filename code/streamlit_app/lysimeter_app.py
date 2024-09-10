'''
Streamlit app for lysimeter data analysis.
Created by: A.J. Brown
Date: 30 Aug 2024

This script is a Streamlit app that allows users to upload lysimeter data files
and run the lysimeter data analysis tool. The app provides a user interface for
configuring the analysis settings and running the analysis.

Helpful streamlit coding notes:
- numbers need to have same consistent data type (e.g., 'float') in 
st.number_input
- st.button() returns a boolean value, so you can use it to trigger events
- st.file_uploader() returns a BytesIO object, which can be saved to a file
- st.date_input() returns a datetime object
- st.text_input() returns a string
- st.selectbox() returns a string
- st.markdown() can be used to display markdown text
- st.title() can be used to display a title
- st.write() can be used to display text
- st.write() can be used to display dataframes
- st.write() can be used to display plots

'''

import sys
import os
import streamlit as st
import plotly.io as pio


# Add the 'code' directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.run_analysis import run_analysis  # noqa: E402

# Title
st.title("Lysimeter Data Analysis Tool")

# Description
txt = (
    '''Created by A.J. Brown, '''
    '''[Ansley.Brown@colostate.edu](mailto:Ansley.Brown@colostate.edu)\n\n'''

    '''This app is designed to analyze weighing lysimeter data files and calculate '''
    '''crop ET. It can also calculate reference evapotranspiration using the ASCE-PM '''
    '''method and derive crop coefficients. The app is designed to be user-friendly '''
    '''and easy to use.\n\n'''

    '''To learn more, and download the open-source python module, visit the '''
    '''[GitHub repository.](https://github.com/ansleybrown1337/'''
    '''lysimeter-analysis)\n\n'''

    '''A video tutorial on the tool's use can also be found '''
    '''[here!](https://www.loom.com/share/9c793730e6914da0ae5b7aee1609f762?'''
    '''sid=bd3c035e-41d5-4796-b7a0-f3f1f78fb9df)\n\n'''

    '''Further help and data format documentation can be found '''
    '''[here!](https://github.com/ansleybrown1337/lysimeter-analysis/tree/main/'''
    '''documentation)'''
)
st.markdown(txt)

# Store file uploaders in session state if not already stored
if 'data_directory' not in st.session_state:
    st.session_state['data_directory'] = None
if 'manual_nse_file' not in st.session_state:
    st.session_state['manual_nse_file'] = None
if 'weather_file' not in st.session_state:
    st.session_state['weather_file'] = None
if 'calibration_file' not in st.session_state:
    st.session_state['calibration_file'] = None

# File uploads
st.markdown("## Upload the following files to run the analysis:")
uploaded_data_files = st.file_uploader(
    "Upload Lysimeter Data Files", type=['dat'], accept_multiple_files=True
)
manual_nse_file = st.file_uploader(
    "Upload Manual NSE File (Optional)", type=['csv']
)
weather_file = st.file_uploader(
    "Upload Weather Data File (Optional)", type=['dat', 'csv']
)
calibration_file = st.file_uploader(
    "Upload Calibration File (Optional)", type=['csv']
)

# Store the uploaded files in session state
if uploaded_data_files:
    st.session_state['data_directory'] = uploaded_data_files
if manual_nse_file:
    st.session_state['manual_nse_file'] = manual_nse_file
if weather_file:
    st.session_state['weather_file'] = weather_file
if calibration_file:
    st.session_state['calibration_file'] = calibration_file

# Clear session state on refresh or new upload
st.markdown("*Clear Data Cache: Press to Refresh before uploading new data*")
if st.button("Clear Uploaded Data"):
    st.session_state['data_directory'] = None
    st.session_state['manual_nse_file'] = None
    st.session_state['weather_file'] = None
    st.session_state['calibration_file'] = None
    st.success("Session state cleared!")

# Use the files from session state for processing
data_directory = st.session_state['data_directory']
manual_nse_file = st.session_state['manual_nse_file']
weather_file = st.session_state['weather_file']
calibration_file = st.session_state['calibration_file']

# Output directory (not needed w/ download button)
output_directory = '.'

# Configuration settings
st.markdown("## Lysimeter Data Configuration Settings:")

input_timescale = st.selectbox(
    "Input Timescale (i.e., keyword in input file name that needs to be present)",
    ["Min5", "Min15", "Min60", "Daily"],
    value="Min15"
)

frequency = st.selectbox(
    "Data Aggregation Frequency (if any)",
    [None, "5T", "15T", "H", "D", "W"],
    index=1,
    value=None
)

lysimeter_type = st.selectbox(
    "Lysimeter Type (if any)",
    [None, "SL", "LL"],
    value=None
)

threshold = st.number_input(
    "Non Standard Event (NSE) Detection Threshold (mV/V)",
    min_value=0.0001,
    max_value=1.0000,
    step=0.0001,
    value=0.0034,
    format="%.4f"
)


# Load Cell Calibration Settings (collapsible)
with st.expander("Custom Load Cell Calibration Settings (Optional)", expanded=False):
    st.markdown('''
    ### Calibration Factor Equation

    $$
    \\text{Calibration Factor} \\left(\\frac{\\text{mm}}{\\text{mV/V}}\\right) = 
    \\alpha \\left(\\frac{\\text{kg}}{\\text{mV/V}}\\right) \\times 
    \\left(\\frac{1 \\, \\text{m}^3}{1000 \\, \\text{kg}}\\right) \\times 
    \\left(\\frac{1}{\\beta \\, \\text{m}^2}\\right) \\times 
    \\left(\\frac{1000 \\, \\text{mm}}{1 \\, \\text{m}}\\right)
    $$

    ### Depth of Water Equation

    $$
    \\text{DoW (mm)} = 
    \\left(\\frac{\\text{mV/V}}{1}\\right) \\times 
    \\text{Calibration Factor} \\left(\\frac{\\text{mm}}{\\text{mV/V}}\\right)
    $$
    ''')

    custom_alpha = st.number_input(
        "Custom Alpha Value for Load Cell Calibration ($\\alpha$ in kg/mV/V)",
        min_value=1.00,
        max_value=10000.00,
        step=0.01,
        value=None
    )
    custom_beta = st.number_input(
        "Custom Beta Value for Load Cell Calibration (Surface Area $\\beta$ in m²)",
        min_value=0.01,
        max_value=1000.00,
        step=0.01,
        value=None
    )

# ASCE-PM reference ET settings (collapsible)
with st.expander("ASCE-PM ETref Settings (Optional)", expanded=False):
    st.markdown(
        '## ASCE-PM ETref Settings:',
        help='ETref is only calculated if data is at or aggregated to a daily value'
    )
    latitude = st.number_input(
        "Latitude (decimal degrees)",
        step=0.0000,
        value=38.0385,
        format="%.4f"
    )
    elevation = st.number_input(
        "Elevation (meters)",
        step=0.0000,
        value=1274.0640,
        format="%.4f"
    )

    # Date inputs for Kc graphing
    planting_date = st.date_input(
        "Lysimeter Crop Planting Date (YYYY/MM/DD)"
    )
    harvest_date = st.date_input(
        "Lysimeter Crop Harvest Date (YYYY/MM/DD)"
    )

# Run Analysis Button
if st.button("Run Analysis"):
    missing_files = []

    # Check if data directory is missing
    if not data_directory:
        missing_files.append("Lysimeter Data Files")

    if not output_directory:
        missing_files.append("Output Directory")

    if missing_files:
        for missing_file in missing_files:
            st.error(f"Missing required input: {missing_file}")
    else:
        # Proceed with the analysis if no files are missing
        os.makedirs(output_directory, exist_ok=True)
        
        data_directory_path = os.path.join(output_directory, 'data_directory')
        os.makedirs(data_directory_path, exist_ok=True)
        
        for data_file in data_directory:
            with open(os.path.join(data_directory_path, data_file.name), 'wb') as f:
                f.write(data_file.getbuffer())

        calibration_file_path = None
        if calibration_file:  # Check if calibration file is provided
            calibration_file_path = os.path.join(
                output_directory, calibration_file.name
            )
            with open(calibration_file_path, 'wb') as f:
                f.write(calibration_file.getbuffer())
        
        manual_nse_file_path = None
        if manual_nse_file:
            manual_nse_file_path = os.path.join(output_directory, manual_nse_file.name)
            with open(manual_nse_file_path, 'wb') as f:
                f.write(manual_nse_file.getbuffer())
        
        weather_file_path = None
        if weather_file:
            weather_file_path = os.path.join(output_directory, weather_file.name)
            with open(weather_file_path, 'wb') as f:
                f.write(weather_file.getbuffer())

        # Run the analysis
        try:
            eta_df, nse_fig, eta_fig, cumulative_eta_fig, etr_vs_eta_fig, \
            kc_with_fit_fig, report_str = run_analysis(
                data_directory=data_directory_path,
                output_directory=output_directory,
                calibration_file=calibration_file_path,
                input_timescale=input_timescale,
                manual_nse_file_path=manual_nse_file_path,
                frequency=frequency,
                lysimeter_type=lysimeter_type,
                custom_alpha=custom_alpha if custom_alpha else None,
                custom_beta=custom_beta if custom_beta else None,
                threshold=threshold,
                weather_file_path=weather_file_path,
                planting_date=(
                    planting_date.strftime('%m-%d-%Y') if planting_date else None
                ),
                harvest_date=(
                    harvest_date.strftime('%m-%d-%Y') if harvest_date else None
                ),
                latitude=latitude,
                elevation=elevation
            )

            st.success("Analysis Completed!")
            # (Rest of the code for displaying results and download buttons)
            st.download_button(
                label="Download Results",
                data=eta_df.to_csv().encode(),
                file_name="processed_lysimeter_data.csv",
                mime="text/csv"
            )

            st.download_button(
                label="Download Analysis Report",
                data=report_str.encode(),
                file_name="lysimeter_analysis_report.txt",
                mime="text/plain"
            )

            # Display the charts and add download buttons
            if nse_fig:
                st.plotly_chart(nse_fig, use_container_width=True)
                nse_fig_html = pio.to_html(nse_fig, full_html=False)
                st.download_button(
                    label="Download NSE Plot (HTML)",
                    data=nse_fig_html.encode(),
                    file_name="nse_plot.html",
                    mime="text/html"
                )

            if eta_fig:
                st.plotly_chart(eta_fig, use_container_width=True)
                eta_fig_html = pio.to_html(eta_fig, full_html=False)
                st.download_button(
                    label="Download ETa Plot (HTML)",
                    data=eta_fig_html.encode(),
                    file_name="eta_plot.html",
                    mime="text/html"
                )

            if cumulative_eta_fig:
                st.plotly_chart(cumulative_eta_fig, use_container_width=True)
                cumulative_eta_fig_html = pio.to_html(
                    cumulative_eta_fig, full_html=False
                )
                st.download_button(
                    label="Download Cumulative ETa Plot (HTML)",
                    data=cumulative_eta_fig_html.encode(),
                    file_name="cumulative_eta_plot.html",
                    mime="text/html"
                )

            if etr_vs_eta_fig:
                st.plotly_chart(etr_vs_eta_fig, use_container_width=True)
                etr_vs_eta_fig_html = pio.to_html(etr_vs_eta_fig, full_html=False)
                st.download_button(
                    label="Download ETa vs ETr Plot (HTML)",
                    data=etr_vs_eta_fig_html.encode(),
                    file_name="eta_vs_etr_plot.html",
                    mime="text/html"
                )

            if kc_with_fit_fig:
                st.plotly_chart(kc_with_fit_fig, use_container_width=True)
                kc_with_fit_fig_html = pio.to_html(kc_with_fit_fig, full_html=False)
                st.download_button(
                    label="Download Kc with Fit Plot (HTML)",
                    data=kc_with_fit_fig_html.encode(),
                    file_name="kc_with_fit_plot.html",
                    mime="text/html"
                )

        except Exception as e:
            st.error(f"An error occurred during analysis: {str(e)}")