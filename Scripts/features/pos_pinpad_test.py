"""
    File name: pos_pinpad_test.py
    Tags:
    Description: Simple tests for PINpad related functions in the POS module.
    Author: Cassidy Garner
    Date created: 2019-05-07 17:05:49
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import mws, pos, system, Navi, register
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class pos_pinpad_test():
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
        Navi.navigate_to("POS")
        self.pos.sign_on()

    @test
    def pay_card_default(self):
        """Pay with basic Visa card
        Args: None
        Returns: None
        """
        self.pos.add_item("Generic Item", method="Speedkey", price="100")
        self.pos.pay_card()

    @test
    def manual_entry_default(self):
        """Pay with manual card entry
        Args: None
        Returns: None
        """
        self.pos.add_item("Generic Item", method="Speedkey", price="100")
        self.pos.manual_entry()

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        pass