"""
    File name: acc_opt_test.py
    Tags:
    Description: 
    Author: 
    Date created: 2019-06-19 15:42:52
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import mws, system, accounting_options
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class acc_opt_test():
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
        if not system.restore_snapshot():
            raise Exception

        self.ao = accounting_options.AccountingOptions()

    @test
    def configure_acc_opt(self):
        """Tests whether the Accounting Options module can be correctly configured.
        Args: None
        Returns: None
        """
        self.ao.navigate_to()
        acc_opt_info = {
            "General":{
                "Allow operator to see system totals when balancing their till": True,
                "Allow preview of previous counts when reconciling tills": True,
                "The maximum number of times a till can be counted in Manager Workstation": "25"
            },
            "Tender Options":{
                "Cash": "1.00",
                "Check": "2.00",
                "Credit": "3.00",
                "Debit": "4.00",
                "Other": "5.00",
                "UCC": "6.00",
                "EBT Food": "7.00",
                "EBT Cash": "8.00",
                "Added Tender 1": "9.00",
            },
            "Safe Options":{
                "Main Safe":{
                    "Safe ID": "1",
                    "Safe Name": "Main Safe",
                    "Main Safe": True,
                },
                "Other Safe":{
                    "Safe ID": "2",
                    "Safe Name": "Other Safe"
                }
            }
        }
        if not self.ao.configure(acc_opt_info):
            tc_fail("Configuring failed...")
    
    @test
    def add_safe(self):
        """Tests whether a new safe can be added.
        Args: None
        Returns: None
        """
        self.ao.navigate_to()
        if not self.ao.configure_safe("new_safe", "3", safe_name = "Test Safe"):
            tc_fail("Adding safe failed.")
    
    @test
    def change_safe(self):
        """Tests whether a safe can be changed.
        Args: None
        Returns: None
        """
        self.ao.navigate_to()
        if not self.ao.configure_safe("Test Safe", "25", "New Safe"):
            tc_fail("Changing safe failed.")
            
    @test
    def delete_safe(self):
        """Tests whether a safe can be deleted and replaced with a new main safe.
        Args: None
        Returns: None
        """
        self.ao.navigate_to()
        if not self.ao.delete_safe(["Main Safe","Other Safe"],"New Safe"):
            tc_fail("Deleting safes failed.")


    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        # delete pass after you implement.
        pass