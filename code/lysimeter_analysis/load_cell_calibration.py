# lysimeter_analysis/load_cell_calibration.py

from colorama import Fore, Style, init

# Initialize colorama for colored output
init()

class LoadCellCalibration:
    def __init__(self):
        self.alpha = 684.694  # Default value for LL
        self.beta = 9.181      # Default value for LL
        self.calibration_factor = (self.alpha * 1000) / (self.beta * 1000)
        self.lysimeter_type = 'LL (default)'
        self.custom_values_provided = False  # Flag to track if custom values were provided

    def set_alpha(self, alpha):
        self.alpha = alpha
        self.custom_values_provided = True
        self._update_calibration_factor()

    def set_beta(self, beta):
        self.beta = beta
        self.custom_values_provided = True
        self._update_calibration_factor()

    def _update_calibration_factor(self):
        self.calibration_factor = (self.alpha * 1000) / (self.beta * 1000)

    def get_calibration_factor(self, lysimeter_type=None):
        if lysimeter_type == 'SL':
            self.alpha = 368.538
            self.beta = 2.341
            self.lysimeter_type = 'SL'
        elif lysimeter_type == 'LL':
            self.alpha = 684.694
            self.beta = 9.181
            self.lysimeter_type = 'LL'
        else:
            self.lysimeter_type = 'Custom'
            if not self.custom_values_provided:
                print(Fore.YELLOW + "Warning: Custom alpha and/or beta not provided. Default values are being used. Please see the report for details." + Style.RESET_ALL)

        self._update_calibration_factor()
        return self.calibration_factor

    def calculate_calibration_factor(self):
        self._update_calibration_factor()
        return self.calibration_factor

