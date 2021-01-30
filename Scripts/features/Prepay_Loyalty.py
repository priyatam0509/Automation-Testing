"""
    File name: Prepay_Loyalty.py
    Tags:
    Description: [PEACOCK-3737] This will perform PrePay sale with loyalty configured for fuel, non-fuel and transaction rewards.
                 After sale this will verify receipt for loyalty discounts.
    Pre-requisite: Fuel price must be $1.00
                   Fuel(20 cents), non-fuel(30 cents) and transaction(10 cents) rewards must 
                   be configured for loyalty1(card mask - 6008) and loyalty2(card mask - 7079) in loyalty simulator. 
                   Apply non-fuel reward on Item2(Price:$5.00)
    Author: Asha
    Date created: 2019-11-25 14:53:24
    Date last modified: 
    Python Version: 3.7
"""

import logging, time
from app import Navi, pos, mws, system, pinpad, item
from Scripts.framework import Loyalty_Check_Functions
from app.simulators import loyaltysim 
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class Prepay_Loyalty():
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

        # Item on which non-fuel loyalty will be applied
        self.item_PLU = "002"

        self.fuel_amount = "$5.00"

        self.fuel_grade = "Diesel 1"

        # Setting fuel price
        self.fuel_price = 1.00

        # 20 cents fuel reward
        self.fuel_loyalty = 0.25

        # 20 cents transaction reward
        self.trans_loyalty = 0.20

        # 15 cents non-fuel discount
        self.nonfuel_loyalty = 0.15

        # Fuel loyalty text
        self.fuel_loyalty_text = "DISCOUNTS APPLIED BEFORE FUELING"

        # transaction loyalty text
        self.trans_loyalty_text = "$" + str(self.trans_loyalty)

        #Make item discoutable
        self.item_data = {
            "General": {
                "This item sells for": True,
                "per unit": "5.00"
            },
            "Options": {
                "Discountable": True
            }
        }

    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        # Navigate to POS
        Navi.navigate_to("MWS")

        # Create object for Item
        obj = item.Item()

        # Make item discountable
        obj.change("002", self.item_data)

        mws.click_toolbar("Exit")
        
        #Sign on to POS screen if not already sign-on
        Navi.navigate_to("POS")
        pos.sign_on()

    @test
    def fuel_prepay(self):
        """
        Zephyr Id : This will add fuel and perform a prepay sale with loyalty configured.
                    This will swipe loyalty card on pinpad simulator.
                    It will check receipt for fuel and transaction loyalty rewards applied in sale
        Args: None
        Returns: None
        """

        # Adding fuel having fuel grade Diesel 1
        pos.add_fuel(self.fuel_amount, grade=self.fuel_grade)
       
        if not pos.click_function_key("pay", verify=False):
            return False

        # Select Kickback from list
        if "Select Loyalty Program" in pos.read_status_line():
            pos.select_list_item("Kickback", verify=False)
            pos.click_keypad("ENTER", verify=False)
            self.log.info("Kickback selected")
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

        pos.pay()

        # Wait until dispenser 1 is idle
        pos.wait_for_fuel(timeout=60, verify=False)

        #Calculate sale amount after loyalty rewards
        fuel_amount = float(self.fuel_amount.replace('$',''))
        fuel_rewards = self.fuel_price - self.fuel_loyalty
        discount = fuel_amount / fuel_rewards
        fuel_discount_text = format(discount, '0.3f') + "GAL @ $"+format(fuel_rewards,'0.3f')+"/GAL"
        total_amount = fuel_amount - self.trans_loyalty

        # Check receipt for loyalty rewards
        if not pos.check_receipt_for([fuel_discount_text, self.fuel_loyalty_text, self.trans_loyalty_text, "$"+str(total_amount)]):
           tc_fail("Loyalty rewards not displayed in receipt")
           return False
           
        return True 

    @test
    def fuel_drystock_carwash_prepay(self):
        """
        Zephyr Id : This will add fuel, dry stock and car wash and Perform a prepay sale with loyalty configured.
                    This will swipe loyalty card on pinpad simulator.
                    It will check receipt for fuel, non-fuel and transaction loyalty rewards applied in sale.
        Args: None
        Returns: None
        """

        # Rename Loyalty2 as Kickback, before running it. 
        Loyalty_Check_Functions.rename_loyalty("Loyalty1","Kickback","Loyalty2")

        # Adding fuel having fuel grade Diesel 1
        pos.add_fuel(self.fuel_amount, grade=self.fuel_grade)

        # Add Car Wash Item
        pos.add_item("1234", method="plu", qualifier="CARWASH 1")

        # Add Item2
        pos.add_item(self.item_PLU, method="plu")
       
        if not pos.click_function_key("pay", verify=False):
            return False

        # Rename Loyalty2 as Kickback, before running it. 
        if "Select Loyalty Program" in pos.read_status_line():
            pos.select_list_item("Kickback", verify=False)
            pos.click_keypad("ENTER", verify=False)
            self.log.info("Loyalty2 selected")
        else:
            tc_fail("Loyalty selection not available")
            return False
            
        # Swipe loyalty2 card
        try:
            if "Enter Kickback ID" in pos.read_status_line():
                pinpad.swipe_card(brand=system.get_brand(), card_name="Loyalty2")
                time.sleep(5)
            else:
                tc_fail("Loyalty2 not selected")
                return False
        except Exception as e:
            self.log.warning(f"Card swipe in pinpad failed. Exception: {e}")
            pos.click_keypad("CANCEL")
            return False

        # Let's add logic to handle optional drystock reward
        message = pos.read_message_box(5)
        if message and ("Reward?" in pos.read_message_box(5)):
            pos.click_message_box_key("YES")

        # Perform cash payment
        pos.pay()

        # Wait until dispenser 1 is idle
        pos.wait_for_fuel(timeout=60, verify=False)

        # Calculate sale amount after loyalty rewards
        fuel_amount = float(self.fuel_amount.replace('$',''))
        fuel_rewards = self.fuel_price - self.fuel_loyalty
        discount = fuel_amount / fuel_rewards
        fuel_discount_text = format(discount, '0.3f') + "GAL @ $"+format(fuel_rewards,'0.3f')+"/GAL"
        nonfuel_loyalty_text = "$-" + str(self.nonfuel_loyalty)
        
        # Total amount is calculated as fuel sale amount + carwash1 amount + ( item2 amount - non-fuel reward) - transaction reward
        total_amount = fuel_amount + 2.50 + (5.00 - self.nonfuel_loyalty) - self.trans_loyalty

        # Check receipt for loyalty rewards
        if not pos.check_receipt_for([nonfuel_loyalty_text, fuel_discount_text, self.fuel_loyalty_text, self.trans_loyalty_text, "$"+str(total_amount)]):
           tc_fail("Loyalty rewards not displayed in receipt")
           return False
           
        return True

    @test
    def manual_loyalty_prepay(self):
        """
        Zephyr Id : This will add fuel and car wash and Perform a prepay sale with loyalty configured.
                    This will enter loyalty card number manually on pinpad simulator.
                    It will check receipt for fuel and transaction loyalty rewards applied in sale.
        Args: None
        Returns: None
        """
        # Adding fuel having fuel grade Diesel 1
        pos.add_fuel(self.fuel_amount, grade=self.fuel_grade)

        # Add Car Wash Item
        pos.add_item("1234", method="plu", qualifier="CARWASH 1")
       
        if not pos.click_function_key("pay", verify=False):
            return False

        # Select Loyalty2
        if "Select Loyalty Program" in pos.read_status_line():
            pos.select_list_item("Kickback", verify=False)
            pos.click_keypad("ENTER", verify=False)
            pos.click_keypad("MANUAL", verify=False)
            self.log.info("Loyalty2 selected")
        else:
            tc_fail("Loyalty selection not available")
            return False
            
        # Swipe loyalty2 card
        try:
            if "Have Customer Enter Kickback ID" in pos.read_status_line():
                pinpad.manual_entry(brand=system.get_brand(), card_name="Loyalty2")
            else:
                tc_fail("Loyalty2 not selected")
                return False
        except Exception as e:
            self.log.warning(f"Card swipe in pinpad failed. Exception: {e}")
            pos.click_keypad("CANCEL")
            return False

        # Perform cash payment
        pos.pay()
        
        # Wait until dispenser 1 is idle
        pos.wait_for_fuel(timeout=60, verify=False)

        # Calculate sale amount after loyalty rewards
        fuel_amount = self.fuel_amount.replace('$','')
        fuel_amount = float(fuel_amount)
        fuel_rewards = self.fuel_price - self.fuel_loyalty
        discount = fuel_amount / fuel_rewards
        fuel_discount_text = format(discount, '0.3f') + "GAL @ $"+format(fuel_rewards,'0.3f')+"/GAL"
        
        # Total amount is calculated as fuel sale amount + carwash1 amount - transaction reward
        total_amount = fuel_amount + 2.50 - self.trans_loyalty

        # Check receipt for loyalty rewards
        if not pos.check_receipt_for([fuel_discount_text, self.fuel_loyalty_text, self.trans_loyalty_text, "$"+str(total_amount)]):
           tc_fail("Loyalty rewards not displayed in receipt")
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