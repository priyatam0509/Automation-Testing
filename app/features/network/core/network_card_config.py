from app import system, mws, Navi
import logging

class NetworkCardConfiguration:
    """
    Core network card config feature class. Supports Concord network. To be extended and overridden for other networks
    where needed.
    """
    def __init__(self):
        self.tab_bbox = (177, 143, 397, 170)
        self.log = logging.getLogger()
        self.navigate_to()

    @staticmethod
    def navigate_to():
        """
        Navigates to the Network Card Configuration menu.
        Args:
            None
        Returns:
            Returns the result of execution of Navi.navigate_to()
        """
        return Navi.navigate_to("Network Card Configuration")

    def change(self, config):
        """
        Changes the configuration of the Network Card Configuration.

        Args:
            config: The dictionary of values being added.

        Returns:
            True: If the values were successfully set.
            False: If the values could not be changed.
            
        Examples:
            \code
            nc_info = {
                "Debit":{
                    "Page 1":{
                        "Accept Card": 'Yes',
                        "Inside Floor Limit": '5',
                        "CRIND Floor Limit": '10',
                        "CRIND Authorization Amount": '20'
                        "CRIND Auth Control": 'On Host Response',
                        "AVS Zip Code Prompt": 'None'
                    },
                    "Page 2":{
                        "Can Use As Debit": 'No',
                        "Manual Entry Allowed": 'Yes',
                        "Track Configuration": 'Preferred Track 2',
                        "Signature Required Limit": '10.00'
                    }
                }
            }
            nc = network_card_config.NetworkCard()
            if not nc.add(nc_info):
                tc_fail("Could not add the configuration")
            True
            \endcode
        """
         #Select the card we're configuring
        for card in config:
            if not mws.set_value("Card List", card):
                self.log.error(f"Failed to find card, {card}, in the list")
                system.takescreenshot()
                return False
                
            for tab in config[card]:
                if not mws.select_tab(tab, bboxes=self.tab_bbox):
                    self.log.error(f"Could not select tab with the name {tab}.")
                    system.takescreenshot()
                    return False

                for key, value in config[card][tab].items():
                    if not mws.set_value(key, value, tab):
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