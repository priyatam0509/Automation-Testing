from app.framework import Navi, mws
from app.util import system
import logging, time, pywinauto, copy, re

class TaxMaintenance:
    def __init__(self):
        self.log = logging.getLogger()
        TaxMaintenance.navigate_to()

    @staticmethod
    def navigate_to():
        return Navi.navigate_to("Tax Maintenance")

    def configure(self, config):
        """
        Configure tax rates and groups. Rates and groups that already exist will be modified, those that don't will be created.
        Args:
            config: A dictionary describing the configuration to apply. See example.
        Returns: (bool) True on success, False on failure.
        Example:
            >>> cfg = { "Rates":
                        { "NC Sales": 
                            { "Name": "NC Sales",
                              "Receipt Description": "NC Tax",
                              "Percent": "1",
                              "Table": [".04", ".08", ".12", ".16", ".20", ".24", ".28"],
                              "Activate": True },
                          "GST Tax":
                            { "Name": "GST Tax",
                              "Receipt Description": "GST",
                              "GST": True,
                              "Percent": "6.75",
                              "Activate": True },
                         "PST Tax":
                            { "Name": "PST Tax",
                              "Receipt Description": "PST",
                              "Percent": "3.00",
                              "PST": True,
                              "Table": "Remove" }
                        },
                        "Groups":
                            { "Sales Tax":
                                { "Name": "Sales Tax",
                                  "POS Description": "SalesTax",
                                  "Rates": { "NC Sales": True, "GST Tax": False },
                                  "Activate": True },
                               "PST Tax":
                                { "Name": "GST3Percent",
                                  "POS Description": "3Percent",
                                  "Identify taxed items with": True,
                                  "Identify taxed items with text box": "GST3",
                                  "and print receipt key": "GST3",
                                  "Rates": { "NC Sales": False, "GST Tax": True },
                                  "Activate": False }
                            },
                        "Options":
                            { "Print all assigned fuel tax amounts on receipt": True }
                      }
            >>> TaxMaintenance().configure(cfg)
            True            
        """
        for tab, settings in config.items():
            if tab == "Rates":
                for rate, values in settings.items(): 
                    if not self.configure_rate(rate, values):
                        return False
            elif tab == "Groups":
                for group, values in settings.items():
                    if not self.configure_group(group, values):
                        return False
            else:
                mws.select_tab(tab)
                for field, value in settings.items():
                    if not mws.set_value(field, value, tab=tab):
                        return False

        try:
            mws.click_toolbar("Save", main=True)
        except mws.ConnException:
            self.log.warning(f"Error saving Tax Maintenance. Passport message: {mws.get_top_bar_text()}")
            return False

        return True

    def configure_group(self, group, config):
        """
        Configure a tax group. If the group already exists, modify it; otherwise, add a new group.
        Args:
            group: The name of the group to modify, if any.
            config: A dictionary describing the configuration to apply. See example.
        Example:
            >>> cfg = { "Name": "NC Sales Tax",
                        "Group used for fuel tax assignment": True,
                        "POS Description": "SalesTax",
                        "Rates": { "No Tax": False, "NC Tax": True },
                        "Activate": True }
            >>> TaxMaintenance().configure_group("NC Sales Tax", cfg)
            True
        """
        if not mws.select_tab("Groups"):
            return False

        if mws.set_value("Tax Groups", group, tab="Groups"):
            # Group already exists, change it
            if not mws.search_click_ocr("Change",tolerance='808080'):
                return False
        else:
            # Group doesn't exist, add it
            if not mws.search_click_ocr("Add",tolerance='808080'):
                return False

        for field, value in config.items():
            if field == "Activate" or field == "Rates":
                continue # We'll do this later
            elif not mws.set_value(field, value, tab="Groups"):
                return False

        if not mws.search_click_ocr("Update List",tolerance='808080'):
            return False
        top_bar_text = mws.get_top_bar_text()
        if top_bar_text:
            self.log.warning(f"Couldn't save {group} group. Passport message: {top_bar_text}")
            return False

        # Make sure the group saved and select it for the next step
        try: # We might have changed the name or not. Have to account for both
            if not mws.set_value("Tax Groups", config["Name"], tab="Groups"):
                log.warning(f"{config['Name']} not found in list of tax groups after configuration.")
                return False
        except KeyError:
            if not mws.set_value("Tax Groups", group, tab="Groups"):
                log.warning(f"{group} not found in list of tax groups after configuration.")
                return False

        # Select rates to include in the group
        if "Rates" in config:           
            for rate, setting in config["Rates"].items():
                if not mws.set_value(rate, setting, tab="Groups", list="Tax Rates"):
                    return False
                if "Deactivated rates cannot be selected" in mws.get_top_bar_text():
                    self.log.warning(f"Cannot select deactivated rate {rate} for group {group}.")

        if "Activate" in config:
            if config["Activate"]:
                if not mws.search_click_ocr("Activate",tolerance='808080'):
                    return False
            else:
                if not mws.search_click_ocr("Deactivate",tolerance='808080'):
                    return False
                mws.click_toolbar("YES")

        return True

    def configure_rate(self, rate, config):
        """
        Configure a tax rate. If the rate already exists, modify it; otherwise, add a new group.
        Args:
            rate: The name of the rate to modify, if any.
            config: A dictionary describing the configuration to apply. See example.
        Example:
            >>> cfg = { "Name": "NC Sales",
                        "Receipt Description": "NC Tax",
                        "Percent": "1",
                        "Table": [".04", ".08", ".12", ".16", ".20", ".24", ".28"],
                        "Activate": True },
            >>> TaxMaintenance().configure_rate("NC Sales", cfg)
            True
        """
        if "GST" in config and config["GST"] == True and "Table" in config:
            mws.log.warning("Tax table is not applicable for GST tax rates. Aborting configuration.")
            return False

        if not mws.select_tab("Rates"):
            return False
        if mws.set_value("Rates", rate, tab="Rates"):
            # Rate already exists. Modify it
             if "Table" in config:
                 # Handle removing table. If table is being added/modified we'll handle it later
                 if config["Table"] == "Remove":
                     if not mws.search_click_ocr("Remove Table", tolerance='808080'):
                         return False
                     mws.click_toolbar("YES")
                     try:
                         mws.set_value("Percent", config["Percent"], tab="Rates")
                     except KeyError:
                         self.log.warning("Percent must be specified when removing tax rate table.")
                         return False
                     if not mws.search_click_ocr("Update List"):
                         return False
                 elif type(config["Table"]) == str:
                     self.log.warning("Unrecognized value for Table setting. Please provide a list of End Amounts or 'Remove'.")
                     return False
             if not mws.search_click_ocr("Change", tolerance='808080'):
                return False          
        else:
            # Rate doesn't exist. Add it
            if not mws.search_click_ocr("Add", tolerance='808080'):
                return False
            if "Table" in config and config["Table"] == "Remove":
                self.log.warning("Can't remove tax table from a newly created rate.")
                return False
        
        # Configure fields for the rate
        for field, value in config.items():            
            if field == "Table" or field == "Activate":
                continue # These are handled elsewhere
            elif not mws.set_value(field, value, tab="Rates"):
                return False

        if not mws.search_click_ocr("Update List", tolerance='808080'):
            return False
        top_bar_text = mws.get_top_bar_text()
        if top_bar_text:
            self.log.warning(f"Couldn't save {rate} rate. Passport message: {top_bar_text}")
            return False

        # Ensure it saved and select it for activation/deactivation
        try: # We might have changed the name or not. Have to account for both
            if not mws.set_value("Rates", config["Name"], tab="Rates"):
                log.warning(f"{config['Name']} not found in list of tax rates after configuration.")
                return False
        except KeyError:
            if not mws.set_value("Rates", rate, tab="Rates"):
                log.warning(f"{rate} not found in list of tax rates after configuration.")
                return False

        if "Activate" in config:
            if config["Activate"]:
                if not mws.search_click_ocr("Activate", tolerance='808080'):
                    return False
            else:
                if not mws.search_click_ocr("Deactivate", tolerance='808080'):
                    return False
                mws.click_toolbar("YES")

        if "Table" in config and type(config["Table"]) == list:
            self._configure_table(config["Table"])

        return True
         
    def test(self, amount, rate):
        """
        Test a tax rate with a given amount.
        Args:
            amount: (str) The dollar amount to use in the Test Amount field.
            rate: (str) The tax rate to select.
        Returns: (str) The contents of the Result field after testing.
        Example:
            >>> TaxMaintenance().test("10.00", "NC Sales")
            "0.68"
        """
        mws.select_tab("Test")
        if not mws.set_value("Test Amount", amount):
            return False
        if not mws.set_value("Tax Rates", rate, tab="Test"):
            return False
        if not mws.search_click_ocr("Test", instance=4):
            return False
        return mws.get_value("Result")

    def PLUs(self, group):
        """
        Check what PLUs are assigned to a given tax group.
        Args:
            group: (str) The tax group to check.
        Returns: (list) The PLUs and descriptions for items taxed by the group.
        Example:
            >>> TaxMaintenance().PLUs("Sales Tax")
            [["7100", "Burger"], ["7101", "Fries"], ["7102", "Coke"]]
        """
        mws.select_tab("PLU")
        if not mws.set_value("Select a tax group to view the PLUs that are taxed by that group", group):
            return False
        return mws.get_value("PLUs")

    
    def _configure_table(self, end_amounts):
        """
        Configure a rate table for the currently selected tax rate.
        Args:
            end_amounts: (list) End amount to set for each rate bracket.
        Returns: (bool) True if successful, False if failure (such as invalid pattern).
        Example:
            >>> TaxMaintenance()._configure_table([".04", ".08", ".12", ".16", ".20", ".24", ".30"])
            True
        """
        # No support for Change Table. Just overwrite if there is already a table
        if not mws.search_click_ocr("Create Table"):
            return False
        if not mws.search_click_ocr("Add To End"):
            return False
        if not mws.set_value("Continuous Add", True):
            return False
        for end_amount in end_amounts:
            if not mws.set_value("End Amount", end_amount):
                return False
            if not mws.search_click_ocr("Update List"):
                return False
        if not mws.search_click_ocr("Cancel"):
            return False
        mws.click_toolbar("Save")
        msg = mws.get_top_bar_text()
        if msg:
            self.log.warning(f"Couldn't save rate table. Message: {msg}")
            return False
        return True