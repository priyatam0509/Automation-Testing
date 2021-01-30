from app import mws, system, Navi
import logging, time

class AccountingOptions:

    def __init__(self):
        self.log = logging.getLogger()
        AccountingOptions.navigate_to()

    @staticmethod
    def navigate_to():
        """
        Navigates to the Accounting Options feature module.
        Args: None
        Returns: Returns the result of execution of Navi.navigate_to()
        """
        return Navi.navigate_to("Accounting Options")

    def configure(self, config):
        """
        Configures the Accounting Options module.
        Args:
            config: A dictionary of controls so the user can add the information that
                      they need to. This is according to the schema in controls.json.
        Returns:
            True/False success condition
        Examples:
            acc_opt_info = {
                "General":{
                    "Allow operator to see system totals when balancing their till": True,
                    "Allow preview of previous counts when reconciling tills": True,
                    "The maximum number of times a till can be counted in Manager Workstation": "25"
                },
                "Tender Options":{
                    "Cash": "1.00",
                    "Check": "2.00",
                    "Credit": "3.00",
                    "Debit": "4.00",
                    "Other": "5.00",
                    "UCC": "6.00",
                    "EBT Food": "7.00",
                    "EBT Cash": "8.00",
                    "Added Tender 1": "9.00",
                    "Added Tender 2": "10.00",
                    "Added Tender 3": "11.00"
                },
                "Safe Options":{
                    "Main Safe":{
                        "Safe ID": "1",
                        "Safe Name": "Main Safe",
                        "Main Safe": True,
                    },
                    "Other Safe":{
                        "Safe ID": "2",
                        "Safe Name": "Other Safe"
                    }
                }
            }
            ao = accounting_options.AccountingOptions()
            ao.configure(acc_opt_info)
        """
        for tab in config:
            mws.select_tab(tab)
            if tab == "Safe Options":
                # Add/Change/Delete in Safe Options does not work unless Tender Options is loaded first.
                mws.select_tab("Tender Options")
                mws.select_tab(tab)
                for safe in config[tab]:
                    # Check if the safe exists
                    if mws.set_value("Safe List", safe):
                        self.log.debug(f"Found '{safe}' in list, clicking Change...")
                        mws.click("Change")
                    else:
                        self.log.debug(f"Adding '{safe}'...")
                        mws.click("Add")
                    # Configure safe fields
                    for key, value in config[tab][safe].items():
                        if not mws.set_value(key,value):
                            self.log.error(f"Could not set {key} to {value} for '{safe}'.")
                            return False 
                    mws.click("Update List")
                    # Check for error messages
                    if not self.check_error():
                        return False
            #Set other general controls
            else:
                for key, value in config[tab].items():
                    if not mws.set_value(key, value):
                        self.log.error(f"Could not set {key} to {value} on {tab} tab.")
                        return False
                    # Setting controls sometimes doesnt work immediately after select_tab()
                    if mws.get_value(key) != value:
                        self.log.debug(f"Setting {key} to {value} didn't work. Retrying...")
                        if not mws.set_value(key, value):
                            self.log.error(f"Could not set {key} to {value} on {tab} tab.")
                            return False
        mws.click_toolbar("Save")
        # Check for error messages
        if not self.check_error():
            return False
        return True

    def configure_safe(self, select, safe_id = None, safe_name = None, main_safe = None):
        """
        Adds a new safe or changes an existing safe.
        Args:
            select: A string that specifies the name of the safe to look for in the Safe List.
                    If safe_name is not specified, this variable is chosen as the name of the safe.
            safe_id: A string specifying the ID of the safe. Ignore to leave ID unchanged. 
            safe_name: A string containing the new name of the safe. If left blank, select will be
                       chosen for the name. 
            main_safe: A boolean value to specify whether the safe should be set as the main safe.
                       If a main safe has already been set, this checkbox will be greyed out and
                       passing a T/F argument will result in the test failing.
        Returns:
            True/False success condition
        Examples:
            ao = accounting_options.AccountingOptions()
            ao.configure_safe("new_safe", "3", "New Main Safe", False)
            True
        """
        # Add/Change/Delete in Safe Options does not work unless Tender Options is loaded first.
        mws.select_tab("Tender Options")
        mws.select_tab("Safe Options")
        # If safe_name not specified, set it to select
        if not safe_name:
            safe_name = select
        # Check if select is in list
        if mws.set_value("Safe List", select):
            self.log.debug(f"Found '{select}' in list. Changing...")
            mws.click("Change")
        else:
            self.log.debug(f"Couldn't find '{select}' in list. Adding safe as '{safe_name}'...")
            mws.click("Add")
        # Set controls
        mws.set_value("Safe ID", safe_id)
        mws.set_value("Safe Name", safe_name)
        if main_safe != None:
            if not mws.set_value("Main Safe", main_safe):
                self.log.error("Failed while setting control 'Main Safe'. There may have already been a main safe set. Make sure your configuration unsets the current main safe.")
                return False

        mws.click("Update List")
        # Check for error messages
        if not self.check_error():
            return False

        mws.click_toolbar("Save")

        # Check for error messages
        if not self.check_error():
            return False

        return True

    def delete_safe(self, safe_name, new_main_safe = None):
        """
        Deletes an existing safe.
        Args:
            safe_name: A string (or list of strings) containing the safe(s) to delete.
            new_main_safe: A string specifying the name of the safe to set as the main safe 
                           (only used when the previous main safe is deleted).
        Returns:
            True/False success condition
        Examples:
            ao = accounting_options.AccountingOptions()
            ao.delete_safe(["Main Safe","Other Safe"],"New Main Safe")
            True
        """
        # Add/Change/Delete in Safe Options does not work unless Tender Options is loaded first.
        mws.select_tab("Tender Options")
        mws.select_tab("Safe Options")
        # Check if a list of safes is passed in
        if type(safe_name) == list:
            # Delete every safe in list
            for safe in safe_name:
                if not mws.set_value("Safe List", safe):
                    self.log.error(f"Could not find {safe} in list.")
                    return False
                self.log.debug("Clicking delete.")
                mws.click("Delete")
                mws.click_toolbar("Yes")
        # Else just delete the safe
        else:
            if not mws.set_value("Safe List", safe_name):
                self.log.error(f"Could not find {safe_name} in list.")
                return False
            mws.click("Delete")
            mws.click_toolbar("Yes")
        mws.click_toolbar("Save")

        starttime = time.time()
        while time.time() - starttime < 1: 
            # Check if a new main safe needs to be set
            try:
                errormessage = mws.get_top_bar_text().lower()
                # Check error message
                if "no main safe" in errormessage or "error" in errormessage:
                    self.log.debug(f"Deleted main safe. Setting {new_main_safe} as new main safe...")
                    # Find and set new_main_safe
                    if not mws.set_value("Safe List", new_main_safe):
                        self.log.debug(f"Could not find {new_main_safe} in list.")
                        return False
                    mws.click("Change")
                    if not mws.set_value("Main Safe", True):
                        self.log.debug("Failed setting new main safe.")
                        return False
                    mws.click("Update List")
                    # Check for error messages
                    if not self.check_error():
                        return False
                    mws.click_toolbar("Save")
            except:
                self.log.debug("Cannot find top bar text, retrying...")
                continue
        
        return True

    def check_error(self, timeout = 1):
        """
        Returns False if an error was found.
        """
        starttime = time.time()
        while time.time() - starttime < timeout:
            # Check if there are any error messages in the top bar
            try:
                errormessage = mws.get_top_bar_text().lower()
                if "no main safe" in errormessage or "error" in errormessage:
                    self.log.error(errormessage)
                    self.log.error("Some part of your configuration was incorrect. Exiting...")
                    mws.recover()
                    return False
            except:
                continue
        return True