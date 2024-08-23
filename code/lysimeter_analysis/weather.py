# weather.py

import pandas as pd
import numpy as np
import os
from datetime import datetime
from pyfao56.refet import ascedaily

class WeatherETR:
    def __init__(self, elevation=1274.064, latitude=38.0385):
        """
        Initializes the WeatherETR class with default elevation and latitude for RFD01 CoAgMET station.
        
        Args:
            elevation (float): Elevation of the weather station in meters.
            latitude (float): Latitude of the weather station in decimal degrees.
        """
        self.elevation = elevation
        self.latitude = latitude
        self.df = None

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

        # Calculate dew point temperature Td = T - ((100 - RH) / 5) where T is temperature in Celsius and RH is relative humidity in percent
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
            # Automatically detect columns ending with '_ETa'
            eta_columns = [col for col in self.df.columns if col.endswith('_ETa')]
        
        for eta_col in eta_columns:
            if eta_col in self.df.columns:
                kc_col = eta_col.replace('_ETa', '_Kc')
                self.df[kc_col] = self.df[eta_col] / self.df[etr_column]
                print(f"Calculated Kc for {eta_col}, results stored in {kc_col}.")
            else:
                print(f"Warning: {eta_col} column not found in DataFrame.")
