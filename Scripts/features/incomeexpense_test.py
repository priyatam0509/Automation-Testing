"""
    File name: incomeexpense_test.py
    Tags:
    Description: tests the income/expense methods
    Author: 
    Date created: 2019-06-10 10:35:53
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import mws, system, income_expense
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class incomeexpense_test():
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

        self.ie_info = {
            "Account ID":"1234",
            "Description":"Test Account",
            "Eligible for miscellaneous tender transfers.": False
            # "Income": True
            # Income/expense radio buttons currently not functional (6-10-19)
        }

        self.changed_ie_info = {
            "Account ID":"1234",
            "Description":"Test Account (EDIT)",
            "Eligible for miscellaneous tender transfers.": True,
            "Income": True
        }

    @setup
    def setup(self):
        """Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        # if not system.restore_snapshot():
        #     raise Exception
        self.ie = income_expense.IncomeExpenseAccountMaintenance()
        self.ie.navigate_to()

    @test
    def add_incomeexpense(self):
        """Tests whether an income/expense account can be added
        Args: None
        Returns: None
        """
        if not self.ie.add(self.ie_info):
            tc_fail("Could not add income/expense account")

    @test
    def change_incomeexpense(self):
        """Tests whether an income/expense account can be changed
        Args: None
        Returns: None
        """
        if not self.ie.change("Test Account",self.changed_ie_info):
            tc_fail("Could not change income/expense account")

    @test
    def delete_incomeexpense(self):
        """Tests whether an income/expense account can be deleted
        Args: None
        Returns: None
        """
        if not self.ie.delete(self.changed_ie_info["Description"]):
            tc_fail("Could not change income/expense account")

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        # delete pass after you implement.
        pass