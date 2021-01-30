"""
    File name: POS_Close_Till.py
    Tags:
    Description: Script for testing the Close Till button/functionality in HTML POS.
    Author: 
    Date created: 04-6-2020
    Date last modified: 04-15-2020
    Python Version: 3.7
"""

import logging, time
from app import Navi, mws, pos, system
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class POS_Close_Till():

    def __init__(self):
        """
        Initializes the POS_Close_Till class
        """
        # The logging object. 
        # Example: self.log.info(f"Current value of var: {my_var}")
        self.log = logging.getLogger()
        self.wait_time = 1
        self.long_wait_time = 15
        self.paid_in_button = pos.controls['function keys']['paid in']
        self.sign_on_button = pos.controls['function keys']['sign on']
        self.cash_tender_key = pos.controls['pay']['type'] % 'cash'
        self.bills_button = pos.controls['function keys']['bills ->']
        self.coins_button = pos.controls['function keys']['coins ->']

    @setup
    def setup(self):
        """
        Performs initialization
        """
        # if not system.restore_snapshot():
        #     self.log.debug("No snapshot to restore, if this is not expected please contact automation team")
        mws.sign_on()
        pos.connect()
        

    #@test
    def close_till_no_balance(self):
        """
        Execute a basic close till operation
        that doesn't involve balancing the till
        """
        # Sign on
        pos.sign_on()

        # Click close till and initiate the close
        self.log.info("Attempting to click close till...")
        pos.click('close till')

        self.log.info("Attempting to click 'yes' at the 'Are you sure?' prompt...")
        msg = pos.read_message_box(timeout = self.wait_time)
        if not msg:
            tc_fail("Message asking if you are sure you would like to close till did not appear.")
        pos.click("yes")

        # Execute a till close without balancing the till
        self.log.info("Declining to balance the till...")
        pos.click('no')

        self.log.info("Checking whether it returned to the sign on screen...")
        if not pos.is_element_present(self.sign_on_button, timeout = self.long_wait_time):
            tc_fail("Did not return to the sign in screen after closing till.")

        self.log.info("Successfully closed till without balancing!")


    #@test
    def close_till_and_balance(self):
        """
        Execute a basic close till operation
        that DOES involve balancing the till
        """
        # Sign on (since last case signed off)
        pos.sign_on()

        # Click close till and initiate the close
        self.log.info("Attempting to click close till...")
        pos.click('close till')

        self.log.info("Attempting to click 'yes' at the 'Are you sure?' prompt...")
        msg = pos.read_message_box(timeout = self.wait_time)
        if not msg:
            tc_fail("Message asking if you are sure you would like to close till did not appear.")
        pos.click("yes")

        # Execute a till close and balance the till
        self.log.info("Attempting to start balancing the till...")
        pos.click('yes')

        # Check that all the denominations are present in the selection list
        coins = {'pennies':.01, 'nickels':.05, 'dime':.1, 'quarter':.25, 'roll of pennies':.5, 'roll of nickels':2, 'roll of dimes':5, 'roll of quarters':10, 'fifty cent piece':.5, 'one dollar coin':1}
        bills = {'one dollar bill':1, 'two dollar bill':2, 'five dollar bill':5, 'ten dollar bill':10, 'twenty dollar bill':20, 'fifty dollar bill':50, 'one hundred dollar bill':100}
        tempcoins = coins.copy()
        tempbills = bills.copy()


        self.log.info("Checking coin denominations...")
        selection_list = pos.read_list_items(timeout = self.wait_time)
        for denomination in selection_list:
            # Remove trailing characters
            denomination = denomination.split('\n', 1)[0].lower()
            try:
                del tempcoins[denomination]
            except ValueError:
                self.log.error(denomination.upper() + " isn't in the coins selection list...")
        if len(tempcoins) != 0:
            pos.click('+')
            pos.click('finalize')
            tc_fail("The following denominations were incorrectly spelled or missing in the coins selection list: " + str(tempcoins))

        self.log.info("Checking bill denominations...")
        pos.click('bills ->')

        # Make sure you're on the right screen
        pos.is_element_present(self.coins_button, timeout=self.wait_time)

        selection_list = pos.read_list_items(timeout = self.wait_time)
        for denomination in selection_list:
            # Remove trailing characters
            denomination = denomination.split('\n', 1)[0].lower()
            try:
                del tempbills[denomination]
            except ValueError:
                self.log.error(denomination.upper() + " isn't in the bills selection list...")
        if len(tempbills) != 0:
            pos.click('+')
            pos.click('finalize')
            tc_fail("The following denominations were incorrectly spelled or missing in the bills selection list: " + str(tempbills))

        # Check that the denominations are correct (i.e. the right amounts)
        self.log.info("Checking that bill denominations correspond to correct dollar amounts...")
        
        # Increment the amount of each denomination
        for denomination in pos.read_list_items(timeout = self.wait_time):
            pos.select_list_item(denomination)
            pos.enter_keypad('11', after='+')
            pos.enter_keypad('1', after='-')

        # Check the values
        for denomination in pos.read_list_items(timeout = self.wait_time):
            # Get the amount of money of that denomination and make sure it's right
            true_amount = float(denomination.split('$ ', 1)[1])
            expected_amount = bills[denomination.split('\n', 1)[0].lower()] * 10.0
            if not true_amount == expected_amount:
                pos.click('finalize')
                tc_fail(denomination.split('\n', 1)[0].upper() + " is not set to the right monetary value.")
        
        self.log.info("Monetary value of all the bills is correct...")

        pos.click('coins ->')
        self.log.info("Checking that coin denominations correspond to correct cent amounts...")

        # Make sure you're on the right screen
        pos.is_element_present(self.bills_button, timeout = self.wait_time)
        
        # Increment the amount of each denomination
        for denomination in pos.read_list_items(timeout = self.wait_time):
            pos.select_list_item(denomination)
            pos.enter_keypad('11', after='+')
            pos.enter_keypad('1', after='-')
        
        # Check the values
        for denomination in pos.read_list_items(timeout = self.wait_time):
            # Get the amount of money of that denomination and make sure it's right
            true_amount = float(denomination.split('$ ', 1)[1])
            expected_amount = coins[denomination.split('\n', 1)[0].lower()] * 10.0
            if not true_amount == expected_amount:
                pos.click('finalize')
                tc_fail(denomination.split('\n', 1)[0].upper() + " is not set to the right monetary value.")
        
        self.log.info("Monetary value of all the coins is correct...")

        # Finalize
        pos.click('finalize')

        # Make sure it returned to the sign on screen
        if not pos.is_element_present(self.sign_on_button, timeout = self.long_wait_time):
            tc_fail("Didn't return to the sign-on screen.")

        self.log.info("Successfully balanced and closed till!")


    #@test
    def cancel_till_balance(self):
        """
        Start a close till and go to the balance till screen,
        then cancel balancing the till and make sure it returns
        to the sign on screen like a close till without balance
        """
        # Sign on (since last case signed off)
        pos.sign_on()

        # Click close till and initiate the close
        self.log.info("Attempting to click close till...")
        pos.click('close till')

        self.log.info("Attempting to click 'yes' at the 'Are you sure?' prompt...")
        msg = pos.read_message_box(timeout = self.wait_time)
        if not msg:
            tc_fail("Message asking if you are sure you would like to close till did not appear.")
        pos.click("yes")

        # Execute a till close and go to the balance till screen
        self.log.info("Attempting to navigate to the balance till screen...")
        pos.click('yes')

        # Cancel the balance till
        pos.is_element_present(self.bills_button, timeout=self.wait_time)
        self.log.info("Attempting to cancel out of balancing the till...")
        pos.click('cancel')
        
        msg = pos.read_message_box(timeout = self.wait_time)
        if not msg:
            tc_fail("Did not verify whether user wanted to cancel balancing till.")
        pos.click('yes')

        # Make sure it returned to the sign on screen
        if not pos.is_element_present(self.sign_on_button, timeout = self.long_wait_time):
            tc_fail("Didn't return to the sign-on screen.")

        self.log.info("Successfully canceled balance till!")


    @test
    def suppress(self):
        """
        Make sure the toggle in Register Groups > Change >
        Till Counts that says "Suppress opening/closing till counts"
        affects HTML POS
        """
        
        # Set the toggle in the MWS
        self.log.info("Toggling the suppress setting in the MWS...")
        Navi.navigate_to('Register Group Maintenance')
        mws.click_toolbar('Change')
        mws.select_tab('Till Counts')
        mws.set_value("Suppress opening/closing till counts", True)

        if not mws.click_toolbar('Save'):
            tc_fail("Failed to save changes.")
        self.log.info("Saved change to suppress opening/closing till counts...")

        # Make sure changed settings are sent to register
        if not self._wait_for_reload(timeout = 10):
            tc_fail("Register did not reload after changing setting.")
        self.log.info("Reloaded register...")

        # Close the till with till count suppressed
        pos.connect()
        pos.sign_on()
        self.log.info("Closing till...")
        pos.click('close till')
        pos.click('yes')

        # Check that the till close and HTML POS returned to the sign-on screen
        self.log.info("Checking that HTML POS returned to the sign-on screen after closing till...")
        if not pos.is_element_present(self.sign_on_button, timeout = self.long_wait_time):
            tc_fail("Did not return to the sign-on screen after closing till.")


    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        pos.close()

        # Undo the toggle that was changed in suppress()
        self.log.info("Reverting the suppress setting in the MWS...")
        Navi.navigate_to('Register Group Maintenance')
        mws.click_toolbar('Change')
        mws.select_tab('Till Counts')
        mws.set_value("Suppress opening/closing till counts", False)

        mws.click_toolbar('Save')
        self.log.info("Reverted change to suppress opening/closing till counts...")

        # Make sure changed settings are sent to register
        if not self._wait_for_reload(timeout = 10):
            tc_fail("Register did not reload after changing setting.")
        self.log.info("Reloaded register...")
        self.log.info("Teardown complete!")



    def _wait_for_reload(self, timeout):
        """
        Helper function to make sure the mws has reloaded
        registers before trying to do something affected
        by a changed setting
        """
        start_time = time.time()
        while time.time() - start_time <= timeout:
            msg = mws.get_top_bar_text()
            if not msg:
                return True
        else:
            return False