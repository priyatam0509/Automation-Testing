"""
    File name: PriceCheck_POS.py
    Tags:
    Description: 
    Author: 
    Date created: 2020-02-28 06:58:38
    Date last modified: 
    Python Version: 3.7
"""

import logging, time
from app import Navi, mws, pos, system
from app.framework.tc_helpers import setup, test, teardown, tc_fail

default_timeout = 3

class PriceCheck_POS():
    """
    Description: Test class that provides an interface for testing.
    """

    def __init__(self):
        """
        Initializes the Template class.
        """
        self.log = logging.getLogger()
        

    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        """
        #if not system.restore_snapshot():
        #    self.log.debug("No snapshot to restore, if this is not expected please contact automation team")
        if not pos.connect():
            self.tc_fail("Failed to connect to POS")
        self.recover()

    @test
    def test_basicNoSalePC(self):
        """
        Confirms we can do a basic price check without selling or entering a transaction.
        Chooses item via speedkey.
        """
        # Basic price check
        self.log.info("Price checking Generic Item via speedkey")
        pos.click("Price Check")
        pos.click_speed_key("Generic Item")
        
        # Confirm the right item, at the right price
        self.read_price_check("Generic Item", "$0.01")
        # Don't add the item
        pos.click("Ok")
        
        # Confirm we aren't in a transaction
        if self.in_transaction():
            self.tc_fail("Unintentionally In Transaction")
        else:
            self.log.info("Confirmed we are not in a transaction")
            
        # Setup for next test
        self.recover()
        
    @test
    def test_basicSalePC(self):
        """
        Confirms we can do a basic price check while selling an item.
        Chooses item via speedkey.
        """
        # Basic price check
        self.log.info("Price checking Generic Item via speedkey")
        pos.click("Price Check")
        pos.click_speed_key("Generic Item")
        
        # Confirm the right item, at the right price
        self.read_price_check("Generic Item", "$0.01")
        # Add the item
        pos.click("Sell Item")
        
        # Confirm we added the item
        ret = self.confirm_line(-1, "Generic Item", "$0.01")
        if ret == True:
            self.log.info("Confirmed item added")
        else:
            self.tc_fail(ret)
            
        # Setup for next test
        self.recover()
        
    @test
    def test_PriceCheckPLU(self):
        """
        Confirm items can be price checked using PLU
        """
        # Basic price check
        self.log.info("Price checking Generic Item via PLU")
        pos.click("Price Check")
        pos.enter_keypad("1", after="enter")
        
        # Confirm the right item, at the right price
        self.read_price_check("Generic Item", "$0.01")
        # Don't add the item
        pos.click("Ok")
        
        # Confirm we aren't in a transaction
        if self.in_transaction():
            self.tc_fail("Unintentionally In Transaction")
        else:
            self.log.info("Confirmed we are not in a transaction")
            
        # Setup for next test
        self.recover()

    @test
    def test_NegativePriceCheck(self):
        """
        Confirms we can price check a negative item
        """
        # Basic price check
        self.log.info("Price checking Negative Item via speedkey")
        pos.click("Price Check")
        pos.click_speed_key("Negative Item")
        
        # Confirm the right item, at the right price
        # NOTE: Price check returns negative prices as possitive. Legacy defect deemed 'Will Not Fix'
        self.read_price_check("Negative Item", "$5.00")
        # Add the item
        pos.click("Sell Item")
        
        # Confirm we are in a transaction
        if not self.in_transaction():
            self.tc_fail("POS did not start a transaction; can not confirm item was added")
        else:
            self.log.info("Confirmed we are in a transaction")
            
        # Confirm we added the item, and that it was negative
        ret = self.confirm_line(-1, "Negative Item", "-$5.00")
        if ret == True:
            self.log.info("Confirmed item added")
        else:
            self.tc_fail(ret)
            
        # Setup for next test
        self.recover()
        
    @test
    def test_LinkedPriceCheck(self):
        """
        Confirms that adding a linked item via price check adds both items.
        """
        # Basic price check
        self.log.info("Price checking Linked Item 1 via PLU")
        pos.click("Price Check")
        pos.enter_keypad("014", after="enter")
        
        # Confirm the right item, at the right price
        self.read_price_check("Linked Item 1", "$1.00")
        # Add the item
        pos.click("Sell Item")
        
        # Confirm we are in a transaction
        if not self.in_transaction():
            self.tc_fail("POS did not start a transaction; can not confirm item was added")
        else:
            self.log.info("Confirmed we are in a transaction")
            
        # Confirm we added the item
        ret = self.confirm_line(-2, "Linked Item 1", "$1.00")
        if ret == True:
            self.log.info("Confirmed item added")
        else:
            self.tc_fail(ret)
            
        # Confirm we added the linked item
        ret = self.confirm_line(-1, "Linked Item 2", "$1.00")
        if ret == True:
            self.log.info("Confirmed item added")
        else:
            self.tc_fail(ret)
            
        # Setup for next test
        self.recover()

    @test
    def qualified_item(self):
        """
        Test price check for qualified items
        """
        # Price check with base item
        self.log.info("Price checking Qual 1 via PLU")
        pos.click("Price Check")
        pos.enter_keypad("030", after='enter')
        if self.selection_list_visible():
            pos.select_list_item("Qual 1 ($5.00)")
            pos.click("enter")
        else:
            tc_fail("Selection list didn't appear.")

        # Confirm the right item, at the right price
        self.read_price_check("Qual 1", "$5.00")
        # Add the item
        pos.click("Sell Item")

        # Price check with qualifier
        self.log.info("Price checking Qual 1 via PLU")
        pos.click("Price Check")
        pos.enter_keypad("030", after='enter')
        if self.selection_list_visible():
            pos.select_list_item("Test Type ($10.00)")
            pos.click("enter")
        else:
            tc_fail("Selection list didn't appear.")

        # Confirm the right item, at the right price
        self.read_price_check("Qualifier 1", "$10.00")
        # Add the item
        pos.click("Sell Item")

        # Confirm we are in a transaction
        if not self.in_transaction():
            self.tc_fail("POS did not start a transaction; can not confirm item was added")
        else:
            self.log.info("Confirmed we are in a transaction")
            
        # Confirm we added the item
        ret1 = self.confirm_line(-2, "Qual 1", "$5.00")
        if ret1:
            self.log.info("Confirmed Qual 1 item added")
        else:
            self.tc_fail(ret1)
            
        # Confirm we added the linked item
        ret2 = self.confirm_line(-1, "Qualifier 1", "$10.00")
        if ret2:
            self.log.info("Confirmed Qualifier 1 item added")
        else:
            self.tc_fail(ret2)
            
        # Setup for next test
        self.recover()
        
    @test
    def test_inTransSalePC(self):
        """
        Repeats test_basicSalePC test, starting from an in Transaction state.
        """
        # Start a transasction
        pos.click_speed_key("Generic Item")
        
        # Void the item to an empty transaction
        # NOTE: Should uncomment this when related defect is fixed (likely in MERLIN-1335)
        #pos.click("Void item")
        
        # Repeat earlier test
        self.test_basicSalePC()

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        pos.close()
        
    def read_price_check(self, item_name, item_price):
        """
        Helper function that reads the price check message.
        Returns true if it matches provided information.
        Throws TC_FAIL if an issue is detected.
        """
        msg = pos.read_message_box()
        self.log.info(f"Message received: [{msg}]")
        if not msg:
            self.tc_fail("Did not receive price check prompt")
        if not item_name.lower() in msg.lower():
            self.tc_fail(f"Did not find correct item [{item_name}] in message")
        if not item_price.lower() in msg.lower():
            self.tc_fail(f"Did not find correct price [{item_price}] in message")
        return True
        
    def confirm_line(self, line_num, item_name, item_price):
        """
        helper function to confirm that an item was added to the transaction with the correct price
        Returns True if the correct information is matched
        Returns the reason for failure as a string otherwise
        """
        items = pos.read_transaction_journal()
        # Index out of bounds - handles positive and negative indexing
        if line_num >= len(items) or abs(line_num) > len(items):
            return f"Target line [{line_num}] is greater than number of items [{len(items)}]"
        # Check item name
        if items[line_num][0].lower() != item_name.lower():
            return f"Target item name [{item_name}] did not match found [{items[line_num][0]}]"
        # Check item price
        if items[line_num][1].lower() != item_price.lower():
            return f"Target item price [{item_price}] did not match found [{items[line_num][1]}]"
        # No issues - so must be right
        return True
        
    def in_transaction(self):
        """
        Helper function return true if we believe we are in a transaction, false otherwise.
        """
        # We likely just changed data - give it a second to catch up
        time.sleep(0.1) # I think I keep reading journal watermark too soon without this
        
        # Get relevant data
        water_mark = pos.read_journal_watermark()
        self.log.info(f"Watermark: [{water_mark}]")
        balance = pos.read_balance()['Total']
        self.log.info(f"Balance: [{balance}]")
        
        # Decide if we need more checks based on watermark
        if water_mark == "TRANSACTION IN PROGRESS":
            self.log.info("In Transaction: In Transaction Watermark found")
            return True
        elif water_mark == "TRANSACTION COMPLETE" or water_mark == "TRANSACTION VOIDED":
            self.log.info("Not in Transaction: Transaction Complete/Voided watermarks found")
            return False
        else:
            # No watermark - decide based on balance
            if balance == "$0.00":
                self.log.info("Not in Transaction: $0 balance with no watermark")
                return False
            else:
                self.log.info("In Transaction: Non-$0 balance with no watermark")
                return True

    def selection_list_visible(self, timeout=default_timeout):
        """
        Helper function to determine whether the selection list is visible
        """
        return pos.read_list_items(timeout=timeout)
        
    def recover(self, repeat=True):
        """
        Helper function to try and get back to a nuetral idle state
        """
        posStateEnum = { 
            0 : "LoggedOff",
            1 : "Idle",
            2 : "Transaction",
            3 : "Tendering",
            4 : "TransactionComplete",
            5 : "PayingOutPrepay",
            8 : "OptionReload",
            "LoggedOff" : 0,
            "Idle" : 1,
            "Transaction" : 2,
            "Tendering" : 3,
            "TransactionComplete" : 4,
            "PayingOutPrepay" : 5,
            "OptionReload" : 8
        }
        self.log.info("Attempting to get to a neutral transaction state.")
        pos_state = pos.driver.execute_script("return posState")
        # Solves a small possible timing issue when first connecting - no impact otherwise
        start_time = time.time()
        while not pos_state and (time.time() - start_time < 20): 
            self.log.warning("pos_state not received")
            time.sleep(.5)
            pos.driver.execute_script("return posState")
        
        # Handle any popups
        if pos_state['ActivePrompt']:
            msg = pos.read_message_box()
            self.log.warning(f"Unhandled message during recovery: [{msg}]")
            pos.click("Ok", verify=False)
        
        # Try to get to an idle state
        self.log.info(f"posState.TransactionState: [{pos_state['TransactionState']}]")
        if pos_state['TransactionState'] == posStateEnum['LoggedOff']:
            # Attempt to sign on
            self.log.info("Not signed in - signing on")
            pos.sign_on()
        elif pos_state['TransactionState'] == posStateEnum['Idle']:
            # We're good - continue on
            self.log.info("POS Idle")
            return
        elif pos_state['TransactionState'] == posStateEnum['Transaction']:
            # Try to void the transaction
            self.log.info("In transaction - voiding")
            pos.void_transaction()
        else:
            self.log.warning("Unhandled posState. Recovery not attempted.")
            
        # If we're here, we weren't Idle, so try again one more time
        if repeat:
            self.recover(repeat=False)
        
    def tc_fail(self, msg):
        """
        replacement TC_FAIL to try to get back to a neutral state before failing
        """
        self.recover()
        tc_fail(msg)
