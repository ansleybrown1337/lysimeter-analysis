# lysimeter_analysis/load_cell_calibration.py

from colorama import Fore, Style, init

# Initialize colorama for colored output
init()

class LoadCellCalibration:
    def __init__(self):
        self.alpha = None
        self.beta = None
        self.calibration_factor = None
        self.lysimeter_type = None
        self.custom_values_provided = False  

    def set_alpha(self, alpha):
        self.alpha = alpha
        self.custom_values_provided = True
        self._update_calibration_factor()

    def set_beta(self, beta):
        self.beta = beta
        self.custom_values_provided = True
        self._update_calibration_factor()

    def _update_calibration_factor(self):
        if self.alpha is not None and self.beta is not None:
            self.calibration_factor = (self.alpha * 1000) / (self.beta * 1000)
        else:
            self.calibration_factor = None

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
                self._print_default_values_warning()
                self.lysimeter_type = 'LL (default)'
                self.alpha = 684.694
                self.beta = 9.181

        self._update_calibration_factor()
        return self.calibration_factor

    def _print_default_values_warning(self):
        """
        Prints a warning message when neither a lysimeter type nor custom alpha and beta
        values are provided.
        """
        print(
            Fore.YELLOW + 
            "Warning: No lysimeter type or custom alpha/beta values provided. "
            "Default LL values are being used. Please see the report for details." + 
            Style.RESET_ALL
        )

    def calculate_calibration_factor(self):
        self._update_calibration_factor()
        return self.calibration_factor
