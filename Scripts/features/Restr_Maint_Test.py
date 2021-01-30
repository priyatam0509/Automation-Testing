"""
    File name: Restr_Maint_Test.py
    Tags:
    Description: Tests Restriction Maintenance module
    Author: Alex Rudkov
    Date created: 2019-06-11 10:54:20
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import Navi, mws, pos, system
from app.framework.tc_helpers import setup, test, teardown, tc_fail

from app.features import restriction_maint

class Restr_Maint_Test():
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
        """Adds new restriction group. Normal flow
        Args: None
        Returns: None
        """
        restriction_maint.RestrictionMaintenance.navigate_to()
        
        rm_info = {
            "Restriction For Group": "Under 99",
            "Buyer/Seller": {
                "Seller must be at least": True,
                "Minimum Seller Age": "22",
                "Buyer Verify Only": True,
                "Entry of birth date required": True,
                "Permit Verify Only": True,
                "Entry of permit number required": True,
                "Items in this group must be sold separately": True
            },
            "Days Of Week": {
                "Monday Start 1": "10:00 AM",
                "Monday Stop 1": "11:00 PM",
                "Clear All" : True,
                "Monday All Day" : True,
                "Make all days same as dropdown" : "Monday",
                "Make all days same as" : True
            }
        }

        rm = restriction_maint.RestrictionMaintenance()

        if not rm.add(rm_info):
            tc_fail("Could not add restriction group")

    @test
    def test_case_2(self):
        """Changes restriction group. Normal flow
        Args: None
        Returns: None
        """
        restriction_maint.RestrictionMaintenance.navigate_to()
        
        rm_info = {
            "Restriction For Group": "Over 99",
            "Buyer/Seller": {
                "Seller must be at least": True,
                "Minimum Seller Age": "101",
                "Buyer Verify Only": False,
                "Entry of birth date required": True,
                "Permit Verify Only": True,
                "Entry of permit number required": False,
                "Items in this group must be sold separately": False
            },
            "Days Of Week": {
                "Monday Start 1": "10:00 AM",
                "Monday Stop 1": "11:00 PM",
                "Clear All" : True,
                "Monday All Day" : True,
                "Tuesday Start 1": "10:00 AM",
                "Tuesday Stop 1": "11:00 PM",
                "Make all days same as dropdown" : "Tuesday",
                "Make all days same as" : True
            }
        }

        rm = restriction_maint.RestrictionMaintenance()

        if not rm.change("Under 99", rm_info):
            tc_fail("Could not add restriction group")

    @test
    def test_case_3(self):
        """Deletes restriction group. Normal flow
        Args: None
        Returns: None
        """
        restriction_maint.RestrictionMaintenance.navigate_to()
        
        rm = restriction_maint.RestrictionMaintenance()

        if not rm.delete("Over 99"):
            tc_fail("Could not add restriction group")

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        # delete pass after you implement.
        mws.recover()
        pass