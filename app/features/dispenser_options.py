from app import mws, Navi
import logging, time

class DispenserOptions:
    """
    The class representing the Dispenser Options
    window in Set Up -> Forecourt section of MWS.

    The class provides the setup method that allows
    to confiugre various fields for different dispensers
    with the config provided by user.
    """

    def __init__(self):
        self.log = logging.getLogger()
        DispenserOptions.navigate_to()
        return
    
    @staticmethod
    def navigate_to():
        """
        Navigates to the Dispenser Options menu.
        Args:
            None
        Returns:
            Returns the result of execution of Navi.navigate_to()
        """
        return Navi.navigate_to("Dispenser Options")


    def setup(self, params):
        """
        Configures various fields for the dispensers
        based on the params dictionary.
        Returns True if the operation is a success, otherwise returns False.
        Params dictionary should include the Mode list for correct configuration.
        Args:
            params: (dictionary) the dictionary with parameters used for configuration
                    This will need to be setup according to the schema in controls.json.
        Returns:
            True: if the operations is performed without errors
            False: if there were errors in the process
        Example:
            params = {
                "Mode" : ["Primary", "Secondary"],
                "Dispensers" : {
                    "1 P" : {
                                "Modes": "Unattended",
                                "Service Level": "SELF",
                                "General Authorization": True,
                                "PrePay Only": True,
                                "Pre-Authorization Time Out": 120,
                                "Allow Outdoor Presets": True,
                                "Enable Unattended Operation": True,
                                "Payment Mode": "Payment First",
                            },
                    "2 S" : {
                                "Modes": "Semi-Attended",
                                "Service Level": "SELF",
                                "General Authorization": True,
                                "Pre-Authorization Time Out": 120,
                                "Allow Outdoor Presets": True,
                                "Enable Unattended Operation": True,
                                "Payment Mode": "Payment First",
                            }
                }
            }

            >>> setup(params)
                True
        """
        error = False

        # Set modes
        for mode in params["Mode"]:
            mws.select_checkbox(mode)
        
        # Iterate over individual dispensers
        for dispenser, config in params["Dispensers"].items():
            # Select the dispenser in the list and double click it
            # to enable editing
            mws.get_control("Top List").select(dispenser).click(double=True)

            time.sleep(1)

            # Setup fields
            for key, value in config.items():
                # "Modes": "Semi-Attended"
    
                if not mws.set_value(key, value):
                    self.log.error(f"Unable to set field '{key}' with '{value}'")
                    error = True
                    continue

            time.sleep(1)

            # Apply changes
            if not mws.click("Update List"):
                self.log.error(f"Unable to sava the changes to the dispenser '{dispenser}'")
        
        # Click Save
        try:
            if not mws.click_toolbar("Save", main=True):
                self.log.error("Unable to save Dispenser Options")
                error = True
        except mws.ConnException:
            self.log.error(f"Didn't return to main menu after saving Dispenser Options. Top bar message: {mws.get_top_bar_text()}")
            error = True
        
        if error:
            self.log.error("There were errors in the process of configuring Dispenser Options")
            return False
        
        return True

    def _check_top_bar_msg(self, msg="", wait=10):
        """
        Private method that makes sure that the top bar contains
        the text that mathces the given msg after the time defined by wait param.
        Args:
            msg: (string) the message the top bar should match
            wait: (int) a time in seconds after which the the top bar will be checked
        
        Returns:
            True: if the top bar message matched the given msg
            False: if the top bar message did not match the given msg
        """
        time.sleep(wait)

        self.log.debug(f"The top bar message is \'{mws.get_top_bar_text()}\'")
        self.log.debug(f"The return from check_msg is \'{mws.get_top_bar_text() == msg}\'")
        return mws.get_top_bar_text() == msg
