"""
    File name: POS_Local_Accounts_Paid_In.py
    Tags:
    Description: Script for testing local accounts paid in on HTML POS.
    Author: David Mayes
    Date created: 2020-05-12
    Date last modified: 
    Python Version: 3.7
"""

import logging, time
from app import pos, system
from app.framework.tc_helpers import setup, test, teardown, tc_fail

default_timeout = 10

class POS_Local_Accounts_Paid_In():
    """
    Class for testing local accounts paid in
    """

    def __init__(self):
        """
        Initializes the POS_Local_Accounts_Paid_In class
        """
        # The logging object. 
        # Example: self.log.info(f"Current value of var: {my_var}")
        self.log = logging.getLogger()
        self.manual_search_button = pos.controls['function keys']['manual search']
        self.confirm_button = pos.controls['function keys']['confirm']
        self.details_button = pos.controls['function keys']['details']
        self.cancel_button = pos.controls['function keys']['cancel']
        self.paid_in_button = pos.controls['function keys']['paid in']
        self.header_1 = pos.controls['local accounts']['header']
        self.header_2 = pos.controls['local accounts']['subacct header']
        self.short_wait_time = 3
        self.long_wait_time = 10


    @setup
    def setup(self):
        """
        Performs initialization
        """
        # if not system.restore_snapshot():
        #     self.log.debug("No snapshot to restore, if this is not expected please contact automation team")
        pos.connect()
        pos.sign_on()


    @test
    def components_present(self):
        """
        Make sure the right buttons + table headers are present on the
        local account selection screen
        """
        self.log.info("Entering a local account paid in transaction...")
        pos.click('loc acct paid in')

        # Make sure that the buttons/headers are right
        self.log.info("Checking that all of the appropriate elements are present...")
        if not pos.is_element_present(self.cancel_button, timeout=self.short_wait_time):
            tc_fail("Cancel button was not present.")
        if not pos.is_element_present(self.manual_search_button, timeout=self.short_wait_time):
            pos.click('cancel')
            tc_fail("Manual search button was not present.")
        if not pos.is_element_present(self.details_button, timeout=self.short_wait_time):
            tc_fail("Details button was not present.")
        if not pos.is_element_present(self.confirm_button, timeout=self.short_wait_time):
            tc_fail("The confirm button was not present.")
        self.log.info("All of the correct buttons are present...")

        header_list = ['Account ID', 'Account Name', 'Vat #',\
         'Sub-Account ID', 'Vehicle ID', 'Description']
        header = pos.get_text(self.header_1) + pos.get_text(self.header_2)
        for item in header_list:
            if item in header:
                header_list.remove(item)
            else:
                tc_fail("'" + item + "' was not found in the header on the local account paid in screen.")
        self.log.info("All of the correct headers are present...")
            
        self.log.info("All of the buttons and headers were correct!")


    @test
    def check_function_keys(self):
        """
        Make sure that the function keys don't show up
        on manual search or confirm screens
        """
        # Make sure that HTML POS is on the loc acct paid in screen
        if self.on_main_screen(timeout=self.short_wait_time):
            pos.click('loc acct paid in')
            self.log.info("On the local account paid in screen...")
        elif self.on_loc_acct_screen(timeout=self.short_wait_time):
            self.log.info("On the local account paid in screen...")
        else:
            tc_fail("Started on an unknown screen.")

        # Make sure no func keys on manual search screen
        self.log.info("Checking that there are no function keys on the manual search screen...")
        fkeys_manual_search = ""
        pos.click("manual search")
        if self.status_line_contains('ID', self.short_wait_time):
            if pos.is_element_present(self.confirm_button, timeout=0.1):
                fkeys_manual_search+=" Confirm;"
            if pos.is_element_present(self.manual_search_button, timeout=0.1):
                fkeys_manual_search+=" Manual Search;"
            if pos.is_element_present(self.details_button, timeout=0.1):
                fkeys_manual_search+=" Details;"
            if pos.is_element_present(self.cancel_button, timeout=0.1):
                fkeys_manual_search+=" Cancel"
        else:
            pos.click_keypad('cancel')
            tc_fail("Did not confirm that HTML POS is on the manual search screen.")
        
        pos.click_keypad('cancel')

        # Make sure no func keys on confirm screen
        self.log.info("Checking that there are no function keys on the confirm screen...")
        fkeys_confirm = ""
        pos.click("confirm")
        if self.status_line_contains('Amount', self.short_wait_time):
            if pos.is_element_present(self.confirm_button, timeout=0.1):
                fkeys_confirm+=" Confirm;"
            if pos.is_element_present(self.manual_search_button, timeout=0.1):
                fkeys_confirm+=" Manual Search;"
            if pos.is_element_present(self.details_button, timeout=0.1):
                fkeys_confirm+=" Details;"
            if pos.is_element_present(self.cancel_button, timeout=0.1):
                fkeys_confirm+=" Cancel"
        else:
            pos.click_keypad('cancel')
            tc_fail("Did not confirm that HTML POS is on the confirm screen.")

        pos.click_keypad('cancel')

        # Fail if any func keys were found
        if not fkeys_manual_search == "" and not fkeys_confirm == "":
            tc_fail("The following function keys were found on the manual search screen: " + fkeys_manual_search\
             + "\n And the following function keys were found on the confirm screen: " + fkeys_confirm)
        elif not fkeys_manual_search == "":
            tc_fail("The following function keys were found on the manual search screen: " + fkeys_manual_search)
        elif not fkeys_confirm == "":
            tc_fail("The following function keys were found on the confirm screen: " + fkeys_confirm)
        else:
            self.log.info("No function keys found on the manual search or confirm screens!")
        

    @test
    def basic_paid_in(self):
        """
        Execute a basic local account paid in transaction
        """
        # Make sure that HTML POS is on the loc acct paid in screen
        if self.on_main_screen(timeout=self.short_wait_time):
            pos.click('loc acct paid in')
            self.log.info("On the local account paid in screen...")
        elif self.on_loc_acct_screen(timeout=self.short_wait_time):
            self.log.info("On the local account paid in screen...")
        else:
            tc_fail("Started on an unknown screen.")

        # Select the local account
        pos.select_local_account('DG, Inc.')

        # Confirm the paid in transaction
        pos.click('confirm')
        msg = pos.read_status_line(timeout=self.short_wait_time)
        if msg == None:
            tc_fail("Status line message did not exist after clicking confirm.")
        elif not "enter" in msg.lower() or not "amount" in msg.lower():
            tc_fail("Status line message was '" + str(msg) + "' instead of 'Enter an Amount' or 'Enter Amount'\
             or any other phrase that includes the words both enter and amount.")
        
        pos.enter_keypad('1100', after='enter')

        # Check that the transaction completed
        if self.on_main_screen(timeout=self.long_wait_time):
            msg = pos.read_journal_watermark(timeout=self.short_wait_time)
            if msg == None:
                tc_fail("No journal watermark saying 'Transaction Complete' present")
            elif "transaction complete" not in msg.lower():
                tc_fail("Journal watermark said '" + str(msg) + "' instead of 'Transaction Complete'")
            self.log.info("'Transaction Complete' journal watermark appeared...")
        else:
            tc_fail("Did not return to the main screen after completing local account paid in.")

        array = pos.read_transaction_journal(timeout=self.short_wait_time)
        array_checker = ['Local Account Paid In Transaction', 'Account ID: 1', 'Account Name: DG, Inc.',\
         'Sub-Account ID: 0000000000', 'Description: aDescription', 'Vehicle ID: aVehicleRegNo', 'Account Balance:']

        for row in array:
            for item in array_checker:
                if item in row[0]:
                    array_checker.remove(item)
                    break

        if not len(array_checker) == 0:
            tc_fail("The transaction journal was not formatted correctly.  The following was not found: " + str(array_checker))

        self.log.info("Successfully completed a basic local account paid in transaction!")                    


    @test
    def cancel_manual_search(self):
        """
        Begin a manual search and cancel it
        """
        # Make sure that HTML POS is on the loc acct paid in screen
        if self.on_main_screen(timeout=self.short_wait_time):
            pos.click('loc acct paid in')
            self.log.info("On the local account paid in screen...")
        elif self.on_loc_acct_screen(timeout=self.short_wait_time):
            self.log.info("On the local account paid in screen...")
        else:
            tc_fail("Started on an unknown screen.")

        # Start a manual search and cancel it
        pos.click('manual search')
        msg = pos.read_status_line(timeout=self.short_wait_time)
        if msg == None:
            tc_fail("Status line message did not exist after clicking manual search.")
        elif "enter account id" not in msg.lower():
            tc_fail("Status line message for manual search was " + str(msg.lower()) + " instead of 'Enter Account ID'.")
        pos.click_keypad('cancel')

        if self.on_loc_acct_screen(timeout=self.long_wait_time):
            self.log.info("Successfully cancelled manual search!")
        else:
            tc_fail("Cancel manual search failed.")


    @test
    def manual_search(self):
        """
        Do a manual search for account ID
        and complete a local account paid in
        """
        # Make sure that HTML POS is on the loc acct paid in screen
        if self.on_main_screen(timeout=self.short_wait_time):
            pos.click('loc acct paid in')
            self.log.info("On the local account paid in screen...")
        elif self.on_loc_acct_screen(timeout=self.short_wait_time):
            self.log.info("On the local account paid in screen...")
        else:
            tc_fail("Started on an unknown screen.")

        # Do a manual search
        pos.click('manual search')
        msg = pos.read_status_line(timeout=self.short_wait_time)
        if msg == None:
            tc_fail("Status line message did not exist after clicking manual search.")
        elif "enter account id" not in msg.lower():
            tc_fail("Status line message for manual search was '" + str(msg) + "' instead of 'Enter Account ID'.")
        
        pos.enter_keypad('2', after='enter')
        
        # Complete the paid in transaction
        pos.click('confirm')
        pos.enter_keypad('1000', after='enter')

        # Check that the transaction completed
        if self.on_main_screen(timeout=self.long_wait_time):
            msg = pos.read_journal_watermark(timeout=self.short_wait_time)
            if msg == None:
                tc_fail("No journal watermark saying 'Transaction Complete' present")
            elif "transaction complete" not in msg.lower():
                tc_fail("Journal watermark said '" + str(msg) + "' instead of 'Transaction Complete'")
        else:
            tc_fail("Did not return to the main screen after completing local account paid in.")

        array = pos.read_transaction_journal(timeout=self.short_wait_time)
        array_checker = ['Local Account Paid In Transaction', 'Account ID: 2', 'Account Name: KK Company',\
         'Sub-Account ID: 0000000000', 'Description:', 'Vehicle ID:', 'Account Balance:']

        for row in array:
            for item in array_checker:
                if item in row[0]:
                    array_checker.remove(item)
                    break

        if not len(array_checker) == 0:
            tc_fail("The transaction journal was not formatted correctly.  The following was not found: " + str(array_checker))

        self.log.info("Successfully completed manual search and local account paid in transaction!")


    @test
    def manual_search_fail(self):
        """
        Try to search for a local account that doesn't exist
        and make sure the correct error message comes up
        """
        # Make sure that HTML POS is on the loc acct paid in screen
        if self.on_main_screen(timeout=self.short_wait_time):
            pos.click('loc acct paid in')
            self.log.info("On the local account paid in screen...")
        elif self.on_loc_acct_screen(timeout=self.short_wait_time):
            self.log.info("On the local account paid in screen...")
        else:
            tc_fail("Started on an unknown screen.")

        # Do an incorrect manual search
        pos.click('manual search')
        msg = pos.read_status_line(timeout=self.short_wait_time)
        if msg == None:
            tc_fail("Status line message did not exist after clicking manual search.")
        elif "enter account id" not in msg.lower():
            tc_fail("Status line message for manual search was '" + str(msg) + "' instead of 'Enter Account ID'.")
        
        pos.enter_keypad('6666', after='enter')

        msg = pos.read_message_box(timeout=self.short_wait_time)
        if msg == None:
            tc_fail("No message appeared in the message box.")
        elif not "not found" in msg.lower():
            tc_fail("Incorrect error message: " + str(msg) + ".  Should include the string 'not found'.")
        
        pos.click('ok')

        if self.on_loc_acct_screen(timeout=self.long_wait_time):
            self.log.info("HTML POS followed proper protocol on nonexistent local account entry!")
        else:
            tc_fail("Did not return to local account paid in screen.")


    @test
    def details(self):
        """
        Make sure that the details come up and
        that the message box displays all the correct info
        """
        # Make sure that HTML POS is on the loc acct paid in screen
        if self.on_main_screen(timeout=self.short_wait_time):
            pos.click('loc acct paid in')
            self.log.info("On the local account paid in screen...")
        elif self.on_loc_acct_screen(timeout=self.short_wait_time):
            self.log.info("On the local account paid in screen...")
        else:
            tc_fail("Started on an unknown screen.")

        # Select the local account
        pos.select_local_account('DG, Inc.')

        # Check that all of the correct details are shown
        msg_checker = ['Account ID: 1', 'Account Name: DG, Inc.', 'Sub-Account ID: 00000000000',\
         'Description: aDescription', 'Status: Enabled', 'Vehicle ID: aVehicleRegNo', 'Account Balance:',\
         'Account Credit Limit: $500.00']

        pos.click('details')
        
        msg = pos.read_message_box(timeout=self.short_wait_time)
        if msg == None:
            tc_fail("No message displayed in the details message box.")
        for item in msg_checker:
            if item not in msg:
                pos.click('ok')
                tc_fail("The following should be displayed when you click details but isn't: " + item)
        
        pos.click('ok')

        if self.on_loc_acct_screen(timeout=self.short_wait_time):
            self.log.info("Successfully displayed details!")
        else:
            tc_fail("Did not return to local account paid in screen after clicking 'ok' on details message box.")


    @test
    def cancel_list_screen(self):
        """
        Cancel on the account list screen and make sure
        it exists local account paid in
        """
        # Make sure that HTML POS is on the loc acct paid in screen
        if self.on_main_screen(timeout=self.short_wait_time):
            pos.click('loc acct paid in')
            self.log.info("On the local account paid in screen...")
        elif self.on_loc_acct_screen(timeout=self.short_wait_time):
            self.log.info("On the local account paid in screen...")
        else:
            tc_fail("Started on an unknown screen.")

        # Click cancel and make sure it exists local account paid in
        self.log.info("Clicking cancel...")
        pos.click('cancel')

        if self.on_main_screen(timeout=self.short_wait_time):
            self.log.info("Successfully cancelled local account paid in!")
        else:
            tc_fail("Did not return to main screen after clicking cancel.")


    @test
    def cancel_money_screen(self):
        """
        Click confirm and then click cancel on the keypad
        on the screen where you input the amount of money
        to be paid in.  Make sure it exits the transaction
        """
        # Make sure that HTML POS is on the loc acct paid in screen
        if self.on_main_screen(timeout=self.short_wait_time):
            pos.click('loc acct paid in')
            self.log.info("On the local account paid in screen...")
        elif self.on_loc_acct_screen(timeout=self.short_wait_time):
            self.log.info("On the local account paid in screen...")
        else:
            tc_fail("Started on an unknown screen.")

        # Navigate to the monetary input screen and cancel
        pos.click('confirm')
        msg = pos.read_status_line(timeout=self.short_wait_time)
        if msg == None:
            tc_fail("Status line message did not exist after clicking confirm.")
        elif not "enter" in msg.lower() or not "amount" in msg.lower():
            tc_fail("Status line message was '" + str(msg) + "' instead of 'Enter an Amount' or 'Enter Amount'\
             or any other phrase that includes the words both enter and amount.")
        
        pos.click_keypad('cancel')

        if self.on_main_screen(timeout=self.long_wait_time):
            msg = pos.read_journal_watermark(timeout=self.short_wait_time)
            if msg == None:
                tc_fail("No journal watermark displayed.")
            elif not "transaction voided" in msg.lower():
                tc_fail("Journal watermark was '" + str(msg) + "' instead of 'Transaction Voided.")
            self.log.info("Successfully cancelled local account paid in!")
        else:
            tc_fail("Did not return to main screen after clicking cancel.")


    @test
    def enter_without_entry(self):
        """
        Click enter on the manual search screen
        and also the confirm/screen where you input an
        amount of money and make sure the right error messages
        appear
        """
        # Make sure that HTML POS is on the loc acct paid in screen
        if self.on_main_screen(timeout=self.short_wait_time):
            pos.click('loc acct paid in')
            self.log.info("On the local account paid in screen...")
        elif self.on_loc_acct_screen(timeout=self.short_wait_time):
            self.log.info("On the local account paid in screen...")
        else:
            tc_fail("Started on an unknown screen.")

        # Check that click enter with no keypad entry in manual search shows error message
        pos.click('manual search')
        msg = pos.read_status_line(timeout=self.short_wait_time)
        if msg == None:
            tc_fail("Status line message did not exist after clicking manual search.")
        elif "enter account id" not in msg.lower():
            tc_fail("Status line message for manual search was '" + str(msg) + "' instead of 'Enter Account ID'.")
        
        pos.click('enter')

        msg = pos.read_message_box(timeout=self.short_wait_time)
        if msg == None:
            tc_fail("No error message in the message box (manual search screen).")
        elif not "not found" in msg.lower():
            tc_fail("Incorrect error message displayed (manual search screen): " + str(msg))
        self.log.info("Correct error message showed up for manual search without keypad entry!")
    
        pos.click('ok')

        if self.on_loc_acct_screen(timeout=self.short_wait_time):
            self.log.info("Returned to main local account paid in screen after clicking ok on the manual search error message...")
        else:
            tc_fail("Did not return to main local account paid in screen after clicking ok on manual search error message.")

        # Check that clicking enter with no keypad entry on confirm screen shows error message
        pos.click('confirm')

        msg = pos.read_status_line(timeout=self.short_wait_time)
        if msg == None:
            tc_fail("Status line message did not exist after clicking confirm.")
        elif not "enter" in msg.lower() or not "amount" in msg.lower():
            tc_fail("Status line message was '" + str(msg) + "' instead of 'Enter an Amount' or 'Enter Amount'\
             or any other phrase that includes the words both enter and amount.")

        pos.click('enter')

        msg = pos.read_message_box(timeout=self.short_wait_time)
        if msg == None:
            tc_fail("No error message in the message box (confirm screen).")
        elif not "enter" in msg.lower() or not "amount" in msg.lower():
            tc_fail("Incorrect error message displayed (confirm screen): " + str(msg))
        self.log.info("Correct error message showed up when you click enter without keypad entry after clicing confirm!")

        pos.click('ok')
        

    @teardown
    def teardown(self):
        """
        Performs cleanup
        """
        msg = pos.read_status_line()
        if not msg == None:
            if "enter" in msg.lower():
                pos.click('cancel')
        if self.on_loc_acct_screen(2):
            pos.click('cancel')
        if self.on_main_screen(2):
            self.log.info("Returned to the main screen.")
        pos.close()


    def on_loc_acct_screen(self, timeout=default_timeout):
        """
        Helper function to detect whether HTML POS
        is on the local account paid in screen
        """
        return pos.is_element_present(self.details_button, timeout=timeout)


    def on_main_screen(self, timeout=default_timeout):
        """
        Helper function to detect whether HTML POS
        is on the main logged-in screen (mainly makes it
        easier to follow in the test cases above)
        """
        return pos.is_element_present(self.paid_in_button, timeout=timeout)


    def status_line_contains(self, string, timeout=default_timeout):
        """
        Helper function to check the status line
        until it contains the given string
        """
        start_time = time.time()
        period = timeout / 50.0
        while time.time() - start_time <= timeout:
            time.sleep(period)
            if string in pos.read_status_line():
                return True
        else:
            return False       
