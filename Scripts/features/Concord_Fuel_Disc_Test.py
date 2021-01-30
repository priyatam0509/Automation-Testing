"""
    File name: Concord_Fuel_Disc_Test.py
    Tags: Concord, Valero, Phillips66
    Description: Tests the Fuel Discount Configuration
    Author: Conor McWain
    Date created: 2019-06-28 14:45:56
    Date last modified: 2019-07-19 14:45:56
    Python Version: 3.7
"""

import logging
from app import Navi, mws, pos, system
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app import fuel_disc_config

class Concord_Fuel_Disc_Test():
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
        pass

    @test
    def add_disc(self):
        """Change a Fuel Discount Configuration
        Args: None
        Returns: None
        """
        fd_info = {
            "Debit": "NONE",
            "Visa": "NONE"
            }
        fd = fuel_disc_config.FuelDiscountConfiguration()
        if not fd.change(fd_info):
            mws.recover()
            tc_fail("Could not set the configuration")

    @test
    def change_disc(self):
        """Change a Fuel Discount Configuration
        Args: None
        Returns: None
        """
        fd_info = {
            "Debit": "NONE",
            "Visa": "NONE"
            }
        fd = fuel_disc_config.FuelDiscountConfiguration()
        if not fd.change(fd_info):
            mws.recover()
            tc_fail("Could not set the configuration")

    @test
    def wrong_disc(self):
        """Change a Fuel Discount Configuration with an incorrect discount
        Args: None
        Returns: None
        """
        fd_info = {
            "Debit": "Fake Group"
            }
        fd = fuel_disc_config.FuelDiscountConfiguration()
        if fd.change(fd_info):
            tc_fail("Was able to set the configuration")
        else:
            mws.recover()

    @test
    def wrong_card(self):
        """Change a Fuel Discount Configuration with an incorrect card
        Args: None
        Returns: None
        """
        fd_info = {
            "Golf": "NONE"
            }
        fd = fuel_disc_config.FuelDiscountConfiguration()
        if fd.change(fd_info):
            tc_fail("Was able to set the configuration")
        else:
            mws.recover()

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        # delete pass after you implement.
        pass