"""
    File name: POS_Lock.py
    Tags:
    Description: Script to test lock functionality in HTML POS
    Author: David Mayes
    Date created: 2020-05-01
    Date last modified: 
    Python Version: 3.7
"""

import logging, time
from app import Navi, mws, pos, system
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class POS_Lock():
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
        self.short_wait_time = 1
        self.medium_wait_time = 3
        self.paid_in_button = pos.controls['function keys']['paid in']
        self.unlock_button = pos.controls['function keys']['unlock']
        self.lock_button = pos.controls['function keys']['lock']
        self.sell_item_button = pos.controls['prompt box']['key_by_text'] % 'sell item'
        self.sell_button = pos.controls['prompt box']['key_by_text'] % 'sell'
        self.ok_button = pos.controls['prompt box']['key_by_text'] % 'ok'
        self.generic_item_button = pos.controls['item keys']['key_by_text'] % 'generic item'

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
    def basic_lock(self):
        """
        Attempt a basic lock/unlock with the correct credentials
        """
        self.log.info("Locking HTML POS...")
        pos.click('lock')

        # Attempt to unlock
        self.log.info("Unlocking HTML POS...")
        pos.click('unlock')

        pos.enter_keypad('91', after='enter')
        pos.enter_keypad('91', after='ok')

        # Check the HTML POS returned to main screen (i.e. unlocked)
        if pos.is_element_present(self.paid_in_button, timeout = self.medium_wait_time):
            self.log.info("Successfully locked/unlocked HTML POS with correct credentials!")
        else:
            tc_fail("91/91 did not unlock HTML POS.")


    @test
    def incorrect_username(self):
        """
        Make sure that entering an incorrect username
        displays the correct message
        """
        # Go to the lock screen if not already on it
        if pos.is_element_present(self.lock_button, self.short_wait_time):
            pos.click('lock')
        
        # Enter incorrect username
        self.log.info("Entering incorrect username...")
        pos.click('unlock')
        pos.enter_keypad('90', after='enter')

        # Check that correct message comes up
        msg = pos.read_message_box()

        if msg == None:
            tc_fail("No message appeared.")
        elif not "Operator ID does not match, please re-enter information" in msg:
            self.log.info("Incorrect message showed in message box: " + str(msg))
            pos.click('ok')
            tc_fail("Incorrect message was displayed for incorrect operator ID entry.")
        else:
            self.log.info("Correct message showed up in a message box!")
            pos.click('ok')
    

    @test
    def incorrect_password(self):
        """
        Make sure that entering an incorrect password
        displays the correct message/doesn't unlock
        HTML POS
        """
        # Get rid of the message box if there is one present
        if pos.read_message_box():
            pos.click('ok')
        
        # Go to the lock screen if not already on it
        if pos.is_element_present(self.lock_button, self.short_wait_time):
            pos.click('lock')

        # Attempt to unlock with incorrect password
        self.log.info("Attempting to unlock with an incorrect password...")
        pos.click('unlock')
        pos.enter_keypad('91', after='enter')
        pos.enter_keypad('90', after='ok')

        # Make sure the correct message comes up
        msg = pos.read_message_box()

        if pos.is_element_present(self.paid_in_button, timeout=self.medium_wait_time):
            tc_fail("Unlocked HTML POS with an incorrect password.")

        if msg == None:
            tc_fail("No message appeared.")
        elif not "You have entered an invalid password" in msg:
            self.log.error("Incorrect message displayed in message box: " + str(msg))
            pos.click('ok')
            tc_fail("Incorrect message on incorrect password entry.")
        else:
            self.log.info("Correct message appeared on invalid password entry!")
            pos.click('ok')


    @test
    def price_check(self):
        """
        Make sure you can't sell an item using price check
        """
        # Get rid of the message box if there is one present
        if pos.read_message_box():
            pos.click('ok')
        
        # Go to the lock screen if not already on it
        if pos.is_element_present(self.lock_button):
            pos.click('lock')

        # Make sure the sell item button doesn't come up
        # and clicking ok doesn't send HTML POS into a weird state
        self.log.info("Checking that price check doesn't cause any weird behavior...")
        pos.click('price check')
        pos.click('generic item')

        # Wait until the message box is visible to check for buttons
        pos.read_message_box()

        if pos.is_element_present(self.sell_item_button, timeout = self.short_wait_time)\
         or pos.is_element_present(self.sell_button, timeout = self.short_wait_time):
            pos.click('ok')
            tc_fail("Button allowing you to sell an item appeared.")
        
        pos.click('ok')

        if self._element_not_present(element=self.paid_in_button, timeout = self.short_wait_time)\
         and self._element_not_present(element=self.generic_item_button, timeout = self.short_wait_time):
            self.log.info("Everything checks out with price check on the locked screen!")
        else:
            tc_fail("Clicking OK caused buttons to appear")


    @test
    def cancel(self):
        """
        Make sure the cancel button on the keypad does what it's supposed to do
        """
        pos.click('unlock')

        # Click cancel and make sure it returns to unlock screen
        self.log.info("Clicking cancel on username input...")
        pos.click('cancel')
        if pos.is_element_present(self.unlock_button, timeout = self.short_wait_time):
            self.log.info("Returned to locked screen after clicking cancel on username input...")
        else:
            tc_fail("Did not return to locked screen after clicking cancel on username input.")

        self.log.info("Clicking cancel on password input...")
        pos.click('unlock')
        pos.enter_keypad('91', after='enter')
        pos.click('cancel')
        if pos.is_element_present(self.unlock_button, timeout = self.short_wait_time):
            self.log.info("Returned to locked screen after clicking cancel on password input...")
        else:
            tc_fail("Did not return to locked screen after clicking cancel on password input.")
        
        self.log.info("Correctly returned to locked screen after cancelling on both username and password input screens!")
    
    # TODO: Once all buttons are implemented for the tools/signed off state,
    #       add a test case that checks for those buttons
        

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        if pos.is_element_present(self.unlock_button, timeout = self.short_wait_time):
            pos.click('unlock')
            pos.enter_keypad('91', after='enter')
            pos.enter_keypad('91', after='ok')
        pos.close()


    def _element_not_present(self, element, timeout):
        """
        Helper function for determining if a button
        or other element is not visible on the screen
        for cases when it takes time for the element to disappear
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if pos.is_element_present(element, timeout=timeout/10.0) == False:
                return True
        else:
            return False
