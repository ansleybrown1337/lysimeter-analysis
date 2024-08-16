# lysimeter_analysis/utils.py
'''
A compilation of utility functions that are used in the lysimeter analysis 
pipeline, but do not fit into any of the other modules per se.
'''

import os
import pandas as pd
from datetime import datetime

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

    


def awat_filter(data, wmax=31, delta_max=0.24):
    """
    TODO: need to figure out parameters and double check this function for
    accurate implementation.
    
    Apply the AWAT filter to the provided data. Derived from:
    Peters, A., Nehls, T., Schonsky, H., and Wessolek, G.: Separating 
    precipitation and evapotranspiration from noise – a new filter routine for 
    high-resolution lysimeter data, Hydrol. Earth Syst. Sci., 18, 1189–1198, 
    https://doi.org/10.5194/hess-18-1189-2014, 2014.

    Args:
        data (pd.Series or np.ndarray): The input data to filter.
        wmax (int): The maximum window size for the Savitzky-Golay filter.
        delta_max (float): The maximum allowable deviation for local maxima.

    Returns:
        np.ndarray: The filtered data.
    """
    filtered_data = np.zeros_like(data)
    n = len(data)

    for i in range(n):
        local_window = min(i, n - i - 1, wmax)
        window_size = 2 * local_window + 1
        order = min(2, window_size - 1)  # Ensure polyorder is less than window_size
        
        # Apply the Savitzky-Golay filter
        if window_size > 1:
            filtered_value = savgol_filter(data[max(i-local_window, 0):i+local_window+1], window_size, order)[local_window]
        else:
            filtered_value = data[i]

        # Check for the deviation condition
        if abs(data[i] - filtered_value) < delta_max:
            filtered_data[i] = data[i]
        else:
            filtered_data[i] = filtered_value

    return filtered_data
