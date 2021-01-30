"""
    File name: POS_Refund.py.py
    Tags:
    Description: Test script for testing the refund feature in HTML POS
                 (but especially in relation to the mws toggle for doing a sale and
                 refund in the same transaction)
    Author: David Mayes
    Date created: 2020-05-14
    Date last modified: 
    Python Version: 3.7
"""

import logging, time
from app import mws, pos, system
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app.features import register_grp_maint

default_timeout = 3

class POS_Refund():


    def __init__(self):
        """
        Initializes the POS_Refund class
        """
        # The logging object. 
        # Example: self.log.info(f"Current value of var: {my_var}")
        self.log = logging.getLogger()
        self.paid_in_button = pos.controls['function keys']['paid in']
        self.short_wait_time = 5
        self.long_wait_time = 10


    @setup
    def setup(self):
        """
        Performs initialization
        """
        # if not system.restore_snapshot():
        #     self.log.debug("No snapshot to restore, if this is not expected please contact automation team")
        mws.sign_on()
        pos.connect()
        pos.sign_on()

    
    @test
    def untoggled(self):
        """
        With 'Allow sales and refunds in the same transaction'
        untoggled in the mws, perform a refund transaction
        """
        # Toggle the setting on the MWS
        self.log.info("Toggling setting in MWS...")
        rgm = register_grp_maint.RegisterGroupMaintenance()
        rgm.change("POSGroup1", {
            "Sales and Refunds": {
                "Allow sales and refunds in the same transaction": False
            }
        })

        # Make sure register reloads with changed setting
        if not self._register_reloaded():
            mws.click_toolbar("Cancel")
            mws.click_toolbar("Exit")
            tc_fail("Register failed to reload after changing Register Group Maintenance setting.")
        self.log.info("Setting changed and register reloaded...")
        mws.click_toolbar("Exit")

        # Bring HTML POS window back to the front so that screenshots of failures are useful
        pos.minimize_pos()
        pos.maximize_pos()

        # Do a refund
        self.log.info("Doing a refund transaction...")
        pos.click('refund')
        pos.click('generic item')
        pos.click('pay')
        if pos.read_message_box(self.short_wait_time):
            self._return_to_main_screen()
            tc_fail("Message box appeared when pay was clicked -- should only happen when setting is toggled to True.")

        # Complete the refund
        self.log.info("Attempting to complete the refund...")
        pos.click('cash')
        pos.click_tender_key('Exact Change')

        # Check whether refund was successful
        self.log.info("Checking whether refund was successful...")
        pos.is_element_present(self.paid_in_button, self.long_wait_time)
        msg = pos.read_journal_watermark(self.short_wait_time)
        if msg == None:
            self._return_to_main_screen()
            tc_fail("No journal watermark displayed after attempting refund transaction.")
        elif not "transaction complete" in msg.lower():
            self._return_to_main_screen()
            tc_fail("Incorrect journal watermark: " + msg)
        balances = pos.read_balance(self.short_wait_time)
        if balances == None:
            self._return_to_main_screen()
            tc_fail("Refund total not displayed in the transaction journal.")
        try:
            if balances['Total'] == '-$0.01':
                self.log.info("Refund was successful!")
            else:
                self._return_to_main_screen()
                tc_fail("Incorrect total for refund transaction was displayed in the transaction journal.")
        except KeyError:
            self._return_to_main_screen()
            tc_fail("Refund total not displayed in the transaction journal.")



    @test
    def toggled_sale(self):
        """
        With "Allow sales and refunds in the same transaction"
        toggled in the mws, perform a refund transaction in conjunction
        with a sale of some items
        """
        self.log.info("Toggling setting in MWS...")
        rgm = register_grp_maint.RegisterGroupMaintenance()
        rgm.change("POSGroup1", {
            "Sales and Refunds": {
                "Allow sales and refunds in the same transaction": True
            }
        })

        # Make sure register reloads with changed setting
        if not self._register_reloaded():
            mws.click_toolbar("Cancel")
            mws.click_toolbar("Exit")
            tc_fail("Register failed to reload after changing Register Group Maintenance setting.")
        self.log.info("Setting changed and register reloaded...")
        mws.click_toolbar("Exit")

        # Bring HTML POS window back to the front so that screenshots of failures are useful
        pos.minimize_pos()
        pos.maximize_pos()

        # Do a refund with sale
        self.log.info("Doing a refund transaction...")
        pos.click('refund')
        pos.click('generic item')
        pos.click('generic item')
        pos.click('generic item')
        pos.click('pay')
        msg = pos.read_message_box(self.short_wait_time)
        if msg == None:
            self._return_to_main_screen()
            tc_fail("Message box did not appear asking whether you want to sell items.")
        elif not "sell" in msg.lower():
            self._return_to_main_screen()
            tc_fail("Incorrect message displayed.  Should ask whether you want to sell items.")
        pos.click('yes')

        pos.click('generic item')
        pos.click('pay')

        # Complete the transaction
        self.log.info("Attempting to complete the transaction...")
        pos.click('cash')
        pos.click_tender_key('Exact Change')

        # Check whether refund was successful
        self.log.info("Checking whether refund was successful...")
        pos.is_element_present(self.paid_in_button, self.long_wait_time)
        msg = pos.read_journal_watermark(self.short_wait_time)
        if msg == None:
            self._return_to_main_screen()
            tc_fail("No journal watermark displayed after attempting refund transaction.")
        elif not "transaction complete" in msg.lower():
            self._return_to_main_screen()
            tc_fail("Incorrect journal watermark: " + msg)
        balances = pos.read_balance(self.short_wait_time)
        if balances == None:
            self._return_to_main_screen()
            tc_fail("Total not displayed in the transaction journal.")
        try:
            if balances['Total'] == '-$0.02':
                self.log.info("Refund with sale was successful!")
            else:
                self._return_to_main_screen()
                tc_fail("Incorrect total for transaction was displayed in the transaction journal.")
        except KeyError:
            self._return_to_main_screen()
            tc_fail("Total not displayed in the transaction journal.")

    
    @test
    def toggled_no_sale(self):
        """
        With "Allow sales and refunds in the same transaction"
        toggled in the mws, perform a refund transaction
        without the sale of any other items
        """
        self.log.info("Toggling setting in MWS...")
        rgm = register_grp_maint.RegisterGroupMaintenance()
        rgm.change("POSGroup1", {
            "Sales and Refunds": {
                "Allow sales and refunds in the same transaction": True
            }
        })

        # Make sure register reloads with changed setting
        if not self._register_reloaded():
            mws.click_toolbar("Cancel")
            mws.click_toolbar("Exit")
            tc_fail("Register failed to reload after changing Register Group Maintenance setting.")
        self.log.info("Setting changed and register reloaded...")
        mws.click_toolbar("Exit")

        # Bring HTML POS window back to the front so that screenshots of failures are useful
        pos.minimize_pos()
        pos.maximize_pos()

        # Do a refund without sale
        self.log.info("Doing a refund transaction...")
        pos.click('refund')
        pos.click('generic item')
        pos.click('generic item')
        pos.click('generic item')
        pos.click('pay')
        msg = pos.read_message_box(self.short_wait_time)
        if msg == None:
            self._return_to_main_screen()
            tc_fail("Message box did not appear asking whether you want to sell items.")
        elif not "sell" in msg.lower():
            self._return_to_main_screen()
            tc_fail("Incorrect message displayed.  Should ask whether you want to sell items.")
        pos.click('no')

        # Complete the refund
        self.log.info("Attempting to complete the refund...")
        pos.click('cash')
        pos.click_tender_key('Exact Change')

        # Check whether refund was successful
        self.log.info("Checking whether refund was successful...")
        pos.is_element_present(self.paid_in_button, self.long_wait_time)
        msg = pos.read_journal_watermark(self.short_wait_time)
        if msg == None:
            self._return_to_main_screen()
            tc_fail("No journal watermark displayed after attempting refund transaction.")
        elif not "transaction complete" in msg.lower():
            self._return_to_main_screen()
            tc_fail("Incorrect journal watermark: " + msg)
        balances = pos.read_balance(self.short_wait_time)
        if balances == None:
            self._return_to_main_screen()
            tc_fail("Total not displayed in the transaction journal.")
        try:
            if balances['Total'] == '-$0.03':
                self.log.info("Refund with sale was successful!")
            else:
                self._return_to_main_screen()
                tc_fail("Incorrect total for transaction was displayed in the transaction journal.")
        except KeyError:
            self._return_to_main_screen()
            tc_fail("Total not displayed in the transaction journal.")
    

    def _on_pay_screen(self, timeout=default_timeout):
        """
        Helper function to determine whether HTML POS
        is on the pay screen
        """
        return pos.is_element_present(pos.controls['pay']['exact_amount'], timeout=timeout)


    def _on_transaction_screen(self, timeout=default_timeout):
        """
        Helper function to determine whether HTML POS
        is in a transaction
        """
        return pos.is_element_present(pos.controls['function keys']['void transaction'], timeout=timeout)


    def _on_main_screen(self, timeout=default_timeout):
        """
        Helper function to determine whether HTML POS
        is on the main screen
        """
        return pos.is_element_present(pos.controls['function keys']['paid in'], timeout=timeout)


    def _return_to_main_screen(self, timeout=default_timeout):
        """
        Helper function to attempt to return main screen
        in failure cases
        """
        if pos.read_message_box(timeout=timeout):
            pos.click('no')
        if self._on_pay_screen():
            pos.click(pos.controls['pay']['exact_amount'])
            if self._on_main_screen(timeout=default_timeout*10):
                self.log.info("Returned to main screen...")
                return True
            else:
                self.log.warning("Failed to return to main screen!")
                return False
        if self._on_transaction_screen():
            pos.void_transaction()
        if self._on_main_screen():
            self.log.info("Returned to main screen...")
            return True
        self.log.info("Failed to return to main screen!")
        return False


    def _register_reloaded(self, timeout=15):
        """
        Helper function to make sure that the register has reloaded
        after saving a change in Register Group Maintenance
        """
        start_time = time.time()
        while time.time() - start_time <= timeout:
            if mws.get_top_bar_text() == '':
                return True
        else:
            return False
        

    @teardown
    def teardown(self):
        """
        Performs cleanup
        """
        # Reset the MWS setting
        self.log.info("Toggling setting in MWS...")
        rgm = register_grp_maint.RegisterGroupMaintenance()
        rgm.change("POSGroup1", {
            "Sales and Refunds": {
                "Allow sales and refunds in the same transaction": False
            }
        })

        pos.close()