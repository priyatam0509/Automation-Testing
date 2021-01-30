from app import mws, Navi
import logging, time

class TillBalance:

    def __init__(self):
        self.log = logging.getLogger()
        TillBalance.navigate_to()

    @staticmethod
    def navigate_to():
        """
        Navigates to the Till Balance feature module.
        
        Returns:
            Returns the result of execution of Navi.navigate_to()
        """
        return Navi.navigate_to("till balance")

    def configure(self, till_id, config):
        """
        Configures tenders and amounts in the Till Balance feature module. Can be used to add
        new amounts or change pre-existing entries.

        Args:
            till_id: A string containing the ID number of the till to select from the Tills list.
            config: • A dictionary of controls so the user can add the information that
                      they need to. This is according to the schema in controls.json.
                    • Tender buttons on the next screen (accessible after clicking 'Next') 
                      can be specified by using numbers 17-32 in their control name.
                    • Tenders such as Cash, with multiple different denominations, must be inputted
                      as a dictionary. See template below. 
                    • Tenders such as Credit or Debit may be inputted as a list of strings or tuples.
                      Strings will ADD new amounts. Tuples will REPLACE the first entry in the tuple
                      with the second entry.
            save: A boolean value specifying whether to save and exit after configuration.

        Returns:
            bool: Success/Failure

        Example: 
            till_balance_info = {
                "Tender Button 1": {
                    "Coins": {
                        "Nickels": "25",
                        "Quarter": "10"
                    },
                    "Bills": {
                        "One Dollar Bill": "15",
                        "Five Dollar Bill": "10",
                        "Twenty Dollar Bill": "5"
                    }
                },
                "Tender Button 2": ["5.00", "125.50"],
                "Tender Button 3": [("5.00","25.00"), "7.50"],
                "Tender Button 17": ["25.00"]
            }
            tb = till_balance.TillBalance()
            tb.configure("70", till_balance_info)
            True
        """
        # Check whether we are on Till Balance homescreen or already balancing specific till
        if mws.find_text_ocr("Till ID", (100,120,200,140)):
            self.log.debug("Already balancing a till. Checking till number...")
            # make sure the till currently being balanced is the one we want to select
            if not mws.find_text_ocr(till_id, (100,120,200,140)):
                self.log.error(f"Currently selected till does not have ID '{till_id}'. Please exit till configuration and retry.")
                return False
            self.log.debug(f"Till ID matches ID specified: {till_id}. Continuing with configuration.")
        else: # not in till balance screen, so select specific till...
            if not mws.set_value("Tills", till_id):
                self.log.error(f"Could not find till with ID '{till_id}' in list.")
                return False
            mws.click_toolbar("Select")

        on_next_page = False # remember where we are in the tender button menu

        # Begin adding tenders and amounts
        for tenderbutton, value in config.items(): # iterate over each tender button
            # check if tenderbutton is valid
            if "Tender Button" in tenderbutton:
                # Click tender button
                try:
                    mws.click(tenderbutton)
                    self.log.debug(f"Clicked '{tenderbutton}'.")
                    # NOTE: Since there can be more than 16 tender buttons, program needs to click 'next'
                    # to access any buttons above #16. However, 17th button has control ID "Tender Button 1",
                    # 18th has ID #2, etc, so to click buttons on next screen the control ID should be 
                    # decremented by 16.
                except:   
                    self.log.warning(f"Could not find '{tenderbutton}' among tender buttons. Trying second button menu...")
                    mws.click("Tender Button 16") # clicks 'Next' button
                    num = int(tenderbutton.split(' ')[2]) # retrieves number from end of 'tenderbutton' string
                    new_num = num-16 # subtracts 16
                    if not mws.click(tenderbutton.replace(str(num),str(new_num))): # inserts new number into 'tenderbutton' string and clicks
                        self.log.error(f"Could not find '{tenderbutton}' among tender buttons.")
                        return False
                    self.log.debug(f"Clicked '{tenderbutton}' on second page.")
                    on_next_page = True
            else:
                self.log.error(f"{tenderbutton} is not a valid Tender Button.")
                return False

            if type(value) == dict: # for cash-type tenders (with different denominations)
                for tenderunit in config[tenderbutton]: # iterate over each tender unit type (coins, bills, etc.)
                    # Load correct denomination list
                    if not mws.set_value("View Other Tender Units", tenderunit):
                        self.log.error(f"Could not find '{tenderunit}' in Tender Unit dropdown list.")
                        return False
                    for denomination, amount in config[tenderbutton][tenderunit].items(): # iterate over each denomination
                        # Click denomination in list
                        if not mws.set_value("Tenders", denomination):
                            self.log.error(f"Could not find '{denomination}' in '{tenderbutton}' list.")
                            return False
                        # Enter amount and update
                        mws.set_value("Count", amount)
                        if not mws.click("Update List"):
                            self.log.error(f"Failed clicking 'Update List' while adding {denomination}.")
                            return False

            else: # for non-cash tenders (with no denominations)
                for amount in value: # iterate over each string/tuple
                    if type(amount) == str: # Add amount...
                        mws.set_value("Amount", amount)
                        if not mws.click("Update List"):
                            self.log.error(f"Failed clicking 'Update List' while configuring '{tenderbutton}'.")
                            return False
                    elif type(amount) == tuple: # Change amount...
                        if not mws.set_value("Tenders", amount[0]): # find existing amount
                            self.log.error(f"Could not find existing amount '{amount[0]}' in list of '{tenderbutton}'.")
                            return False
                        # Set new amount and update
                        mws.set_value("Amount", amount[1]) 
                        if not mws.click("Update List"):
                            self.log.error(f"Failed clicking 'Update List' while changing {amount[0]} to {amount[1]} in '{tenderbutton}' list.")
                            return False
                    else:
                        self.log.error(f"Type: '{type(amount)}' is not supported as an argument for '{tenderbutton}'. Only strings and tuples are accepted.")
                        return False

            if on_next_page: # go back to first tender button page so all controls are not different
                mws.search_click_ocr("Back", (450,510,530,550))
                on_next_page = False

        mws.click_toolbar("Save")
        # Deal with all possible error messages during 5 second timeout 
        self.log.debug("Starting error checking with 5 second timeout.")
        starttime = time.time()
        while time.time() - starttime < 5:
            error_message = mws.get_top_bar_text()
            if error_message:
                if "recount your till" in error_message.lower():
                    mws.click_toolbar("NO")  
                elif "accept the counts" in error_message.lower():
                    mws.click_toolbar("YES") 
                elif "balanced correctly" in error_message.lower():
                    mws.click_toolbar("OK") 
                    break
            else:
                self.log.error(f"Unrecognized error message: {error_message}")
                return False
        return True
