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

# Add the 'code' directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now you can import your lysimeter_analysis package
from scripts.run_analysis import run_analysis

# Title
st.title("Lysimeter Data Analysis Tool")

# File uploads
st.markdown("## Upload the following files to run the analysis:")
data_directory = st.file_uploader("Upload Lysimeter Data Files", type=['dat'], accept_multiple_files=True)
calibration_file = st.file_uploader("Upload Lysimeter Weather Station Sensor Calibration File (Optional)", type=['csv'])
manual_nse_file = st.file_uploader("Upload Manual NSE File (Optional)", type=['csv'])
weather_file = st.file_uploader("Upload Weather Data File (Optional)", type=['dat', 'csv'])

# Output directory (not needed w/ download button)
output_directory = '.'
#output_directory = st.text_input("Output Directory", value=".")

# Configuration settings
st.markdown("## Lysimeter Data Configuration Settings:")
input_timescale = st.selectbox(
    "Input Timescale (i.e., keyword in input file name that needs to be present)",
    ["Min5", "Min15", "Min60", "Daily"]
    )
frequency = st.selectbox(
    "Data Aggregation Frequency (if any)",
    [None, "5T", "15T", "H", "D", "W"],
    index=1
    )
lysimeter_type = st.selectbox(
    "Lysimeter Type (if any)",
    [None, "SL", "LL"]
    )
threshold = st.number_input(
    "Non Standard Event (NSE) Detection Threshold (mV/V)",
    min_value=0.0001,
    max_value=1.0000,
    step=0.0001,
    value=0.0034
    )

## Load Cell Calibration Settings
st.markdown("## Custom Load Cell Calibration Settings:")
st.markdown('''
### Calibration Factor Equation

$$
\\text{Calibration Factor} = \\alpha \\left(\\frac{\\text{kg}}{\\text{mV/V}}\\right) \\times \\left(\\frac{1 \\, \\text{m}^3}{1000 \\, \\text{kg}}\\right) \\times \\left(\\frac{1}{\\beta \\, \\text{m}^2}\\right) \\times \\left(\\frac{1000 \\, \\text{mm}}{1 \\, \\text{m}}\\right)
$$

### Depth of Water Equation

$$
\\text{DoW (mm)} = \\left(\\frac{\\text{mV/V}}{1}\\right) \\times \\text{Calibration Factor}
$$
''')

custom_alpha = st.number_input(
    "Custom Alpha Value for Load Cell Calibration ($\\alpha$ in kg/mV/V)",
    min_value=1.00,
    max_value=10000.00,
    step=0.01,
    value=684.69
)
custom_beta = st.number_input(
    "Custom Beta Value for Load Cell Calibration (Surface Area $\\beta$ in m²)",
    min_value=0.01,
    max_value=1000.00,
    step=0.01,
    value=9.18
)

# ASCE-PM reference ET settings
st.markdown(
    '## ASCE-PM ETref Settings:',
    help='ETref is only calculated if data is at or aggregated to a daily value'
    )
latitude = st.number_input(
    "Latitude (decimal degrees)",
    step=0.0000,
    value=38.0385
    )
elevation = st.number_input(
    "Elevation (meters)",
    step=0.0000,
    value=1274.0640
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
    if data_directory and calibration_file and output_directory:
        # Save uploaded files to the output directory
        os.makedirs(output_directory, exist_ok=True)
        
        data_directory_path = os.path.join(output_directory, 'data_directory')
        os.makedirs(data_directory_path, exist_ok=True)
        
        for data_file in data_directory:
            with open(os.path.join(data_directory_path, data_file.name), 'wb') as f:
                f.write(data_file.getbuffer())

        calibration_file_path = os.path.join(output_directory, calibration_file.name)
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
        eta_df = run_analysis(
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
            planting_date=planting_date.strftime('%m-%d-%Y') if planting_date else None,
            harvest_date=harvest_date.strftime('%m-%d-%Y') if harvest_date else None,
            latitude=latitude,
            elevation=elevation
        )

        st.success("Analysis Completed!")
        st.download_button(
            label="Download Results",
            data=eta_df.to_csv().encode(),
            file_name="processed_lysimeter_data.csv",
            mime="text/csv"
        )
        # TODO: embed plotly charts here
        st.line_chart(
            eta_df,
            x="TIMESTAMP",
            y="SM50_1_Avg_ETa",
            xlabel="",
            ylabel="ETa (mm)"
        )
    else:
        st.error("Please upload all required files and specify the output directory.")
