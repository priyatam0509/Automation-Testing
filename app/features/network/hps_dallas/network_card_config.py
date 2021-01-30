from app import system, mws, Navi

from app.features.network.core.network_card_config import NetworkCardConfiguration as CoreNCC

class NetworkCardConfiguration(CoreNCC):
    """
    The class extends the core Network Card Configuration class.
    This class is specific to Dallas brand.
    """

    @staticmethod
    def navigate_to():
        """
        Navigates to the Card Info Editor menu.
        Args:
            None
        Returns:
            Returns the result of execution of Navi.navigate_to()
        """
        return Navi.navigate_to("Card Info Editor")

    def change(self, config):
        """
        Changes the configuration of the Card Info Editor.

        Args:
            config: The dictionary of values being added.

        Returns:
            True: If the values were successfully set.
            False: If the values could not be changed.
            
        Examples:
            /code
            nc_info = {
                "Card Information" : {
                    "AMEX" : {
                        "Accept Card" : 'Yes',
                        "Crind Fallback" : 'Yes',
                        "Floor Limit" : '50',
                        "CRIND Pre-Auth Amount" : '50.00',
                        "Shut Off Limit" : '50',
                        "ZIP Code Prompt At CRIND" : 'No',
                        "ZIP Code Prompt on Manual Entry" : 'No',
                        "Response Auth" : 'HOST RSP'
                    },
                    "VISA" : {
                        "Accept Card" : 'Yes',
                        "Crind Fallback" : 'No',
                        "Floor Limit" : '50',
                        "CRIND Pre-Auth Amount" : '1.00',
                        "Shut Off Limit" : '50',
                        "ZIP Code Prompt At CRIND" : 'No',
                        "ZIP Code Prompt on Manual Entry" : 'No',
                        "Response Auth" : 'HOST RSP'
                    }
                }
            }
            nc = network_card_config.NetworkCard()
            if not nc.add(nc_info):
                tc_fail("Could not add the configuration")
            True
            /endcode
    Example 2:
        /code
        nc_info = {
            "WEX PL" : {
                "Receipt Name" : 'WEX PL',
                "Mask   690046" : ''
            }
        }
        nc = network_card_config.NetworkCard()
        if not nc.add(nc_info):
            tc_fail("Could not add the configuration")
        True
        /endcode
    """
        #Select the card we're configuring
        for tab in config:
            #"Card Information"
            if not mws.select_tab(tab):
                self.log.error(f"Could not select tab with the name {tab}.")
                system.takescreenshot()
                return False
            
            for key, value in config[tab].items():
                #Key = "AMEX", Value = {"Accept Card" : 'Yes', ...}
                #Key = "Receipt Name", Value = "WEX PL"
                if type(value) is dict:
                    cardlist = mws.get_value("Card List", tab = "Card Information")
                    mws.set_value("Card List", cardlist[1])
                    if not mws.set_value("Card List", key):
                        self.log.error(f"Failed to find card, {key}, in the list")
                        system.takescreenshot()
                        return False
                    #Field = "Accept Card"
                    #FieldValue = "Yes"
                    for field, field_value in value.items():
                        if not mws.set_value(field, field_value):
                            self.log.error(f"Could not set {field} with {field_value}")
                            system.takescreenshot()
                            return False
                elif not mws.set_value(key, value):
                    self.log.error(f"Could not set {key} with {value}")
                    system.takescreenshot()
                    return False
        try:
            mws.click_toolbar("Save", main = True)
            return True
        except:
            self.log.error("Failed to navigate back to Splash Screen")
            error_msg = mws.get_top_bar_text()
            if error_msg is not None:
                self.log.error(f"Error message: {error_msg}")
                system.takescreenshot()
            return False