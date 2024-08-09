# lysimeter_analysis/utils.py

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
