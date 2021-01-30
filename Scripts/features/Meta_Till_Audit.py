"""
    File name: Meta_Till_Audit.py
    Tags:
    Description: The meta test to verify the functionality of the till_audit.py module
    Author: 
    Date created: 2019-07-01 15:15:14
    Date last modified: 2020-01-16 14:22:10
    Modified By: Conor McWain
    Python Version: 3.7
"""

import logging, time
from app import Navi, mws, system, till_audit
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class Meta_Till_Audit():
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
        self.ta = till_audit.TillAudit()
        #default till to edit to be the first till in the list
        self.till_id = mws.get_value("Tills")[0][0]

    @test
    def configure_till_audit(self):
        """
        Verifies the fields in the Till Audit feature module can be set. Requires an active till.
        """
        till_audit_info = {
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
            "Tender Button 3": ["10.00", "20.00"]
        }

        if not self.ta.configure(self.till_id, till_audit_info):
            tc_fail("Failed while configuring till amounts.")

    @test
    def change_amount_cash(self):
        """
        Verifies the amounts of a Cash denomination can be changed.
        """
        new_till_audit_info = {
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

        if not self.ta.configure(self.till_id, new_till_audit_info):
            tc_fail("Failed while changing cash denomination amounts.")

    @test
    def change_amount_TB(self):
        """
        Verifies the amounts of a Tender Button tender can be changed.
        """
        new_till_audit_info = {
            "Tender Button 17": ["10.00", ("10.00","15.00")] 
            # adds a new amount to TB17, then immediately changes it
        }

        if not self.ta.configure(self.till_id, new_till_audit_info):
            tc_fail("Failed while changing non-cash amounts.")
    

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        pass