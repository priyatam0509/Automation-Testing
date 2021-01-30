"""
    File name: Tank_Inventory_Test.py
    Tags:
    Description: 
    Author: 
    Date created: 2019-07-01 08:46:18
    Date last modified: 
    Python Version: 3.7
"""

import logging, time
from app import Navi, mws, pos, system, tank_inventory
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class Tank_Inventory_Test():
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
        # if not system.restore_snapshot():
        #     raise Exception

    @test
    def test_case_1(self):
        """<Description here>
        Args: None
        Returns: None
        """
        ti = tank_inventory.TankInventory()

        params = {
            "Entry" : ['1', 'REGULAR'], # However many parameters that can serve as selection criteria,
            "Date" : "07/01/2019",
            "Operator" : "Area Manager",
            "Time": "8:56:07 AM",
            "Adjusted Level": "1000",
            "Reason for Adjustment": "Calibration"
        }

        self.log.info("Trying to adjust the tank inventory with valid config")
        if not ti.adjust(params):
            tc_fail("Failed to adjust the tank inventory")
        self.log.info("Successfully adjusted")

        # Check
        time.sleep(2)
        ti.navigate_to()

        mws.select("Tanks", params["Entry"])
        adj_manifold_lvl = mws.get_text("Adjusted Manifold Level")
        if adj_manifold_lvl != params["Adjusted Level"]:
            tc_fail(f"The field 'Adjusted Level' was set successfully, but upon check had value '{adj_manifold_lvl}' when '{params['Adjusted Level']}' was expected")
        mws.recover()

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        # delete pass after you implement.
        pass