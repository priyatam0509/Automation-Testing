"""
    File name: POS_Tax_Modify.py
    Tags:
    Description: Script to test Tax Modify on HTML POS.
    Author: David Mayes
    Date created: 03-04-2020
    Date last modified: 03-31-2020
    Python Version: 3.7
"""

import logging, time
from app import Navi, mws, pos, system
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class POS_Tax_Modify():
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
        self.tax_modify_button = pos.controls['function keys']['tax modify']
        self.cash_button = pos.controls['pay']['type'] % 'cash'
        self.paidin_button = pos.controls['function keys']['paid in']
        self.journal_update_wait_time = 0.5  # Time given for the receipt journal to update (in seconds)
        self.screen_update_wait_time = 0.5  # Time given for the screen to update (in seconds)

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
    def simple_tax_modify(self):
        """
        Tax modify a single item
        """
        # Add an item
        pos.add_item("Item 5")

        # Check that the item's price is $2.00
        if not self._balance_equals('$2.00'):
            self._fail_and_end_transaction("Item's price is not right before tax modifying.")
        
        # Tax modify the item
        self._tax_modify()

        # Check that the item's price has increased to $2.20
        if not self._balance_equals('$2.20'):
            self._fail_and_end_transaction("Item's price is not right after tax modifying.")

        # Exit the transaction
        pos.pay()


    @test
    def appears_only_in_transactions(self):
        """
        Make sure that the tax modify button
        only appears when in a transaction
        """
        # Make sure button NOT present on screen before starting transaction
        if pos.is_element_present(self.tax_modify_button):
            tc_fail("Tax Modify button is present on home screen.")

        # Make sure button is present when in transaction
        pos.add_item()
        if not pos.is_element_present(self.tax_modify_button, timeout=self.screen_update_wait_time):
            self._fail_and_end_transaction("Tax Modify button is NOT present during transaction.")

        # Make sure button is NOT present on pay screen
        pos.click('Pay')
        if pos.is_element_present(self.tax_modify_button, timeout=self.screen_update_wait_time):
            pos.click('cancel')
            self._fail_and_end_transaction("Tax Modify button is present on pay screen.")
        pos.click('cancel')

        # Make sure button is NOT present after paying
        pos.pay()
        if pos.is_element_present(self.tax_modify_button, timeout=self.screen_update_wait_time):
            tc_fail("Tax Modify button is present after paying.")

        # Make sure button is NOT present after voiding transaction
        pos.add_item()
        pos.void_transaction()
        if pos.is_element_present(self.tax_modify_button, timeout=self.screen_update_wait_time):
            tc_fail("Tax Modify button is present after voiding transaction.")
    

    @test
    def not_in_empty_transaction(self):
        """
        Make sure that the tax modify button doesn't show
        up when a transaction has no items in it
        """
        # Add an item
        pos.add_item()

        # Remove the item
        pos.click('Void Item')

        # Check that the tax modify button does not exist
        system.wait_for(lambda: not pos.is_element_present(self.tax_modify_button, timeout=self.screen_update_wait_time))
        if pos.is_element_present(self.tax_modify_button):
            self._fail_and_end_transaction("Tax modify button is present with no items in the transaction.")

        # Exit the transaction
        pos.void_transaction()


    @test
    def only_selected_item(self):
        """
        Make sure that tax modify only applies tax
        to the currently selected item
        """
        # Add 2 items
        pos.add_item('Item 5')
        pos.add_item('Item 5')

        # Make sure the initial balance is $4.00
        if not self._balance_equals('$4.00'):
            self._fail_and_end_transaction("Total balance is not right before tax modifying.")

        # Tax modify one item
        self._tax_modify()

        # Make sure that only the selected item
        # was tax modified
        if not self._balance_equals('$4.20'):
            self._fail_and_end_transaction("Total balance is not right after tax modifying")
        
        # Exit the transaction
        pos.pay()


    @test
    def cancel(self):
        """
        Make sure that canceling tax modify works
        """
        # Add an item
        pos.add_item('Item 5')

        # Check that the item's initial price is $2.00
        if not self._balance_equals('$2.00'):
            self._fail_and_end_transaction("Item's price is not right.")

        # Click tax modify + cancel the tax modifying
        pos.click('Tax Modify')
        pos.click('cancel')

        # Check that the item's price after cancel is still $2.00
        if not self._balance_equals('$2.00'):
            self._fail_and_end_transaction("Total balance with tax is not right is not right.")
        
        # Exit the transaction
        pos.pay()


    @test
    def receipt_shows_tax(self):
        """
        Make sure that tax modifying an item
        adds tax to the receipt
        """
        # Add an item
        pos.add_item('Item 5')

        # Check that the transaciton's balance is $2.00
        if not self._balance_equals('$2.00'):
            self._fail_and_end_transaction("Transaction's balance is not right before tax modifying.")

        # Tax modify the item
        self._tax_modify()

        # Complete the transaction
        pos.pay()

        # Check and make sure that the receipt shows $0.20 of tax
        if not pos.check_receipt_for("Tax = $0.20", verify=False):
            tc_fail("Tax did not show up on the receipt.")


    @test
    def negative_item(self):
        """
        Make sure that a negative item is properly tax modified
        (ex: -$5.00 becomes -$5.50 at 10% tax)
        """
        # Add an item
        pos.add_item('Negative Item')

        # Check that the transaciton's balance is $2.00
        if not self._balance_equals('-$5.00'):
            self._fail_and_end_transaction("Transaction's balance is not right before tax modifying.")

        # Tax modify the item and check that it worked
        self._tax_modify()

        if not self._balance_equals('-$5.50'):
            self._fail_and_end_transaction("Did not properly tax modify negative transaction.")

        # Exit the transaction
        pos.pay()

    
    @test
    def zero_price_item(self):
        """
        Tax modify a zero price item and make sure it
        1) doesn't change the total balance while still $0
        2) saves it's tax modification so when its price increases,
            tax is added
        """
        # Add an item
        pos.add_item(item="Dept 1", method="DEPT KEY", price='0')

        # Check that the balance is 0 initially
        if not self._balance_equals('$0.00'):
            self._fail_and_end_transaction("Balance was not $0.00 after only adding a free item.")

        # Tax modify the free item
        self._tax_modify()

        # Check that the balance is still $0
        if not self._balance_equals('$0.00'):
            self._fail_and_end_transaction("Price increased after tax modifying a free item.")
        
        # Change item quantity and make sure the price is still $0
        pos.click('Change Item Qty')
        pos.enter_keypad('25', after='enter')
        if not self._balance_equals('$0.00'):
            self._fail_and_end_transaction("Price increased after tax modifying free item and changing its quantity.")

        # Override item's price so that it isn't free
        # and make sure it has tax
        self._override('100')
        if not self._balance_equals('$27.50'):
            self._fail_and_end_transaction("Transaction balance is not right after overriding 25 tax-modified free items to a price of $1.00.")

        # Exit the transaction
        pos.pay()


    @test
    def two_decimal_places(self):
        """
        Make sure that when an item is low enough in price that
        you can't see the tax in the total balance, it is still
        successfully tax modified
        """
        # Add an item
        pos.add_item()

        # Check that the balance is $0.01 initially
        if not self._balance_equals('$0.01'):
            self._fail_and_end_transaction("Balance was not $0.01 after only adding a generic item.")

        # Tax modify the item
        self._tax_modify()

        # Check that the balance is still $0.01
        if not self._balance_equals('$0.01'):
            self._fail_and_end_transaction("Balance was not $0.01 after tax modifying $0.01-priced item.")

        # Increase the item's quantity and make sure it's taxed
        pos.click('Change Item Qty')
        pos.enter_keypad('25', after='enter')
        if not self._balance_equals('$0.28'):
            self._fail_and_end_transaction("$0.01 price item did not show tax when increased to a quantity of 25.")

        # Exit the transaction
        pos.pay()


    @test
    def remove_tax(self):
        """
        Make sure that removing tax from a taxed item works
        """
        # Add an item
        pos.add_item('Item 5')

        # Check that balance is $2.00 initially
        if not self._balance_equals('$2.00'):
            self._fail_and_end_transaction("Initial balance is not correct.")

        # Tax modify the item and check that it worked
        self._tax_modify()
        if not self._balance_equals('$2.20'):
            self._fail_and_end_transaction("Balance is not correct after tax modifying.")

        # Remove tax and check that it worked
        pos.click('Tax Modify')
        pos.select_list_item('No Tax')
        pos.click('enter')

        if not self._balance_equals('$2.00'):
            self._fail_and_end_transaction("Tax was not properly removed.")

        # Exit the transaction
        pos.pay()


    @test
    def plus_and_minus(self):
        """
        Make sure that the tax increases/decreases
        at the right rate when you increment/decrement
        """
        # Add an item
        pos.add_item('Item 5')

        # Make sure balance is right initially
        if not self._balance_equals('$2.00'):
            self._fail_and_end_transaction("Initial balance is not correct.")

        # Tax modify + make sure it worked
        self._tax_modify()
        if not self._balance_equals('$2.20'):
            self._fail_and_end_transaction("Balance after tax modify is not correct.")
    
        # Increment item's quantity and make sure tax increases
        pos.click('+')
        if not self._balance_equals('$4.40'):
            self._fail_and_end_transaction("Balance after incrementing quantity is not correct.")

        # Decrement item's quantity and make sure tax decreases
        pos.click('-')
        if not self._balance_equals('$2.20'):
            self._fail_and_end_transaction("Balance after decrementing quantity is not correct.")

        # Exit the transaction
        pos.pay()


    @test
    def override(self):
        """
        Make sure that the tax changes at the right rate
        when you override the price of an item
        """
        # Add an item
        pos.add_item('Item 5')

        # Make sure balance is right initially
        if not self._balance_equals('$2.00'):
            self._fail_and_end_transaction("Initial balance is not correct.")

        # Tax modify + make sure it worked
        self._tax_modify()
        if not self._balance_equals('$2.20'):
            self._fail_and_end_transaction("Balance after tax modify is not correct.")

        # Override item's price and make sure tax changes appropriately
        self._override('500')

        if not self._balance_equals('$5.50'):
            self._fail_and_end_transaction("Tax did not properly change after price override.")

        # Exit the transation
        pos.pay()


    @test
    def change_quantity(self):
        """
        Make sure that tax changes at the right rate
        when you change the quantity of an item
        """
        # Add an item
        pos.add_item('Item 5')

        # Make sure balance is right initially
        if not self._balance_equals('$2.00'):
            self._fail_and_end_transaction("Initial balance is not correct.")

        # Tax modify + make sure it worked
        self._tax_modify()
        if not self._balance_equals('$2.20'):
            self._fail_and_end_transaction("Balance after tax modify is not correct.")

        # Override item's price and make sure tax changes appropriately
        pos.click('Change Item Qty')
        pos.enter_keypad('25', after='enter')

        if not self._balance_equals('$55.00'):
            self._fail_and_end_transaction("Tax did not properly change after price override.")

        # Exit the transation
        pos.pay()


    def _fail_and_end_transaction(self, msg):
        # Helper method to cleanly close on failure in transaction
        # and be ready for the next test case
        pos.pay(verify=False)
        tc_fail(msg)


    def _tax_modify(self):
        # Helper method to make code more readable by
        # doing the 3 actions required to tax modify an item
        pos.click('Tax Modify')
        pos.select_list_item('Test Tax')
        pos.click('enter')


    def _balance_equals(self, amount=None):
        # Helper method to wait a second for the journal to update
        # and read the total balance on it
        start_time = time.time()
        while time.time() - start_time <= self.journal_update_wait_time:
            if pos.read_balance()['Total'] == amount:
                return True
        else:
            return False


    def _override(self, price='0'):
        # Helper method for overriding
        self.log.info("Attempting to override price...")
        pos.click('override')
        pos.enter_keypad(price, after='enter')


    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        pos.close()
