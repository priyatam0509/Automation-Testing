from app.framework import Navi, mws
from app.util import system
import logging, time, pywinauto, copy, re

class SecurityCamera:
    """
    The class representing the Security Camera
    window in Set Up -> Store section of MWS.


    The module has a setup method that allows to configure
    the security camera Interface settings.
    """
    # The fields that should have the master field set to a specific value before they can be
    # edited
    FORCE_CHECK_FIELDS = {
        "Stand alone clients use COM" : ["Data will be set via", "COM Port"],
        "Combined server use COM" : ["Data will be set via", "COM Port"],
        "Field Separator" : ["Data Format", "Field Delimited"],
        "Host Name": ["Data will be set via", "TCP"],
        "Host Port": ["Data will be set via", "TCP"]
    }
    
    def __init__(self):
        """
        Set up mws connection.
        """
        self.log = logging.getLogger()
        SecurityCamera.navigate_to()
        return

    @staticmethod
    def navigate_to():
        """
        Navigates to the Security Camera menu.
        Args:
            None
        Returns:
            Returns the result of execution of Navi.navigate_to()
        """
        return Navi.navigate_to("Security Camera")

    def setup(self, params):
        """
        Configures the fields accessible in the
        Security Camera window according to the provided
        dictionary.
    
        Args:
        params: the dictionary with the information about
            fields that need to be configured.
            This will need to be setup according to the schema in controls.json.
    
        Returns:
            True: If Security Camera was successfully set up.
            False: If something went wrong while setting up Security Camera (will be logged).
    
        Example:
            params = {
                "Data will be set via": "COM Port",
                "Stand alone clients use COM": "9", # With COM Port set
                "Combined server use COM": "16", # With COM Port set
                "Data Format": "Field Delimited",
                "Field Separator": "|"
            }

            >>> setup(params)
                True
            >>> setup({""Host Port": "1010", "Data will be set via: "TCP"})
                Could not set Host Port with 1010.
                There were errors in the process of configuring Security Camera Interface.
                False
        """
        error = False

        for key, value in params.items():
            # Example:
            #    key = "Data will be set via"
            #    value = "COM Port"

            if not mws.set_value(key, value):
                self.log.error(f"Could not set {key} with {value}.")
                error = True

        try:
            mws.click_toolbar("Save", main=True, main_wait=3)
        except mws.ConnException:
            # Check for top bar message
            top_bar_message = mws.get_top_bar_text()
            if top_bar_message:
                if top_bar_message == "Do you want to save changes?":
                    mws.click_toolbar("YES")
                    time.sleep(1)
                    mws.click_toolbar("OK")
                else:
                    self.log.error("Unable to save Security Camera Interface")
                    self.log.error(f"Unexpected top bar message is '{top_bar_message}'")
                    system.takescreenshot()
                    mws.click_toolbar("OK")
                    error = True
        
        # Check for errors
        if error:
            self.log.error("There were errors in the process of configuring Security Camera Interface")
            return False
        
        return True