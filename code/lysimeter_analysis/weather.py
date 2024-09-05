# lysimeter_analysis/weather.py

import pandas as pd
import numpy as np
import os
from datetime import datetime
from pyfao56.refet import ascedaily
import plotly.graph_objects as go

class WeatherETR:
    def __init__(self, elevation=None, latitude=None, planting_date=None, harvest_date=None):
        """
        Initializes the WeatherETR class with default elevation, latitude, planting date, and harvest date.
        
        Args:
            elevation (float): Elevation of the weather station in meters.
            latitude (float): Latitude of the weather station in decimal degrees.
            planting_date (str): Default planting date in 'MM-DD-YYYY' format.
            harvest_date (str): Default harvest date in 'MM-DD-YYYY' format.
        """
        self.elevation = elevation
        self.latitude = latitude
        self.df = None
        self.output_directory = None
        # Initialize planting and harvest dates as datetime objects for the current year
        self.planting_date = self.set_planting_date(planting_date)
        self.harvest_date = self.set_harvest_date(harvest_date)

    def set_elevation(self, elevation):
        """
        Sets the elevation of the weather station.
        
        Args:
            elevation (float): Elevation in meters.
        """
        self.elevation = elevation
        print(f"Elevation set to {self.elevation} meters.")

    def set_latitude(self, latitude):
        """
        Sets the latitude of the weather station.
        
        Args:
            latitude (float): Latitude in decimal degrees.
        """
        self.latitude = latitude
        print(f"Latitude set to {self.latitude} degrees.")

    def set_output_directory(self, output_directory):
        """
        Sets the output directory for saving plots.
        
        Args:
            output_directory (str): Path to the directory where plots should be saved.
        """
        self.output_directory = output_directory

    def load_data(self, file_path):
        """
        Loads the weather data from a CSV file into a pandas DataFrame.
        
        Args:
            file_path (str): Path to the CSV file containing weather data.
        """
        try:
            self.df = pd.read_csv(
                file_path,
                skiprows=[0,2,3],  # Skipping unnecessary header rows
                parse_dates=['TIMESTAMP'],
                dayfirst=False,  # Adjust based on your date format
                na_values=['NAN', 'nan', 'NaN', ' ']
            )
            print(f"Data successfully loaded from {file_path}")
        except Exception as e:
            print(f"Error loading data: {e}")

    def preprocess_data(self):
        """
        Preprocesses the DataFrame by handling missing values and calculating necessary parameters.
        """
        if self.df is None:
            raise ValueError("DataFrame is empty. Please load data first using load_data().")
        
        # Rename columns for clarity
        self.df.rename(columns={
            'AirTemp_Max': 'Tmax',
            'AirTemp_Min': 'Tmin',
            'SrMJ_Tot': 'SolarRad',
            'Vap_Press_Avg': 'VaporPressure',
            'WS_2m_Avg': 'WindSpeed',
            'RH_Max': 'RHmax',
            'RH_Min': 'RHmin',
        }, inplace=True)
        
        # Calculate Day of Year
        self.df['DOY'] = self.df['TIMESTAMP'].dt.dayofyear

        # Calculate dew point temperature Td = T - ((100 - RH) / 5)
        self.df['TDew'] = self.df['AirTemp_Avg'] - ((100 - self.df['RH_Avg']) / 5)
        
        # Ensure necessary columns are present
        required_columns = ['TIMESTAMP', 'Tmax', 'Tmin', 'SolarRad', 'VaporPressure', 'WindSpeed', 'DOY']
        for col in required_columns:
            if col not in self.df.columns:
                raise ValueError(f"Required column '{col}' is missing in the data.")
        
        # Handle missing values by interpolation or dropping
        self.df[required_columns[1:]] = self.df[required_columns[1:]].interpolate(method='linear', limit_direction='forward')
        self.df.dropna(subset=required_columns[1:], inplace=True)
        
        print("Data preprocessing completed.")

    def set_planting_date(self, planting_date):
        """
        Sets the planting date.
        
        Args:
            planting_date (str): Planting date in 'MM-DD-YYYY' format.
        """
        self.planting_date = planting_date
        print(f"Planting date set to {self.planting_date}")

    def set_harvest_date(self, harvest_date):
        """
        Sets the harvest date.
        
        Args:
            harvest_date (str): Harvest date in 'MM-DD-YYYY' format.
        """
        self.harvest_date = harvest_date
        print(f"Harvest date set to {self.harvest_date}")

    def calculate_daily_etr(self):
        """
        Calculates daily reference evapotranspiration (ETr) and adds it to the DataFrame.
        """
        if self.df is None:
            raise ValueError("DataFrame is empty. Please load and preprocess data first.")
        
        etr_values = []
        for index, row in self.df.iterrows():
            try:
                etr = ascedaily(
                    rfcrp='T',  # Tall reference crop (alfalfa)
                    z=self.elevation,
                    lat=self.latitude,
                    doy=int(row['DOY']),
                    israd=row['SolarRad'],
                    tmax=row['Tmax'],
                    tmin=row['Tmin'],
                    vapr=row['VaporPressure'],
                    tdew=row['TDew'],
                    rhmax=row['RHmax'],
                    rhmin=row['RHmin'],
                    wndsp=row['WindSpeed'],
                    wndht=2.0 # Wind height in meters, assuming 2m
                )
                etr_values.append(etr)
            except Exception as e:
                print(f"Error calculating ETr for index {index}: {e}")
                etr_values.append(np.nan)
        
        self.df['ETr'] = etr_values
        print("Daily ETr calculation completed.")
    
    def calculate_kc(self, eta_columns=None, etr_column='ETr'):
        """
        Calculates the crop coefficient (Kc) using the formula Kc = ETa / ETr for each specified ETa column.
        
        Args:
            eta_columns (list): List of column names for Actual Evapotranspiration (ETa).
                                If None, it will automatically detect columns ending with '_ETa'.
            etr_column (str): Column name for Reference Evapotranspiration (ETr).
        
        Returns:
            None: The result is added as new columns to the DataFrame.
        """
        if self.df is None:
            raise ValueError("DataFrame is empty. Please load and preprocess data first.")
        
        if etr_column not in self.df.columns:
            raise ValueError(f"'{etr_column}' column is missing. Please ensure ETr is calculated before calculating Kc.")

        if eta_columns is None:
            # Automatically detect columns ending with '_ETa', except '_Cumulative_ETa'
            eta_columns = [col for col in self.df.columns if col.endswith('_ETa') and not col.endswith('_Cumulative_ETa')]
        
        for eta_col in eta_columns:
            if eta_col in self.df.columns:
                kc_col = eta_col.replace('_ETa', '_Kc')
                self.df[kc_col] = self.df[eta_col] / self.df[etr_column]
                print(f"Calculated Kc for {eta_col}, results stored in {kc_col}.")
            else:
                print(f"Warning: {eta_col} column not found in DataFrame.")
    
    def plot_etr_vs_eta(self, eta_columns=None):
        """
        Plots a time series of ETa and ETr values, including points on the lines, saves it as an HTML file, 
        and returns the Plotly figure.
        
        Args:
            eta_columns (list): List of column names for Actual Evapotranspiration (ETa).
                                If None, it will automatically detect columns ending with '_ETa' but not '_Cumulative_ETa'.
        
        Returns:
            plotly.graph_objects.Figure: The Plotly figure object.
        """
        if self.df is None:
            raise ValueError("DataFrame is empty. Please load and preprocess data first.")
        
        if eta_columns is None:
            # Automatically detect columns ending with '_ETa' but exclude '_Cumulative_ETa'
            eta_columns = [col for col in self.df.columns if col.endswith('_ETa') and '_Cumulative_ETa' not in col]
        
        fig = go.Figure()
        
        # Plot ETr with points and lines
        fig.add_trace(go.Scatter(x=self.df['TIMESTAMP'], y=self.df['ETr'], mode='lines+markers', name='ETr'))
        
        # Plot each ETa column with points and lines
        for eta_col in eta_columns:
            if eta_col in self.df.columns:
                fig.add_trace(go.Scatter(x=self.df['TIMESTAMP'], y=self.df[eta_col], mode='lines+markers', name=eta_col))
        
        fig.update_layout(
            title='Time Series of ETa and ETr',
            xaxis_title='Date',
            yaxis_title='Evapotranspiration (mm)',
            template='plotly_white'
        )
        
        # Save the plot as an HTML file
        if not self.output_directory:
            raise ValueError("Output directory must be set before plotting.")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename_html = os.path.join(self.output_directory, f"ETa_vs_ETr_{timestamp}.html")
        fig.write_html(output_filename_html)

        print(f"Interactive plot saved to {output_filename_html}")

        # Return the Plotly figure
        return fig


    def plot_kc_with_fit(self, kc_columns=None):
        """
        Plots a time series of Kc values, saves it as an HTML file, and returns the Plotly figure.
        
        Args:
            kc_columns (list): List of column names for Crop Coefficient (Kc).
                            If None, it will automatically detect columns ending with '_Kc'.
        
        Returns:
            plotly.graph_objects.Figure: The Plotly figure object.
        """
        if self.df is None:
            raise ValueError("DataFrame is empty. Please load and preprocess data first.")
        
        if kc_columns is None:
            # Automatically detect columns ending with '_Kc'
            kc_columns = [col for col in self.df.columns if col.endswith('_Kc')]
        
        fig = go.Figure()

        # Filter the DataFrame for the period between planting and harvest, if they are defined
        if self.planting_date and self.harvest_date:
            df_filtered = self.df[(self.df['TIMESTAMP'] >= self.planting_date) & (self.df['TIMESTAMP'] <= self.harvest_date)]
        else:
            df_filtered = self.df
        
        # Plot each Kc column
        for kc_col in kc_columns:
            if kc_col in df_filtered.columns:
                # Scatter plot of Kc values
                fig.add_trace(go.Scatter(x=df_filtered['TIMESTAMP'], y=df_filtered[kc_col], mode='markers', name=kc_col))
                
                # Fit a 2nd order polynomial
                x_vals = np.arange(len(df_filtered[kc_col].dropna()))
                y_vals = df_filtered[kc_col].dropna().values
                poly_fit = np.polyfit(x_vals, y_vals, 2)
                poly_vals = np.polyval(poly_fit, x_vals)
                
                # Plot the polynomial fit line
                fig.add_trace(go.Scatter(x=df_filtered['TIMESTAMP'].iloc[:len(poly_vals)], y=poly_vals, mode='lines', name=f'{kc_col} Fit'))
        
        fig.update_layout(
            title='Time Series of Kc with 2nd Order Polynomial Fit',
            xaxis_title='Date',
            yaxis_title='Crop Coefficient (Kc)',
            template='plotly_white'
        )
        
        # Save the plot as an HTML file
        if not self.output_directory:
            raise ValueError("Output directory must be set before plotting.")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename_html = os.path.join(self.output_directory, f"Kc_with_fit_{timestamp}.html")
        fig.write_html(output_filename_html)

        print(f"Interactive plot saved to {output_filename_html}")

        # Return the Plotly figure
        return fig
