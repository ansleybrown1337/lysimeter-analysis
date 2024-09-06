# lysimeter_analysis/dat_file_merger.py
'''
Lysimeter data processing tool

Created by:
A.J. Brown
Agricultural Data Scientist
Colorado State University
Ansley.Brown@colostate.edu
5 April 2024

Description: This script loads all ".dat" files in the specified data directory that 
             contain the specified timescale in the filename, imports them into a pandas
             DataFrame, cleans the data, merges them together, and exports the merged 
             DataFrame as a CSV with a datetime in the filename to the specified output 
             directory.
'''

import os
import pandas as pd
from colorama import Fore, Style, init
from datetime import datetime

# Initialize colorama for Windows (allows colored print statements)
init()

class DatFileMerger:
    """
    A class to handle the loading, cleaning, merging, calibrating, and exporting of .dat
    files.
    """

    def __init__(self):
        self.data_directory = None
        self.output_directory = None
        self.calibration_file = None
        self.timescale = "Min15"
        self.dataframes = []
        self.headers_units = {}
        self.designations = []
        self.calibration_df = None
        self.merged_files = []

    def set_data_directory(self, path):
        """Sets the data directory."""
        self.data_directory = path

    def set_output_directory(self, path):
        """Sets the output directory."""
        self.output_directory = path

    def set_calibration_file(self, path):
        """Sets the calibration file path and loads the calibration data if provided."""
        if path:
            self.calibration_file = path
            self._load_calibration_df()
        else:
            self.calibration_file = None

    def set_timescale(self, timescale):
        """
        Sets the timescale to search for in filenames (e.g., 'Min15', 'Min5', 
        'Min60').
        """
        self.timescale = timescale

    def _load_calibration_df(self):
        """
        Loads the calibration coefficients from a CSV file if the calibration file is
        set.
        """
        if self.calibration_file:
            self.calibration_df = pd.read_csv(self.calibration_file, encoding='utf-8')
        else:
            self.calibration_df = None

    def _load_dat_files(self):
        """
        Loads all .dat files in the specified data directory that contain the specified 
        timescale in the filename into pandas DataFrames,
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
                    designation = [
                        desig.strip('"') for desig in lines[3].strip().split(',')
                        ]
                
                # Create dictionary of header names and measurement units
                self.headers_units = {header[i]: units[i] for i in range(len(header))}
                self.designations = designation
                
                # Load the data
                df = pd.read_csv(
                    file_path, skiprows=4, 
                    na_values=["NAN"], 
                    low_memory=False, 
                    names=header
                    )
                
                # Clean the data
                df = self._clean_data(df)
                self.dataframes.append(df)
                self.merged_files.append(file)  # Track the merged file
                print(f"Importing and merging: {file}\n")

    def _clean_data(self, df):
        """
        Cleans the DataFrame by:
        - Converting columns with numeric values in scientific notation from string to 
          numeric.
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

    def _merge_dataframes(self):
        """
        Merges all loaded DataFrames into a single DataFrame.
        
        Returns:
            pd.DataFrame: The merged DataFrame.
        """
        if not self.dataframes:
            raise ValueError("No dataframes to merge. Load data files first. Ensure")
        return pd.concat(self.dataframes, ignore_index=True)

    def _calibrate_data(self, df):
        """
        Adds calibrated data columns to the DataFrame based on the calibration 
        equations.
        
        Args:
            df (pd.DataFrame): The DataFrame to add calibrated columns to.
        
        Returns:
            pd.DataFrame: The DataFrame with calibrated data.
        """
        if self.calibration_df is None:
            print(
                Fore.YELLOW + 
                "No calibration file provided. Proceeding without calibration." + 
                Style.RESET_ALL
            )
            return df  # Return the original dataframe if no calibration is applied

        q7_rn_plus_coefficient = self.calibration_df[
            self.calibration_df['Variable'] == 'Q7_Rn_Plus'
        ]['Coefficient'].values[0]
        
        q7_rn_minus_coefficient = self.calibration_df[
            self.calibration_df['Variable'] == 'Q7_Rn_Minus'
        ]['Coefficient'].values[0]

        for _, row in self.calibration_df.iterrows():
            row['Variable']
            coefficient = row['Coefficient']
            col_name = row['Col_Name']
            new_col_name = f"{col_name}_calibrated"

            if col_name not in df.columns:
                print(
                    Fore.CYAN + 
                    f"Warning: Coefficient column '{col_name}' not found in data."
                    "Proceeding without calibration for this column." + 
                    Style.RESET_ALL
                )
                continue

            if col_name == 'Q7_Rn_Avg':
                df[new_col_name] = df.apply(
                    lambda x: (
                        q7_rn_plus_coefficient * 
                        (1 + (0.066 * 0.2 * x['PVWspeed_Avg'])) * x['Q7_Rn_Avg']
                        if x['PVWspeed_Avg'] > 0 
                        else q7_rn_minus_coefficient * 
                        ((0.00174 * x['PVWspeed_Avg']) + 0.99755) * x['Q7_Rn_Avg']
                    ), 
                    axis=1
                )
            else:
                df[new_col_name] = df[col_name] * coefficient


        return df
    
    def get_merged_files(self):
        """
        Returns the list of files that were successfully merged.
        
        Returns:
            list: List of filenames that were merged.
        """
        return self.merged_files

    def clean_and_calibrated_data(self):
        """
        The main function to load, merge, clean, and calibrate data, and return the 
        processed DataFrame.
        
        Returns:
            pd.DataFrame: The cleaned and calibrated DataFrame, or just cleaned if 
            calibration is not applied.
        """
        self._load_dat_files()
        merged_df = self._merge_dataframes()
        
        if self.calibration_df is not None:
            return self._calibrate_data(merged_df)
        else:
            return merged_df


    def export_to_csv(self, df):
        """
        Exports the processed DataFrame to a CSV file with the current datetime in the 
        filename.
        Includes units as the second row and designations as the third row.
        
        Args:
            df (pd.DataFrame): The DataFrame to export.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = os.path.join(
            self.output_directory, f"merged_data_{timestamp}.csv")
        
        # Create DataFrames for the units and designation rows
        units_row = pd.DataFrame([self.headers_units], index=["units"])
        
        # Adjust designations_row to match the merged_df columns
        designations_row = pd.DataFrame(
            [self.designations + [''] * (df.shape[1] - len(self.designations))], 
            index=["designations"], 
            columns=df.columns
            )
        
        # Concatenate the units and designations rows with the merged dataframe
        combined_df = pd.concat([units_row, designations_row, df], ignore_index=True)
        
        # Write to CSV
        combined_df.to_csv(output_filename, index=False)
        
        print(f"Merged data exported to {output_filename}")
