from app import Navi, system, mws
import logging

class CardConfiguration:
    """
    The class representing the Card Configuration
    window in Set Up -> Network Menu -> InComm section of MWS.


    The class has a setup method that edits the Card Configuration
    according to the configuration dictionary provided by user.
    """

    def __init__(self):
        """
        Set up mws connection.
        """
        self.log = logging.getLogger()
        CardConfiguration.navigate_to()
        return

    @staticmethod
    def navigate_to():
        """
        Navigates to the Card Configuration menu.
        Args:
            None
        Returns:
            Returns the result of execution of Navi.navigate_to()
        """
        return Navi.navigate_to("Card Configuration")
    
    def add(self, params):
        """
        Adds new entry or entries to the Card Configuration according to the provided
        dictionary or list of dictionaries.

        If the entry with the given name already exists, the data will be overwritten based
        on the information from the user dictionary.
    
        Args:
        params: the list/dictionary with the information about the entries that need to be configured.
            This will need to be setup according to the schema in controls.json.
        
        Returns:
            True: If Card Configuration was successfully set up.
            False: If something went wrong while setting up Card Configuration (will be logged).
        
        Example:
            >>> params = {
                "Card Name": "Test Card 1",
                "IIN": "123456789",
                "CRIND Auth Request Amount": "5.00",
                "Fuel Discount Group": "NONE"
            }
            >>> add(params)
                True
            
            # Assuming Fuel Discount Group "Test Fuel Discount" was added
            >>> params = {
                "Card Name": "Test Card 2",
                "IIN": "321654987",
                "Fuel Discount Group": "Test Fuel Discount"
            }
            >>> add(params)
                True

            >>> params = [
                {
                    "Card Name": "Test Card 3",
                    "IIN": "357951239"
                },
                {
                    "Card Name": "Test Card 4",
                    "IIN": "465321789"
                }
            ]
            >>> add(params)
                True
            
            >>> params = {
                "Card Name": "Test Card 5",
                "IIN": "321654987"
            }

            >>> add(params)
                Unable to save Card Configuration
                Unexpected top bar message: 'Enter Card IIN. This is the card prefix used for routing. Selected range is in conflict with another card.'
                False

            >>> params = {
                "Card Name": "Test Card 4",
                "IIN": "123987456"
            }
            >>> add(params)
                True
        """
        if type(params) is dict:
            params = [params]

        for entry in params:
            # entry = {
            #     "Card Name": "Test Card 1",
            #     "IIN": "123456789",
            #     "CRIND Auth Request Amount": "5.00",
            #     "Fuel Discount Group": "NONE"
            # }

            # Check if the entry already exists
            if not mws.select("Card List", entry["Card Name"]):
                # If not, add new entry
                mws.click_toolbar("Add")

            for key, value in entry.items():
                # "Card Name": "Test Card 1"
                if not mws.set_value(key, value):
                    self.log.error(f"Unable to set the field '{key}' with '{value}'")
                    return False
        
        try:
            mws.click_toolbar("Save", main=True, main_wait=3)
        except:
            # Check for top bar message
            top_bar_message = mws.get_top_bar_text()
            self.log.error("Unable to save Card Configuration")
            if top_bar_message:
                self.log.error(f"Unexpected top bar message: '{top_bar_message}'")
                system.takescreenshot()
            
            return False

        return True

    def delete(self, params):
        """
        Deltes the entries in the Card Configuration window according to the provided
        list.
    
        Args:
        params: the dictionary with the information about
            fields that need to be configured.
            This will need to be setup according to the schema in controls.json.
        
        Returns:
            True: If Card Configuration was successfully set up.
            False: If something went wrong while setting up Card Configuration (will be logged).
        
        Example:
            # Assuming 'Test Card 1', 'Test Card 2', 'Test Card 3' exist in Card Configuration
            >>> params = 'Test Card 1'
            >>> delete(params)
                True
            >>> params = ['Test Card 2', 'Test Card 2']
            >>> delete(params)
                True
            >>> params = 'Something that is not there'
            >>> delete(params)
                Unable to remove 'Something that is not there' because it was not found in the list.
                False
        """
        if type(params) is str:
            params = [params]

        for entry in params:
            # entry = "Test Card 1"

            if not mws.select("Card List", entry):
                self.log.error(f"Unable to remove '{entry}' because it was not found in the list.")
                return False

            if not mws.click_toolbar("Delete") or not mws.click_toolbar("YES"):
                self.log.error(f"Unable to click 'Delete' to remove '{entry}'")
                return False
        
        try:
            mws.click_toolbar("Save", main=True, main_wait=3)
        except:
            # Check for top bar message
            top_bar_message = mws.get_top_bar_text()
            self.log.error("Unable to save Card Configuration")
            if top_bar_message:
                self.log.error(f"Unexpected top bar message: '{top_bar_message}'")
                system.takescreenshot()
            
            return False

        return True