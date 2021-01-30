"""
    File name: PasswordChange_POS.py
    Tags:
    Description: 
    Author: 
    Date created: 2020-02-18 13:06:27
    Date last modified: 
    Python Version: 3.7
"""

import logging, time
from app import Navi, mws, pos, system, runas
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class PasswordChange_POS():
    """
    Description: Test class that provides an interface for testing.
    """

    def __init__(self):
        """
        Initializes the Template class.
        """
        self.log = logging.getLogger()
        # Record what the password was changed to for the next test
        self.password = "91"

    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        """
        #if not system.restore_snapshot():
        #    self.log.debug("No snapshot to restore, if this is not expected please contact automation team")
        
        self.log.info("Connecting to POS")
        pos.connect()
        time.sleep(2) # Connect is not waiting long enough
        self.log.info("Attempting to sign on")
        pos.sign_on()
        pos.click_function_key("Tools")

    @test
    def test_wrongPassword(self):
        """
        Confirms we cannot change password with the wrong initial password
        """
        # Start password change
        self.log.info("Clicking 'Change Password'")
        pos.click_function_key("Change Password")       
        
        # Enter in the wrong password.
        # Need valid newpassword to get correct error.
        self.log.info("Entering in the wrong password")
        pos.enter_keyboard("123", after="Ok")
        self.log.info("Entering remaining information")
        pos.enter_keyboard("123", after="Ok")
        pos.enter_keyboard("123", after="Ok")
        
        # Confirm the password change fails.
        self._confirmMessage("Password change failed.")
    
    @test
    def test_differentNewPasswords(self):
        """
        Tests that we fail to change password if our confirmation password does not match the initial.
        """
        # Start password change
        self.log.info("Clicking 'Change Password'")
        pos.click_function_key("Change Password")
        
        # Enter in current password - desired prompt preceeds check for accuracy.
        self.log.info("Entering in current password")
        pos.enter_keyboard(self.password, after="Ok")
        
        # Enter in different passwords for intial and confirmation
        self.log.info("Entering '123' for intial password")
        pos.enter_keyboard("123", after="Ok")
        self.log.info("Entering '321' for intial password")
        pos.enter_keyboard("321", after="Ok")
        
        # Confirm the password change fails. Cancel re-prompt
        self._confirmMessage("New password and confirmation don't match.")
        pos.enter_keyboard("", after="Cancel")
    
    @test
    def test_successfulChange(self):
        """
        Confirm we can properly change password
        """
        # Start password change
        self.log.info("Clicking 'Change Password'")
        pos.click_function_key("Change Password")
        
        # Enter in current password
        self.log.info("Entering in current password")
        pos.enter_keyboard(self.password, after="Ok")
        
        # Enter in new password
        self.password = "123"
        self.log.info(f"Entering [{self.password}] for new password")
        pos.enter_keyboard(self.password, after="Ok")
        pos.enter_keyboard(self.password, after="Ok")
        
        # Confirm the password change fails.
        self._confirmMessage("Password changed.")
    
    @test
    def test_minPasswordLength(self):
        """
        Tests that we warn for too short of a password
        """
        # Start password change
        self.log.info("Clicking 'Change Password'")
        pos.click_function_key("Change Password")
        
        # Enter in current password
        self.log.info("Entering in current password")
        pos.enter_keyboard(self.password, after="Ok")
        
        # Enter in too short of a password
        temp_password = "1"
        self.log.info(f"Entering [{temp_password}] for new password")
        pos.enter_keyboard(temp_password, after="Ok")
        pos.enter_keyboard(temp_password, after="Ok")
        
        # Confirm the password change fails. Cancel re-prompt
        self._confirmMessage("Password too short.")
        pos.enter_keyboard("", after="Cancel")
    
    @test
    def test_maxPasswordLength(self):
        """
        Tests that we warn for too long of a password
        """
        # Start password change
        self.log.info("Clicking 'Change Password'")
        pos.click_function_key("Change Password")
        
        # Enter in current password
        self.log.info("Entering in current password")
        pos.enter_keyboard(self.password, after="Ok")
        
        # Enter in too long of a password
        temp_password = "123456789a123456789b1"
        self.log.info(f"Entering [{temp_password}] for new password")
        pos.enter_keyboard(temp_password, after="Ok")
        pos.enter_keyboard(temp_password, after="Ok")
        
        # Confirm the password change fails. Cancel re-prompt
        self._confirmMessage("Password too long.")
        pos.enter_keyboard("", after="Cancel")
    
    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        # Reset the password - more reliable than trying to through POS
        self.log.info("Deleting user 91 password history")
        runas.run_as('sqlcmd -d GlobalSTORE -Q "delete from PASSWORD_HIST where EMP_ID=91"')
        self.log.info("Signing off and back on MWS")
        try:
            mws.sign_off()
        except:
            self.log.info("Failed to sign off. Likely already signed in.")
        try:
            mws.sign_on()
        except:
            self.log.warning("Failed to sign in. Passwords may fail for subsequent tests.")
        
        pos.close()

    # Helper function to confirm that we got a warning about the limit
    def _confirmMessage(self, target_msg=None):
        msg = pos.read_message_box()
        pos.click_message_box_key("Ok", verify=False)
        if not msg and not target_msg:
            self.log.info("Confirmed no message")
        if msg == target_msg:
            self.log.info("Confirmed desired message")
        else:
            tc_fail(f"Did not find desired Message. Message found: [{msg}]")
    
