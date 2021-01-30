from app.framework import mws, Navi
import logging

log = logging.getLogger()

class NetworkSetup:
    
    def __init__(self):
        mws.create_connection()
        return

    #Pulled directly from loaylty module
    def configure_fields(self, tab=[], config={}):
        """
        Configure data fields in the current menu. Uses recursion to handle tabs and subtabs.
        Helper function to add_provider and change_provider.
        Args:
            tab: (list) The tab to configure.
            config: (dict) A dictionary of all of the controls that the user wants to setup. 
                    This will need to be setup according to the schema in controls.json.
        Examples:
            >>> cfg = {'General': {'Enabled': 'Yes', 'Host IP Address': '10.5.48.6', 'Port Number': '7900', 'Site Identifier': '1', 'Page2': {'Loyalty Vendor': 'Kickback Points'}}, 'Receipts': {'Outside offline receipt line 2': 'a receipt line'}}
            >>> configure_fields(cfg)
            True
        """
        if tab != []:
            if type(tab) is not list:
                tab = [tab]
            mws.select_tab(tab[-1])
        for key, value in config.items():
            if type(value) is dict:
                tab.append(key)
                if not self.configure_fields(tab, value):
                    return False
                tab.remove(key)
            elif not mws.set_value(key, value, tab):
                log.error(f"Could not set {key} with {value} on the {tab} tab.")
                return False
        return True