#!/usr/bin/env python3
'''
Lysimeter data processing tool

Created by:
A.J. Brown
Agricultural Data Scientist
Colorado State University
Ansley.Brown@colostate.edu
5 April 2024

Description: This script loads all ".dat" files in the specified data directory that contain "Min15" in the filename,
             imports them into a pandas DataFrame, cleans the data, merges them together,
             and exports the merged DataFrame as a CSV with a datetime
             in the filename to the specified output directory.
'''

import os
import pandas as pd
from datetime import datetime

class DatFileMerger:
    """
    A class to handle the loading, cleaning, merging, and exporting of .dat files.
    """

    def __init__(self, data_directory, output_directory):
        """
        Initializes the DatFileMerger with the given directories.
        
        Args:
            data_directory (str): The directory to search for .dat files.
            output_directory (str): The directory to save the output CSV file.
        """
        self.data_directory = data_directory
        self.output_directory = output_directory
        self.dataframes = []
        self.headers_units = {}

    def load_dat_files(self):
        """
        Loads all .dat files in the specified data directory that contain "Min15" in the filename into pandas DataFrames,
        and prints out the files being imported and merged.
        """
        for file in os.listdir(self.data_directory):
            if file.endswith(".dat") and "Min15" in file:
                file_path = os.path.join(self.data_directory, file)
                
                # Read the header lines
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                    header = [col.strip('"') for col in lines[1].strip().split(',')]
                    units = [unit.strip('"') for unit in lines[2].strip().split(',')]
                
                # Create dictionary of header names and measurement units
                self.headers_units = {header[i]: units[i] for i in range(len(header))}
                
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

    def export_to_csv(self, merged_df):
        """
        Exports the merged DataFrame to a CSV file with the current datetime in the filename.
        Includes units as the second row.
        
        Args:
            merged_df (pd.DataFrame): The merged DataFrame to export.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = os.path.join(self.output_directory, f"merged_data_{timestamp}.csv")
        
        # Create a DataFrame for the units row
        units_row = pd.DataFrame([self.headers_units], index=["units"])
        
        # Concatenate the units row with the merged dataframe
        combined_df = pd.concat([pd.DataFrame(units_row), merged_df], ignore_index=True)
        
        # Write to CSV
        combined_df.to_csv(output_filename, index=False)
        
        print(f"Merged data exported to {output_filename}")

def main(data_directory, output_directory):
    """
    The main function to execute when the script is run directly.
    
    Args:
        data_directory (str): The directory to search for .dat files.
        output_directory (str): The directory to save the output CSV file.
    """
    merger = DatFileMerger(data_directory, output_directory)
    
    merger.load_dat_files()
    merged_df = merger.merge_dataframes()
    merger.export_to_csv(merged_df)

    # Print header names and measurement units
    print("\nHeader names and measurement units:")
    for header, unit in merger.headers_units.items():
        print(f"{header}: {unit}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Merge .dat files containing 'Min15' and export to CSV.")
    parser.add_argument("data_directory", type=str, help="Directory containing .dat files.")
    parser.add_argument("output_directory", type=str, help="Directory to save the output CSV file.")
    args = parser.parse_args()
    
    main(args.data_directory, args.output_directory)


"""
Example usage:

1. Open Anaconda Prompt.

2. Activate the conda environment:
    conda activate playground2

3. Navigate to the script directory:
    cd C:\\Users\\AJ-CPU\\Documents\\GitHub\\lysimeter-data-2023\\code

4. Run the script, specifying the data directory and output directory:
    python lysimeter.py C:\\Users\\AJ-CPU\\Documents\\GitHub\\lysimeter-data-2023\\private_data C:\\Users\\AJ-CPU\\Documents\\GitHub\\lysimeter-data-2023\\private_output
"""

