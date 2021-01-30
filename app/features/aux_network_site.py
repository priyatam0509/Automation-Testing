from app import mws, Navi
import logging, time

class AuxiliaryNetworkSiteConfig:
    def __init__(self):
        self.log = logging.getLogger()
        AuxiliaryNetworkSiteConfig.navigate_to()

    @staticmethod
    def navigate_to():
        """
        Navigates to the Auxiliary Network Site Configuration feature module.
        Args: None
        Returns: Returns the result of execution of Navi.navigate_to()
        """
        return Navi.navigate_to("Auxiliary Network Site Configuration")

    def configure(self, config):
        """
        Configures fields in the Auxiliary Network Site Configuration feature module.
        Args:
            config: A dictionary of controls so the user can add the information that
                    they need to. This is according to the schema in controls.json.
        Returns:
            bool: Success/Failure
        Example: 
            ansc_info = {
                "Com Port": "1",
                "Baud Rate": "9600",
                "Data bits": "4", # "cannot be less than" 4, not exceed 8
                "Stop Bit": "2",
                "Parity Bit": "No Parity",
                "ACK Timer": "5000", #cannot be less than 1
                "Response Timer": "60000",
                "NAK Quantity": "5",
                "Comm Test Timer Polling": "10000",
                "Site ID": "123456789",
                "Print store copy of the receipt inside": "Yes",
                "Print customer copy of the receipt inside": "No"
            }

            ansc = aux_network_menu.AuxiliaryNetworkSiteConfig()
            ansc.configure(ansc_info)
            True
        """
        # Set each field
        for key, value in config.items():
            if not mws.set_value(key, value):
                self.log.error(f"Could not '{key}' to '{value}'.")
                return False
        # Check fields for correct values
        self.log.debug("Rechecking fields for correct values...")
        for key, intended_value in config.items():
            current_value = mws.get_value(key)
            if type(current_value) != list:
                current_value = [current_value] #force to list so next line works correctly
            # Combo box controls return a list of possible values with the
            # currently selected option as the first index
            if current_value[0] != intended_value:
                self.log.error(f"'{key}' control was not set correctly.")
                return False
        # Save and check for errors
        mws.click_toolbar("Save")
        errormessage = mws.get_top_bar_text()
        if "cannot be less than" in errormessage or "cannot exceed" in errormessage:
            self.log.error(errormessage)
            self.log.error("Some part of your configuration was incorrect.")
            return False
        return True