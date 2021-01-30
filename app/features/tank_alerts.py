from app import mws
from app import Navi, system
import logging, time

class TankAlerts:
    def __init__(self):
        self.log = logging.getLogger()
        TankAlerts.navigate_to()

    @staticmethod
    def navigate_to():
        """
        Navigates to the Tank Alerts feature module.
        Args: None
        Returns: Returns the result of execution of Navi.navigate_to()
        """
        return Navi.navigate_to("tank alerts")

    def configure(self, tank_number, low_level, reorder_level):
        """
        Changes the fields in the Tank Alerts feature module.
        Args:
            tank_number: (Str) The identification number to select from the Tanks list.
            low_level: (Str) The number to input into the "Low Level Alert" field.
            reorder_level: (Str) The number to input into the "Reorder Level Alert" field.
        Returns:
            bool: True/False success condition
        Example:
        ta = tank_alerts.TankAlerts()
        ta.configure("1","500","1000")
        True
        """
        # Find tank in list
        if not mws.set_value("Tanks", tank_number):
            self.log.error(f"Could not find tank number {tank_number} in list.")
            return False
        # Set values and save
        mws.set_value("Low Level Alert", low_level)
        mws.set_value("Reorder Level Alert", reorder_level)
        mws.click("Update List")
        msg = mws.get_top_bar_text()
        if msg:
            self.log.error(f"Got an unexpected message when trying to update tank alerts: {msg}")
            mws.click_toolbar("Exit", main=True)
            return False
        # Verify values were set correctly
        for tank in mws.get_value("Tanks"):
            if tank[0] == tank_number:
                self.log.debug("Checking fields for correct values...")
                if tank[4] != low_level or tank[5] != reorder_level:
                    self.log.error(f"Could not successfully configure tank alerts.")
                    return False
        self.log.debug("Field verification passed.")

        try:
            mws.click_toolbar("Save", main=True)
        except mws.ConnException:
            msg = mws.get_top_bar_text()
            self.log.error(f"Didn't return to main menu after saving tank alerts. Current top bar text: {msg}")
            return False

        return True