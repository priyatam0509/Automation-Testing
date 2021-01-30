import functools
import logging, time, json, requests
import winreg
from app import pos, system
from app import constants
from app import pinpadsim, crindsim
from app.framework.tc_helpers import tc_fail

logger = logging.getLogger()

def pinpad_retry(func):
    """
    Decorator for test methods
    Defines an optional verify parameter that, if set to True, will cause tc_fail to be invoked if the decorated function returns False or None
    The parameter defaults to True
    TODO: Add parameter to allow temporary changes in logging level
    TODO: Add parameter for timeouts?
    """
    @functools.wraps(func) # Preserve func attributes like __name__ and __doc__
    def pinpad_retry_wrapper(*args, **kwargs):
        
        try:
            retry  = kwargs['retry']
            del kwargs['retry']
        except KeyError:
            retry = True
        
        try:
            verify = kwargs['verify']
            del kwargs['verify']
        except KeyError:
            verify = True

        if retry:
            #Tracks if the pinpad has been reset yet to loop back through 3 swipe attempts
            reset_count = 0
            while (reset_count < 2):
                #counts the number of failed pay attempts for the pinpad reset
                fail_counter = 0
                while fail_counter < 3:
                    ret = func(**kwargs)
                    if ret:
                        return True
                    else:
                        #tracks if none of the message box prompts or function key were used
                        #if none are used, we assume it is edge case prompt that takes longer to show (No response from host)
                        failure_flag = False
                        fail_counter += 1
                        logger.info(f"Trying pay_card for {fail_counter} attempt")
                        #Handles message box fails
                        if pos.click_message_box_key("Ok", verify=False):
                            failure_flag = True
                        #Handles hanging prompt fails
                        if pos.click_function_key("Cancel", verify=False):
                            failure_flag = True
                        #Clears message of canceled payment if hanging prompt fail
                        if pos.click_message_box_key("Ok", verify=False):
                            failure_flag = True
                        #If none of the prompts or function key were clicked, assume edge case prompt (no response from host)
                        if not failure_flag:
                            time.sleep(20) #sleep for 20 seconds for prompt to be visible
                            pos.click_message_box_key("Ok", verify=False)
                logger.info("Resetting pinpad after 3 transaction failures")
                requests.get(url='http://10.80.31.212/api/tools/start')
                time.sleep(120) #Sleep for 2 mins for pinpad to redownload
                crindsim.set_flow_rate("10")
                reset_count += 1
            #Failed 3 attempts before and after a pinpad reset
            if verify and (ret is None or not ret):
                tc_fail(f"{func.__module__}.{func.__name__} failed.")
            pos.void_transaction(verify=False) #If all attempts failed, must void to have next test receipt be correct
            return ret
        else:
            ret = func(**kwargs)
        
        if verify and (ret is None or not ret):
            tc_fail(f"{func.__module__}.{func.__name__} failed.")
        pos.void_transaction(verify=False) #If all attempts failed, must void to have next test receipt be correct
        return ret

    return pinpad_retry_wrapper

def sale_func(card_info = ["Visa", 'CORE'], item_info = [['002', 'Item 2', 5]]):
    """Performs a sale with the passed in card and item list.  
    
    Args: 
        card_info: List containing card name and card group respectively.  This card will be used for the sale
        item_info: List of triplets containing item information for sale.  Each tuplet consists of item plu (String), 
            item name (String) and price (double).  Price must sum to whole dollar amount  
    
    Returns: 
        True if the sale with the given card succeeded and receipt is verified
        False if the sale with the given card fails or the receipt is incorrect
    """
    card_name = card_info[0]
    card_group = card_info[1]
    #Add expected item prints for receipt into list during transaction
    receipt_list = []
    total_price = 0

    for item in item_info:
        item_plu = item[0]
        item_name = item[1]
        item_price = item[2]

        logger.info(f"Adding item PLU: {item_plu}, Name:{item_name}")
        pos.add_item(item_plu, "PLU")
        #For item ["002", "Item 2", 5] you get "Item 2 $5.00"
        receipt_list.append(f"{item_name} ${item_price}.00") 
        total_price += item_price

    if (not total_price % 1 == 0):
        logger.warning("Total item price was not a whole dollar amount.  Pinpad will decline")
        return False

    if not pos.pay_card(brand=card_group, card_name=card_name, verify=False):
        logger.warning("Pay_Card failed.  Returning False for sale_func")
        return False

    #Add the line to check for total price in receipt to receipt_list
    receipt_list.append(f"Total = ${total_price}.00") 

    #Current way of checking approval is just verifying transaction went through with receipt.
    #can be changed later to do different verification.
    logger.info(f"Checking receipt for card sale: {card_name}")
    return pos.check_receipt_for(receipt_list, verify=False)

def sale_decline_func(card_info = ["MCFleet_FuelOnly_1", 'CORE'], item_info = [['002', 'Item 2', 5]], decline_prompt = 'Fuel only card'):
    """Performs a card sale that is expected to be declined with the given card info, item list and decline_prompt.
    
    Args: 
        card_info: List containing card name and card group respectively.  This card will be used for the sale
        item_info: List of triplets containing item information for sale.  Each tuplet consists of item plu (String), 
            item name (String) and price (double).  Price must sum to whole dollar amount  
        decline_prompt: The expected decline message when attempting a sale with the given card/items

    Returns: 
        True if the sale with the given card succeeded and receipt is verified
        False if the sale with the given card fails or the receipt is incorrect
    """
    card_name = card_info[0]
    card_group = card_info[1]
    #Add expected item prints for receipt into list during transaction
    receipt_list = []
    total_price = 0

    for item in item_info:
        item_plu = item[0]
        item_name = item[1]
        item_price = item[2]

        logger.info(f"Adding item PLU: {item_plu}, Name:{item_name}")
        pos.add_item(item_plu, "PLU")
        #For item ["002", "Item 2", 5] you get "Item 2 $5.00"
        receipt_list.append(f"{item_name} ${item_price}.00") 
        total_price += item_price

    logger.info(f"Name of card about to be swiped: {card_name}")#TODO used to track card swipes while pinpad is still broken and repoting isnt finished
    return pay_card_decline(brand=card_group, card_name=card_name, decline_prompt = decline_prompt)

def manual_entry_func(card_info = ["Visa", 'CORE'], item_info = [['002', 'Item 2', 5]]):
    """Performs a manual entry sale with the passed in card and item list.  
    
    Args: 
        card_info: List containing card name and card group respectively.  This card will be used for the sale
        item_info: List of triplets containing item information for sale.  Each tuplet consists of item plu (String), 
            item name (String) and price (double).  Price must sum to whole dollar amount  
    
    Returns: 
        True if the manual entry sale with the given card succeeded and receipt is verified
        False if the manual entry sale with the given card fails or the receipt is incorrect
    """
    card_name = card_info[0]
    card_group = card_info[1]
    logger.info(f"Checking {constants.CARD_DATA_MANUAL} for {card_name}")
    card_data = {}
    with open(constants.CARD_DATA_MANUAL, 'r') as fp:
        card_data_file = json.load(fp)
        try:
            card_data = card_data_file[system.get_brand().upper()][card_name]
        except:
            logger.warning(f"Unable to find {card_name} under {system.get_brand().upper()} within {constants.CARD_DATA_MANUAL}.")
    if not card_data:
        logger.info(f"Checking {constants.CARD_DATA} for {card_name}")
        brand = card_group.upper()
        with open(constants.CARD_DATA, 'r') as fp:
            card_data_file = json.load(fp)
            try:
                card_data = card_data_file[brand][card_name]
            except:
                logger.error(f"Unable to find {card_name} under {brand} within {constants.CARD_DATA}.")
    try:
        exp_date = card_data["Expiration Date"]
    except:
        exp_date = "1230"
        logger.warning("No expiration date provded for this card")
    #Add expected item prints for receipt into list during transaction
    receipt_list = []
    total_price = 0

    for item in item_info:
        item_plu = item[0]
        item_name = item[1]
        item_price = item[2]

        logger.info(f"Adding item PLU: {item_plu}, Name:{item_name}")
        pos.add_item(item_plu, "PLU")
        #For item ["002", "Item 2", 5] you get "Item 2 $5.00"
        receipt_list.append(f"{item_name} ${item_price}.00") 
        total_price += item_price

    if (not total_price % 1 == 0):
        logger.warning("Total item price was not a whole dollar amount.  Pinpad will decline")
        return False

    if not pos.manual_entry(brand=card_group, card_name=card_name, expiration_date=exp_date, verify=False):
        logger.warning("Pay_Card failed.  Returning False for sale_func")
        return False

    #Add the line to check for total price in receipt to receipt_list
    receipt_list.append(f"Total = ${total_price}.00") 

    #Current way of checking approval is just verifying transaction went through with receipt.
    #can be changed later to do different verification.
    logger.info(f"Checking receipt for card sale: {card_name}")
    return pos.check_receipt_for(receipt_list, verify=False)

def manual_entry_decline_func(card_info = ["Expired_Visa", 'CORE'], expiration_date = "1215", item_info = [['002', 'Item 2', 5]], decline_prompt = 'Expired Card: Try Another'):
    """Performs a card sale that is expected to be declined with the given card info, item list and decline_prompt.
    
    Args: 
        card_info: List containing card name and card group respectively.  This card will be used for the sale
        item_info: List of triplets containing item information for sale.  Each tuplet consists of item plu (String), 
            item name (String) and price (double).  Price must sum to whole dollar amount  
        decline_prompt: The expected decline message when attempting a sale with the given card/items

    Returns: 
        True if the sale with the given card succeeded and receipt is verified
        False if the sale with the given card fails or the receipt is incorrect
    """
    card_name = card_info[0]
    card_group = card_info[1]
    #Add expected item prints for receipt into list during transaction
    receipt_list = []
    total_price = 0

    for item in item_info:
        item_plu = item[0]
        item_name = item[1]
        item_price = item[2]

        logger.info(f"Adding item PLU: {item_plu}, Name:{item_name}")
        pos.add_item(item_plu, "PLU")
        #For item ["002", "Item 2", 5] you get "Item 2 $5.00"
        receipt_list.append(f"{item_name} ${item_price}.00") 
        total_price += item_price

    logger.info(f"Name of card about to be swiped: {card_name}")#TODO used to track card swipes while pinpad is still broken and repoting isnt finished
    return manual_entry_decline(brand=card_group, card_name=card_name, expiration_date = expiration_date, decline_prompt = decline_prompt)

def refund_func(card_info = ["Visa", "Core"], item_info = [['002', 'Item 2', 5], ['008', 'Item 8', 5]], refund_list = [['002', 'Item 2', 5]]):
    """
    Performs a refund with the passed in card information.
    #NOTE can be expanded to allow selection of items purchased and items refunded if desired

    Args: 
        card_info: List containing card name and card group respectively.  This card will be used for the sale
            
    Returns: 
        True if the sale and refund with the given card succeeded and receipt is verified
        False if the sale and refund with the given card fails or the receipt is incorrect
    """
    card_name = card_info[0]
    card_group = card_info[1]
    #Add expected item prints for receipt into list during transaction
    receipt_list = []
    refund_receipt_list = []
    total_price = 0

    for item in item_info:
        item_plu = item[0]
        item_name = item[1]
        item_price = item[2]

        logger.info(f"Adding item PLU: {item_plu}, Name:{item_name}")
        pos.add_item(item_plu, "PLU")
        #For item ["002", "Item 2", 5] you get "Item 2 $5.00"
        receipt_list.append(f"{item_name} ${item_price}.00") 
        total_price += item_price

    #Use current card in CardData.json CORE group to pay for sale
    logger.info(f"Name of card about to be swiped: {card_name}")
    if pos.pay_card(brand=card_group, card_name=card_name, verify=False):
        logger.info(f"Successful transaction before refund with {card_name}")
            
    # Find invoice number of last transaction
    logger.info("Clicking Receipt Search")
    pos.click_function_key("Receipt Search")
    contents = pos.read_receipt()
    invoice_num = -1
    for i in range(len(contents)):
        field = contents[i]
        if "INVOICE" in field:
            invoice_num = contents[i + 1]
            logger.info(f"Found invoice number: {invoice_num}")
    
    if invoice_num == -1:
        tc_fail("Unable to find INVOICE number in receipt")

    logger.info("Clicking refund button.")
    pos.click_function_key("Refund", verify=False)

    start_time = time.time()
    while (time.time()-start_time <5):
        if pos.read_journal_watermark() == 'REFUND':
            break
    else:
        logger.info(f"During Refund for {card_name} did not read refund watermark after clicking refund.")
        return False

    for item in refund_list:
        item_plu = item[0]
        item_name = item[1]
        item_price = item[2]

        logger.info(f"Adding refund item PLU: {item_plu}, Name:{item_name}")
        pos.add_item(item_plu, "PLU")
        #For item ["002", "Item 2", 5] you get "Item 2 $5.00"
        refund_receipt_list.append(f"{item_name} $-{item_price}.00") 
        total_price += item_price
    
    if not refund_items(card_info = card_info, invoice_num = invoice_num, verify=False):
        return False

    # Check to make sure both items are on the receipt
    logger.info("Checking receipt for correct items, price and tender type")
    return pos.check_receipt_for(refund_receipt_list, verify=False)

def split_tender_func(card_info = ["Visa", 'CORE'], item_info = [['002', 'Item 2', 5]]):
    """Performs a split tender sale with the passed in card and $1.00 in Cash with the item list.  
    
    Args: 
        card_info: List containing card name and card group respectively.  This card will be used for the sale
        item_info: List of triplets containing item information for sale.  Each tuplet consists of item plu (String), 
            item name (String) and price (double).  Price must sum to whole dollar amount  
    
    Returns: 
        True if the sale with the given card succeeded and receipt is verified
        False if the sale with the given card fails or the receipt is incorrect
    """
    card_name = card_info[0]
    card_group = card_info[1]
    #Add expected item prints for receipt into list during transaction
    receipt_list = []
    total_price = 0

    for item in item_info:
        item_plu = item[0]
        item_name = item[1]
        item_price = item[2]

        logger.info(f"Adding item PLU: {item_plu}, Name:{item_name}")
        pos.add_item(item_plu, "PLU")
        #For item ["002", "Item 2", 5] you get "Item 2 $5.00"
        receipt_list.append(f"{item_name} ${item_price}.00") 
        total_price += item_price

    if (not total_price % 1 == 0):
        logger.warning("Total item price was not a whole dollar amount.  Pinpad will decline")
        return False

    #Paying out partially with cash
    pos.pay("$1.00")
    start_time = time.time()
    while (time.time()-start_time < 5):
        if ['Cash', '$1.00'] in pos.read_transaction_journal():
            break
    else:
        logger.error("Did not see partial cash in transaction journal.")
        return False

    if not pos.pay_card(brand=card_group, card_name=card_name, verify=False):
        logger.warning("Pay_Card failed.  Returning False for sale_func")
        return False

    #Add the line to check for total price in receipt to receipt_list
    receipt_list.append(f"Total = ${total_price}.00") 

    #Current way of checking approval is just verifying transaction went through with receipt.
    #can be changed later to do different verification.
    logger.info(f"Checking receipt for card sale: {card_name}")
    return pos.check_receipt_for(receipt_list, verify=False)

def sale_discount_func(card_info = ["Visa", 'CORE'], item_info = [['008', 'Item 8', 5]], discount = ["Transaction", "Std_Trans_Amt"]):
    """
    Performs a sale with a discount applied.  Can use any card passed in, on a list of any configured items, with the desired discount.  

    Args:
        card_info: card to be used for the sale with discount
        item_info: list of items that the sale with discount will be performed on
        discount: list containing [discount_type, discount_name] 
            discount_type: "Item" or "Transaction" to describe what type of discount you want to use
            discount_name: the name of the discount you want to use
    
    Returns:
        True if the sale with discount succeeded and receipt was verified
        False if the sale fails or the receipt does not match the expected results.
    """
    discount_type = discount[0]
    discount_name = discount[1]
    card_name = card_info[0]
    card_group = card_info[1]
    #Add expected item prints for receipt into list during transaction
    receipt_list = []
    total_price = 0

    for item in item_info:
        item_plu = item[0]
        item_name = item[1]
        item_price = item[2]

        logger.info(f"Adding item PLU: {item_plu}, Name:{item_name}")
        pos.add_item(item_plu, "PLU")
        #For item ["002", "Item 2", 5] you get "Item 2 $5.00"
        receipt_list.append(f"{item_name} ${item_price}.00") 
        total_price += item_price

    if (not total_price % 1 == 0):
        logger.warning("Total item price was not a whole dollar amount.  Pinpad will decline")
        return False

    logger.info("Clicking transaction button")
    pos.click_function_key("Transaction")
    logger.info(f"Clicking Discount {discount_type} button")
    pos.click_function_key(f"Discount {discount_type}")
    logger.info(f"Choosing {discount_name} for discount in message box.")
    pos.click_message_box_key(discount_name)
    receipt_list.append(discount_name)

    if not pos.pay_card(brand=card_group, card_name=card_name, verify=False):
        logger.warning("Pay_Card failed.  Returning False for sale_discount_func")
        return False

    #Add the line to check for total price in receipt to receipt_list
    receipt_list.append(f"Subtotal = ${total_price}.00") 

    #Current way of checking approval is just verifying transaction went through with receipt.
    #can be changed later to do different verification.
    logger.info(f"Checking receipt for card sale with discount: {card_name}")
    return pos.check_receipt_for(receipt_list, verify=False)

def cashback_sale_func(card_info = ["Visa", 'CORE'], item_info = [['002', 'Item 2', 5]], cashback_amount = "1.00"):
    """Performs a sale with the passed in card and item list.  
    
    Args: 
        card_info: List containing card name and card group respectively.  This card will be used for the sale
        item_info: List of triplets containing item information for sale.  Each tuplet consists of item plu (String), 
            item name (String) and price (double).  Price must sum to whole dollar amount  
        cashback_amount: (String) the amount of cash you want back
    
    Returns: 
        True if the sale with the given card succeeded and receipt is verified
        False if the sale with the given card fails or the receipt is incorrect
    """
    card_name = card_info[0]
    card_group = card_info[1]
    #Add expected item prints for receipt into list during transaction
    receipt_list = []
    total_price = 0

    #Need to convert string to float before int
    cashback_price = int(float(cashback_amount))
    total_price += cashback_price
    receipt_list.append(f"Cash Back ${cashback_amount}")

    for item in item_info:
        item_plu = item[0]
        item_name = item[1]
        item_price = item[2]

        logger.info(f"Adding item PLU: {item_plu}, Name:{item_name}")
        pos.add_item(item_plu, "PLU")
        #For item ["002", "Item 2", 5] you get "Item 2 $5.00"
        receipt_list.append(f"{item_name} ${item_price}.00") 
        total_price += item_price

    if (not total_price % 1 == 0):
        logger.warning("Total item price was not a whole dollar amount.  Pinpad will decline")
        return False

    if not pos.pay_card(brand=card_group, card_name=card_name, cashback_amount = cashback_amount, verify=False):
        logger.warning("Pay_Card failed.  Returning False for sale_func")
        return False

    #Add the line to check for total price in receipt to receipt_list
    receipt_list.append(f"Total = ${total_price}.00") 

    #Current way of checking approval is just verifying transaction went through with receipt.
    #can be changed later to do different verification.
    logger.info(f"Checking receipt for card sale: {card_name}")
    return pos.check_receipt_for(receipt_list, verify=False)
        
def debit_sale_fee_func(card_info = ["Visa", 'CORE'], item_info = [['002', 'Item 2', 5]]):
    """Performs a sale with the passed in card and item list.  
    
    Args: 
        card_info: List containing card name and card group respectively.  This card will be used for the sale
        item_info: List of triplets containing item information for sale.  Each tuplet consists of item plu (String), 
            item name (String) and price (double).  Price must sum to whole dollar amount  
    
    Returns: 
        True if the sale with the given card succeeded and receipt is verified
        False if the sale with the given card fails or the receipt is incorrect
    """
    card_name = card_info[0]
    card_group = card_info[1]
    #Add expected item prints for receipt into list during transaction
    receipt_list = []
    total_price = 0
    #Add debit sale fee price onto total price
    total_price += 1

    for item in item_info:
        item_plu = item[0]
        item_name = item[1]
        item_price = item[2]

        logger.info(f"Adding item PLU: {item_plu}, Name:{item_name}")
        pos.add_item(item_plu, "PLU")
        #For item ["002", "Item 2", 5] you get "Item 2 $5.00"
        receipt_list.append(f"{item_name} ${item_price}.00") 
        total_price += item_price

    if (not total_price % 1 == 0):
        logger.warning("Total item price was not a whole dollar amount.  Pinpad will decline")
        return False

    if not pos.pay_card(brand=card_group, card_name=card_name, debit_fee = True, verify=False):
        logger.warning("Pay_Card failed.  Returning False for sale_func")
        return False

    #Add the line to check for total price in receipt to receipt_list
    receipt_list.append(f"Total = ${total_price}.00") 

    #Current way of checking approval is just verifying transaction went through with receipt.
    #can be changed later to do different verification.
    logger.info(f"Checking receipt for card sale: {card_name}")
    return pos.check_receipt_for(receipt_list, verify=False)

def cashback_fee_sale_func(card_info = ["Visa", 'CORE'], item_info = [['002', 'Item 2', 5]], cashback_amount = "1.00"):
    """Performs a sale with the passed in card and item list.  
    
    Args: 
        card_info: List containing card name and card group respectively.  This card will be used for the sale
        item_info: List of triplets containing item information for sale.  Each tuplet consists of item plu (String), 
            item name (String) and price (double).  Price must sum to whole dollar amount  
        cashback_amount: (String) the amount of cash you want back
    
    Returns: 
        True if the sale with the given card succeeded and receipt is verified
        False if the sale with the given card fails or the receipt is incorrect
    """
    card_name = card_info[0]
    card_group = card_info[1]
    #Add expected item prints for receipt into list during transaction
    receipt_list = []
    total_price = 0
    #Add cashback fee to total
    total_price += 1

    #Need to convert string to float before int
    cashback_price = int(float(cashback_amount))
    total_price += cashback_price
    receipt_list.append(f"Cash Back ${cashback_amount}")

    for item in item_info:
        item_plu = item[0]
        item_name = item[1]
        item_price = item[2]

        logger.info(f"Adding item PLU: {item_plu}, Name:{item_name}")
        pos.add_item(item_plu, "PLU")
        #For item ["002", "Item 2", 5] you get "Item 2 $5.00"
        receipt_list.append(f"{item_name} ${item_price}.00") 
        total_price += item_price

    if (not total_price % 1 == 0):
        logger.warning("Total item price was not a whole dollar amount.  Pinpad will decline")
        return False

    if not pos.pay_card(brand=card_group, card_name=card_name, cashback_amount = cashback_amount, verify=False):
        logger.warning("Pay_Card failed.  Returning False for sale_func")
        return False

    #Add the line to check for total price in receipt to receipt_list
    receipt_list.append(f"Total = ${total_price}.00") 

    #Current way of checking approval is just verifying transaction went through with receipt.
    #can be changed later to do different verification.
    logger.info(f"Checking receipt for card sale: {card_name}")
    return pos.check_receipt_for(receipt_list, verify=False)

def cashback_fee_sale_fee_func(card_info = ["Visa", 'CORE'], item_info = [['002', 'Item 2', 5]], cashback_amount = "1.00"):
    """Performs a debit sale with the passed in card and item list and gets cashback with a fee and a sale fee applied.  
    
    Args: 
        card_info: List containing card name and card group respectively.  This card will be used for the sale
        item_info: List of triplets containing item information for sale.  Each tuplet consists of item plu (String), 
            item name (String) and price (double).  Price must sum to whole dollar amount  
        cashback_amount: (String) the amount of cash you want back
    
    Returns: 
        True if the sale with the given card succeeded and receipt is verified
        False if the sale with the given card fails or the receipt is incorrect
    """
    card_name = card_info[0]
    card_group = card_info[1]
    #Add expected item prints for receipt into list during transaction
    receipt_list = []
    total_price = 0
    #Add cashback fee to total
    total_price += 1
    #Add sale fee to total
    total_price += 2

    #Need to convert string to float before int
    cashback_price = int(float(cashback_amount))
    total_price += cashback_price
    receipt_list.append(f"Cash Back ${cashback_amount}")

    for item in item_info:
        item_plu = item[0]
        item_name = item[1]
        item_price = item[2]

        logger.info(f"Adding item PLU: {item_plu}, Name:{item_name}")
        pos.add_item(item_plu, "PLU")
        #For item ["002", "Item 2", 5] you get "Item 2 $5.00"
        receipt_list.append(f"{item_name} ${item_price}.00") 
        total_price += item_price

    if (not total_price % 1 == 0):
        logger.warning("Total item price was not a whole dollar amount.  Pinpad will decline")
        return False

    if not pos.pay_card(brand=card_group, card_name=card_name, cashback_amount = cashback_amount, debit_fee=True, verify=False):
        logger.warning("Pay_Card failed.  Returning False for sale_func")
        return False

    #Add the line to check for total price in receipt to receipt_list
    receipt_list.append(f"Total = ${total_price}.00") 

    #Current way of checking approval is just verifying transaction went through with receipt.
    #can be changed later to do different verification.
    logger.info(f"Checking receipt for card sale: {card_name}")
    return pos.check_receipt_for(receipt_list, verify=False)

def cashback_sale_fee_func(card_info = ["Visa", 'CORE'], item_info = [['002', 'Item 2', 5]], cashback_amount = "1.00"):
    """Performs a sale with the passed in card and item list, getting cashback with a sale fee applied.  
    
    Args: 
        card_info: List containing card name and card group respectively.  This card will be used for the sale
        item_info: List of triplets containing item information for sale.  Each tuplet consists of item plu (String), 
            item name (String) and price (double).  Price must sum to whole dollar amount  
        cashback_amount: (String) the amount of cash you want back
    
    Returns: 
        True if the sale with the given card succeeded and receipt is verified
        False if the sale with the given card fails or the receipt is incorrect
    """
    card_name = card_info[0]
    card_group = card_info[1]
    #Add expected item prints for receipt into list during transaction
    receipt_list = []
    total_price = 0
    #Add sale fee to total
    total_price += 2

    #Need to convert string to float before int
    cashback_price = int(float(cashback_amount))
    total_price += cashback_price
    receipt_list.append(f"Cash Back ${cashback_amount}")

    for item in item_info:
        item_plu = item[0]
        item_name = item[1]
        item_price = item[2]

        logger.info(f"Adding item PLU: {item_plu}, Name:{item_name}")
        pos.add_item(item_plu, "PLU")
        #For item ["002", "Item 2", 5] you get "Item 2 $5.00"
        receipt_list.append(f"{item_name} ${item_price}.00") 
        total_price += item_price

    if (not total_price % 1 == 0):
        logger.warning("Total item price was not a whole dollar amount.  Pinpad will decline")
        return False

    if not pos.pay_card(brand=card_group, card_name=card_name, cashback_amount = cashback_amount, debit_fee=True, verify=False):
        logger.warning("Pay_Card failed.  Returning False for sale_func")
        return False

    #Add the line to check for total price in receipt to receipt_list
    receipt_list.append(f"Total = ${total_price}.00") 

    #Current way of checking approval is just verifying transaction went through with receipt.
    #can be changed later to do different verification.
    logger.info(f"Checking receipt for card sale: {card_name}")
    return pos.check_receipt_for(receipt_list, verify=False)
    
def postpay_sale_func(card_info = ["Visa", "Core"], dispenser_num = 1, money_amount = "5.00"):
    """Performs a postpay fuel sale.  Approve the fuel sale and pay after it is fueled.

    Args:
        card_info: card to be used for the refund
        dispenser_num: (int) the dispenser number you want to use for the sale
        money_amount = (string) the dollar amount of fuel you would like to purchase
    
    Returns:
        True if refund is successful
        False if refund fails
    """    
    crindsim.set_mode("manual")

    card_name = card_info[0]
    card_group = card_info[1]
    
    crindsim.set_sales_target(target=money_amount)

    #TODO: Not sure if we need to be resetting crind to fix status.  Revisit after runs
    # pos.select_dispenser(dispenser_num)
    # pos.click_forecourt_key("Reset")
    # pos.click_message_box_key("Yes")
    # if not pos.wait_for_disp_status(status = "", dispenser = 1, timeout = 720, verify=False):
    #     logger.warning("Dispenser was never ready to dispense fuel.")
    #     return False

    pos.select_dispenser(dispenser_num)
    crindsim.set_sales_target("money", money_amount)

    # Fuel 5.00
    logger.info("Opening Nozzle")
    crindsim.open_nozzle()
    logger.info("Lifting handle")
    crindsim.lift_handle()

    if not pos.click_forecourt_key("Auth", verify=False):
        logger.warning(f"Failed to click Auth key for card {card_name}")
        system.takescreenshot()

    logger.info("Waiting for the buffer to be clear")
    start_time = time.time()
    while time.time() - start_time <= 20:
        if pos.read_fuel_buffer() == "":
            logger.info("Fueling has finished")
            break
        else:
            logger.warning(pos.read_fuel_buffer())
    else:
        logger.error("Fueling failed to finish")
        #Recover and fail

    logger.info("Lowering handle")
    crindsim.lower_handle()
    logger.info("Closing nozzle")
    crindsim.close_nozzle()

    logger.info(f"Checking fuel buffer for sale amount for card: {card_name}")
    start_time = time.time()
    while(time.time() - start_time < 5):
        if f"${money_amount}" in pos.read_fuel_buffer():
            logger.info(f"Found fuel buffer displaying sale amount for card: {card_name}")
            break
    else:
        logger.warning(f"Couldn't see sale amount in the fuel buffer")
        system.takescreenshot()
        return False
        
    pos.click_fuel_buffer("A")

    logger.info(f"PostPay Name of card about to be swiped: {card_name}")
    if not pos.pay_card(brand=card_group, card_name=card_name):
        logger.warning(f"Pay card failed in postpay for card: {card_name}")
        system.takescreenshot()
        return False

    #TODO Do we want to leave checking the receipt scriptside to handle fuel type/price per gallon?  Could also take it args
    if not pos.check_receipt_for(["Regular", "5.000 GAL @ $1.000/GAL $5.00", money_amount], verify=False):
        system.takescreenshot()
    else:
        return True

def prepay_sale_func(card_info = ["Visa", "Core"], dispenser_num = 1, money_amount = "5.00"):
    """Performs a prepay fuel sale.  Approve the fuel sale and pay after it is fueled.

    Args:
        card_info: card to be used for the refund
        dispenser_num: (int) the dispenser number you want to use for the sale
        money_amount = (string) the dollar amount of fuel you would like to purchase
    
    Returns:
        True if refund is successful
        False if refund fails
    """
    crindsim.set_mode("auto")
    crindsim.set_sales_target(target=money_amount)

    card_name = card_info[0]
    card_group = card_info[1]

    pos.select_dispenser(dispenser_num)
    if not pos.click_forecourt_key("Prepay", verify = False):
        logger.warning(f"Could not click Prepay on dispenenser {dispenser_num}")
        system.takescreenshot()
        return False
    pos.enter_keypad(money_amount.replace(".", ""), after="Enter")

    logger.info(f"Prepay Name of card about to be swiped: {card_name}")
    if not pos.pay_card(brand=card_group, card_name=card_name):
        logger.warning(f"Pay card failed for card {card_name}")
        system.takescreenshot()
        return False

    start_time = time.time()
    while (time.time()-start_time < 10):
        if (pos.read_journal_watermark() == 'TRANSACTION COMPLETE'):
            break
    else:
        logger.warning(f"Did not see transaction complete watermark after waiting for fueling.")
        system.takescreenshot()
        return False

    #Allow Transaction to finish before checking receipt
    time.sleep(5)

    if not pos.check_receipt_for([f"PUMP# {dispenser_num}", f"${money_amount}"]):
        logger.info(f"Receipt not displaying expected fuel total for the card: {card_name}")
        system.takescreenshot()
        return False
    return True

def overrun_sale_func(card_info = ["Visa", "Core"], dispenser_num = 1, init_money_amount = "4.00", overrun_money_amount = "5.00"):
    """Performs a overrun fuel sale.  Approve the fuel sale and pay after it is fueled.

    Args:
        card_info: card to be used for the refund
        dispenser_num: (int) the dispenser number you want to use for the sale
        init_money_amount: (string) *Must be even dollar amount* The dollar amount of fuel you would like to purchase before the overrun
        overrun_money_amount: (string) *Must be even dollar amount* The dollar amount you would like to overrun to. 
    
    Returns:
        True if refund is successful
        False if refund fails
    """
    crindsim.set_mode("auto")

    card_name = card_info[0]
    card_group = card_info[1]

    crindsim.set_sales_target("money", overrun_money_amount)

    pos.select_dispenser(dispenser_num)
    if not pos.click_forecourt_key("Prepay", verify = False):
        logger.warning(f"Could not click Prepay on dispenenser {dispenser_num}")
        system.takescreenshot()
        return False
    pos.enter_keypad(init_money_amount.replace(".", ""), after="Enter")

    logger.info(f"Card being used to pay: {card_name}")
    if not pos.pay_card(brand=card_group, card_name=card_name):
        logger.warning(f"Pay card failed for card {card_name}")
        system.takescreenshot()
        return False

    start_time = time.time()
    while (time.time()-start_time < 10):
        if (pos.read_journal_watermark() == 'TRANSACTION COMPLETE'):
            break
    else:
        logger.warning(f"Did not see transaction complete watermark after waiting for fueling.")
        system.takescreenshot()
        return False

    #Allow Transaction to finish before checking receipt
    time.sleep(5)

    #Find the difference between the overrun amount and initial amount for buffer check
    init_int = int(float(init_money_amount))
    overrun_int = int(float(overrun_money_amount))
    diff_int = overrun_int - init_int
    diff_string = 'Overrun $' + str(diff_int) + '.00'
    diff_receipt_str = '$' + str(diff_int) + '.00'

    pos.select_dispenser(dispenser_num)

    start_time = time.time()
    while time.time()-start_time < 5:
        if diff_string in pos.read_fuel_buffer():
            logger.info("Found the difference amount in the fuel buffer")
            break
    else:
        logger.warning(f"Did not see correct difference amount in fuel buffer for overrun {card_name}")
        system.takescreenshot()
        return False

    pos.click_fuel_buffer("A")

    logger.info(f"Card name to pay for overrun: {card_name}")
    if not pos.pay_card(brand=card_group, card_name=card_name):
        logger.warning(f"Pay card failed for card {card_name}")
        system.takescreenshot()
        return False

    if not pos.check_receipt_for([f"PUMP# {dispenser_num}", f"${overrun_money_amount}", f"${init_money_amount}", f"{diff_receipt_str}"]):
        logger.info(f"Receipt not displaying expected fuel total for the card: {card_name}")
        system.takescreenshot()
        return False
    return True

def underrun_sale_func(card_info = ["Visa", "Core"], dispenser_num = 1, init_money_amount = "10.00", underrun_money_amount = "5.00"):
    """Performs a underrun fuel sale.  Approve the fuel sale and pay after it is fueled.

    Args:
        card_info: card to be used for the refund
        dispenser_num: (int) the dispenser number you want to use for the sale
        init_money_amount: (string) *Must be even dollar amount* The dollar amount of fuel you would like to purchase before the overrun
        overrun_money_amount: (string) *Must be even dollar amount* The dollar amount you would like to underrun to. 
    
    Returns:
        True if refund is successful
        False if refund fails
    """
    crindsim.set_mode("auto")

    card_name = card_info[0]
    card_group = card_info[1]

    crindsim.set_sales_target("money", underrun_money_amount)

    pos.select_dispenser(dispenser_num)
    if not pos.click_forecourt_key("Prepay", verify = False):
        logger.warning(f"Could not click Prepay on dispenenser {dispenser_num}")
        system.takescreenshot()
        return False
    pos.enter_keypad(init_money_amount.replace(".", ""), after="Enter")

    logger.info(f"Prepay Name of card about to be swiped: {card_name}")
    if not pos.pay_card(brand=card_group, card_name=card_name):
        logger.warning(f"Pay card failed for card {card_name}")
        system.takescreenshot()
        return False

    start_time = time.time()
    while (time.time()-start_time < 10):
        if (pos.read_journal_watermark() == 'TRANSACTION COMPLETE'):
            break
    else:
        logger.warning(f"Did not see transaction complete watermark after waiting for fueling.")
        system.takescreenshot()
        return False

    #Allow Transaction to finish before checking receipt
    # time.sleep(5)
    pos.wait_for_fuel()

    #Find the difference between the overrun amount and initial amount for buffer check
    init_int = int(float(init_money_amount))
    underrun_int = int(float(underrun_money_amount))
    diff_int = init_int - underrun_int
    diff_string = 'Change $' + str(diff_int) + '.00'
    diff_receipt_str = '$' + str(diff_int) + '.00'

    pos.select_dispenser(dispenser_num)

    start_time = time.time()
    while time.time()-start_time < 5:
        if diff_string in pos.read_fuel_buffer():
            break
    else:
        logger.warning(f"Did not see correct difference amount in fuel buffer for underrun {card_name}")
        system.takescreenshot()
        return False

    pos.click_fuel_buffer("A")

    start_time = time.time()
    while (time.time()-start_time < 10):
        if (pos.read_journal_watermark() == 'TRANSACTION COMPLETE'):
            break
    else:
        logger.warning(f"Did not see transaction complete watermark after waiting for fueling.")
        system.takescreenshot()
        return False

    time.sleep(3)

    if not pos.check_receipt_for([f"PUMP# {dispenser_num}", f"${underrun_money_amount}", f"${init_money_amount}", f"{diff_receipt_str}"]):
        logger.info(f"Receipt not displaying expected fuel total for the card: {card_name}")
        system.takescreenshot()
        return False
    return True

def manual_fuel_sale_func(card_info = ["Visa", "Core"], dispenser_num = 1, money_amount = "5.00"):
    """Performs a manual fuel sale.  Approve the fuel sale and pay after it is fueled.

    Args:
        card_info: card to be used for the refund
        dispenser_num: (int) the dispenser number you want to use for the sale
        init_money_amount: (string) *Must be even dollar amount* The dollar amount of fuel you would like to purchase before the overrun
        overrun_money_amount: (string) *Must be even dollar amount* The dollar amount you would like to underrun to. 
    
    Returns:
        True if refund is successful
        False if refund fails
    """
    crindsim.set_mode("auto")

    card_name = card_info[0]
    card_group = card_info[1]

    if not crindsim.set_sales_target("money", money_amount):
        logger.warning("Failed to set sales target on crind sim")
        return False

    pos.select_dispenser(dispenser_num)
    if not pos.click_forecourt_key("Manual Sale", verify = False):
        logger.warning(f"Could not click Prepay on dispenenser {dispenser_num}")
        system.takescreenshot()
        return False
    pos.click_message_box_key("Diesel 1", timeout = 3, verify=False)
    pos.enter_keypad(money_amount.replace(".", ""), after="Enter")

    logger.info(f"Prepay Name of card about to be swiped: {card_name}")
    if not pos.pay_card(brand=card_group, card_name=card_name):
        logger.warning(f"Pay card failed for card {card_name}")
        system.takescreenshot()
        return False

    start_time = time.time()
    while (time.time()-start_time < 10):
        if (pos.read_journal_watermark() == 'TRANSACTION COMPLETE'):
            break
    else:
        logger.warning(f"Did not see transaction complete watermark after waiting for fueling.")
        system.takescreenshot()
        return False

    #Allow Transaction to finish before checking receipt
    time.sleep(3)

    if not pos.check_receipt_for([f"PUMP# {dispenser_num}", f"${money_amount}"]):
        logger.info(f"Receipt not displaying expected fuel total for the card: {card_name}")
        system.takescreenshot()
        return False
    return True

def manual_fuel_card_based_discount_sale_func(card_info = ["Visa", "Core"], dispenser_num = 1, money_amount = "10.00", discount_name = "CardDiscount"):
    """Performs a manual fuel sale.  Approve the fuel sale and pay after it is fueled.

    Args:
        card_info: card to be used for the refund
        dispenser_num: (int) the dispenser number you want to use for the sale
        init_money_amount: (string) *Must be even dollar amount* The dollar amount of fuel you would like to purchase before the overrun
        overrun_money_amount: (string) *Must be even dollar amount* The dollar amount you would like to underrun to. 
    
    Returns:
        True if refund is successful
        False if refund fails
    """
    crindsim.set_mode("auto")

    card_name = card_info[0]
    card_group = card_info[1]

    if not crindsim.set_sales_target("money", money_amount):
        logger.warning("Failed to set sales target on crind sim")
        return False

    pos.select_dispenser(dispenser_num)
    if not pos.click_forecourt_key("Manual Sale", verify = False):
        logger.warning(f"Could not click Prepay on dispenenser {dispenser_num}")
        system.takescreenshot()
        return False
    pos.click_message_box_key("Diesel 1", timeout = 3, verify=False)
    pos.enter_keypad(money_amount.replace(".", ""), after="Enter")

    logger.info(f"Prepay Name of card about to be swiped: {card_name}")
    if not pos.pay_card(brand=card_group, card_name=card_name):
        logger.warning(f"Pay card failed for card {card_name}")
        system.takescreenshot()
        return False

    start_time = time.time()
    while (time.time()-start_time < 10):
        if (pos.read_journal_watermark() == 'TRANSACTION COMPLETE'):
            break
    else:
        logger.warning(f"Did not see transaction complete watermark after waiting for fueling.")
        system.takescreenshot()
        return False

    #Allow Transaction to finish before checking receipt
    time.sleep(3)

    if not pos.check_receipt_for([f"PUMP# {dispenser_num}", f"${money_amount}"], discount_name):
        logger.info(f"Receipt not displaying expected fuel total for the card: {card_name}")
        system.takescreenshot()
        return False
    return True

@pinpad_retry
def refund_items(card_info = ["Visa", "Core"], invoice_num = None):
    """
    #NOTE If refund_func is expanded, this must also be expanded

    Args:
        card_info: card to be used for the refund
        invoice_num: invoice number associated with the sale made with the passed in card
    
    Returns:
        True if refund is successful
        False if refund fails
    """
    logger.info(f"Card being used for refund: {card_info[0]}")
    if not pos.pay_card(brand=card_info[1], card_name=card_info[0], verify=False):
        logger.info(f"Failed pay_card after refund with {card_info[0]}")
        return False
    else:
        logger.info(f"Successful pay_card after refund with {card_info[0]}")
    logger.info(f"Entering invoice num: {invoice_num}")
    pos.enter_keypad(invoice_num, after = "Enter")

    start_time = time.time()
    while (time.time()-start_time <5):
        if pos.read_journal_watermark() == 'TRANSACTION COMPLETE':
            break
    else:
        logger.info(f"Refund for {card_info[0]} did not complete after entering invoice.")
        return False
    
    return True


@pinpad_retry
def pay_card_decline(brand='Core', card_name='Visa', debit_fee=False, cashback_amount=None, zip_code=None, cvn=None, custom=None, split_tender=False, decline_prompt=None):
    """
    Pay out tranaction with card and checks for expected decline message.
    
    Args:
        brand   : (str) String representation of the Brand (found in CardData.json)
        card_name : (str) The key/name of the card you wish to use located in the CardData.json file.
        debit_fee : (bool) If Debit Fee is prompted and set to True, we click OK; otherwise, we click No.
        cashback_amount: (str) The cashback amount you wish to enter
        zip_code : (str) The ZIP code value you wish to enter
        custom : (str) The Custom prompt value you wish to enter
        split_tender: (bool) Set True if you are expecting the host to trigger split payment (i.e. gift card with insufficient balance)
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
        decline_prompt: The expected string in the message box after a declined card swipe   
    
    Returns:
        bool: True if success, False if fail
    
    Examples:
        >>> pay_card_decline(
                brand='Core',
                card_name='VisaFleet1_FuelOnly',
                decline_prompt: 'Fuel Only Card'
            )
        True
    """
    #Determine payment type (swipe or insert)
    payment_type = None
    if ("EMV") in card_name:
        payment_type = "insert"
        logger.info("Inserting card for payment.  Card name: " + card_name)
    else:
        payment_type = "swipe"
        logger.info("Swiping card for payment.  Card name: " + card_name)
    
    #Call private function
    if _pay_card_decline(method = payment_type,brand = brand,card_name = card_name,debit_fee=debit_fee,cashback_amount=cashback_amount,zip_code=zip_code,cvn=cvn,custom=custom,split_tender=split_tender, decline_prompt=decline_prompt):
        return True
            

def _pay_card_decline(method='swipe', brand='Core', card_name='Visa', debit_fee=False, cashback_amount=None, zip_code=None, cvn=None, custom=None, split_tender=False, decline_prompt=None):
    """
    Support function for pay_card_decline.  Performs the payment with card and checking for expected decline prompt.
    
    Args:
        method: (str) the card payment method: swipe or insert
        brand   : (str) String representation of the Brand (found in CardData.json)
        card_name : (str) The key/name of the card you wish to use located in the CardData.json file.
        debit_fee : (bool) If Debit Fee is prompted and set to True, we click OK; otherwise, we click No.
        cashback_amount: (str) The cashback amount you wish to enter
        zip_code : (str) The ZIP code value you wish to enter
        custom : (str) The Custom prompt value you wish to enter
        split_tender: (bool) Set True if you are expecting the host to trigger split payment (i.e. gift card with insufficient balance)
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
        decline_prompt: The expected string in the message box after a declined card swipe
    
    Returns:
        bool: True if success, False if fail
    
    Examples:
        >>> _pay_card_decline(
                brand='Core',
                card_name='VisaFleet1_FuelOnly'
            )
        True
        >>> _pay_card_decline(card_name="some_card_not_in_CarData.json")
        False
    """
    logger.info("Entered _pay_card() method")

    if not ( method == 'swipe' or method == 'insert' ):
        logger.error(f"Invalid payment method {method}")
        return False

    if not pos.click_function_key('Pay', verify=False):
        logger.info("COULD NOT HIT PAY")
        return False  

    logger.info("Looking for Loyalty popup message")
    if pos._is_element_present(pos.PROMPT['body']):
        logger.info("Clicking no for loyalty prompt")
        pos.click_message_box_key(key='No', verify=False)

    #Variable wait to ensure the tender key for card was clicked before continuing with the payment
    tender_time = time.time()
    while time.time()-tender_time < 5:
        if pos.click_tender_key("Card", verify=False): #TODO Once timeout of click_tender_key is fixed, remove while else
            break
    else:
        logger.info("Could not click card tender key")
        return False

    # Verify that pinpad payment is initiated
    if method == 'swipe':
        logger.info("Verifying the card type transaction is initiated. Looking for pinpad panel in POS")
        if not ( pos._is_element_present(pos.PAYMENT_PROC['panel'], timeout = 10) or 
                ("Swipe" not in pos._get_text(pos.PAYMENT_PROC['text']) and "Card" not in pos._get_text(pos.PAYMENT_PROC['text']))):
            logger.error("The Pinpad payment was not initiated before timeout.")
            return False
    
    # Verify that pinpad payment is initiated
    if method == 'insert':
        logger.info("Verifying the card type transaction is initiated. Looking for pinpad panel in POS")
        if not ( pos._is_element_present(pos.PAYMENT_PROC['panel'], timeout = 10) or 
                ("Insert" not in pos._get_text(pos.PAYMENT_PROC['text']) and "Card" not in pos._get_text(pos.PAYMENT_PROC['text']))):
            logger.error("The Pinpad payment was not initiated before timeout.")
            return False
    
    #Variable wait to ensure the prompt for inserting/swiping the card is up before trying to swipe a card
    insert_time = time.time()
    swipe_text_list = ["Swipe", "Card"]
    logger.info("Waiting up to 5 seconds for prompt to insert card.")
    try:
        while time.time()-insert_time < 5:
            if (swipe_text in pos._get_text(pos.PAYMENT_PROC['text']) for swipe_text in swipe_text_list):
                logger.info("Have read the insert card prompt.")
                break
        else:
            logger.info("Prompt for inserting card never showed.")
            return False
        if method == 'swipe':
            logger.info("Trying to swipe a card")
            payload = pos.pinpad.swipe_card(
                brand=brand,
                card_name=card_name,
                debit_fee=debit_fee,
                cashback_amount=cashback_amount,
                zip_code=zip_code,
                cvn=cvn,
                custom=custom
            )
                
        elif method == 'insert':
            logger.info("Trying to insert a card")
            payload = pos.pinpad.insert_card(
                brand=brand,
                card_name=card_name,
                debit_fee=debit_fee,
                cashback_amount=cashback_amount,
                zip_code=zip_code,
                cvn=cvn,
                custom=custom
            )
    except Exception as e:
        logger.error(f"Card swipe in pay_card failed. Exception: {e}")
        # TODO Do we want to cancel it??
        logger.info("Trying to Cancel the transaction")
        pos.click_function_key("Cancel", verify=False)
        return False
        
    message_time = time.time()           
    while (time.time()-message_time < 10):
        if (pos.read_message_box() != None):
            if (decline_prompt in pos.read_message_box()):
                break
    else:
        logger.info("Message box with expected decline wasn't present after timeout")
        return False

    pos.pinpad.reset()
    pos.click_message_box_key("Ok")
    pos.void_transaction()

    start_time = time.time()
    while(time.time() - start_time < 5):
        #Make sure 'Transaction Voided' is displayed in receipt watermark so pos is ready for next transaction
        if pos._get_text('//*[@id="transaction_void_watermark"]') == 'TRANSACTION\nVOIDED':
            break
    else:
        logger.info("Did not display transaction voided watermark after voiding.  Waited 5 secs.")
        return False

    return True

@pinpad_retry
def manual_entry_decline(brand='Core', card_name='Visa', expiration_date="1230", zip_code=None, custom=None, split_tender=False, decline_prompt=None):
    """
    Pay out tranaction expected to be declined using Manual entry.  Checks for decline message to match passed in decline_prompt
    
    Args:
        brand   : (str) String representation of the Brand (found in CardData.json)
        card_name : (str) The key/name of the card you wish to use located in the CardData.json file.
        expiration_date : (str) The string representation of expiration date for card that'll be entered on POS.
        zip_code : (str) The ZIP code value you wish to enter
        custom : (str) The Custom prompt value you wish to enter
        split_tender: (bool) Set True if this payment will not complete the transaction.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
        decline_prompt: (str) Expected fail message after entering a card
    
    Returns:
        bool: True if success, False if fail
    
    Examples:
        >>> manual_entry_decline(
                brand='Core',
                card_name='Expired_Visa',
                decline_prompt='Expired Card: Try Another'
            )
        >>> manual_entry_decline(
                brand='Core',
                card_name='Expired_Visa',
                decline_prompt='Some wrong decline message'
            )    
        False
    """
    if not pos.click_function_key('Pay'):
        return False

    if not pos.click_tender_key("Card"):
        return False

    if pos._is_element_present(pos.PROMPT['body']): # Loyalty
        pos.click_message_box_key(key='No', verify=False)
    
    if not pos.click_function_key("Manual", verify=False):
        logger.warning("Unable to click Manual button")
        return False
    
    try:
        payload = pos.pinpad.manual_entry(
            brand=brand,
            card_name=card_name,
            zip_code=zip_code,
            custom=custom
        )
    except Exception as e:
        logger.warning(f"Manual entry failed. Exception: {e}")
        pos.click_function_key("Cancel", verify=False)
        return False

    if not pos.click_message_box_key(key='Yes', verify=False):
        logger.warning("Unable to click yes for confirming Account Number")
        return False
    
    pos.click_message_box_key(key="No", verify=False)

    if expiration_date[2] == '/':
        expiration_date = expiration_date.replace('/', '')
    if not pos.enter_keypad(expiration_date, verify=False):
        return False
            
    if not pos.click_keypad('Enter', verify=False):
        return False

    message_time = time.time()           
    while (time.time()-message_time < 10):
        if (pos.read_message_box() != None):
            if (decline_prompt in pos.read_message_box()):
                break
    else:
        logger.info("Message box with expected decline wasn't present after timeout")
        return False

    pos.pinpad.reset()
    pos.click_message_box_key("Ok")
    pos.void_transaction()
    return True