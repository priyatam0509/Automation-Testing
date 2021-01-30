"""
    File name: Meta_Till_Balance.py
    Tags:
    Description: The meta test to verify the functionality of the till_balance.py module
    Author: 
    Date created: 2019-06-28 09:41:19
    Date last modified: 2020-01-16 14:19:10
    Modified By: Conor McWain
    Python Version: 3.7
"""

import logging, time
from app import Navi, mws, system, till_balance
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class Meta_Till_Balance():
    """
    Test class that provides an interface for testing.
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
        self.tb = till_balance.TillBalance()

    @test
    def configure_till_balance(self):
        """
        Verifies the fields in the Till Balance feature module can be set. Requires a till to have been opened.
        """
        till_balance_info = {
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
        if not self.tb.configure("70", till_balance_info, save = False):
            tc_fail("Failed while configuring till balance.")

    @test
    def change_amount_cash(self):
        """
        Verifies the amounts of a Cash denomination can be changed.
        """
        new_till_balance_info = {
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
        if not self.tb.configure("70", new_till_balance_info, save = False):
            tc_fail("Failed while changing cash denomination amounts.")

    @test
    def change_amount_TB2(self):
        """
        Verifies the amounts of a Tender Button tender can be changed.
        """
        new_till_balance_info = {
            "Tender Button 2": [("10.00", "15.00")],
            "Tender Button 3": [("20.00","25.00")],
            "Tender Button 17":[("10.00","15.00")] # Changes first value to second value
        }
        
        # Saves and exits configuration
        if not self.tb.configure("70", new_till_balance_info, save = True):
            tc_fail("Failed while changing non-cash amounts.")
    

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        pass