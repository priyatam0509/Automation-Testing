from app import mws
from app import Navi, system
import logging, time

log = logging.getLogger()

class FuelDiscountConfiguration:

    def __init__(self):
        FuelDiscountConfiguration.navigate_to()

    @staticmethod
    def navigate_to():
        """
        Navigates to the Fuel Discount Configuration feature module.
        Args: None
        Returns: mws.create_connection() if navigation was successful.
        """
        process = "netxmlconfig.exe"
        end = "local fuel discount configuration"

        # Since searching "Fuel Discount Configuration" in searchbar takes you to a
        # different module, Navi does not work conventionally.
        if system.process_wait(process, 1):
            log.debug('Already in %s menu' %end)
            mws.load_controls(end)
            return mws.create_connection()

        # search for "Frequently Used in MWS menu"
        mws.find_text_ocr("Frequently Used", (18,93,145,122), color = "FFFFFF", tolerance = "443E30")
        
        #TODO: add logic to determine what module/menu we are currently in and navigate back to MWS
        
        mws.click_toolbar("Set Up")
        mws.click_toolbar("Network Menu")
        mws.click_toolbar("Mobile Payment")
        mws.click_toolbar("Fuel Discount Configuration")

        # if in local fuel discount config, load controls
        if system.process_wait(process, 3):
            mws.load_controls(end)
            return mws.create_connection()

    def configure(self, default_discount, config):
        """
        Description: Sets default fuel discount and adds/changes local fuel discounts.
        Args:
            default_discount: A string specifying what discount to choose as the default fuel discount group.
            config: A dictionary of controls specifying what local discounts to add/change
                    in the Local Fuel Discounts tab, as well as what values to insert into
                    each field.
        Returns:
            bool: Success/Failure
        Example: 
            fdc_info = {
                "NewLocalDiscount1": {
                    "Mobile Local Discount Description": "This is a test discount.",
                    "Fuel Discount Group": "discount1"
                },
                "NewLocalDiscount2": {
                    "Mobile Local Discount Description": "This is also a test discount.",
                    "Fuel Discount Group": "discount2"
                }
            }
            fdc = fuel_discount_config.FuelDiscountConfiguration()
            fdc.configure("discount1", fdc_info)
            True
        """
        mws.select_tab("Default Local Fuel Discount")
        # Set default discount
        if not mws.set_value("Default Fuel Discount Group", default_discount, "Default Local Fuel Discount"):
            log.error(f"Could not find {default_discount} in list of discounts.")
            return False
        
        mws.select_tab("Local Fuel Discounts")
        # Iterate over each local discount and check existence
        for localdiscount in config:
            if not mws.set_value("Discount List", localdiscount):
                log.debug(f"Could not find '{localdiscount}' in discount list. Adding...")
                mws.click_toolbar("Add")
                mws.set_value("Mobile Local Discount Code", localdiscount)
            else:
                log.debug(f"'{localdiscount}' already exists in list. Editing...")
            
            # Begin setting values
            for key, value in config[localdiscount].items():
                if not mws.set_value(key, value, "Local Fuel Discounts"):
                    log.error(f"Failed setting '{key}' to '{value}' while configuring '{localdiscount}'.")
                    return False
        
        try:
            mws.click_toolbar("Save", main=True)
        except mws.ConnException:
            # Didn't make it back to main menu, check for errors
            errorcode = mws.get_top_bar_text()
            log.error(errorcode)
            log.error("Some part of your configuration was incorrect.")
            return False
        
        return True

    def delete(self, discount_list):
        """
        Description: Deletes specified discounts from the Local Fuel Discounts list. Must be called
                     from within the Fuel Discount Configuration menu.
        Args:
            discount_list: A list of strings specifying which entries to delete from
            the Local Fuel Discounts list.
        Returns:
            bool: Success/Failure
        Example: 
            fdc = fuel_discount_config.FuelDiscountConfiguration()
            fdc.delete(["NewLocalDiscount1","NewLocalDiscount2"])
            True
        """
        mws.select_tab("Local Fuel Discounts")
        
        # Delete each entry
        for localdiscount in discount_list:
            if not mws.set_value("Discount List", localdiscount):
                log.error(f"Could not find '{localdiscount}' in discount list.")
                return False
            mws.click_toolbar("Delete")
            mws.click_toolbar("Yes")
        
        # Check successful deletion
        for localdiscount in discount_list:
            if mws.set_value("Discount List", localdiscount):
                log.error(f"Could not successfully delete '{localdiscount}' from discount list.")
                return False
        
        try:
            mws.click_toolbar("Save", main=True)
        except mws.ConnException:
            # Didn't make it back to main menu, check for errors
            errorcode = mws.get_top_bar_text()
            log.error(errorcode)
            log.error("Some part of your configuration was incorrect.")
            return False

        return True