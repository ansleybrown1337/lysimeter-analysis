import os
from datetime import datetime

class ReportGenerator:
    def __init__(self):
        self.report = {}
        self.start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def add_parameter(self, key, value):
        self.report[key] = value

    def add_nse_summary(self, nse_summary_df):
        # Convert the DataFrame to a dictionary for easier formatting in the text report
        nse_summary_dict = nse_summary_df.to_dict(orient='records')
        self.report['NSE Summary'] = nse_summary_dict

    def add_calibration_info(self, calibration_info):
        self.report['Calibration Info'] = calibration_info

    def add_file_info(self, merged_files):
        self.report['Merged Files'] = merged_files

    def _format_section(self, title, content):
        """Helper method to format sections of the report."""
        formatted_content = f"{title}\n{'=' * len(title)}\n"
        if isinstance(content, dict):
            for key, value in content.items():
                formatted_content += f"{key}: {value}\n"
        elif isinstance(content, list):
            for item in content:
                if isinstance(item, dict):
                    for key, value in item.items():
                        formatted_content += f"{key}: {value}\n"
                    formatted_content += "\n"
                else:
                    formatted_content += f"{item}\n"
        else:
            formatted_content += f"{content}\n"
        formatted_content += "\n"
        return formatted_content

    def export_report(self, output_directory, prefix="run_report"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = os.path.join(output_directory, f"{prefix}_{timestamp}.txt")

        report_content = ""
        report_content += f"Run Report\n{'=' * 10}\n"
        report_content += f"Run Start Time: {self.start_time}\n"
        report_content += f"Run End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        for section, content in self.report.items():
            report_content += self._format_section(section, content)

        with open(output_filename, 'w') as f:
            f.write(report_content)
        
        print(f"Run report exported to {output_filename}")
