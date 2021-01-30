from app import mws, Navi
import logging

class ReasonCodeMaintenance:
    def __init__(self):
        self.log = logging.getLogger()
        ReasonCodeMaintenance.navigate_to()

    @staticmethod
    def navigate_to():
        """
        Navigates to the Reason Code Maintenance feature module.
        Args: None
        Returns: Returns the result of execution of Navi.navigate_to()
        """
        return Navi.navigate_to("Reason Code Maintenance")

    def add(self, code_list):
        """
        Description: Add new reason codes.
        Args:
            code_list: A string or list of strings.
        Returns:
            bool: Success/Failure
        Example: 
            reasoncodes = ["This is a reason code.",
                           "This is also a reason code."]
        """
        if type(code_list) is str:
            code_list = [code_list]
        for code in code_list:
            if not mws.set_value("Reason Codes",code):
                mws.click_toolbar("Add")
                mws.set_value("Reason Code", code)
                mws.click_toolbar("Save")
            else:
                self.log.error(f"The code '{code}' already exists. Failing...")
                return False

        # Verify code added
        if code not in mws.get_value("Reason Codes"):
            self.log.error(f"{code} not found in list of reason codes after adding.")
            return False

        return True
    
    def change(self, code, changed_code):
        """
        Description: Changes an existing reason code.
        Args:
            code: A string corresponding to an existing reason code.
            changed_code: What the specified reason code will be changed to.
        Returns:
            bool: Success/Failure
        """
        if not mws.set_value("Reason Codes",code):
            self.log.error("Could not find existing reason code.")
            return False
        mws.click_toolbar("Change")
        mws.set_value("Reason Code", changed_code)
        mws.click_toolbar("Save")

        # Verify code changed
        if code not in mws.get_value("Reason Codes"):
            self.log.error(f"{changed_code} not found in list of reason codes after changing.")
            return False

        return True

    def delete(self, code_list):
        """
        Description: Deletes specified reason codes.
        Args:
            code_list: A string or list of strings that correspond
                       to existing reason codes.
        Returns:
            bool: Success/Failure
        """
        if type(code_list) is str:
            code_list = [code_list]
        for code in code_list:
            if not mws.set_value("Reason Codes",code):
                self.log.error(f"Reason code '{code}' could not be found. Failing...")
                return False
            mws.click_toolbar("Delete")
            mws.click_toolbar("Yes")

        # Verify code deleted
        if code in mws.get_value("Reason Codes"):
            self.log.error(f"{code} found in list of reason codes after deletion.")
            return False

        return True



