"""
    File name: POS_Safe_Drop.py
    Tags:
    Description: Script for testing safe drop on HTML POS.
    Author: David Mayes
    Date created: 2020-04-27
    Date last modified:
    Python Version: 3.7
"""

import logging, time
from app import Navi, mws, pos, system
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class POS_Safe_Drop():
    """
    Class for testing safe drop
    """

    def __init__(self):
        """
        Initializes the POS_Safe_Drop class.
        """
        # The logging object. 
        # Example: self.log.info(f"Current value of var: {my_var}")
        self.log = logging.getLogger()
        self.generic_item_button = pos.controls['item keys']['key_by_text'] % 'generic item'
        self.paid_in_button = pos.controls['function keys']['paid in']
        self.keypad_one = pos.controls['keypad']['1']
        self.wait_time = 5
        self.long_wait_time = 15


    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        """
        # if not system.restore_snapshot():
        #     self.log.debug("No snapshot to restore, if this is not expected please contact automation team")
        mws.sign_on()
        pos.connect()
        pos.sign_on()


    @test
    def plain_safe_drop(self):
        """
        Do a plain safe drop without any prompt for pouch number/color
        """
        # Change settings in MWS
        self.log.info("Disabling pouch number/color prompt...")
        Navi.navigate_to('Register Group Maintenance')
        mws.click_toolbar('Change', submenu=True)
        mws.select_tab('Safe Drops')
        mws.set_value("Prompt for a pouch/envelope number", False)
        if not self._save(timeout=self.long_wait_time):
            tc_fail("MWS settings changes did not save.")
        else:
            self.log.info("MWS settings saved...")
        
        # Do a safe drop
        self.log.info("Attempting to execute a safe drop...")
        if not pos.click('safe drop'):
            tc_fail("Safe drop button did not become visible.")
        
        if self._in_safe_drop(self.wait_time):
            pos.enter_keypad('1000', after='+')
            pos.click('finalize')
        else:
            tc_fail("Did not enter safe drop transaction.")

        if pos.read_message_box(timeout=self.wait_time):
            pos.click('yes')
        else:
            tc_fail("Did not ask if the user was sure they wanted to finalize the safe drop transaction.")

        if pos.is_element_present(self.paid_in_button, timeout=self.long_wait_time):
            self.log.info("Plain safe drop succeeded!")
        else:
            tc_fail("Did not finalize the safe drop.  Safe drop failed.")

    
    @test
    def cancel_plain_safe_drop(self):
        """
        Cancel a plain safe drop without any prompt for number or color
        """
        # Start a safe drop
        self.log.info("Attempt to get to the safe drop screen...")
        if not pos.click('safe drop'):
            tc_fail("Safe drop button did not become visible.")
        
        # Cancel the safe drop
        self.log.info("Attempting to cancel...")
        if self._in_safe_drop(self.wait_time):
            pos.click('cancel')
        else:
            tc_fail("Did not enter safe drop transaction.")

        if pos.read_message_box(timeout=self.wait_time):
            pos.click('yes')
        else:
            tc_fail("Did not ask if the user wanted to cancel the safe drop transaction.")

        if pos.is_element_present(self.paid_in_button, timeout=self.long_wait_time):
            self.log.info("Canceling a plain safe drop succeeded!")
        else:
            tc_fail("Did not successfully cancel a safe drop.")


    @test
    def envelope_number(self):
        """
        Do a safe drop with a prompt for envelope number
        """
        # Change settings in MWS
        self.log.info("Enable pouch/envelope number prompt...")
        Navi.navigate_to('Register Group Maintenance')
        mws.click_toolbar('Change', submenu=True)
        mws.select_tab('Safe Drops')
        mws.set_value("Prompt for a pouch/envelope number", True)
        if not self._save(timeout=self.long_wait_time):
            tc_fail("MWS settings changes did not save.")
        else:
            self.log.info("MWS settings saved...")
        
        # Do a safe drop
        self.log.info("Attempting to execute a safe drop...")
        if not pos.click('safe drop'):
            tc_fail("Safe drop button did not become visible")
        
        
        if self._in_safe_drop(self.wait_time):
            pos.enter_keypad('1', after='enter')
            if not self._recorded_in_journal('1', timeout=self.wait_time):
                tc_fail("Did not update the transaction journal with the envelope number.")
            pos.enter_keypad('1100', after='+')
            pos.click('finalize')
        else:
            tc_fail("Did not enter safe drop transaction.")

        if pos.read_message_box(timeout=self.wait_time):
            pos.click('yes')
        else:
            tc_fail("Did not ask if the user was sure they wanted to finalize the safe drop transaction.")

        if pos.is_element_present(self.paid_in_button, timeout=self.long_wait_time):
            self.log.info("Safe drop with number prompt succeeded!")
        else:
            tc_fail("Did not finalize the safe drop.  Safe drop failed.")

        
    @test
    def cancel_envelope_number(self):
        """
        Cancel a safe drop with a prompt for envelope number
        """
        # Start a safe drop
        self.log.info("Attempt to get to the safe drop screen...")
        if not pos.click('safe drop'):
            tc_fail("Safe drop button did not become visible.")
        
        # Cancel the safe drop
        self.log.info("Attempting to cancel...")
        if self._in_safe_drop(self.wait_time):
            pos.click('cancel')
        else:
            tc_fail("Did not enter safe drop transaction.")

        if pos.is_element_present(self.paid_in_button, timeout=self.long_wait_time):
            self.log.info("Canceling a safe drop with envelope number prompt succeeded!")
        else:
            tc_fail("Did not successfully cancel a safe drop with envelope number prompt.")


    @test
    def pouch_color(self):
        """
        Do a safe drop with a prompt for pouch color
        """
        # Change settings in MWS
        self.log.info("Enable pouch/envelope color prompt...")
        Navi.navigate_to('Register Group Maintenance')
        mws.click_toolbar('Change', submenu=True)
        mws.select_tab('Safe Drops')
        mws.set_value("Prompt for a pouch/envelope color", True)
        mws.set_value(list="Pouch Colors", control="Black", value=True)
        mws.set_value("Prompt for a pouch/envelope number", False)
        if not self._save(timeout=self.long_wait_time):
            tc_fail("MWS settings changes did not save.")
        else:
            self.log.info("MWS settings saved...")
        
        # Do a safe drop
        self.log.info("Attempting to execute a safe drop...")
        if not pos.click('safe drop'):
            tc_fail("Safe drop button did not become visible.")
        
        if self._in_safe_drop(self.wait_time):
            pos.select_list_item('Black')
            pos.click('enter')
            if not self._recorded_in_journal('Black', timeout=self.wait_time):
                tc_fail("Did not update the transaction journal with the pouch color.")
            pos.enter_keypad('1200', after='+')
            pos.click('finalize')
        else:
            tc_fail("Did not enter safe drop transaction.")

        if pos.read_message_box(timeout=self.wait_time):
            pos.click('yes')
        else:
            tc_fail("Did not ask if the user was sure they wanted to finalize the safe drop transaction.")

        if pos.is_element_present(self.paid_in_button, timeout=self.long_wait_time):
            self.log.info("Safe drop with color prompt succeeded!")
        else:
            tc_fail("Did not finalize the safe drop.  Safe drop failed.")


    @test
    def cancel_pouch_color(self):
        """
        Cancel a safe drop with a prompt for pouch color
        """
        # Start a safe drop
        self.log.info("Attempt to get to the safe drop screen...")
        if not pos.click('safe drop'):
            tc_fail("Safe drop button did not become visible.")
        
        # Cancel the safe drop
        self.log.info("Attempting to cancel...")
        if self._in_safe_drop(self.wait_time):
            pos.click('cancel')
        else:
            tc_fail("Did not enter safe drop transaction.")

        if pos.is_element_present(self.paid_in_button, timeout=self.long_wait_time):
            self.log.info("Canceling a safe drop with pouch color prompt succeeded!")
        else:
            tc_fail("Did not successfully cancel a safe drop with pouch color prompt.")


    @test
    def number_and_color(self):
        """
        Do a safe drop with a prompt for pouch color AND envelope number
        """
        # Change settings in MWS
        self.log.info("Enable pouch/envelope color AND number prompt...")
        Navi.navigate_to('Register Group Maintenance')
        mws.click_toolbar('Change', submenu=True)
        mws.select_tab('Safe Drops')
        mws.set_value("Prompt for a pouch/envelope number", True)
        mws.set_value("Prompt for a pouch/envelope color", True)
        mws.set_value(list="Pouch Colors", control="Black", value=True)
        if not self._save(timeout=self.long_wait_time):
            tc_fail("MWS settings changes did not save.")
        else:
            self.log.info("MWS settings saved...")
        
        # Do a safe drop
        self.log.info("Attempting to execute a safe drop...")
        if not pos.click('safe drop'):
            tc_fail("Safe drop button did not become visible.")
        
        if self._in_safe_drop(self.wait_time):
            pos.select_list_item('Black')
            pos.click('enter')
            pos.enter_keypad('1', after='enter')
            if not self._recorded_in_journal('Black - 1', timeout=self.wait_time):
                tc_fail("Did not update the transaction journal with the pouch color.")
            pos.enter_keypad('1200', after='+')
            pos.click('finalize')
        else:
            tc_fail("Did not enter safe drop transaction.")

        if pos.read_message_box(timeout=self.wait_time):
            pos.click('yes')
        else:
            tc_fail("Did not ask if the user was sure they wanted to finalize the safe drop transaction.")

        if pos.is_element_present(self.paid_in_button, timeout=self.long_wait_time):
            self.log.info("Safe drop with color and number prompt succeeded!")
        else:
            tc_fail("Did not finalize the safe drop.  Safe drop failed.")


    @test
    def cancel_number_and_color(self):
        """
        Cancel a safe drop with a prompt for envelope number AND pouch color
        """
        # Start a safe drop
        self.log.info("Attempt to get to the safe drop screen...")
        if not pos.click('safe drop'):
            tc_fail("Safe drop button did not become visible.")
        
        # Cancel the safe drop on color prompt
        self.log.info("Attempting to cancel on the color prompt...")
        if self._in_safe_drop(self.wait_time):
            pos.click('cancel')
        else:
            tc_fail("Did not enter safe drop transaction.")

        if pos.is_element_present(self.paid_in_button, timeout=self.long_wait_time):
            self.log.info("Canceling the safe drop at the pouch color prompt succeeded...")
        else:
            tc_fail("Did not successfully cancel a safe drop with pouch color prompt.")

        # Start a safe drop
        self.log.info("Attempt to get to the safe drop screen...")
        if not pos.click('safe drop'):
            tc_fail("Safe drop button did not become visible.")

        # Cancel the safe drop on number prompt
        self.log.info("Attempting to cancel on the number prompt...")
        if self._in_safe_drop(self.wait_time):
            pos.click('enter')
            if pos.is_element_present(self.keypad_one, timeout=self.long_wait_time):
                pos.click('cancel')
            else:
                tc_fail("Did not move on to the envelope numebr entry screen.")
        else:
            tc_fail("Did not enter safe drop transaction.")

        if pos.is_element_present(self.paid_in_button, timeout=self.long_wait_time):
            self.log.info("Canceling the safe drop at the envelope number prompt succeeded...")
        else:
            tc_fail("Did not successfully cancel a safe drop with pouch color prompt.")

        self.log.info("Both cancels succeeded!")


    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        self.log.info("Reverting MWS changes...")
        Navi.navigate_to('Register Group Maintenance')
        mws.click_toolbar('Change', submenu=True)
        mws.select_tab('Safe Drops')
        mws.set_value("Prompt for a pouch/envelope number", True)
        mws.set_value("Prompt for a pouch/envelope color", True)
        mws.set_value(list="Pouch Colors", control="Black", value=False)
        mws.set_value("Prompt for a pouch/envelope color", False)
        self._save(timeout=self.long_wait_time)
        mws.click_toolbar('exit')
        pos.close()

    
    def _in_safe_drop(self, timeout):
        """
        Helper function for checking whether the
        message that says "Safe Drop Transaction"
        appears in the transaction journal, which is used
        to confirm that HTML POS is in a safe drop transaction
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            msg = pos.read_transaction_journal()
            if msg == None:
                time.sleep(timeout/10.0)
                continue
            try:
                if "safe drop" in pos.read_transaction_journal()[0][0].lower():
                    return True
            except:
                time.sleep(timeout/10.0)
                continue
        return False


    def _recorded_in_journal(self, envelope, timeout):
        """
        Helper function for checking that the transaction
        journal updates to show the correct number/color
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            msg = pos.read_transaction_journal()
            if msg == None:
                time.sleep(timeout/10.0)
                continue
            try:
                if envelope.lower() in pos.read_transaction_journal()[1][0].lower():
                    return True
            except:
                time.sleep(timeout/10.0)
                continue
        return False


    def _save(self, timeout):
        """
        Helper function for savings settings in the MWS
        """
        start_time = time.time()
        mws.click_toolbar('save')
        time.sleep(0.5)
        start_time = time.time()
        while time.time() - start_time <= timeout:
            msg = mws.get_top_bar_text()
            if not msg:
                return True
        else:
            return False

