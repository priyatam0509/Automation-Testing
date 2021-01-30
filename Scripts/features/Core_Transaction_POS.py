"""
    File name: Core_Transaction_POS.py
    Tags:
    Description: Test file for miscellaneous tests for functions core to POS's ability to perform transactions.
    i.e. voic item, add item, change quantity, change price. Tests using these more related to specific features
    should be in test files for those features.
    Author: Gene Todd
    Date created: 2020-01-24 12:55:12
    Date last modified: 
    Python Version: 3.7
"""

# NOTE: Test should be supported by edge as well as htmlPOS. Tested on htmlPOS, unconfirmed for Edge.
# Test is predicated on functioning pos.close() and pos.click_journal_item() functions.

import logging, time
from app import Navi, mws, pos, system
from app.framework.tc_helpers import setup, test, teardown, tc_fail

default_timeout = 5

class Core_Transaction_POS():
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
        # if not system.restore_snapshot():
            # self.log.debug("No snapshot to restore, if this is not expected please contact automation team")
            
        self.log.info("Connecting to POS")
        pos.connect()
        self.log.info("Attempting to sign on")
        pos.sign_on()
        self.log.info("Waiting for an idle state")
        if not _wait_for_trans_state("Idle"):
            self.log.warning("Failed to confirm Idle state. Tests may not run as expected")
        
    @test
    def test_basicTrans(self):
        """
        Test for a basic transaction; adding an item, then paying out the transaction.
        """
        pos.click_speed_key("Generic Item")
        self._confirmTotal(1)
        self._clearTrans()
    
    @test
    def test_basicVoid(self):
        """
        Test for basic void functionality
        """
        # Add 2 items, void 1
        self.log.info("Adding 2 Generic Items")
        pos.click_speed_key("Generic Item")
        pos.click_speed_key("Generic Item")
        self.log.info("Voiding last item")
        pos.click_function_key("Void Item")
        
        # Confirm there is only 1 item in the basket
        item_count = pos.read_balance()['Basket Count']
        self.log.info(f"Basket count is: [{item_count}]")
        if int(item_count) != 1:
            self._clearTrans()
            tc_fail("More than 1 item in transaction. Item not voided")
            
        self._clearTrans()
        
    @test
    def test_voidTarget(self):
        """
        Confirms void affects the selected item
        """
        # Add 5 items of different prices
        tracked_total = 0
        for i in range(1,6):
            self.log.info(f"Adding Item [{i}]")
            pos.click_speed_key("Item 1")
            pos.enter_keypad(i, after="Enter")
            tracked_total = tracked_total + i
            
        # Use different prices to determine who we voided
        # Void Item 3 and confirm
        self.log.info("Voiding item 3")
        pos.click_journal_item(instance=3)
        pos.click_function_key("Void Item")
        tracked_total = tracked_total - 3 # Item 3 should be $0.03
        # Check that item has been voided
        if not self._number_of_items(4):
            pos.void_transaction()
            tc_fail("Item 3 was not successfully voided.")
        self._confirmTotal(tracked_total)
        
        # Void Item 5 and confirm
        self.log.info("Voiding item 5")
        pos.click_journal_item(instance=4) # Former item 5 is now 4th in list
        pos.click_function_key("Void Item")
        tracked_total = tracked_total - 5 # Item 5 should be $0.05
        # Check that item has been voided
        if not self._number_of_items(3):
            pos.void_transaction()
            tc_fail("Item 5 was not successfully voided.")
        self._confirmTotal(tracked_total)
        
        # Void Item 1 and confirm
        self.log.info("Voiding item 1")
        pos.click_journal_item(instance=1)
        pos.click_function_key("Void Item")
        tracked_total = tracked_total - 1 # Item 1 should be $0.01
        # Check that item has been voided
        if not self._number_of_items(2):
            pos.void_transaction()
            tc_fail("Item 1 was not successfully voided.")
        self._confirmTotal(tracked_total)
        
        self._clearTrans()
    
    @test
    def test_voidAll(self):
        """
        Makes sure you can safely void all items in a transaction
        """
        # Add 2 items
        self.log.info("Add 2 items to transaction")
        pos.click_speed_key("Generic Item")
        pos.click_speed_key("Generic Item")
        # Void both items
        self.log.info("Voiding all item")
        pos.click_function_key("Void Item")
        pos.click_function_key("Void Item")
        if pos.read_message_box(1):
            pos.click('ok')
            pos.click_function_key("Void Item")
        # Check that all items have been voided
        if not self._number_of_items(0):
            pos.void_transaction()
            tc_fail("Not all items were successfully voided.")
        # Confirm 0 items
        self._confirmTotal(0)
        # Confirm PAY is disabled
        if pos.click_function_key("Pay", verify=False):
            tc_fail("Pay was enabled with 0 item")
        else:
            self.log.info("Confirmed pay button was not enabled")
        # Void Transaction
        self.log.info("Clearing Transaction")
        pos.void_transaction(reason="Cashier Error")
       
    @test
    def test_changeQuantity(self):
        """
        Confirm we can change item quantity normally
        """
        self.log.info("Adding item")
        pos.click_speed_key("Generic Item")
        self.log.info("Changing quantity")
        pos.click_function_key("Change Item Qty")
        pos.enter_keypad(2, after="Enter")
        self._confirmTotal(2)
        
        self._clearTrans()
        
    @test
    def test_zeroQuantity(self):
        """
        Confirm we can not set item quantity to 0
        """
        self.log.info("Adding item")
        pos.click_speed_key("Generic Item")
        self.log.info("Changing quantity")
        pos.click_function_key("Change Item Qty")
        pos.enter_keypad(0, after="Enter")
        self._confirmMessage("Please enter a non zero value for the quantity.")
        
        self._clearTrans()
        # Possibly to do with clearing a prompt right before, but pay takes longer than we wait.
        # Sleeping a small bit to avoid impacting next test
        time.sleep(1)
        
    # if a linked items test comes to be, this should probably be in there instead
    @test
    def test_linkedQuantity(self):
        """
        Confirm linked items change quantity together, and only the base item can be changed
        """
        self.log.info("Adding linked item")
        pos.enter_plu("014")
        
        # Make sure we can't change the second item
        self.log.info("Changing linked item's quantity")
        pos.click_function_key("Change Item Qty")
        self._confirmMessage("Unable to change quantity on a linked item.")
        
        # Make sure changing the first updates the second
        self.log.info("Changing base item's quantity")
        pos.click_journal_item(instance=1)
        pos.click_function_key("Change Item Qty")
        pos.enter_keypad(2, after="Enter")
        item_count = pos.read_balance()['Basket Count']
        self.log.info(f"Basket count is: [{item_count}]")
        if int(item_count) != 4:
            self._clearTrans()
            tc_fail("Unexpected number of items in basket")
            
        self._clearTrans()
        
    @test
    def test_changePrice(self):
        """
        Confirm we can change item price normally
        """
        self.log.info("Adding item")
        pos.click_speed_key("Generic Item")
        self.log.info("Changing price")
        pos.click_function_key("Override")
        # If reasoncodes, ignore and accept default
        pos.enter_keypad(2, after="Enter")
        self._confirmTotal(2)
        
        self._clearTrans()
        
    @test
    def test_basicRefund(self):
        """
        Verifies we can perform a basic refund
        """
        self.log.info("Refunding a generic item")
        pos.click_function_key("Refund")
        pos.click_speed_key("Generic Item")
        self._confirmTotal(1)
        
        self._clearTrans()
        
    @test
    def test_suspendTransaction(self):
        """
        Verifies that we can suspend and resume a transaction without issue
        """
        self.log.info("Adding Item 1 for $3.21")
        pos.click("Item 1")
        pos.enter_keypad(321, after="Enter")
        
        self.log.info("Suspending transaction")
        pos.click("Suspend Transaction")
        msg = pos.read_message_box()
        if not msg or not "suspend the transaction?" in msg:
            tc_fail("Prompt for suspend transaction not found")
        pos.click("Yes")
        
        self.log.info("Confirming transaction was suspended")
        # Confirm the watermark
        if not pos.read_journal_watermark() == "TRANSACTION SUSPENDED":
            tc_fail("Suspend transaction watermark not found")
        self.log.info("Watermark for suspended transaction found")
        sus_trans = pos.read_suspended_transactions()
        # Confirm the transaction is in the suspended list by its price
        if not sus_trans or not sus_trans[0][2] == '$3.21':
            tc_fail("Suspeded transaction not found in transactions list")
        self.log.info("Transaction matching our suspended transaction found")
        
        self.log.info("Attempting to resume transaction and pay it out")
        pos.click_suspended_transaction() # It should be at the top of our list
        self._confirmTotal(321)
        pos.pay()
        
    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        pos.close()

    # Helper function to try and end a transaction - even when test failed
    def _clearTrans(self):
        self.log.info("Completing the transaction")
        try:
            pos.click_function_key("Pay")
            pos.click_tender_key("Exact Change")
        except Exception as e:
            self.log.warning("Failure to pay out transaction. Attempting to recover.")
            msg = pos.read_message_box()
            if msg:
                self.log.warning(f"POS Message detected: {msg}")
                pos.click_message_box_key("Ok", verify=False)
            self.log.info("Voiding the transaction")
            pos.void_transaction()
        # Ensure we got to the speedkeys menu without issue
        _wait_for_trans_state('Idle')

    # Helper function to check whether the total is at the maximum transaction limit
    def _confirmTotal(self, expected_value):
        total = pos.read_balance()['Total']
        total = total.replace(".", "")
        total = total.replace("$", "")
        total = total.replace("-", "")
        while len(total) > 1 and total[0] == '0':
            total = total[1:]
        if int(total) == expected_value:
            self.log.info(f"Confirmed total at expected: [{expected_value}]")
        else:
            self._clearTrans()
            tc_fail(f"Unexpected total: [{total}]")
            
    # Helper function to confirm that we got a warning about the limit
    def _confirmMessage(self, target_msg=None):
        msg = pos.read_message_box()
        pos.click_message_box_key("Ok", verify=False)
        if not msg and not target_msg:
            self.log.info("Confirmed no message")
        if msg == target_msg:
            self.log.info("Confirmed desired message")
        else:
            self._clearTrans()
            tc_fail(f"Did not find desired Message. Message found: [{msg}]")

    # Helper function to make sure transaction journal contains a certain number of items
    def _number_of_items(self, number, timeout1=default_timeout):
        start_time = time.time()
        while time.time() - start_time <= timeout1:
            if int(len(pos.read_transaction_journal(timeout=(timeout1/20.0)))) == int(number):
                return True
            time.sleep(timeout1/20.0)
        else:
            return False
        
# These functions are a little hacky, and lack logging, but could be really useful in the framework.
# Should be documented well enough for a clean move if anyone wants them. Just change pos.driver to driver.
posStateDict = { 
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

def _wait_for_trans_state(desired_state, timeout=5):
    """
    Waits for system reported posState to return the desired value.
    Useful for state handling. Not recommended for test validations.
    Args:
        desired_state: String corresponding to the desired state
        timeout: Maximum number of seconds to wait for the desired state
    Returns:
        True if we've entered the desired state. False otherwise.
    Examples:
        >>> _wait_for_trans_state("TransactionComplete", timeout=7)
        True
    """
    start_time = time.time()
    while _get_trans_state() != desired_state and (time.time() - start_time) < timeout:
        time.sleep(.1)
    if _get_trans_state() == desired_state:
        return True
    else:
        return False

def _get_trans_state():
    """
    Uses system reported posState to determine the current transaction state.
    Useful for handling recovery situations. Not recommended for test validations.
    Returns:
        String: A string corresponding to the transaction state.
    Examples:
        >>> _get_trans_state()
        'Idle'
    """
    posState = pos.driver.execute_script("return posState") # Change this line if moved to frmwrk
    if not posState:
        return False # means we've git posState too early in connection
    return posStateDict[posState['TransactionState']]
