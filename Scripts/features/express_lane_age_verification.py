"""
    File name: express_lane_age_verification.py
    Tags:
    Description: This script tests the age restriction functionality in the Cashier Control Console (CCC).
    Author: Christopher Haynes
    Date created: 2019-12-6
    Date last modified: 
    Python Version: 3.7
"""

import logging, time, datetime
from app import mws, item, checkout, console, restriction_maint
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class express_lane_age_verification():
    """
    Description: Testing the ability to control access to age restricted items from the CCC.
    """

    def __init__(self):
        """
        Description:
                Initializes the express_lane_age_verification class.
        Args:
                None
        Returns:
                None
        """
        # The logging object.
        # Example: self.log.info(f"Current value of var: {my_var}")
        self.log = logging.getLogger()
        self.button_sleep_time = 0.5
        self.item_num = 2057
        self.rest_group_name = "Over 30"
        self.todays_date = datetime.datetime.now().year

    @setup
    def setup(self):
        """
        Description:
                Performs any initialization that is not default.
        Args:
                None
        Returns:
                None
        """
        
        restrictions = restriction_maint.RestrictionMaintenance()
        self.log.info("Deleting the restriction group if it already exists.")
        if self.rest_group_name in mws.get_value("Restriction"):
            restrictions.delete(self.rest_group_name)
            
        restrictions = restriction_maint.RestrictionMaintenance()
        self.log.info("Adding a restriction group for the test.")
        new_restriction = {
            "Restriction For Group": "{}".format(self.rest_group_name),
            "Buyer/Seller": {
                "Seller must be at least": False,
                "Buyer Verify Only": False,
                "Entry of birth date required": True,
                "Minimum Buyer Age": "30"
                }
            }
        restrictions.add(new_restriction)
        mws.click_toolbar("Exit", main = True)
        
        self.log.info("Adding an item to use for the test.")
        items = item.Item()
        new_item = {
                "General": {
                    "PLU/UPC": "{}".format(self.item_num),
                    "Description": "Item {}".format(self.item_num),
                    "Department": "Dept 1",
                    "Item Type": "Regular Item",
                    "Receipt Desc": "Item {}".format(self.item_num),
                    "per unit": "100"
                },
                "Options": {
                    "Return Price": "100",
                    "Restriction Group": "{}".format(self.rest_group_name)
                }
            }
        items.add(new_item, overwrite = True)
        mws.click_toolbar("Exit", main = True)
    
    @test
    def manually_denied_item_1(self):
        """
        Description:
                Checks for the function of rejecting an age restricted item through manual denial.  This automates M-90708.
        Args: 
                None
        Returns: 
                None
        """
     
        self.log.info("Connecting to the Express Lane.")
        self.prep_checkout()
            
        self.log.info("Adding the restricted item to the transaction.")
        if not checkout.enter_plu("{}".format(self.item_num)):
            tc_fail("The restricted item couldn't be added.")
        checkout.close()
        console.connect()
        console.click_key("//button[text()='Deny']")
        time.sleep(1)
        if console.is_element_present("//div[@class = 'approval_item approval_text' and text()='Item {}']".format(self.item_num)):
            tc_fail("The item is still waiting for approval after being denied.")
        if ["Item {}".format(self.item_num), "$1.00"] in console.read_journal("1"):
            tc_fail("The restricted item was added to the transaction despite being Denied.")
        console.close()

    @test
    def check_date_denied_item_2(self):
        """
        Description:
                Checks for the function of rejecting an age restricted item by date entry.  This automates M-90708.
        Args: 
                None
        Returns: 
                None
        """

        self.log.info("Connecting to the Express Lane.")
        self.prep_checkout()
            
        self.log.info("Adding the restricted item to the transaction.")
        if not checkout.enter_plu("{}".format(self.item_num)):
            tc_fail("The restricted item couldn't be added.")
        checkout.close()
        console.connect()
        console.click_key("//button[text()='Approve']")
        if not self.enter_credentials():
            tc_fail("Failed to authenticate cashier.")

        self.log.info("Entering invalid date.")
        self.enter_date(10)
            
        if console.is_element_present("//div[@class = 'approval_item approval_text' and text()='Item {}']".format(self.item_num)):
            tc_fail("The item is still waiting for approval after being denied.")
        if ["Item {}".format(self.item_num), "$1.00"] in console.read_journal("1"):
            tc_fail("The restricted item was added to the transaction despite being denied.")
        console.close()

    # Commenting this test case, need to discuss with Merline team
    # @test
    # def check_id_denied_item_3(self):
    #     """
    #     Description:
    #             Checks for the function of accepting an age restricted item by scanning a driver's license.  This automates M-90708.
    #     Args: 
    #             None
    #     Returns: 
    #             None
    #     """
    #     if self.test3:
    #         self.log.info("Connecting to the Express Lane.")
    #         self.prep_checkout()
            
    #         self.log.info("Adding the restricted item to the transaction.")
    #         if not checkout.enter_plu("{}".format(self.item_num)):
    #             tc_fail("The restricted item couldn't be added.")
    #         checkout.close()
    #         console.connect()
    #         console.click_key("//button[text()='Approve']")
    #         if not self.enter_credentials():
    #             tc_fail("Failed to authenticate cashier.")

    #         #TODO: scan an invalid ID

    #         time.sleep(1)
    #         if console.is_element_present("//div[@class = 'approval_item approval_text' and text()='Item {}']".format(self.item_num)):
    #             tc_fail("The item is still waiting for approval after being denied.")
    #         if ["Item {}".format(self.item_num), "$1.00"] in console.read_journal("1"):
    #             tc_fail("The restricted item was added to the transaction despite being denied.")
    #         console.close()
    #     else:
    #         self.log.info("Test 3 has been skipped due to a flag in the init method.")


    @test
    def check_date_approved_item_4(self):
        """
        Description:
                Checks for the function of accepting an age restricted item by date entry.  This automates M-90708.
        Args: 
                None
        Returns: 
                None
        """
        
        self.log.info("Connecting to the Express Lane.")
        self.prep_checkout()
            
        self.log.info("Adding the restricted item to the transaction.")
        if not checkout.enter_plu("{}".format(self.item_num)):
            tc_fail("The restricted item couldn't be added.")
        checkout.close()
        console.connect()
        console.click_key("//button[text()='Approve']")
        if not self.enter_credentials():
            tc_fail("Failed to authenticate cashier.")

        self.log.info("Entering valid date.")
        self.enter_date(40)

        if console.is_element_present("//div[@class = 'approval_item approval_text' and text()='Item {}']".format(self.item_num)):
            tc_fail("The item is still waiting for approval after being approved.")
        if not ["Item {}".format(self.item_num), "$1.00"] in console.read_journal("1"):
            tc_fail("The restricted item was not added to the transaction despite being approved.")

        #void transaction to return to a neutral state
        self.void_transaction()

        console.close()
        
    # Commenting this test case, need to discuss with Merline team
    # @test
    # def check_id_approved_item_5(self):
    #     """
    #     Description:
    #             Checks for the function of accepting an age restricted item by scanning a driver's license.  This automates M-90708.
    #     Args: 
    #             None
    #     Returns: 
    #             None
    #     """
    #     if self.test5:
    #         self.log.info("Connecting to the Express Lane.")
    #         self.prep_checkout()
            
    #         self.log.info("Adding the restricted item to the transaction.")
    #         if not checkout.enter_plu("{}".format(self.item_num)):
    #             tc_fail("The restricted item couldn't be added.")
    #         checkout.close()
    #         console.connect()
    #         console.click_key("//button[text()='Approve']")
    #         if not self.enter_credentials():
    #             tc_fail("Failed to authenticate cashier.")

    #         #TODO: scan a valid ID

    #         time.sleep(1)
    #         if console.is_element_present("//div[@class = 'approval_item approval_text' and text()='Item {}']".format(self.item_num)):
    #             tc_fail("The item is still waiting for approval after being approved.")
    #         if not ["Item {}".format(self.item_num), "$1.00"] in console.read_journal("1"):
    #             tc_fail("The restricted item was not added to the transaction despite being approved.")

    #         #void transaction to return to a neutral state
    #         self.void_transaction()

    #         console.close()
    #     else:
    #         self.log.info("Test 5 has been skipped due to a flag in the init method.")

    @teardown
    def teardown(self):
        """
        Description:
                Performs cleanup after this script ends.
        Args:
                None
        Returns:
                None
        """

        pass

# ##########################################################################################
# #################################### HELPER FUNCTIONS ####################################
# ##########################################################################################

    def prep_checkout(self):
        """
        Description:
                Gets the Express Lane ready for use.
        Args:
                None
        Returns:
                None
        """
        checkout.connect()
        #waiting for express lane to come up
        while checkout._is_element_present("//div[@id='disabled_screen']"):
            time.sleep(1)

        try:
            checkout.click_message_box_key("OK")
        except:
            pass #I only want the message box out of the way.  If it doesn't exist to click, this isn't a problem.

        #ensuring the welcome screen is not in the way
        if checkout._is_element_present("//div[@id = 'welcomescreen']"):
            checkout.click_welcome_key("Start")
           
    def void_transaction(self):
        """
        Description:
                Voids the current transaction from the CCC.
        Args:
                None
        Returns:
                None
        """
        console.click("Void Transaction")
        self.enter_credentials()

    def enter_date(self, years_ago):
        """
        Description:
                Types out a date from a given number of years ago.
        Args:
                years_ago: the number of years into the past to enter the date of.
        Returns:
                None
        """
        self.log.info("Entering a date for {} years ago.".format(years_ago))
        #month
        time.sleep(self.button_sleep_time)
        console.click_keypad_key("1")
        time.sleep(self.button_sleep_time)
        console.click_keypad_key("1")
        #day
        time.sleep(self.button_sleep_time)
        console.click_keypad_key("1")
        time.sleep(self.button_sleep_time)
        console.click_keypad_key("1")
        #year
        d = str(self.todays_date - years_ago)
        for i in d:
            time.sleep(self.button_sleep_time)
            console.click_keypad_key(i)
        time.sleep(self.button_sleep_time)
        console.click_keypad_key("Ok")
        time.sleep(self.button_sleep_time) #gives it time to finish working
              
    def enter_credentials(self):
        """
        Description:
                Enters the credentials (user: 91, pass: 91) to authenticate the user.
        Args:
                None
        Returns:
                None
        """
        time.sleep(self.button_sleep_time)
        if console.is_element_present("//div[@id='loginKeypad']"):
            if not console.click_keypad_key("9"):
                return False
            time.sleep(self.button_sleep_time)
            if not console.click_keypad_key("1"):
                return False
            time.sleep(self.button_sleep_time)
            if not console.click_keypad_key("Ok"):
                return False
            time.sleep(self.button_sleep_time)
            if not console.click_keyboard_key("9"):
                return False
            time.sleep(self.button_sleep_time)
            if not console.click_keyboard_key("1"):
                return False
            time.sleep(self.button_sleep_time)
            if not console.click_keyboard_key("Ok"):
                return False
            time.sleep(self.button_sleep_time) #gives it time to finish working
            return True
        else:
            return False