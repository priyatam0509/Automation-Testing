"""
    File name: EL_PaymentTest.py
    Tags:
    Description: 
    Author: 
    Date created: 2019-07-24 15:12:07
    Date last modified: 
    Python Version: 3.7
"""

import logging, time
from app import Navi, mws, pos, system, checkout, console, networksim
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app import pinpad
from app.simulators import ip_scanner

log = logging.getLogger()

def suspend_transaction():
    """
    Suspends the current transaction from the CCC.
    """
    
    console.connect()
    time.sleep(2)
    if console._get_text("//*[@id='terminal_list']/div/div[4]/div/div[2]") != "In Transaction":
        console.click_function_key("In Transaction")
    if console.is_element_present("//button[starts-with(@class, 'funcButton') and contains(text(), 'Suspend Transaction')]"):
        log.info("Suspending the transaction.")
        console.click("Suspend Transaction")
    console.close()

class EL_PaymentTest():
    """
    Description: A test case for checking most of the ways to tender out in Express Lane.
    """

    def __init__(self):
        """Initializes the Template class.
        Args: None
        Returns: None
        """
        # The logging object. 
        # Example: log.info(f"Current value of var: {my_var}")

    @setup
    def setup(self):
        # Attempt to start Self Checkout
        # Might need to remove and manage connections as part of suites
        log.info("Connecting to Express Lane...")
        checkout.prompt_timeout = 0.3
        if not checkout.connect():
            tc_fail("Unable to connect to Express Lane")
        

    def setupTransaction(self, welcome=True):
        # helper to setup a basic transaction
        try:
            if welcome:
                checkout.click_welcome_key("Start", timeout=10)
            checkout.enter_plu("002")
        except Exception as e:
            log.warning(f"ERROR PREPARING TRANSACTION:\n{e}")
            raise

    def handleMessages(self):
        # helper to check for messages sent after payment fails
        eMsg = checkout.read_message_box()
        if (eMsg):
            checkout.click_message_box_key("OK")
            tc_fail(f"Unexpected message: {eMsg}")

    @test
    def testDebitTender(self):
        """Perform a basic transaction with debit."""
        self.setupTransaction()
        if not checkout.pay_card(card_name='Debit'):
            tc_fail("Failed to pay with debit tender")
        # This is an attempt to prevent PHYK-85 from happening
        self.setupTransaction()
        if not checkout.pay_card(card_name='Debit'):
            tc_fail("Failed to pay with debit tender")
        self.handleMessages()
    
    @test
    def testAmexTender(self):
        """Perform a basic transaction with American Express Credit."""
        self.setupTransaction()
        if not checkout.pay_card(card_name='AmEx'):
            tc_fail("Failed to pay with AmEx credit tender")
        self.handleMessages()

    @test
    def testDiscTender(self):
        """Perform a basic transaction with Discover Credit."""
        self.setupTransaction()
        if not checkout.pay_card(card_name='Discover'):
            tc_fail("Failed to pay with Discover credit tender")
        self.handleMessages()

    @test
    def testExpiredMCTender(self):
        """Attempts a transaction with an expired MasterCard Credit."""
        self.setupTransaction()
        checkout.pay_card(card_name='Expired_MC', verify=False)
        eMsg = checkout.read_message_box(timeout=10)
        if (eMsg):
            checkout.click_message_box_key("OK")
            if "Expired" not in eMsg:
                tc_fail("Expired message not found for MasterCard")
        else:
            tc_fail("Expired MasterCard was accepted")
            
    @test
    def testMCTender(self):
        """Perform a basic transaction with MasterCard Credit."""
        self.setupTransaction(welcome=False)
        if not checkout.pay_card(card_name='MasterCard'):
            tc_fail("Failed to pay with MasterCard Credit Tender")
        self.handleMessages()

    @test
    def testExpiredVisaTender(self):
        """Attempts a transaction with an expired Visa Credit."""
        self.setupTransaction()
        checkout.pay_card(card_name='Expired_Visa', verify=False)
        eMsg = checkout.read_message_box(timeout=10)
        if (eMsg):
            checkout.click_message_box_key("OK")
            if "Expired" not in eMsg:
                tc_fail("Expired message not found for Visa")
        else:
            tc_fail("Expired Visa was accepted")
            
    @test
    def testVisaTender(self):
        """Perform a basic transaction with Visa Credit."""
        self.setupTransaction(welcome=False)
        if not checkout.pay_card(card_name='Visa'):
            tc_fail("Failed to pay with Visa Credit Tender")
        self.handleMessages()

    @test
    def testGiftCardTender(self):
        """Perform a basic transaction with a GiftCard."""
        self.setupTransaction()
        log.info(f"Using brand: {system.get_brand()}")
        
        # Add balance to gift card
        gift_card = pinpad._get_card_data(
            brand=system.get_brand(),
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
        if not checkout.pay_card(
            brand=system.get_brand(),
            card_name="GiftCard"
        ):
            tc_fail("Unable to pay out with Gift Card")
        self.handleMessages()

    @teardown
    def teardown(self):
        checkout.close()
        # Suspend Transaction if any test case is fail due to payment issue
        suspend_transaction()

