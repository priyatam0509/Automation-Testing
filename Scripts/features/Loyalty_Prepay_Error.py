"""
    File name: Loyalty_Prepay_Error.py
    Tags:
    Description: [PEACOCK-3737] This will verify error when wrong loyalty card is swiped
    Pre-requisite: Loyalty must be configured in loyalty interface
    Author: Asha
    Date created: 2019-11-25 14:53:24
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import Navi, pos, system, pinpad, loyalty
from Scripts.framework import Loyalty_Check_Functions
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class Loyalty_Prepay_Error():
    """
    Description: Test class that provides an interface for testing.
    """
    def __init__(self):
        """
        Initializes the Template class.
        Args: None
        Returns: None
        """
        # The logging object. 
        # Example: self.log.info(f"Current value of var: {my_var}")
        self.log = logging.getLogger()

        self.fuel_amount = "$5.00"

        self.fuel_grade = "Diesel 1"

    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        # Navigate to POS
        Navi.navigate_to("POS")
        
        # Sign on to POS screen if not already sign-on
        pos.sign_on()

    @test
    def invalid_card_error(self):
        """
        Zephyr Id : This will verify that error message box pops up 
                    when credit/debit card is swiped instead of loyalty card.
        Args: None
        Returns: None
        """
        Loyalty_Check_Functions.rename_loyalty("Loyalty2","Kickback","Loyalty3")

        # Adding fuel having fuel grade Diesel 1
        pos.add_fuel(self.fuel_amount, grade=self.fuel_grade)
       
        if not pos.click_function_key("pay", verify=False):
            return False

        # Select Loyalty3
        if "Select Loyalty Program" in pos.read_status_line():
            pos.select_list_item("Kickback", verify=False)
            pos.click_keypad("ENTER", verify=False)
            self.log.info("Loyalty3 selected")
        else:
            tc_fail("Loyalty selection not available")
            return False
            
        # Swipe Visa card
        if "Enter Kickback ID" in pos.read_status_line():
            pinpad.swipe_card()
        else:
            tc_fail("Loyalty3 not selected")
            return False

        try:
            error_msg = pos.read_message_box()
            if not "invalid loyalty identifier.  please re-enter" in error_msg.lower():
                tc_fail("Error message not correct")
        except Exception as e:
            tc_fail(f"Message box not came. Exception: {e}")
            
        # Void transaction
        if not pos.click_message_box_key("OK", verify=False):
            return False
        if not pos.click_keypad("CANCEL", verify=False):
            return False
        if not pos.click_keypad("CANCEL", verify=False):
            return False
        if not pos.click_function_key("VOID TRANS", verify=False):
            return False
        if not pos.click_keypad("ENTER", verify=False):
            return False

        return True

    @test
    def invalid_loyaltycard_error(self):
        """
        Zephyr Id : This will verify that error message pops up 
                    when you swipe wrong configured loyalty card with different card mask 
        Args: None
        Returns: None
        """
        Loyalty_Check_Functions.rename_loyalty("Loyalty3","Kickback","Loyalty4")

        # Adding fuel having fuel grade Diesel 1
        pos.add_fuel(self.fuel_amount, grade=self.fuel_grade)
       
        if not pos.click_function_key("pay", verify=False):
            return False

        # Select Loyalty4
        if "Select Loyalty Program" in pos.read_status_line():
            pos.select_list_item("Kickback", verify=False)
            pos.click_keypad("ENTER", verify=False)
            self.log.info("Loyalty4 selected")
        else:
            tc_fail("Loyalty selection not available")
            return False

        # Swipe Loyalty1 card having different card mask than Loyalty4
        if "Enter Kickback ID" in pos.read_status_line():
            pinpad.swipe_card(brand=system.get_brand(), card_name="Loyalty1")
        else:
            tc_fail("Loyalty4 not selected")
            return False

        try:
            error_msg = pos.read_message_box()
            if not "invalid loyalty identifier.  please re-enter" in error_msg.lower():
                tc_fail("Error message not correct")
        except Exception as e:
            tc_fail(f"Message box not came. Exception: {e}")
            
        # Void transaction
        if not pos.click_message_box_key("OK", verify=False):
            return False
        if not pos.click_keypad("CANCEL", verify=False):
            return False
        if not pos.click_keypad("CANCEL", verify=False):
            return False
        if not pos.click_function_key("VOID TRANS", verify=False):
            return False
        if not pos.click_keypad("ENTER", verify=False):
            return False

        return True

    @test
    def multiple_loyalty_error(self):
        """
        Zephyr Id : This will verify that multiple loyalty is not applied.
        Args: None
        Returns: None
        """
        Loyalty_Check_Functions.rename_loyalty("Loyalty4","Kickback","Loyalty2")
        # Adding fuel having fuel grade Diesel 1
        pos.add_fuel(self.fuel_amount, grade=self.fuel_grade)
       
        if not pos.click_function_key("pay", verify=False):
            return False

        # Select Loyalty2
        if "Select Loyalty Program" in pos.read_status_line():
            pos.select_list_item("Kickback", verify=False)
            pos.click_keypad("ENTER", verify=False)
            self.log.info("Loyalty2 selected")
        else:
            tc_fail("Loyalty selection not available")
            return False

        # Swipe Loyalty2 card having different card mask than Loyalty4
        if "Enter Kickback ID" in pos.read_status_line():
            pinpad.swipe_card(brand=system.get_brand(), card_name="Loyalty2")
        else:
            tc_fail("Loyalty2 not selected")
            return False

        # Cancel transaction
        if not pos.click_keypad("CANCEL", verify=False):
            return False

        # Again try to select loyalty
        if not pos.click_function_key("pay", verify=False):
            return False    

        if "Select Loyalty Program" in pos.read_status_line():
            tc_fail("loyalty selection window came again ")

        #Void transaction
        if not pos.click_keypad("CANCEL", verify=False):
            return False
        if not pos.click_function_key("VOID TRANS", verify=False):
            return False
        if not pos.click_keypad("ENTER", verify=False):
            return False

        return True

    @test
    def cancel_loyalty(self):
        """
        Zephyr Id : This will verify cancel for loyalty when we perform prepay.
        Args: None
        Returns: None
        """
        # Adding fuel having fuel grade Diesel 1
        pos.add_fuel(self.fuel_amount, grade=self.fuel_grade)
       
        if not pos.click_function_key("pay", verify=False):
            return False

        # Select Loyalty2
        if "Select Loyalty Program" in pos.read_status_line():
            pos.click_keypad("CANCEL", verify=False)
        else:
            tc_fail("Loyalty selection not available")
            return False

        # Swipe Loyalty2 card having different card mask than Loyalty4
        if not "Please select the tender type and enter an amount." in pos.read_status_line():
            tc_fail("Loyalty selection not available")
            return False
        else:
            self.log.info("Payment screen is displayed")

        # Void transaction
        if not pos.click_keypad("CANCEL", verify=False):
            return False
        if not pos.click_function_key("VOID TRANS", verify=False):
            return False
        if not pos.click_keypad("ENTER", verify=False):
            return False

        return True

    @test
    def invalid_card_error_manual(self):
        """
        Zephyr Id : This will verify that error message box pops up 
                    when credit/debit card is entered manually on pinpad instead of loyalty card.
        Args: None
        Returns: None
        """
        Loyalty_Check_Functions.rename_loyalty("Loyalty2","Kickback","Loyalty5")
        # Adding fuel having fuel grade Diesel 1
        pos.add_fuel(self.fuel_amount, grade=self.fuel_grade)
       
        if not pos.click_function_key("pay", verify=False):
            return False

        # Select Loyalty5
        if "Select Loyalty Program" in pos.read_status_line():
            pos.select_list_item("Kickback", verify=False)
            pos.click_keypad("ENTER", verify=False)
            pos.click_keypad("MANUAL", verify=False)
            self.log.info("Loyalty5 selected")
        else:
            tc_fail("Loyalty selection not available")
            return False
            
        # Manually enter Visa card number on pinpad
        if "Enter Kickback ID" in pos.read_status_line():
            pinpad.manual_entry()
        else:
            tc_fail("Loyalty5 not selected")
            return False

        try:
            error_msg = pos.read_message_box()
            if not "invalid loyalty identifier.  please re-enter" in error_msg.lower():
                tc_fail("Error message not correct")
        except Exception as e:
            tc_fail(f"Message box not came. Exception: {e}")
            
        # Void transaction
        if not pos.click_message_box_key("OK", verify=False):
            return False
        if not pos.click_keypad("CANCEL", verify=False):
            return False
        if not pos.click_keypad("CANCEL", verify=False):
            return False
        if not pos.click_function_key("VOID TRANS", verify=False):
            return False
        if not pos.click_keypad("ENTER", verify=False):
            return False

        return True

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        pass