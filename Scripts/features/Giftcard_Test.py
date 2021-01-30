"""
    File name: Giftcard_Test.py
    Tags:
    Description: [PEACOCK-3717] This will add Cash Card item and activate / recharge it
    Pre-Requisite : Make sure that giftcard is not-active and card balance is 0.00
    Author: Asha Sangrame
    Date created: 2020-1-28 14:53:24
    Date last modified: 
    Python Version: 3.7
"""


import logging
from app import Navi, mws, pos, system, pinpad, item
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class Giftcard_Test():
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

        self.cashcard_plu = "12345"

        self.desired_amount = "$30.00"

    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        pass

    @test
    def activate_giftcard1(self):
        """
        Zephyr Id : This will activate gift card item for value pre-denominated(default value) and
                    Verify on receipt that card is activated
        Args: None
        Returns: None
        """        
        #Navigate to POS screen
        Navi.navigate_to("POS")
        
        # Sign on to POS screen if not already sign-on
        pos.sign_on()

        # Add cash card item 
        if not pos.add_item(self.cashcard_plu, method="plu", cash_card_action="Activate"):
            tc_fail("Not able to add cash card")

        if not pos.pay(cash_card="GiftCard1"):
            tc_fail("Not able to activate giftcard")        

        # Verify receipt
        if not pos.check_receipt_for(["CARD ACTIVATED", "ACTIVATION AMOUNT: $10.00"]):
            tc_fail("Activation message not came on receipt")

        return True

    @test
    def recharge_giftcard(self):
        """
        Zephyr Id : This will recharge gift card and verift receipt for 'CARD RECHARGED' text
        Args: None
        Returns: None
        """        
        #Navigate to POS screen
        Navi.navigate_to("POS")
        
        # Sign on to POS screen if not already sign-on
        pos.sign_on()

        # Add cash card item 
        if not pos.add_item(self.cashcard_plu, method="plu", price=self.desired_amount, cash_card_action="Recharge"):
            tc_fail("Not able to add cash card")

        if not pos.pay(cash_card="GiftCard1"):
            tc_fail("Not able to recharge giftcard")    
        
        # Verify receipt
        if not pos.check_receipt_for("CARD RECHARGED"):
            tc_fail("Message not came on receipt")

        return True

    @test
    def activate_giftcard2(self):
        """
        Zephyr Id : This will activate giftcard for value non-denominated(user required value) and
                    Verify on receipt that card is activated
        Args: None
        Returns: None
        """              
        #Navigate to POS screen
        Navi.navigate_to("POS")
        
        # Sign on to POS screen if not already sign-on
        pos.sign_on()

        # Add cash card item 
        if not pos.add_item(self.cashcard_plu, method="plu", price=self.desired_amount, cash_card_action="Activate"):
            tc_fail("Not able to add cash card")

        if not pos.pay(cash_card="GiftCard1"):
            tc_fail("Not able to activate giftcard")    

        #Verify receipt
        if not pos.check_receipt_for(["CARD ACTIVATED", "ACTIVATION AMOUNT:"]):
            tc_fail("Activation message not came on receipt")

        return True

    @test
    def verify_balance(self):
        """
        Testlink Id : This will verify balance on gift card
        Args: None
        Returns: None
        """              
        #Navigate to POS screen
        Navi.navigate_to("POS")
        
        # Sign on to POS screen if not already sign-on
        pos.sign_on()

        # navigate to balance request screen
        pos.click_function_key("MORE", timeout=3, verify=False)
        pos.click_function_key("NETWORK", timeout=3, verify=False)
        pos.click_function_key("BALANCE REQUEST", timeout=3, verify=False)

        #Swipe gift card for recharge    
        pinpad.swipe_card(system.get_brand(), card_name="GiftCard1")

        #Verify receipt
        if not pos.check_receipt_for("CARD BALANCE: $70.00"):
            tc_fail("Card balance not correct")

        return True

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        pass