"""
    File name: CarWash_POS.py
    Tags:
    Description: 
    Author: Gene Todd
    Date created: 2020-05-27 14:22:04
    Date last modified: 
    Python Version: 3.7
"""

# Car wash PLU
cw_plu = 1234

import logging
from app import Navi, mws, pos, system
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class CarWash_POS():
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
        #if not system.restore_snapshot():
        #    self.log.debug("No snapshot to restore, if this is not expected please contact automation team")
        pos.connect()
        pos.sign_on()

    @test
    def test_noBaseItem(self):
        """
        Confirm that car wash does not show the base item
        """
        self.log.info("Getting car wash options preseted")
        pos.click_speed_key("Car Wash")
        options = pos.read_list_items()
        if len(options) == 4:
            self.log.info("Correct number of packages found")
        else:
            tc_fail(f"Unexpected number of packages: [{len(options)}] - {options}")
        pos.click("Cancel")
        
    @test
    def test_limit1CarWash(self):
        """
        Confirm that only 1 carwash package can be added to a transaction
        """
        self.log.info("Adding first car wash")
        pos.click_speed_key("Car Wash")
        pos.click("Enter")
        self.log.info("Adding second car wash")
        pos.click_speed_key("Car Wash")
        
        #Confirming error message
        if "one carwash" in pos.read_message_box():
            self.log.info("Desired message found")
        else:
            tc_fail("Did not receieve desired warning message for carwash limit")
            
        pos.click("Ok")
        pos.pay()
        
    @test
    def test_flatTax(self):
        """
        Confirm we get the correct price for carwashes with flat taxes included
        """
        self.log.info("Adding Car wash package 1")
        pos.click_speed_key("Car Wash")
        options = pos.read_list_items()
        pos.select_list_item(options[0])
        pos.click("Enter")
        
        self.log.info("Confirming price")
        total = pos.read_balance()['Total']
        if total == "$2.50":
            self.log.info("Correct total found")
        else:
            tc_fail(f"Incorrect total found: [{total}]")
            
        pos.pay()
            
    @test
    def test_taxIncluded(self):
        """
        Confirm we get the correct price for carwashes with taxes included in the price
        """
        self.log.info("Adding Car wash package 2")
        pos.click_speed_key("Car Wash")
        options = pos.read_list_items()
        pos.select_list_item(options[1])
        pos.click("Enter")
        
        self.log.info("Confirming price")
        total = pos.read_balance()['Total']
        if total == "$4.00":
            self.log.info("Correct total found")
        else:
            tc_fail(f"Incorrect total found: [{total}]")
            
        pos.pay()
            
    @test
    def test_taxExcluded(self):
        """
        Confirm we get the correct price for carwashes with taxes not included in the price
        """
        self.log.info("Adding Car wash package 4")
        pos.click_speed_key("Car Wash")
        options = pos.read_list_items()
        pos.select_list_item(options[3])
        pos.click("Enter")
        
        self.log.info("Confirming price")
        total = pos.read_balance()['Total']
        if total == "$8.25":
            self.log.info("Correct total found")
        else:
            tc_fail(f"Incorrect total found: [{total}]")
            
        pos.pay()

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        pos.close()
