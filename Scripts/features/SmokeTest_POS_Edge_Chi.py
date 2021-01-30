"""
    File name: SmokeTest_POS_Edge_Chi.py
    Tags:
    Description: Basic POS Transaction tests. Written as a basic smoke test against Edge
    Author: Conor McWain
    Date created: 2019-09-10
    Date last modified: 
    Python Version: 3.7
"""

import logging, time

from app import Navi, pos, store_close, crindsim
from app.simulators import ip_scanner
from app.framework.tc_helpers import setup, test, teardown, tc_fail

# region TODO Notes
'''
Test Cases to add:
    Add a test for Contactless
    Add a test for EBT Food

Remove the time.sleep() calls once the functions have been enhanced
'''
# endregion


class SmokeTest_POS_Edge_Chi():
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
        # Loopback as workaround for device id
        pos.connect()
        #Need something to wait for the POS to load
        time.sleep(10)

    @test
    def sign_on_POS(self):
        """
        Sign on the the POS
        """
        time.sleep(2)
        pos.sign_on(till_amount = '1.00')
        #TODO: Remove this sleep when we get the ability to check the state of the PINPad Sim
        self.log.debug("Waiting for the PINPad Sim to finish its download")
        time.sleep(200)

    @test
    def basic_trans(self):
        """
        Sell an item
        """
        time.sleep(2)
        pos.add_item("57355", method = "PLU")
        time.sleep(2)
        pos.pay()

    @test
    def scan_trans(self):
        """
        Sell an item
        """
        time.sleep(2)
        if not pos.scan_item("893594002075"):
            tc_fail("Failed to scan the item")
        time.sleep(2)
        pos.pay()

    @test
    def basic_return(self):
        """
        Return an item
        """
        time.sleep(2)
        pos.click_function_key("REFUND")
        time.sleep(2)
        pos.add_item("57355", method = "PLU")
        time.sleep(2)
        pos.pay()

    @test
    def credit_card(self):
        """
        Tender a sale with a credit card
        """
        time.sleep(2)
        pos.add_item("57355", method = "PLU")
        time.sleep(2)
        pos.pay_card()

    @test
    def debit_card(self):
        """
        Tender a sale with a debit card
        """
        time.sleep(2)
        pos.add_item("57355", method = "PLU")
        time.sleep(2)
        pos.pay_card(card_name='Debit')

    @test
    def dispenser_trans(self):
        """
        Tender a sale with a dispenser
        """
        crindsim.set_sales_target()
        crindsim.set_mode("auto")
        pos.wait_disp_ready()
        pos.add_fuel('$5.00')
        pos.pay()
        pos.wait_for_fuel(timeout=120)

    @test
    def store_close(self):
        """
        Perform a Store Close
        """
        pos.close_till()
        pos.close()
        self.log.info("Navigating to MWS")
        Navi.navigate_to("MWS")
        store_close.StoreClose.navigate_to()
        sc = store_close.StoreClose()
        if not sc.begin_store_close():
            tc_fail("Could not generate report")

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        pass