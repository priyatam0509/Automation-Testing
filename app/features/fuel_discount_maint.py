from app.framework import mws, Navi
import logging

class FuelDiscountMaintenance:

    def __init__(self):
        FuelDiscountMaintenance.navigate_to()
        self.log = logging.getLogger()

    @staticmethod
    def navigate_to():
        return Navi.navigate_to("Fuel Discount Maintenance")

    def add(self, tab, config):
        """
        Adds one fuel discount to the specific tab.

        Args:
            tab: The name of the tab that needs to have the discount added to.
            config: A dictionary of control:value pairs.

        Returns:
            True: If the Fuel discount was able to be added.
            False: If something on adding the fuel discount went wrong (will be logged.)
        
        Example:
            \code
            
            fdm_info = {
                "Discount Group Name" : "testdiscount",
                "Grades" : {
                    "REGULAR" : "0.100"
                }
            }

            fdm = fuel_discount_maint.FuelDiscountMaintenance()
            fdm.add("Fuel Discount Groups", fdm_info)
                True
            
            \code
        """
        mws.select_tab(tab)
        mws.click_toolbar("Add")

        for key, value in config.items():
            if "Discount" in key and tab is not "Fuel Discounts by Cash":
                if mws.set_value("Discounts", value, tab): # check if discount group is already in discount list
                    self.log.warning(f"'{value}' discount group already exists. Exiting config...")
                    return True
            # for flexgrids:
            if key is "Grades" and type(value) is dict:
                for grade, amount in config[key].items():
                    mws.config_flexgrid("Grades", {grade:amount}, 182, tab = tab, max_dist = 0, instances = {})
            # for classic controls:
            elif not mws.set_value(key, value, tab):
                self.log.error(f"Could not set {key} to {value} on the {tab} tab.")
                mws.click_toolbar("Cancel")
                return False

        mws.click_toolbar("Save")

        # check for errors
        msg = mws.get_top_bar_text()
        if msg:
            self.log.error(msg)
            self.log.error("Some part of your configuration was incorrect.")
            return False

        return True

    def change(self, tab, discount_name, config):
        """
        Changes the setting to a specific fuel discount on the defined tab.

        Args:
            tab: The name of the tab in which the discount will be changed on.
            discount_name: The name of the discount that will be changed.
            config: A dictionary of control:value pairs.

        Returns:
            True: If the fuel discount was successfully changed.
            False: If something went wrong while changing the fuel discount.
        """
        mws.select_tab(tab)
        if tab.lower() != "fuel discounts by cash":
            if not mws.set_value("Discounts", discount_name):
                self.log.error(f"Could not select {discount_name} on the {tab} tab.")
                return False
        mws.click_toolbar("Change")
        for key, value in config.items():
            if not mws.set_value(key, value, tab):
                self.log.error(f"Could not set {key} to {value} on the {tab} tab.")
                mws.click_toolbar("Cancel")
                return False
        mws.click_toolbar("Save")

        # check for errors
        msg = mws.get_top_bar_text()
        if msg:
            self.log.error(msg)
            self.log.error("Some part of your configuration was incorrect.")
            return False

        return True

    def delete(self, tab, discount_name):
        """
        Deletes a specified fuel discount.

        Args:
            tab: The tab in which the fuel discount will be deleted from.
            discount_name: The name of the discount that will be deleted.

        Returns:
            True: If the discount was successfully deleted.
            False: If something went wrong while deleting the fuel discount. (Will be logged)
        """
        mws.select_tab(tab)
        #The other pages require you to select the discount you want to delete
        if tab.lower() != "fuel discounts by cash":
            if not mws.set_value("Discounts", discount_name, tab):
                self.log.error(f"Could not select {discount_name} on the {tab} tab.")
                return False
        mws.click_toolbar("Delete")
        if not mws.click_toolbar("Yes"):
            self.log.error(f"Could not successfully delete {discount_name}.")

        # check for errors
        msg = mws.get_top_bar_text()
        if msg:
            self.log.error(msg)
            self.log.error("Some part of your configuration was incorrect.")
            return False

        return True