from app.framework import mws, Navi
import logging

log = logging.getLogger()

class DiscountMaintenance:

    def __init__(self):
        DiscountMaintenance.navigate_to()

    @staticmethod
    def navigate_to():
        return Navi.navigate_to("Discount Maintenance")

    def add(self, config):
        """
        Adds a discount

        Args:
            config: A list of key:value pairs that will set the GUI while adding the discount.
        Returns:
            True: If the discount was successfully added.
            False: If something went wrong while adding the discount. (Should be logged)
        Examples:
            >>>disc_maint = {
                "Discount Name" : "Standard 20% off",
                "General" : {
                    "Standard" : True,
                    "Standard Discount Options Text Box" : "20"
                }}
            >>>add(disc_maint)
            True
            >>>add(disc_maint)
            False
        """
        mws.click_toolbar("Add")
        for key, value in config.items():
            if type(value) != dict:
                #This is here for Discount Name mainly.
                if not mws.set_value(key, value):
                    log.warning(f"Could not set {value} to {key}.")
                    return False
            else:
                mws.select_tab(key)
                for key2, value2 in value.items():
                    if not mws.set_value(key2, value2, key):
                        log.warning(f"Could not set {key2} with {value2} on the {key} tab.")
                        return False
        mws.click_toolbar("Save")
        msg = mws.get_top_bar_text()
        if msg and "error" in msg:
            log.warning(f"Failed to save discount. Error message: {msg}")
            mws.click_toolbar("Cancel")
            mws.click_toolbar("No")
            return False
        if "Discount Name" in config:
            log.info(f"Successfully added the {config['Discount Name']} discount.")
        else:
            log.info("Successfully added a discount.")
        return True
    
    def change(self, discount_name, config):
        """
        Changes a discount

        Args:
            discount_name: The name of the discount that will be changed.
            config: A list of key:value pairs that will set the GUI while changing the discount.
        Returns:
            True: If the discount was successfully changed.
            False: If something went wrong while changing the discount. (Should be logged)
        Examples:
            >>>disc_maint = {
                "Discount Name" : "Standard 20% off",
                "General" : {
                    "Standard" : True,
                    "Standard Discount Options Text Box" : "20"
                }}
            >>>change("Standard 10% off", disc_maint)
            True
            >>>change("Variable 10% off", disc_maint)
            False
        """
        if not mws.set_value("Discounts", discount_name):
            log.warning(f"Could not select {discount_name} in the discounts list.")
            return False
        mws.click_toolbar("Change")
        for key, value in config.items():
            if type(value) != dict:
                #This is here for Discount Name mainly.
                if not mws.set_value(key, value):
                    log.warning(f"Could not set {value} to {key}.")
                    return False
            else:
                mws.select_tab(key)
                for key2, value2 in value.items():
                    if not mws.set_value(key2, value2, key):
                        log.warning(f"Could not set {key2} with {value2} on the {key} tab.")
                        return False
        mws.click_toolbar("Save")
        msg = mws.get_top_bar_text()
        if msg and "error" in msg:
            log.warning(f"Failed to save discount. Error message: {msg}")
            mws.click_toolbar("Cancel")
            mws.click_toolbar("No")
            return False
        if "Discount Name" in config:
            log.info(f"Successfully added the {config['Discount Name']} discount.")
        else:
            log.info("Successfully added a discount.")
        return True

    def delete(self, discount_name):
        """
        Deletes a discount

        Args:
            discount_name: The name of the discount that will be deleted.
        Returns:
            True: If the discount was successfully deleted.
            False: If the discount could not be deleted. (Should be logged)
        Examples:
            >>>delete("Standard 10% off")
            True
            >>>delete("Standard 20% off")
            False
        """
        if not mws.set_value("Discounts", discount_name):
            log.warning(f"Could not select {discount_name} in the discounts list.")
            return False
        mws.click_toolbar("Delete")
        mws.click_toolbar("Yes")
        msg = mws.get_top_bar_text()
        if msg and "error" in msg:
            log.warning(f"Failed to save discount. Error message: {msg}")
            mws.click_toolbar("Cancel")
            mws.click_toolbar("No")
            return False
        return True
