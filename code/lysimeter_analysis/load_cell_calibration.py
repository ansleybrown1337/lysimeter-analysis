# lysimeter_analysis/load_cell_calibration.py
'''
A script for handling load cell calibration calculations for lysimeters. 

This script allows users to either use default calibration values for specific
lysimeter types (e.g., SL, LL) or input custom calibration parameters to calculate 
a custom calibration factor.
'''

class LoadCellCalibration:
    """
    A class to handle load cell calibration calculations for lysimeters.
    """

    def __init__(self):
        """
        Initializes the LoadCellCalibration class with default values.
        """
        self.alpha = None
        self.beta = None
        self.custom_calibration_factor = None

        # Default calibration factors (mm/mV/V)
        self.default_calibrations = {
            'SL': 157.43,
            'LL': 76.2
        }

    def set_alpha(self, alpha):
        """
        Sets the alpha value, the load cell conversion coefficient (mV/V to kg).
        
        Args:
            alpha (float): The load cell conversion coefficient (mV/V to kg).
        """
        self.alpha = alpha

    def set_beta(self, beta):
        """
        Sets the beta value, the effective surface area of the lysimeter (m^2).
        
        Args:
            beta (float): The effective surface area of the lysimeter (m^2).
        """
        self.beta = beta

    def calculate_calibration_factor(self):
        """
        Calculates the custom calibration factor based on the alpha and beta values.
        
        Returns:
            float: The custom calibration factor (mm/mV/V).
        """
        if self.alpha is None or self.beta is None:
            raise ValueError("Both alpha (mV/V to kg) and beta (surface area) must be provided for custom calibration.")
        
        # Calculate the calibration factor: α kg/(mV/V) * (1 m^3)/(1000 kg) * (1/β m^2) * (1000 mm)/(1.0 m)
        self.custom_calibration_factor = (self.alpha * (1 / 1000) * (1 / self.beta) * 1000)
        return self.custom_calibration_factor

    def get_calibration_factor(self, lysimeter_type=None):
        """
        Retrieves the calibration factor for the given lysimeter type or the custom calibration.
        
        Args:
            lysimeter_type (str): The lysimeter type ("SL" or "LL"). Optional if custom calibration is set.
        
        Returns:
            float: The calibration factor (mm/mV/V).
        """
        if lysimeter_type and lysimeter_type in self.default_calibrations:
            return self.default_calibrations[lysimeter_type]
        elif self.custom_calibration_factor is not None:
            return self.custom_calibration_factor
        else:
            raise ValueError("Invalid lysimeter type provided or custom calibration not set.")
