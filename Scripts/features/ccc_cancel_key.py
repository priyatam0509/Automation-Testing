"""
    File name: ccc_cancel_key.py
    Tags:
    Description: This script tests the cancel key functionality in the Cashier Control Console (CCC).
    Author: Christopher Haynes
    Date created: 2019-12-11
    Date last modified: 
    Python Version: 3.7
"""

import logging, time
from app import system, checkout, console
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from Scripts.features import EL_PaymentTest

class ccc_cancel_key():
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
        self.max_attempts = 40 #number of times check for disabled screen
        self.button_sleep_time = 0.5
        self.item_plu = "002"

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
        pass

    @test
    def cancel_payment_screen_1(self):
        """
        Description:
                Checks for the ability to cancel a payment screen.  This automates M-90699.
        Args: 
                None
        Returns: 
                None
        """
        
        self.log.info("Adding an item to the transaction.")
        self.prep_checkout()
        checkout.enter_plu(self.item_plu)
        self.log.info("Clicking pay.")
        checkout.click("Pay")
        checkout.click("card")
        self.click_cancel()
        if not checkout._is_element_present("//div[@id='notification_box_text' and text()='Payment Cancelled']"):
                tc_fail("Cancellation message not present.")
        if not checkout.click("OK"):
                tc_fail("Couldn't close cancellation message.")
        if not checkout._is_element_present("//div[@class='speedkeys']"):
                tc_fail("Didn't return to the transaction screen after clicking cancel.")
        self.void_transaction()
        checkout.close()
        
    @test
    def cancel_plu_entry_2(self):
        """
        Description:
                Checks for the ability to cancel PLU entry.  This automates M-90699.
        Args: 
                None
        Returns: 
                None
        """
        
        self.log.info("Navigating to PLU entry.")
        self.prep_checkout()
        checkout.click("Key In Code")
        self.click_cancel()
        time.sleep(self.button_sleep_time)
        if checkout._is_element_present("//div[@class='keypad_pane']"):
                tc_fail("The keypad is still visible.")
        if not checkout._is_element_present("//div[@class='speedkeys']"):
                tc_fail("Didn't return to the transaction screen after clicking cancel.")
        checkout.close()

    @test
    def cancel_help_screen_3(self):
        """
        Description:
                Checks for the ability to cancel the help screen.  This automates M-90699.
        Args: 
                None
        Returns: 
                None
        """
       
        self.log.info("Clicking Help.")
        self.prep_checkout()
        checkout.click("Help")
        self.click_cancel()
        if checkout._is_element_present("//div[@class='help_screen upper_right_panel']"):
                tc_fail("The help panel didn't close.")
        if not checkout._is_element_present("//div[@class='speedkeys']"):
                tc_fail("Didn't return to the transaction screen after clicking cancel.")
        checkout.close()

    @test
    def cancel_help_from_payment_4(self):
        """
        Description:
                Checks for the ability to cancel the help screen when accessed from the payment screen.  This automates M-90699.
        Args: 
                None
        Returns: 
                None
        """
        
        self.log.info("Adding an item to the transaction.")
        self.prep_checkout()
        checkout.enter_plu(self.item_plu)
        time.sleep(self.button_sleep_time)
        self.log.info("Clicking Pay.")
        checkout.click("Pay")
        time.sleep(self.button_sleep_time)
        self.log.info("Clicking Help.")
        checkout.click("Help")
        self.click_cancel()
        if checkout._is_element_present("//div[@class='help_screen upper_right_panel']"):
                tc_fail("The help panel didn't close.")
        if not checkout._is_element_present("//div[@class='payment_options_pane']"):
                tc_fail("Didn't return to the payment screen after clicking cancel.")
        self.void_transaction()
        checkout.close()

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

        # Suspend Transaction if any test case is fail due to payment issue
        EL_PaymentTest.suspend_transaction()

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
        attempts = 0
        while checkout._is_element_present("//div[@id='disabled_screen']") and attempts < self.max_attempts:
            attempts = attempts + 1
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
        self.log.info("Voiding the transaction.")
        console.connect()
        console.click_function_key("Cancel")
        if console._get_text("//*[@id='terminal_list']/div/div[4]/div/div[2]") != "In Transaction":
                console.click_function_key("In Transaction")
        console.click("Void Transaction")
        self.enter_credentials()
        console.close()

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

    def click_cancel(self):
        """
        Description:
                Clicks the cancel button on the CCC. Assumes checkout is already connected.
        Args:
                None
        Returns:
                None
        """
        self.log.info("Switching to ccc to click cancel.")
        console.connect()
        if not console.click_function_key("Cancel"):
            tc_fail("Cancel button couldn't be clicked.")
        self.log.info("Closing ccc connection.")
        console.close()


