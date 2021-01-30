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
from app import Navi, mws, pos, system, store_options, item
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class BasicTest():
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
        """Configure a Menu
        Args: None
        Returns: None
        """

        so = store_options.StoreOptions()
        so_info = {
            "General": {
                "Store Name" : "Automation Land",
                "Address Line 1" : "1234 Address Lane",
                "City" : "Raleigh",
                "State" : "NC",
                "Postal Code" : "27420",
                "Store" : "(954)555-1481",
                "Help Desk" : "(336)555-1234"
                }
            }
        if not so.setup(so_info):
            mws.click_toolbar("Cancel")
            mws.click_toolbar("Yes")
            tc_fail("Failed to set up Store Options.")
        mws.click_toolbar("Save", main=True)


    @test
    def test_case_2(self):
        """Navigate to the POS and Sign On
        Args: None
        Returns: None
        """
        self.log.info("Navigating to POS")
        Navi.navigate_to("POS")
        self.log.info("Signing On")
        if not pos.sign_on():
            tc_fail("Could not sign onto the pos.")

        msg = pos.read_message_box(timeout = .5)
        if msg and "WILL NOT OPEN" in msg:
            pos.click_message_box_key("Ok")

    @test
    def test_case_3(self):
        """Sell an Item
        Args: None
        Returns: None
        """
        pos.enter_plu("003")
        pos.click("PLU")
        if not pos.pay():
            tc_fail("Could not pay out the transaction.")

    @test
    def test_case_4(self):
        """Change an Item and Sell it
        Args: None
        Returns: None
        """
        Navi.navigate_to("Item")
        item = item.Item()
        item_info = {
            "003":{
                "General": {
                    "This item sells for" : True,
                    "per unit" : "1000"
                    }
                }
            }
        for plu in item_info:
            if not item.change(plu, item_info[plu]):
                mws.click_toolbar("Cancel")
                mws.click_toolbar("Exit")
                tc_fail("Failed to change Item.")

        Navi.navigate_to("POS")
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
        # pass
        if not system.restore_snapshot():
            raise Exception