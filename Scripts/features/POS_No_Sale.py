"""
    File name: POS_No_Sale.py
    Tags:
    Description: Test Script for testimg the No Sale button in HTML POS.
    Author: David Mayes
    Date created: 2020-04-13 10:42:42
    Date last modified: 2020-04-13
    Python Version: 3.7
"""

import logging, time
from app import Navi, mws, pos, system
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class POS_No_Sale():
    """
    Class that tests the No Sale button
    """

    def __init__(self):
        """
        Initializes the POS_No_Sale class
        """
        # The logging object. 
        # Example: self.log.info(f"Current value of var: {my_var}")
        self.log = logging.getLogger()
        self.journal_watermark = pos.controls['receipt journal']['watermark']
        self.cancel_button = pos.controls['keypad']['cancel']
        self.paid_in_button = pos.controls['function keys']['paid in']
        self.wait_time = 5
        self.reload_time = 10


    @setup
    def setup(self):
        """
        Performs initial setup and connections/log on
        """
        # if not system.restore_snapshot():
        #     self.log.debug("No snapshot to restore, if this is not expected please contact automation team")
        mws.sign_on()
        pos.connect()
        pos.sign_on()


    @test
    def without_reason_codes(self):
        """
        Make sure a no sale transaction works without reason codes
        configured in register group maintenance
        """
        # Make sure reason codes are configured to not show up
        self.log.info("Setting no sale to not use reason codes...")
        Navi.navigate_to('Register Group Maintenance')
        mws.click_toolbar('Change')
        mws.select_tab('Reason Codes')
        mws.set_value('Available Functions', 'No Sale')
        mws.set_value('Require Reason Code', False)

        self.log.info("Saving reason code settings...")
        if not mws.click_toolbar('Save'):
            tc_fail("Failed to save reason code settings.")

        if not self._wait_for_reload(self.reload_time):
            tc_fail("Did not reload register within " + str(self.reload_time) + " seconds.")
        self.log.info("Registers successfully reloaded...")

        # Do a no sale transaction
        self.log.info("Doing a no sale transaction...")
        pos.click('no sale')

        # Check that the transaction journal shows the right stuff
        if pos.is_element_present(self.paid_in_button, timeout = self.wait_time):
            if self._journal_watermark_is('transaction complete', timeout = self.wait_time):
                self.log.info("Transaction journal watermark is correct...")
            else:
                tc_fail("The correct watermark did not appear on the transaction journal.")

        if self._transaction_journal_contains(string="no sale", element=1, timeout=self.wait_time):
            self.log.info("Successfully did a no sale transaction without reason codes!")
        else:
            tc_fail("Did not properly display no sale receipt item in the transaction journal.")

    
    @test
    def with_reason_codes(self):
        """
        Make sure a no sale transaction works with reason codes
        configured in register group maintenance
        """
        # Make sure reason codes are configured to show up
        self.log.info("Setting no sale to use reason codes...")
        Navi.navigate_to('Register Group Maintenance')
        mws.click_toolbar('Change')
        mws.select_tab('Reason Codes')
        mws.set_value('Available Functions', 'No Sale')
        mws.set_value('Require Reason Code', True)

        self.log.info("Saving reason code settings...")
        if not mws.click_toolbar('Save'):
            tc_fail("Failed to save reason code settings.")

        if not self._wait_for_reload(self.reload_time):
            tc_fail("Did not reload register within " + str(self.reload_time) + " seconds.")
        self.log.info("Registers successfully reloaded...")

        # Do a no sale transaction
        self.log.info("Attempting to do a no sale transaction...")
        pos.click('no sale')
        if self._status_line_contains('reason', timeout = self.wait_time):
            pos.click('enter')
        else:
            tc_fail("Did not change to the no sale screen/status message did not appear.")

        # Check that the transaction journal shows the right stuff
        if pos.is_element_present(self.paid_in_button, timeout = self.wait_time):
            if self._journal_watermark_is('transaction complete', timeout = self.wait_time):
                self.log.info("Transaction journal watermark is correct...")
            else:
                tc_fail("The correct watermark did not appear on the transaction journal.")
        else:
            tc_fail("Did not complete the no sale transaction and return to the home screen.")

        if self._transaction_journal_contains(string="no sale", element=1, timeout=self.wait_time)\
         and self._transaction_journal_contains(string="cashier error", element=1, timeout=self.wait_time):
            self.log.info("Successfully did a no sale transaction with reason codes!")
        else:
            tc_fail("Did not properly display no sale receipt item in the transaction journal.")


    @test
    def cancel(self):
        """
        Click the cancel button during a no sale transaction
        when reason codes are assembled and make sure it cancels
        the no sale transaction
        """
        # Start a no sale transaction
        self.log.info("Starting a no sale transaction...")
        pos.click('no sale')

        # Attempt to cancel to no sale transaction
        self.log.info("Attempting to cancel the no sale transaction...")
        if self._status_line_contains('reason', timeout = self.wait_time):
            pos.click('cancel')
        else:
            tc_fail("Did not change to the no sale screen/status message did not appear.")

        # TODO: Change this to be "transaction voided" once it's
        # changed to have that watermark instead
        # Make sure the no sale transaction was cancelled
        if pos.is_element_present(self.paid_in_button, timeout = self.wait_time):
            if self._journal_watermark_is('transaction complete', timeout = self.wait_time):
                self.log.info("Journal watermark is 'Transaction Complete'.  This is good enough for now, but probably eventually should become 'Transaction Voided'...")
            elif self._journal_watermark_is('transaction voided', timeout = self.wait_time):
                self.log.info("Transaction journal watermark is correct...")
            else:
                tc_fail("The correct watermark did not appear on the transaction journal.")
        else:
            tc_fail("Did not cancel the no sale transaction and return to the home screen.")



    @test
    def check_electronic_journal(self):
        """
        Make sure that the right notes regarding the previous 3
        uses of no sale are recorded in the electronic journal
        """
        # Make sure that the most recent version of the
        # electronic journal is updated as an html file
        Navi.navigate_to('Journal Reports')
        mws.click_toolbar('Select')
        mws.click_toolbar('Print Preview')

        # Wait for the file to update
        if self._wait_for_reload(self.reload_time):
            self.log.info("Electronic journal updated...")
        else:
            tc_fail("The electronic journal was not updated.")

        # Open the file
        self.log.info("Reading electronic journal...")
        # NOTE: file location may change later on
        with open('C:/Passport/advpos/Reports/eng/html/ElectronicJournalReport.htm', 'r') as ej:
            rows = list(ej)
            ej.close()

        # Check that the electronic journal logged the no sales
        logged_cancel = False
        cancel_index = 0
        logged_reason_code = False
        reason_code_index = 0
        logged_no_reason_code = False
        no_reason_code_index = 0
        index = len(rows) - 1

        for text_row in rows[::-1]:
            if "sign-on" in text_row.lower():
                break
            if not logged_cancel and "end no sale" in text_row.lower():
                logged_cancel = True
                cancel_index = index
            elif not logged_cancel and "cashier error" in text_row.lower():
                tc_fail("Logged no sale with reason code after cancel.")
            elif not logged_reason_code and "cashier error" in text_row.lower():
                logged_reason_code = True
                reason_code_index = index
            elif not logged_cancel and "transaction complete" in text_row.lower():
                tc_fail("Logged no sale without reason code after cancel.")
            elif not logged_reason_code and "transaction complete" in text_row.lower():
                tc_fail("Logged no sale without reason code after no sale with reason code.")
            elif not logged_no_reason_code and "transaction complete" in text_row.lower()\
             and not "reason" in text_row:
                logged_no_reason_code = True
                no_reason_code_index = index
                break
            index -= 1
        
        if  len(rows) - no_reason_code_index > 200:
            tc_fail("The no sale transactions are logged to far back in the electronic journal.  Something is wrong.")

        if logged_cancel and logged_reason_code and logged_no_reason_code:
            if cancel_index > reason_code_index and reason_code_index > no_reason_code_index:
                self.log.info("No sale transactions correctly logged in the electronic journal!")
            else:
                tc_fail("No sale transactions were logged out of order in the transaction journal.")
        else:
            tc_fail("Not all of the no sale transactions were logged/logged with the correct messages in the electronic journal.")
        

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends
        """
        pos.close()
        mws.sign_off()


    def _status_line_contains(self, string, timeout):
        """
        Helper function for checking whether the screen has changed
        but integrating a timeout (not just a one time time read -- keeps
        reading until it contains the string argument given or it times out)
        """
        start_time = time.time()
        while time.time() - start_time <= timeout:
            if string in pos.read_status_line():
                return True
        else:
            return False


    def _wait_for_reload(self, timeout):
        """
        Helper function to give time for the MWS to reload the registers
        before clicking something like no sale (which would have old settings
        if the reload was not complete)
        """
        time.sleep(0.5)
        start_time = time.time()
        while time.time() - start_time <= timeout:
            msg = mws.get_top_bar_text()
            if not msg:
                return True
        else:
            return False


    def _journal_watermark_is(self, string, timeout):
        """
        Helper function to check for the correct journal watermark
        over a period of time (rather than just checking once and then failing
        when it isn't correct)
        """
        start_time = time.time()
        while time.time() - start_time <= timeout:
            msg = pos.read_journal_watermark()
            if not msg:
                continue
            elif string.lower() in msg.lower():
                return True
        else:
            return False

    
    def _transaction_journal_contains(self, string, element, timeout):
        """
        Helper function to check the transaction journal
        for an element that contains the string "string"
        at the index determined by "element"
        """
        start_time = time.time()
        while time.time() - start_time <= timeout:
            try:
                msg = pos.read_transaction_journal(element = element, timeout = 1)[0]
                if not msg:
                    continue
                elif string.lower() in msg.lower():
                    return True
                continue
            except IndexError:
                continue
        else:
            return False