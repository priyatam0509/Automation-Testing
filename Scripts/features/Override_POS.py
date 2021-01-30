"""
    File name: Override_POS.py
    Tags:
    Description: Script for testing the override button in HTML POS.
    Author: David Mayes
    Date created: 02-24-2020
    Date last modified: 03-02-2020
    Python Version: 3.7
"""

import logging
from app import Navi, mws, pos, system
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app.features import item

default_timeout = 3

class Override_POS():
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
    def generic_override(self):
        """
        Buy a Generic Item and override its price
        """
        # Add generic item
        pos.add_item()

        # Override price
        pos.click('override')
        # If reasons codes are not present, exit and fail
        if not pos.is_element_present(pos.controls['selection list']['list'], default_timeout):
            pos.click('cancel')
            tc_fail("Selection list was not present.")
        pos.enter_keypad('200', after='enter')

        # Check that override worked
        if not pos.read_balance()['Total'] == "$2.00":
            tc_fail("Override did not properly update the price of a generic item.")
        pos.pay()
    

    @test
    def group_override(self):
        """
        Buy a grouped-together bunch of the same item and update its price
        """
        # Add generic item
        pos.add_item()

        # Change number of generic items
        pos.click('Change Item Qty')
        pos.enter_keypad('10', after='enter')

        # Override price and make sure it multiplies correctly
        pos.click('override')
        # If reasons codes are not present, exit and fail
        if not pos.is_element_present(pos.controls['selection list']['list'], default_timeout):
            pos.click('cancel')
            tc_fail("Selection list was not present.")
        pos.enter_keypad('3', after='enter')
        if not pos.read_balance()['Total'] == "$0.30":
            tc_fail("Override did not properly multiply the overriden price for multiple items.")
        pos.pay()
        

    @test
    def cancel(self):
        """
        Cancel the override and make sure the price stays the same
        """
        # Add generic item
        pos.add_item()
        balance = pos.read_balance()['Total']

        # Click override, then cancel override
        # and check that price stayed the same
        pos.click('override')
        # If reasons codes are not present, exit and fail
        if not pos.is_element_present(pos.controls['selection list']['list'], default_timeout):
            pos.click('cancel')
            tc_fail("Selection list was not present.")
        pos.enter_keypad('200', after='cancel')
        if not balance == pos.read_balance()['Total']:
            tc_fail('Clicking cancel did not successfully stop attempt to override price.')
        pos.pay()
        

    @test
    def without_item(self):
        """
        Click override without any items having been bought
        """
        # Add generic item
        pos.add_item()

        # Remove generic item
        pos.void_transaction()

        # Make sure can't override
        if pos.is_element_present('override', default_timeout):
            tc_fail('Override button present when no item exists to override.')


    @test
    def after_paying(self):
        """
        Click override after transaction was complete
        """
        # Add generic item
        pos.add_item()

        # Pay for generic item
        pos.pay()

        # Make sure can't override after transaction has ended
        if pos.is_element_present('override', default_timeout):
            tc_fail("Override button present when no item exists to override.")


    @test
    def selected_item(self):
        """
        Select an item that wasn't the most recent in the
        journal and price override it
        """
        # Add 3 generic items
        for i in range(1, 4):
            pos.add_item(item='Dept 1', method='dept key', price=str(i))

        # Override the price of the first item
        pos.click_journal_item(instance=1)
        pos.click('override')
        # If reasons codes are not present, exit and fail
        if not pos.is_element_present(pos.controls['selection list']['list'], default_timeout):
            pos.click('cancel')
            tc_fail("Selection list was not present.")
        pos.enter_keypad('20000', after='enter')

        # Make sure override worked
        if not pos.read_balance()['Total'] == "$200.05" or not pos.read_transaction_journal(1)[1] == "$200.00":
            tc_fail("Override button did not successfully change price for item further back in the journal.")
        pos.pay()


    @test
    def zero(self):
        """
        Override an item's price to 0 and make sure it worked.
        """
        # Add a generic item
        pos.add_item()

        # Override item's price to 0
        pos.click('override')
        # If reasons codes are not present, exit and fail
        if not pos.is_element_present(pos.controls['selection list']['list'], default_timeout):
            pos.click('cancel')
            tc_fail("Selection list was not present")
        pos.click('enter')
        pos.click('yes')

        # Make sure price is 0
        if not pos.read_balance()['Total'] == "$0.00":
            tc_fail("Did not properly override an item's price to 0.")
        pos.click('pay')


    @test
    def above_max(self):
        """
        Override an item's price to be above the max of 9999.00
        and make sure it properly does not allow this.
        """
        # Add a generic item
        pos.add_item()

        # Override item's price past max
        pos.click('override')
        # If reasons codes are not present, exit and fail
        if not pos.is_element_present(pos.controls['selection list']['list'], default_timeout):
            pos.click('cancel')
            tc_fail("Selection list was not present.")
        pos.enter_keypad('999999', after='enter')

        # Make sure it isn't allowed
        if not "max" in pos.read_message_box():
            tc_fail("Allowed an item to be overridden with price greater than max allowed price.")
        if not pos.read_balance()['Total'] == "$0.01":
            tc_fail("Price changed on item when trying to override with a price above the max allowed.")
        
        # Close error message box
        pos.click('ok')
        pos.pay()


    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        pos.close()
