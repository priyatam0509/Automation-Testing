"""
    File name: POS_Receipt_Search.py
    Tags:
    Description: Script for testing receipt search in HTML POS.
    Author: David Mayes
    Date created: 2020-06-18
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import Navi, mws, pos, system
from app.framework.tc_helpers import setup, test, teardown, tc_fail

default_timeout = 3

class POS_Receipt_Search():
    """
    Holds test cases
    """

    def __init__(self):
        """
        Initializes the POS_Receipt_Search class
        """
        # The logging object. 
        # Example: self.log.info(f"Current value of var: {my_var}")
        self.log = logging.getLogger()
        self.disp_1 = pos.controls['forecourt']['dispenser'] % '1'
        self.dispensers = pos.controls['receipt search']['dispensers']

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
    def cancel(self):
        """
        Cancel out of receipt search and make sure it returns to
        the last screen it was on
        """
        if not self._return_to_main_screen():
            tc_fail("Was not on main screen/could not return to main screen at the beginning of the cancel test case.")

        # Go back from the main screen
        pos.click("receipt search")
        
        if not self._on_receipt_search_screen():
            tc_fail("Did not open the receipt search screen.")
        
        pos.click("back")

        if not self._on_main_screen():
            tc_fail("Did not return to main screen after clicking the back button.")

        # Go back from the dispenser screen
        pos.click_key(self.disp_1)

        if not self._on_dispenser_screen():
            tc_fail("Did not open the dispenser screen.")

        pos.click("receipt")
        pos.click("back")

        if not self._on_dispenser_screen():
            tc_fail("Did not return to the dispenser screen after clicking back on the receipt search screen.")

        if not self._return_to_main_screen():
            self.log.warning("Failed to return to the main screen at the end of cancel test case!")
        
        self.log.info("The back button on the receipt search screen worked as intended!")


    @test
    def register_receipts(self):
        """
        Do a standard transaction on the register and make sure its
        receipt shows up in receipt search
        """
        if not self._return_to_main_screen():
            tc_fail("Was not on main screen/could not return to main screen at the beginning of the normal_receipt test case.")

        pos.click("generic item")
        pos.pay()

        if not self._on_main_screen():
            tc_fail("Failed to return to the main screen after attempting to pay for a generic item.")

        pos.click("receipt search")

        if not self._on_receipt_search_screen():
            tc_fail("Did not open the receipt search screen.")

        pos.check_receipt_for("Generic Item")
        pos.check_receipt_for("$0.01")

        if not self._return_to_main_screen():
            self.log.warning("Failed to return to the main screen at the end of register_receipts test case!")
        
        self.log.info("Register receipt appeared in the transaction journal!")
    
    
    @test
    def dispenser_receipts(self):
        """
        Do a crind transaction and make sure its receipt shows up
        in receipt search
        """
        if not self._return_to_main_screen():
            tc_fail("Was not on main screen/could not return to main screen at the beginning of the dispenser_receipt test case.")

        pos.click_key(self.disp_1)

        if not self._on_dispenser_screen():
            tc_fail("Did not change to dispenser screen.")

        pos.click("prepay")
        pos.enter_keypad("1000", after="enter")
        pos.click("pay")
        pos.click_tender_key("Exact Change")
        if pos.read_message_box():
            pos.click("ok")
        pos.wait_for_fuel(timeout=120)

        if self._on_dispenser_screen():
            pos.click("receipt")
        else:
            if not self._return_to_main_screen():
                tc_fail("Failed to return to main screen.")
            pos.click("receipt journal")

        pos.click("select terminal")

        pos.click_key(self.dispensers % "Dispenser 1")

        pos.check_receipt_for("$1.000/GAL")
        pos.check_receipt_for("$10.00")

        if not self._return_to_main_screen():
            self.log.warning("Failed to return to the main screen at the end of dispenser_receipt test case!")
        
        self.log.info("Dispenser receipt appeared in the receipt journal!")
        

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        self._return_to_main_screen()
        pos.close()


    def _on_main_screen(self, timeout=default_timeout):
        """
        Helper function to determine whether HTML POS
        is on the main signed in screen
        """
        return pos.is_element_present(pos.controls['function keys']['paid in'], timeout=timeout)


    def _on_dispenser_screen(self, timeout=default_timeout):
        """
        Helper function to determine whether HTML POS
        is on a dispenser screen (i.e. the screen you get
        when you click a dispenser at the bottom)
        """
        return pos.is_element_present(pos.controls['function keys']['prepay'], timeout=timeout)
    

    def _on_receipt_search_screen(self, timeout=default_timeout):
        """
        Helper function to determine whether HTML POS
        is on the receipt search screen
        """
        return pos.is_element_present(pos.controls['function keys']['select terminal'], timeout=timeout)

    
    def _in_transaction(self, timeout=default_timeout):
        """
        Helper function to determine whether HTML POS
        is in a transaction
        """
        return pos.is_element_present(pos.controls['function keys']['void transaction'], timeout=timeout)
    

    def _return_to_main_screen(self, timeout=default_timeout):
        """
        Helper function to make sure HTML POS is on the main signed in screen/
        return HTML POS to the main signed in screen if not
        """
        if self._on_main_screen(timeout=timeout):
            self.log.info("On the main screen...")
            return True
        elif self._in_transaction(timeout=timeout):
            if not pos.void_transaction():
                self.log.warning("Failed to return to main screen!")
                return False
            if not self._on_main_screen(timeout=timeout):
                self.log.warning("Failed to return to main screen!")
                return False
            self.log.info("On the main screen...")
            return True
        elif self._on_receipt_search_screen(timeout=timeout):
            if not pos.click("back"):
                self.log.warning("Failed to return to main screen!")
                return False
            if self._on_dispenser_screen():
                if not pos.click("back"):
                    self.log.warning("Failed to return to main screen!")
                    return False
            if self._in_transaction():
                if not pos.void_transaction():
                    self.log.warning("Failed to return to main screen!")
                    return False
            if not self._on_main_screen(timeout=timeout):
                self.log.warning("Failed to return to main screen!")
                return False
            self.log.info("On the main screen...")
            return True
        elif self._on_dispenser_screen(timeout=timeout):
            if not pos.click("back"):
                self.log.warning("Failed to return to main screen!")
                return False
            if self._in_transaction():
                if not pos.void_transaction():
                    self.log.warning("Failed to return to main screen!")
                    return False
            if not self._on_main_screen(timeout=timeout):
                self.log.warning("Failed to return to main screen!")
                return False
            self.log.info("On the main screen...")
            return True
        else:
            self.log.warning("On an unknown screen!")
            return False
        
            
            
