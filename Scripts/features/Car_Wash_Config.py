"""
    File name: Car_Wash_Config.py
    Tags:
    Description: 
    Author: 
    Date created: 2019-05-01 13:52:18
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import Navi, mws, pos, system, carwash
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class Car_Wash_Config():
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
        """Add a kiosk and carwash package
        Args: None
        Returns: None
        """
        cw = carwash.CarWashMaintenance()
        cw_info = {
            "Site":{
                "Type of Car Wash":"Unitec Ryko Emulation",
                "Car Wash PLU":"1234",
                "Rewash PLU":"5678",
                "Receipt Footer 1":"Footer #1"
            },
            "Packages":{
                "Carwash 1":{
                    "Package Name":"Carwash 1",
                    "Total Price":"5.00"
                }
            }
        }
        self.log.info("Editing Car Wash Maintenance")
        if not cw.add(cw_info):
            mws.click_toolbar("Cancel")
            mws.click_toolbar("No")
            tc_fail("Failed to edit Car Wash Maintenance.")
        self.log.info("TC Passed")

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        if not system.restore_snapshot():
            raise Exception