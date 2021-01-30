"""
    File name: tender_test.py
    Tags:
    Description: 
    Author: 
    Date created: 2019-06-14 14:23:45
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import mws, system, tender
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class tender_test():
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

        self.tm = tender.TenderMaintenance()

    @test
    def tender_configure(self):
        """Tests whether a new tender type can be added.
        Args: None
        Returns: None
        """
        tender_info = {
            "Tender Code": "1234",
            "Tender Description": "Test US Dollars",
            "General": {
                "Tender group this tender belongs to": "Cash",
                "Safe drops allowed for this tender": True,
                "Print tax invoice text on Receipt": True,
                "Receipt Description": "Test Desc",
                "Tender Button Description": "Test Desc",
                "NACS Tender Code": "generic"
            },
            "Currency and Denominations": {
                "Currency": "US Dollars",
                "Round this tender": True,
                "Hundred Dollar Bill": { 
                    "Description": "Hundred Dollar Bill",
                    "Amount": "100.00",
                    "Bill": True
                },
                "Twenty Dollar Bill": { 
                    "Description": "Twenty Dollar Bill",
                    "Amount": "20.00",
                    "Bill": True
                }
            },
            "Functions": {
                "Sale": {
                    "Show exact amount button": True,
                    "Show next highest button": True,
                    "Select a denomination then select one of the preset buttons": {
                        "Hundred Dollar Bill": ["Preset button top left", "Preset button bottom left"],
                        "Twenty Dollar Bill": ["Preset button top right", "Preset button bottom right"]
                    }
                },
                "Refund": {
                    "Show exact amount button": True,
                    "Select a denomination then select one of the preset buttons": {
                        "Hundred Dollar Bill": ["Preset button top left", "Preset button bottom left"],
                        "Twenty Dollar Bill": ["Preset button top right", "Preset button bottom right"]
                    }
                }   
            },
            "Min/Max": {
                "Minimum Allowed": "0.00",
                "Maximum Allowed": "100.00",
                "Repeated Use Limit": "5",
                "Maximum Refund": "25.00",
                "Primary tender for change": "Test US Dollars",
                "Maximum primary change allowed": "100.00",
                "Secondary tender for change": "Cash"
            },
            "Register Groups": {
                "POSGroup1": {
                    "Sales": True,
                    "Refunds": False,
                    "Loans": True,
                    "Paid In": False,
                    "Paid Out": True,
                    "Open cash drawer when this tender is received": True
                }
            }
        }
        self.tm.configure("Test US Dollars",tender_info,False)
    
    @test
    def tender_changestatus(self):
        """Tests whether the status of an existing tender type can be changed.
        Args: None
        Returns: None
        """
        self.tm.change_status("Test US Dollars",True)

    @test
    def tender_denominations(self):
        """Tests whether the denominations of an existing tender can be created, changed, and deleted.
        Args: None
        Returns: None
        """
        mws.set_value("Tenders","Test US Dollars")
        mws.click_toolbar("Change")

        if not self.tm.configure_denomination("Add", desc= "New Tender", amount= "1.00", bill= True):
            tc_fail("Adding failed...")
        if not self.tm.configure_denomination("Change", "New Tender", desc= "New Tender (edit)", amount= "2.50", bill= False):
            tc_fail("Changing failed...")
        if not self.tm.configure_denomination("Delete", "New Tender (edit)"):
            tc_fail("Deletion failed...")

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        # delete pass after you implement.
        pass