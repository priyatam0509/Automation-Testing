from app.framework import mws
from app.framework import Navi
from app.util import system
import logging

log = logging.getLogger()

class PlayAtPump:
    
    def __init__(self):
        PlayAtPump.navigate_to()
        self.order = ['Enabled']

    @staticmethod
    def navigate_to():
        """
        Navigates to the Play at the Pump Configuration menu.
        Args:
            None
        Returns:
            Returns the result of execution of Navi.navigate_to()
        """
        return Navi.navigate_to("Play at the Pump Configuration")

    def configure(self, config={}):
        """
        Configure data fields in the current menu.
        Args:
            config: (dict) A dictionary of all of the controls that the user wants to setup. 
                    This will need to be setup according to the schema in controls.json.
        Examples:
            >>> config = {
                    'Enabled': 'Yes',
                    'Site ID': '999',
                    'Host IP Address': '10.5.48.6',
                    'Host IP Port': '7900'
                }
            >>> configure(config)
            True
        """
        for field in self.order:
            try:
                value = config[field]
            except KeyError:
                continue
            if not mws.set_value(field, value):
                log.error(f"Could not set {key} with {value}.")
                return False
            del config[field]

        for key, value in config.items():
            if not mws.set_value(key, value):
                log.error(f"Could not set {key} with {value}.")
                return False
        
        try:
            mws.click_toolbar("Save", main=True)
        except mws.ConnException:
            log.error("Did not return to main menu from play at the pump after clicking Save.")

        error_msg = mws.get_top_bar_text()
        if error_msg is not None and error_msg is not '':
            log.error(error_msg)
            system.takescreenshot()
            return False

        return True