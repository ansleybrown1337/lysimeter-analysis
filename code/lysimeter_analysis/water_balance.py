'''
Script that converts load cell data (mV/V) to mass (kg) for each time step, and
calculates the actual transpiration rate (mm/t) for each time step.

The logical flow will be as follows:
1. Load the data after being processed by the DatFileMerger and 
NonStandardEvents classes.
2. Convert load cell data to depth of water using the calibration eq. for each
for each lysimeter type (i.e., SL or LL).
    2a. For the SL, 1 mV/V change in the load cell = 157.43 mm (6.198 in)
        of water added or removed.
        "Using a slope of 812.488 and intercept of -112.07, assumed water 
        density of 1000 kg/m3, and a surface area of 2.341 m2 a calibration 
        coefficient of 157.43 mm/mV/V was determined." - Lane Simmons, 11/7/22
        This means the equation is: DoW (mm) = (delta_mV/V * 157.43)
    2b. For the LL, 1 mV/V change in the load cell = 76.2 mm (3.000 in)
        of water added or removed.
        This means the equation is: DoW (mm) = (delta_mV/V * 76.2)
    2c. The DoW is actual evapotranspiration (ETa) in mm, when not in an NSE.
3. Identify ETa rates that are immediately prior to and after each NSE, then
linearly interpolate the ETa rate for the NSE and use that in place of the load
cell-derived ETa rate.
5. Use the ETa rates to calculate the water balance for the selected lysimeter.
'''

import pandas as pd
import os
from datetime import datetime
import plotly.graph_objects as go

class WaterBalance:
    def __init__(self):
        self.df = None
        self.custom_calibration_factor = None
        self.output_directory = None

    def set_dataframe(self, dataframe):
        """
        Sets the dataframe for the WaterBalance class.
        
        Args:
            dataframe (pd.DataFrame): The dataframe containing the cleaned, 
            calibrated, and NSE-detected data.
        """
        self.df = dataframe

    def set_custom_calibration_factor(self, factor):
        """
        Allows the user to set a custom calibration factor instead of using 
        predefined ones.
        
        Args:
            factor (float): Custom calibration factor in mm/mV/V.
        """
        self.custom_calibration_factor = factor

    def set_output_directory(self, output_directory):
        """
        Sets the output directory for saving the plots.
        
        Args:
            output_directory (str): The directory to save the output plot.
        """
        self.output_directory = output_directory

    def calculate_eta(self):
        """
        Calculates the ETa, interpolates values for NSE periods and noisy data, 
        and creates plots with NSEs highlighted.
        
        Returns:
            pd.DataFrame: DataFrame with ETa columns.
        """
        if self.custom_calibration_factor is None:
            raise ValueError("Calibration factor must be set before calculating ETa.")
        
        # Adding placeholder columns for delta weight (previously labeled as ETa)
        for column in self.df.columns:
            if "_deltaMVV" in column:
                delta_weight_column = column.replace("_deltaMVV", "_deltaMM")
                self.df[delta_weight_column] = (
                    self.df[column] * self.custom_calibration_factor * -1
                )
                eta_column_raw = delta_weight_column.replace("_deltaMM", "_ETa_Raw")
                
                # Store the raw ETa values
                self.df[eta_column_raw] = self.df[delta_weight_column].copy()

                # Interpolate NSE periods
                self._interpolate_nse_eta(delta_weight_column)
                eta_column = eta_column_raw.replace("_ETa_Raw", "_ETa")

                # Create the clean _ETa column before noisy interpolation
                self.df[eta_column] = self.df[eta_column_raw].copy()

                # Interpolate noisy ETa values based on the raw data
                self._interpolate_noisy_eta(eta_column_raw)

        # Calculate cumulative ETa after ETa interpolation
        self._calculate_cumulative_eta()

        return self.df

    def _interpolate_nse_eta(self, delta_weight_column):
        """
        Interpolates ETa values for NSE periods by using neighboring ETa values.
        
        Args:
            delta_weight_column (str): The name of the delta weight column 
            to be interpolated.
        """
        nse_column = delta_weight_column.replace("_deltaMM", "_NSE")
        
        if nse_column in self.df.columns:
            # Identify NSE periods where interpolation is needed
            nse_mask = self.df[nse_column] == 1
            
            if nse_mask.any():
                eta_column = delta_weight_column.replace("_deltaMM", "_ETa_Raw")
                self.df[eta_column] = self.df[delta_weight_column].copy()

                # Interpolate ETa values for NSEs using linear interpolation
                self.df[eta_column] = self.df[eta_column].where(
                    ~nse_mask).interpolate(method='linear', limit_direction='both'
                )
                
                # Fill any remaining NaNs after interpolation
                self.df[eta_column].fillna(method='ffill', inplace=True)
                self.df[eta_column].fillna(method='bfill', inplace=True)

                if (self.df[eta_column] == self.df[delta_weight_column]).all():
                    print("Warning: Interpolation did not change any values.")

    def _interpolate_noisy_eta(self, eta_column_raw, threshold_percent=70):
        """
        Identifies noisy ETa values based on the percentage difference from 
        the previous value, if they are negative, or if they are more than 
        3 standard deviations from the mean of the '_ETa_Raw' series, or if 
        they are flagged as NSE. Linearly interpolates over noisy/NSE regions.
        
        Args:
            eta_column_raw (str): The name of the raw ETa column to be processed.
            threshold_percent (float): Percentage threshold to detect noisy values.
        """
        if eta_column_raw not in self.df.columns:
            raise ValueError(f"Column {eta_column_raw} not found in DataFrame.")
        
        # Create a copy of the ETa column for manipulation
        eta_values = self.df[eta_column_raw].copy()

        # Calculate percentage difference between consecutive values
        percentage_diff = eta_values.pct_change() * 100

        # Identify noisy values where the percentage difference exceeds the threshold
        noisy_mask_percent_diff = percentage_diff.abs() > threshold_percent

        # Identify negative ETa values
        noisy_mask_negative = eta_values < 0

        # Calculate the mean and standard deviation of the ETa raw values
        mean_eta = eta_values.mean()
        std_eta = eta_values.std()

        # Identify noisy values more than 3 standard deviations from the mean
        noisy_mask_std_dev = (
            (eta_values < (mean_eta - 3 * std_eta)) |
            (eta_values > (mean_eta + 3 * std_eta))
        )

        # Flag NSE (Non-Standard Events) values as noisy
        nse_column = eta_column_raw.replace("_ETa_Raw", "_NSE")
        if nse_column in self.df.columns:
            noisy_mask_nse = self.df[nse_column] == 1
        else:
            noisy_mask_nse = pd.Series([False] * len(self.df))

        # Combine all noisy conditions
        noisy_mask = (
            noisy_mask_percent_diff | noisy_mask_negative |
            noisy_mask_std_dev | noisy_mask_nse
        )

        # Create a noisy flag column
        noisy_flag_column = eta_column_raw.replace("_ETa_Raw", "_Noisy_Flag")
        self.df[noisy_flag_column] = noisy_mask.astype(int)

        # Interpolate noisy, negative, and NSE values
        eta_column = eta_column_raw.replace("_ETa_Raw", "_ETa")
        self.df[eta_column] = eta_values.copy()

        for i in range(len(self.df)):
            if noisy_mask.iloc[i]:
                start_idx = i - 1
                while start_idx >= 0 and (
                    noisy_mask.iloc[start_idx] or eta_values.iloc[start_idx] <= 0
                ):
                    start_idx -= 1

                end_idx = i + 1
                while end_idx < len(self.df) and (
                    noisy_mask.iloc[end_idx] or eta_values.iloc[end_idx] <= 0
                ):
                    end_idx += 1

                if start_idx >= 0 and end_idx < len(self.df):
                    start_val = eta_values.iloc[start_idx]
                    end_val = eta_values.iloc[end_idx]
                    span = end_idx - start_idx
                    for idx in range(start_idx + 1, end_idx):
                        self.df.loc[idx, eta_column] = (
                            start_val + (
                            (end_val - start_val) / span
                            ) * (idx - start_idx)
                        )

        self.df[eta_column].fillna(method='ffill', inplace=True)
        self.df[eta_column].fillna(method='bfill', inplace=True)

        num_noisy_values = noisy_mask.sum()
        if num_noisy_values > 0:
            print(f"Interpolated {num_noisy_values} noisy or NSE ETa values.")
        else:
            print(f"No noisy or NSE values detected in {eta_column}.")

    def _calculate_cumulative_eta(self):
        """
        Calculates the cumulative ETa for each ETa column in the dataframe.
        This is a private method that is automatically called within the 
        `calculate_eta` method.
        """
        for column in self.df.columns:
            if "_ETa" in column and "_Cumulative_ETa" not in column:
                cumulative_column = column.replace("_ETa", "_Cumulative_ETa")
                self.df[cumulative_column] = self.df[column].cumsum()

    def plot_eta_with_nse(self):
        """
        Plots the ETa timeseries with NSEs and noisy points highlighted, 
        saves the plot as an HTML file, and returns the Plotly figure.
        
        Returns:
            plotly.graph_objects.Figure: The Plotly figure object.
        """
        fig = go.Figure()

        # Add raw and clean ETa columns to the plot, excluding cumulative ETa
        for column in self.df.columns:
            if "_ETa_Raw" in column and "_Cumulative_ETa" not in column:
                clean_column = column.replace("_ETa_Raw", "_ETa")
                
                fig.add_trace(go.Scatter(
                    x=self.df['TIMESTAMP'], y=self.df[column], mode='lines', 
                    name=f'Raw {column}', line=dict(dash='dot')
                ))
                
                if clean_column in self.df.columns:
                    fig.add_trace(go.Scatter(
                        x=self.df['TIMESTAMP'], y=self.df[clean_column], mode='lines', 
                        name=f'Clean {clean_column}'
                    ))

                nse_column = clean_column.replace("_ETa", "_NSE")
                if nse_column in self.df.columns:
                    nse_points = self.df[self.df[nse_column] == 1]
                    fig.add_trace(go.Scatter(
                        x=nse_points['TIMESTAMP'], y=nse_points[clean_column], 
                        mode='markers', name=f'NSE {clean_column}', 
                        marker=dict(color='red', size=7)
                    ))

                noisy_flag_column = clean_column.replace("_ETa", "_Noisy_Flag")
                if noisy_flag_column in self.df.columns:
                    noisy_points = self.df[self.df[noisy_flag_column] == 1]
                    fig.add_trace(go.Scatter(
                        x=noisy_points['TIMESTAMP'], y=noisy_points[clean_column], 
                        mode='markers', name=f'Noisy {clean_column}', 
                        marker=dict(color='blue', size=7)
                    ))

        fig.update_layout(
            title='ETa Timeseries with NSEs and Noisy Points Highlighted',
            xaxis_title='Timestamp', yaxis_title='ETa (mm)', template='plotly_white'
        )

        if self.output_directory:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename_html = os.path.join(
                self.output_directory, f"ETa_instance_{timestamp}.html"
            )
            fig.write_html(output_filename_html)
            print(f"Interactive plot saved to {output_filename_html}")

        return fig

    def plot_cumulative_eta(self):
        """
        Plots the cumulative ETa over time, saves the plot as an HTML file, 
        and returns the Plotly figure.
        
        Returns:
            plotly.graph_objects.Figure: The Plotly figure object.
        """
        fig = go.Figure()

        for column in self.df.columns:
            if "_Cumulative_ETa" in column:
                fig.add_trace(go.Scatter(
                    x=self.df['TIMESTAMP'], y=self.df[column], mode='lines', name=column
                ))

        fig.update_layout(
            title='Cumulative ETa Timeseries', xaxis_title='Timestamp', 
            yaxis_title='Cumulative ETa (mm)', template='plotly_white'
        )

        if self.output_directory:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename_html = os.path.join(
                self.output_directory, f"Cumulative_ETa_{timestamp}.html"
            )
            fig.write_html(output_filename_html)
            print(f"Cumulative ETa plot saved to {output_filename_html}")

        return fig
