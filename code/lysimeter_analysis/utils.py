# lysimeter_analysis/utils.py
'''
A compilation of utility functions that are used in the lysimeter analysis 
pipeline, but do not fit into any of the other modules per se.
'''

import os
import pandas as pd
import numpy as np
from datetime import datetime
from scipy.signal import savgol_filter
from scipy.stats import t
from warnings import warn

def export_to_csv(df, output_directory, prefix="merged_data"):
    """
    Exports the DataFrame to a CSV file with the current datetime in the filename.
    
    Args:
        df (pd.DataFrame): The DataFrame to export.
        output_directory (str): The directory to save the output CSV file.
        prefix (str): The prefix for the output filename.
    """
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = os.path.join(output_directory, f"{prefix}_{timestamp}.csv")
    
    df.to_csv(output_filename, index=False)
    
    print(f"Data exported to {output_filename}")

def awat_filter(data, wmax=31, delta_max=0.24, kmax=6):
    """
    Apply the AWAT (Adaptive Window and Adaptive Threshold) filter to the data.

    Args:
        data (pd.Series or np.ndarray): The time series data to be filtered.
        wmax (int): The maximum window width for the moving average (in data points).
        delta_max (float): The maximum allowed threshold value.
        kmax (int): The maximum polynomial order for fitting.

    Returns:
        np.ndarray: The filtered data.
    """
    n = len(data)
    filtered_data = np.zeros(n)
    local_window = wmax // 2

    for i in range(n):
        # Define the local window around the current data point
        window_start = max(i - local_window, 0)
        window_end = min(i + local_window + 1, n)
        window_data = data[window_start:window_end]
        t_range = np.arange(len(window_data))

        best_order = 0
        best_aicc = np.inf

        for k in range(1, kmax + 1):
            if len(window_data) > k + 2:
                # Fit polynomial of order k
                coeffs = np.polyfit(t_range, window_data, k)
                poly_fit = np.polyval(coeffs, t_range)
                residuals = window_data - poly_fit
                ssq = np.sum(residuals ** 2)

                # Calculate AICc
                if len(residuals) > k + 2:
                    aicc = len(residuals) * np.log(ssq / len(residuals)) + 2 * (k + 1) + \
                           (2 * (k + 1) * (k + 2)) / (len(residuals) - k - 2)
                    if aicc < best_aicc:
                        best_aicc = aicc
                        best_order = k
            else:
                warn(f"Insufficient residuals for reliable AICc calculation at index {i}. "
                     f"Consider increasing wmax.", UserWarning)
                break

        # Refit the polynomial with the best order if AICc was successfully calculated
        if best_aicc != np.inf:
            coeffs_best = np.polyfit(t_range, window_data, best_order)
            poly_fit_best = np.polyval(coeffs_best, t_range)

            # Calculate the noise (sres) and signal strength (B)
            sres = np.std(window_data - poly_fit_best)
            sdat = np.std(window_data)
            B = sres / sdat if sdat != 0 else 0

            # Adaptive window width based on signal strength B
            wi = max(1, int(B * wmax))
            if wi % 2 == 0:
                wi += 1

            # Calculate adaptive threshold (δ)
            # TODO: not sure if this works correctly!!!
            delta_i = min(max(sres, delta_max), delta_max)

            # Apply moving average within the adaptive window
            filtered_value = np.mean(data[window_start:window_end])

            # Apply the adaptive threshold
            if abs(filtered_value - data[i]) > delta_i:
                filtered_data[i] = filtered_value
            else:
                filtered_data[i] = data[i]
        else:
            # If AICc calculation wasn't successful, keep the original data point
            filtered_data[i] = data[i]

    return filtered_data

def convert_to_minutes(time_string):
    """
    Converts a time string (e.g., '15T', '1H', '1D') to minutes.
    
    Args:
        time_string (str): The time string to convert.
    
    Returns:
        int: The equivalent time in minutes.
    """
    time_units = {
        'T': 1,         # Minutes
        'H': 60,        # Hours
        'D': 1440,      # Days
        'W': 10080,     # Weeks
        'M': 43200,     # Months (assuming 30 days in a month)
        'Y': 525600     # Years (assuming 365 days in a year)
    }
    
    # Extract the numeric part and the unit part from the time string
    numeric_part = ''.join(filter(str.isdigit, time_string))
    unit_part = ''.join(filter(str.isalpha, time_string))
    
    # Default numeric part to 1 if no digits are found (e.g., 'D' means '1D')
    numeric_part = int(numeric_part) if numeric_part else 1
    
    # Convert to minutes
    return numeric_part * time_units.get(unit_part, 0)

def aggregate_data(df, frequency, timestamp_col='TIMESTAMP', input_timescale=None):
    """
    Aggregates the DataFrame into a specified time frequency by averaging numeric values, except for columns
    with '_ETa', '_deltaMM', or '_deltaMVV', which are summed. NSE flags are carried forward, and unique event 
    types are combined into a single string.

    Args:
        df (pd.DataFrame): The DataFrame to be aggregated.
        frequency (str): The frequency to aggregate by (e.g., 'H' for hourly, 'D' for daily).
        timestamp_col (str): The name of the timestamp column. Defaults to 'TIMESTAMP'.
        input_timescale (str): Optional. The input timescale provided by the user.

    Returns:
        pd.DataFrame: The aggregated DataFrame.
    """
    # Ensure timestamp column is in datetime format
    df[timestamp_col] = pd.to_datetime(df[timestamp_col])

    # Fallback dictionary for input timescales
    fallback_timescale_dict = {
        "Min5": "5T",
        "Min15": "15T",
        "Min60": "1H",
        "Daily": "1D"
    }

    # Detect the actual frequency of the input data
    detected_timescale = pd.infer_freq(df[timestamp_col])
    print(f"Inferred input data frequency: {detected_timescale}")  # Print the detected frequency for debugging

    # If frequency cannot be inferred, fall back to input_timescale or fallback dictionary
    if detected_timescale is None:
        if input_timescale in fallback_timescale_dict:
            detected_timescale = fallback_timescale_dict[input_timescale]
            print(f"Using fallback timescale for '{input_timescale}': {detected_timescale}")
        elif input_timescale is not None:
            detected_timescale = input_timescale
            print(f"Using provided input_timescale: {detected_timescale}")
        else:
            raise ValueError("Could not infer the frequency of the input data. Please check the TIMESTAMP column, or ensure that the lysimeter filename contains 'Min5', 'Min15', 'Min60', or 'Daily'.")

    # Convert custom frequency strings (e.g., Min15) to valid pandas offset aliases (e.g., 15T)
    frequency = fallback_timescale_dict.get(frequency, frequency)

    # Convert both detected_timescale and frequency to minutes for comparison
    detected_minutes = convert_to_minutes(detected_timescale)
    frequency_minutes = convert_to_minutes(frequency)

    # Check if the user is trying to downsample to a smaller timescale
    if detected_minutes > frequency_minutes:
        raise ValueError(f"Cannot aggregate to a smaller timescale than the input timescale. "
                         f"Input timescale: {detected_timescale}, requested frequency: {frequency}")

    # Set the timestamp column as the index for resampling
    df = df.set_index(timestamp_col)

    # Define aggregation rules
    agg_dict = {}
    for col in df.columns:
        if '_NSE' in col and df[col].dtype != 'object':
            # Use 'max' to carry forward the NSE flag if any exists in the period for numeric NSE columns
            agg_dict[col] = 'max'
        elif '_NSE_Type' in col:
            # Combine unique event types into a comma-separated string
            agg_dict[col] = lambda x: ', '.join(sorted(set(x.dropna())))
        elif pd.api.types.is_numeric_dtype(df[col]):
            # For columns with '_ETa', '_deltaMM', or '_deltaMVV', sum the values
            if any(keyword in col for keyword in ['_ETa', '_deltaMM', '_deltaMVV']):
                agg_dict[col] = 'sum'
            else:
                # For other numeric columns, use 'mean' for average
                agg_dict[col] = 'mean'
        else:
            # For non-numeric columns, take the first non-null entry
            agg_dict[col] = 'first'

    # Resample the dataframe based on the frequency and aggregation rules
    df_resampled = df.resample(frequency).agg(agg_dict).reset_index()

    return df_resampled