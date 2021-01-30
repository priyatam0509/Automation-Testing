"""
    File name: Plus_Minus_POS.py
    Tags:
    Description: Script to test the plus and minus buttons on HTLM POS
    Author: David Mayes
    Date created: 02-28-2020
    Date last modified: 03-06-2020
    Python Version: 3.7
"""

import logging, time
from app import Navi, mws, pos, system
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class Plus_Minus_POS():
    """
    Description: Test class that provides an interface for testing.
    """

    def __init__(self):
        """
        Initializes the Template class.
        """
        # The logging object. 
        # Example: self.log.info(f"Current value of var: {my_var}")
        self.log = logging.getLogger()


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
    def click_plus(self):
        """
        Click the plus button and make sure it increments
        the selected item's quantity by one
        """
        # Add a generic item
        pos.add_item()

        # Click the plus button
        pos.click('+')
    
        # Wait for transaction journal to update
        time.sleep(2)

        # Check that the item's quantity was incremented by one
        # [1][4] = [quantity + price string][number representing quantity]
        # in the list read_transaction_journal returns
        try:
            item_char = pos.read_transaction_journal(1)[1][4]
        except IndexError:
            tc_fail("Transaction journal does not look like click_plus expected.")
        if not item_char == '2':
            pos.pay()
            tc_fail("Did not successfully increment the item's quantity by one.")
        pos.pay()


    @test
    def click_minus(self):
        """
        Click the minus button and make sure it decrements
        the selected item's quantity by one
        """
        # Add a generic item
        pos.add_item()

        # Increase quantity to 3
        pos.click('Change Item Qty')
        pos.enter_keypad('3', after='enter')

        # Wait for transaction journal to update
        time.sleep(2)

        # Check that the item's quantity was incremented by one
        # [1][4] = [quantity + price string][number representing quantity]
        # in the list read_transaction_journal returns
        try:
            item_char = pos.read_transaction_journal(1)[1][4]
        except IndexError:
            tc_fail("Transaction journal does not look like click_minus expected.")
        if not item_char == '3':
            pos.pay()
            tc_fail("Did not successfully change item's quantity to 3 before testing the minus button.")

        # Click the minus button
        pos.click('-')
        
        # Wait for transaction journal to update
        time.sleep(2)

        # Check that the item's quantity was decremented by one
        # [1][4] = [quantity + price string][number representing quantity]
        # in the list read_transaction_journal returns
        try:
            item_char = pos.read_transaction_journal(1)[1][4]
        except IndexError:
            tc_fail("Transaction journal does not look like click_minus expected.")
        if not item_char == '2':
            pos.pay()
            tc_fail("Did not successfully decrement the item's quantity.")
        pos.pay()


    @test
    def above_max(self):
        """
        Attempt to increment an item that already has max quantity
        and make sure it is not allowed
        """
        # Add a generic item
        pos.add_item()

        # Change item's quantity to max
        pos.click('Change Item Qty')
        pos.enter_keypad('25', after='enter')

        # Wait for transaction journal to update
        time.sleep(2)

        # Check that the item's quantity is 25
        # [1][3:5] = [quantity + price string][number representing quantity]
        # in the list read_transaction_journal returns
        try:
            item_char = pos.read_transaction_journal(1)[1][3:5]
        except IndexError:
            tc_fail("Transaction journal does not look like above_max expected.")
        if not item_char == '25':
            pos.pay()
            tc_fail("Did not successfully change item quantity to 25 for testing incrementing over max allowed quantity.")

        # Attempt to increment above the max
        pos.click('+')
        if not "max" in pos.read_message_box():
            pos.pay()
            tc_fail("Did not display a message about exceeding max item quantity.")
        pos.click('ok')
        pos.pay()


    @test
    def above_max_total_price(self):
        """
        Attempt to increment past the total allowed price
        for a transaction
        """
        # Get the price up to the max
        pos.add_item(item='Dept 1', method='dept key', price='999900')
        pos.click('Change Item Qty')
        pos.enter_keypad('10', after='enter')
        pos.add_item(item='Dept 1', method='dept key', price='501')

        # Attempt to exceed the max
        pos.click('+')
        if not "Unable to change quantity on item" in pos.read_message_box():
            pos.pay()
            tc_fail("Did not display error message when clicking + increased total price over the max.")
        pos.click('ok')
        pos.void_transaction()


    @test
    def only_in_transaction(self):
        """
        Make sure that the plus and minus buttons
        only exist when there's actually a transaction
        (DOES NOT test all screens -- tests screens that
        are more likely to have this issue b/c they have
        the keypad present)
        """
        # Used to give a brief pause so that
        # add_item() has access to the buttons it clicks
        wait_time = 0.5

        # Execute normal transaction and pay
        # then check for + / - buttons
        pos.add_item()
        if not _plus_and_minus_exist():
            _fail_and_end("+ / - button wasn't present during transaction.")
        pos.pay()
        if _plus_or_minus_exists():
            _fail_and_end("+ / - button persisted after paying.")

        # Void a transaction then check for
        # + / - buttons
        time.sleep(wait_time)
        pos.add_item()
        if not _plus_and_minus_exist():
            _fail_and_end("+ / - button wasn't present during transaction.")
        pos.click('Void Transaction')
        if _plus_or_minus_exists():
            _fail_and_end("+ / - button persisted after voiding transaction.")
        pos.click('cancel')

        # Look at the pay screen
        time.sleep(wait_time)
        pos.add_item()
        if not _plus_and_minus_exist():
            _fail_and_end("+ / - button wasn't present during transaction.")
        pos.click('Pay')
        if _plus_or_minus_exists():
            _fail_and_end("+ / - button was present on the pay screen.")
        pos.click('cancel')

        # Look at the overide screen
        pos.click('Override')
        if _plus_or_minus_exists():
            _fail_and_end("+ / - button was present on the override screen.")
        pos.click('cancel')

        # Look at the change item qty screen
        pos.click('Change Item Qty')   
        if _plus_or_minus_exists():
            _fail_and_end("+ / - button was present on the change item qty screen.")
        pos.click('cancel')

        # Look at the price check screen
        pos.click('Price Check')
        if _plus_or_minus_exists():
            _fail_and_end("+ / - button was present on the price check screen.")
        pos.click('cancel')

        # Look at the tax modify screen
        pos.click('Tax Modify')
        if _plus_or_minus_exists():
            _fail_and_end("+ / - button was present on the tax modify screen.")
        pos.click('cancel')

        # Framework currently having issues clicking on
        # the Customer ID button -- no trouble clicking on it manually
        # Look at the customer id screen
        # pos.click('Customer ID')
        # if _plus_or_minus_exists():
        #     _fail_and_end("+ / - button was present on the tax modify screen.")
        # pos.click('cancel')

        # End the transaction
        pos.pay()


    @test
    def increment_only_selected_item(self):
        """
        Make sure that only the selected item
        is incremented in quantity
        """
        # Add 2 generic items
        pos.add_item()
        pos.add_item()

        # Increment + check that only
        # lowest item in journal changed quantity
        pos.click('+')
        pos.click('+')
        
        # Wait for transaction journal to update
        time.sleep(2)

        # Check that the one item was incremented in quantity
        # [1][4] = [quantity + price string][number representing quatity]
        # in the list read_transaction_journal returns
        try:
            item_2_char = pos.read_transaction_journal(2)[1][4]
            item_1_char = pos.read_transaction_journal(1)[1][0]
        except IndexError:
            tc_fail("Transaction journal does not look like increment_only_selected_item expected.")
        if not item_2_char == "3":
            tc_fail("Did not successfully increment the item's quantity.")
        elif not item_1_char == "$":
            tc_fail("Incremented both items (instead of just the selected one).")
        
        # Now with decrement
        pos.click('-')
        
        # Wait for transaction journal to update
        time.sleep(2)

        # Check that the one item was decremented in quantity
        try:
            item_2_char = pos.read_transaction_journal(2)[1][4]
            item_1_char = pos.read_transaction_journal(1)[1][0]
        except IndexError:
            tc_fail("Transaction journal does not look like increment_only_selected_item expected.")
        if not item_2_char == "2":
            tc_fail("Did not successfully decrement the item's quantity.")
        elif not item_1_char == "$":
            tc_fail("Decremented both items instead of just the selected one.")

        pos.pay()


    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        pos.close()


def _fail_and_end(msg):
    # Helper function for cleanly exiting
    # test case on failure (so other tests can run)
    pos.click('cancel', verify=False)
    pos.pay(verify=False)
    tc_fail(msg)

def _plus_and_minus_exist():
    # Helper function to see if plus and minus
    # buttons appear on the screen
    time.sleep(0.5)
    return (pos.is_element_present(pos.controls['keypad']['+']) and pos.is_element_present(pos.controls['keypad']['-']))

def _plus_or_minus_exists():
    # Helper function to see if plus or minus
    # buttons appear on the screen
    time.sleep(0.5)
    return (pos.is_element_present(pos.controls['keypad']['+']) or pos.is_element_present(pos.controls['keypad']['-']))