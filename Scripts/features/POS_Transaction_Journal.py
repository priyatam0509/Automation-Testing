"""
    File name: POS_Transaction_Journal.py
    Tags:
    Description: HTML POS script to test the functionality of the transaction journal.
    Author: David Mayes
    Date created: 2020-06-02
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import pos, system
from app.framework.tc_helpers import setup, test, teardown, tc_fail

default_timeout = 20

class POS_Transaction_Journal():
    """
    Class for testing
    """

    def __init__(self):
        """
        Initializes the POS_Transaction_Journal class
        """
        # The logging object. 
        # Example: self.log.info(f"Current value of var: {my_var}")
        self.log = logging.getLogger()
        self.short_wait_time = 1


    @setup
    def setup(self):
        """
        Performs initialization
        """
        # if not system.restore_snapshot():
        #     self.log.debug("No snapshot to restore, if this is not expected please contact automation team")
        pos.connect()
        pos.sign_on()


    @test
    def line_limit(self):
        """
        Make sure HTML POS responds to the setting located at
        Register Group Maintenance > Change > Transaction Options >
        Maximum number of line items (100 by default)
        """
        # Add 100 items
        self.log.info("Adding 100 items to a transaction...")
        for i in range(0, 100):
            if not pos.click('generic item', verify=False):
                ending = self.parse_english(i)
                msg = pos.read_message_box(timeout=self.short_wait_time)
                if msg == None:
                    pos.pay()
                    tc_fail("Failed to click generic item speedkey when attempting to add " + str(i) + ending +\
                     " to the transaction.  No message box appeared.")
                elif msg:
                    pos.click('ok')
                    pos.pay()
                    tc_fail("Message box appeared after adding the " + str(i) + ending + " item.  It should appear only"\
                     "after adding more than 100 line items.  Message box said: " + msg)
        
        # Go over line item limit
        self.log.info("Attempting to add the 101st item and checking that the correct error message appears...")
        if not pos.click('generic item', verify=False):
            if pos.read_message_box():
                pos.click('ok')
                pos.pay()
                tc_fail("Error message appeared after adding 100 items.  It should appear on addition of the 101st item.")
        msg = pos.read_message_box()
        if msg == None:
            pos.pay()
            tc_fail("No message box appeared after going over the line item limit.")
        elif not "max" in msg.lower():
            pos.click('ok')
            pos.pay()
            tc_fail("Message box did not contain the right message.  It contained: " + msg)
        
        self.log.info("Correct message appeared after trying to go over the line item limit...")

        pos.click('ok')
        pos.pay()

        self.log.info("HTML POS obeys max line items MWS setting!")


    @test
    def quantity_limit(self):
        """
        Make sure HTML POS responds to the setting located at
        Register Group Maintenance > Change > Transaction Options >
        Maximum quantity that can be set for an item (25 by default)
        """
        # Make sure HTML POS is on the main screen
        if self._on_main_screen():
            self.log.info("Verified that HTML POS is on the main screen...")
        else:
            tc_fail("Did not appear to be on the main screen after " + str(default_timeout) + " seconds.")
        
        # Start transaction
        self.log.info("Adding an item...")
        pos.click('generic item')

        # Change quantity above max
        pos.click('change item qty')
        self.log.info("Attempting to change the quantity above max...")
        pos.enter_keypad('26', after='enter')
        msg = pos.read_message_box()
        if msg == None:
            tc_fail("No error message appeared.")
        elif not "max" in msg.lower():
            pos.click('ok')
            tc_fail("Incorrect error message displayed.")
        
        self.log.info("Correct error message displayed...")
        pos.click('ok')

        # Change quantity below max
        pos.click('change item qty')
        self.log.info("Attempting to change the quantity below max...")
        pos.enter_keypad('25', after='enter')
        if not pos.pay(verify=False):
            msg = pos.read_message_box()
            if msg:
                pos.click('ok')
                tc_fail("The following message displayed after entering a quantity below the max: "\
                 + msg)
            tc_fail("Failed to pay.")

        self.log.info("Successfully changed the item quantity below the max...")

        self.log.info("HTML POS obeys max individual item quantity MWS setting!")

        

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        pos.close()

    
    def parse_english(self, x):
        """
        Helper function for finding the proper English
        ending for an ordinal number
        """
        number = str(x)
        if len(number) == 2 and number[-2:-1] == '1':
            return 'th'
        elif number[-1:] == '1':
            return 'st'
        elif number[-1:] == '2':
            return 'nd'
        elif number [-1:]:
            return 'rd'
        else:
            return 'th'

        
    def _on_main_screen(self, timeout=default_timeout):
        """
        Helper function to make sure
        HTML POS is on its main screen
        """
        return pos.is_element_present(pos.controls['function keys']['paid in'], timeout=timeout)