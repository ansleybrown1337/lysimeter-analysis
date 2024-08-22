# lysimeter_analysis/non_standard_events.py

import pandas as pd
import plotly.graph_objects as go
import os
from datetime import datetime
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d  # Import Gaussian filter
from lysimeter_analysis.utils import awat_filter  # Import AWAT filter

class NonStandardEvents:
    def __init__(self, dataframe=None):
        """
        Initializes the NonStandardEvents class with an optional dataframe.
        
        Args:
            dataframe (pd.DataFrame, optional): The DataFrame containing the cleaned and calibrated data. Defaults to None.
        """
        self.df = dataframe
        self.columns = None
        self.threshold = 0.0034  # Default threshold for detecting NSEs
        self.output_directory = None
        self.possible_columns = None  # New attribute for possible columns
        self.NSEcount = {}  # Attribute to store NSE counts

    def set_dataframe(self, dataframe):
        """Sets the dataframe to be used for NSE detection."""
        self.df = dataframe

    def set_possible_columns(self, possible_columns):
        """Sets the possible columns to check for NSEs."""
        self.possible_columns = possible_columns

    def set_threshold(self, threshold):
        """
        Sets the rate of change threshold to classify an NSE.
        The initial threshold is set to 0.0004, but this will be changed.
        The new default will be 0.0034 mV/V, or .254 mm (0.01") of water, which
        is the smallest detectable precip in the tipping bucket rain gauge.
        The new, larger threshold will result in less NSEs being detected.
        """
        self.threshold = threshold

    def set_output_directory(self, output_directory):
        """Sets the output directory for saving plots and results."""
        self.output_directory = output_directory

    def _select_columns(self):
        """Selects columns for NSE detection based on the possible columns provided."""
        columns_to_check = []
        for col in self.possible_columns:
            if col in self.df.columns:
                columns_to_check.append(col)
        
        if not columns_to_check:
            raise ValueError("None of the expected columns for NSE detection were found.")
        
        self.columns = columns_to_check

    def detect_nse(self):
        """
        Detects non-standard events (NSEs) based on sharp increases in the specified columns.
        
        Returns:
            pd.DataFrame: A DataFrame with additional columns indicating NSEs.
        """
        self._select_columns()  # Ensure columns are selected before detecting NSEs
        
        for column in self.columns:
            # Calculate the rate of change
            self.df[f'{column}_deltaMVV'] = self.df[column].diff()
            # Flag positive NSEs
            self.df[f'{column}_NSE'] = self.df[f'{column}_deltaMVV'].apply(lambda x: 1 if x > self.threshold else 0)
            # Store the NSE count in the dictionary
            self.NSEcount[column] = self.df[f'{column}_NSE'].sum()

        return self.df

    def plot_nse(self):
        """
        Plots the time series with NSE values highlighted and saves the plot as both a PNG file and an HTML file.
        Also adds Gaussian-smoothed and AWAT-filtered data to the Plotly graph.
        """
        # Static Matplotlib Plot
        plt.figure(figsize=(14, 8))
        colors = ['blue', 'green', 'red', 'orange']

        for idx, column in enumerate(self.columns):
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
        output_filename_png = os.path.join(self.output_directory, f"NSE_plot_{timestamp}.png")
        plt.savefig(output_filename_png)
        plt.close()
        
        print(f"Static NSE plot saved to {output_filename_png}")

        # Interactive Plotly Plot
        fig = go.Figure()

        for idx, column in enumerate(self.columns):
            # Plot original data
            fig.add_trace(go.Scatter(x=self.df['TIMESTAMP'], y=self.df[column], mode='lines', name=column))

            # Apply Gaussian smoothing and plot the smoothed data
            smoothed_data = gaussian_filter1d(self.df[column], sigma=1)  # Adjust sigma as needed
            fig.add_trace(go.Scatter(x=self.df['TIMESTAMP'], y=smoothed_data, mode='lines', name=f'{column} (Gaussian Smoothed)', line=dict(dash='dash')))

            '''# Apply AWAT filter and plot the filtered data (commented out for now until we get it working)

            awat_data = awat_filter(self.df[column], wmax=11, delta_max=0.24, kmax=6)  # Adjust wmax and delta_max as needed
            fig.add_trace(go.Scatter(x=self.df['TIMESTAMP'], y=awat_data, mode='lines', name=f'{column} (AWAT Filtered)', line=dict(dash='dot')))'''

            # Highlight NSEs
            nse_points = self.df[self.df[f'{column}_NSE'] == 1]
            fig.add_trace(go.Scatter(x=nse_points['TIMESTAMP'], y=nse_points[column], mode='markers', 
                                     name=f'NSE {column}', marker=dict(color='red', size=10)))

        fig.update_layout(
            title='Time Series with NSEs Highlighted (Including Smoothed and Filtered Data)',
            xaxis_title='Timestamp',
            yaxis_title='mV/V',
            template='plotly_white'
        )

        output_filename_html = os.path.join(self.output_directory, f"NSE_plot_{timestamp}.html")
        fig.write_html(output_filename_html)

        print(f"Interactive NSE plot saved to {output_filename_html}")
