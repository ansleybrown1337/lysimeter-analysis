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

    def detect_nse(self, columns, threshold):
        """
        Detects non-standard events (NSEs) based on sharp increases in the specified columns.
        
        Args:
            columns (list): List of column names to analyze for NSEs.
            threshold (float): The rate of change threshold to classify an NSE.
        
        Returns:
            pd.DataFrame: A DataFrame with an additional column indicating NSEs.
        """
        for column in columns:
            # Calculate the rate of change
            self.df[f'{column}_rate_of_change'] = self.df[column].diff()
            # Flag positive NSEs
            self.df[f'{column}_NSE'] = self.df[f'{column}_rate_of_change'].apply(lambda x: 1 if x > threshold else 0)
        return self.df

    def plot_nse(self, columns, output_directory):
        """
        Plots the time series with NSE values highlighted and saves the plot as a PNG file.
        
        Args:
            columns (list): List of column names to plot.
            output_directory (str): The directory to save the output plot.
        """
        plt.figure(figsize=(14, 8))
        colors = ['blue', 'green', 'red', 'orange']

        for idx, column in enumerate(columns):
            plt.plot(self.df['TIMESTAMP'], self.df[column], label=column, color=colors[idx % len(colors)])
            # Highlight NSEs
            nse_points = self.df[self.df[f'{column}_NSE'] == 1]
            plt.scatter(nse_points['TIMESTAMP'], nse_points[column], color=colors[(idx + 2) % len(colors)], label=f'NSE {column}', zorder=5)
        
        plt.xlabel('Timestamp')
        plt.ylabel('mV/V')
        plt.title('Time Series with NSEs Highlighted')
        plt.legend()
        plt.grid(True)

        # Save the plot as a PNG file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = os.path.join(output_directory, f"NSE_plot_{timestamp}.png")
        plt.savefig(output_filename)
        plt.close()
        
        print(f"Plot saved to {output_filename}")

    def summarize_nse(self):
        """
        Summarizes the NSEs detected in the dataframe.
        
        Returns:
            pd.DataFrame: A summary DataFrame of NSE counts.
        """
        nse_columns = [col for col in self.df.columns if col.endswith('_NSE')]
        summary = self.df[nse_columns].sum().reset_index()
        summary.columns = ['NSE_Type', 'Counts']
        return summary
