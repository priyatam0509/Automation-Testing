"""
    File name: TransactionLimits_POS.py
    Tags:
    Description: Test file for testing limits related to transaction limits. 
    Most of these limits will be found in Register Group Maintenance, under Transactions tab.
    These include: Maximum Refund limit, Maximum Transaction limit, and Maximum number of line items.
    This test should support HtmlPos, and Edge.
    Author: Gene Todd
    Date created: 2020-01-24 12:55:12
    Date last modified: 
    Python Version: 3.7
"""

# TODO: Edge needs a few changes to fully support this test.
# edge.read_balance() sometimes grabs wrong totals (grabbing too soon)
# edge.read_balance() parses values > $100 and < -$10 wrong.
# Occasional timing issues with Edge
# Above issues are fixed in pos_html.py

import logging, time
from app import Navi, mws, pos, system
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app import register_grp_maint

class TransactionLimits_POS():
    """
    Description: Test class that provides an interface for testing.
    """

    def __init__(self):
        """
        Initializes the TransactionLimits_POS class.
        """
        self.log = logging.getLogger()
        # Maximum cash value for transaction (sale/refund) in cents and string
        self.maxTrans = 10000
        self.maxTransStr = "$100.00"
        # Maximum number of line items - not testing until Edge supports
        self.maxItems = 10
        # Expected message for transMax
        self.maxTransError = "This item cannot be added." # Specific enough. More resistant to slight changes/differences

    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        """
        # if not system.restore_snapshot():
        #    self.log.debug("No snapshot to restore, if this is not expected please contact automation team")
        self.log.info("Attempting to setup transaction limits")
        rgm = register_grp_maint.RegisterGroupMaintenance()
        rgm.change("POSGroup1", {
            "Transaction Options": {
                "Maximum number of line items": self.maxItems,
                "Maximum total for the transaction": self.maxTrans
            },
            "Sales and Refunds": {
                "Refund transaction maximum amount": self.maxTrans
            }
        })
        self.log.info("Transaction limits set")
        pos.connect()
        self.log.info("Attempting to sign on")
        pos.sign_on()
        self.log.info("Waiting for an idle state")
        if not _wait_for_trans_state("Idle"):
            self.log.warning("Failed to confirm Idle state. Tests may not run as expected")
        
    @test
    def test_transMaxByAdd(self):
        """
        Test the maximum total for a transaction by a basic adding an item.
        """
        self._setupTrans()
        
        # Confirm we reached the max
        self._confirmTotal(True)
            
        # Confirm we can't add anything else - assume Generic Item is $0.01
        self.log.info("Adding $0.01 cent item to go over limit")
        pos.click_speed_key("Generic Item")
        self._confirmMessage()
            
        self._clearTrans()
        
    @test
    def test_transMaxByVoid(self):
        """
        Confirms that voiding an item does not impact transaction total calculations
        """
        self._setupTrans()
        
        # Void the last item added - Item 2
        self.log.info("Voiding Item 2")
        pos.click_function_key("Void Item")
        
        # Confirm we're not at the max anymore
        self._confirmTotal(False)
            
        # Add the item back to the transaction
        self.log.info("Adding Item 2")
        pos.click_speed_key("Item 2")
        
        # Confirm we're back at max
        self._confirmTotal(True)
        
        self._clearTrans()
        
    @test
    def test_transMaxByChangePrice(self):
        """
        Test maximum total for a transaction by changing item prices.
        Includes Price required items, as they functionally change from price 0.
        """
        self._setupTrans()
        
        # Confirm we can't add a price required item
        self.log.info("Adding price required item to transaction")
        pos.click_speed_key("Item 1")
        pos.enter_keypad(1, after="Enter")
        self._confirmMessage()
        
        # Confirm we can't raise Item 2's price above $5
        self.log.info("Overriding Item 2's price")
        pos.click_function_key("Override")
        # Assume default reason code and enter price
        pos.enter_keypad(501, after="Enter")
        self._confirmMessage("Unable to change price on item.")
        
        self._clearTrans()
        
    @test
    def test_transMaxByChangeQuantity(self):
        """
        Test maximum total for a transaction by changing item quantity.
        Includes tests for the '+' and '-' buttons.
        """
        self._setupTrans()
        
        # Confirm we can't use the '+' key to increase item 2
        self.log.info("Using '+' key on item 2")
        pos.enter_keypad('+')
        self._confirmMessage("Unable to change quantity on item.")
        
        # Confirm we can't change Item 2's quantity to 2
        self.log.info("Using 'Change Quantity' function on Item 2")
        pos.click_function_key("Change Item Qty")
        pos.enter_keypad(2, after="Enter")
        self._confirmMessage("Unable to change quantity on item.")
        
        self._clearTrans()
        
    @test
    def test_transMaxByTax(self):
        """
        Confirms that tax is included when checking maximum total for a transaction
        """
        self._setupTrans(self.maxTrans - 1000) # Setup transaction to max - $10
        
        # Confirm we can't add a $10 item with $1 Tax when $10 from max
        self.log.info("Adding $10 item with $1 tax")
        pos.click_speed_key("Tax 1")
        self._confirmMessage()
        
        self._clearTrans()
        
    @test
    def test_transMaxByLink(self):
        """
        Confirms that linked items are considered when checking maximum total for a transaction
        """
        self._setupTrans(self.maxTrans - 100) # Setup transaction to max - $1
        
        # Confirm we can't add a $1 item with a $1 linked item when $1 from max
        self.log.info("Adding $1 item with $1 linked item")
        pos.enter_plu("014")
        self._confirmMessage()
        
        self._clearTrans()
    
    @test
    def test_refundMaxByAdd(self):
        """
        Performs test_transMaxByAdd using refunds instead.
        """
        self._startRefund()
        self.test_transMaxByAdd()
                
    @test
    def test_refundMaxByVoid(self):
        """
        Confirms that voiding an item does not impact transaction total calculations
        """
        self._startRefund()
        self.test_transMaxByVoid()
        
    @test
    def test_refundMaxByChangeQuantity(self):
        """
        Test maximum total for a transaction by changing item quantity.
        Includes tests for the '+' and '-' buttons.
        """
        self._startRefund()
        self.test_transMaxByChangeQuantity()
        
    @test
    def test_refundMaxByTax(self):
        """
        Confirms that tax is included when checking maximum total for a transaction
        """
        self._startRefund()
        self.test_transMaxByTax()
        
    @test
    def test_refundMaxByLink(self):
        """
        Confirms that linked items are considered when checking maximum total for a transaction
        """
        self._startRefund()
        self.test_transMaxByLink()
        
    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        pos.close()

    # Helper function for setting up a transaction at the maximum limit
    # target_price = Optional argument for some tests. Makes total this value, in cents.
    def _setupTrans(self, target_price=None):
        # If we're still in a transaction, try to reset first
        if not _wait_for_trans_state("Idle"):
            self.log.warning(f"System not idle. Attempting to recover.")
            self._clearTrans()
        # Get to the transMax - Asssume Item 2 is $5
        self.log.info("Adding items to reach transaction maximum")
        pos.click_speed_key("Item 1")
        if target_price != None:
            pos.enter_keypad(target_price - 500, after="Enter")
        else:
            pos.enter_keypad(self.maxTrans - 500, after="Enter")
        #pos.click_speed_key("Item 2")
        pos.enter_plu("002") # Cheeky way to keep HtmlPos keyboard from being mad

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
            pos.click_function_key("Void Transaction", verify=False)
            pos.click_message_box_key("Yes", verify=False)
            raise

    # Helper function to check whether the total is at the maximum transaction limit
    def _confirmTotal(self, expected_value):
        total = pos.read_balance()['Total']
        total = total.replace("-", "") # Don't care if its positive or negative for refunds
        if total == self.maxTransStr and expected_value:
            self.log.info(f"Confirmed total at max: [{self.maxTransStr}]")
        elif total != self.maxTransStr and not expected_value:
            self.log.info(f"Confirmed total not at max: [{total}]")
        else:
            self._clearTrans()
            tc_fail(f"Incorrect total. Total {'==' if expected_value else '!='} Max. Total: [{total}]")
            
    # Helper function to confirm that we got a warning about the limit
    def _confirmMessage(self, target_msg=None):
        if target_msg == None:
            target_msg = self.maxTransError
        msg = pos.read_message_box()
        pos.click_message_box_key("Ok", verify=False)
        if target_msg in msg:
            self.log.info("Confirmed warning for transaction limit")
        else:
            self._clearTrans()
            tc_fail(f"Did not find desired Message. Message found: [{msg}]")
        
    # Helper function for handling clicking refund and possible error messages
    def _startRefund(self):
        if not _wait_for_trans_state("Idle"):
            self.log.warning(f"System not idle. Attempting to recover.")
            self._clearTrans()
        self.log.info("Starting a refund")
        pos.click_function_key("Refund")
        
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
    return posStateDict[posState['TransactionState']]
