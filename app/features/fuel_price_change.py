from app.framework import mws, Navi
import logging

class FuelPriceChange:

    def __init__(self):
        self.log = logging.getLogger()
        FuelPriceChange.navigate_to()

    @staticmethod
    def navigate_to():
        return Navi.navigate_to("Fuel Price Change")

    # TODO: A method to configure multiple prices in one call
    def change_prices(self, fuel_item, price):
        """
        Changes the price to the specified fuel item.

        Args:
            fuel_item: The specific fuel item that the user would like to change the price to.
            price: The new price that the fuel item would be changed to.

        Returns:
            True: If the fuel item's price was successfully changed.
            False: If the price to the fuel item could not be changed.
        """
        if not mws.set_value("Prices", fuel_item):
            self.log.error(f"{fuel_item} does not exist.")
            return False
        mws.set_value("Change selected prices to", True)
        if not mws.set_value("Change selected prices to edit", price):
            self.log.error(f"Could not change the fuel price edit to {price}.")
            return False
        if not mws.click("Update List"):
            self.log.error("Could not click the 'Update List' buttton.")
            return False

        msg = mws.get_top_bar_text()
        if msg:
            self.log.error("Unable to change fuel price. Passport message: {msg}")
            return False

        return True

    def increase(self, fuel_item, amount):
        """
        Increases the price to a selected fuel item by a specific cent amount.

        Args:
            fuel_item: The specific fuel item that the user would like to increase the price to.
            amount: The amount (in cents) that the fuel item will be increased to.

        Returns:
            True: The fuel item was successfully set to increase by the certain amount.
            False: If the fuel item was not successfully increased.
        """
        if not mws.set_value("Prices", fuel_item):
            self.log.error(f"Could not select the following fuel type: {fuel_item}")
            return False
        if not mws.set_value("Increase selected prices by", True):
            self.log.error(f"Could not select the 'Increase selected prices by' radio button.")
            return False
        if not mws.set_value("Cent(s)", amount):
            self.log.error(f"Could not set the cents amount to {amount}")
            return False
        if not mws.click("Cents button"):
            self.log.error("Could not click the 'Update List' button.")
            return False

        msg = mws.get_top_bar_text()
        if msg:
            self.log.error("Unable to increase fuel price. Passport message: {msg}")
            return False

        return True

    def decrease(self, fuel_item, amount):
        """
        Decreases the price to a selected fuel item by a specific cent amount.

        Args:
            fuel_item: The specific fuel item that the userwould like to decrease the price to.
            amount: The amount (in cents) that the fuel item willl be decreased to.

        Returns:
            True: The fuel item was successfully set to decrease by the specified amount.
            False: If the fuel item was not successfully decreased
        """
        if not mws.set_value("Prices", fuel_item):
            self.log.error(f"Could not select the following fuel type: {fuel_item}")
            return False
        if not mws.set_value("Decrease selected prices by", True):
            self.log.error(f"Could not select the 'Decrease selected prices by' radio button.")
            return False
        if not mws.set_value("Cent(s)", amount):
            self.log.error(f"Could not set the cents amount to {amount}")
            return False
        if not mws.click("Cents button"):
            self.log.error("Could not click the 'Update List' button.")
            return False

        msg = mws.get_top_bar_text()
        if msg:
            self.log.error("Unable to decrease fuel price. Passport message: {msg}")
            return False

        return True

    def select_pending_time(self, time_frame = "Immediately"):
        """
        To select the pending time in which the fuel price will change.

        Args:
            time_frame: The pending time that the fuel price will change to.

        Returns:
            True: If the time frame could be successfully set.
            False: If the time frame was not successfully set.
        """
        if not mws.set_value(time_frame, True):
            self.log.error(f"Could not select the following radio button: {time_frame}")
            return False
        return True