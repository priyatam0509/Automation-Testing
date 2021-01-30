"""
    File name: BasicTest.py
    Tags:
    Description: 
    Author: 
    Date created: 2019-04-26 13:59:03
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import Navi, mws, pos, system
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class BasicTest2():
    """
    Description: Test class that provides an interface for testing.
    """

    def __init__(self):
        """Initializes the Template class.
        Args: None
        Returns: None
        """
        # The logging object. 
        # Example: self.log.info(f"Current value of var: {my_var}")
        self.log = logging.getLogger()

    @setup
    def setup(self):
        """Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        # delete pass after you implement.
        pass

    @test
    def test_case_1(self):
        """Sell an Item
        Args: None
        Returns: None
        """
        self.log.info("Navigating to POS")
        Navi.navigate_to("POS")
        self.log.info("Signing On")
        if not pos.sign_on():
            tc_fail("Could not sign onto the pos.")

        msg = pos.read_message_box(timeout = .5, log=False, verify=False)
        if "WILL NOT OPEN" in msg:
            pos.click_message_box_key("Ok")

        pos.enter_plu("003")
        pos.click("PLU")
        if not pos.pay():
            tc_fail("Could not pay out the transaction.")

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        pass
        # if not system.restore_snapshot():
        #     raise Exception