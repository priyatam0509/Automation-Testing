from app import mws, system, Navi
import logging

class FuelDiscountConfiguration:
    """
    Core fuel discount config feature class. Supports Concord network. To be extended and overridden for other networks
    where needed.
    """
    def __init__(self):
        self.log = logging.getLogger()
        self.navigate_to()

    @staticmethod
    def navigate_to():
        return Navi.navigate_to("Fuel Discount Configuration")
    
    def change(self, config):
        """
        Changes the configuration of the Fuel Discount Configuration.

        Args:
            config: The dictionary of values being added.

        Returns:
            True: If the values were successfully set.
            False: If the values could not be changed.
            
        Examples:
            \code
            fd_info = {
                "Gulf": "NONE",
                "JCB": "NONE"
                }
            fd = fuel_disc_config.FuelDiscount()
            if not fd.change(fd_info):
                mws.recover()
                tc_fail("Could not set the configuration")
            True
            \endcode
        """
        #Select the card we're configuring
        for card in config:
            if not mws.set_value("Cards", card):
                self.log.error(f"Failed to find card, {card}, in the list")
                system.takescreenshot()
                return False

            if not mws.set_value("Discount Group", config[card]):
                self.log.error(f"Could not set Discount Group with {config[card]}")
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