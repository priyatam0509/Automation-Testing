"""
    File name: Signon_POS.py
    Tags:
    Description: Script for testing the sign on functionality of HTML POS.
    Author: David Mayes & Gene Todd
    Date created: 02-10-2020
    Date last modified: 02-10-2020
    Python Version: 3.7
"""

import logging, time
from app import Navi, mws, pos, system, runas
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app.features import register_grp_maint

class Signon_POS():
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
        self.max_input_length = 12
        self.paid_in_button = pos.controls['function keys']['paid in']
        self.wait_time = 1

    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        """
        # if not system.restore_snapshot():
        #     self.log.debug("No snapshot to restore, if this is not expected please contact automation team")
        
        #Setup auto sign-off in register group maintenance
        #NOTE: dependant on fix for radio buttons in framework
        rgm = register_grp_maint.RegisterGroupMaintenance()
        rgm.change("POSGroup1", {
            "Accounting": {
                "Automatically sign the operator off after": True,
                "sign off operator minutes of inactivity": 1
            }
        })
        
        pos.connect()

    @test
    def open_new_till(self):
        """
        Make sure the user is prompted to open a new till
        on log in if none has been opened
        """
        # First sign on
        self.log.info("Attempting to sign on...")
        pos.click('sign on')
        pos.enter_keypad('91', after='enter')
        pos.enter_keypad('91', after='ok')

        # If till already open, close till to be able to go through the prompts
        # and sign back on
        if '' == pos.read_status_line():
            self.log.info("Till already opened... closing till...")
            pos.click('close till')
            pos.click('yes')
            
            pos.click('sign on')
            pos.enter_keypad('91', after='enter')
            pos.enter_keypad('91', after='ok')
        
        # Enter the till amount
        msg = pos.read_status_line(timeout = self.wait_time)
        if not msg or not "enter opening amount" in msg.lower():
            tc_fail("Did not ask for an opening till amount.")

        self.log.info("Entering opening till amount...")
        pos.enter_keypad('9900', after='enter')

        if pos.is_element_present(self.paid_in_button, timeout = 20):
            self.log.info("Successfully opened till and signed on!")
        else:
            tc_fail("Did not successfully sign on.")
        if pos.read_balance()['Total'] != "$99.00":
            tc_fail("Did not successfilly open till after sign on.")
           
        pos.sign_off()

    @test
    def without_username_correct_password(self):
        """
        Try to log on without any username input
        but with the correct password for user 91
        """
        # Input no username + password that exists in database
        _failed_signon('', '91')

        # Try to click 'ok' on 'Operator Not Found.' prompt
        pos.click('ok')

        # Make sure it didn't sign on
        if not _on_signin_screen():
            tc_fail("Failed to return to sign on screen.")

    @test
    def without_username_incorrect_password(self):
        """
        Try to log in without a username
        and with an incorrect password
        """
        # Input no username + password that doesn't exist in database
        _failed_signon('', '6')

        # Try to click 'ok' on 'Operator Not Found.' prompt
        pos.click('ok')

        # Make sure it didn't sign on
        if not _on_signin_screen():
            tc_fail("Failed to return to sign on screen.")

    @test
    def wrong_username_correct_password(self):
        """
        Try to log in with a nonexistent username
        and password 91 (which is a password for a user that exists)
        """
        # Input user that doesn't exist in database + password that does exist in database
        _failed_signon('6', '91')

        # Try to click 'ok' on 'Operator Not Found.' prompt
        pos.click('ok')

        # Make sure it didn't sign on
        if not _on_signin_screen():
            tc_fail("Failed to return to sign on screen.")

    @test
    def no_password(self):
        """
        Try to log in with correct username, then no password
        """
        # Input user that exists in database + no password
        _failed_signon('91', '')

        # Try to click 'ok' on 'Operator Not Found.' prompt
        pos.click('ok')

        # Make sure it didn't sign on
        if not _on_signin_screen():
            tc_fail("Failed to return to sign on screen.")

    @test
    def wrong_password(self):
        """
        Try to log on with correct username, then the wrong password
        """
        # Input user that exists in database
        _failed_signon('91', '6')

        # Try to click 'ok' on 'Operator Not Found.' prompt
        pos.click('ok')

        # Make sure it didn't sign on
        if not _on_signin_screen():
            tc_fail("Failed to return to sign on screen.")

    @test
    def go_back(self):
        """
        Try to log on with correct username, then go back to the username input screen
        """
        # Input user that exists in the database
        pos.click('sign on')
        pos.enter_keypad('91', after='enter')

        # Go back
        pos.click('cancel')

        # Make sure it's at the initial sign on screen
        if not _on_signin_screen():
            tc_fail("Failed to return to sign on screen.")
        
    @test
    def correct_credentials(self):
        """
        Try to log on with the correct username and correct password
        """
        # Input username + password combo that exists in the database
        pos.sign_on()

        # Sign off
        if not pos.sign_off():
            tc_fail("Failed to return to sign on screen.")

    @test
    def click_cancel(self):
        """
        Click the cancel button
        """
        # Click the cancel button
        pos.click('sign on')
        pos.click('cancel')
    
    @test
    def without_username_or_password(self):
        """
        Attempt to sign on without any username or password.
        """
        # Input no username + no password
        _failed_signon('', '')

        # Try to click 'ok' on 'Operator Not Found.' prompt
        pos.click('ok')

        # Make sure it didn't sign on
        if not _on_signin_screen():
            tc_fail("Attempting to sign on without username/password caused unexpected behavior")

    @test
    def username_twice(self):
        """
        Input a nonexistent username, click the ok button,
        then click the back button.
        Atfer that, input an existent username and the password that goes with it
        and attempt to sign on.
        """
        # Input a user that doesn't exist in the database
        pos.click('sign on')
        pos.enter_keypad('6', after='enter')

        # Go back
        pos.click('cancel')
        
        # Sign on with correct username + password
        pos.sign_on()

        # Sign off
        if not pos.sign_off():
            tc_fail("Failed to return to sign on screen.")

    @test
    def lock_account(self):
        """
        Set the amount of incorrect sign on attempts it takes
        to lock account, then try to sign on incorrectly that many times
        and make sure it does indeed lock the account.
        """
        # Set the number of sign on attempts allowed
        # Yes... this is hardcoded.  This is the default value
        # for the automation setup; if there's a fast way to actually
        # get/set this value in MWS, feel free to comment
        attempts_allowed = 3

        # Attempt incorrect sign on too many times
        for i in range(0, attempts_allowed+1):
            _failed_signon('91', '6')
            msg = pos.read_message_box(timeout=2)
            if (not msg) or (msg and 'invalid password' not in msg.lower()):
                tc_fail("Correct message not displayed on invalid password input.")
            pos.click('ok')

        _failed_signon('91', '6')

        # Make sure account is locked
        msg = pos.read_message_box()
        if (not msg) or (msg and "locked" not in msg.lower()):
            pos.click('ok')
            tc_fail("Account did not lock after too many login attempts.")

        # Close the message that says account is locked
        pos.click('ok')

        # Reset the amount of incorrect log on attempts for user 91
        # so account will no longer be locked
        runas.run_as('sqlcmd -d globalSTORE -Q "UPDATE PASSWORD_HIST set FAIL_LOGON_CNT=0 where EMP_ID=91"')

    @test
    def expired_password(self):
        """
        Make sure the correct set of procedures occurs
        when an expired password is used
        """
        # Flag user 91's password as expired
        # (STAT = 2 means password has expired)
        runas.run_as('sqlcmd -d globalSTORE -Q "UPDATE PASSWORD_HIST set STAT=2 where EMP_ID=91"')

        # Input expired password
        pos.sign_on(verify=False)

        # Check that it comes up with correct expired password message
        message = pos.read_message_box()
        if message == None or not "password" in message.lower():
            tc_fail("Did not display appropriate message for expired password.")
        pos.click('ok')
        pos.enter_keypad('91', after='ok')
        pos.enter_keypad('91', after='ok')
        pos.click('ok')
        pos.click('cancel')
        if not _on_signin_screen():
            tc_fail("Logged in with expired password.")

        # Flag user 91's password as not expired
        # (STAT = 1 means password isn't expired)
        runas.run_as('sqlcmd -d globalSTORE -Q "UPDATE PASSWORD_HIST set STAT=1 where EMP_ID=91"')
    
    @test
    def test_autoSignOff(self):
        """
        Confirms that auto sign-off fires correctly.
        """
        self.log.info("Signing on")
        pos.sign_on()
        for i in range(6):
            self.log.info(f"[{(6-i)*10}] seconds until auto sign-off")
            time.sleep(10)
        # Give it just an extra second or two
        time.sleep(2)
        # Check if we're signed on
        if pos.click('sign on', verify=False):
            pos.click('cancel')
            self.log.info("Confirmed we are signed out")
        else:
            pos.sign_off()
            tc_fail("Failed to confirm that we are signed out")
    
    @test
    def test_promptNoSignOff(self):
        """
        Confirms yes/no prompts will prevent auto sign-off from firing
        """
        self.log.info("Signing on")
        pos.sign_on()
        pos.click("Close Till")
        for i in range(6):
            self.log.info(f"[{(6-i)*10}] seconds until auto sign-off")
            time.sleep(10)
        # Give it just an extra second or two
        time.sleep(2)
        self.log.info("Closing prompt")
        pos.click_message_box_key('No')
        # Check if we're signed on
        if pos.click('sign on', verify=False):
            pos.click('cancel')
            tc_fail("Auto Sign off triggered during prompt.")
        else:
            self.log.info("Confirmed we are still signed in")
            pos.sign_off()
    
    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        pos.close()


def _on_signin_screen(timeout=2):
    """
    Helper function that determines whether or not
    HTML POS is on the sign-in screen or not
    output:
    True if on sign-in screen
    False if not on sign-in screen
    """
    start_time = time.time()
    while time.time() - start_time <= timeout:
        if pos.driver.execute_script('return posState')['TransactionState'] == 0 and pos.is_element_present(pos.controls['function keys']['sign on']):
            break
    else:
        return False
    return True

def _failed_signon(username='', password=''):
    """
    Helper function to return whether
    a sign on attempt failed (returns True)
    or succeeded (returns False)
    """
    return not pos.sign_on((username, password), verify=False)