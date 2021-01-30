from app import mws
from app import Navi, system
import logging, time

class IncomeExpenseAccountMaintenance:
    def __init__(self):
        self.log = logging.getLogger()
        IncomeExpenseAccountMaintenance.navigate_to()

    @staticmethod
    def navigate_to():
        """
        Navigates to the Income/Expense Account Maintenance feature module.
        Args: None
        Returns: Returns the result of execution of Navi.navigate_to()
        """
        return Navi.navigate_to("income/expense account maintenance")

    def add(self, config):
        """
        Description: Adds an income/expense account.
        Args:
            config: A dictionary of controls so the user can add the information that
            they need to. This is according to the schema in controls.json.
        Returns:
            bool: Success/Failure
        Example: 
            ie_info = {
                "Account ID":"1234",
                "Description":"Test Account",
                "Eligible for miscellaneous tender transfers.": True,
                "Income": True
            }
        """
        # Click Add button
        if not mws.click_toolbar("Add"):
            self.log.error("Could not click Add button.")
            system.takescreenshot()
            return False
        # Cycle through controls and set each value according to config
        for key in config:
            if not mws.set_value(key, config[key]):
                self.log.error(f"Could not set '{key}' control to value '{config[key]}")
                system.takescreenshot()
                return False
        # Click Save button
        if not mws.click_toolbar("Save"):
            self.log.error("Could not click Save button.")
            system.takescreenshot()
            return False
        # Check for error messages
        starttime = time.time()
        while time.time() - starttime < 1:
            try:
                errormessage = mws.get_top_bar_text().lower()
                if "errors" in errormessage:
                    self.log.error("Some part of your configuration is incorrect.")
                    return False
            except AttributeError:
                continue
        #Confirm new account is in list
        if not mws.set_value("Accounts", config["Description"]):
            self.log.error(f"Could not confirm successful addition. Failing...")
            system.takescreenshot()
            return False
        return True

    def change(self, account_name, config):
        """
        Description: Changes the fields of an income/expense account.
        Args:
            account_name: The name of the account being changed.
            config: A dictionary of controls so the user can add the information that
            they need to. This is according to the schema in controls.json.
        Returns:
            bool: Success/Failure
        Example:
            account_name = Test Account
            changed_ie_info = {
                "Account ID":"5678",
                "Description":"Test Account",
                "Eligible for miscellaneous tender transfers.": True,
                "Expense": True
        """
        # Find and select specified account in list
        if not mws.set_value("Accounts",account_name):
            self.log.error(f"Could not find '{account_name} in list.")
            return False
        # Click Change button
        if not mws.click_toolbar("Change"):
            self.log.error("Could not click Change button.")
            system.takescreenshot()
            return False        
        for key in config:
            if "Account ID" in key:
                self.log.warning("Account ID can not be changed once set. Skipping...")
            elif "Income" in key or "Expense" in key:
                self.log.warning("Income/Expense can not be changed once set. Skipping...")
            else:
                # Cycle through controls and set each value according to config
                if not mws.set_value(key, config[key]):
                    self.log.error(f"Could not set '{key}' control to value '{config[key]}")
                    system.takescreenshot()
                    return False
        # Click Save button
        if not mws.click_toolbar("Save"):
            self.log.error("Could not click Save button.")
            system.takescreenshot()
            return False
        # Check for error messages for 1 second
        starttime = time.time()
        while time.time() - starttime < 1:
            try:
                errormessage = mws.get_top_bar_text().lower()
                if "errors" in errormessage:
                    self.log.error("Some part of your configuration is incorrect.")
                    return False
            except AttributeError:
                continue
            
        return True

    def delete(self, account_name):
        """
        Description: Deletes an income/expense account.
        Args:
            account_name: The name of the account being deleted.
        Returns:
            bool: Success/Failure
        Example:
            account_name = "Test Account"
        """
        # Find and select specified account in list
        if not mws.set_value("Accounts", account_name):
            self.log.error(f"Could not find {account_name} in the list.")
            system.takescreenshot()
            return False
        # Click Delete button
        if not mws.click_toolbar("Delete"):
            self.log.error("Could not click Delete button.")
            system.takescreenshot()
            return False    
        mws.click_toolbar("Yes")
        # Check to see if account is still in list
        if mws.set_value("Accounts", account_name):
            self.log.error("Account is still in the list, deletion unsuccessful.")
            system.takescreenshot()
            return False
        return True
