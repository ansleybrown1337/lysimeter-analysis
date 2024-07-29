#!/usr/bin/env python3
'''
Lysimeter data processing tool

Created by:
A.J. Brown
Agricultural Data Scientist
Colorado State University
Ansley.Brown@colostate.edu
5 April 2024

Description: This script loads all ".dat" files in the specified data directory that contain the specified timescale in the filename,
             imports them into a pandas DataFrame, cleans the data, merges them together,
             and exports the merged DataFrame as a CSV with a datetime
             in the filename to the specified output directory.
'''

import os
import pandas as pd
from colorama import Fore, Style, init
from datetime import datetime
import argparse

# Initialize colorama for Windows (allows colored print statements)
init()

class DatFileMerger:
    """
    A class to handle the loading, cleaning, merging, calibrating, and exporting of .dat files.
    """

    def __init__(self, data_directory, output_directory, calibration_file, timescale):
        """
        Initializes the DatFileMerger with the given directories, calibration file, and timescale.
        
        Args:
            data_directory (str): The directory to search for .dat files.
            output_directory (str): The directory to save the output CSV file.
            calibration_file (str): The file path for the calibration coefficients CSV file.
            timescale (str): The timescale to search for in the filenames (e.g., "Min15", "Min5", "Min60").
        """
        self.data_directory = data_directory
        self.output_directory = output_directory
        self.calibration_file = calibration_file
        self.timescale = timescale
        self.dataframes = []
        self.headers_units = {}
        self.designations = []
        self.calibration_df = self.load_calibration_df()

    def load_calibration_df(self):
        """
        Loads the calibration coefficients from a CSV file.
        
        Returns:
            pd.DataFrame: The calibration coefficients DataFrame.
        """
        return pd.read_csv(self.calibration_file, encoding='utf-8')

    def load_dat_files(self):
        """
        Loads all .dat files in the specified data directory that contain the specified timescale in the filename into pandas DataFrames,
        and prints out the files being imported and merged.
        """
        for file in os.listdir(self.data_directory):
            if file.endswith(".dat") and self.timescale in file:
                file_path = os.path.join(self.data_directory, file)
                
                # Read the header lines
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                    header = [col.strip('"') for col in lines[1].strip().split(',')]
                    units = [unit.strip('"') for unit in lines[2].strip().split(',')]
                    designation = [desig.strip('"') for desig in lines[3].strip().split(',')]
                
                # Create dictionary of header names and measurement units
                self.headers_units = {header[i]: units[i] for i in range(len(header))}
                self.designations = designation
                
                # Load the data
                df = pd.read_csv(file_path, skiprows=4, na_values=["NAN"], low_memory=False, names=header)
                
                # Clean the data
                df = self.clean_data(df)
                self.dataframes.append(df)
                print(f"Importing and merging: {file}\n")

    def clean_data(self, df):
        """
        Cleans the DataFrame by:
        - Converting columns with numeric values in scientific notation from string to numeric.
        - Converting the first column to datetime.
        - Removing quotation marks from column headers and units.
        
        Args:
            df (pd.DataFrame): The DataFrame to clean.
        
        Returns:
            pd.DataFrame: The cleaned DataFrame.
        """
        # Remove quotation marks from column headers
        df.columns = df.columns.str.strip('"')
        
        # Convert all columns to numeric where possible, except the first column
        for col in df.columns[1:]:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Convert the first column to datetime
        df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], errors='coerce')

        # Ensure the first column remains named 'TIMESTAMP'
        df.rename(columns={df.columns[0]: 'TIMESTAMP'}, inplace=True)
        
        return df

    def merge_dataframes(self):
        """
        Merges all loaded DataFrames into a single DataFrame.
        
        Returns:
            pd.DataFrame: The merged DataFrame.
        """
        if not self.dataframes:
            raise ValueError("No dataframes to merge. Load data files first.")
        merged_df = pd.concat(self.dataframes, ignore_index=True)
        return merged_df

    def calibrate_data(self, df):
        """
        Adds calibrated data columns to the DataFrame based on the calibration equations.
        
        Args:
            df (pd.DataFrame): The DataFrame to add calibrated columns to.
        
        Returns:
            pd.DataFrame: The DataFrame with calibrated data.
        """
        q7_rn_plus_coefficient = self.calibration_df[self.calibration_df['Variable'] == 'Q7_Rn_Plus']['Coefficient'].values[0]
        q7_rn_minus_coefficient = self.calibration_df[self.calibration_df['Variable'] == 'Q7_Rn_Minus']['Coefficient'].values[0]

        for _, row in self.calibration_df.iterrows():
            variable = row['Variable']
            coefficient = row['Coefficient']
            col_name = row['Col_Name']
            new_col_name = f"{col_name}_calibrated"

            if col_name not in df.columns:
                print(Fore.CYAN + f"Warning: Coefficient column '{col_name}' not found in lysimeter data. Proceeding without calibration for this column." + Style.RESET_ALL)
                continue

            if col_name == 'Q7_Rn_Avg':
                df[new_col_name] = df.apply(
                    lambda x: q7_rn_plus_coefficient * (1 + (0.066 * 0.2 * x['PVWspeed_Avg'])) * x['Q7_Rn_Avg'] 
                    if x['PVWspeed_Avg'] > 0 else q7_rn_minus_coefficient * ((0.00174 * x['PVWspeed_Avg']) + 0.99755) * x['Q7_Rn_Avg'], axis=1)
            else:
                df[new_col_name] = df[col_name] * coefficient

        return df

    def export_to_csv(self, merged_df):
        """
        Exports the merged DataFrame to a CSV file with the current datetime in the filename.
        Includes units as the second row and designations as the third row.
        
        Args:
            merged_df (pd.DataFrame): The merged DataFrame to export.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = os.path.join(self.output_directory, f"merged_data_{timestamp}.csv")
        
        # Create DataFrames for the units and designation rows
        units_row = pd.DataFrame([self.headers_units], index=["units"])
        
        # Adjust designations_row to match the merged_df columns
        designations_row = pd.DataFrame([self.designations + [''] * (merged_df.shape[1] - len(self.designations))], 
                                        index=["designations"], 
                                        columns=merged_df.columns)
        
        # Concatenate the units and designations rows with the merged dataframe
        combined_df = pd.concat([units_row, designations_row, merged_df], ignore_index=True)
        
        # Write to CSV
        combined_df.to_csv(output_filename, index=False)
        
        print(f"Merged data exported to {output_filename}")

def main(data_directory, output_directory, calibration_file, timescale):
    """
    The main function to execute when the script is run directly.
    
    Args:
        data_directory (str): The directory to search for .dat files.
        output_directory (str): The directory to save the output CSV file.
        calibration_file (str): The file path for the calibration coefficients CSV file.
        timescale (str): The timescale to search for in the filenames (e.g., "Min15", "Min5", "Min60").
    """
    merger = DatFileMerger(data_directory, output_directory, calibration_file, timescale)
    
    merger.load_dat_files()
    merged_df = merger.merge_dataframes()
    calibrated_df = merger.calibrate_data(merged_df)
    merger.export_to_csv(calibrated_df)

    # Print header names, measurement units, and calibration coefficients
    print("\nHeader names, measurement units, and designations:")
    for header, unit in merger.headers_units.items():
        print(f"{header}: {unit}")
    print("\nDesignations:")
    print(merger.designations)

    # Print calibration coefficients
    print("\nSensor Calibration Coefficients:")
    print(merger.calibration_df)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge .dat files containing the specified timescale and export to CSV.")
    parser.add_argument("data_directory", type=str, help="Directory containing .dat files.")
    parser.add_argument("output_directory", type=str, help="Directory to save the output CSV file.")
    parser.add_argument("calibration_file", type=str, help="File path for the calibration coefficients CSV file.")
    parser.add_argument("timescale", type=str, help="Timescale to search for in filenames (e.g., 'Min15', 'Min5', 'Min60').")
    args = parser.parse_args()
    
    main(args.data_directory, args.output_directory, args.calibration_file, args.timescale)

"""
Example usage:

1. Open Anaconda Prompt.

2. Activate the conda environment:
    conda activate playground2

3. Navigate to the script directory:
    cd C:\\Users\\AJ-CPU\\Documents\\GitHub\\lysimeter-data-2023\\code

4. Run the script, specifying the data directory, output directory, calibration file, and timescale:
    python lysimeter_analysis/dat_file_merger.py C:\\Users\\AJ-CPU\\Documents\\GitHub\\lysimeter-data-2023\\private_data C:\\Users\\AJ-CPU\\Documents\\GitHub\\lysimeter-data-2023\\private_output C:\\Users\\AJ-CPU\\Documents\\GitHub\\lysimeter-data-2023\\code\\coefficients.csv Min15
"""