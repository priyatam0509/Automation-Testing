from app.framework import mws, Navi
import logging

class FuelDelivery:

    def __init__(self):
        FuelDelivery.navigate_to()
        self.log = logging.getLogger()

    @staticmethod
    def navigate_to():
        return Navi.navigate_to("Fuel Delivery")

    def set(self, config):
        """
        Sets the Fuel Delivery according to the values of the controls sent by the user.

        Args:
            config: A dictionary of control:value pairs.
        Returns:
            True: If Fuel Delivery can be fully set.
            False: If something in Fuel Delivery could not be set.
        """
        for key, value in config.items():
            if not mws.set_value(key, value):
                self.log.error(f"Could not set {key} to {value}")
                return False
        try:
            mws.click_toolbar("Save", main=True)               
        except mws.ConnException:
            self.log.error(f"Didn't return to main menu after saving Fuel Delivery. Top bar message: {mws.get_top_bar_text()}")
            mws.recover()
            return False
        return True