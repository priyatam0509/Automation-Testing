from app import system, mws
from app.features.network.core.network_site_config import NetworkSetup as CoreNetworkSetup

class WorldpayNetworkSetup(CoreNetworkSetup):
    """
    The class extends general NetworkSiteConfiguration class.
    This class is specific to Worldpay brand.
    """

    #Pulled directly from loyalty module
    def configure_fields(self, tab=[], config={}):
        """
        Configure data fields in the current menu. Uses recursion to handle tabs and subtabs.
        Args:
            tab: (list) The tab to configure.
            config: (dict) A dictionary of all of the controls that the user wants to setup. 
                    This will need to be setup according to the schema in controls.json.
        Examples:
            >>> cfg = {'General': {'Enabled': 'Yes', 'Host IP Address': '10.5.48.6', 'Port Number': '7900', 'Site Identifier': '1', 'Page2': {'Loyalty Vendor': 'Kickback Points'}}, 'Receipts': {'Outside offline receipt line 2': 'a receipt line'}}
            >>> configure_fields(**cfg)
            True
        """
        if tab != []:
            if type(tab) is not list:
                tab = [tab]
            mws.select_tab(tab[-1])
        for key, value in config.items():
            if key is "EMV Parameters":
                if not self.configure_emv_params(value):
                    return False
            elif type(value) is dict:
                tab.append(key)
                if not self.configure_fields(tab, **value):
                    return False
                tab.remove(key)
            elif not mws.set_value(key, value, tab):
                self.log.error(f"Could not set {key} with {value} on the {tab} tab.")
                return False
        return True

    def configure_emv_params(self, config):
        """
        Helper function that deals with the unique listbox in the EMV Parameters tab.
        """
        # 'config' is the dict value of "EMV Parameters"
        for key, value in config.items():
            if not mws.set_value("Card List", key):
                self.log.error(f"Could not find {key} in card list.")
                return False
            if not self.configure_fields(config = value):
                return False
        return True