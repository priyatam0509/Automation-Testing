"""
    File name: Shift_Close_Test.py
    Tags:
    Description: Tests the shift_close.ShiftClose module
    Author: Alex Rudkov
    Date created: 2019-06-07 15:07:45
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import Navi, mws, pos, system, shift_close
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class Shift_Close_Test():
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

        # Prerequisite
        # period_maint.PeriodMaintenance.navigate_to()
        # pm_info = {
        #     "General" : {
        #         "Variable Shift (Shift Close)" : True
        #     }
        # }

        # pm = period_maint.PeriodMaintenance()
        # pm.setup(pm_info)

        # if not system.restore_snapshot():
        #     raise Exception

    @test
    def test_case_1(self):
        """Tests the report generation
        Args: None
        Returns: None
        """
        shift_close.ShiftClose.navigate_to()
        sc = shift_close.ShiftClose()
        if not sc.begin_shift_change():
            tc_fail("Could not generate report")

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        # delete pass after you implement.
        pass