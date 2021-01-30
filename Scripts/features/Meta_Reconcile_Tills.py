"""
    File name: Meta_Reconcile_Tills.py
    Tags:
    Description: The meta test to verify the functionality of the recondile_tills.py module
    Author: 
    Date created: 2019-07-01 16:30:03
    Date last modified: 2020-01-16 14:13:10
    Modified By: Conor McWain
    Python Version: 3.7
"""

import logging, time
from app import Navi, mws, system, reconcile_tills
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class Meta_Reconcile_Tills():
    """
    Test class that provides an interface for testing.
    """

    def __init__(self):
        """
        Initializes the Template class.
        """
        # The logging object. 
        # Example: self.log.info(f"Current value of var: {my_var}")
        self.log = logging.getLogger()

    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        """
        self.rt = reconcile_tills.ReconcileTills()
        #TODO: Set the till id dynamically
        self.till_id = "73"
        
    @test
    def change_safe_amount(self):
        """
        Verifies the amount of a safe drop can be changed.
        """
        if not self.rt.reconcile_safe_drop(self.till_id, "123", "50"):
            tc_fail("Failed while changing safe drop amount.")

    @test
    def configure_reconcile_tills(self):
        """
        Verifies the fields in the Reconcile Tills feature module can be set.
        Requires a till to have been opened and closed, and the till to have been 
        balanced.
        """
        reconcile_tills_info = {
            "Tender Button 1": {
                "Coins": {
                    "Nickels": "10",
                    "Quarter": "10"
                },
                "Bills": {
                    "One Dollar Bill": "10",
                    "Five Dollar Bill": "10",
                    "Twenty Dollar Bill": "10"
                }
            },
            "Tender Button 2": ["10.00", "20.00"],
            "Tender Button 3": ["10.00", "20.00"],
            "Tender Button 17": ["10.00"]
        }

        # Does not exit configuration
        if not self.rt.configure(self.till_id, reconcile_tills_info, save = False):
            tc_fail("Failed while configuring Reconcile Tills module.")

    @test
    def change_amount_cash(self):
        """
        Verifies the amounts of a Cash denomination can be changed.
        """
        new_reconcile_tills_info = {
            "Tender Button 1": {
                "Coins": {
                    "Nickels": "15",
                    "Quarter": "15"
                },
                "Bills": {
                    "One Dollar Bill": "15",
                    "Five Dollar Bill": "15",
                    "Twenty Dollar Bill": "15"
                }
            }
        }

        # Does not exit configuration
        if not self.rt.configure(self.till_id, new_reconcile_tills_info, save = False):
            tc_fail("Failed while changing cash denomination amounts.")

    @test
    def change_amount_TB(self):
        """
        Verifies the amounts of a Tender Button tender can be changed.
        """
        new_reconcile_tills_info = {
            "Tender Button 2": [("10.00", "15.00")],
            "Tender Button 3": [("20.00","25.00")],
            "Tender Button 17":[("10.00","15.00")]
        }
        
        # Saves and exits configuration
        if not self.rt.configure(self.till_id, new_reconcile_tills_info, save = True):
            tc_fail("Failed while changing non-cash amounts.")
    
    
    
    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        pass