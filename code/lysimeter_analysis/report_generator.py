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

    def add_nse_summary(self, nse_summary):
        self.report_lines.append("## NSE Summary:")
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
            "Calibration Factor Equation: α (kg / (mV/V)) * (1 m³ / 1000 kg) * "
            "(1 / β m²) * (1000 mm / 1 m) = Calibration Factor (mm / (mV/V))"
        )
        self.report_lines.append("Depth of water equation: DoW (mm) = (mV/V * Calibration Factor)")
        self.report_lines.append("Assuming a water density of 1000 kg/m^3")
        self.report_lines.append("")  # Add a blank line for spacing

    def export_report(self, output_directory, prefix="run_report"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = os.path.join(output_directory, f"{prefix}_{timestamp}.txt")
        
        self.report_lines.append("## Analysis Model Run Times")
        self.report_lines.append(f"Run Start Time: {self.start_time}")
        self.report_lines.append(f"Run End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        with open(output_filename, 'w') as f:
            f.write("\n".join(self.report_lines))
        
        print(f"Run report exported to {output_filename}")
