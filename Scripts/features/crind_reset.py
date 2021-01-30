"""
    File name: crind_reset.py
    Tags:
    Description: Merlin 1405 - Implement CRIND Reset for HTML POS
    Author: Kevin Walker
    Date created: 2020-07-08 14:23:03
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import Navi, mws, pos, system, crindsim
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class crind_reset():
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

    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        """
        # if not system.restore_snapshot():
        #     self.log.debug("No snapshot to restore, if this is not expected please contact automation team")
        crindsim.set_mode("manual")
        pos.connect()
        pos.sign_on()
        

    @test
    def idle_reset(self):
        """
        Verify the crind resets when at idle
        """
        pos.select_dispenser(1)
        pos.click("reset")
        pos.click("yes")
        #Checks crind diag to see if reset message is displayed
        if not system.wait_for(lambda: "reset" in pos.read_dispenser_diag()["Status"].lower(), verify = False):
            tc_fail("CRIND did not reset")
        #Wait for crind to return to idle
        if not system.wait_for(lambda: "idle" in pos.read_dispenser_diag()["Status"].lower(), timeout = 120, verify = False):
            tc_fail("CRIND did not return to idle")
        pos.click("back")

    @test
    def call_for_auth_reset(self):
        """
        Verify reset works when pressed when a dispenser is calling for auth
        """
        pos.select_dispenser(1)
        crindsim.lift_handle()
        pos.click("reset")
        pos.click("yes")
        crindsim.lower_handle()
        #Checks crind diag to see if reset message is displayed
        if not system.wait_for(lambda: "reset" in pos.read_dispenser_diag()["Status"].lower(), verify = False):
            tc_fail("CRIND did not reset")
        #Wait for crind to return to idle
        if not system.wait_for(lambda: "idle" in pos.read_dispenser_diag()["Status"].lower(), timeout = 120, verify = False):
            tc_fail("CRIND did not return to idle")
        pos.click("back")

    @test
    def fueling_reset(self):
        """
        Verify reset works when pressed when a dispesner is fueling
        """
        pos.select_dispenser(1)
        crindsim.swipe_card()
        if system.wait_for(lambda: "debit" in crindsim.get_display_text().lower(), verify = False):
            crindsim.press_softkey("no")
        if system.wait_for(lambda: "zip" in crindsim.get_display_text().lower(), verify = False):
            crindsim.press_keypad("2")
            crindsim.press_keypad("7")
            crindsim.press_keypad("4")
            crindsim.press_keypad("1")
            crindsim.press_keypad("0")
            crindsim.press_keypad("enter")
        if system.wait_for(lambda: "carwash" in crindsim.get_display_text().lower(), verify = False):
            crindsim.press_softkey("no")
        crindsim.lift_handle()
        crindsim.open_nozzle()
        pos.click("reset")
        pos.click("yes")
        crindsim.close_nozzle()
        crindsim.lower_handle()
        #Checks crind diag to see if reset message is displayed
        if not system.wait_for(lambda: "reset" in pos.read_dispenser_diag()["Status"].lower(), verify = False):
            tc_fail("CRIND did not reset")
        #Wait for crind to return to idle
        if not system.wait_for(lambda: "idle" in pos.read_dispenser_diag()["Status"].lower(), timeout = 120, verify = False):
            tc_fail("CRIND did not return to idle")
        pos.click("back")

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        crindsim.set_mode("auto")
        pos.close()
