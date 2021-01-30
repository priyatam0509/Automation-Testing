from app import Navi, system, mws
import logging

class SiteConfiguration:
    """
    The class representing the Site Configuration
    window in Set Up -> Network Menu -> InComm section of MWS.


    The class has a setup method that edits the Site Configuration
    according to the configuration dictionary provided by user.
    """

    def __init__(self):
        """
        Set up mws connection.
        """
        self.log = logging.getLogger()
        SiteConfiguration.navigate_to()
        return

    @staticmethod
    def navigate_to():
        """
        Navigates to the Site Configuration menu.
        Args:
            None
        Returns:
            Returns the result of execution of Navi.navigate_to()
        """
        return Navi.navigate_to("Site Configuration")
    
    def setup(self, params):
        """
        Configures the fields accessible in the
        InComm Network Site Parameters window according to the provided
        dictionary.
    
        Args:
        params: the dictionary with the information about
            fields that need to be configured.
            This will need to be setup according to the schema in controls.json.
    
        Returns:
            True: If InComm Network Site Parameters was successfully set up.
            False: If something went wrong while setting up InComm Network Site Parameters (will be logged).
    
        Example:
            params = {
                "Primary Host IP Address": "127.0.0.1",
                "Primary Host IP Port": "5001",
                "Site ID": "00000",
                "Merchant/Retailer ID": "123456789",
                "Print store copy of the receipt inside": "Yes", # Or 'No'
                "Print customer copy of the receipt inside": "Yes", # Or 'No'
            }

            >>> setup(params)
                True
        """
        error = False
        for key, value in params.items():
            if not mws.set_value(key, value):
                self.log.error(f"Unable to set the field '{key}' with {value}")
                error = True
        
        try:
            mws.click_toolbar("Save", main=True, main_wait=5)
        except:
            # Check for top bar message
            top_bar_message = mws.get_top_bar_text()
            if top_bar_message:
                system.takescreenshot()
                self.log.error("Unable to save Site Configuration")
                self.log.error(f"Unexpected top bar message is '{top_bar_message}'")
                error = True
        
        # Check for errors
        if error:
            self.log.error("There were errors in the process of configuring Site Configuration")
            return False
        
        return True