# lysimeter_analysis/report_generator.py

import os
from datetime import datetime

class ReportGenerator:
    def __init__(self):
        self.report_lines = []
        self.start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def add_file_info(self, merged_files):
        self.report_lines.append("## Merged Files:")
        for file in merged_files:
            self.report_lines.append(f"- {file}")
        self.report_lines.append("")  # Add a blank line for spacing

    def add_nse_summary(self, nse_summary, threshold):
        self.report_lines.append("## NSE Summary:")
        self.report_lines.append(f"Threshold for NSE Detection: {threshold} mV/V")
        for column, count in nse_summary.items():
            self.report_lines.append(f"Load Cell Name: {column}:\nNSE count: {count}")
        self.report_lines.append("")  # Add a blank line for spacing

    def add_calibration_info(self, lysimeter_type, calibration_factor, alpha, beta):
        """
        Adds calibration information to the report.

        Args:
            lysimeter_type (str): The type of lysimeter (e.g., 'SL', 'LL', 'Custom').
            calibration_factor (float): The calibration factor in mm/mV/V.
            alpha (float): The alpha coefficient in kg/mV/V.
            beta (float): The beta coefficient in m².
        """
        self.report_lines.append("## Calibration Information:")
        self.report_lines.append(f"Lysimeter Type: {lysimeter_type}")
        self.report_lines.append(f"Calibration Factor: {calibration_factor} mm/mV/V")
        self.report_lines.append(f"Load Cell Conversion Coefficient (Alpha): {alpha} kg/mV/V")
        self.report_lines.append(f"Effective Lysimeter Surface Area (Beta): {beta} m^2")

        # Static text for calibration assumptions and equation
        self.report_lines.append("")  # Add a blank line for spacing
        self.report_lines.append(
            "Calibration Factor Equation: alpha (kg / (mV/V)) * (1 m³ / 1000 kg) * "
            "(1 / beta m²) * (1000 mm / 1 m) = Calibration Factor (mm / (mV/V))"
        )
        self.report_lines.append("Depth of water equation: DoW (mm) = (mV/V * Calibration Factor)")
        self.report_lines.append("Assuming a water density of 1000 kg/m^3")
        self.report_lines.append("")  # Add a blank line for spacing

    def add_timescale_info(self, input_timescale, output_timescale):
        """
        Adds timescale information to the report.

        Args:
            input_timescale (str): The timescale of the input data (e.g., 'Min15').
            output_timescale (str): The timescale of the output data (e.g., 'Hourly').
        """
        self.report_lines.append("## Timescale Information:")
        self.report_lines.append(f"Input Data Timescale: {input_timescale}")
        self.report_lines.append(f"Output Data Timescale: {output_timescale}")
        self.report_lines.append("")  # Add a blank line for spacing

    def add_ETa_Kc_info(self, planting_date, harvest_date):
        """
        Adds ETa and Kc information to the report.

        Args:
            planting_date (str): The planting date in 'YYYY-MM-DD' format.
            harvest_date (str): The harvest date in 'YYYY-MM-DD' format.
        """
        self.report_lines.append("## ETa and Kc Information:")
        self.report_lines.append(f"Planting Date: {planting_date}")
        self.report_lines.append(f"Harvest Date: {harvest_date}")
        self.report_lines.append("Assumptions:")
        self.report_lines.append("Kc values are based on FAO-56 guidelines.")
        self.report_lines.append("Kc = ETc / ETa")
        self.report_lines.append("ETa values are calculated using the ASCE Penman-Monteith method via pyfao56 and provided weather station data.")
        self.report_lines.append("Lysimeter crop conditions are assumed to be non-limiting (i.e., no plant stress)")
        self.report_lines.append("") # Add a blank line for spacing

    def export_report(self, output_directory, prefix="run_report"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = os.path.join(output_directory, f"{prefix}_{timestamp}.txt")
        
        self.report_lines.append("## Analysis Model Run Times")
        self.report_lines.append(f"Run Start Time: {self.start_time}")
        self.report_lines.append(f"Run End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        with open(output_filename, 'w') as f:
            f.write("\n".join(self.report_lines))
        
        print(f"Run report exported to {output_filename}")
