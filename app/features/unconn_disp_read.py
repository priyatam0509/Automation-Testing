from app.framework import mws, Navi
import logging

class UnconnectedDispenserReadings:

    def __init__(self):
        UnconnectedDispenserReadings.navigate_to()
        self.log = logging.getLogger()

    @staticmethod
    def navigate_to():
        return Navi.navigate_to("Unconnected Dispenser Readings")

    def setup(self, dispenser_number, config):
        """
        Sets up the Unconnected Dispenser Readings GUI to the user defined settings.

        Args:
            dispenser_number: The number of the dispenser that needs to be set up.
            config: A dictionary of control:value pairs.

        Returns:
            True: If the unconnected dispenser was successfully set up.
            False: If something went wrong while setting up the unconnected dispenser.
        """
        if not mws.set_value("Dispenser Number", dispenser_number):
            self.log.error(f"Could not selected the {dispenser_number} dispenser.")
            return False
        for key, value in config.items():
            if not mws.set_value(key, value):
                self.log.error(f"Could not set {key} to {value}.")
                return False
        mws.click("Update List")
        return True