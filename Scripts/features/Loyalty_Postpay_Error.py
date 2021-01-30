"""
    File name: Loyalty_Postpay_Error.py
    Tags:
    Description: [PEACOCK-3747] This will verify error when wrong loyalty card is swiped.
    Preconditions: Loyalty must be configured in loyalty interface
    Author: Satish
    Date created: 2020-01-10 02:22:21
    Date last modified: 
    Python Version: 3.7
"""

import logging, time
from app import Navi, pos, system, pinpad, loyalty
from Scripts.framework import Loyalty_Check_Functions
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class Loyalty_Postpay_Error():
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
        #Navigate to POS
        Navi.navigate_to("POS")

        #Sign on to POS screen if not already sign-on
        pos.sign_on()

    @test
    def invalid_card_error(self):
        """
        Zephyr Id : This will verify that error message box pops up
                    when credit/debit card is swiped instead of loyalty card
        Args: None
        Returns: None
        """
        # Rename loyalty
        Loyalty_Check_Functions.rename_loyalty("Loyalty1","Kickback","Loyalty3")

        # Adding fuel having fuel grade Diesel 1
        pos.add_fuel(self.fuel_amount, mode="preset", grade=self.fuel_grade)

        # Check if fueling is completed
        pos.wait_for_fuel(timeout=60, verify=False)

        # Take fuel inside POS
        pos.click_suspended_transaction()

        # Perform Payment
        if not pos.click_function_key("pay", verify=False):
            return False

        # Select Loyalty3
        if "Select Loyalty Program or Cancel" in pos.read_status_line():
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
            tc_fail("Loyalty3 is not selected")
            return False

        try:
            error_msg = pos.read_message_box()
            if not "invalid loyalty identifier" in error_msg.lower():
                tc_fail("Error message not correct")
        except Exception as e:
                tc_fail(f"message box not came. Exception: {e}")

        # Complete the transaction 
        if not pos.click_message_box_key("OK", verify=False):
            return False
        if not pos.click_keypad("CANCEL", verify=False):
            return False
        if not pos.pay():
            return False

        return True

    @test
    def invalid_loyalty_card_error(self):
        """
        Zephyr Id : This will verify that error message pops up 
                    when you swipe wrong configured loyalty card with different card mask 
        Args: None
        Returns: None
        """
        Loyalty_Check_Functions.rename_loyalty("Loyalty3","Kickback","Loyalty4")
        # Adding fuel having fuel grade Diesel 1
        pos.add_fuel(self.fuel_amount, mode="preset", grade=self.fuel_grade)

        # Check if fueling is completed
        pos.wait_for_fuel(timeout=60, verify=False)

        # Take fuel inside POS
        pos.click_suspended_transaction()

        # Perform Payment
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
            if not "invalid loyalty identifier" in error_msg.lower():
                tc_fail("Error message not correct")
        except Exception as e:
            tc_fail(f"Message box not came. Exception: {e}")

        # Complete the transaction 
        if not pos.click_message_box_key("OK", timeout=20, verify=False):
            return False
        if not pos.click_keypad("CANCEL", timeout=20, verify=False):
            return False
        if not pos.pay():
            return False

        return True

    @test
    def multiple_loyalty_error(self):
        """
        Zephyr Id : This will verify that multiple loyalty is not applied.
        Args: None
        Returns: None
        """
        # Rename loyalty
        Loyalty_Check_Functions.rename_loyalty("Loyalty4","Kickback","Loyalty1")

        # Adding fuel having fuel grade Diesel 1
        pos.add_fuel(self.fuel_amount, mode="preset", grade=self.fuel_grade)

        # Check if fueling is completed
        pos.wait_for_fuel(timeout=60, verify=False)

        # Take fuel inside POS
        pos.click_suspended_transaction()

        # Perform Payment
        if not pos.click_function_key("pay", verify=False):
            return False
        
        # Select Loyalty1
        if "Select Loyalty Program or Cancel" in pos.read_status_line():
            pos.select_list_item("Kickback", verify=False)
            pos.click_keypad("ENTER", verify=False)
            self.log.info("Loyalty1 selected")
        else:
            tc_fail("Loyalty selection not available")
            return False
            
        # Swipe loyalty1 card
        try:
            if "Enter Kickback ID" in pos.read_status_line():
                pinpad.swipe_card(brand=system.get_brand(), card_name="Loyalty1")
            else:
                tc_fail("Loyalty1 not selected")
                return False
        except Exception as e:
            self.log.warning(f"Card swipe in pinpad failed. Exception: {e}")
            pos.click_keypad("CANCEL")
            return False
        
        # Cancel the payment by clicking on Cancel button.
        if not pos.click_keypad("CANCEL", verify=False):
            return False
        
        # To verify whether multiple loyalties are selected or not
        if not pos.click_function_key("pay", verify=False):
            return False

        if not "Select Loyalty Program or Cancel" in pos.read_status_line():
            self.log.info("Loyalty is already applied")
            pos.pay()
            return True
        else:
            tc_fail("Multiple loyalties should not be allowed")
            return False
                
        return True

    @test
    def cancel_loyalty_postpay_error(self):
        """
        Zephyr Id : This will verify cancel for loyalty when we perform postpay.
        Args: None
        Returns: None
        """
        # Adding fuel having fuel grade Diesel 1
        pos.add_fuel(self.fuel_amount, mode="preset", grade=self.fuel_grade)

        # Check if fueling is completed
        pos.wait_for_fuel(timeout=60, verify=False)
        
        # Take fuel inside POS
        pos.click_suspended_transaction()

        # Perform Payment
        if not pos.click_function_key("pay", verify=False):
            return False

        # Cancel the Loyalty program selection screen
        if "Select Loyalty Program" in pos.read_status_line():
            pos.click_keypad("CANCEL", verify=False)
        else:
            tc_fail("Loyalty selection not available")
            return False

        # Payment Screen
        if not "Please select the tender type" in pos.read_status_line():
            tc_fail("Loyalty selection not available")
            return False
        else:
            self.log.info("Payment screen is displayed")

        # Complete the transaction
        if not pos.pay():
            return False

        return True
        
    @test
    def invalid_card_error_manual(self):
        """
        Zephyr Id : This will verify that error message box pops up
                    when credit/debit card is entered manualy on pinpad instead of loyalty card.
        Args: None
        Returns: None
        """
        # Rename Loyalty
        Loyalty_Check_Functions.rename_loyalty("Loyalty1","Kickback","Loyalty5")

        # Adding fuel having fuel grade Diesel 1
        pos.add_fuel(self.fuel_amount, mode="preset", grade=self.fuel_grade)

        # Check if fueling is completed
        pos.wait_for_fuel(timeout=60, verify=False)

        # Take fuel inside POS
        pos.click_suspended_transaction()

        # Perform Payment
        if not pos.click_function_key("pay", verify=False):
            return False
        
        # Select Loyalty5
        if "Select Loyalty Program or Cancel" in pos.read_status_line():
            pos.select_list_item("Kickback", verify=False)
            pos.click_keypad("ENTER", verify=False)
            pos.click_keypad("MANUAL", verify=False)
            self.log.info("Loyalty5 selected")
        else:
            tc_fail("Loyalty selection not available")
            return False

        # Manual enter Visa card number on pinpad
        if "Enter Kickback ID" in pos.read_status_line():
            pinpad.manual_entry()
        else:
            tc_fail("Loyalty5 not selected")
            return False

        try:
            error_msg = pos.read_message_box()
            if not "invalid loyalty identifier" in error_msg.lower():
                tc_fail("Error message not correct")
        except Exception as e:
                tc_fail(f"Message boc not came. Exception :{e}")

        # Complete the transaction
        if not pos.click_message_box_key("OK", timeout=20, verify=False):
            return False

        if not pos.click_keypad("CANCEL", timeout=30, verify=False):
            return False

        if not pos.pay():
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