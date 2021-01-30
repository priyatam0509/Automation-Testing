"""
    File name: linked_items.py
    Tags:
    Description: 
    Author: 
    Date created: 2019-11-26 14:14:56
    Date last modified: 
    Python Version: 3.7
"""

import logging, time
from app import Navi, mws, pos, system, item, checkout
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class linked_items():
    """
    Description: Test class that provides an interface for testing.
    """

    def __init__(self):
        """
        Description:
                Initializes the linked_items class.
        Args:
                None
        Returns:
                None
        """
        # The logging object.
        # Example: self.log.info(f"Current value of var: {my_var}")
        self.log = logging.getLogger()
        self.item1 = 1001
        self.item2 = 1002



    @setup
    def setup(self):
        """
        Description:
                Performs any initialization that is not default.
        Args:
                None
        Returns:
                None
        """
        self.log.info("Setting up linked items.")
        items = item.Item()
        new_item = {
                    "General": {
                        "PLU/UPC": "{}".format(self.item2),
                        "Description": "Item {}".format(self.item2),
                        "Department": "Dept 1",
                        "Item Type": "Regular Item",
                        "Receipt Desc": "Item {}".format(self.item2),
                        "per unit": "200"
                                },
                    "Options":  {
                        "Return Price": "200"
                                }
                   }
        items.add(new_item, overwrite = True)
        new_item = {
                        "General": {
                            "PLU/UPC": "{}".format(self.item1),
                            "Description": "Item {}".format(self.item1),
                            "Department": "Dept 1",
                            "Item Type": "Regular Item",
                            "Receipt Desc": "Item {}".format(self.item1),
                            "per unit": "100"
                        },
                        "Linked Items": {
                            "Add": ["{}".format(self.item2)]
                        },
                        "Options": {
                            "Return Price": "100"
                        }
                   }
        items.add(new_item, overwrite = True)
        mws.click_toolbar("Exit", main = True)



    @test
    def check_linked_items_1(self):
        """
        Description:
                Checks for the function of linked items in the Express Lane.  This automates M-90730.
        Args: 
                None
        Returns: 
                None
        """
        self.log.info("Testing linked items.")
        checkout.connect()
        #waiting for express lane to come up
        while checkout._is_element_present("//div[@id='disabled_screen']"):
            time.sleep(1)
        #ensuring the welcome screen is not in the way
        if checkout._is_element_present("//div[@id = 'welcomescreen']"):
            checkout.click_welcome_key("Start")
        checkout.enter_plu("{}".format(self.item1))
        balance = checkout.read_balance()
        time.sleep(1) #This seems to be needed to give the journal time to populate
        self.log.info("Total Balance: {}".format(balance))
        if balance['Total'] != "$3.00 ":
            tc_fail("The balance is not correct.")
        checkout.pay_card()
        checkout.close()

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """

        if not system.restore_snapshot():
            self.log.debug("No snapshot to restore, if this is not expected please contact automation team")