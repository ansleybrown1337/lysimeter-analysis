# lysimeter_analysis/non_standard_events.py

import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

class NonStandardEvents:
    def __init__(self, dataframe):
        """
        Initializes the NonStandardEvents class with the given dataframe.
        
        Args:
            dataframe (pd.DataFrame): The DataFrame containing the cleaned and calibrated data.
        """
        self.df = dataframe

    def detect_nse(self, column, threshold):
        """
        Detects non-standard events (NSEs) based on sharp increases in the specified column.
        
        Args:
            column (str): The name of the column to analyze for NSEs.
            threshold (float): The rate of change threshold to classify an NSE.
        
        Returns:
            pd.DataFrame: A DataFrame with an additional column indicating NSEs.
        """
        # Calculate the rate of change
        self.df['rate_of_change'] = self.df[column].diff()

        # Flag positive NSEs
        self.df['NSE'] = self.df['rate_of_change'].apply(lambda x: 1 if x > threshold else 0)

        return self.df

    def plot_nse(self, column, output_directory):
        """
        Plots the time series with NSE values highlighted and saves the plot as a PNG file.
        
        Args:
            column (str): The name of the column to plot.
            output_directory (str): The directory to save the output plot.
        """
        plt.figure(figsize=(14, 8))
        plt.plot(self.df['TIMESTAMP'], self.df[column], label=column, color='blue')
        
        # Highlight NSEs
        nse_points = self.df[self.df['NSE'] == 1]
        plt.scatter(nse_points['TIMESTAMP'], nse_points[column], color='red', label='NSE', zorder=5)
        
        plt.xlabel('Timestamp')
        plt.ylabel('mV/V')
        plt.title(f'Time Series of {column} with NSEs Highlighted')
        plt.legend()
        plt.grid(True)

        # Save the plot as a PNG file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = os.path.join(output_directory, f"{column}_NSE_plot_{timestamp}.png")
        plt.savefig(output_filename)
        plt.close()
        
        print(f"Plot saved to {output_filename}")

    def summarize_nse(self):
        """
        Summarizes the NSEs detected in the dataframe.
        
        Returns:
            pd.DataFrame: A summary DataFrame of NSE counts.
        """
        nse_summary = self.df['NSE'].value_counts().rename_axis('NSE').reset_index(name='counts')
        return nse_summary
