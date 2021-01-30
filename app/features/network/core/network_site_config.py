from app import mws, Navi
import logging

class NetworkSetup:
    """
    Core Network Setup class. Supports Concord. To be extended and overridden by other networks
    where needed.
    """
    def __init__(self):
        self.log = logging.getLogger()
        self.navigate_to()

    @staticmethod
    def navigate_to():
        """
        Navigates to the Network Site Configuration menu.

        Returns:
            Returns the result of execution of Navi.navigate_to()
        """
        return Navi.navigate_to("Network Site Configuration")

    def configure_network(self, config={}):
        """
        Configure the Network Site Configuration menu
        
        Args:
            config: (dict) A dictionary of all of the controls that the user wants to setup. 
                    This will need to be setup according to the schema in controls.json.
        
        Examples:
            >>> cfg = {'General': {'Enabled': 'Yes', 'Host IP Address': '10.5.48.6', 'Port Number': '7900', 'Site Identifier': '1', 'Page2': {'Loyalty Vendor': 'Kickback Points'}}, 'Receipts': {'Outside offline receipt line 2': 'a receipt line'}}
            >>> configure_network(**cfg)
                True
        """
        if not self.configure_fields(config):
            return False
        try:
            mws.click_toolbar("Save", main=True, main_wait=30)
        except mws.ConnException:
            msg = mws.get_top_bar_text()
            self.log.error(f"Failed to save network configuration. Passport message: {msg}")
            return False

        return True

    def configure_fields(self, config={}, tab=[]):
        """
        Configure data fields in the current menu. Uses recursion to handle tabs and subtabs.
        Helper function to configure_network.
        
        Args:
            tab: (list) The tab to configure.
            config: (dict) A dictionary of all of the controls that the user wants to setup. 
                    This will need to be setup according to the schema in controls.json.
        """
        if tab != []:
            if type(tab) is not list:
                tab = [tab]
            mws.select_tab(tab[-1])
        for key, value in config.items():
            if type(value) is dict:
                tab.append(key)
                if not self.configure_fields(value, tab):
                    return False
                tab.remove(key)
            elif not mws.set_value(key, value, tab):
                self.log.error(f"Could not set {key} with {value} on the {tab} tab.")
                return False
        return True