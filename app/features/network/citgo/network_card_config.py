from app import system, mws, Navi

from app.features.network.hps_dallas.network_card_config import NetworkCardConfiguration as HPDNetworkCardConfiguration

class NetworkCardConfiguration(HPDNetworkCardConfiguration):
    """
    The class extends HPS Dallas Network Card Configuration class.
    This class is specific to Citgo brand.
    """

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
                    "Citgo Plus" : {
                        "Response Auth" : 'Card ID'
                    },
                    "EBT Cash" : {
                        "Response Auth" : 'ON Trans '
                    }
                }
            }
            nc = network_card_config.NetworkCard()
            if not nc.add(nc_info):
                tc_fail("Could not add the configuration")
            True
            /endcode
        """

        for card in config:
            if not mws.set_value("Card List", card):
                    self.log.error(f"Failed to find card {card}, in th list")
                    system.takescreenshot()
                    return False
            #Select the card we're configuring
            for key, value in config[card].items():
                #Key = "Response Auth", Value = "Card ID"
                if not mws.set_value(key, value):
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