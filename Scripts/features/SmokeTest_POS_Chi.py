"""
    File name: SmokeTest_POS_Chi.py
    Tags:
    Description: Basic POS Transaction tests. Written as a basic smoke test against Passport
    Author: Conor McWain
    Date created: 2019-09-10
    Date last modified: 
    Python Version: 3.7
"""

import logging, time

from app import Navi, pos, store_close, crindsim
from app.framework.tc_helpers import setup, test, teardown, tc_fail

# region TODO Notes
'''
Test Cases to add:
    Add a test for Contactless
    Add a test for EBT Food
    Add a test for Scanning an Item

Verify the download has completed before starting the Dispenser TC
Verify the state of the PINPad sim (Remove the hardcoded sleep after sign on)
'''
# endregion


class SmokeTest_POS_Chi():
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
        # delete pass after you implement.
        pass

    @test
    def sign_on_POS(self):
        """
        Sign on the the POS
        """
        self.log.info("Navigating to POS")
        Navi.navigate_to("POS")
        self.log.info("Signing On")
        pos.sign_on()
        #TODO: Change this when we have a State system in PINPad Sim
        self.log.debug("Taking a break so the PINPad Sim can finish its download before we hit the Credit Tans")
        time.sleep(120)

    @test
    def basic_trans(self):
        """
        Sell an item
        """
        self.log.info("Navigating to POS")
        Navi.navigate_to("POS")
        pos.add_item("57355", method = "PLU")
        pos.pay()

    @test
    def read_receipt(self):
        """
        Check the receipt for the previously sold item
        """
        pos.check_receipt_for("Smoke Test")

    @test
    def carwash(self):
        """
        Sell a car wash
        """
        self.log.info("Navigating to POS")
        Navi.navigate_to("POS")
        pos.add_item("1234",method="plu",qualifier="CARWASH 1")
        pos.pay()

    @test
    def basic_return(self):
        """
        Return an item
        """
        self.log.info("Navigating to POS")
        Navi.navigate_to("POS")
        pos.click_function_key("REFUND")
        pos.add_item("57355", method = "PLU")
        pos.pay()

    @test
    def credit_card(self):
        """
        Tender a sale with a credit card
        """
        self.log.info("Navigating to POS")
        Navi.navigate_to("POS")
        pos.add_item("57355", method = "PLU")
        pos.pay_card()

    @test
    def debit_card(self):
        """
        Tender a sale with a debit card
        """
        self.log.info("Navigating to POS")
        Navi.navigate_to("POS")
        pos.add_item("57355", method = "PLU")
        pos.pay_card(card_name='Debit')

    @test
    def dispenser_trans(self):
        """
        Tender a sale with a dispenser
        """
        self.log.info("Navigating to POS")
        Navi.navigate_to("POS")
        crindsim.set_sales_target()
        crindsim.set_mode("auto")
        pos.wait_disp_ready()
        pos.add_fuel('$10.00')
        pos.pay()
        pos.wait_for_fuel(timeout=120)

    @test
    def dispenser_receipt(self):
        """
        Check the receipt for the previously sold item
        """
        pos.check_receipt_for("REGULAR", dispenser = 1)
        pos.check_receipt_for("REGULAR")

    @test
    def store_close(self):
        """
        Perform a Store Close
        """
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