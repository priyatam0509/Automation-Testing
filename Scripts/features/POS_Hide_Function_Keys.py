"""
    File name: POS_Hide_Function_Keys.py
    Tags:
    Description: Script to test whether function keys hide after clicking on things such
                 as override, change item qty, tax modify, and discount
    Author: 
    Date created: 03-09-2020
    Date last modified: 03-09-2020
    Python Version: 3.7
"""

import logging, time
from app import Navi, mws, pos, system
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class POS_Hide_Function_Keys():
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

        self.transaction_func_keys = [
            pos.controls['function keys']['price check'],
            pos.controls['function keys']['dept keys'],
            pos.controls['function keys']['speed keys'],
            pos.controls['function keys']['override'],
            pos.controls['function keys']['discount'],
            pos.controls['function keys']['void item'],
            pos.controls['function keys']['suspend transaction'],
            pos.controls['function keys']['change item qty'],
            pos.controls['function keys']['store coupon'],
            pos.controls['function keys']['void transaction'],
            pos.controls['function keys']['tax modify'],
            pos.controls['function keys']['show all dispensers'],
            pos.controls['function keys']['pay'],
            pos.controls['keypad']['+'], pos.controls['keypad']['-'],
            pos.controls['function keys']['customer id']
        ]

        self.main_menu_func_keys = [
            pos.controls['function keys']['price check'],
            pos.controls['function keys']['chg/ref due'],
            pos.controls['function keys']['paid in'],
            pos.controls['function keys']['paid out'],
            pos.controls['function keys']['receipt search'],
            pos.controls['function keys']['speed keys'],
            pos.controls['function keys']['dept keys'],
            pos.controls['function keys']['no sale'],
            pos.controls['function keys']['lock'],
            pos.controls['function keys']['tank alarms'],
            pos.controls['function keys']['loc acct paid in'],
            pos.controls['function keys']['till audit'],
            pos.controls['function keys']['refund'],
            pos.controls['function keys']['sign-off'],
            pos.controls['function keys']['change speedkeys'],
            pos.controls['function keys']['loan'],
            pos.controls['function keys']['change password'],
            pos.controls['function keys']['clean'],
            pos.controls['function keys']['show all dispensers'],
            pos.controls['function keys']['tools'],
            pos.controls['function keys']['safe drop'],
            pos.controls['function keys']['close till']
        ]


    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        """
        # if not system.restore_snapshot():
        #     self.log.debug("No snapshot to restore, if this is not expected please contact automation team")
        pos.connect()
        pos.sign_on()
        pos.add_item('Item 8')


    @test
    def override(self):
        """
        Make sure function keys are hidden after clicking "Override"
        """
        # Click the override button
        self.log.info("Attempting to click override and cancel.")
        pos.click('override')

        # Make sure the function keys are hidden
        if not self._func_keys_hidden(in_transaction=True):
            pos.click('cancel')
            tc_fail("The function keys were not hidden after clicking override.")

        # Click cancel
        pos.click('cancel')
        if self._func_keys_hidden(in_transaction=True):
            tc_fail("The function keys did not return after canceling override.")

        self.log.info("Func keys hid in override + reappeared after cancel.")
        
        # Click the override button again
        self.log.info("Attempting to override an item's price.")
        pos.click('override')
        
        # Make sure the function keys are hidden
        if not self._func_keys_hidden(in_transaction=True):
            pos.click('cancel')
            tc_fail("The function keys were not hidden after clicking override.")

        # Complete override and make sure function keys return
        pos.enter_keypad('666', after='enter')

        if self._func_keys_hidden(in_transaction=True):
            tc_fail("The function keys did not return after completing override.")

        self.log.info("Func keys hid in override + returned after override.")


    @test
    def tax_modify(self):
        """
        Make sure function keys are hidden after clicking "Tax Modify"
        """
        # Click the tax modify button
        self.log.info("Attempting to click tax modify and cancel.")
        pos.click('tax modify')

        # Make sure the function keys are hidden
        if not self._func_keys_hidden(in_transaction=True):
            pos.click('cancel')
            tc_fail("The function keys were not hidden after clicking tax modify.")

        # Click cancel
        pos.click('cancel')

        if self._func_keys_hidden(in_transaction=True):
            tc_fail("The function keys did not return after canceling tax modify.")

        self.log.info("Func keys hid in tax modify + returned after cancel.")

        # Complete a tax modification
        self.log.info("Attempting to tax modify an item.")
        pos.click('tax modify')
        pos.select_list_item('Test Tax')
        pos.click('enter')
        
        # Make sure the function keys are hidden
        if self._func_keys_hidden(in_transaction=True):
            tc_fail("The function keys were not hidden after clicking tax modify.")

        self.log.info("Func keys hid during tax modify + returned after.")

    
    @test
    def change_item_qty(self):
        """
        Make sure the function keys are hidden after clicking "Change Item Qty"
        """
        # Click the change item qty button
        self.log.info("Attempting to click the change item qty button and cancel.")
        pos.click('change item qty')

        # Make sure the function keys are hidden
        if not self._func_keys_hidden(in_transaction=True):
            pos.click('cancel')
            tc_fail("The function keys were not hidden after clicking change item qty.")

        # Click cancel
        pos.click('cancel')
        if self._func_keys_hidden(in_transaction=True):
            tc_fail("The function keys did not return after canceling change item qty.")

        self.log.info("Func keys hid during change item qty + returned after cancel.")

        # Click the change item qty button again
        self.log.info("Attempting to change item qty.")
        pos.click('change item qty')
        
        # Make sure the function keys are hidden
        if not self._func_keys_hidden(in_transaction=True):
            pos.click('cancel')
            tc_fail("The function keys were not hidden after clicking change item qty.")

        # Complete change item qty and make sure function keys return
        pos.enter_keypad('10', after='enter')

        if self._func_keys_hidden(in_transaction=True):
            tc_fail("The function keys did not return after completing change item qty.")

        self.log.info("Func keys hids during change item qty + returned after.")


    @test
    def price_check_in_transaction(self):
        """
        Make sure the function keys are hidden after clicking "Price Check" while in a transaction
        """
        # Click the price check button
        self.log.info("Attempting to click price check and cancel in a transaction.")
        pos.click('price check')

        # Make sure the function keys are hidden
        if not self._func_keys_hidden(in_transaction=True):
            pos.click('cancel')
            tc_fail("The function keys were not hidden after clicking price check in a transaction.")

        # Click cancel
        pos.click('cancel')
        if self._func_keys_hidden(in_transaction=True):
            tc_fail("The function keys did not return after canceling price check in a transaction.")

        self.log.info("Func keys hid during price check + returned after cancel.")

        # Click the price button again
        self.log.info("Attempting to do a price check.")
        pos.click('price check')
        
        # Make sure the function keys are hidden
        if not self._func_keys_hidden(in_transaction=True):
            pos.click('cancel')
            tc_fail("The function keys were not hidden after clicking price check in a transaction.")

        # Complete price check and make sure function keys return
        pos.click_speed_key('Generic Item')
        pos.click('ok')

        if self._func_keys_hidden(in_transaction=True):
            tc_fail("The function keys did not return after completing price check in a transaction.")

        self.log.info("Func keys hid during price check + returned after.")

    @test
    def customer_id(self):
        """
        Make sure the function keys are hidden after clicking "Customer ID"
        """
        # Click the customer id button
        self.log.info("Attempting to click customer ID and cancel.")
        pos.click('customer id')

        # Make sure the function keys are hidden
        if not self._func_keys_hidden(in_transaction=True):
            pos.click('cancel')
            pos.click('ok')
            tc_fail("The function keys are not hidden after clicking the customer id button.")

        # Cancel the customer id entry
        pos.click('cancel')
        pos.click('ok')
        if self._func_keys_hidden(in_transaction=True):
            tc_fail("The function keys did not return after canceling customer id entry.")

        self.log.info("Func keys hid during customer ID entry + returned after cancel.")

        # Click the customer id button again
        self.log.info("Attempting to enter a customer ID.")
        pos.click('customer id')

        # Make sure the function keys are hidden
        if not self._func_keys_hidden(in_transaction=True):
            pos.click('cancel')
            pos.click('ok')
            tc_fail("The function keys are not hidden after clicking the customer id button.")

        # Enter a customer id and make sure the function keys are visible
        pos.enter_keypad('1', after='enter')

        if self._func_keys_hidden(in_transaction=True):
            tc_fail("The function keys did not return after entering a customer id.")

        self.log.info("Func keys hid during customer ID entry + returned after.")


    @test
    def price_check_not_in_transaction(self):
        """
        Make sure the function keys are hidden after clicking "Price Check" while not in a transaction
        """
        # NOTE pos.pay() does not pertain to what is actually being tested by this script
        # but we need to exit out of the transaction for the next set of cases
        self.log.info("Attempting to exit the transaction for the next set of test cases.")
        if not pos.pay():
            self.log.warning("pos.pay() failed -- it has NOTHING TO DO WITH HIDING FUNCTION KEYS, but it is necessary to exit the transaction to access the buttons that the next test cases use.")

        # Click the price check button
        self.log.info("Attempting to do a price check and cancel outside of a transaction.")
        pos.click('price check')

        # Make sure the function keys are hidden
        if not self._func_keys_hidden(in_transaction=False):
            pos.click('cancel')
            tc_fail("The function keys were not hidden after clicking price check outside of a transaction.")

        # Click cancel
        pos.click('cancel')
        if self._func_keys_hidden(in_transaction=False):
            tc_fail("The function keys did not return after canceling price check outside of a transaction.")

        self.log.info("Func keys hid during price check + returned after cancel.")

        # Click the price button again
        self.log.info("Attempting price check outside of a transaction.")
        pos.click('price check')
        
        # Make sure the function keys are hidden
        if not self._func_keys_hidden(in_transaction=False):
            pos.click('cancel')
            tc_fail("The function keys were not hidden after clicking price check outside of a transaction.")

        # Complete price check and make sure function keys return
        pos.click_speed_key('Generic Item')
        pos.click('ok')

        if self._func_keys_hidden(in_transaction=False):
            tc_fail("The function keys did not return after completing price check outside of a transaction.")

        self.log.info("Func keys hid during price check and returned after.")

    @test
    def change_speedkeys(self):
        """
        Make sure the function keys are hidden after clicking "Change Speedkeys"
        """
        # Click the change speedkeys button
        self.log.info("Attempting to click the change speedkeys button and cancel.")
        pos.click('tools')
        pos.click('change speedkeys')

        # Make sure the function keys are hidden
        if not self._func_keys_hidden(in_transaction=False):
            pos.click('cancel')
            pos.click('back')
            tc_fail("The function keys were not hidden after clicking the change speedkeys button.")

        # Click cancel and make sure the function keys reappear
        pos.click('cancel')
        pos.click('back')
        
        if self._func_keys_hidden(in_transaction=False):
            tc_fail("The function keys did not reappear after canceling out of the change speedkeys screen.")

        self.log.info("Func keys hid on change speedkeys screen + returned after cancel.")


    @test
    def loan(self):
        """
        Make sure the function keys are hidden after clicking "Loan"
        """
        # Click the loan button
        self.log.info("Attempting to click the loan button and cancel.")
        pos.click('loan')

        # Make sure the function keys are hidden
        if not self._func_keys_hidden(in_transaction=False):
            pos.click('cancel')
            tc_fail("The function keys were not hidden after clicking the loan button.")

        # Click cancel and make sure the function keys reappear
        pos.click('cancel')

        if self._func_keys_hidden(in_transaction=False):
            tc_fail("The function keys did not reappear after canceling the loan.")

        self.log.info("Func keys hid on loan screen + returned after cancel.")


    @test
    def paidin(self):
        """
        Make sure the functions keys are hidden after clicking "Paid In"
        """
        # Click the paid in button
        self.log.info("Attempting to click the paid in button and cancel.")
        pos.click('paid in')

        # Make sure the function keys are hidden
        if not self._func_keys_hidden(in_transaction=False):
            pos.click('cancel')
            tc_fail("The function keys were not hidden after clicking the paid in button.")

        # Click cancel and make sure the function keys reappear
        pos.click('cancel')

        if self._func_keys_hidden(in_transaction=False):
            tc_fail("The function keys did not reappear after canceling the paid in.")

        self.log.info("Func keys hid on paid in screen + returned after cancel.")

        # Click the paid in button
        self.log.info("Doing a paid in transaction and making sure the func keys disappear during + reappear after.")
        pos.click('paid in')

        # Make sure the function keys are hidden
        if not self._func_keys_hidden(in_transaction=False):
            pos.click('cancel')
            tc_fail("The function keys were not hidden after clicking the paid in button.")

        # Complete paid in and make sure the function keys reappear
        pos.enter_keypad('100', after='enter')

        if self._func_keys_hidden(in_transaction=False):
            tc_fail("The function keys did not reappear after completing the paid in.")

        self.log.info("Func keys hid on paid in screen + returned after.")


    @test
    def paidout(self):
        """
        Make sure the functions keys are hidden after clicking "Paid Out"
        """
        # Click the paid out button
        self.log.info("Attempting to click the paid out button and cancel.")
        pos.click('paid out')

        # Make sure the function keys are hidden
        if not self._func_keys_hidden(in_transaction=False):
            pos.click('cancel')
            tc_fail("The function keys were not hidden after clicking the paid out button.")

        # Click cancel and make sure the function keys reappear
        pos.click('cancel')

        if self._func_keys_hidden(in_transaction=False):
            tc_fail("The function keys did not reappear after canceling the paid out.")

        self.log.info("Func keys hid on paid out screen + returned after cancel.")

        # Click the paid out button
        self.log.info("Doing a paid out transaction and making sure the func keys disappear during + reappear after.")
        pos.click('paid out')

        # Make sure the function keys are hidden
        if not self._func_keys_hidden(in_transaction=False):
            pos.click('cancel')
            tc_fail("The function keys were not hidden after clicking the paid out button.")

        # Complete paid out and make sure the function keys reappear
        pos.enter_keypad('100', after='enter')

        if self._func_keys_hidden(in_transaction=False):
            tc_fail("The function keys did not reappear after completing the paid out.")

        self.log.info("Func keys hid on paid out screen + returned after.")       

    
    def _func_keys_hidden(self, in_transaction=False):
        # Helper function for testing whether any of the
        # function keys are on the screen
        time.sleep(1)
        if in_transaction:
            for button in self.transaction_func_keys:
                if pos.is_element_present(button, timeout=0.01):
                    return False
            return True
        else:
            for button in self.main_menu_func_keys:
                if pos.is_element_present(button, timeout=0.01):
                    return False
            return True


    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        pos.close()
