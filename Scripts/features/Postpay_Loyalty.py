"""
    File name: Postpay_Loyalty.py
    Tags:
    Description: [PEACOCK-3747] This will perform PostPay sale with loyalty configured for fuel, non-fuel and transaction rewards.
                 After sale this will verify receipt for loyalty discounts.
    Pre-requisite: Fuel price must be $1.00
                   Fuel(20 cents), non-fuel(30 cents) and transaction(10 cents) rewards must 
                   be configured for loyalty1(card mask - 6008) and loyalty2(card mask - 7079) in loyalty simulator. 
                   Apply non-fuel reward on Item2
    Author: Satish Venkat
    Date created: 2019-12-26 17:53:32
    Date last modified: 
    Python Version: 3.7
"""

import logging, time
from app import Navi, pos, system, pinpadsim, pinpad, loyalty
from Scripts.framework import Loyalty_Check_Functions
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class Postpay_Loyalty():
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

        self.fuel_amount = "$2.00"

        self.fuel_grade = "Diesel 1"

        # Fuel reward
        self.fuel_rewards = 0.25

        # Transaction reward
        self.trans_reward = 0.20

        # Dry Stock rewards
        self.nonfuel_reward = 0.15
        
        # Fuel Loyalty rewards texts
        self.fuel_discount_text = "DISCOUNTS APPLIED AFTER FUELING"

        # Transaction loyalty text
        self.trans_text = "$" + str(self.trans_reward)

    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        # Navigate to POS
        Navi.navigate_to("POS")

        #Sign on to POS screen if not already sign-on
        pos.sign_on()

    @test
    def fuel_postpay(self):
        """
        Zephyr Id : This will add fuel and Perform a postpay sale with loyalty configured.
                    This will swipe loyalty card on pinpad simulator.
                    It will check receipt for fuel and transaction loyalty rewards applied in sale
        Args: None
        Returns: None
        """

        # Rename loyalty 
        Loyalty_Check_Functions.rename_loyalty("Loyalty5","Kickback","Loyalty1")
        # Adding fuel having fuel grade Diesel 1
        pos.add_fuel(self.fuel_amount, mode="preset", grade=self.fuel_grade)

        # Check if fueling is completed
        pos.wait_for_fuel(timeout=60, verify=False)

        # Take fuel inside POS
        pos.click_suspended_transaction()

        # Perform Payment
        if not pos.click_function_key("pay", verify=False):
            return False

        # Loyalty1 Selection
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

        # Perform cash payment
        pos.pay()

        #Transaction amount after applying loyalty discounts
        fuel_price = self.fuel_amount.replace('$','')
        fuel_discount = float(fuel_price) * self.fuel_rewards
        fuel_amount = float(fuel_price) - fuel_discount
        total_price = (fuel_amount - self.trans_reward) 
        fuel_text = "$-"+ format(self.fuel_rewards,'0.3f') + "/GAL $-" + str(fuel_discount)
        
        # Check Rewards in the receipt
        if not pos.check_receipt_for([self.fuel_discount_text, fuel_text, "$" + str(total_price), self.trans_text]):
            tc_fail("Loyalty Rewards are not applied on the transaction")
            return False

        return True    

    @test
    def fuel_postpay_manual(self):
        """
        Zephyr Id : This will add fuel and Perform a postpay sale with loyalty configured .
                    This will enter loyalty card number manualy on pinpad simulator.
                    It will check receipt for fuel and transaction loyalty rewards applied in sale
        Args: None
        Returns: None
        """
        # Rename Loyalty 

        Loyalty_Check_Functions.rename_loyalty("Loyalty1","Kickback","Loyalty2")
        # Adding fuel having fuel grade Diesel 1
        pos.add_fuel(self.fuel_amount, mode="preset", grade=self.fuel_grade)

        # Check if fueling is completed
        pos.wait_for_fuel(timeout=60, verify=False)

        # Take fuel inside POS
        pos.click_suspended_transaction()

        # Perform Payment
        if not pos.click_function_key("pay", verify=False):
            return False

        # Loyalty2 Selection
        if "Select Loyalty Program or Cancel" in pos.read_status_line():
            pos.select_list_item("Kickback", verify=False)
            pos.click_keypad("ENTER", verify=False)
            pos.click_keypad("MANUAL", verify=False)
            self.log.info("Loyalty2 selected")
        else:
            tc_fail("Loyalty selection not available")
            return False    
        
        # Manual entry of loyalty2 card
        try:
            msg = pos.read_status_line()
            if "HAVE CUSTOMER ENTER KICKBACK ID" in msg.upper():
                pinpad.manual_entry(brand=system.get_brand(), card_name="Loyalty2")
            else:
                tc_fail("Loyalty2 not selected")
                return False
        except Exception as e:
            self.log.warning(f"Card swipe in pinpad failed. Exception: {e}")
            pos.click_keypad("CANCEL")
            return False

        # Peform cash payment
        pos.pay()

        #Transaction amount after applying loyalty discounts
        fuel_price = self.fuel_amount.replace('$','')
        fuel_discount = float(fuel_price) * self.fuel_rewards
        fuel_amount = float(fuel_price) - fuel_discount
        total_price = (fuel_amount - self.trans_reward) 
        fuel_text = "$-"+ format(self.fuel_rewards,'0.3f') + "/GAL $-" + str(fuel_discount)

        # Check Rewards in the receipt
        if not pos.check_receipt_for([self.fuel_discount_text, fuel_text, "$" + str(total_price), self.trans_text]):
            tc_fail("Loyalty Rewards are not applied in the transaction")
            return False

        return True 

    @test
    def fuel_carwash_dryStock_postpay(self):
        """
        Zephyr Id : This will add fuel with car wash 1 and drystock and Perform a postpay sale with loyalty configured .
                    It will check receipt for fuel, non-fuel and transaction loyalty rewards applied in sale.
        Args: None
        Returns: None
        """
        # Adding fuel having fuel grade Diesel 1
        pos.add_fuel(self.fuel_amount, mode="preset", grade=self.fuel_grade)
         
        # Check if fueling is completed
        pos.wait_for_fuel(timeout=60, verify=False)
      
        # Take fuel inside POS
        pos.click_suspended_transaction()

        # Add Dry Stock Item
        pos.add_item("002", method="PLU")
        
        # Add Car Wash Item
        pos.add_item("1234", method="plu", qualifier="CARWASH 1")
        
        if not pos.click_function_key("pay", verify=False):
            return False
        
        # Select Loyalty2
        if "Select Loyalty Program or Cancel" in pos.read_status_line():
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
        
        #Transaction amount after applying loyalty discounts
        fuel_price = self.fuel_amount.replace('$','')
        self.log.info(f"fuel price is {self.fuel_amount} replaced with {fuel_price}")
        fuel_discount = float(fuel_price) * self.fuel_rewards
        self.log.info(f"fuel discount is {fuel_discount} made from getting {self.fuel_rewards}")
        fuel_amount = float(fuel_price) - fuel_discount
        self.log.info(f"fuel amount is {fuel_amount} which is from subtracting {fuel_discount}")
        fuel_text = "$-"+ format(self.fuel_rewards,'0.3f') + "/GAL $-" + str(fuel_discount)
        self.log.info(f"text is {fuel_text}")
        nonfuel_Loyalty_Text = "$-" + str(self.nonfuel_reward)
        
        # Total amount is calculated as fuel sale amount + ( item2 amount - non-fuel reward) + carwash1 amount - transaction reward        
        total_price = round(((fuel_amount + (5.00 - self.nonfuel_reward) + 2.50) - self.trans_reward) , 2)
        
        # Check the rewards are applied on the receipt
        if not pos.check_receipt_for([self.fuel_discount_text, nonfuel_Loyalty_Text, fuel_text, "$" + str(total_price), self.trans_text]):
            tc_fail("Rewards are not applied on the transaction")
            return False

        return True    

    @test 
    def fuel_carwash_drystock_postpay_manual(self):
        """
        Zephyr Id : This will add fuel with car wash 1 and drystock and Perform a postpay sale with different loyalty card mask configured .
                    This will enter loyalty card number manualy on pinpad simulator.
                    It will check receipt for fuel, non-fuel and transaction loyalty rewards applied in sale.
        Args: None
        Returns: None
        """

        # Adding fuel having fuel grade Diesel 1
        pos.add_fuel(self.fuel_amount, mode="preset", grade=self.fuel_grade)
         
        # Check if fueling is completed
        pos.wait_for_fuel(timeout=60, verify=False)
       
        # Take fuel inside POS
        pos.click_suspended_transaction()

        # Add Dry Stock Item
        pos.add_item("002", method="PLU")
        
        # Add Car Wash Item
        pos.add_item("1234", method="plu", qualifier="CARWASH 1")
        
        if not pos.click_function_key("pay", verify=False):
            return False
        
        # Select Loyalty2
        if "Select Loyalty Program or Cancel" in pos.read_status_line():
            pos.select_list_item("Kickback", verify=False)
            pos.click_keypad("ENTER", verify=False)
            pos.click_keypad("MANUAL", verify=False)
            self.log.info("Loyalty2 selected")
        else:
            tc_fail("Loyalty selection not available")
            return False
            
        # Manual entry of loyalty2 card
        try:
            msg = pos.read_status_line()
            if "HAVE CUSTOMER ENTER KICKBACK ID" in msg.upper():
                pinpad.manual_entry(brand=system.get_brand(), card_name="Loyalty2")
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

        #Transaction amount after applying loyalty discounts
        fuel_price = self.fuel_amount.replace('$','')
        fuel_discount = float(fuel_price) * self.fuel_rewards
        fuel_amount = float(fuel_price) - fuel_discount
        fuel_text = "$-"+ format(self.fuel_rewards,'0.3f') + "/GAL $-" + str(fuel_discount)
        self.log.info(f"text is {fuel_text}")
        nonfuel_Loyalty_Text = "$-" + str(self.nonfuel_reward)
        
        # Total amount is calculated as fuel sale amount + ( item2 amount - non-fuel reward) + carwash1 amount - transaction reward
        total_price = round(((fuel_amount + (5.00 - self.nonfuel_reward) + 2.50) - self.trans_reward) , 2)
        
        # Check the rewards are applied on the receipt
        if not pos.check_receipt_for([self.fuel_discount_text, nonfuel_Loyalty_Text, fuel_text, "$" + str(total_price), self.trans_text]):
            tc_fail("Rewards are not applied on the transaction")
            return False

        return True 
    
    @test
    def dry_stock_loyalty_postpay(self):
        """
        Zephyr Id : This will add drystock and Perform a postpay sale with loyalty configured .
                    It will check receipt non-fuel and transaction loyalty rewards applied in sale.
        Args: None
        Returns: None
        """
        # Rename Loyalty
        Loyalty_Check_Functions.rename_loyalty("Loyalty2","Kickback","Loyalty1")
        # Add Dry Stock Item
        pos.add_item("002", method="PLU")

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

        # Let's add logic to handle optional drystock reward
        message = pos.read_message_box(5)
        if message and ("Reward?" in pos.read_message_box(5)):
            pos.click_message_box_key("YES")

        # Perform cash payment
        pos.pay()

        #Transaction amount after applying loyalty discounts
        nonfuel_Loyalty_Text = "$-" + str(self.nonfuel_reward)
        
        total_price = round((5.00 - self.nonfuel_reward)- self.trans_reward)

        # Check the rewards are applied on the receipt
        if not pos.check_receipt_for([nonfuel_Loyalty_Text, "$" + str(total_price), self.trans_text]):
            tc_fail("Rewards are not applied on the transaction")
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
        