"""
    File name: SL-1902.py
    Brand:  Concord
    Description: Service Code in Voyager EMV cards
    Author: Paresh
    Date created: 2020-09-25 08:42:19
    Date last modified: 
    Python Version: 3.7
"""

import logging, time
from app import pos, pinpad
from app.framework.tc_helpers import setup, test, teardown, tc_fail

# The logging object. 
log = logging.getLogger()

class SL_1902():
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
        Description : To verify when EMV Voyager card is swiped on pin pad magstripe reader then POS is used the magstripe reader to process the card when performed prepay & dry stock transactions
        Args: None
        Returns: None
        """
        # Add 1 dry stock item and fuel with prepay
        pos.add_item("Item 2")

        # Add fuel in prepay mode
        pos.add_fuel(amount = self.fuel_amount, grade = self.fuel_grade)
        
        # Swipe Voyager emv card
        pos.click("Pay")
        pos.click("Card")
        try:
            pinpad.swipe_card(card_name= "Voyager1_EMV")
            time.sleep(2)
        except Exception as e:
            log.warning(f"Card swipe in pinpad failed. Exception: {e}")
        
        # Wait for message appear
        message = pos.read_processing_text()
        
        # Verify message if we are swipping the Voyager emv card
        if "Swipe not allowed on EMV cards. Please insert" not in message:
            tc_fail("Error message is not displayed for Voyager card")
        
        # Complete transaction using Voyager emv card
        pos.click("Cancel")
        pos.click_message_box_key("OK")

        pos.pay_card(card_name = "Voyager1_EMV")
        
        # Wait until dispenser 1 is idle
        pos.wait_for_disp_status('IDLE', timeout=90)
        
        return True

    @test
    def TC02(self):
        """ 
        Description : To verify when EMV Voyager card is swiped on pin pad magstripe reader then POS is used the chip card reader to process the card when performed postpay & dry stock transactions
        Args: None
        Returns: None
        """

        # Add fuel with preset
        pos.add_fuel(amount = self.fuel_amount, mode = "preset", grade = self.fuel_grade)
        
        # Check if fueling is completed
        if not pos.wait_for_disp_status("IDLE",timeout=90):
            return False

        # Take fuel inside POS
        pos.click_fuel_buffer("A")
        
        # Add item
        pos.add_item("Item 2")
        
        # Swipe Voyager emv card
        pos.click("Pay")
        pos.click("Card")
        try:
            pinpad.swipe_card(card_name= "Voyager1_EMV")
            time.sleep(2)
        except Exception as e:
            log.warning(f"Card swipe in pinpad failed. Exception: {e}")

        # Wait for message appear
        message = pos.read_processing_text()
        
        # Verify message if we are swipping the Voyager emv card
        if "Swipe not allowed on EMV cards. Please insert" not in message:
            tc_fail("Error message is not displayed for Voyager card")
        
        # Complete transaction using Voyager emv card
        pos.click("Cancel")
        pos.click_message_box_key("OK")

        pos.pay_card(card_name = "Voyager1_EMV")
        
        return True

    @test
    def TC03(self):
        """ 
        Description : To verify when EMV Voyager card is swiped on pin pad magstripe reader after EMV fallback then POS is used the magstripe reader to process the card when performed manual fuel sale & dry stock transactions 
        Args: None
        Returns: None
        """
        
        # Add fuel in manual mode
        pos.add_fuel(self.fuel_amount, mode="manual", grade=self.fuel_grade)
        
        # Add dry stock item
        pos.add_item("Item 2")
        
        # Swipe Voyager emv card
        pos.click("Pay")
        pos.click("Card")
        try:      
            pinpad.swipe_card(card_name= "Voyager1_EMV")
            time.sleep(2)
        except Exception as e:
            log.warning(f"Card swipe in pinpad failed. Exception: {e}")

        # Wait for message appear
        message = pos.read_processing_text()
        
        # Verify message if we are swipping the Voyager emv card
        if "Swipe not allowed on EMV cards. Please insert" not in message:
            tc_fail("Error message is not displayed for Voyager card")
        
        # Complete transaction using Voyager emv card
        pos.click("Cancel")
        pos.click_message_box_key("OK")

        pos.pay_card(card_name = "Voyager1_EMV")
        
        return True

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """

        pos.close()