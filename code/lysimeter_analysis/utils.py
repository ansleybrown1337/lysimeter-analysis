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