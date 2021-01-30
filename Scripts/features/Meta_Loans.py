"""
    File name: Meta_Loans.py
    Tags:
    Description: The meta test to verify the functionality of the loans.py module
    Author: 
    Date created: 2019-06-20 15:50:04
    Date last modified: 2020-01-16 14:04:10
    Modified By: Conor McWain
    Python Version: 3.7
"""

import logging
from app import mws, system, loans
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class Meta_Loans():
    """
    Description: Test class that provides an interface for testing.
    """

    def __init__(self):
        """
        Initializes the Template class.
        """
        self.log = logging.getLogger()
        
    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        """
        self.loan = loans.Loans()

    @test
    def configure_loan(self):
        """
        Verifies that tenders can be added to the Tenders list.
        """
        self.loans_info = {
            "Tender Button 1": ["1000","5000","10000"],
            "Tender Button 2": "2500",
            "Tender Button 3": ["500"]
        }
        if not self.loan.configure("70", "Main Safe", self.loans_info, False):
            tc_fail("Failed during configuration.")

    @test
    def change_tender(self):
        """
        Verifies a tender in the Tenders list can be changed.
        """
        if not self.loan.change_amount(("Cash","50.00"), "2500"):
            tc_fail("Failed while changing amount.")

    @test
    def delete_tender(self):
        """
        Verifies tenders can be deleted from the Tenders list.
        """
        if not self.loan.delete_tender(("Cash","25.00")):
            tc_fail("Failed while deleting tender.")
        mws.click("Save")

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        pass