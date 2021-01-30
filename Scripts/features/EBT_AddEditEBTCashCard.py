"""
    File name: EBT_AddEditEBTCashCard.py
    Tags:
    Description: SL-1572 - Enable the EBT tender keys
    Brand: Phillips 66
    Author: Paresh
    Date created: 2019-31-12 13:31:37
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app.features import tender
from app import mws
from app.framework.tc_helpers import setup, test, teardown, tc_fail


class EBT_AddEditEBTCashCard():
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
        self.tm = tender.TenderMaintenance()
    
    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        pass
    
    @test
    def add_cash_card(self):
        """
        Testlink Id: SL-1572 - Enable the EBT tender keys
		Description: Verify we can add EBT cash card
        Args: None
        Returns: None
        """
		
        tender_info = {
                "Tender Code": "93",
                "Tender Description": "Test EBT1",
                "General": {
                    "Tender group this tender belongs to": "EBT Cash (Non-integrated)",
                    "Safe drops allowed for this tender": True,
                    "Print tax invoice text on Receipt": True,
                    "Receipt Description": "Test Desc1",
                    "Tender Button Description": "Test Desc1",
                    "NACS Tender Code": "ebt"
                },
                "Currency And Denominations": {
                    "Currency": "US Dollars",
                    "Round this tender": True
                },
                "Min/Max": {
                    "Minimum Allowed": "0.00",
                    "Maximum Allowed": "100.00",
                    "Repeated Use Limit": "5",
                    "Maximum Refund": "25.00",
                    "Primary tender for change": "Cash",
                    "Maximum primary change allowed": "100.00",
                    "Secondary tender for change": "Cash"
                },
                "Register Groups": {
                    "POSGroup1": {
                        "Sales": True,
                        "Refunds": True,
                        "Loans": True}
                }
            }
        if not self.tm.configure("Test EBT1", tender_info, False):
            tc_fail("Unable to add EBT Cash type")

        return True
    
    @test
    def edit_cash_card(self):
        """
        Testlink Id: SL-1572 - Enable the EBT tender keys
        Description: Verify we can edit EBT cash card details
        Args: None
        Returns: None
        """
        
        tender_info = {
                "Tender Code": "93",
                "Tender Description": "Test EBT2",
                "General": {
                    "Tender group this tender belongs to": "EBT Cash (Non-integrated)",
                    "Safe drops allowed for this tender": False,
                    "Print tax invoice text on Receipt": False,
                    "Receipt Description": "Test Desc2",
                    "Tender Button Description": "Test Desc2",
                    "NACS Tender Code": "ebt"
                },
                "Min/Max": {
                    "Minimum Allowed": "0.00",
                    "Maximum Allowed": "10.00",
                    "Repeated Use Limit": "4",
                    "Maximum Refund": "5.00",
                    "Primary tender for change": "Cash",
                    "Maximum primary change allowed": "100.00",
                    "Secondary tender for change": "Cash"
                }
            }
        if not self.tm.configure("Test EBT1", tender_info, True):
            tc_fail("Unable to edit EBT Cash type")
        if not self.tm.change_status("Test EBT2", False):
            tc_fail("Failed to change status")
        
        mws.click_toolbar("Exit")
        
        return True
 
    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        pass