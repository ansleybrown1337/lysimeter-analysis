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
cell -derived ETa rate.
5. Use the ETa rates to calculate the water balance for the selected lysimeter.
'''
import pandas as pd
import os
from datetime import datetime
import plotly.graph_objects as go

class WaterBalance:
    def __init__(self):
        self.df = None
        self.lysimeter_type = None
        self.custom_calibration_factor = None
        self.output_directory = None

    def set_dataframe(self, dataframe):
        """
        Sets the dataframe for the WaterBalance class.
        
        Args:
            dataframe (pd.DataFrame): The dataframe containing the cleaned, calibrated, and NSE-detected data.
        """
        self.df = dataframe

    def set_lysimeter_type(self, lysimeter_type):
        """
        Sets the lysimeter type and automatically assigns the appropriate calibration factor.
        
        Args:
            lysimeter_type (str): The type of lysimeter ('SL' or 'LL').
        """
        self.lysimeter_type = lysimeter_type
        if lysimeter_type == "SL":
            self.custom_calibration_factor = 157.43
        elif lysimeter_type == "LL":
            self.custom_calibration_factor = 76.2
        else:
            raise ValueError("Invalid lysimeter type. Choose either 'SL' or 'LL'.")

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
        Calculates the ETa and creates a plot with NSEs highlighted.
        
        Returns:
            pd.DataFrame: DataFrame with ETa columns.
        """
        if self.custom_calibration_factor is None:
            raise ValueError("Calibration factor must be set either via lysimeter type or custom factor.")
        
        # Adding placeholder columns for ETa
        for column in self.df.columns:
            if "_rate_of_change" in column:
                eta_column = column.replace("_rate_of_change", "_ETa")
                self.df[eta_column] = self.df[column] * self.custom_calibration_factor

        # Automatically plot ETa with NSEs highlighted
        self._plot_eta_with_nse()

        return self.df

    def _plot_eta_with_nse(self):
        """
        Plots the ETa timeseries with NSEs highlighted and saves the plot as an HTML file.
        This is a private method that is automatically called within the `calculate_eta` method.
        """
        if not self.output_directory:
            raise ValueError("Output directory must be set before plotting.")

        fig = go.Figure()

        # Add ETa columns to the plot
        for column in self.df.columns:
            if "_ETa" in column:
                fig.add_trace(go.Scatter(x=self.df['TIMESTAMP'], y=self.df[column], mode='lines', name=column))

                # Highlight NSEs
                nse_column = column.replace("_ETa", "_NSE")
                if nse_column in self.df.columns:
                    nse_points = self.df[self.df[nse_column] == 1]
                    fig.add_trace(go.Scatter(x=nse_points['TIMESTAMP'], y=nse_points[column], mode='markers',
                                             name=f'NSE {column}', marker=dict(color='red', size=10)))

        fig.update_layout(
            title='ETa Timeseries with NSEs Highlighted',
            xaxis_title='Timestamp',
            yaxis_title='ETa (mm)',
            template='plotly_white'
        )

        # Save the plot as an HTML file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename_html = os.path.join(self.output_directory, f"ETa_plot_{timestamp}.html")
        fig.write_html(output_filename_html)

        print(f"Interactive plot saved to {output_filename_html}")