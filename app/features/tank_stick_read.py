from app.framework import mws, Navi
import logging

class TankStickReading:

    def __init__(self):
        TankStickReading.navigate_to()
        self.log = logging.getLogger()

    @staticmethod
    def navigate_to():
        return Navi.navigate_to("Tank Stick Reading")

    def update(self, tank_item, config):
        """
        Updates the Tank Stick Reading.

        Args:
            tank_item: The specific tank item that needs to be updated.
            config: A dictionary of control:value pairs.

        Returns:
            True: If the Tank Stick Reading was successfully updated.
            False: If something went wrong when updating the Tank Stick Reading.
        """
        self.log.info(f"Updating {tank_item}")
        if not mws.set_value("Tanks", tank_item):
            self.log.error(f"Could not select {tank_item}")
            return False
        for key, value in config.items():
            if not mws.set_value(key, value):
                self.log.error("Could not set {key} to {value}")
                return False
        mws.click("Update List")
        msg = mws.get_top_bar_text()
        if msg:
            self.log.error(f"Got an unexpected message when updating a tank stick reading: {msg}")
            return False
        return True