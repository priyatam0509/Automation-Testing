"""
    File name: GenericItemSale.py
    Tags: CashSale, Core, POS 
    Description: Performs a generic item cash sale.
    Author: John Smith
    Date created: 01/24/2019
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import mws, pos
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class GenericItemSale():
    """
    Test class that that provides an interface for testing.
    """
    def __init__(self):
        """Initializes the Template class.
        Params: None
        Returns: None
        """
        # The logging object. 
        # Example: self.log.info(f"Current value of var: {my_var}")
        self.log = logging.getLogger()

        # The main MWS object 
        self.mws = mws

        # The main POS object
        self.pos = pos

    @setup
    def setup(self):
        """Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        self.navigate_to_pos()

    @test
    def test_case_1(self):
        """Perform a cash sale with a Generic Item.
        Args: None
        Returns: None
        """
        # do nothing..
        self.log.info("Hi from tc1 in GenericItemSale.py!")
        return
        #self.pos.click_speedkey('Generic Item')
        #self.pos.click_function_key('Pay') #self.pos.pay()
        #self.pos.click_tender_key('$0.01')

    @test
    def test_case_2(self):
        """Simulates a failed test case.
        Args: None
        Returns: None
        """
        tc_fail("This is a simulated failure reason")

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends. 
        Args: None
        Returns: None
        """
        self.pos.navigate_to(where='MWS')
        self.mws.sign_off()

    def navigate_to_pos(self):
        """Helper method that will help you with your Test Case(s). This one signs 
        on the MWS and moves to the POS
        Args: None
        Returns: None
        """
        self.mws.sign_on()
        self.mws.navigate_to(where='POS')