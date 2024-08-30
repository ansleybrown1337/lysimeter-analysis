# lysimeter_analysis/non_standard_events.py

import pandas as pd
import plotly.graph_objects as go
import os
from datetime import datetime
from scipy.ndimage import gaussian_filter1d
from lysimeter_analysis.utils import awat_filter

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
        self.manual_nse_df = None  # DataFrame for manually defined NSEs
        self.plotly_figure = None  # Attribute to store the Plotly figure

    def set_dataframe(self, dataframe):
        """Sets the dataframe to be used for NSE detection."""
        self.df = dataframe

    def set_possible_columns(self, possible_columns):
        """Sets the possible columns to check for NSEs."""
        self.possible_columns = possible_columns

    def set_threshold(self, threshold):
        """
        Sets the rate of change threshold to classify an NSE.
        """
        self.threshold = threshold

    def set_output_directory(self, output_directory):
        """Sets the output directory for saving plots and results."""
        self.output_directory = output_directory

    def load_manual_nse(self, file_path):
        """
        Loads a CSV file containing manually defined NSE events.
        
        Args:
            file_path (str): Path to the CSV file.
        """
        try:
            self.manual_nse_df = pd.read_csv(file_path, parse_dates=['Start Datetime', 'Stop Datetime'])
            print(f"Manual NSE data successfully loaded from {file_path}")
            # Coerce columns to correct data types
            self.manual_nse_df['Event Type'] = self.manual_nse_df['Event Type'].astype(str)
            self.manual_nse_df['Start Datetime'] = pd.to_datetime(self.manual_nse_df['Start Datetime'])
            self.manual_nse_df['Stop Datetime'] = pd.to_datetime(self.manual_nse_df['Stop Datetime'])
            self.manual_nse_df['Notes'] = self.manual_nse_df['Notes'].astype(str)
        except Exception as e:
            print(f"Error loading manual NSE data: {e}")

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
        Detects non-standard events (NSEs) based on sharp increases in the specified columns and incorporates manually defined events.
        
        Returns:
            pd.DataFrame: A DataFrame with additional columns indicating NSEs and their type.
        """
        self._select_columns()  # Ensure columns are selected before detecting NSEs
        
        for column in self.columns:
            # Calculate the rate of change for auto-detection
            self.df[f'{column}_deltaMVV'] = self.df[column].diff()
            # Initialize the NSE detection columns
            self.df[f'{column}_NSE'] = 0
            self.df[f'{column}_NSE_Type'] = None
            
            # Detect auto-detected NSEs
            auto_detect_mask = self.df[f'{column}_deltaMVV'] > self.threshold
            self.df.loc[auto_detect_mask, f'{column}_NSE'] = 1
            self.df.loc[auto_detect_mask, f'{column}_NSE_Type'] = 'auto-detected'
            
            # Incorporate manually defined NSEs
            if self.manual_nse_df is not None:
                for _, row in self.manual_nse_df.iterrows():
                    start = row['Start Datetime']
                    stop = row['Stop Datetime']
                    event_type = row['Event Type']
                    # Flag the NSEs within the manually defined range
                    manual_nse_mask = (self.df['TIMESTAMP'] >= start) & (self.df['TIMESTAMP'] <= stop)
                    
                    # Update NSE flag and type only if not already flagged
                    self.df.loc[manual_nse_mask, f'{column}_NSE'] = 1
                    self.df.loc[manual_nse_mask & (self.df[f'{column}_NSE_Type'].isna()), f'{column}_NSE_Type'] = event_type
                    
                    # If already flagged, append the manual event type to existing type
                    self.df.loc[manual_nse_mask & (~self.df[f'{column}_NSE_Type'].isna()), f'{column}_NSE_Type'] += f', {event_type}'

            # Store the NSE count in the dictionary
            self.NSEcount[column] = self.df[f'{column}_NSE'].sum()

        return self.df

    def plot_nse(self):
        """
        Creates an interactive Plotly plot highlighting NSEs, adds Gaussian-smoothed data, and returns the figure.
        
        Returns:
            plotly.graph_objects.Figure: The Plotly figure object.
        """
        # Interactive Plotly Plot
        fig = go.Figure()

        for idx, column in enumerate(self.columns):
            # Plot original data
            fig.add_trace(go.Scatter(x=self.df['TIMESTAMP'], y=self.df[column], mode='lines', name=column))

            # Apply Gaussian smoothing and plot the smoothed data
            smoothed_data = gaussian_filter1d(self.df[column], sigma=1)  # Adjust sigma as needed
            fig.add_trace(go.Scatter(x=self.df['TIMESTAMP'], y=smoothed_data, mode='lines', name=f'{column} (Gaussian Smoothed)', line=dict(dash='dash')))

            # Highlight NSEs
            nse_points = self.df[self.df[f'{column}_NSE'] == 1]
            fig.add_trace(go.Scatter(x=nse_points['TIMESTAMP'], y=nse_points[column], mode='markers', 
                                     name=f'NSE {column}', marker=dict(color='red', size=10)))

        fig.update_layout(
            title='Time Series with NSEs Highlighted (Including Smoothed Data)',
            xaxis_title='Timestamp',
            yaxis_title='mV/V',
            template='plotly_white'
        )

        # Store the figure as a class attribute
        self.plotly_figure = fig

        # Optionally save the plot to an HTML file (comment this out if not needed)
        if self.output_directory:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename_html = os.path.join(self.output_directory, f"NSE_plot_{timestamp}.html")
            fig.write_html(output_filename_html)
            print(f"Interactive NSE plot saved to {output_filename_html}")

        # Return the Plotly figure
        return fig
