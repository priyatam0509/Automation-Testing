"""
    File name: scanner_test.py
    Tags:
    Description: This script tests the ability to change scanners associated
                    with an express lane site.  This test automates M-90696.
    Author: Christopher Haynes
    Date created: 2019-09-13 08:29:20
    Date last modified: 
    Python Version: 3.7
"""

import logging, time
from app import Navi, mws, system, checkout, register_setup, item
from app.simulators.ip_scanner import IPScanner
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from Scripts.features import EL_PaymentTest

class scanner_test():
    """
    Description: Testing the ability to configure a TCP/IP or serial scanner.
    """
    
    def __init__(self):
        """Initializes the Template class.
        Args: None
        Returns: None
        """
        # The logging object. 
        # Example: self.log.info(f"Current value of var: {my_var}")
        self.log = logging.getLogger()
        self.scanner = IPScanner(ip = "10.5.48.2")

    @setup
    def setup(self):
        """Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        cfg = { "General": {
                            "PLU/UPC": "1",
                            "Description": "Generic Item",
                            "Department": "Dept 1",
                            "per unit": "500" },
                        "Scan Codes": {
                            "Add": ["8901860633532"],
                            "Expand UPCE": True },       
                        "Options": {
                            "Food Stampable": False,
                            "Quantity Allowed": True,
                            "Quantity Required": True,
                            "Return Price": "500" }
                        }
        item_obj = item.Item()
        item_obj.add(cfg, overwrite=True)        
        mws.click_toolbar("Exit", main = True)

    @test
    def ip_scanner_1(self):
        """Changes the express lane to use an IP based scanner
        Args: None
        Returns: None
        """
        
        # Tests that the changes were successful.
        self.log.info("Testing scanner changes.")
        balance = 0
        if checkout.connect():
            time.sleep(3)
            checkout.click_welcome_key("Start")
            time.sleep(3)
            self.scanner.scan("8901860633532")
            time.sleep(5)
            balance = checkout.read_balance()
            time.sleep(5)
            checkout.pay_card()
            checkout.close()
        else:
            tc_fail("Couldn't connect to Express Lane.")
            
        if balance['Total'] != "$5.00 ":
            tc_fail("The transaction balance was incorrect.")

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """

        # Suspend Transaction if any test case is fail due to payment issue
        EL_PaymentTest.suspend_transaction()
