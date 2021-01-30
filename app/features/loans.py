from app import mws, system, Navi
import logging, time

class Loans:

    def __init__(self):
        self.log = logging.getLogger()
        Loans.navigate_to()

    @staticmethod
    def navigate_to():
        """
        Navigates to the Loans feature module.
        
        Returns: 
            Returns the result of execution of Navi.navigate_to()
        """
        return Navi.navigate_to("Loans")

    def configure(self, till_id, safe, config, save = True):
        """
        Configures the safes, tenders, and amounts.

        Args:
            till_id: A string containing the ID number of the till to select from the list.
                     If the string passed is less than 12 characters, it will be padded
                     from the left with zeros.
            safe: A string containing the name of the safe to add loans to.
            config: A dictionary of controls so the user can add the information that
                      they need to. This is according to the schema in controls.json.
                      Tender Button controls can have keys of strings or lists of strings.
            save: A boolean value specifying whether to click "Save" at the end of configuration.
                  May be set to false if testing the functionality of other toolbar buttons.

        Returns:
            bool: Success/Failure

        Example: 
            loans_info = {
                "Tender Button 1": ["1000","5000","10000"],
                "Tender Button 2": "2500",
                "Tender Button 3": ["500"]
            }
            loan = loans.Loans()
            loan.configure("70", "Main Safe", loans_info, False)
            True
        """
        # Pad the till_id from left
        till_id = till_id.zfill(12)

        # Select specified till
        if not mws.set_value("Tills", till_id):
            self.log.error(f"Could not find till with ID '{till_id}' in list.")
            return False
        mws.click_toolbar("Add")

        # Select specified safe
        if not mws.set_value("Safe", safe, timeout = 1):
            if mws.get_value("Safe")[0] != safe:
                self.log.error(f"'{safe}' is not configured as a safe and cannot be selected.")
                return False
        # Begin adding tenders and amounts
        for tender_button, amounts in config.items():
            # Convert single strings to lists for easier iteration
            if type(amounts) == str:
                amounts = [amounts]
            for amount in amounts:
                mws.set_value("Amount", amount)
                if not mws.click(tender_button):
                    self.log.error(f"Could not find {tender_button}.")
                    return False
        # Save and exit if specified
        if save:
            mws.click_toolbar("Save")
            msg = mws.get_top_bar_text()
            if msg:
                self.log.error(f"Got an unexpected message when saving loan. Passport message: {msg}")
                return False

        return True

    def change_amount(self, select, changed_amount):
        """
        Changes a tender to a different amount. Must be on "Loan for Till ID:" subpage.

        Args:
            select: A tuple (tender,amount) of strings containing the values 
                    of the row to select from the list.
            changed_amount: The new amount of the tender.

        Returns:
            bool: Success/Failure

        Example:
            loan = loans.Loans()
            loan.change_amount(("Cash","50.00"), "2500")
            True
        """
        if type(select) == tuple:
            if not mws.set_value("Tenders", select):
                self.log.error(f"Could not find {select} in list.")
                return False
            mws.click_toolbar("Change Amount")
            time.sleep(1)
            if not mws.set_value("Amount", changed_amount):
                self.log.error(f"Could not set Amount to {changed_amount}.")
            mws.click_toolbar("Add Amount")
        else: 
            self.log.error("Please pass select as a tuple.")
            return False

        msg = mws.get_top_bar_text()
        if msg:
            self.log.error(f"Got an unexpected error when changing loan amount: {msg}")
            return False

        return True
    
    def delete_tender(self, select):
        """
        Removes a tender/amount entry from the list. Must be on "Loan for Till ID:" subpage.

        Args:
            select: A tuple (tender,amount) of strings containing the values 
                    of the row to select from the list.

        Returns:
            bool: Success/Failure

        Example:
            loan = loans.Loans()
            loan.delete_tender(("Cash","25.00"))
            Trues
        """
        if type(select) == tuple:
            if not mws.set_value("Tenders", select):
                self.log.error(f"Could not find {select} in list.")
                return False
            mws.click_toolbar("Delete Amount")
        else: 
            self.log.error("Please pass select as a tuple.")
            return False

        msg = mws.get_top_bar_text()
        if msg:
            self.log.error(f"Got an unexpected error when deleting amount from loan: {msg}")
            return False

        return True
