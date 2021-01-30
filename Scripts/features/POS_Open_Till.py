"""
    File name: POS_Open_Till.py
    Tags:
    Description: Script for testing functionality of opening a till.
    Author: 
    Date created: 2020-06-18 15:23:09
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import Navi, mws, pos, system
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class POS_Open_Till():

    def __init__(self):
        """
        Initializes the Template class.
        """
        # The logging object. 
        # Example: self.log.info(f"Current value of var: {my_var}")
        self.log = logging.getLogger()

    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        """
        if not system.restore_snapshot():
            self.log.debug("No snapshot to restore, if this is not expected please contact automation team")
        pos.connect()

        # Sign off / close till if necessary
        if pos.is_element_present(pos.controls['function keys']['sign-off']):
            pos.click("close till")
            pos.click("yes")
            pos.click("no")
            pos.is_element_present(pos.controls['function keys']['sign on'], timeout=20)
        elif pos.is_element_present(pos.controls['function keys']['sign on']):
            pos.sign_on()
            pos.click("close till")
            pos.click("yes")
            pos.click("no")
            pos.is_element_present(pos.controls['function keys']['sign on'], timeout=20)
        

    @test
    def test_openTill(self):
        """
        Basic test attempting to open a till.
        """
        self.simpleSignOn()
        
        # Verify that we were prompted to enter our opening till
        msg = pos.read_status_line()
        if not msg or not "Opening Amount" in msg:
            tc_fail(f"Desired status line not found. Found: [{msg}]")
        self.log.info("Found desired status line")
            
        # Enter an amount for the till, and close till for next test
        # Pressence of close till button confirms we signed in
        pos.enter_keypad('1000', after="Enter")
        self.closeTill()
        
    @test
    def test_cancelOpenTill(self):
        """
        Ensure that the till is required for sign on.
        """
        self.simpleSignOn()
        
        # Cancel open till and confirm warning appears
        pos.click_function_key("Cancel")
        msg = pos.read_message_box()
        if not msg or not "You haven't entered an opening till" in msg:
            tc_fail(f"Desired message not found. Found: [{msg}]")
        self.log.info("Found desired warning message")
        pos.click("Yes")
        
        self.closeTill()
        
    @test
    def test_presetTill(self):
        """
        Test that we can set a preconfigured amount for the till to open with
        """
        # Set the toggle in the MWS
        pos.close() # get the browser out of the way of the MWS
        self.log.info("Setting preconfigured till amount in the MWS...")
        Navi.navigate_to('Register Group Maintenance')
        mws.click_toolbar('Change')
        mws.select_tab('Till Counts')
        
        # Change values - read first to make sure we wait for tab to load
        mws.set_value("loan amount", 7500)
        mws.set_value("The opening loan for every till should automatically be", True)

        if not mws.click_toolbar('Save'):
            tc_fail("Failed to save changes.")
        self.log.info("Saved change to preconfigured till amount in till counts...")
        pos.connect() # Reopen browser
        
        self.simpleSignOn()
        
        # Make sure the till prompt did not appear
        msg = pos.read_status_line()
        if msg:
            tc_fail(f"Unexpected status line found: [{msg}]")
            
        self.closeTill()
        
    @test
    def test_suppressTill(self):
        """
        Confirm that we do not prompt for open till amounts when it is suppressed
        """
        # Set the toggle in the MWS
        pos.close() # get the browser out of the way of the MWS
        self.log.info("Toggling the suppress setting in the MWS...")
        Navi.navigate_to('Register Group Maintenance')
        mws.click_toolbar('Change')
        mws.select_tab('Till Counts')
        
        mws.set_value("Suppress opening/closing till counts", True)

        if not mws.click_toolbar('Save'):
            tc_fail("Failed to save changes.")
        self.log.info("Saved change to suppress opening/closing till counts...")
        pos.connect() # Reopen browser
        
        self.simpleSignOn()
        
        # Check for and answer open till prompt
        msg = pos.read_message_box()
        if not msg or not "start a new till" in msg:
            tc_fail(f"Desired message not found. Found: [{msg}]")
        pos.click("Yes")
        
        # Make sure the till amount was not requested
        msg = pos.read_status_line()
        if msg:
            tc_fail(f"Unexpected status line found: [{msg}]")
            
        self.closeTill(suppressed=True)
        
    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        pos.close()
        # Revert changes for future tests
        self.log.info("Toggling the suppress setting in the MWS...")
        Navi.navigate_to('Register Group Maintenance')
        mws.click_toolbar('Change')
        mws.select_tab('Till Counts')
        mws.set_value("Suppress opening/closing till counts", False)
        mws.set_value("Operator enters opening balance by lump sum", True)
        mws.click_toolbar('Save')

    def simpleSignOn(self):
        """
        Helper function to handle signing on, without trying to handle the till
        """
        self.log.info("Attempting to sign on")
        pos.click("sign on")
        pos.enter_keypad("91", after="Enter")
        pos.enter_keyboard("91", after="Ok")
        self.log.info("sign on information entered")
        
    def closeTill(self, suppressed=False):
        """
        Helper functionn to handle closing till for next test
        """
        self.log.info("Closing Till")
        pos.click("close till")
        pos.click("Yes") # Yes to close till prompt
        if not suppressed:
            pos.click("No") # No to balance till prompt
        self.log.info("Till closed")