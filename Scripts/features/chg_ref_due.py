"""
    File name: chg_ref_due.py
    Tags:
    Description: Do not show Chg/Ref Due button if cash acceptors have not been configured.
    Author: Kevin Walker
    Date created: 2020-07-06 11:13:09
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import Navi, mws, pos, system, forecourt_installation
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class chg_ref_due():
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
        pos.connect()
        pos.sign_on()

    @test
    def cash_acceptor_not_configured(self):
        """
        Verify the Chg/Ref Due button is not visible when cash acceptor is not configured
        """
        if pos.is_element_present(pos.controls['function keys']['chg/ref due']):
            tc_fail("Chg/Ref Due button found in Main Menu, should not be there")
        pos.close()

    @test
    def cash_acceptor_configured(self):
        """
        Verify Chg/Ref Due button is visible when cash acceptors are configured
        """
        #Set cash acceptor configuration to true
        fc = forecourt_installation.ForecourtInstallation()
        mws.click("Set Up")
        fc.change(item = "1", tab = "Dispensers", config = {"Bill Acceptor": True})
        mws.click_toolbar("Save")
        mws.click_toolbar("Save")
        system.wait_for(mws.get_top_bar_text, None)
        pos.connect()
        pos.sign_on()
        #Reloads POS screens to get button refresh
        pos.click("tools")
        pos.click("back")
        if not pos.is_element_present(pos.controls['function keys']['chg/ref due']):
            tc_fail("Chg/Ref Due button not found in Main Menu")

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        pos.close()
        fc = forecourt_installation.ForecourtInstallation()
        mws.click("Set Up")
        fc.change(item = "1", tab = "Dispensers", config = {"Bill Acceptor": False})
        mws.click_toolbar("Save")
        mws.click_toolbar("Save")
        system.wait_for(mws.get_top_bar_text, None)
