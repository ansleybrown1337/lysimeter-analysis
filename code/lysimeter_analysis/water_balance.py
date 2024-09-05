# lysimeter_analysis/water_balance.py
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
            dataframe (pd.DataFrame): The dataframe containing the cleaned, calibrated, and NSE-detected data.
        """
        self.df = dataframe

    def set_custom_calibration_factor(self, factor):
        """
        Allows the user to set a custom calibration factor instead of using predefined ones.
        
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
        Calculates the ETa, interpolates values for NSE periods and noisy data, and creates plots with NSEs highlighted.
        
        Returns:
            pd.DataFrame: DataFrame with ETa columns.
        """
        if self.custom_calibration_factor is None:
            raise ValueError("Calibration factor must be set before calculating ETa.")
        
        # Adding placeholder columns for delta weight (previously labeled as ETa)
        for column in self.df.columns:
            if "_deltaMVV" in column:
                delta_weight_column = column.replace("_deltaMVV", "_deltaMM")
                self.df[delta_weight_column] = self.df[column] * self.custom_calibration_factor * -1
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
            delta_weight_column (str): The name of the delta weight column to be interpolated.
        """
        nse_column = delta_weight_column.replace("_deltaMM", "_NSE")
        
        if nse_column in self.df.columns:
            # Identify NSE periods where interpolation is needed
            nse_mask = self.df[nse_column] == 1
            
            if nse_mask.any():
                # Create a new column for interpolated ETa values
                eta_column = delta_weight_column.replace("_deltaMM", "_ETa_Raw")
                self.df[eta_column] = self.df[delta_weight_column].copy()

                # Interpolate ETa values for NSEs using linear interpolation
                self.df[eta_column] = self.df[eta_column].where(~nse_mask).interpolate(method='linear', limit_direction='both')
                
                # Optionally, fill any remaining NaNs after interpolation
                self.df[eta_column].fillna(method='ffill', inplace=True)
                self.df[eta_column].fillna(method='bfill', inplace=True)

                # Check if interpolation was successful by verifying differences between the original and interpolated values
                if (self.df[eta_column] == self.df[delta_weight_column]).all():
                    print("Warning: Interpolation did not change any values. Ensure that there are valid data points before and after NSEs.")

    def _interpolate_noisy_eta(self, eta_column_raw, threshold_percent=70):
        """
        Identifies noisy ETa values based on the percentage difference from the previous value, 
        and linearly interpolates over those values.

        Args:
            eta_column_raw (str): The name of the raw ETa column to be processed for noise.
            threshold_percent (float): The percentage threshold to detect noisy values. Default is 50%.
        """
        if eta_column_raw not in self.df.columns:
            raise ValueError(f"Column {eta_column_raw} not found in DataFrame.")
        
        # Create a copy of the ETa column for manipulation
        eta_values = self.df[eta_column_raw].copy()

        # Calculate the percentage difference between consecutive values
        percentage_diff = eta_values.pct_change() * 100

        # Identify noisy values where the percentage difference exceeds the threshold
        noisy_mask = percentage_diff.abs() > threshold_percent

        # Create a noisy flag column to indicate where noisy values were detected
        noisy_flag_column = eta_column_raw.replace("_ETa_Raw", "_Noisy_Flag")
        self.df[noisy_flag_column] = noisy_mask.astype(int)  # 1 for noisy, 0 for not noisy

        # Create a new column for the interpolated ETa values, this will be the final '_ETa' column
        eta_column = eta_column_raw.replace("_ETa_Raw", "_ETa")
        self.df[eta_column] = eta_values.copy()

        # Interpolate noisy values by ignoring them and using linear interpolation
        self.df[eta_column] = self.df[eta_column].where(~noisy_mask).interpolate(method='linear')

        # Optionally fill any NaN values created during interpolation (e.g., at the start or end of the data)
        self.df[eta_column].fillna(method='ffill', inplace=True)
        self.df[eta_column].fillna(method='bfill', inplace=True)

        # Log any changes for debugging purposes
        num_noisy_values = noisy_mask.sum()
        if num_noisy_values > 0:
            print(f"Interpolated {num_noisy_values} noisy ETa values in column {eta_column}.")
        else:
            print(f"No noisy values detected in column {eta_column}.")


    def _calculate_cumulative_eta(self):
        """
        Calculates the cumulative ETa for each ETa column in the dataframe.
        This is a private method that is automatically called within the `calculate_eta` method.
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
                # Plot raw ETa values
                clean_column = column.replace("_ETa_Raw", "_ETa")
                
                # Plot the raw ETa line
                fig.add_trace(go.Scatter(x=self.df['TIMESTAMP'], y=self.df[column], mode='lines', name=f'Raw {column}', line=dict(dash='dot')))
                
                # Plot the clean ETa line
                if clean_column in self.df.columns:
                    fig.add_trace(go.Scatter(x=self.df['TIMESTAMP'], y=self.df[clean_column], mode='lines', name=f'Clean {clean_column}'))

                # Highlight NSEs for the clean ETa
                nse_column = clean_column.replace("_ETa", "_NSE")
                if nse_column in self.df.columns:
                    nse_points = self.df[self.df[nse_column] == 1]
                    fig.add_trace(go.Scatter(x=nse_points['TIMESTAMP'], y=nse_points[clean_column], mode='markers',
                                            name=f'NSE {clean_column}', marker=dict(color='red', size=7)))

                # Highlight noisy points for the clean ETa
                noisy_flag_column = clean_column.replace("_ETa", "_Noisy_Flag")
                if noisy_flag_column in self.df.columns:
                    noisy_points = self.df[self.df[noisy_flag_column] == 1]
                    fig.add_trace(go.Scatter(x=noisy_points['TIMESTAMP'], y=noisy_points[clean_column], mode='markers',
                                            name=f'Noisy {clean_column}', marker=dict(color='blue', size=7)))

        fig.update_layout(
            title='ETa Timeseries with NSEs and Noisy Points Highlighted',
            xaxis_title='Timestamp',
            yaxis_title='ETa (mm)',
            template='plotly_white'
        )

        # Save the plot as an HTML file
        if self.output_directory:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename_html = os.path.join(self.output_directory, f"ETa_instance_{timestamp}.html")
            fig.write_html(output_filename_html)
            print(f"Interactive plot saved to {output_filename_html}")

        # Return the Plotly figure
        return fig



    def plot_cumulative_eta(self):
        """
        Plots the cumulative ETa over time, saves the plot as an HTML file, 
        and returns the Plotly figure.
        
        Returns:
            plotly.graph_objects.Figure: The Plotly figure object.
        """
        fig = go.Figure()

        # Add cumulative ETa columns to the plot
        for column in self.df.columns:
            if "_Cumulative_ETa" in column:
                fig.add_trace(go.Scatter(x=self.df['TIMESTAMP'], y=self.df[column], mode='lines', name=column))

        fig.update_layout(
            title='Cumulative ETa Timeseries',
            xaxis_title='Timestamp',
            yaxis_title='Cumulative ETa (mm)',
            template='plotly_white'
        )

        # Save the plot as an HTML file
        if self.output_directory:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename_html = os.path.join(self.output_directory, f"Cumulative_ETa_{timestamp}.html")
            fig.write_html(output_filename_html)
            print(f"Cumulative ETa plot saved to {output_filename_html}")

        # Return the Plotly figure
        return fig
