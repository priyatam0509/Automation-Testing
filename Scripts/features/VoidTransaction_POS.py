"""
    File name: VoidTransaction_POS.py
    Tags:
    Description: This script tests the void transaction button on HTML 5 POS.
    Author: David Mayes & Logan Hornbuckle
    Date created: 2020-02-07
    Date last modified: 2020-02-07 
    Python Version: 3.7
"""

import logging, time
from app import Navi, pos
from app.framework.tc_helpers import setup, test, teardown, tc_fail


class VoidTransaction_POS():
    """
    Test class that provides an interface for testing
    """

    def __init__(self):
        self.log = logging.getLogger()


    @setup
    def setup(self):
        """
        Performs an initialization that isn't default
        """
        # Connect & sign-in to htmlPOS
        pos.connect()
        pos.sign_on()


    @test
    def test_voidPositiveItem(self):
        """
        Testing voiding a simple transaction w/ a positive balankce
        """
        # Add an item for purchase
        pos.add_item("Item 2")

        # Confirm balance reads $5.00
        _confirm_balance()
        
        pos.void_transaction()


    @test
    def test_voidNegativeItem(self):
        """
        Testing voiding a simple transaction w/ negative balance
        """
        # Add a negatively priced item
        pos.add_item("Negative Item")

        # Confirm balance reads -$5.00
        _confirm_balance('-$5.00')
        
        pos.void_transaction()


    @test
    def test_voidTaxItem(self):
        """
        Testing voiding a simple transaction w/ a positive balankce
        """
        # Add an item for purchase
        pos.add_item("Tax 1")

        # Confirm balance reads $11.00
        _confirm_balance('$11.00')

        pos.void_transaction()
        

    @test
    def test_voidMultipleItems(self):
        """
        Testing voiding a simple transaction w/ multiple items
        """
        # Add an items for purchase
        pos.add_item("Item 2")
        pos.add_item("Tax 1")
        pos.add_item("Negative Item")

        # Confirm balance reads $11.00
        _confirm_balance('$11.00')

        pos.void_transaction()
   

    @test
    def test_cancelVoid(self):
        """
        Checks whether "No" button on the prompt after clicking the void transaction button successfully cancels the attempt to void the transaction
        """
        # Add item
        pos.add_item("Item 2")

        # Confirm balance reads $5.00
        _confirm_balance()
        
        pos.click_function_key("void transaction")

        # TODO: remove after pos drop 4 (PSC-2873)
        # Account for message box if still in POShtml build
        msg = pos.read_message_box(timeout=2)
        if msg and "Are you sure" in msg:
            pos.click_message_box_key("No")
        else:
            pos.click_keypad("Cancel")

        # Check watermark to ensure void was cancelled
        if 'TRANSACTION VOIDED' in pos.read_journal_watermark():
            tc_fail("Unable to confirm void was cancelled")

    
    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends
        """
        # Void unfinished transaction
        pos.void_transaction()


# ##########################################################################################
# #################################### HELPER FUNCTIONS ####################################
# ##########################################################################################


def _confirm_balance(balance='5.00', sleep_time = 5):

    # confirm till balance, wait for balance to update
    start_time = time.time()
    while time.time() - start_time <= sleep_time:
        if balance in pos.read_balance()['Total']:
            break
    else:
        tc_fail("Unable to confirm balance")

    return True