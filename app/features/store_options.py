from app.framework import Navi, mws
import logging

class StoreOptions:

    def __init__(self):
        self.log = logging.getLogger()
        StoreOptions.navigate_to()
        return

    @staticmethod
    def navigate_to():
        return Navi.navigate_to("Store Options")

    def setup(self, config):
        """
        Goes through every tab in Store Options and configures them to the 
                     information that the user gives.
        Args:
            config: A dictionary of all of the controls that the user wants to setup. 
                      This will need to be setup according to the schema in controls.json.
        Returns:
            True: If Store Options was successfully set up.
            False: If something went wrong while setting up Store Options (will be logged).
        """
        for tab in config:
            mws.select_tab(tab)
            for key, value in config[tab].items():
                if not mws.set_value(key, value, tab):
                    self.log.error(f"Could not set {key} with {value} on the {tab} tab.")
                    return False
                    
        mws.click_toolbar("Save")
        msg = mws.get_top_bar_text()
        if msg == f"Existing password may no longer be valid!  Continue with save?":
            mws.click_toolbar("Yes", main=True)
        elif msg and "Saving Store Options" not in msg:
            self.log.error(f"Got an unexpected message when saving Store Options: {msg}")
            return False

        return True