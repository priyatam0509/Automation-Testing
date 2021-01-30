"""
    File name: VoidTender_POS.py
    Tags:
    Description: 
    Author: Gene Todd
    Date created: 2020-04-16 09:40:28
    Date last modified: 
    Python Version: 3.7
"""

import logging, time
from app import Navi, mws, pos, system
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class VoidTender_POS():
    """
    Description: Test class that provides an interface for testing.
    """

    def __init__(self):
        self.log = logging.getLogger()

    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        """
        #if not system.restore_snapshot():
        #    self.log.debug("No snapshot to restore, if this is not expected please contact automation team")
        pos.connect()
        pos.sign_on()

    @test
    def test_voidCash(self):
        """
        Basic void tender case using cash. Reason codes enabled.
        """
        self.prep_trans()
        
        self.log.info("Adding tender")
        pos.enter_keypad(100, after="Enter")
        
        # Assume the tender has already been selected when it was added
        self.log.info("Voiding cash tender")
        pos.click_tender_key("Void")
        # Confirms the reason codes appeared
        pos.select_list_item("Cashier Error")
        pos.click("Enter")
        
        # Confirm the tender is gone
        jrnl = pos.read_transaction_journal()
        for line in jrnl:
            if "Cash" in line:
                tc_fail("Cash tender found in transaction after being voided")
        self.log.info("Cash confirmed no longer in transaction journal")
        
        # Pay out the transaction for the next test
        self.log.info("Paying out transaction")
        pos.click_tender_key("Exact Change")
        pos.is_element_present(pos.controls['function keys']['tools'], timeout=5)
           
    @test
    def test_noReasonCodes(self):
        """
        Tests our ability to void tenders without reason codes enabled
        """
        # Disable reason codes
        pos.close()
        self.log.info("Removing void tender reason code")
        Navi.navigate_to('Register Group Maintenance')
        mws.click_toolbar('Change')
        mws.select_tab('Reason Codes')
        mws.set_value('Available Functions', 'Void Tender')
        mws.set_value('Require Reason Code', False)
        mws.click_toolbar('Save')
        pos.connect()
        
        tries = 0
        while mws.get_top_bar_text() and tries < 10:
            self.log.info("Waiting for reload options...")
            tries = tries + 1
            time.sleep(.5)
        
        self.prep_trans()
        
        self.log.info("Adding tender")
        pos.enter_keypad(100, after="Enter")
        
        # Assume the tender has already been selected when it was added
        self.log.info("Voiding cash tender")
        pos.click_tender_key("Void")
        
        # Wait for void to process
        pos.is_element_present(pos.controls['pay']['exact_amount'], timeout=5)
        
        # Confirm the tender is gone
        jrnl = pos.read_transaction_journal()
        for line in jrnl:
            if "Cash" in line:
                tc_fail("Cash tender found in transaction after being voided")
        self.log.info("Cash confirmed no longer in transaction journal")
        
        # Pay out the transaction for the next test
        self.log.info("Paying out transaction")
        pos.click_tender_key("Exact Change")
        pos.is_element_present(pos.controls['function keys']['tools'], timeout=5)

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        pos.close()
        # Re-enable reason codes
        self.log.info("Removing void tender reason code")
        Navi.navigate_to('Register Group Maintenance')
        mws.click_toolbar('Change')
        mws.select_tab('Reason Codes')
        mws.set_value('Available Functions', 'Void Tender')
        mws.set_value('Require Reason Code', True)
        mws.click_toolbar('Save')
        
    def prep_trans(self):
        """
        Helper function for adding an item and getting to the pay screen for tests
        """
        self.log.info("Setting up transaction for VoidTender test...")
        pos.click("Item 1")
        pos.enter_keypad(1000, after="Enter")
        pos.click("Pay")
        self.log.info("... Setup complete")
        