"""
    File name: ccc_authentication.py
    Tags:
    Description: This script tests the aunthentication functionality in the Cashier Control Console (CCC).
    Author: Christopher Haynes
    Date created: 2019-12-18
    Date last modified: 
    Python Version: 3.7
"""

import logging, time
from app import system, checkout, console, store_options
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from Scripts.features import EL_PaymentTest

class ccc_authentication():
    """
    Description: Testing authentication in the CCC.
    """

    def __init__(self):
        """
        Initializes the test class.
        """
        # The logging object.
        # Example: self.log.info(f"Current value of var: {my_var}")
        self.log = logging.getLogger()
        self.credentials_timeout = 60 #time it takes for a login to expire
        self.connection_timeout = 30 #time to wait for connection to 
        self.button_sleep_time = 1
        self.valid_username = "91"
        self.valid_password = "91"
        self.invalid_username = "301"
        self.invalid_password = "301"

    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        """

        self.log.info("Increasing the maximum number of logon attempts to avoid getting locked out.")
        st = store_options.StoreOptions()
        new_settings = {
            "General": {
                "Store Name" : "Automation Land",
                "Address Line 1" : "1234 Address Lane",
                "City" : "Raleigh",
                "State" : "NC",
                "Postal Code" : "27420",
                "Store" : "(954)555-1481",
                "Help Desk" : "(336)555-1234"
                },
            "Password": {
                "Invalid Sign-On Attempts Allowed": "20"
            }
        }
        st.setup(new_settings)
        
        self.log.info("Starting a transaction to ensure that all needed options are available.")
        self.start_transaction(first=True)

    @test
    def cancel_username_authentication_1(self):
        """
        Checks for the correct behavior when an authentication attempt is canceled.
        This automates M-90712.
        """
        
        console.connect()

        self.log.info("Canceling authentication for \"Support\" button on CCC.")
        console.click("Support")
        console.click_keypad_key("Cancel")
        if console.is_element_present("//div[@id='menuTitle' and text() = 'Terminal 1 Support']", timeout=2):
            tc_fail("The Support menu was accessed inappropriately.")

        self.log.info("Canceling authentication for \"Void Transaction\" button on CCC.")
        console.click("Void Transaction")
        console.click_keypad_key("Cancel")
        if len(console.read_journal(terminal="1")) == 0:
            tc_fail("The transaction was inappropriately voided.")

        console.close()

    @test
    def cancel_password_authentication_2(self):
        """
        Checks for the correct behavior when an authentication attempt is canceled.
        This automates M-90712.
        """
        
        console.connect()

        self.log.info("Canceling authentication for \"Support\" button on CCC.")
        console.click("Support")
        self.cancel_password()
        if console.is_element_present("//div[@id='menuTitle' and text() = 'Terminal 1 Support']", timeout=2):
            tc_fail("The Support menu was accessed inappropriately.")
        
        self.log.info("Canceling authentication for \"Void Transaction\" button on CCC.")
        console.click("Void Transaction")
        self.cancel_password()
        if len(console.read_journal(terminal="1")) == 0:
            tc_fail("The transaction was inappropriately voided.")

        console.close()

    @test
    def invalid_username_3(self):
        """
        Checks for the correct behavior when an authentication attempt receives an invalid username.
        This automates M-90712.
        """
        console.connect()

        self.log.info("Entering invalid username for \"Support\" button authentication on CCC.")
        console.click("Support")
        console.sign_in((self.invalid_username, self.valid_password), verify=False)
        if not console.is_element_present("//div[@id='prompt_box_text' and text() = 'Operator not found']", timeout=2):
            tc_fail("Operator not found wasn't displayed.")
        console.click_prompt_key("Ok")

        self.log.info("Entering invalid username for \"Void Transaction\" button authentication on CCC.")
        console.click("Void Transaction")
        console.sign_in((self.invalid_username, self.valid_password), verify=False)
        if not console.is_element_present("//div[@id='prompt_box_text' and text() = 'Operator not found']", timeout=2):
            tc_fail("Operator not found wasn't displayed.")
        console.click_prompt_key("Ok")
        if len(console.read_journal(terminal="1")) == 0:
            tc_fail("The transaction was inappropriately voided.")

        console.close()

    @test
    def invalid_password_4(self):
        """
        Checks for the correct behavior when an authentication attempt receives an invalid password.
        This automates M-90712.
        """
        console.connect()

        self.log.info("Entering invalid password for \"Support\" button authentication on CCC.")
        console.click("Support")
        console.sign_in((self.valid_username, self.invalid_password), verify=False)
        if not console.is_element_present("//div[@id='prompt_box_text' and text() = 'Invalid password entered.']", timeout=2):
            tc_fail("Operator not found wasn't displayed.")
        console.click_prompt_key("Ok")

        self.log.info("Entering invalid password for \"Void Transaction\" button authentication on CCC.")
        console.click("Void Transaction")
        console.sign_in((self.valid_username, self.invalid_password), verify=False)
        if not console.is_element_present("//div[@id='prompt_box_text' and text() = 'Invalid password entered.']", timeout=2):
            tc_fail("Operator not found wasn't displayed.")
        console.click_prompt_key("Ok")
        if len(console.read_journal(terminal="1")) == 0:
            tc_fail("The transaction was inappropriately voided.")

        console.close()

    @test
    def valid_authentication_5(self):
        """
        Checks for the correct behavior when an authentication attempt receives a valid username and password.
        This automates M-90712.
        """
        console.connect()

        self.log.info("Entering valid credentials for \"Support\" button authentication on CCC.")
        console.click("Support")
        console.sign_in((self.valid_username, self.valid_password), verify=False)
        if not console.is_element_present("//div[@id='menuTitle' and text() = 'Terminal 1 Support']", timeout=2):
            tc_fail("The Support menu couldn't be accessed successfully.")
        console.click_options_key("Cancel")

        self.log.info("Entering valid credentials for \"Void Transaction\" button authentication on CCC.")
        console.void_transaction(user_credentials=(self.valid_username, self.valid_password))

        console.close()

    @test
    def valid_authentication_6(self):
        """
        Description:
                Checks for the ability to click multiple buttons from a single authentication.
                This automates M-93581.
        """
        
        self.log.info("Starting a new transaction.")
        self.start_transaction()
        
        console.connect()
        self.log.info("Waiting for the authentication to timeout so credentials need to be entered again.")
        time.sleep(self.credentials_timeout)
        
        self.log.info("Entering valid credentials for \"Support\" button authentication on CCC.")
        console.click("Support")
        console.sign_in((self.valid_username, self.valid_password), verify=False)
        if not console.is_element_present("//div[@id='menuTitle' and text() = 'Terminal 1 Support']", timeout=2):
            tc_fail("The Support menu couldn't be accessed successfully.")
        console.click_options_key("Cancel")

        self.log.info("Accessing Support without requiring re-authentication.")
        console.click("Support")
        if console.is_element_present("//div[@id='loginKeypad']", timeout=2):
            tc_fail("Authentication required for \"Support\" button when it shouldn't be.")
        console.click_options_key("Cancel")

        self.log.info("Voiding a transaction without requiring re-authentication.")
        console.click("Void Transaction")
        if console.is_element_present("//div[@id='loginKeypad']", timeout=2):
            tc_fail("Authentication required for \"Void Transaction\" button when it shouldn't be.")

        console.close()

    @teardown
    def teardown(self):
        """
        Description:
                Performs cleanup after this script ends.
        """
        # Suspend Transaction if any test case is fail due to payment issue
        EL_PaymentTest.suspend_transaction()


# ##########################################################################################
# #################################### HELPER FUNCTIONS ####################################
# ##########################################################################################

    def cancel_password(self, username = "91"):
        """
        Description:
                Enters the user (default: 91) to cancel the authentication process on the password screen.
                This function assumes that console.connect has already been called.
        Args:
                username:
                    The username to use to get to password entry.
        Returns:
                True if the username and password could be entered successfully.
        """
        time.sleep(self.button_sleep_time)
        if console.is_element_present("//div[@id='loginKeypad']", timeout=2):
            self.log.info("Entering {} as the username.".format(username))
            for c in username:
                console.click_keypad_key(c)
                time.sleep(self.button_sleep_time)
            console.click_keypad_key("Ok")
            
            return console.click_keyboard_key("Cancel")
        else:
            tc_fail("Couldn't cancel password entry.")

    def start_transaction(self, first=False):
        """
        Description:
            Gets the Express Lane ready for use.
        """
        if first:
            checkout.connect()
            time.sleep(20)

            # due to reloading of store options, loading start button takes longer than usual
            start_time = time.time()
            while time.time() - start_time <= 30:
                if checkout.click_welcome_key("Start", timeout=2):
                    break           
            else:
                self.log.error("Unable to click 'start'")
        
        else:
            checkout.connect()
            
            #waiting for express lane to come up
            system.wait_for(checkout._is_element_present, desired_result=False, timeout = self.connection_timeout, args = ["//div[@id='disabled_screen']"])

            # I only want the message box out of the way.  If it doesn't exist to click, this isn't a problem.
            try:
                checkout.click_message_box_key("OK")
            except:
                pass

            if checkout._is_element_present("//div[@id = 'welcomescreen']"):
                checkout.click_welcome_key("Start")

        checkout.enter_plu("002")
        checkout.close()