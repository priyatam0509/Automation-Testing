"""
    File name: SL-1905.py
    Brand:  Concord
    Description: As a store owner I want required information to be shown on receipt so that transaction details as available
    Author: Paresh
    Date created: 2020-10-06 08:42:19
    Date last modified: 
    Python Version: 3.7
"""

import logging, time
from app import pos
from app.framework.tc_helpers import setup, test, teardown, tc_fail

# The logging object. 
log = logging.getLogger()

class SL_1905():
    """
    Description: Test class that provides an interface for testing.
    """

    def __init__(self):
        """Initializes the Template class.
        Args: None
        Returns: None
        """
        self.fuel_amount = "$5.00"
        self.fuel_grade = "Diesel 1"
        
    @setup
    def setup(self):
        """Performs any initialization that is not default.
        Args: None
        Returns: None
        """

        if not pos.connect():
            log.error("Unable to connect with pos")
            return False
        
        if not pos.sign_on():
            log.error("failed to login in pos")
            return False

    @test
    def TC01(self):
        """ 
        Description : To verify prepay & dry stock item transactions is completed successfully for EMV VOYAGER card with bin range 708885-708889
        Args: None
        Returns: None
        """
        # Add 1 dry stock item and fuel with prepay
        pos.add_item("Item 2")

        # Add fuel in prepay mode
        pos.add_fuel(amount = self.fuel_amount, grade = self.fuel_grade)
        
        # Pay usign Voyager EMV card
        pos.pay_card(card_name = "Voyager1_EMV")
        
        # Wait until dispenser 1 is idle
        pos.wait_for_disp_status('IDLE', timeout=90)

        # Verify card name and aid is printed on receipt
        if not pos.check_receipt_for(["1394", "Voyager", "A0000000041010"]):
           tc_fail("Card Name and AID is not present in receipt")
        
        return True

    @test
    def TC02(self):
        """ 
        Description : To verify Postpay & dry stock item transactions is completed successfully for EMV VOYAGER card with bin range 708885-708889
        Args: None
        Returns: None
        """

        # Add fuel with preset mode
        pos.add_fuel(amount = self.fuel_amount, mode = "preset", grade = self.fuel_grade)
        
        # Check if fueling is completed
        if not pos.wait_for_disp_status("IDLE", timeout=90):
            return False

        # Take fuel inside POS
        pos.click_fuel_buffer("A")
        
        # Add item
        pos.add_item("Item 2")
        
        # Complete transaction using Voyager emv card
        pos.pay_card(card_name = "Voyager1_EMV")

        # Verify card name and aid is printed on receipt
        if not pos.check_receipt_for(["1394", "Voyager", "A0000000041010"]):
           tc_fail("Card Name and AID is not present in receipt")
        
        return True

    @test
    def TC03(self):
        """ 
        Description : To verify Manual & dry stock item transactions is completed successfully for EMV VOYAGER card with bin range 708885-708889
        Args: None
        Returns: None
        """
        
        # Add fuel in manual mode
        pos.add_fuel(self.fuel_amount, mode="manual", grade=self.fuel_grade)
        
        # Add dry stock item
        pos.add_item("Item 2")

        # Complete transaction using Voyager emv card
        pos.pay_card(card_name = "Voyager1_EMV")

        # Verify card name and aid is printed on receipt
        if not pos.check_receipt_for(["1394", "Voyager", "A0000000041010"]):
           tc_fail("Card Name and AID is not present in receipt")
        
        return True

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """

        pos.close()