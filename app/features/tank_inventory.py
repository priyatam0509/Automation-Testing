from app import mws, system, Navi
import logging, copy, re, time

class TankInventory:
    """
    The class representing the Tank Inventory
    window in Set Up -> Forecourt section of MWS.


    The class has a setup method that allows to perform
    Fuel Inventory Adjustment based on the user configuration
    dictionary.
    """
    def __init__(self):
        """
        Set up mws connection.
        """
        self.log = logging.getLogger()
        TankInventory.navigate_to()
        return


    @staticmethod
    def navigate_to():
        """
        Navigates to the Tank Inventory menu.
        Args:
            None
        Returns:
            Returns the result of execution of Navi.navigate_to()
        """
        return Navi.navigate_to("Tank Inventory")
    
    def adjust(self, params):
        """
        Configures the fields accessible in the
        Tank Inventory window according to the provided
        dictionary.
    
        Args:
        params: the dictionary with the information about
            fields that need to be configured.
            This will need to be setup according to the schema in controls.json.
    
        Returns:
            True: If Tank Inventory was successfully set up.
            False: If something went wrong while setting up Tank Inventory (will be logged).
    
        Example:
            params = {
                "Entry" : ['1', 'REGULAR'], # However many parameters that can serve as selection criteria,
                "Date" : "07/05/2019",
                "Operator" : "Area Manager",
                "Time": "08:56:07 AM",
                "Adjusted Level": "1000",
                "Reason for Adjustment": "Calibration"
            }
        """
        params = copy.deepcopy(params)
        if not mws.select("Tanks", params["Entry"]):
            self.log.error("Failed to select the requested tank")
            return False
        
        del params["Entry"]

        error = False
        for key, value in params.items():
            if key == "Time":
                # Check that it is a valid time
                if not re.match(r'^\d{1,2}:\d{2}:\d{2} [AP]M$', value):
                    self.log.error(f"Invalid time '{value}' is provided")
                    error = True
                
                time_str, period_str = value.split(' ')
                mws.set_value("Time", time_str)
                mws.get_control("Time").type_keys('{VK_RIGHT}%s'%period_str)

                # Check
                if mws.get_value("Time")[0] != value:
                    self.log.error(f"Unable to set the time to '{value}'")
                    error = True

            elif not mws.set_value(key, value):
                self.log.error(f"Failed to set the field '{key}' with value '{value}'")
                error = True

        mws.click("Update List")

        # Check for top bar message
        time.sleep(1)
        top_bar_message = mws.get_top_bar_text()
        if top_bar_message:
            self.log.error(f"Unexpected top bar message is '{top_bar_message}'")
            system.takescreenshot()
            error = True
        
        # Check for errors
        if error:
            self.log.error("There were errors in the process of configuring of Tank Inventory")
            return False
        else:
            return mws.click_toolbar("Save", main=True, main_wait=3)
        
        return True
