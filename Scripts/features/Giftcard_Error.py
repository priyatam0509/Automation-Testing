"""
    File name: Giftcard_Error.py
    Tags:
    Description: [PEACOCK-3717] This will verify that POS will not allow for incorrect activation/recharge amount.
    Pre-Requisite: Make sure that giftcard is not-active.
    Author: Asha Sangrame
    Date created: 2020-01-27 14:53:24
    Date last modified:
    Python Version: 3.7
"""


import logging, time
from app import Navi, mws, pos, system, pinpad, item, store_close
from app import networksim
from app.framework.tc_helpers import setup, test, teardown, tc_fail

log = logging.getLogger()

def add_giftcard_item(cashcard_plu, item_data):
    """
    This is helper method. This will add cash card item for Gift card in MWS
    Args: 
        cashcard_plu : (str) PLU of cashcard item
    Returns: True if success or False on failure
    """        
    # Create object for Item
    itm = item.Item()

    #Adding the cash card item 
    mws.set_value("PLU/UPC", cashcard_plu)

    mws.click_toolbar("Search")

    stringResult = mws.get_top_bar_text()

    # Check if item already present. If not then add item
    if ("No" in stringResult):
        itm.add(item_data)
        log.info("Cash Card item added")
    else:
        log.info("Cash Card item already exists")
            
    mws.click_toolbar("Exit")
    return True

def set_giftcard_data(brand, Giftcard):
    """
    This is helper method. This will inactive giftcard data
    Args: 
        brand : (str) Brand for which you need to set giftcard data
        Guftcard : (str) Giftcard for which you need to set data
    Returns: Dictionary that represents the gift card data.
    """
    card_data = networksim._get_card_data(brand, Giftcard)
    card_number = card_data['Track2']
    card_number=card_number.split("=")
    
    msg = networksim.set_prepaid_manager(card_number[0], False, "0.00", "0.00", "0.00")
    return msg

def verify_decimal_error(cashcard_plu, limit, action):
    """
    This is helper method. This will verify that 
    POS will not allow for activation/Recharge if amount is decimal.
    Args: 
        cashcard_plu : (str) PLU of cashcard item
        limit : (str) Minimum amount for activation or Recharge
        action : (str) This can be either Activate or Recharge as per requirement
    Return: 
        bool: True on success, False on failure.
    """        
    # Take amount which is greater than minimum activation amount and make it decimal
    amount = int(limit) + 1
    amount_to_enter = str(amount) + "25"
    log.info(f"{action} amount is {amount_to_enter}")
            
    # Add cash card item 
    pos.add_item(cashcard_plu, method="plu", price=amount_to_enter, cash_card_action=action) 
  
    try:
        error_msg = pos.read_message_box()
        if "price must be at least" not in error_msg.lower():
            log.error("Error message not correct")
            return False
    except Exception as e:
        log.error(f"Message box not came. Exception: {e}")
        return False
        
    pos.click_message_box_key("OK", verify=False)
    return True

def verify_minimum_amt_error(limit, action):
    """
    This is helper method. This will verify POS will not allow for activation/Recharge if amount is less than minimum amount.
    Args: 
        limit : (str) Minimum amount for activation or Recharge
        action : (str) This can be either activation or recharge as per requirement
    Return: 
        bool: True on success, False on failure.
    """        
    # Make amount less than minimum amount
    amount = int(limit) - 1
    amount_to_enter = str(amount) + "00"
    log.info(f"{action} amount is {amount_to_enter}")
        
    for num in amount_to_enter:
        pos.click_keypad(num, verify=False)
    pos.click_keypad("ENTER", verify=False)      
    
    try:
        error_msg = pos.read_message_box()
        if ("price must be at least $"+limit) not in error_msg.lower():
            log.error("Error message not correct")
            return False
    except Exception as e:
        log.error(f"Message box not came. Exception: {e}")
        return False
        
    pos.click_message_box_key("OK", verify=False)
    return True

def verify_maximum_amt_error(limit, action):
    """
    This is helper method. This will verify POS will not allow for activation/Recharge if amount is more than maximum amount.
    Args: 
        limit : (str) Maximum amount for activation or Recharge
        action : (str) This can be either activation or recharge as per requirement
    Return: 
        bool: True on success, False on failure.
    """        
    # Make amount less than minimum amount
    amount = int(limit) + 1
    amount_to_enter = str(amount) + "00"
    log.info(f"{action} amount is {amount_to_enter}")

    for num in amount_to_enter:
        pos.click_keypad(num, verify=False)
    pos.click_keypad("ENTER", verify=False)      
        
    try:
        error_msg = pos.read_message_box()
        if ("not more than $"+activation_max_limit) not in error_msg.lower():
            log.error("Error message not correct")
            return False
    except Exception as e:
        log.error(f"Message box not came. Exception: {e}")
        return False
        
    # Void transaction
    if not pos.click_message_box_key("OK", verify=False):
        return False
    if not pos.click_keypad("CANCEL", verify=False):
        return False
    if not pos.click_function_key("VOID TRANS", verify=False):
        return False
    if not pos.click_keypad("ENTER", verify=False):
        return False

    return True

class Giftcard_Error():
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
        self.cashcard_plu = "12345"

        self.item_data = {
            "General": {
                "PLU/UPC": self.cashcard_plu,
                "Description": "Cash Card",
                "Department": "Cash Card",
                "Item Type": "Cash Card",
                "This item sells for": True,
                "per unit": "10.0"
            },
            "Options": {
                "Return Price": "10.0",
                "Network Product Code": "500",
            }
        }

    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        #TO-DO Need to declare below variables with self object once test harness scoping issue resolves
        global activation_max_limit, activation_min_limit, recharge_max_limit, recharge_min_limit

        # Navigate to MWS
        Navi.navigate_to("MWS")

        # Navigate to network setup
        Navi.navigate_to("Global Info Editor")
        mws.select_tab("Prepaid Card Settings")

        # Fetch minimum activation amount
        activation_min_limit = mws.get_text("Minimum Activation Amount", timeout=3)

        # Fetch maximum activation amount
        activation_max_limit = mws.get_text("Maximum Activation Amount", timeout=3)

        # Fetch minimum recharge amount
        recharge_min_limit = mws.get_text("Minimum Recharge Amount", timeout=3)

        # Fetch maximum recharge amount
        recharge_max_limit = mws.get_text("Maximum Recharge Amount", timeout=3)

        mws.click_toolbar("Cancel")

        # Add giftcard item
        if not add_giftcard_item(self.cashcard_plu, self.item_data):
            log.error("Not able to add cashcard item")
            return False

        # Set giftcard to Inactive state
        success_msg = set_giftcard_data(system.get_brand(), "GiftCard1")

        if not success_msg['success'] == True:
            log.error("Not able to set giftcard data")
            return False

        # Navigate to POS
        Navi.navigate_to("POS")
        
        # Sign on to POS screen if not already sign-on
        pos.sign_on()
    
    @test
    def activation_decimal_error(self):
        """
        Zephyr Id : This will verify POS will not allow for activation 
                    if amount is decimal.
        Args: None
        Returns: None
        """        
        if not verify_decimal_error(cashcard_plu=self.cashcard_plu, limit=activation_min_limit, action="Activate"):
            tc_fail("Allowing activation for decimal activation amount")
            return False

    @test
    def activation_minimum_amt_error(self):
        """
        Zephyr Id : This will verify POS will not allow for activation amount 
                    if amount is less than minimum amount
        Args: None
        Returns: None
        """        
        if not verify_minimum_amt_error(limit=activation_min_limit, action="Activate"):
            tc_fail("Allowing activation for amount less than minimum amount")
            return False

    @test
    def activation_maximum_amt_error(self):
        """
        Zephyr Id : This will verify POS will not allow for activation amount if amount is more than maximum amount
        Args: None
        Returns: None
        """        
        if not verify_maximum_amt_error(limit=activation_max_limit, action="Activate"):
            tc_fail("Allowing activation for amount more than maximum amount")
            return False

    @test
    def recharge_decimal_error(self):
        """
        Zephyr Id : This will verify POS will not allow for recharge if amount is decimal.
        Args: None
        Returns: None
        """        
        if not verify_decimal_error(cashcard_plu=self.cashcard_plu, limit=recharge_min_limit, action="Recharge"):
            tc_fail("Allowing recharge for decimal recharge amount")
            return False

    @test
    def recharge_minimum_amt_error(self):
        """
        Zephyr Id : This will verify POS will not allow for recharge amount if amount is less than minimum amount
        Args: None
        Returns: None
        """        
        if not verify_minimum_amt_error(limit=recharge_min_limit, action="Recharge"):
            tc_fail("Allowing recharge for amount less than minimum amount")
            return False

    @test
    def recharge_maximum_amt_error(self):
        """
        Zephyr Id : This will verify POS will not allow for recharge amount if amount is more than maximum amount
        Args: None
        Returns: None
        """        
        if not verify_maximum_amt_error(limit=recharge_max_limit, action="Recharge"):
            tc_fail("Allowing recharge for amount more than maximum amount")
            return False

    @test
    def drystock_sale(self):
        """
        Zephyr Id : This will add drystock item and try to do payment with giftcard which is not active.
                    This will verify that Inactive card error comes.
        Args: None
        Returns: None
        """
        
        # navigating to pos and open till

        SC = store_close.StoreClose()
        if not SC.begin_store_close():
            log.error("There was an issue with the Store Close")
        
        # Navigate to POS
        Navi.navigate_to("POS")
        
        # Sign on to POS screen if not already sign-on
        pos.sign_on()
        
        # Add generic item
        pos.add_item()

        if not pos.click_function_key("PAY", verify=False):
            return False
        
        if not pos.click_tender_key('CARD', verify=False):
            return False
        
        try: 
            pinpad.swipe_card(system.get_brand(), card_name="GiftCard1")
        except Exception as e:
            log.warning(f"Card swipe in pinpad failed. Exception: {e}")
            pos.click_keypad("CANCEL")
            return False

        start_time = time.time()
        while time.time() - start_time <= 60:
            status = pos.read_status_line()
            if "30 - INACTIVE CARD" in status:
                log.info("Inactive card message came")
                break
        else:
            tc_fail("Inactive card message not came")
            return False

        if not pos.click_keypad("CANCEL", verify=False):
            return False
        if not pos.click_function_key("VOID TRANS", verify=False):
            return False
        if not pos.click_keypad("ENTER", verify=False):
            return False

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        pass