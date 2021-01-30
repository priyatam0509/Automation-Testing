"""
    File name: POS_Quick_Void.py
    Tags:
    Description: Test script for testing quick void (the trashcan icon 
    that appears to the right of an item when you click on it in
    the transaction journal) in HTML POS.
    Author: David Mayes
    Date created: 2020-04-28
    Date last modified: 
    Python Version: 3.7
"""

import logging, time
from app import Navi, mws, pos, system
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class POS_Quick_Void():
    """
    Class for testing
    """

    def __init__(self):
        """
        Initializes the Template class.
        """
        # The logging object. 
        # Example: self.log.info(f"Current value of var: {my_var}")
        self.log = logging.getLogger()
        self.wait_time = 1
        self.long_wait_time = 15
        self.override_button = pos.controls['function keys']['override']
        self.quick_void_button = pos.controls['receipt journal']['quick_void']
        self.plus_button = pos.controls['keypad']['+']
        self.price_check_button = pos.controls['function keys']['price check']

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
    def plain_void(self):
        """
        Test a simple quick void
        """
        # Start a transaction
        self.log.info("Adding items to transaction...")
        pos.click('generic item')
        pos.click('generic item')
        pos.click('generic item')

        # Void an item
        self.log.info("Voiding one item...")
        if pos.is_element_present(self.override_button, timeout=self.wait_time):
            if pos.is_element_present(self.quick_void_button, timeout=self.wait_time):
                tc_fail("Quick void appeared without clicking an item in the receipt journal.")
            pos.click_journal_item('generic item')
            if pos.is_element_present(self.quick_void_button, timeout=self.wait_time):
                pos.click_key(self.quick_void_button)
            else:
                tc_fail("Quick void button didn't appear.")
        
        # Make sure the item was removed
        self.log.info("Making sure item was removed...")
        start_time = time.time()
        while time.time() - start_time < self.wait_time:
            journal = pos.read_transaction_journal()
            if not journal:
                continue
            elif len(pos.read_transaction_journal()) == 2:
                break
        else:
            tc_fail("Clicking quick void did not the void an item.")

        self.log.info("Successfully voided an item with quick void!")


    @test
    def submenus(self):
        """
        Make sure you can't void items in the submenus
        where quick void should be disabled
        """
        # Start transaction if not in one already
        if not pos.is_element_present(self.override_button, timeout=self.wait_time):
            pos.click('generic item')

        # Check that quick void won't appear on the various submenus
        self._check_submenu(name='price check', timeout=self.wait_time)
        self._check_submenu(name='override', timeout=self.wait_time)
        self._check_submenu(name='change item qty', timeout=self.wait_time)
        self._check_submenu(name='tax modify', timeout=self.wait_time)
        self._check_submenu(name='void transaction', timeout=self.wait_time)
        
        self.log.info("Checking the customer id screen...")
        pos.click('customer id')
        if "Cancelled" in pos.read_message_box(timeout=self.wait_time):
            pos.click('ok')
        elif self._in_submenu(timeout=self.wait_time):
            pos.click_journal_item('generic item')
            if pos.is_element_present(self.quick_void_button, timeout=self.wait_time):
                tc_fail("Quick void button appeared on the customer id submenu.")
            pos.click('cancel')
            if pos.read_message_box(timeout=self.wait_time):
                pos.click('ok')
        else:
            tc_fail("Prompt did not come up after cancelling customer id entry.")
        self.log.info("Quick void did not appear on the customer id submenu...")
        
        pos.is_element_present(self.price_check_button, timeout=self.wait_time)

        self.log.info("Checking the pay screen...")
        pos.click('pay')
        if self._in_submenu(timeout=self.wait_time):
            pos.click_journal_item('generic item')
            if pos.is_element_present(self.quick_void_button, timeout=self.wait_time):
                tc_fail("Quick void button appeared on the pay submenu.")
        self.log.info("Quick void did not appear on the pay submenu...")
        pos.click('cash')
        pos.enter_keypad('100', after='enter')
        pos.is_element_present(self.price_check_button, timeout=self.long_wait_time)
        
        self.log.info("Quick void did not appear on any of the submenus it wasn't supposed to!")

        
    @test
    def journal(self):
        """
        Check the electronic journal to make sure the void
        is recorded
        """
        # Make sure that the most recent version of the
        # electronic journal is updated as an html file
        Navi.navigate_to('Journal Reports')
        mws.click_toolbar('Select')
        mws.click_toolbar('Print Preview')

        # Wait for the electronic journal to update
        if self._wait_for_reload(self.long_wait_time):
            self.log.info("Electronic journal updated...")
        else:
            tc_fail("The electronic journal was not updated.")

        # Open the file
        self.log.info("Reading electronic journal...")
        with open('C:/Passport/advpos/Reports/eng/html/ElectronicJournalReport.htm', 'r') as ej:
            rows = list(ej)

        ej_final_index = len(rows) - 1
        index = ej_final_index

        for text_row in rows[::-1]:
            if 'voided item' in text_row.lower():
                break
            elif ej_final_index - index >= 100 or index == 0:
                tc_fail("Void item was not recorded in the transaction journal.")
            index-=1

        self.log.info("Void item was recorded in the electronic journal!")
        

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        pos.close()
        mws.sign_off()


    def _in_submenu(self, timeout):
        """
        Helper function that uses the disappearance of the
        + button to determine whether HTML POS has entered/
        loaded a submenu
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if not pos.is_element_present(self.plus_button, timeout=0.05):
                return True
        else:
            return False
    

    def _check_submenu(self, timeout, finish_timeout=None, name=None):
        """
        Helper function for checking whether quick void appears
        in a submenu
        """
        if not finish_timeout:
            finish_timeout = timeout
        if name == None:
            tc_fail("Did not input a submenu argument to _check_submenu.")
        self.log.info("Checking the " + str(name) + " screen...")
        pos.click(name)
        if self._in_submenu(timeout=self.wait_time):
            pos.click_journal_item('generic item')
            if pos.is_element_present(self.quick_void_button, timeout=timeout):
                tc_fail("Quick void button appeared in the " + str(name) + " submenu.")
        self.log.info("Quick void did not appear on the " + str(name) + " submenu...")
        if not pos.click('cancel'):
            pos.click_message_box_key('ok')
        if not pos.is_element_present(self.price_check_button, timeout=finish_timeout):
            tc_fail("Did not return to the main screen after clicking cancel on the " + str(name) + " screen.")


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