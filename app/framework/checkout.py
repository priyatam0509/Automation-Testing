"""
Name: checkout
Description: This is a process to use the keys for the Self-Checkout POS. This is
            for general use.

Date created: 03/13/2018
Modified By:
Date Modified:
"""

# Selenium modules
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, SessionNotCreatedException, ElementClickInterceptedException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait

# Third party modules
import time
import json
import logging

# In house modules
from app import pinpad, runas
from app.util import constants
from app.simulators.ip_scanner import IPScanner
from app.framework.tc_helpers import test_func

# Log object
logger = logging.getLogger()

# Scanner object
# TODO: This will only be setup once with a 5 second timeout when this module is imported. If scanner gets setup AFTER this module is imported, we need to check DB to see if it is setup or not.
scanner = IPScanner(ip="10.5.48.2")

# Retry and Timeouts
driver_timeout  = 2
default_timeout = 1.5
prompt_timeout  = 10
key_timeout     = 0.5
pay_timeout     = 7
pinpad_timeout  = 10

# JSON file paths
controls_path  = constants.CONTROLS_SCO

# Self Checkout config file
sco_xml                 = r"C:\Passport\ExpressLane\bin\SCPOSStart.exe.config"

# Selenium objects
driver  = None
wait    = None

# Edge element locators and button names
with open(controls_path) as f:
    controls = json.load(f)

WELCOME = controls['Welcome']
SPEED_KEYS = controls['Speed Keys']
FUNC_KEYS = controls['Function Keys']
PAYMENT_KEYS = controls['Payment Keys']
CARD_PROCESSING = controls['Card Processing']
MSG_BOX = controls['Message Box']
PROMPT_BOX = controls['Prompt Box']
QUALIFIERS = controls['Qualifiers']
LOYALTY_KEYS = controls['Loyalty']
KEYPAD = controls['Keypad']
HELP = controls['Help']
WEIGHTS_MEASURES = controls['Weights and Measures']
RCPT_JOURNAL = controls['Receipt Journal']

def connect(url="https://POSCLIENT001:8765/"):
    """
    Initializes Chrome driver instance and navigates to self checkout.
    Args:
        None
    Returns:
        True if success, False if failure
    Examples:
        >>> connect()
        True
        >>> connect()
        False
    """
    global driver, wait

    # Run SCO executable
    # TODO : this needs to be ran on the Client.
    # runas.run_as(
    #     cmd=r"C:\Passport\ExpressLane\bin\SCPOSStart.exe",
    #     ignore_stdout=True
    # )

    # Edit the XML file so the .exe doesn't stop when payment goes offline
    if not edit_sco_xml():
        logger.warning(f"Unable to edit the settings for {sco_xml}")
     
    if driver is None:
        try:
            options = webdriver.ChromeOptions()
            options.add_experimental_option('w3c', False)
            options.add_argument("ignore-certificate-errors")
            driver = webdriver.Chrome(constants.CHROME_DRIVER, chrome_options=options)
        except WindowsError:
            logger.warning(f"Unable to locate {constants.CHROME_DRIVER}")
            return False
        except SessionNotCreatedException as e:
            logger.warning(f"Unable to instantiate chrome driver: {e}")
            return False

        try:
            driver.get(url)
        except:
            logger.warning("Unable to open web page.")
            return False

        # Verify Express Lane page loads
        if "Express Lane" not in driver.title:
            logger.warning("Opened a web page, but it wasn't Express Lane. Check Passport status and URL.")
            return False

        wait = WebDriverWait(driver, timeout=driver_timeout, poll_frequency=1.0)
        driver.maximize_window()
        return True
    else:
        logger.debug(f"Already connected to a chrome driver instance")
        return True

def close():
    try:
        global driver
        driver.close()
        driver = None
        return True
    except:
        logger.warning("Unable to close chrome driver instance")
        return False

def get_to_mws(sign_in=True):
    """
    Closes chrome instance and navigates to the MWS.
    Args:
        None
    Returns:
        True if success, False if failure
    Examples:
        >>> get_to_mws(sign_in=True)
        True
        >>> get_to_mws(sign_in=True)
        False
    """
    try:
        return close()
        # TODO : do we want to connect to MWS after closing browser?
        # TODO : we should not have sign in here (so I commented it out). what if user does not want to sign in?
        # if sign_in:
        #     return mws.sign_on()
        # else:
        #     return True
    except:
        logger.warning("Unable to close chrome driver instance")
        return False

def get_to_pos(timeout=1, sign_on=False):
    return connect()

@test_func
def add_prepay(amount, dispenser=1):
    """
    Add a prepay to the current transaction.
    Args:
        amount: (str) The dollar amount of fuel to purchase.
        dispenser: (int) The ID of the dispenser to put the prepay on.
    Returns: (bool) True/False for success/failure
    Examples:
        >>> add_prepay("$10.00")
        True
        >>> add_prepay("35.00", 2)
        True
    """
    amount = amount.replace("$", "").replace(".", "")
    if not click_function_key("Fuel"):
        return False
    if not click_key(controls['Prompt Box']['Prepay']):
        return False
    # wait_disp_ready(dispenser, verify=False)
    if not select_dispenser(dispenser, verify=False):
        click_payment_key("Back")
        return False
    if not click_prompt_key("Enter Value", verify=False):
        return False
    if not enter_keypad(amount, verify=False):
        return False
    if not click_keypad("Enter", verify=False):
        return False
    if not click_prompt_key("Yes", verify=False):
        return False

    return True

@test_func
def add_postpay(dispenser=1, sale_num=1):
    """
    Add a pending postpay to the current transaction.
    Args:
        dispenser: (int) The ID of the dispenser holding the postpay.
        sale_num: (int) If the dispenser is holding multiple postpays, use this to select the 1st/2nd/3rd.
    Returns: (bool) True/False for success/failure
    Examples:
        >>> add_postpay()
        True
        >>> add_postpay(2, 2)
        True
    """
    if not click_function_key("Fuel"):
        return False
    if not click_key(controls['Prompt Box']['Postpay']):
        return False
    # wait_disp_ready(dispenser, verify=False)
    if not select_postpay(dispenser, sale_num, verify=False):
        click_payment_key("Back")
        return False
    if not click_prompt_key("Yes", verify=False):
        return False

    return True

@test_func
def click_welcome_key(key, timeout=default_timeout):
    """
    Clicks a key on Welcome Screen
    Args:
        None
    Returns:
        True if success, False if failure
    """
    return click_key(WELCOME[key], timeout=timeout)

@test_func
def enter_keypad(values):
    """
    Enter value on numerical keypad for item prompts, etc.
    Args:
        values: (str) The value you want to enter into keypad.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> enter_keypad_value("$1.00")
        True
        >>> enter_keypad_value("123")
        True
        >>> enter_keypad_value("SomeText")
        False
    """
    values = _strip_currency(values) # Just in case.
    try:
        for value in str(values):
            click_keypad(str(value), timeout=.5, verify=False)
        return True
    except:
        logger.warning("Unable to enter %s on keypad" %(values))
        return False

@test_func
def swipe_loyalty(brand='Core', card_name='Loyalty'):
    """
    Select yes to loyalty prompt and swipes loyalty card.
    Args:
        brand : (str) String representation of the Brand (found in CardData.json)
        card_name : (str) The key/name of the card you wish to use located in the CardData.json file.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Return:
        bool: True if success, False if failure
    Examples:
        >>> swipe_loyalty(brand='Core', card_name="Loyalty")
        True
        >>> swipe_loyalty(brand='Core', card_name="Visa")
        False
    """
    if not click_function_key('Pay'):
        return False

    if _is_element_present(PROMPT_BOX['Heading']):
        if not click_prompt_key('Yes'):
            return False
            
        payload = pinpad.swipe_loyalty(
            brand=brand,
            card_name=card_name
        )
        start_time = time.time()
        while time.time() - start_time <= pinpad_timeout:
            try:
                if payload['success'] and _is_element_present(CARD_PROCESSING["PINPad Image"]):
                    return True
            except:
                continue
        else:
            logger.warning(f"Unable to swipe loyalty card {card_name}")
            return False
    else:
        return False

@test_func
def pay_card(brand='Core', card_name='Visa', debit_fee=False, cashback_amount=None, zip_code=None, cvn=None, custom=None, split_tender=False):
    """
    Pay out tranaction with swiping card.
    Args:
        brand   : (str) String representation of the Brand (found in CardData.json)
        card_name : (str) The key/name of the card you wish to use located in the CardData.json file.
        debit_fee : (bool) If Debit Fee is prompted and set to True, we click OK; otherwise, we click No.
        cashback_amount: (str) The cashback amount you wish to enter
        zip_code : (str) The ZIP code value you wish to enter
        cvn : (str) The CVN value you wish to enter
        custom : (str) The Custom prompt value you wish to enter
        split_tender : (bool) If True, accept split pay; otherwise, decline it
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if fail
    Examples:
        >>> pay_card(
                brand='Citgo',
                card_name='GiftCard'
            )
        True
        >>> pay_card(
            brand='Core',
            card_name='Debit',
            debit_fee=True,
            cashback_amount='10.00'
        )
        >>> pay_card(
            brand='Core',
            card_name='VisaFleet_NoRestrictions_1',
            zip_code='27587',
            cvn='123'
        )
        >>> pay_card(card_name="some_card_not_in_CarData.json")
        False
    """
    # TODO : match loyalty prompt text to see if it is there once, Merlin gets the sco html finalized.
    if not _is_element_present(CARD_PROCESSING['PINPad Image']):
        if not click_function_key('Pay'):
            return False
        if _is_element_present(PROMPT_BOX["Heading"]):
            if not click_prompt_key('No'):
                return False

    payload = pinpad.swipe_card(
        brand=brand,
        card_name=card_name,
        debit_fee=debit_fee,
        cashback_amount=cashback_amount,
        zip_code=zip_code,
        cvn=cvn,
        custom=custom
    )
    # Wait until transaction is fully finished.
    start_time = time.time()
    while time.time() - start_time <= pinpad_timeout: # TODO : how long do we want to wait?
        try:
            if payload['success'] and not _is_element_present(CARD_PROCESSING['PINPad Image']):
                # Answer receipt prompt if it appears.
                if _is_element_present(PROMPT_BOX["Heading"]):
                    if not click_prompt_key('No'):
                        return False
                break
            # TODO : Has not been tested. I know this will fail as the 'Yes' and 'No'
            # button text are "weird". Instead of "Yes" it is "\n\n\nYes"..
            # When I run into this scenario, I will fix this.
            elif "SPLIT PAY" in _get_text(PROMPT_BOX['Message']).upper():
                if split_tender:
                    if not click_prompt_key('Yes'): 
                        logger.warning("Unable to click 'Yes' for Split Pay") 
                        return False
                    else:
                        logger.info("Clicked Yes for Split Pay")
                        return True
                else:
                    if not click_prompt_key('No'):
                        logger.warning("Unable to click 'No' for Split Pay")
                        return False
                    else:
                        logger.info("Clicked No for Split Pay")
                        return True
        except:
            continue
    else:
        logger.warning(f"Unable to pay with {card_name}")
        return False

    msg = read_message_box()
    if msg:
        logger.warning(f"Got an error after payment: {msg}")
        return False

    return True

# TODO : needs to be tested.
@test_func
def insert_card(brand='Core', card_name='EMVVisaCredit', debit_fee=False, cashback_amount=None, zip_code=None, cvn=None, custom=None, split_tender=False):
    """
    Pay out tranaction with inserting EMV card.
    Args:
        brand   : (str) String representation of the Brand (found in CardData.json)
        card_name : (str) The key/name of the card you wish to use located in the CardData.json file.
        debit_fee : (bool) If Debit Fee is prompted and set to True, we click OK; otherwise, we click No.
        cashback_amount: (str) The cashback amount you wish to enter
        zip_code : (str) The ZIP code value you wish to enter
        cvn : (str) The CVN value you wish to enter
        custom : (str) The Custom prompt value you wish to enter
        split_tender : (bool) If True, accept split pay; otherwise, decline it
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if fail
    Examples:
        >>> insert_card(
                brand='Citgo',
                card_name='EMVVisaCredit'
            )
        True
        >>> insert_card(card_name="some_card_not_in_CarData.json")
        False
    """
    # TODO : match loyalty prompt text to see if it is there once, Merlin gets the sco html finalized.
    if not _is_element_present(CARD_PROCESSING["PINPad Image"]):
        if not click_function_key('Pay'):
            return False
        if _is_element_present(PROMPT_BOX["Heading"]):
            if not click_prompt_key('No'):
                return False

    payload = pinpad.insert_card(
        brand=brand,
        card_name=card_name,
        debit_fee=debit_fee,
        cashback_amount=cashback_amount,
        zip_code=zip_code,
        cvn=cvn,
        custom=custom
    )
    # Wait until transaction is fully finished.
    start_time = time.time()
    while time.time() - start_time <= pinpad_timeout: # TODO : how long do we want to wait?
        try:
            if payload['success'] and not _is_element_present(CARD_PROCESSING["PINPad Image"]):
                return True
            # TODO : Has not been tested. I know this will fail as the 'Yes' and 'No'
            # button text are "weird". Instead of "Yes" it is "\n\n\nYes"..
            # When I run into this scenario, I will fix this.
            elif "SPLIT PAY" in _get_text(PROMPT_BOX["Message"]).upper():
                if split_tender:
                    if not click_prompt_key('Yes'):
                        logger.warning("Unable to click 'Yes' for Split Pay")
                        return False
                    else:
                        logger.info("Clicked Yes for Split Pay")
                        return True
                else:
                    if not click_prompt_key('No'):
                        logger.warning("Unable to click 'No' for Split Pay")
                        return False
                    else:
                        logger.info("Clicked No for Split Pay")
                        return True
        except:
            continue
    else:
        logger.warning(f"Unable to pay with {card_name}")
        return False

"""
Scanner functions
"""
@test_func
def scan_item(barcode):
    """
    Scans an item using IP bar code scanner
    Args:
        barcode : (str) The barcode you wish to send
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if failure
    """
    return scanner.scan(barcode)

@test_func
def scan_id(barcode):
    """
    Scans driver's license using IP bar code scanner
    Args:
        barcode : (str) The barcode you wish to send
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if failure
    """
    return scanner.scan(barcode)

@test_func
def click(key, timeout=default_timeout):
    """
    Click almost any key on the POS. Searches all windows that the requested key may exist in.
    If this doesn't work for your desired key, you may need one of this module's more specialized
    click functions.
    Args:
        key: (str) The text of the key to click.
        timeout: (int) How long to search for the key before failing.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if failure.
    Examples:
        >>> click("PRICE CHECK")
        True
        >>> click("Enter")
        True
        >>> click("Not a real key")
        False
    """
    WILD = "**" # Indicates places where keys can have variable text.
    WILDNUM = "##" # Variable number

    # Map of functions and the keys they may be used to click on.
    map = { "click_function_key": ['KEY IN CODE', 'HELP', 'PAY'],
            "click_welcome_key": ['START'],
            "click_help_key": ['REQUEST ASSISTANCE', 'BACK', 'WEIGHTS AND MEASURES'],
            "click_weights_measures_key": ['BACK'],
            "click_payment_key": ['BACK', 'HELP'],
            "click_loyalty_key": ['ENTER ID'],
            "click_message_box_key": ['OK', 'YES', 'NO'],
            "click_prompt_key": ['OK', 'YES', 'NO'],
            "click_speed_key": ['GENERIC ITEM', WILD],
            "click_keypad": ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '00', 'BACK', 'CLEAR', 'CANCEL', 'ENTER']
          }

    # Figure out which functions might work for the desired key
    def build_func_list(key):
        import sys
        funcs_to_try = []
        for func in map:
            if key.upper() in map[func]:
                funcs_to_try.append(getattr(sys.modules[__name__], func))
        return funcs_to_try

    # Create list of functions to search with
    funcs_to_try = build_func_list(key)
    if len(funcs_to_try) == 0:
        # Requested key doesn't match any known menus, try menus that can have custom keys
        if key.isdigit():
            funcs_to_try = build_func_list(WILDNUM) # Menus that are likely to have buttons with varied numbers
        else:
            funcs_to_try = build_func_list(WILD) # Menus that can contain buttons with any text
    
    # Invoke the functions repeatedly until success or timeout
    start_time = time.time()
    while time.time() - start_time <= timeout:
        for func in funcs_to_try:
            if func(key, timeout=0, verify=False):
                return True
    else:
        logger.warning("Couldn't find %s within %d seconds." % (key, timeout))
        return False

@test_func
def enter_plu(plu, timeout=default_timeout):
    """
    Enter a PLU on the POS keypad and press Enter.
    Args:
        plu: (str) The PLU to enter.
        timeout: (int) How many seconds to wait for the keypad to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> enter_plu("1234")
        True
        >>> enter_plu("789asdf")
        False
    """
    try:
        click_function_key("Key In Code", verify=False)
        enter_keypad(plu)
        click_keypad('Enter', verify=False)
        not_found = _item_not_found(item=plu)
        if not_found:
            logger.warning("Item [%s] not found." %(plu))
            return False
        else:
            return True
    except:
        logger.warning("Unable to enter [%s] PLU" %(plu))
        return False

"""
Read functions
"""
def read_message_box(timeout=default_timeout):
    """
    Read the text of the red popup message on the POS, if it exists.
    Args:
        timeout: (int) The time (in seconds) that the function will look for the window's visibility.
    Returns:
        str: The message in the message box
    Examples:
        >>> read_message_box()
        'Are you sure you want to void the transaction?'
        >>> read_message_box() # While no message box is visible
        None
    """
    start_time = time.time()
    while time.time() - start_time <= timeout:
        try:
            if _is_element_present(controls['Message Box']['Message']):
                return _get_text(controls['Message Box']['Message'])
        except:
            continue
    else:
        logger.warning("Could not get text of message box")
        return None

def read_transaction_journal(element=None, timeout=default_timeout):
    """
    Get the text of the transaction journal. Please note that
    this may not work if a list dialog is open (qualifiers,
    reason codes, etc).
    Args:
        element: (int) Which element of the journal to read, if a specific one is desired.
        timeout: (int) How long to wait for the window to be available.
    Returns:
        list: The strings contained in the journal element, or a list of lists containing each element.
    Examples:
        >>> read_transaction_journal()
        [['Generic Item', '$0.01'], ['Item 4', '$3.00'], ['Item 1', '$5.00']]
        >>> read_transaction_journal(2)
        ['Item 4', '$3.00']
    """    
    journal_list = []
    contents = _get_text(RCPT_JOURNAL["Items"]).replace("\n", " ")
    
    while len(contents) > 0:
        start = 0
        dollar = contents.find("$")
        end = contents.find(" ", dollar)
        item = contents[start:dollar-1]
        if end == -1:
            end = len(contents)
        price = contents[dollar:end]
        journal_list.append(item)
        journal_list.append(price)
        contents = contents[end+1:]

    journal_list_list = []
    i = 0
    while i < len(journal_list):
        journal_list_list.append(journal_list[i:i+2])
        i+=2
    
    if element is not None:
        if element == 0: element = 1
        return journal_list_list[element-1]
    
    return journal_list_list

def read_balance(timeout=default_timeout):
    """
    Get the transaction totals: subtotal, tax, basket count, total, and
    balance/change.
    Args:
        timeout: (int) How long to wait for the window to be available.
    Returns:
        dict: A dictionary mapping each text element to its corresponding
              value.
    Examples:
        >>> read_balance()
        {'Basket Count': '1', 'Total': '$0.01', 'Change Due': '$0.00'}
        >>> read_balance()
        {'Basket Count': '2', 'Total': '$10.00', 'Balance Due': '$10.00'}
    """
    text = {}
    balance_str = ['Subtotal', 'Tax', 'Basket Count', 'Total', 'Balance Due', 'Change Due']
    contents = _get_text(RCPT_JOURNAL["Totals"]).replace("\n", " ")
    
    receipt_contents = {}
    try:
        for i in range(0, len(balance_str)):
            if balance_str[i] in contents:
                len_of_str = len(balance_str[i])
                if balance_str[i] == 'Basket Count':
                    start = contents.find(balance_str[i])
                    start += len_of_str + 1
                    end = contents.find(" ", start)
                else:
                    start = contents.find(balance_str[i])
                    start += len_of_str + 1
                    end = start + 6  # $xx.xx     
                receipt_contents.update({balance_str[i] : contents[start:end]})
    except:
        logger.warning("Unable to read receipt contents")    
    return receipt_contents

@test_func
def check_balance_for(elements, timeout=default_timeout):
    """
    Check for the presence of desired values in the transaction balance.
    Args:
        elements: (dict) The elements to check and their desired values.
        verify: (bool) Whether or not to fail the current test case if this returns False. Defaults to True.
    Returns:
        (bool) Whether or not all elements were matched within the time limit.
    Examples:
        >>> check_balance_for({"Total": "$5.00", "Balance Due": "$5.00"})
        True
        >>> check_balance_for({"Subtotal": "$10.00", "Tax": "$1.00", "Total": "$11.00"})
        True
        >>> check_balance_for({"Change Due": "$12.34"})
        False
    """
    balance = {}

    start_time = time.time()
    while time.time() - start_time >= timeout:
        balance = read_balance(timeout=0)
        if all([element in balance.items() for element in elements]):
            log.debug(f"All desired balance elements {elements} were found.")
            return True

    log.warning(f"Not all desired balance elements were found within {timeout} seconds.")
    log.warning(f"Expected: {elements}")
    log.warning(f"Actual: {balance}")
    return False

def read_keypad_entry(timeout=default_timeout):
    """
    Read the current entry in the text field above the keypad.
    Args:
        timeout: (int) How long to wait for the window to be available.
    Returns:
        str: The contents of the field.
    Examples:
        >>> read_keypad_entry()
        '10.00'
        >>> read_keypad_entry()
        ''
    """
    return _get_text(KEYPAD["Display"])

def read_weights_and_measures(timeout=default_timeout):
    """
    Read the information on the Weights and Measures screen
    Args:
       timeout: (int) How long to wait for the window to be available.
    Returns:
        dict : Dictionary containing the weights and measures information. 
    Examples:
        >>> {
                'Model #': '(Unknown)',
                'Serial #': '(Unknown)',
                'NTEP CC No.': 'NTEP CC No. 02-039'
            }
        >>> {}
    """
    if _find_element(WEIGHTS_MEASURES["Model #"]):
        start_time = time.time()
        while time.time() - start_time <= timeout:
            try:
                model_header = _get_text(WEIGHTS_MEASURES["Model # Header"]) if _find_element(WEIGHTS_MEASURES["Model # Header"]) else ""
                serial_header = _get_text(WEIGHTS_MEASURES["Serial # Header"]) if _find_element(WEIGHTS_MEASURES["Serial # Header"]) else ""
                ntep_header = _get_text(WEIGHTS_MEASURES["NTEP CC No. Header"]) if _find_element(WEIGHTS_MEASURES["NTEP CC No. Header"]) else ""
                if model_header == "" or serial_header == "" or ntep_header== "": # Headers should have values
                    continue
                else:
                    return {
                        model_header : _get_text(WEIGHTS_MEASURES["Model #"]),
                        serial_header : _get_text(WEIGHTS_MEASURES["Serial #"]),
                        ntep_header : _get_text(WEIGHTS_MEASURES["NTEP CC No."])
                    }
            except:
                continue
        else:
            logger.warning(f"Couldn't find Weights and Measures screen's contents")
            return {}    
    else:
        logger.warning(f"Couldn't find Weights and Measures screen's contents")
        return {}

"""
Misc. click/select functions
"""
@test_func
def click_journal_item(item='', instance=1, timeout=default_timeout+1):
    """
    Click on an item in the transaction journal. Please note that
    this may not work if a list dialog is open (qualifiers,
    reason codes, etc).
    Args:
        item: (str) Text identifying the item or transaction to select.
                This can be the name, price, etc.
        instance: (int) Index of item to select if there are multiple matches
                    or if no text is specified. Note that Begin/End Transaction
                    count as items in the journal.
        timeout: (int) How long to wait for the window to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: Whether or not the item was successfully selected
    Examples:
        >>> click_journal_item("$5.00")
        True
        >>> click_journal_item("Generic Item", instance=2)
        True
        >>> click_journal_item(instance=3)
        True
        >>> click_journal_item("NotInTheJournal")
        False
    """
    xpath = RCPT_JOURNAL["line"].replace('<text>', item).replace('<instance>', str(instance))
    return click_key(xpath, timeout=timeout)

@test_func
def select_qualifier(qualifier=None, timeout=default_timeout):
    """
    Click on a button to select a qualifier.
    Args:
        qualifier: (str) The name of the qualifier to select. Do not include the price.
                         By default, the unqualified item will be selected.
        timeout: (int) How many seconds to wait for the button to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: Whether or not the qualifier was successfully selected
    Examples:
        >>> select_qualifier("6-Pack")
        True
        >>> select_qualifier("12-Pack ($8.00)")
        True
        >>> select_qualifier("NotAQualifier")
        False
    """
    if qualifier is None:
        logger.info("No qualifier specified. Selecting the unqualified item.")
        return click_key(QUALIFIERS['buttons'])

    qualifiers = _get_texts(QUALIFIERS['buttons'])
    qualifiers_noprice = [q[:q.rfind(' ($')] for q in qualifiers] # Remove prices from button texts
    for i in range(len(qualifiers_noprice)):
        if qualifiers_noprice[i].lower() == qualifier.lower():
            return click_key(QUALIFIERS['button_by_text'] % qualifiers[i])
    else:
        logger.warning(f"Unable to find the qualifier {qualifier}.")
        return False

@test_func
def select_dispenser(id=1, timeout=default_timeout):
    """
    Select a dispenser for prepay.
    Args:
        id: (int) The ID of the dispenser to select.
        timeout: (int) How many seconds to wait for the dispenser to be selectable.
    Returns: (bool) True/False for success/failure
    Examples:
        >>> select_dispenser()
        True
        >>> select_dispenser(4)
        True
    """
    return click_key(controls['Fuel']['prepay_dispenser_by_id'] % id, timeout=timeout)

@test_func
def select_postpay(dispenser=1, sale_num=1, timeout=default_timeout):
    """
    Select a postpay to pay out.
    Args:
        dispenser: (int) The ID of the dispenser holding the postpay.
        sale_num: (int) If there are multiple postpays on the same dispenser, use this to specify 1st/2nd/3rd.
        timeout: (int) How many seconds to wait for the postpay sale to be selectable.
    Returns: (bool) True/False for success/failure
    Examples:
        >>> select_postpay()
        True
        >>> select_postpay(2, 2)
        True
    """
    return click_key(controls['Fuel']['postpay_by_id_and_instance'] % (dispenser, sale_num), timeout=timeout)

"""
Click helper functions
"""
@test_func
def click_function_key(key, timeout=default_timeout):
    """
    Click a key in the POS function key window.
    Args:
        key: (str) The text of the key to click.
        timeout: (int) How many seconds to wait for the key to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> click_function_key("Key In Code")
        True
        >>> click_function_key("Generic Item")
        False
    """
    if key.lower() == "pay":
        # Handle edge case where back end ignores the Pay button
        if not click_key(FUNC_KEYS[key], timeout):
            return False
        if not _is_element_present(CARD_PROCESSING["PINPad Image"], timeout=5):
            logger.warning("PINPad image did not appear after clicking Pay. The back end may have ignored the request.")
            return False
        return True

    return click_key(FUNC_KEYS[key], timeout)

@test_func
def click_payment_key(key, timeout=default_timeout):
    """
    Click a key in the payment key window.
    Args:
        key: (str) The text of the key to click.
        timeout: (int) How many seconds to wait for the key to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> click_function_key("Back")
        True
        >>> click_function_key("Generic Item")
        False
    """
    return click_key(PAYMENT_KEYS[key], timeout)

@test_func
def click_loyalty_key(key, timeout=default_timeout):
    """
    Click a key in the loyalty processing window.
    Args:
        key: (str) The text of the key to click.
        timeout: (int) How many seconds to wait for the key to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns: (bool) True if success, False if failure
    Examples:
        >>> click_loyalty_key("Yes")
        True
        >>> click_loyalty_key("asdf")
        False
    """
    return click_key(LOYALTY_KEYS[key], timeout)

@test_func
def click_help_key(key, timeout=default_timeout):
    """
    Click a key in the Help submenu.
    Args:
        key: (str) The text of the key to click.
        timeout: (int) How many seconds to wait for the key to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns: (bool) True if success, False if failure
    Examples:
        >>> click_help_key("Request Assistance")
        True
        >>> click_help_key("asdf")
        False
    """
    return click_key(HELP[key], timeout)

@test_func
def click_weights_measures_key(key, timeout=default_timeout):
    """
    Click a key in the Weights and Measures submenu.
    Args:
        key: (str) The text of the key to click.
        timeout: (int) How many seconds to wait for the key to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns: (bool) True if success, False if failure
    Examples
        >>> click_weights_measures_key("Back")
        True
        >>> click_weights_measures_key("jkl;")
        False
    """
    return click_key(WEIGHTS_MEASURES[key], timeout)

@test_func
def click_speed_key(key, timeout=default_timeout, case_sens=False):
    """
    Click on a speed key. Switches to speed keys if POS is in dept key mode.              
    Args:
        key: (str, int) The text of the speed key to click on, or its numbered position in the list.
        timeout: (int) How long to wait for the window to be available.
        case_sens (bool): Whether to use a case sensitive search.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> click_speed_key("Generic Item")
        True
        >>> click_speed_key("Not A Speed Key")
        False
    """
    # TODO Allow specifying instance?
    if type(key) == str:
        key = SPEED_KEYS['key_by_text'].replace('<text>', key)
    elif type(key) == int:
        key = SPEED_KEYS['key_by_position'].replace('<position>', key)

    if click_key(key, timeout):
        return True
    else:
        logger.warning(f"Failed to click speed key {key}")
        return False

@test_func
def click_message_box_key(key, timeout=default_timeout):
    """
    Click a key on the red popup message on the POS, if it exists.
    Args:
        key: (str) The text of the key to click.
        timeout: (int) How long to wait for the window to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> click_message_box_key("YES")
        True
        >>> click_message_box_key("MAYBE")
        False
    """
    # TODO: Smart delegation to click_prompt_key for cross compatibility?
    # We use inner text to identify the element to click
    return click_key(MSG_BOX['function_key'].replace('<text>', key), timeout)

@test_func
def click_prompt_key(key, timeout=default_timeout):
    """
    Click a key in the upper right prompt window.
    Args:
        key: (str) The text of the key to click.
        timeout: (int) How long to wait for the window to be available.   
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> click_prompt_key("YES")
        True
        >>> click_prompt_key("MAYBE")
        False
    """
    # TODO: Smart delegation to click_message_box_key for cross compatibility?
    # We use inner text to identify the element to click
    return click_key(PROMPT_BOX['function_key'].replace('<text>', key), timeout)

@test_func
def click_keypad(key, timeout=default_timeout):
    """
    Click a key in the numeric keypad, or one of the keys controlling it (Enter/Cancel/etc).
    This covers all possible keypads, but some lesser-used ones like those in age verification or
    attendant options will be slightly slower. Consider using more specialized functions
    (click_pwd_key, click_restriction_keypad, click_attendant_key) if speed is a priority.
    Args:
        key: (int/str) The keypad key that will be clicked. Must be for a single key, if the
                key is '00' then it needs to be a string in the first place.
        timeout: (int) How long to wait for the window to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> click_keypad(5)
        True
        >>> click_keypad('00')
        True
        >>> click_keypad('A')
        False
    """
    return click_key(KEYPAD[key], timeout)

"""
Helper functions
"""
def click_key(xpath, timeout=default_timeout):
    """
    Click the HTML element in self checkout that matches the given XPATH.
    Args:
        xpath: XPATH for the desired key. See console_controls.json for pre-mapped paths.
        timeout: How many seconds to wait for the desired key to be available.
    Returns: (bool) True if success, False if failure
    Examples:
        >>> click_key(FUNC_KEYS["User Options"])
        True
        >>> click_key("//button[@id='login_enter']")
        True
    """
    logger.debug(f"Clicking the element with XPATH {xpath}")
    start_time = time.time()
    try:
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, xpath)))
        except TimeoutException:
            logger.warning(f"Element with xpath {xpath} was not found within {timeout} seconds.")
            return False

        driver.execute_script("arguments[0].scrollIntoView(true);", element)
    
        try:
            element = WebDriverWait(driver, timeout - (time.time()-start_time)).until(
                EC.element_to_be_clickable((By.XPATH, xpath)))
        except TimeoutException:
            logger.warning(f"Element with xpath {xpath} was found but not clickable within {timeout} seconds.")
            return False   

        while True:
            try:
                element.click()
                break
            except ElementClickInterceptedException as e:
                if time.time() - start_time > timeout:
                    logger.warning(f"Element with xpath {xpath} was found but obscured by another element.")
                    logger.warning(f"Selenium message: {e}") # This exception actually contains useful information
                    return False

        return True
    except StaleElementReferenceException:
        # Account for situations where the element is present but gets overwritten with an identical element
        # This can happen when switching function key menus, for example
        logger.debug("Element became stale after we grabbed it. Restarting the click process.")
        return click_key(xpath, timeout=timeout - (start_time - time.time()))

def _clicked_start():
    """
    Helper function. Checks to see if we have already clicked start on the welcome screen on checkout.
    Args:
        timeout (int): How long to wait for the window and key to be available.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> _clicked_start()
        True
        >>> _clicked_start()
        False
    """
    if _get_text(WELCOME["Message"]) == 'Welcome!' or _is_element_present(WELCOME["Start"]):
        return False
    return True

def _is_element_present(xpath, timeout=prompt_timeout):
    """
    Helper function. Waits for the element/button to be present on the screen.
    Args:
        text (str): The inner text of the desired element
        container (str): An attribute of a parent of the desired element
        find_container_by (str): What attribute type to look for in the parent
        timeout (int): How long to wait for the window and key to be available.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> _is_element_present(SOME_VALID_LOCATOR)
        True
        >>> _is_element_present(SOME_INVALID_LOCATOR)
        False
    """
    start_time = time.time()
    try:
        element = WebDriverWait(driver, timeout).until(
                    EC.visibility_of_element_located(
                        (By.XPATH, xpath)))
    except:
        logger.warning(f"Element with XPATH {xpath} not available within {timeout} seconds")
        return False
    while time.time() - start_time <= timeout:
        if element.is_displayed():
            return True
    else:
        logger.warning(f"Element with XPATH {xpath} was available but not displayed within {timeout} seconds")
        return False

def _get_text(locator, timeout=default_timeout, type = By.XPATH):
    """
    Helper function. Returns the element's text.
    Utilizes _find_element()
    Args:
        locator (str): Element's locator
        timeout (int): How long to wait for the window and element to be available.
        type: the type to use: By.CSS_SELECTOR or By.XPATH
    Returns:
        Returns string with text of the element upon success or None otherwise
    Examples:
        >>> _get_text(SOME_VALID_LOCATOR)
        'Generic Item'
        >>> _get_text(SOME_INVALID_LOCATOR)
        None
    """
    logger.debug("Entered _get_text() method")
    button = _find_element(locator, type = type, timeout = timeout)
    if button:
        return button.text
    return None

def _get_texts(locator, timeout=default_timeout, type = By.XPATH):
    """
    Helper function. Returns the element's text.
    Utilizes _find_elements()
    Args:
        locator (str): Element's locator
        timeout (int): How long to wait for the window and element to be available.
        type: the type to use: By.CSS_SELECTOR or By.XPATH
    Returns:
        Returns string with text of the element upon success or None otherwise
    Examples:
        >>> _get_text(SOME_VALID_LOCATOR)
        'Generic Item'
        >>> _get_text(SOME_INVALID_LOCATOR)
        None
    """
    logger.debug("Entered _get_text() method")
    elts = _find_elements(locator, type = type, timeout = timeout)
    if elts:
        return [elt.text for elt in elts]
    return None

def _find_element(locator, timeout=1, type = By.XPATH):
    """
    Helper function. Searches the DOM to find the element you are looking for.
    Args:
        locator (str): Element's locator (CSS or XPATH)
        timeout (int): How long to wait for the window and element to be available.
        type: the locator type (By.CSS_SELECTOR or By.XPATH)
    Returns:
        The list of selenium webelement or None
    Examples:
        >>> _find_element(SOME_VALID_LOCATOR)
        <selenium.webdriver.remote.webelement.WebElement (session="80f1a1ebe8220157e9d2f394e913db02", element="0.05045595521012469-1")>
        >>> _find_element(SOME_INVALID_LOCATOR)
        None
    """
    elements = _find_elements(locator, timeout, type)
    if elements:
        if len(elements) > 1:
            logger.warning(f"There is more than one element matching the locator {locator}."
                            "Try a more specific locator, or use _find_elements if this is expected.")
            return None
        return elements[0]
    else:
        logger.warning("Could not find element with the locator [%s]"%(locator))
        return None

def _find_elements(locator, timeout=1, type = By.XPATH):
    """
    Helper function. Searches the DOM to find the elements you are looking for.
    Args:
        locator (str): Element's locator (CSS or XPATH)
        timeout (int): How long to wait for the window and element to be available.
        type: the locator type (By.CSS_SELECTOR or By.XPATH)
    Returns:
        The list of selenium webelements or None
    Examples:
        >>> _find_element(SOME_VALID_LOCATOR)
        <selenium.webdriver.remote.webelement.WebElement (session="80f1a1ebe8220157e9d2f394e913db02", element="0.05045595521012469-1")>
        >>> _find_element(SOME_INVALID_LOCATOR)
        None
    """
    try:
        logger.debug("Looking for elements with locator [%s]"%(locator))
        return WebDriverWait(driver, timeout).until(EC.visibility_of_all_elements_located((type, locator)))
    except TimeoutException:
        logger.warning(f"No elements with locator {locator} were visible within {timeout} seconds")
        return None

def _strip_currency(amount):
    """
    Helper function. Strips dollar sign and decimal from a curreny string.
    Args:
        amount (str): The currency amount you wish to strip.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> _strip_currency('$10.00')
        '1000'
        >>> _strip_currency('10.00')
        '1000'
        >>> _strip_currency('1000')
        '1000'
    """
    if amount[0] == '$':
        amount = amount[1:]
    if amount.find(".") != -1:
        return amount.replace(".", "")
    return amount

def _item_not_found(item):
    """
    Helper function. Searhces for item you are looking for, if found, return Success; otherwise, Failure.
    Args:
        item (str): The item you are searching for.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> _item_not_found('Generic Item')
        True
        >>> _find_element('Some speedkey not on the page')
        False
    """
    if _is_element_present(PROMPT_BOX["Heading"]):
        if "not on file" in _get_text(PROMPT_BOX["Heading"]):
            return click_message_box_key("OK", verify=False)
    return False

def edit_sco_xml():
    import xml.etree.ElementTree as ET
    settings_list = [
        "DisableIfPaymentOffline",
        "DisableIfSCCCOffline"
    ]

    # Gets rid of ns0 prefix
    ET.register_namespace('', "http://www.topografix.com/GPX/1/1")
    ET.register_namespace('', "http://www.topografix.com/GPX/1/0")

    tree = ET.parse(sco_xml)
    root = tree.getroot()
    
    changed = False
    i = 0
    for setting in root.iter('setting'):
        if i <= len(settings_list) - 1:
            if setting.attrib['name'] == settings_list[i]:
                for value in setting:
                    value.text = "False"
                    changed = True
                i += 1
            else:
                changed = False
        else:
            break
            
    tree.write(sco_xml)
    return changed