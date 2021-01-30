"""
    File name: Prepay_Giftcard.py
    Tags:
    Description: [PEACOCK-3717] This will perform Fuel, Dry Stock and car wash PrePay sale with Giftcard.
                 After sale this will verify receipt for sale amount and gift card payment.
    Pre-requisite: Giftcard should be active and it should have balance more than sale amount
    Author: Asha Sangrame
    Date created: 2020-1-30 14:53:24
    Date last modified: 
    Python Version: 3.7
"""


import logging, time
from app import Navi, pos, system, pinpad
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class Prepay_Giftcard():
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

        self.fuel_amount = "$3.00"

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

    def check_balance(self):
        """
        This is helper method. This will retrieve balance on gift card
        Args: None
        Returns: (float) Card balance
        """
        # navigate to balance request screen
        pos.click_function_key("MORE", timeout=3, verify=False)
        pos.click_function_key("NETWORK", timeout=3, verify=False)
        pos.click_function_key("BALANCE REQUEST", timeout=3, verify=False)

        #Swipe gift card for recharge    
        pinpad.swipe_card(brand=system.get_brand(), card_name="GiftCard1")

        # Chcek receipt for balance
        pos.click_function_key("SEARCH", verify=False)
        pos.select_receipt(1)
        actual_rcpt = pos.read_receipt()
        card_balance = actual_rcpt[len(actual_rcpt)-2]
        card_balance = float(card_balance[16:])
        self.log.info(f"Card balance is {card_balance}")
        pos.click_receipt_key("CANCEL", verify=False)

        return card_balance

    @test
    def fuel_prepay(self):
        """
        Zephyr Id : This will add fuel and Perform a prepay sale with Giftcard.
                    It will check receipt for gift card payment and sale amount.
        Args: None
        Returns: None
        """
        # Retrieve before sale card balance of giftcard
        before_sale_balance = self.check_balance()

        #wait for dispenser to be Ready
        if not pos.wait_disp_ready(idle_timeout=60):
            return False
        
        # Adding fuel having fuel grade Diesel 1
        pos.add_fuel(self.fuel_amount, grade=self.fuel_grade)
       
        # Perform card Payment with Gift card
        pos.pay_card(brand=system.get_brand(), card_name='GiftCard1')

        # Wait until dispenser 1 is idle
        if not pos.wait_for_disp_status('IDLE'):
            return False

        #Calculate sale amount
        total = self.fuel_amount
        
        strTotal = "Total=" + total

        # Check receipt for sale amount
        if not pos.check_receipt_for([strTotal, "PREPAID"]):
           tc_fail("Required text is not present on receipt")
           return False

        # Check card balance after sale
        after_sale_balance = self.check_balance()

        # verify balance
        sale_amount = float(self.fuel_amount.replace('$',''))

        verify_balance = before_sale_balance - sale_amount

        if not (verify_balance == after_sale_balance):
            tc_fail("card balance not correct after sale")

        return True

    @test
    def fuel_carwash_drystock(self):
        """
        Zephyr Id : This will add fuel, dry stock and car wash and Perform a prepay sale with Giftcard.
                    Also it will check receipt for gift card payment and sale amount                    
        Args: None
        Returns: None
        """
        # Retrieve before sale card balance of giftcard
        before_sale_balance = self.check_balance()
        
        # Add fuel 
        pos.add_fuel(self.fuel_amount, grade=self.fuel_grade) 
        
        # Add Car Wash Item
        pos.add_item("1234", method="plu", qualifier="CARWASH 2")

        # Add Drystock item. Default is Generic item
        pos.add_item(item="ITEM 2")

        # Perform card Payment with gift card
        pos.pay_card(brand=system.get_brand(), card_name='GiftCard1')  

        # Wait until dispenser 1 is idle
        if not pos.wait_for_disp_status('IDLE'):
            return False
        
        #Calculate sale amount. Fuel amount(3.00) + Generic item amount(0.01) + carwash amount(2.50)
        fuel_amount = self.fuel_amount.split('$')
        total = float(fuel_amount[1]) + 5.00 + 4.00
        
        strTotal = "Total=$" + str(total)

        # Check receipt for sale amount
        if not pos.check_receipt_for([strTotal, "PREPAID"]):
           tc_fail("Sale amount is not present on receipt")
           return False

        # Check card balance after sale
        after_sale_balance = self.check_balance()

        # verify balance
        verify_balance = before_sale_balance - total

        if not (verify_balance == after_sale_balance):
            tc_fail("card balance not correct after sale")

        return True

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        pass