"""
    File name: sco_transactions.py
    Tags:
    Description: 
    Author: 
    Date created: 2019-05-09 13:31:37
    Date last modified: 
    Python Version: 3.7
"""

import logging, time
from app import system, pinpad, networksim, checkout, console, initial_setup
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from Scripts.features import EL_PaymentTest

class sco_transactions():
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
        self.checkout = checkout
        self.console = console
        self.brand = system.get_brand()

        self.init_setup = initial_setup.Initial_setup("express")
    
    @setup
    def setup(self):
        """
        Launches Chrome browser and opens up SCO
        Args: None
        Returns: None
        """
        pass

    @test
    def add_items(self):
        """
        Adds Items to basket and pays out using Credit card.
        Args: None
        Returns: None
        """
        self.checkout.connect()
        time.sleep(2)
        self.checkout.click_welcome_key("Start")

        self.checkout.click_speed_key("Item 3")
        if not self.checkout.pay_card(
            brand='Core',
            card_name='Visa'
        ):
            tc_fail("Unable to pay out transaction")

    @test
    def add_plu(self):
        """
        Adds Items using PLU and pays out using Credit card.
        Args: None
        Returns: None
        """
        
        self.checkout.click_welcome_key("Start")

        # Adding items via PLU
        self.checkout.enter_plu("005")
        self.checkout.enter_plu("005")
        
        # Paying out transaction with Debit
        if not self.checkout.pay_card(
            brand='Core',
            card_name='Debit',
            debit_fee=True,
            cashback_amount='10.00'
        ):
            tc_fail("Unable to pay out transaction")

    @test
    def gift_card_transaction(self):
        """
        Add 3 Item 3's and pay out using Gift Card
        """
        self.checkout.click_welcome_key("Start")

        # Adding items to basket
        i = 0
        while i < 3:
            self.checkout.enter_plu("003")
            i += 1
        
        # Add balance to gift card
        gift_card = pinpad._get_card_data(
            brand=self.brand,
            card_name='GiftCard'
        )
        account_number = gift_card["Track2"].split("=")[0]

        if not networksim.set_prepaid_manager(
                account_number=account_number,
                active=True,
                preauth_amount="10.00",
                balance_amount="100.00",
                activation_amount="5.00"
            )['success']:
            tc_fail(f"Unable to update balance for Gift Card: {account_number}")

        # Paying out with GiftCard
        if not self.checkout.pay_card(
            brand=self.brand,
            card_name="GiftCard"
        ):
            tc_fail("Unable to pay out with Gift Card")
    
    @test
    def read_weights(self):
        """
        Reading Weights and Measures
        """
        self.checkout.click_welcome_key("Start")
        self.checkout.click_function_key("Help")
        self.checkout.click_help_key("Weights and Measures")
        weights = self.checkout.read_weights_and_measures()
        self.log.info(f"Weights and Measures: {weights}")
        self.checkout.click_weights_measures_key("Back")
    
    @test
    def request_assistance(self):
        """
        Click on the Help button and request assistance
        """

        self.checkout.click_function_key("Help")
        self.checkout.click_help_key("Request Assistance")
        eMsg = checkout.read_message_box()
        if (eMsg):
            checkout.click_message_box_key("OK")
        self.checkout.close()
        self.console.connect()
        self.console.click_function_key("Dismiss")
        self.console.close()
        
        
    @teardown
    def teardown(self):
        
        # Reset PIN Pad (this will clear out the Queue on Server side)
        pinpad.reset()

        # Suspend Transaction if any test case is fail due to payment issue
        EL_PaymentTest.suspend_transaction()