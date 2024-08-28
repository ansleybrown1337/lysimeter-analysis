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
data_directory = st.file_uploader("Upload Lysimeter Data Files", type=['dat'], accept_multiple_files=True)
calibration_file = st.file_uploader("Upload Lysimeter Weather Station Calibration File (Optional)", type=['csv'])
manual_nse_file = st.file_uploader("Upload Manual NSE File (Optional)", type=['csv'])
weather_file = st.file_uploader("Upload Weather Data File (Optional)", type=['dat', 'csv'])

# Output directory
output_directory = st.text_input("Output Directory", value=".")

# Configuration settings
input_timescale = st.selectbox(
    "Input Timescale (i.e., keyword in input file name that needs to be present)",
    ["Min5", "Min15", "Min60", "Daily"]
    )
frequency = st.selectbox(
    "Aggregation Frequency",
    [None, "5T", "15T", "H", "D", "W"],
    index=1
    )
lysimeter_type = st.selectbox(
    "Lysimeter Type",
    [None, "SL", "LL"]
    )
## numbers need to have same consistent data type (e.g., 'float') 
custom_alpha = st.number_input(
    "Custom Alpha Value for Load Cell Calibration (kg/mV/V)",
    min_value=1.00,
    max_value=10000.00,
    step=0.01,
    value=684.69
    )
custom_beta = st.number_input(
    "Custom Beta Value for Load Cell Calibration (Surface Area in m²)",
    min_value=0.01,
    max_value=1000.00,
    step=0.01,
    value=9.18
    )
threshold = st.number_input(
    "NSE Detection Threshold",
    min_value=0.0001,
    max_value=1.0000,
    step=0.0001,
    value=0.0034
    )
latitude = st.number_input(
    "Latitude",
    step=0.0000,
    value=38.0385
    )
longitude = st.number_input(
    "Longitude",
    step=0.0000,
    value=1274.0640
    )

# Date inputs for planting and harvest dates
planting_date = st.date_input(
    "Planting Date"
    )
harvest_date = st.date_input(
    "Harvest Date"
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
        run_analysis(
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
            elevation=longitude  # assuming longitude was intended to be elevation
        )

        st.success("Analysis Completed! Check the output directory for results.")
    else:
        st.error("Please upload all required files and specify the output directory.")
