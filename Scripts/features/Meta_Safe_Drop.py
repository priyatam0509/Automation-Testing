"""
    File name: Meta_Safe_Drop.py
    Tags:
    Description: The meta test to verify the functionality of the safe_drop.py module
    Author: 
    Date created: 2019-06-21 14:02:26
    Date last modified: 2020-01-16 14:16:10
    Modified By: Conor McWain
    Python Version: 3.7
"""

import logging
from app import mws, system, safe_drop
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class Meta_Safe_Drop():
    """
    Test class that provides an interface for testing.
    """

    def __init__(self):
        """
        Initializes the Template class.
        """
        self.log = logging.getLogger()
        self.safe = safe_drop.SafeDrop()

    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        """
        self.safe.navigate_to()

    @test
    def configure_loan(self):
        """
        Verifies that tenders can be added to the Tenders list.
        """
        self.safe_drop_info = {
            "Tender Button 1": ["1000","5000","10000"],
            "Tender Button 2": "2500",
            "Tender Button 3": ["500"]
        }
        self.safe.configure("70", "Main Safe", "25", self.safe_drop_info, False)

    @test
    def change_tender(self):
        """
        Verifies a tender in the Tenders list can be changed.
        """
        if not self.safe.change_amount(("Cash","50.00"), "2500"):
            tc_fail("Failed while changing amount.")

    @test
    def delete_tender(self):
        """
        Verifies tenders can be deleted from the Tenders list.
        """
        if not self.safe.delete_tender(("Cash","25.00")):
            tc_fail("Failed while deleting tender.")
        mws.click_toolbar("Save")

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        pass