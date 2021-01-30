"""
    File name: POS_Reset_Password.py
    Tags:
    Description: Test reset password functionality/button in HTML POS.
    Author: David Mayes
    Date created: 2020-08-17 16:11:33
    Date last modified: 
    Python Version: 3.7
"""

import logging, time
from app import Navi, mws, pos, system, runas
from app.framework.tc_helpers import setup, test, teardown, tc_fail

default_timeout = 10

class POS_Reset_Password():
    """
    Description: Test class that provides an interface for testing.
    """

    def __init__(self):
        """
        Initializes the POS_Reset_Password class
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
    def before_lock_signed_off(self):
        """
        Reset password button shouldn't work for account that isn't locked on sign on screen
        """
        # Make sure we're on the right screen
        if not self._return_to_signon_screen():
            tc_fail("Failed to return to the sign on screen to start the test case.")

        # Attempt reset password on account that isn't locked
        self.log.info("Clicking reset password and entering user ID...")
        pos.click("reset password")
        pos.enter_keypad("91", after="enter")

        self.log.info("Checking message that appears...")
        msg = pos.read_message_box()
        if msg == None:
            pos.click("cancel", verify=False)
            tc_fail("No message appeared notifying the user that the account entered is not locked.")
        if not "not" in msg.lower():
            pos.click("ok", verify=False)
            tc_fail("Message box did not contain the correct message.  Message should be about the account not being locked, but instead it was: " + msg)
        
        pos.click("ok")
        self.log.info("Correct message was displayed when trying to reset password for account that is not locked!")


    @test
    def before_lock_locked(self):
        """
        Reset password button shouldn't work for account that isn't locked on the lock screen
        """
        # Make sure we're on the right screen
        if not self._return_to_locked_screen():
            tc_fail("Failed to return to the lock screen to start the test case.")

        # Attempt reset password on account that isn't locked
        self.log.info("Clicking reset password and entering user ID...")
        pos.click("reset password")
        pos.enter_keypad("91", after="enter")

        self.log.info("Checking message that appears...")
        msg = pos.read_message_box()
        if msg == None:
            pos.click("cancel", verify=False)
            tc_fail("No message appeared notifying the user that the account entered is not locked.")
        if not "not" in msg.lower():
            pos.click("ok", verify=False)
            tc_fail("Message box did not contain the correct message.  Message should be about the account not being locked, but instead it was: " + msg)
        
        pos.click("ok")
        self.log.info("Correct message was displayed when trying to reset password for account that is not locked!")
    

    @test
    def incorrect_birthday(self):
        """
        Lock account with too many incorrect passwords and try to reset password but with the incorrect birthdate
        """
        # Make sure we're on the right screen
        if not self._return_to_signon_screen():
            tc_fail("Failed to return to the sign on screen to start the test case.")

        # Lock the account
        self.log.info("Attempting to lock account 91...")
        max_tries = 10
        i = 0
        while i < max_tries:
            self._incorrect_signon()
            i+=1
            msg = pos.read_message_box()
            if msg == None or not "lock" in msg.lower():
                continue
            else:
                self.log.info("Account has been successfully locked...")
                pos.click("ok")
                break
        else:
            tc_fail("Account 91 should be locked by now, but is not.")

        # Try to reset using incorrect birthdate
        self.log.info("Entering user ID on reset password...")
        pos.click("reset password")
        pos.enter_keypad("91", after="enter")

        self.log.info("Checking status line...")
        msg = pos.read_status_line()
        if msg == None:
            tc_fail("No status line message asking for birthdate appeared after entering user ID on reset password.")
        elif not "birth" in msg.lower():
            pos.click("cancel", verify=False)
            tc_fail("Incorrect message displayed in the status line.  Should say something about entering birthday, but instead says: " + msg)
        
        self.log.info("Entering birthdate...")
        pos.enter_keypad("01011971", after="enter")

        # Make sure correct message appears
        self.log.info("Checking message...")
        msg = pos.read_message_box()
        if msg == None:
            tc_fail("No message appeared notifying that birthdate was incorrect.")
        elif not "birthdate" in msg.lower():
            pos.click("ok", verify=False)
            pos.click("cancel", verify=False)
            tc_fail("Incorrect message displayed.  Message should say something about birthdate being incorrect; instead, it said: " + msg)
        self.log.info("Correct message appeared notifying of incorrect birthdate...")

        pos.click("ok")
        pos.click("cancel")
        

    @test
    def unlock_account(self):
        """
        Lock account with too many incorrect passwords and reset password
        """
        # Make sure we're on the right screen
        if not self._return_to_signon_screen():
            tc_fail("Failed to return to the sign on screen to start the test case.")

        # Lock the account
        self.log.info("Attempting to lock account 91...")
        max_tries = 10
        i = 0
        while i < max_tries:
            self._incorrect_signon()
            i+=1
            msg = pos.read_message_box()
            if msg == None or not "lock" in msg.lower():
                continue
            else:
                self.log.info("Account has been successfully locked...")
                pos.click("ok")
                break
        else:
            tc_fail("Account 91 should be locked by now, but is not.")

        # Reset the password to the locked account
        self.log.info("Entering user ID on reset password...")
        pos.click("reset password")
        pos.enter_keypad("91", after="enter")

        self.log.info("Checking status line...")
        msg = pos.read_status_line()
        if msg == None:
            tc_fail("No status line message asking for birthdate appeared after entering user ID on reset password.")
        elif not "birth" in msg.lower():
            pos.click("cancel", verify=False)
            tc_fail("Incorrect message displayed in the status line.  Should say something about entering birthday, but instead says: " + msg)
        
        self.log.info("Entering birthdate...")
        pos.enter_keypad("01011970", after="enter")

        # Check that password was reset
        msg = pos.read_message_box()

        if msg == None:
            tc_fail("No message saying that the password was reset appeared.")
        elif not "reset" in msg.lower():
            pos.click("ok", verify=False)
            tc_fail("The message that appeared does not mention the password being reset.  Instead it says: " + msg)
        
        self.log.info("Message appeared noting that the password was reset...")
        pos.click("ok")

        # Try old password
        pos.click("sign on")
        pos.enter_keypad("91", after="enter")
        pos.enter_keyboard("91", after="ok")

        msg = pos.read_message_box()
        if msg == None:
            tc_fail("No message appeared after entering the old password.")
        if not "invalid" in msg.lower():
            pos.click("ok", verify=False)
            tc_fail("Incorrect message appeared on old password entry.  Should say something about an invalid password; instead said: " + msg)
        pos.click("ok")
        self.log.info("Correct behavior occurred when trying to use the old password...")

        # Set password back to 91
        self.log.info("Signing in with 1234567 as the password...")
        pos.click("sign on")
        pos.enter_keypad("91", after="enter")
        pos.enter_keyboard("1234567", after="ok")

        runas.run_as('sqlcmd -d globalSTORE -Q "delete from PASSWORD_HIST where EMP_ID = 91 and STAT = 3"')
        
        msg = pos.read_message_box()

        if msg == None:
            tc_fail("No message appeared notifying that you need to enter a new password.")
        if not "new" in msg.lower():
            pos.click("ok", verify=False)
            tc_fail("Message box should say something about entering a new password.  Instead it said: " + msg)

        self.log.info("Message appeared notifying that you need to enter a new password...")
        pos.click("ok")

        self.log.info("Entering a new password...")
        pos.enter_keyboard("91", after="ok")
        pos.enter_keyboard("91", after="ok")

        msg = pos.read_message_box()

        if msg == None:
            tc_fail("No message appeared notifying the user that the password has been reset.")
        elif not "password" in msg.lower():
            pos.click("ok", verify=False)
            tc_fail("Instead of saying something about the password being reset, the message said: " + msg)
        
        pos.click("ok")

        if not self._on_main_screen(timeout=20):
            tc_fail("HTML POS did not sign on after resetting the password.")

        self.log.info("Successfully reset password!")
        

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        runas.run_as('sqlcmd -d globalSTORE -Q "delete from PASSWORD_HIST where EMP_ID = 91 and STAT = 3"')
        pos.close()


    def _incorrect_signon(self, username="91", password="92", timeout=default_timeout):
        """
        Helper function to make it easier to attempt to sign on with an incorrect password
        """
        pos.click("sign on")
        pos.enter_keypad(username, after="enter")
        pos.enter_keyboard(password, after="ok")
        
        start_time = time.time()
        while start_time - time.time() <= timeout:
            msg = pos.read_message_box(timeout=0.25)
            if msg == None:
                continue
            elif not "password" in msg.lower():
                tc_fail("The word 'password' did not appear in the message box notifying that the password was incorrect.")
            elif "lock" in msg.lower():
                self.log.info("Account locked...")
                return True
            else:
                if pos.click("ok", verify=False):
                    self.log.info("Incorrect sign on attempt was executed.")
                    return True
                else:
                    tc_fail("Failed to click 'ok' at invalid password entry message.")
        else:
            tc_fail("Message notifying user of incorrect password entry did not appear.")
        
        # In case stuff goes past all of this somehow
        return False


    def _on_signon_screen(self, timeout=default_timeout):
        """
        Helper function to determine if HTML POS is on the sign on screen
        """
        return pos.is_element_present(pos.controls['function keys']['sign on'], timeout=timeout)


    def _on_lock_screen(self, timeout=default_timeout):
        """
        Helper function to determine if HTML POS is on the lock screen
        """
        return pos.is_element_present(pos.controls['function keys']['unlock'], timeout=timeout)

    
    def _on_main_screen(self, timeout=default_timeout):
        """
        Helper function to determine if HTML POS is on the main idle screen
        """
        return pos.is_element_present(pos.controls['function keys']['paid in'], timeout=timeout)

    
    def _return_to_signon_screen(self, timeout=default_timeout):
        """
        Helper function to return HTML POS to the sign on screen from some common places
        """
        signon_button = pos.controls['function keys']['sign on']
        signoff_button = pos.controls['function keys']['sign-off']
        unlock_button = pos.controls['function keys']['unlock']
        cancel_button = pos.controls['keypad']['cancel']


        if self._on_signon_screen(timeout=timeout/10.0):
            self.log.info("Already on the sign on screen...")
            return True
        else:
            if pos.is_element_present(cancel_button):
                self.log.info("Clicking cancel...")
                pos.click_key(cancel_button)
            if pos.is_element_present(unlock_button):
                self.log.info("Unlocking...")
                pos.sign_on()
            if pos.is_element_present(signoff_button):
                self.log.info("Signing off")
                pos.sign_off()

        if self._on_signon_screen(timeout=20.0):
            self.log.info("Returned to the sign on screen...")
            return True
        else:
            self.log.warning("Failed to return to the sign on screen.")
            return False

        
    def _return_to_locked_screen(self, timeout=default_timeout):
        """
        Helper function to return HTML POS to the locked screen from some common places
        """
        cancel_button = pos.controls['keypad']['cancel']

        if self._on_lock_screen(timeout=timeout/10.0):
            self.log.info("Already on the lock screen...")
            return True
        if pos.is_element_present(cancel_button):
            self.log.info("Clicking cancel...")
            pos.click_key(cancel_button)
        if self._on_signon_screen():
            self.log.info("Signing on...")
            pos.sign_on()
        if self._on_main_screen():
            self.log.info("Clicking lock...")
            pos.click("lock")
        
        if self._on_lock_screen(timeout=20.0):
            self.log.info("Returned to lock screen...")
            return True
        else:
            self.log.warning("Failed to return to lock screen.")
            return False
            

            