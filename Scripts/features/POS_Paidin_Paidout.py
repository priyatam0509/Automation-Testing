"""
    File name: POS_Paid_In.py.py
    Tags:
    Description: Sript to test the functionality of the "Paid In" and "Paid Out" buttons on HTML POS.
    Author: David Mayes
    Date created: 03-16-2020
    Date last modified: 03-23-2020
    Python Version: 3.7
"""

import logging, time
from app import Navi, mws, pos, system
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class POS_Paidin_Paidout():
    """
    Description: Test class that provides an interface for testing.
    """

    def __init__(self):
        """
        Initializes the POS_Paidin_Paidout class.
        """
        # The logging object. 
        # Example: self.log.info(f"Current value of var: {my_var}")
        self.log = logging.getLogger()
        self.cash_button = pos.controls['pay']['type'] % 'cash'
        self.wait_time = 1

    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        """
        # if not system.restore_snapshot():
        #     self.log.debug("No snapshot to restore, if this is not expected please contact automation team")
        pos.connect()
        pos.sign_on()


    @test
    def paidin_with_account(self):
        """
        Attempt a paid in transaction with income account configured
        """
        pos.click('paid in')
        
        # Give time for the screen to change
        pos.is_element_present(self.cash_button, timeout=self.wait_time)

        # Make sure now in a paid in transaction
        msg = pos.read_transaction_journal(only_selected=True)
        if not msg:
            tc_fail("Did not enter a paid in transaction.")
        try:
            if not "paid in" in msg[0].lower():
                if pos.is_element_present('cancel'):
                    pos.click('cancel')
                tc_fail("Did not display the proper message in the transaction journal after clicking paid in.")
        except IndexError:
            if pos.is_element_present('cancel'):
                    pos.click('cancel')
            tc_fail("No message displayed in the transaction journal.")

        # Make sure you can't enter 0 as paid in amount
        pos.click('enter')
        msg = pos.read_message_box()
        if not msg:
            pos.click('cancel')
            tc_fail("Did not display error message when trying to do a paid in transaction of $0.")
        if not "please enter" in msg.lower():
            pos.click('ok')
            tc_fail("Did not display the correct error message.")

        # Exit error message
        pos.click('ok')

        # Enter amount to be paid in
        pos.enter_keypad('101', after='enter')

        # Make sure the transaction is complete
        msg = pos.read_journal_watermark()
        if not msg or not msg.lower() == "transaction complete":
            tc_fail("The paid in transaction did not complete.")
        # TODO if ability to read receipt_item is added, can check to make sure id of account, etc. is correct

        # Make sure receipt is properly made
        keywords = ["Paid In", "Income Acct", "Cash", "1.01"]
        self._check_receipt_for(keywords)        

        
    @test
    def paidout_with_account(self):
        """
        Attempt a paid out transaction with expense account configured
        """
        pos.click('paid out')

        # Give time for the screen to change
        pos.is_element_present(self.cash_button, timeout=self.wait_time)

        # Make sure now in a paid out transaction
        msg = pos.read_transaction_journal(only_selected=True)
        if not msg:
            tc_fail("Did not enter a paid out transaction.")
        try:
            if not "paid out" in msg[0].lower():
                if pos.is_element_present('cancel'):
                    pos.click('cancel')
                tc_fail("Did not display the proper message in the transaction journal after clicking paid out.")
        except IndexError:
            if pos.is_element_present('cancel'):
                pos.click('cancel')
            tc_fail("No message displayed in the transaction journal.")

        # Make sure you can't enter 0 as paid out amount
        pos.click('enter')
        msg = pos.read_message_box()
        if not msg:
            pos.click('cancel')
            tc_fail("Did not display error message when trying to do a paid out transaction of $0.")
        if not "please enter" in msg.lower():
            pos.click('ok')
            tc_fail("Did not display the correct error message.")

        # Exit error message
        pos.click('ok')

        # Enter amount to be paid out
        pos.enter_keypad('100', after='enter')

        # Make sure the transaction is complete
        msg = pos.read_journal_watermark()
        if not msg or not msg.lower() == "transaction complete":
            tc_fail("The paid in transaction did not complete.")

        # Make sure receipt is properly made
        keywords = ["Paid Out", "ExpenseAcct", "Cash", "1.00"]
        self._check_receipt_for(keywords)
    

    @test
    def cancel_paidin(self):
        """
        Make sure the cancel button works on paid in
        """
        pos.click('paid in')
        pos.click('cancel')

        # Make sure paid in was canceled
        watermark = pos.read_journal_watermark()
        if not watermark.lower() == "transaction voided":
            tc_fail("Clicking cancel did not properly void a paid in transaction.")

    
    @test
    def cancel_paidout(self):
        """
        Make sure the cancel button works on paid out
        """
        pos.click('paid out')
        pos.click('cancel')

        # Make sure paid out was canceled
        watermark = pos.read_journal_watermark()
        if not watermark.lower() == "transaction voided":
            tc_fail("Clicking cancel did not properly void a paid out transaction.")


    @test
    def mws_toggle(self):
        """
        Make sure toggling a tender for paid ins/paid outs in the MWS changes whether it appears in paid ins/paid outs
        """
        # Remove all tender keys
        self.log.info("Attempting to de-toggle tender keys on paid ins/paid out.")
        pos.close()
        Navi.navigate_to("Tender Maintenance")
        mws.set_value("Tenders", "Cash")
        mws.click_toolbar("Change")
        mws.select_tab("Register Groups")
        mws.set_value("Paid In", False)
        mws.set_value("Paid Out", False)
        mws.click_toolbar("Save")
        time.sleep(2)

        mws.set_value("Tenders", "Check")
        mws.click_toolbar("Change")
        mws.select_tab("Register Groups")
        mws.set_value("Paid In", False)
        mws.set_value("Paid Out", False)
        mws.click_toolbar("Save")
        mws.click_toolbar("Exit")
        pos.connect()

        # Make sure no tender keys appear
        self.log.info("Checking that the tender keys don't appear.")
        pos.click('paid in')
        if self._tender_keys_present():
            pos.click('cancel')
            tc_fail("Tender key buttons showed up after clicking paid in.")
        msg = pos.read_message_box()
        if not msg:
            tc_fail("No error message was displayed indicating no tenders are configured for use on paid in.")
        pos.click('ok')

        pos.click('paid out')
        if self._tender_keys_present():
            pos.click('cancel')
            tc_fail("Tender key buttons showed up after clicking paid out.")
        msg = pos.read_message_box()
        if not msg:
            tc_fail("No error message was displayed indicating no tenders are configured for use on paid out.")
        pos.click('ok')

        # Add back tender keys -- cash & check for paid in, cash for paid out
        self.log.info("Attempting to retoggle the tender keys.")
        pos.close()
        Navi.navigate_to("Tender Maintenance")
        mws.set_value("Tenders", "Cash")
        mws.click_toolbar("Change")
        mws.select_tab("Register Groups")
        mws.set_value("Paid In", True)
        mws.set_value("Paid Out", True)
        mws.click_toolbar("Save")
        time.sleep(2)

        mws.set_value("Tenders", "Check")
        mws.click_toolbar("Change")
        mws.select_tab("Register Groups")
        mws.set_value("Paid In", True)
        mws.click_toolbar("Save")
        mws.click_toolbar("Exit")
        pos.connect()

        # Make sure cash & check tender keys appear on paid in, cash on paid out
        self.log.info("Checking that the tender keys appear.")
        pos.click('paid in')
        if not pos.is_element_present(pos.controls['pay']['type'] % 'cash') or not pos.is_element_present(pos.controls['pay']['type'] % 'check'):
            pos.click('cancel')
            tc_fail("After toggling the cash and check tender keys, they did not appear on the paid in screen.")
        pos.click('cancel')
        
        pos.click('paid out')
        if not pos.is_element_present(pos.controls['pay']['type'] % 'cash'):
            pos.click('cancel')
            tc_fail("After toggling the cash tender key, it did not appear on a paid out transaction.")
        pos.click('cancel')


    def _tender_keys_present(self):
        if (pos.is_element_present(pos.controls['pay']['type'] % 'cash') or
        pos.is_element_present(pos.controls['pay']['type'] % 'check') or
        pos.is_element_present(pos.controls['pay']['type'] % 'card') or 
        pos.is_element_present(pos.controls['pay']['type'] % 'credit') or 
        pos.is_element_present(pos.controls['pay']['type'] % 'debit') or 
        pos.is_element_present(pos.controls['pay']['type'] % 'ebt cash') or
        pos.is_element_present(pos.controls['pay']['type'] % 'ebt food') or
        pos.is_element_present(pos.controls['pay']['type'] % 'imprinter') or
        pos.is_element_present(pos.controls['pay']['type'] % 'other') or
        pos.is_element_present(pos.controls['pay']['type'] % 'ucc')):
            return True
        else:
            return False


    def _check_receipt_for(self, array):
        for string in array:
            if not pos.check_receipt_for(string, verify=False):
                pos.click('Speed Keys')
                tc_fail("The string '" + string + "' was not included on the receipt.")


    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        pos.close()
