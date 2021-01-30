"""
Name: edge
Description: This is a process to use the keys for the Edge POS. This is
            for general use.

Date created: 02/26/2018
Modified By:
Date Modified:
"""

import functools
import time
import json
import logging, re, requests
from html.parser import HTMLParser

# Selenium modules
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, SessionNotCreatedException, ElementClickInterceptedException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait

# In house modules
from app.simulators.ip_scanner import IPScanner
from app.simulators.printersim import PrinterSim
from app import pinpad
from app import mws
from app import crindsim
from app.util import constants, system
from app.framework.tc_helpers import test_func, tc_fail

# Change Selenium's logging handlers to avoid spam
from selenium.webdriver.remote.remote_connection import LOGGER as selenium_logging

from urllib3.connectionpool import log as urllibLogger
urllibLogger.setLevel(logging.WARNING)

# Remove all StreamHandlers from Selenium logger
selenium_logging.handlers = [ h for h in selenium_logging.handlers if not isinstance(h, logging.StreamHandler)]
selenium_logging.setLevel(logging.CRITICAL)

# Log object
logger = logging.getLogger(__name__)

# Retry and Timeouts
driver_timeout  = 2
default_timeout = 5
prompt_timeout  = 1
key_timeout     = 0.5
till_timeout    = 7
pinpad_timeout  = 10

# JSON file paths
json_user_credentials   = constants.USER_CREDENTIALS # Change this when we finalize where to store temporary data files
edge_controls_path      = constants.CONTROLS_EDGE

try:
    with open(edge_controls_path) as f:
        controls = json.load(f)
except Exception as e:
    logger.warning(e)

# Selenium objects
driver  = None

# Scanner object
scanner = IPScanner()

# Receipt printer object
printer = PrinterSim(ip_mode=True)

"""
Edge element locators and button names.
"""
MENU_BAR = controls['menu bar']
INFO = controls['information']
NETWORK = controls['network status']
TRANSACTIONS = controls['suspended transactions']
LOGIN = controls['login']
KEYBOARD = controls['keyboard']
PROMPT = controls['prompt box']
KEYPAD = controls['keypad']
ITEM_KEYS = controls['item keys']
FUNC_KEYS = controls['function keys']
PAYMENT = controls['pay']
PAYMENT_PROC = controls['payment_processing']
JOURNAL = controls['receipt journal']
RECEIPTS = controls['receipt search']
FORECOURT = controls['forecourt']


class FeatureNotSupported(Exception):
    def __init__(self, message):
        self.message = message

def connect(timeout=60, recover=False, url = 'https://127.0.0.1:7501/'):
    """
    Initializes Chrome driver instance and navigates to Edge POS.
    Args:
        timeout: (int) How many seconds to wait for a successful connection.
        recover: (bool) Only used for POS
        url: (str) The url of the webpage to connect to
    Returns:
        True if success, False if failure
    Examples:
        >>> connect()
        True
        >>> connect()
        False
    """
    global driver, wait
    already_connected = False
    if driver is not None:
        try: # We have a driver, make sure it's connected to Chrome
            driver.title
            already_connected = True
        except:
            logger.info("We have a driver but no connection to Chrome. Re-creating the driver.")
            driver = None # Chrome was probably closed by something else, need to re-create the driver

    if not already_connected:
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

        start_time = time.time()
        while time.time() - start_time <= timeout:
            try:
                driver.get(url)
                break
            except:
                logger.warning(f"Unable to open web page. Retrying...")
        else:
            logger.warning(f"Unable to open web page within {timeout} seconds.")
            return False

        # Verify Edge page loads
        if "Passport EDGE" not in driver.title:
            logger.warning("Opened a web page, but it wasn't Edge. Check Passport status and URL.")
            return False

        driver.maximize_window()
        return True
    else:
        logger.debug(f"Already connected to a chrome driver instance")
        return True

def close():
    """
    Closes chrome driver instance.
    Args:
        None
    Returns:
        True if success; otherwise, False
    """
    try:
        global driver
        driver.close()
        driver = None
        return True
    except Exception as e:
        logger.warning(f"Unable to close chrome driver instance: {e}")
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
    # TODO : do we want to connect/navigate to MWS after closing browser?    
    return close()

def get_to_pos(timeout=1, sign_on=False):
    return connect()

def minimize_pos():
    """
    Minimizes the instance of the pos to allow mws to be handled
    Args:
        None
    Returns:
        True if success, False if failure
    Examples:
        >>> minimize_pos()
        True
        >>> minimize_pos()
        False
    """
    
    try:
        driver.minimize_window()
        return True
    except Exception as e:
        logger.error(f"Unable to minimize browser: {type(e).__name__} {e}")
        return False

def maximize_pos():
    """
    maximizes the instance of the pos to allow the screenshot take
    the correct image
    Args:
        None
    Returns:
        True if success, False if failure
    Examples:
        >>> minimize_pos()
        True
        >>> minimize_pos()
        False
    """
    
    try:
        driver.maximize_window()
        return True
    except Exception as e:
        logger.error(f"Unable to maximize browser: {type(e).__name__} {e}")
        return False
        

"""
Script Functions
"""
@test_func
def sign_on(user_credentials=None, till_amount = '0.00', reason=None, timeout = 20):
    """
    Signs on to the Edge POS. Covers most typical scenarios encountered when signing on.
    Args:
        user_credentials: (tuple) The users sign on credentials (username, password)
        till_amount: (str) Till Amount for opening balance
        reason: (str) Clock in reason code
        timeout: (int) the amount of seconds to wait for login to process
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        True if success, False if failure
    Examples:
        >>> sign_on()
        True
        >>> sign_on(('91', '91'), till_amount="10.00", reason="reason 1")
        True
        >>> sign_on(('123', 'TheWrongPassword'))
        False
    """
    #Wait for 120 seconds max to see if loading screen logo disappears
    start_time = time.time()
    while (time.time() - start_time <= 120):
        if (not _is_element_present("/html/body/div[6]/div/img")):
            break
    #if loading screen logo never disappeared, return false
    else:
        logger.debug("sign_on exited 2 minute wait without having the loading logo disappear")
        return False

    logger.debug("Checking if already signed on.")
    if _is_signed_on():
        logger.debug("Already signed on to Edge POS")
        return True

    credentials = None
    json_creds = {}

    logger.debug("Checking for the credentials.")
    if user_credentials != None:
        credentials = user_credentials
    else:
        try:
            with open(json_user_credentials) as creds_file:
                json_creds = json.load(creds_file) # Check for existing credentials
                credentials = [json_creds['ID'], json_creds['Password']]
        except: # Nonexistent or empty credentials file
            credentials = ('91', '91')
            logger.warning("Could not find credentials file, using [%s] for credentials." %(str(credentials)))
                
    # Enter Login Credentials
    logger.debug("Checking for the login keypad to be present")
    if _is_element_present(LOGIN['display'], type = By.XPATH, timeout = prompt_timeout):
        _sign_in(credentials)
    else:
        logger.error("Did not find the login keypad. Unable to log in.")
        return False

    result = True
    operations = {
        "Your password must be changed. Please enter a new password." : _change_pwd,
        "Your password has expired. Please enter a new password." : _expired_pwd,
        "Operator not found." : _operator_not_found,
        "Clock In - Select a reason" : _enter_reason
    }

    # TODO The combination of result and return statements is confusing. Re-write using either returns
    # or results
    logger.debug("Checking for popups")
    popup_msg = read_message_box(timeout = 0.1)
    if popup_msg != None:
        logger.debug(f"Found popup message: {popup_msg}")
        logger.debug("Checking if the popup message is known")
        if popup_msg in operations:
            logger.debug("Found known message. Tring to execute the related operation")
            result = operations[op](credentials, reason)
        else:
            logger.error(f"Found unexpected message: {popup_msg}")
            return False

        popup_header = read_message_box(text = 'header', timeout = 0.1)
        if popup_header:
            logger.debug(f"Found header text: {popup_header}")
            # Clock In reason only has header text.
            logger.debug("Checking the header of the popup.")
            if popup_header in operations:
                logger.debug("Clock in reason prompt found")
                result = operations[popup_header](credentials, reason)

    else:
        logger.debug("Checking the message of the login keypad display")
        prompt_msg = read_keypad_prompt(timeout = 0.1)
        if prompt_msg != None:
            logger.debug(f"Found message: {prompt_msg}")
            if "stand by" in prompt_msg:
                # Wait for login display to go away
                logger.debug("Waiting for login display to go away for 10s")
                if not _is_signed_on(timeout = 10):
                    logger.error("Timed out while waiting to login after successfully entering the credentials.")
                    return False

                result = True
    logger.debug("Checking if login curtain is still present")
    if _is_element_present(LOGIN['display'], timeout = 0.1):
        logger.debug(f"Initiating {timeout}s timeout loop. Waiting for the login curtain to go away.")
        start_time = time.time()
        temp_level = logger.getEffectiveLevel()
        logger.setLevel(999)
        while time.time() - start_time <= timeout:
            # Check if the login display is still present. When it's gone, the login is completed
            if not _is_element_present(LOGIN['display'], timeout = 0.1):
                logger.setLevel(temp_level)
                break
        else:
            logger.setLevel(temp_level)
            # Timed out
            logger.error("Timed out while waiting to login after successfully entering the credentials.")
            return False

    # Handle Till
    logger.debug("Checking if the till opening message is present on keypad display")
    prompt_msg = read_keypad_prompt(timeout = 0.1)
    if prompt_msg != None and prompt_msg == "Enter Opening Amount":
        logger.debug("Found the prompt about opening the till")
        logger.debug("Attempting to open till")
        result = enter_keypad(_strip_currency(till_amount), after="Enter", timeout = 1, verify=False)
    else:
        logger.debug("Till message not found. Till is already opened")  
        result = True
    return result

@test_func
def sign_off(user_id=None):
    """
    Signs off Edge site.
    Args:
        user_id: (str) The id of the user that is signing off of the POS.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> sign_off()
        True
    """
    if not click_function_key('Cashier', verify=False):
        return False
    if not click_function_key('Sign-off', verify=False):
        return False
    return click_message_box_key('Yes', verify=False)

@test_func      
def close_till(timeout=till_timeout):
    """
    Closes Till on the Edge POS.
    Args:
        timeout: (int) How long to search for the key before failing.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> close_till()
        True
    """
    click_function_key('Cashier', verify=False)
    click_function_key('Close Till', verify=False)
    click_message_box_key('Yes', verify=False)
    
    if _is_element_present(LOGIN['display'], type = By.XPATH, timeout = timeout):
        return True
    else:
        logger.warning("Exceeded timeout. Unable to close till.")
        return False

@test_func
def enter_keypad(values, timeout=default_timeout, after=None):
    """
    Enter value on numerical keypad for item's quantity, price, PLU, etc.
    Args:
        values: (str) The value you want to enter into keypad.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
        after: (str) The key to press after entering digits.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> enter_keypad("$1.00")
        True
        >>> enter_keypad("123", after="Enter")
        True
        >>> enter_keypad("SomeText")
        False
    """
    logger.debug("Entered enter_keypad() method")
    time.sleep(.2) # Give UIBlocker a bit to get out the way - increases consistancy - possibly improve?
    logger.debug("Trying to press keypad buttons")
    for value in str(values):
        if not click_keypad(str(value), timeout=timeout, verify=False):
            return False
    if after:
        ret = click_keypad(after, verify=False)
        time.sleep(.1) # We probably hit Enter/Cancel. Wait for POSState to process
        return ret

    return True

@test_func
def enter_keyboard_value(values):
    """
    Enter value(s) on keyboard.
    Args:
        values: (str) The value you want to enter into keyboard.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> enter_keyboard_value("Some Text")
        True
        >>> enter_keyboard_value("123")
        True
        >>> enter_keyboard_value("$1.00")
        False       
    """
    try:
        first_char = 0
        for value in str(values):
            if value.istitle() and first_char != 0: # Click Shift if char is upper-case (first char clicks shift by default).
                click_keyboard('shift', verify=False)
                click_keyboard(value, verify=False)
            else:
                click_keyboard(value, verify=False)
            first_char += 1
        return True
    except:
        logger.error("Unable to type %s on keybaord" %(values))
        return False

@test_func
def add_item(item="Generic Item", method="SPEED KEY", quantity=1, price=None, dob=None, qualifier=None, timeout = 10, cash_card_action=None):
    """
    Adds an item to the Edge POS transaction journal via SpeedKey, PLU, or Dept.
    Args:
        item: (str) The item you want to add (text associated with the method). For PLU, use PLU num.
        method: (str) The way you are going to add an item (Speed Key, Dept, PLU)
        quantity: (str) The amount of items you want to add
        price: (str) The item's cost
        dob: (str) The DOB you wish to enter for the item. MM/DD/YYYY
        qualifier: (str) The qualifier to select. Do not include the price of the qualifier. Defaults to the unqualified form.
        cash_card_action: (str) The action to take if this item is a Cash Card. Can be Activate or Recharge.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> add_item(item='Generic Item', method='speedkey')
        True
        >>> add_item(item='item 3', method='speedkey', dob='11/30/1992')
        True
        >>> add_item(item='1234', method='plu')
        True
        >>> add_item(item='Generic Item', method='DEPT')
        False       
    """
    logger.debug(f"Adding {quantity }  {item} with method {method}")
    price = _strip_currency(price) if price else price
    
    logger.debug("Looking for the keypad button to ensure we are able to add items at this point.")
    if not _is_element_present(MENU_BAR['keypad'], timeout = timeout):
        logger.error("Time exceeded. Unable to find keypad")
        return False

    logger.debug(f"Adding {item}")
    if method.upper() == "DEPT KEY":
        if price is None:
            logger.warning(f"price must be specified with {method} method.")
            return False
        if not click_dept_key(item, timeout=2, verify=False):
            logger.warning("Unable to add [%s] via dept key" %(item))
            return False

    elif method.upper() == "SPEED KEY":
        if not click_speed_key(item, timeout=2, verify=False):
            logger.warning("Unable to add [%s] via speed key" %(item))
            return False

    elif method.upper() == "PLU":
        if not enter_plu(plu=item, timeout=10, verify=False):
            logger.warning("Unable to add [%s] via PLU" %(item))
            return False

    else:
        logger.warning("Received: %s for method. Method needs to be <PLU|DEPT|SPEED KEY>." %(method))
        return False
    
    # Check for prompts
    # Set up a loop that will check for pop ups and keypad prompts
    # Create a flag indicating that all prompts and popups were dismissed
    msg_success = False
    price_req = False
    quantity_req = False

    while not msg_success:
        # Set to True
        # If there are prompts, the flag is switched to False to indicate that there were popups or prompts
        # Once no popups and prompts are present, the flag will be True, and the loop will terminate
        msg_success = True

        # Try to read keypad propmpt
        logger.debug("Checking for popups or keypad entries")
        pop_up_prompt    = _is_element_present(PROMPT['body'], timeout=2, type = By.XPATH)
        item_prompt      = _is_element_present(KEYPAD['description'], timeout=2, type = By.XPATH)

        if pop_up_prompt:
            msg_success = False
            # Get the message
            logger.debug("Found popup. Reading the message")
            pop_up_prompt_msg = read_message_box()

            age_text        = "Is the customer at least %d years old?"
            age_text18      = age_text %(18)
            age_text19      = age_text %(19)
            age_text21      = age_text %(21)
            cash_card_text = "Press Yes for Activation or No for Recharge"
            
            if age_text18 == pop_up_prompt_msg or age_text19 == pop_up_prompt_msg or age_text21 == pop_up_prompt_msg:
                logger.debug("Agreeing with age popup")
                click_message_box_key("Yes", verify=False)

            elif _get_text(PROMPT['header']) == 'Select a qualifier': # Qualifier Prompt
                logger.debug("Found Qualifier. Handling that")
                if not _handle_qualifier(qualifier=qualifier):
                    logger.error("Unable to add [%s]" %(item))
                    return False

            elif cash_card_text == pop_up_prompt_msg:
                logger.debug("Handling cash card prompt")
                if cash_card_action.lower() == "activate" or cash_card_action.lower() == "activation":
                    click_message_box_key("Yes", verify=False)
                elif cash_card_action.lower() == "recharge":
                    click_message_box_key("No", verify=False)
                else:
                    logger.error(f"{cash_card_action} is invalid for cash_card_action. Please specify Recharge or Activation.")
            else:
                logger.error("Encountered unexpected popup message. Header: %s. Body: %s" % (_get_text(PROMPT['header']), pop_up_prompt_msg))
                return False

        if item_prompt:
            # Prompt Handling
            birthday_text   = "Enter birthday or scan Id"
            price_text      = "Enter price for"
            quantity_text   = "Enter quantity for"
            plu             = "Enter PLU"

            # In case the *_text is a list convert everything to a list
            birthday_text = birthday_text if type(birthday_text) is list else [birthday_text]
            price_text = price_text if type(price_text) is list else [price_text]
            quantity_text = quantity_text if type(quantity_text) is list else [quantity_text]

            logger.debug("Reading keypad propmpt")
            text_on_prompt  = read_keypad_prompt(0.5)

            # Process each expected pop up separately
            # Using list comprehension, create a list of boolean results of searching for a expected popup
            # message in the actual popup
            # Then, apply logical or to all elements of that list to evaluate if the popup matched the expected string
            dob_req = any([ x in text_on_prompt for x in birthday_text])
            if dob_req:
                logger.debug("Found DOB prompt")
                if dob:
                    enter_keypad(_strip_currency(dob), after="Enter", timeout = 1)                 
                else:
                    click_keypad('Default', timeout = 1, verify=False)   

            if any([ x in text_on_prompt for x in price_text]):
                price_req = True
                logger.debug("Found price prompt")
                if price is None:
                    logger.warning(f"{item} is price required. Please specify price.")
                    click_keypad("Cancel")
                    if method.upper == "DEPT":
                        click_message_box_key("Ok") # Clear unable to sell item popup
                    return False
                enter_keypad(price, after="Enter", timeout = 1, verify=False)

            elif any([ x in text_on_prompt for x in quantity_text]):
                quantity_req = True
                logger.debug("Found quantity prompt")
                enter_keypad(quantity, after="Enter", timeout = 1, verify=False)

    if price is not None and not price_req: # Override price
        click_function_key("Change Item Price", verify=False)
        # if "select a valid reason" in read_status_line().lower():
        #     click_keypad("ENTER", verify=False)
        enter_keypad(price, after='Enter', verify=False)
        click_keypad('ENTER', verify=False) 

    if quantity != 1 and not quantity_req: # Override quantity
        click_function_key('Change Item Qty', verify=False)
        enter_keypad(quantity, after='Enter', verify=False)

    return True

@test_func
def void_transaction():
    """
    Voids transaction
    Args:
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success; otherwise, False
    Examples:
        >>> void_transaction()
        True
        >>> void_transaction()
        False
    """
    logger.debug("Starting void transaction")

    if not click_function_key("Transaction", verify=False):
        return False
    if not click_function_key("Void Transaction", verify=False):
        return False
    if not click_message_box_key("Yes", verify=False):
        return False
    start_time = time.time()
    while time.time()-start_time < 5:
        if read_journal_watermark() == 'TRANSACTION VOIDED':
            break
    else:
        return False
    return True

@test_func
def void_item(item, timeout=default_timeout):
    """
    Voids item specefied
    Args:
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success; otherwise, False
    Examples:
        >>> void_item("GENERIC ITEM")
        True
        >>> void_item("$0.01")
        False
        >>> void_item("Something not in the basket")
        False
    """
    if not click_journal_item(item, verify=False):
        logger.warning(f"Unable to click {item} in the basket")
        return False

    if not click_function_key("Transaction", verify=False):
        return False
    return click_function_key("Void Item", verify=False)

@test_func
def suspend_transaction():
    """
    Suspends transaction
    Args:
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success; otherwise, False
    Examples:
        >>> suspend_transaction()
        True
        >>> suspend_transaction()
        False
    """
    if not click_function_key("Suspend Transaction", verify=False):
        return False
    return click_message_box_key("Yes", verify=False)

@test_func
def pay(amount=None, tender_type="cash", cash_card="GiftCard", prompts = None, timeout_transaction=False):
    """
    Pay out transaction using a non-card tender type.
    User can click any tender type under 'Pay' and pay any amount if this method supports keypad.
    If the amount is not provided, exact amount button will be used instead. Beware that Food Stamp
    support keypad, but have no exact amount. So, if not amount is provided in that case, the pay() will fail.
    Args:
        amount: (str) How much to pay if not using card. Default is exact change.
        tender_type: (str) Type of tender to select. CASH|IMPRINTER|FOOD|CHECK
        cash_card: (str) If activating a cash card, the name of the card in CardData.json.
        prompts: (dict) A dictionary to handle all the commercial prompts
        timeout_transaction: (bool) Used for waiting for the time out message shown after a host does not answer for a period of time (between 30 and 45 second is most of the networks)
    Returns:
        bool: True if success, False if fail
    Examples:
        >>> pay()
        True
        >>> pay(amount="$5.00", tender_type="Check")
        True
        >>> pay(tender_type="card")
        False
    """
    logger.debug("Entered pay() method")
    if tender_type.lower() == "card":
        logger.warning(f"Use pay_card function for card tenders")
        return False

    logger.debug("Trying to click Pay")
    if not click_function_key('Pay', verify=False):
        logger.error(f"Unable to click Pay")
        return False

    logger.debug("Checking for popups")
    if _is_element_present(PROMPT['body']):
        click_message_box_key(key='No', verify=False)

    amount = _strip_currency(amount)

    # Find requested key
    if amount == None:
        logger.debug("Trying to click on exact change button")
        if not click_tender_key("exact change", verify=False):
            logger.error(f"Unable to click exact change key")
            return False
    else:
        logger.debug(f"Trying to click {tender_type}")
        if not click_tender_key(tender_type, verify=False):
            logger.error(f"Unable to click tender {tender_type}")
            return False

        if not prompts is None:

            logger.debug(f"Handeling commercial prompts, these are the provided prompts: {prompts}")
            
            if not commercial_prompts_handler(prompts, timeout_transaction=timeout_transaction, verify=False):
                
                logger.error("The displayed prompt was not provided")
                return False

        # Checking if the keypad is disaplyed, there are 
        # tenders that do not use keypad

        keypad_text = read_keypad_prompt(timeout=2)

        logger.debug(f"The keypad text is {keypad_text}")

        if keypad_text is not None:

            logger.debug("Trying to enter the amount")
            if not enter_keypad(amount, after="Enter"):
                return False   

    # Handle cash card swipe if needed
    status = read_message_box()
    if status and ("activation" in status.lower() or "recharge" in status.lower()):
        try: 
            pinpad.swipe_card(brand=system.get_brand(), card_name=cash_card)
        except Exception as e:
            logger.warning(f"Cash card swipe in pay failed. Exception: {e}")
            click_keypad("CANCEL", verify=False)
            click_message_box_key("YES", verify=False)
            return False

    # Wait for the payment process to finish
    logger.debug("Initiating 20s timeout loop. Waiting for payment process to finish. Looking for processing panel in POS to go away")
    start_time = time.time()
    temp_level = logger.getEffectiveLevel()
    logger.setLevel(999)
    while time.time() - start_time <= 20:
        # Check if the processing screen is still present. When it's gone, the transaction is completed
        if not _is_element_present(PAYMENT_PROC['panel'], timeout = 0.35):
            logger.setLevel(temp_level)
            break
    else:
        logger.setLevel(temp_level)
        # Timed out
        logger.error("Transaction is taking too long and we didn't go back to idle screen. - pay")
        return False
    logger.info("Transaction finished.")

    return True

def read_keyboard_prompt(timeout=default_timeout):
    """
    Read the prompt text from the keyboard prompt
    Args:
        timeout: (int) How long to wait for the prompt
    Returns:
        str: the prompt text
    Example:
        >>> read_keyboard_prompt()
        "Enter Password"
    """
    
    return _get_text(KEYBOARD['prompt'], timeout=timeout)

@test_func
def commercial_prompts_handler(prompts=dict(), timeout=10, timeout_transaction = False):
    """
    Handle the dynamic prompts used for Commercial Feature. The user will configure the prompt type 
    in the host sim so we don't know how it will be set.
    NOTE: The prompt in the dictionary IS CASE SENSITIVE
    Args:
        prompts: (dict) A dictionary to handle all the commercial prompts
        timeout: (int) the time that we will wait for prompts
        timeout_transaction: (bool) wait for a timeout message while payment
    Returns:
        bool: True if success, False if fail
    Examples:
        >>> commercial_prompts = {              
                "ENTER BIRTHDAY IN MMDDYY FORMAT": {
                    "entry": ["120170"],
                    "buttons": ["Ok"] 
                }, 
                "ENTER BILLING ID": {
                    "entry" : ["123456798", "12"], # This allow us to have answer differently to the same prompt in the same transaction
                    "buttons": ["Enter", "Enter"]  # This will hit enter both times              
                },
                "Additional Products Y/N?": {                    
                    "buttons": ["No"]
                },
                "Invalid entry": {                    
                    "buttons": ["Ok"]
                }

            }
        True
    """

    logger.debug(f"Starting commercial prompts handler, the provided prompts are: {prompts} ")

    keypad_text = None
    keyboard_text = None
    prompt_text = None

    start_time = time.time()    

    while keypad_text is None and keyboard_text is None and prompt_text is None and (time.time() - start_time < timeout):

        # Given that we don't know the order or the type of the prompt, we check all types
        
        prompt_text = read_message_box(timeout=1)

        logger.debug(f"The prompt text is {prompt_text}")

        if prompt_text is None:

            keypad_text = read_keypad_prompt(timeout=1)

            logger.debug(f"The keypad text is {keypad_text}")

            if keypad_text is None:
            
                keyboard_text = read_keyboard_prompt(timeout=1)

                logger.debug(f"The keyboard text is {keyboard_text}")
        
    
    # We loop until we do not get more prompts
    while keypad_text is not None or keyboard_text is not None or prompt_text is not None:
    #if keypad_text is not None or keyboard_text is not None:

        if keyboard_text is not None:

            logger.debug(f"Attempting to handle prompt: {keyboard_text}")

            try:
                entry = prompts[keyboard_text]['entry'].pop(0)
                buttons = prompts[keyboard_text]['buttons'].pop(0) #remove the fisrt in the list so next time we pick the following one
                keyboard_text = None

            except KeyError as e:
                logger.error(f"The terminal is prompting for {keyboard_text} and it is not expected")
                logger.error(e)
                
            except IndexError as e:
                logger.error(f"No buttons or entries were provided for prompt: {keyboard_text}, please check if your prompts appear more than one time ")
                logger.error(e)
                return False
            
            if not enter_keyboard_value(entry, verify=False):
                logger.error(f"Unable to type {entry} in the keyboard")
                return False

            if not click_keyboard(buttons, verify=False):
                logger.error(f"Unable to click {buttons} in the keyboard")
                return False

        elif keypad_text is not None:

            logger.debug(f"Attempting to handle prompt: {keypad_text}")

            try:

                entry = prompts[keypad_text]['entry'].pop(0)
                buttons = prompts[keypad_text]['buttons'].pop(0) #remove the fisrt in the list so next time we pick the following one
                keypad_text = None

            except KeyError as e:
                logger.error(f"The terminal is prompting for {keypad_text} and it is not expected")
                logger.error(e)
                
            except IndexError as e:
                logger.error(f"No buttons or entries were provided for prompt: {keypad_text}, please check if your prompts appear more than one time ")
                logger.error(e)
                return False
            
            if not enter_keypad(entry, verify=False):
                logger.error(f"Unable to type {entry} in the keypad")
                return False
            if not click_keypad(buttons, verify=False):
                logger.error(f"Unable to click {buttons} in the keypad")
                return False

        elif prompt_text is not None:
            
            logger.debug(f"Attempting to handle prompt: {prompt_text}")

            try:
                
                buttons = prompts[prompt_text]['buttons'].pop(0) #remove the fisrt in the list so next time we pick the following one
                prompt_text = None

            except KeyError as e:
                logger.error(f"The terminal is prompting for {prompt_text} and it is not expected")
                logger.error(e)
                
            except IndexError as e:
                logger.error(f"No buttons were provided for prompt: {prompt_text}, please check if your prompts appear more than one time ")
                logger.error(e)
                return False
            
            if not click_message_box_key(buttons, verify=False):
                logger.error(f"Unable to click {buttons} in the prompt")
                return False
        
        # Reading again to realize if we have more prompts

        prompt_text = read_message_box(timeout=2)

        logger.debug(f"The prompt text is {prompt_text}")

        if prompt_text is None:

            keypad_text = read_keypad_prompt(timeout=2)

            logger.debug(f"The keypad text is {keypad_text}")

            if keypad_text is None:
            
                keyboard_text = read_keyboard_prompt(timeout=2)

                logger.debug(f"The keyboard text is {keyboard_text}")
    
    start_time = time.time()    

    while prompt_text is None and (time.time() - start_time < 60) and timeout_transaction: # Networks Time out between 30 and 45 seconds

        prompt_text = read_message_box(timeout=1)

        logger.debug(f"The prompt text is {prompt_text}")

        if prompt_text is not None:
            
            logger.debug(f"Attempting to handle prompt: {prompt_text}")

            try:
                
                buttons = prompts[prompt_text]['buttons'].pop(0) #remove the fisrt in the list so next time we pick the following one                

            except KeyError as e:
                logger.error(f"The terminal is prompting for {prompt_text} and it is not expected")
                logger.error(e)
                return False
            except IndexError as e:
                logger.error(f"No buttons were provided for prompt: {prompt_text}, please check if your prompts appear more than one time ")
                logger.error(e)
                return False
            
            click_message_box_key(buttons)

    return True

# TODO : Currently not supported as we do not have a Loyalty sim ready.
# This is a mockup as I have not been able to test Loyalty against the PinPad SIM itself.
def swipe_loyalty(brand='Core', card_name='Loyalty'):
    """
    Select yes to loyalty prompt and swipes loyalty card.
     Args:
        brand : (str) String representation of the Brand (found in CardData.json)
        card_name : (str) The key/name of the card you wish to use located in the CardData.json file.
    Return:
        bool: True if success, False if failure
    Examples:
        >>> swipe_loyalty(brand='Core', card_name="Loyalty")
        True
        >>> swipe_loyalty(brand='Core', card_name="Visa")
        False
    """
    if not click_function_key('Pay', verify=False):
        return False
    if not click_tender_key("Card", verify=False):
        return False

    if _is_element_present(PROMPT['body']): # Loyalty
        click_message_box_key(key='Yes', verify=False)
    
    payload = pinpad.swipe_loyalty(
        brand=brand,
        card_name=card_name
    )
    return _process_payment(card_name, payload)

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
                #NOTE: This will cause a false failure if the transaction has completed but the function returned False
                # This situation arose when attempting to enter the expiration date for a card that didn't require it
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
                        logger.info(f"Trying pay_card for attempt {fail_counter}")
                        #Handles message box fails
                        if click_message_box_key("Ok", verify=False):
                            failure_flag = True
                        #Handles hanging prompt fails
                        if click_function_key("Cancel", verify=False):
                            failure_flag = True
                        #Clears message of canceled payment if hanging prompt fail
                        if click_message_box_key("Ok", verify=False):
                            failure_flag = True
                        #If none of the prompts or function key were clicked, assume edge case prompt (no response from host)
                        if not failure_flag:
                            time.sleep(20) #sleep for 20 seconds for prompt to be visible
                            click_message_box_key("Ok", verify=False)
                logger.info("Resetting pinpad after 3 transaction failures")
                requests.get(url='http://10.80.31.212/api/tools/start')
                time.sleep(120) #Sleep for 2 mins for pinpad to redownload
                #TODO: This needs to be dynamic. Requires the ability to read the current sales target
                crindsim.set_sales_target("money", "5.00")
                reset_count += 1
            #Failed 3 attempts before and after a pinpad reset
            if verify and (ret is None or not ret):
                tc_fail(f"{func.__module__}.{func.__name__} failed.")
            void_transaction(verify=False) #If all attempts failed, must void to have next test receipt be correct
            return ret
        else:
            ret = func(**kwargs)
        
        if verify and (ret is None or not ret):
            tc_fail(f"{func.__module__}.{func.__name__} failed.")
        void_transaction(verify=False) #If all attempts failed, must void to have next test receipt be correct
        return ret

    return pinpad_retry_wrapper
    
@pinpad_retry
def pay_card(brand='Core', card_name='Visa', debit_fee=False, cashback_amount=None, zip_code=None, cvn=None, custom=None, split_tender=False, cash_card="GiftCard", force_swipe=False, prompts = None, timeout_transaction=False):
    """
    Pay out tranaction with swiping card.
    Args:
        method: (str) the card payment method: swipe or insert
        brand   : (str) String representation of the Brand (found in CardData.json)
        card_name : (str) The key/name of the card you wish to use located in the CardData.json file.
        debit_fee : (bool) If Debit Fee is prompted and set to True, we click OK; otherwise, we click No.
        cashback_amount: (str) The cashback amount you wish to enter
        zip_code : (str) The ZIP code value you wish to enter
        custom : (str) The Custom prompt value you wish to enter
        split_tender: (bool) Set True if you are expecting the host to trigger split payment (i.e. gift card with insufficient balance)
        cash_card: (str) If activating a cash card, the name of the card in CardData.json.
        force_swipe : (bool) Force an EMV card to be swiped instead of inserted.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
        prompts: (dict) A dictionary to handle all the commercial prompts
        timeout_transaction: (bool) Used for waiting for the time out message shown after a host does not answer for a period of time (between 30 and 45 second is most of the networks)
        
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
    logger.debug("Entered pay_card() method")

    if not click_function_key('Pay', verify=False):
        return False  

    logger.debug("Looking for Loyalty popup message")
    if _is_element_present(PROMPT['body']):
        click_message_box_key(key='No', verify=False)

    if not click_tender_key("Card", verify=False):
        return False

    # Verify that pinpad payment is initiated
    logger.debug("Verifying the card type transaction is initiated. Looking for pinpad panel in POS")
    if not ( _is_element_present(PAYMENT_PROC['panel'], timeout = pinpad_timeout) or \
            _get_text(PAYMENT_PROC['text']) != "Insert/Swipe/Tap Card"):
        logger.error("The Pinpad payment was not initiated before timeout.")
        return False
    
    payload = pinpad.use_card(
            brand=brand,
            card_name=card_name,
            debit_fee=debit_fee,
            cashback_amount=cashback_amount,
            zip_code=zip_code,
            cvn=cvn,
            custom=custom,
            force_swipe=force_swipe
        )
    if not payload:
        logger.error(f"Card swipe in pay_card failed. Canceling transaction.")
        click_function_key("Cancel", verify=False)
        return False
    
    #Waits to see the "Complete!" message in the processing text so we know the transaction is complete and the pinpad can be reset.
    #TODO temporary fix while we wait for pinpad rewrite.   
    complete_time = time.time()
    while (time.time()-complete_time < 5):
        if (_get_text('//*[@id="processingtext"]') == "Complete!"):
            logger.debug("Resetting pinpad after reading 'Complete!' prompt")
            pinpad.reset()
            break
    else:
        logger.debug("Never saw the 'Complete!' processing text.  Did not reset pinpad queue.")

    # Check for popup about split pay
    logger.debug("Looking for popup message about Split Pay")
    msg = read_message_box(timeout=pinpad_timeout)
    if msg is not None and "split pay" in msg.lower():
        if not split_tender:
            logger.error("Got an unexpected split pay prompt when paying out transaction.")
            logger.debug("Trying to backout of Split Pay message ")
            click_message_box_key("No", verify=False)
            click_message_box_key("Ok", timeout=pinpad_timeout, verify=False)
            return False
        else:
            logger.debug("Accepting Split Pay popup")
            return click_message_box_key("Yes", verify=False)
    elif split_tender:
        logger.error("Expected split payment prompt but didn't get one.")
        logger.debug("Trying to Cancel the transaction")
        click_function_key("Cancel", verify=False)
        return False
    
    if not prompts is None:
        if not commercial_prompts_handler(prompts, timeout_transaction=timeout_transaction, verify=False):

            logger.error("Error handeling Commercial Prompts")
            return False
    
    return _process_payment(card_name, payload)


@pinpad_retry
def manual_entry(brand='Core', card_name='Visa', expiration_date="1230", zip_code=None, custom=None, split_tender=False):
    """
    Pay out tranaction using Manual entry.
    Args:
        brand   : (str) String representation of the Brand (found in CardData.json)
        card_name : (str) The key/name of the card you wish to use located in the CardData.json file.
        expiration_date : (str) The string representation of expiration date for card that'll be entered on POS.
        zip_code : (str) The ZIP code value you wish to enter
        custom : (str) The Custom prompt value you wish to enter
        split_tender: (bool) Set True if this payment will not complete the transaction.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if fail
    Examples:
        >>> manual_entry(
                brand='Generic',
                card_name='GiftCard',
                expiration_date='3012'
            )
        True
        >>> manual_entry(
            brand='Core',
            card_name='Discover',
            expiration_date='3012'
        )
        True
        >>> manual_entry(
            brand='Concord',
            card_name="some_card_not_in_CarData.json",
            expiration_date='3012'
        )
        False
    """
    if not click_function_key('Pay', verify=False):
        return False

    if not click_tender_key("Card", verify=False):
        return False

    if _is_element_present(PROMPT['body']): # Loyalty
        click_message_box_key(key='No', verify=False)
    
    if not click_function_key("Manual", verify=False):
        logger.warning("Unable to click Manual button")
        return False
    
    payload = pinpad.manual_entry(
           brand=brand,
           card_name=card_name,
           zip_code=zip_code,
           custom=custom
        )

    if not payload:
        logger.warning(f"Manual entry failed. Canceling transaction.")
        system.takescreenshot()
        click_function_key("Cancel", verify=False)
        return False

    if not click_message_box_key(key='Yes', verify=False):
        logger.warning("Unable to click yes for confirming Account Number")
        system.takescreenshot()
        return False
    
    #TODO: This needs a delay. We have issues with the prompt appearing and this failing. Assume it's a timing issue
    try:
        click_message_box_key(key="No", verify=False)
    except:
        logger.warning("Unable to click no for auxiliary network card")

    #TODO Enhance the logging if this fails
    if expiration_date:
        if expiration_date[2] == '/':
            expiration_date = expiration_date.replace('/', '')
        if not enter_keypad(expiration_date, verify=False):
            system.takescreenshot()
            return False
            
        if not click_keypad('Enter', verify=False):
            system.takescreenshot()
            return False

    msg = read_message_box(timeout=pinpad_timeout)
    if msg is not None and "split pay" in msg.lower():
        if not split_tender:
            logger.warning("Got an unexpected split pay prompt when paying out transaction.")
            system.takescreenshot()
            click_message_box_key("NO", verify=False)
            click_message_box_key("OK", timeout=pinpad_timeout, verify=False)
            return False
        else:
            return click_message_box_key("YES", verify=False)
    elif split_tender:
        logger.warning("Expected split payment prompt but didn't get one.")
        system.takescreenshot()
        click_function_key("Cancel", verify=False)
        return False

    # Handle cash card swipe if needed
    status = read_message_box()
    if not status == None:
        status = status.lower()
    if not status == None and ("activation" in status or "recharge" in status):
        try: 
            pinpad.swipe_card(brand=system.get_brand(), card_name=cash_card)
        except Exception as e:
            logger.warning(f"Cash card swipe in pay failed. Exception: {e}")
            system.takescreenshot()
            click_keypad("CANCEL", verify=False)
            click_message_box_key("YES", verify=False)
            return False

    return _process_payment(card_name, payload)

@test_func
def activate_gift_card(brand='Core', card_name='Visa', gift_card="GiftCard", debit_fee=False, cashback_amount=None, zip_code=None, cvn=None, custom=None):
    """
    DEPRECATED - USE CASH CARD ARGS IN ADD_ITEM AND PAYMENT FUNCTIONS INSTEAD

    Pays for Cash Card item using the card_name you provided.
    Then, we click Yes for Activation and activate the gift_card you provided.

    Args:
        brand   : (str) String representation of the Brand (found in CardData.json)
        card_name : (str) The key/name of the card you wish to use located in the CardData.json file to pay for the Cash Card item.
        gift_card : (str) The key/name of the gift card you will activate.
        expiration_date : (str) The string representation of expiration date for card that'll be entered on POS.
        zip_code : (str) The ZIP code value you wish to enter
        custom : (str) The Custom prompt value you wish to enter
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.

    Returns:
        bool: True if success, False if fail
        
    Examples:
        >>> 
    """
    logger.warning("activate_gift_card is deprecated - use cash card args in add_item and payment functions instead")

    # Pay using card_name for Cash card item
    if not click_message_box_key("YES", verify=False): # Clicks Yes for Activation
        logger.warning("Unable to click Yes for Activation")
        return False
    # if not pay_card(brand, card_name, debit_fee, cashback_amount, zip_code, cvn, custom):
    #     logger.warning(f"Unable to purchase Cash Card Item using {card_name} card.")
    #     return False

    if not click_function_key('Pay', timeout=3, verify=False):
        return False
    if _is_element_present(PROMPT['body']): # Loyalty
        click_message_box_key(key='No', verify=False)
    if not click_tender_key("Card", verify=False):
        return False

    try:
        payload = pinpad.swipe_card(
            brand=brand,
            card_name=card_name,
            debit_fee=debit_fee,
            cashback_amount=cashback_amount,
            zip_code=zip_code,
            cvn=cvn,
            custom=custom
        )
    except Exception as e:
        logger.warning(f"Card swipe in pay_card failed. Exception: {e}")
        click_function_key("Cancel", verify=False)
        return False
    try:
        start_time = time.time()
        while time.time() - start_time < 5:
            if "swipe card for activation" in _get_text(PAYMENT_PROC['text']).lower():
                payload = pinpad.swipe_card(
                    brand=brand,
                    card_name=gift_card
                )
                break
        else:
            logger.warning(f"Did not get the swipe card for activation prompt.")
    except Exception as e:
        logger.warning(f"Card swipe in pinpad.swipe_card failed. Exception: {e}")
        click_function_key("Cancel", verify=False)
        return False

    return _process_gift_card(gift_card, payload)

@test_func
def recharge_gift_card(brand='Core', card_name='Visa', gift_card="GiftCard", debit_fee=False, cashback_amount=None, zip_code=None, cvn=None, custom=None):
    """
    DEPRECATED - USE CASH CARD ARGS IN ADD_ITEM AND PAYMENT FUNCTIONS INSTEAD

    Pays for Cash Card item using the card_name you provided.
    Then, we click Yes for Activation and recharges the gift_card you provided. 
    Args:
        brand   : (str) String representation of the Brand (found in CardData.json)
        card_name : (str) The key/name of the card you wish to use located in the CardData.json file to pay for the Cash Card item.
        gift_card : (str) The key/name of the gift card you will recharge.
        expiration_date : (str) The string representation of expiration date for card that'll be entered on POS.
        zip_code : (str) The ZIP code value you wish to enter
        custom : (str) The Custom prompt value you wish to enter
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if fail
    Examples:
        >>> 
    """
    logger.warning("recharge_gift_card is deprecated - use cash card args in add_item and payment functions instead")

    # Pay using card_name for Cash card item
    if not click_message_box_key("No", verify=False): # Clicks NO for Recharge
        logger.warning("Unable to click No for Recharge")
        return False
    # if not pay_card(brand, card_name, debit_fee, cashback_amount, zip_code, cvn, custom):
    #     logger.warning(f"Unable to purchase Cash Card Item using {card_name} card.")
    #     return False
    if not click_function_key('Pay', verify=False):
        return False
    if not click_tender_key("Card", verify=False):
        return False

    if _is_element_present(PROMPT['body']): # Loyalty
        click_message_box_key(key='No', verify=False)
    
    try:
        payload = pinpad.swipe_card(
            brand=brand,
            card_name=card_name,
            debit_fee=debit_fee,
            cashback_amount=cashback_amount,
            zip_code=zip_code,
            cvn=cvn,
            custom=custom
        )
    except Exception as e:
        logger.warning(f"Card swipe in pay_card failed. Exception: {e}")
        click_function_key("Cancel", verify=False)
        return False

    # Swipe GiftCard for Recharge
    pinpad.reset()
    
    time.sleep(5) # TODO: need to fix to wait for processing text to have Recharge

    try:
        payload = pinpad.swipe_card(
            brand=brand,
            card_name=gift_card
        )
    except Exception as e:
        logger.warning(f"Card swipe in pinpad.swipe_card failed. Exception: {e}")
        click_function_key("Cancel", verify=False)
        return False

    return _process_gift_card(gift_card, payload)

def _network_status(brand='Concord'):
    """
    Read the network status from GUI and return based on the network status value
    Args: 
        brand : (str) String representation of the Brand (found in CardData.json)
    Returns: (bool) True on success, False on failure.
    """
    # Click on the Network Status menu bar.
    status = click_status_line_key("network status")
    if not (status):
        logger.error(f"Unable to check the network status.")
        return False
    time.sleep(1)
    logger.warning(f"Read Network Status")
    status = read_network_status()
    if (len(status) > 0):
        try:
            if not(status[brand] == 'Network Online'):
                logger.error(f"[{brand}] status: [{status[brand]}]")
                return False
            return True
        except Exception as e:
            logger.error(f"Unable to read network status for brand [{brand}]. Exception: {e}")
            return False
    else:
        logger.error(f"Unable to read network status.")
        return False

def _check_trans_state():
    """
    Check the pos transation state
    """
    is_proceed = False
    jrnl_txt = read_journal_watermark()
    logger.warning(f"Journal Text : [{jrnl_txt}]")
    if (jrnl_txt == ''):
        # Check transaction is in progress or not
        balance = read_balance()
        if (balance['Subtotal'] == '$0.00' and balance['Basket Count'] == '0' and balance['Total'] == '$0.00'):
            # No pending transactions
            is_proceed = True
        else:
            is_proceed = False
    else:
        if (jrnl_txt == 'TRANSACTION IN PROGRESS'):
            is_proceed = False
        elif (jrnl_txt =='TRANSACTION VOIDED' or jrnl_txt == 'TRANSACTION COMPLETE'):
            is_proceed = True
    return is_proceed

def de_activate_gift_card(brand='Concord', card_name='GiftCard'):
    """
    De Activate the gift card functionality from POS HTML GUI
    Args:    
        brand   : (str) String representation of the Brand (found in CardData.json)
        card_name : (str) The key/name of the card you wish to use located in the CardData.json file.
    Return: (bool) True on success, False on failure.
    Examples:
        >>> de_activate_gift_card('Concord')
        True
        >>> de_activate_gift_card()
        True
        >>> de_activate_gift_card('Concord', 'GiftCard')
        True    
    """
    logger.warning(f"De_Activate_gift_card for brand [{brand}], card name = [{card_name}]")
    # Check Network Status and if Online Proceed, otherwise return False
    if not(_check_trans_state()):
        logger.warning(f"Transaction is in progress, unable to proceed")
        return False
    logger.warning(f"Checking Network Status...")
    status = _network_status(brand)
    click_function_key("back")
    if not(status):
        return False
    logger.warning(f"Proceed to perform de-activate GiftCard.")
    click_status = click_function_key("Store")
    if not (click_status):
        logger.error(f"Function Key 'Store' unable to perform @ de_activate_gift_card")
        return False
    time.sleep(1)
    click_status = click_function_key("De-Activate Card")
    if not (click_status):
        logger.error(f"Function Key 'De-Activate Card' unable to perform @ de_activate_gift_card")
        return False
    time.sleep(1)
    click_till_key("1")
    click_till_key("00")
    time.sleep(1)
    click_till_key("Enter")
    time.sleep(3)
    try:
        payload = pinpad.swipe_card(
            brand=brand,
            card_name=card_name)
        logger.warning(f"payload value : [{payload}]")
        if (payload['success']):
            _check_message()
        else:
            logger.error(f"Payload Failed, unable to process de-active gift card.")
            return False
        return True
    except Exception as e:
        logger.error(f"Card swipe in de_activate_gift_card failed. Exception: {e}")
        return False

def _check_message(action="OK"):
    """
    If popup message is visible, then read the message and perform the action based on the parameter
    """
    try:
        popup_msg = read_message_box()
        logger.warning(f"popup_msg = [{popup_msg}]")
        click_message_box_key("OK")
    except Exception as e:
        logger.warning(f"No popup message found: {e}")

@test_func
def add_fuel(amount, dispenser=1, mode="Prepay", grade="REGULAR", level="CASH", fuel_type=None, def_type=None):
    """
    Add fuel to the current transaction.
    Args:
        amount: (str) Dollar amount of fuel to purchase.
        dispenser: (int) Number of the dispenser to purchase fuel on.
        mode: (str) Prepay, preset, or manual.
        grade: (str) The fuel grade to select. Only applies to manual fuel sales.
        level: (str) Cash/Credit pricing level. Only applies to manual fuel sales.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
        fuel_type: (str) This is just used in Commercial Diesel Transactions and it is provided, also def_type should provided. One of the three possible fuel types presented in the prompt
        def_type: (str) This is just used in Commercial Diesel Transactions and it is provided, also fuel_type should provided.This is a prompt that just allows Yes or No

    Return: 
        bool: True on success, False on failure.
    Examples:
        >>> add_fuel("$20.00", 3)
        True
        >>> add_fuel("$11.11", 4, "Manual", "SUPREME", "Credit")
        True
    """    
    wait_disp_ready(dispenser, verify=False)

    if not select_dispenser(dispenser, timeout=3, verify=False):
        return False

    level = level + " PRICING"

    if mode.upper() == "MANUAL" or mode.upper() == "MANUAL SALE":
        click_forecourt_key("MANUAL SALE", timeout=5, verify=False)
        select_list_item(grade, timeout=5)
        if read_message_box(timeout=3):
            select_list_item(level)
    else:
        click_forecourt_key(mode, timeout=5, verify=False)

    stripped_amount = amount.replace("$", "").replace(".", "")
    
    #Checking if the commercial values were provided, if not assume that this isn't a commercial transaction
    if not fuel_type is None  and not def_type is None:
        msg = read_message_box(timeout=10)
        if msg == "Tractor, Reefer or Both?":
            if click_message_box_key(fuel_type, verify=False, timeout=5):
                logger.info("[%s] was selected." %(fuel_type))
            else:
                logger.error(f"Failed attempting to select {fuel_type}")

        msg = read_message_box(timeout=10)
        if msg == "DEF?":
            if click_message_box_key(def_type, verify=False, timeout=5):
                logger.info("[%s] was selected for DEF prompt." %(def_type))
            else:
                logger.error(f"Failed attempting to select {fuel_type}")
    
    elif not fuel_type is None or not def_type is None:

        self.log.error("If either fuel_type or def_type is provided, the other one must be provided also")
        return False
        
    msg = read_message_box()
    if msg:
        logger.warning(f"Couldn't add fuel. Message: {msg}") # Probably already has a prepay
        click_message_box_key("Ok")
        return False

    enter_keypad(stripped_amount, timeout=5)
    click_keypad('ENTER', verify=False)
    msg = read_message_box()
    if msg:
        logger.warning(f"Couldn't add fuel: Message: {msg}")
        click_message_box_key("Ok")
        return False
    return True

@test_func
def wait_for_fuel(dispenser = 1, timeout=45):
    '''
    Wait for the dispenser to finish fueling.

    Args:
        dispenser: (int) The dispenser you want to check.
        timeout: (int) How long you want to wait for the dispenser to finish.

    Returns:
        True/False: (bool) True when the dispenser finishes, or False when it times out.
    '''
    logger.debug(f"Selecting Dispenser #{dispenser}")
    select_dispenser(dispenser)
    start_time = time.time()
    #Wait for the dispenser status to become 'IDLE'
    while time.time() - start_time <= timeout:
        diag = read_dispenser_diag()
        logger.debug(diag)
        if 'IDLE' in diag['Status']:
            logger.debug("Dispenser is Idle")
            return True
    logger.warning("Timed out waiting for the Dispenser to go Idle")
    return False

@test_func
def wait_disp_ready(dispenser=1, idle_timeout=30, dl_timeout=720):
    """
    Wait for a dispenser to be idle, and wait for a download to complete if necessary.
    Args:
        dispenser: (int) The number of the dispenser.
        idle_timeout: (int) How many seconds to wait for the dispenser to be idle.
        dl_timeout: (int) How many seconds to wait for the download to complete, if needed.
    Returns: (bool) Whether or not the dispenser finishes downloading within the timeout.
    Examples:
        >>> wait_disp_ready()
        True
        >>> wait_disp_ready(2, 60)
        False
    """
    if not wait_for_disp_status('Idle', dispenser, idle_timeout, verify=False):
        status = read_dispenser_diag()['Status']
        icon = _find_element(FORECOURT['current status icon'])
        if 'DOWNLOAD' in status or (icon and 'download' in icon.get_attribute('class')):
            logger.info(f"Dispenser {dispenser} is downloading. Waiting up to {dl_timeout} seconds for it to finish.")
            if not wait_for_disp_status('Idle', dispenser, dl_timeout, verify=False):
                logger.warning("Download did not complete within {dl_timeout} seconds.")
                return False
        else:
            logger.warning(f"Dispenser {dispenser} did not become idle or start a download within {idle_timeout} seconds. Actual status: {status}")
            return False
    
    # If status is IDLE we need to set this to true so the function do not fail
    return True

@test_func
def wait_for_disp_status(status, dispenser = 1, timeout=60):
    """
    Wait for a dispenser to have a given status.
    Args:
        status: (str) The status to check for. Use None or empty string for blank status.
        dispenser: (int) The dispenser you want to check.
        timeout: (int) How many seconds to wait for the desired status.
    Returns: (bool) Whether or not the desired status occurred within the timeout.
    Examples:
        >>> wait_for_disp_status("Download", 2)
        True
        >>> wait_for_disp_status("")
        True
    """
    if not status:
        status = 'IDLE' # read_dispenser_diag returns IDLE if there is no status

    select_dispenser(dispenser, verify=False)
    last_diag = ""
    start_time = time.time()
    while time.time() - start_time <= timeout:
        diag = read_dispenser_diag()
        if diag != last_diag:
            logger.info(f"Current status is {diag}")
            last_diag = diag
        if status.upper() in diag['Status'].upper():
            return True
    logger.warning(f"Dispenser did not have status {status} within {timeout} seconds.")
    return False

@test_func
def add_item_to_pricebook(scan_code, item_price, item_description, item_dept, timeout=default_timeout):
    """
    Adds an item to the pricebook. If the item already exists, then it will safely click Ok until
    it gets out of all of the prompts.
    Args:
        scan_code: (str) The scan code for the PLU.
        item_price: (str) The item's price.
        item_description: (str) The item's description.
        item_dept: (str) The item's department to which it will belong to.
        timeout: (int) How long to search for the key before failing.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if fail
    Examples:
        >>> add_item_to_pricebook("5555", "10.00", "Some Description", "10")
        True
        >>> add_item_to_pricebook("1111", "10.00", "Some Description", "99")
        False
    """
    try:
        click_function_key(
            STORE_FUNCTION_NAMES['add_item_to_pricebook'], verify=False
        )
        enter_keypad(str(scan_code), verify=False)
        click_keypad(KEYPAD_NAMES['enter'], timeout, verify=False)
        
        # PLU already exists
        if _is_element_present(PROMPT['body']):
            plu_exists = "PLU [%s] already exists, cannot add item" %(scan_code)
            if plu_exists == _get_text(PROMPT['body']):
                logger.warning("%s" %(plu_exists))
                return click_prompt_key('ok', verify=False)

        enter_keypad(str(_strip_currency(item_price)), verify=False)
        click_keypad(KEYPAD_NAMES['enter'], timeout, verify=False)
        enter_keyboard_value(item_description, verify=False)
        click_keyboard_key('Ok', verify=False)
        
        full_dept = item_dept
        if item_dept[0:4].upper() == "DEPT":
            full_dept = item_dept[5:]
            full_dept += " - " + item_dept
        select_list_item(full_dept, verify=False)

        click('Yes', verify=False)
        return click('Ok', verify=False)
    except:
        logger.warning("Unable to add [%s] to pricebook" %(scan_code))
        return False

@test_func
def click(key, timeout=10):
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
    func_keys_list = [FUNC_KEYS[key] for key in FUNC_KEYS if type(FUNC_KEYS[key]) == list]
    func_keys_list = [item for sublist in func_keys_list for item in sublist]
    func_keys_list += FUNC_KEYS['re-map'].keys()


    # Map of functions and the keys they may be used to click on.
    map = { "click_function_key": func_keys_list,
            "click_message_box_key": [WILD, "ok", "yes", "no", "cancel"] + list(PROMPT.values()),
            "click_speed_key": ['generic item', WILD],
            "click_dept_key": [f"dept {i}" for i in range(1,16)] + [WILD],
            "click_forecourt_key": FORECOURT.keys(),
            "click_preset_key": ['$5.00', '$10.00', '$20.00', '$50.00', 'regular', 'plus', 'supreme', WILD],
            "click_tender_key": ['$1.00', '$5.00', '%10.00', '$20.00', '$50.00', 'card', 'check', 'cash', 'imprinter', 'other', WILD],
            "click_keypad": KEYPAD.keys(),
            "click_pwd_key": KEYBOARD.keys(),
            "click_receipt_key": RECEIPTS.keys(),
          }

    # Figure out which functions might work for the desired key
    def build_func_list(key):
        import sys
        funcs_to_try = []
        for func in map:
            if key.lower() in map[func]:
                funcs_to_try.append(getattr(sys.modules[__name__], func))
        return funcs_to_try

    # Create list of functions to search with
    funcs_to_try = build_func_list(key)
    if len(funcs_to_try) == 0:
        # Requested key doesn't match any known menus, try menus that can have custom keys
        funcs_to_try = build_func_list(WILD) # Menus that can contain buttons with any text
    
    # Invoke the functions repeatedly until success or timeout
    log_level = logger.getEffectiveLevel()
    if log_level > logging.DEBUG:
        logging.disable() # Temporarily disable logging to prevent spam, unless we're at debug level
    start_time = time.time()
    while time.time() - start_time <= timeout:
        for func in funcs_to_try:
            if func(key, timeout=0, verify=False):
                logging.disable(logging.NOTSET)
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
    logger.debug("Entered enter_plu() method")
    # logger.debug("Trying to open keypad")
    # if not click_status_line_key("keypad", verify=False, timeout=timeout):
    #     logger.warning("Unable to open keypad to enter PLU.")
    #     return False
    
    #TODO must be added back into enter_plu in edge.py if it fixes issues.  Part of my fixes that were removed.
    prompt_time = time.time()
    while (time.time()-prompt_time < timeout):
        click_status_line_key("keypad", verify=False, timeout=timeout)
        if (read_keypad_prompt() == "Enter PLU"):
            break
    else:
        logger.warning("Was unable to click keypad or keypad prompt never said 'Enter PLU'")
        return False

    logger.debug("Trying to enter plu")
    return enter_keypad(plu, after="Enter", timeout=2, verify=False)

@test_func
def check_receipt_for(values, rcpt_num=1, dispenser=None, timeout=default_timeout):
    """
    Verify that a receipt contains a specific value or set of values. Ignores whitespace.
    Args:
        values: (str/list) A string or list of strings to find in the receipt.
        rcpt_num: (int) Position of the receipt in the receipt list. Default is 1, the most recent receipt.
        dispenser: (int) Which dispenser to verify the receipt from, if any. None is indoor receipt search.
        timeout: (int) How long to repeat the search for before returning False.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if all values are verified, False if not
    Examples:
        >>> check_receipt_for("Generic Item $0.01")
        True
        >>> check_receipt_for("Total = asdfjkl;")
        False
        >>> check_receipt_for(["Plus CA PUMP# 1", "5.000 GAL @ $1.000/GAL", "$5.00"], dispenser=1, rcpt_num=2)
        True
    """
    if type(values) is not list:
        values = [values]

    attempts = 0
    start_time = time.time()
    lines_not_found = []
    while time.time() - start_time <= timeout:
        if dispenser is not None:
            select_dispenser(dispenser, verify=False)
            click_forecourt_key("Receipt", timeout, verify=False)
        else:
            click_function_key("Receipt Search", timeout, verify=False)
        select_receipt(rcpt_num, verify=False)
        actual_rcpt = read_receipt()
        ret = True
        for value in values:
            value = value.replace(' ', '')
            # List comprehension to search every line of the receipt while ignoring whitespace
            if not any([value in line.replace(' ', '') for line in actual_rcpt]):
                lines_not_found.append(value)
                logger.debug("Did not find %s in the receipt." % value)
                ret = False
        attempts += 1
        if ret:
            return ret
    
    #Removing duplicates
    lines_not_found = list(dict.fromkeys(lines_not_found))
    logger.warning(f"Did not find {lines_not_found} in the receipt within {timeout} seconds. ({attempts} attempts)")
    return False

"""
Read Functions
"""
def read_message_box(timeout=default_timeout, text = 'body'):
    """
    Read the text of the popup message on the POS, if it exists.
    Args:
        timeout: (int) The time (in seconds) that the function will look for the window's visibility.
        text: (str) the string indicating the container the text should be read from: __body__ or __header__
    Returns:
        str: The message in the message box
    Examples:
        >>> read_message_box()
        'Are you sure you want to void the transaction?'
        >>> read_message_box() # While no message box is visible
        None
    """
    try:
        if text == 'body':
            msg = _get_text(PROMPT['body'], timeout=timeout)
            return msg
        elif text == 'header':
            msg = _get_text(PROMPT['header'], timeout=timeout)
            return msg
    except:
        logger.error("Unable to read message box")
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
    if element:
        line = _get_text(controls['receipt journal']['line_by_instance'] % element).split('\n')
        if line is None:
            return []

    lines = _get_texts(controls['receipt journal']['lines'], timeout=timeout)
    if lines is None:
        return []

    return [line.split('\n') for line in lines]  


def read_balance(timeout=default_timeout):
    """
    Get the transaction totals: basket count, total, and
    balance, etc.
    Args:
        timeout: (int) How long to wait for the window to be available.
    Returns:
        dict: A dictionary mapping each total element to its corresponding
              value.
    Examples:
        >>> read_balance()
        {'Subtotal': '$0.01', 'Tax': '$0.00', 'Basket Count': '1', 'Total': '$0.01', 'Change': '$0.00'}
        >>> read_balance()
        {'Subtotal': '$10.00', 'Basket Count': '2', 'Total': '$10.00', 'Balance Due': '$5.00'}
    """
    time.sleep(.1) # Usually called after an update. Makes sure we don't read too soon.
    balance_locator = controls['receipt journal']['totals']
    extra_totals_locator = controls['receipt journal']['extra totals']

    # Get text contents of the balance
    start_time = time.time()
    while time.time() - start_time <= timeout:
        if not _find_element(extra_totals_locator, 0.5):
            if not click_key(balance_locator, 0.5):
                logger.warning("Unable to expand the list of transaction totals. Some total lines may be missing.")
        contents = _get_text(balance_locator)
        if contents:
            break
    else:
        logger.warning("Unable to read balance within {timeout} seconds.")
        return {}
    
    # Convert text contents into a dict
    contents = contents.split('\n')
    receipt_contents = {}
    for i in range(0, len(contents), 2):
        receipt_contents.update({contents[i]: contents[i+1]})

    return receipt_contents

def read_journal_watermark(timeout=default_timeout):
    """
    Get the text of the watermark in the transaction receipt journal.
    Args:
        timeout: (int) How long to wait for a watermark to be visible.
    Returns: (str) The text of the watermark.
    Examples:
        >>> read_journal_watermark()
        'TRANSACTION VOIDED'
        >>> read_journal_watermark()
        ''
    """
    wm = _get_text(JOURNAL["watermark"], timeout)
    return '' if wm is None else wm.replace('\n', ' ')
    
def read_suspended_transactions(timeout=default_timeout):
    """
    Read the contents of the suspended transactions list.
    Args:
        timeout: (int) How long to wait for the list to be readable.
    Returns:
        list: The reg #, transaction #, and amount of each transaction.
    Examples:
        >>> read_suspended_transactions()
        [['1', '11', '$0.01'], ['1', '15', '$5.00']]
        >>> read_suspended_transactions()
        []
    """
    result = []
    texts = _get_texts(TRANSACTIONS['transaction'], timeout=1)
    if not texts:
        if not click_status_line_key('transactions', timeout=1, verify=False):
            logger.warning("There are no suspended transactions.")
            return []
        texts = _get_texts(controls['suspended transactions']['transaction'])
        click_status_line_key('transactions', verify=False)

    return [text.split('\n') for text in texts]

def read_receipt(timeout=default_timeout):
    """
    Gets the text from a receipt after clicking the Search key.
    Args:
        timeout: (int) How long to wait for the window to be available.
    Returns:
        list: Each line of the receipt
    Examples:
        >>> read_receipt()
        ['Header', '', 'Store Name,  299', '123 Somewhere St', 'Raleigh, NC  27587',
         '                      ', '', '          03/11/2019 9:12:28 AM', 
         '    Register: 1 Trans #: 455 Op ID: 91', '            Your cashier: Area',
          '', ' *** REPRINT *** REPRINT *** REPRINT ***', '', 
          'Generic Item                     $0.01  99', 
          '                            ----------    ', 
          '                   Subtotal =    $0.01    ', 
          '                       Tax  =    $0.00    ', 
          '         ----------    ', '                      Total =    $0.01    ',
           '', ' *** REPRINT *** REPRINT *** REPRINT ***', '', 
           '                Change Due  =    $0.00    ', '', 
           'Cash                             $0.01    ', '', '', '', 'Footer']
    """
    # Implement HTMLParser
    class ReceiptParser(HTMLParser):
        def __init__(self):
            super(ReceiptParser, self).__init__()
            self.data = []

        def handle_data(self, data):
            data = data.split("\n")
            for el in data:
                el = el.strip()
                if el:
                    self.data.append(el)

    receipt_locator = RECEIPTS['receipt']
    contents = _find_element(receipt_locator, timeout)
    parser = ReceiptParser()
    parser.feed(contents.get_attribute('innerHTML'))
    return parser.data

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
    return _get_text(KEYPAD['display'], timeout=timeout)

def read_keyboard_entry(timeout=default_timeout):
    """
    Read the current entry in the text field above the keyboard.
    Args:
        timeout: (int) How long to wait for the window to be available.
    Returns:
        str: The contents of the field.
    Examples:
        >>> read_keyboard_entry()
        'Some text'
        >>> read_keyboard_entry()
        ''
    """
    return _get_text(KEYBOARD['entry'], timeout=timeout)

def read_dispenser_diag(timeout=default_timeout):
    """
    Read the diag lines for a dispenser.
    Args:
        timeout: (int) How long to wait for the window to be available.
    Returns:
        dict: Each item in the dispenser diag.
    Example:
        >>> read_dispenser_diag()
        {'Status': 'CRIND DISABLED', 'Errors': 'The CRIND was reset to correct a problem'}
        >>> read_dispenser_diag()
        {'Status': 'IDLE', 'Errors': None}
    """
    status_loc = FORECOURT['dispenser status']
    error_loc = FORECOURT['dispenser error']
    contents = _get_text(status_loc)
    contents = contents.split("\n") if contents else ['IDLE']
    errors = _get_text(error_loc)
    errors = errors.split("\n") if errors else [None]

    result = {}
    result.update({'Status' : contents[0].upper(), 'Errors' : errors[0]})
    return result

def read_fuel_buffer(buffer_id='A', timeout=default_timeout):
    """
    Get the current contents of a fuel buffer.
    Args:
        buffer_id: (char) Letter of the buffer to read.
        timeout: (int) How long to wait for the window to be available.
    Returns:
        list: The text contents of the buffer. In order:
              buffer status, amount dispensed (if fueling in progress),
              total amount, total volume, PPU, grade
    Examples:
        >>> read_fuel_buffer('B')
        ['$9.58', '6.387 GAL @ $1.500/GAL', 'PLS CR', 'Fuel Sale']
        >>> read_fuel_buffer()
        ['Prepay $5.00']
    """
    try:
        loc = FORECOURT[f"buffer {buffer_id.lower()}"]
    except KeyError:
        logger.warning("please enter 'A' or 'B' for buffer_id")
        return []

    return _get_text(loc, timeout=timeout).split("\n")[1:]

def read_keypad_prompt(timeout=default_timeout):
    """
    Read the prompt text from the keypad or login keypad.
    Args:
        timeout: (int) How long to wait for the window to be available.
    Returns:
        str: the text in the display in the keypad window
    Example:
        >>> read_keypad_prompt()
        "Department 'Dept 16' requires a price to be entered."
    """
    logging.disable(logging.WARNING)
    start_time = time.time()
    while time.time() - start_time <= timeout:
        text = _get_text(KEYPAD['description'], timeout=1)
        if not text:
            # Keypad has two different elements that display prompts. Try the other one
            text = _get_text(KEYPAD['prompt'], timeout=1)
        if not text:
            # Try login keypad
            text = _get_text(LOGIN['display'], timeout=1)      
        if text:
            logging.disable(logging.NOTSET)
            return text
    else:
        logging.disable(logging.NOTSET)
        logger.warning(f"Keypad prompt not available within {timeout} seconds.")
        
def read_info(timeout=default_timeout):
    """
    Read the text information on the POS Info screen.
    Args:
        timeout: (int) How long to wait for the window to be available.
    Returns:
        (dict) The text contents of the info screen. (NOT green/red status indicators)
    Examples:
        >>> read_info()
        {'Operator ID': '55', 'Register ID': '1', 'Store ID': '299', 'Store Phone': '(919) 555-5555',
         'Help Desk Phone': '(919) 555-5555', 'Passport Version': '99.99.23.01_DB1902211018', 
         'Support Enabled': 'No', 'SZR Tunnel Status': 'Disabled','Model #': '0', 'Serial #': '0', 
         'NTEP CC No.': '02-039'}
    """
    result = {}
    info_locator = INFO['list']
    
    start_time = time.time()
    while time.time() - start_time <= timeout:
        try:
            contents = _get_text(info_locator).split("\n")
        except:
            continue
    
    if contents == None:
        return None
    
    contents = contents[1:]
    for i in range(0, len(contents)-1, 2):
        key = contents[i]
        val = contents[i+1]
        result.update({key:val})
    
    return result

def read_network_status(timeout=default_timeout):
    """
    Read the text information on the POS Info screen.
    Args:
        timeout: (int) How long to wait for the window to be available.
    Returns:
        (dict) The text contents of the info screen. (NOT green/red status indicators)
    Examples:
        >>> read_network_status()
        {'ExxonMobil': 'Network Online', 'Kickback': 'Disabled'}
    """
    result = {}
    network_locator = NETWORK['list']
    contents = None
    start_time = time.time()
    while time.time() - start_time <= timeout:
        try:
            contents = _get_text(network_locator).split("\n")
        except:
            continue
    
    if contents == None:
        return {}
    
    # contents = contents[1:]
    for i in range(0, len(contents)-1, 2):
        key = contents[i]
        val = contents[i+1]
        result.update({key:val})
        i = i + 2
    return result

def read_processing_text(timeout=default_timeout):
    try:
        return _get_text(PAYMENT_PROC['text'], timeout=timeout)
    except Exception as e:
        logger.warning(f"Unable to read processing text : {e}")
        return ""

"""
Misc. click/select functions
"""
@test_func
def click_journal_item(item=None, instance=1, timeout=default_timeout):
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
        >>> click_journal_item()
        True
        >>> click_journal_item("Generic Item")
        True
        >>> click_journal_item(instance=3)
        False
        >>> click_journal_item("NotInTheJournal")
        False
    """
    return click_key(JOURNAL["line"] % (item.lower(), instance), timeout=timeout)

@test_func
def click_suspended_transaction(price=None, instance=1, timeout=default_timeout):
    """
    Select a suspended transaction. Please not that this may
    not work if a list dialog is open (qualifiers, restrictions,
    etc.)
    Args:
        price: (str) The price of the transaction to resume, i.e. $0.01
        instance: (int) Which transaction to select if there are multiple matches
            or if no price is specified.
        timeout: (int) How long to wait for the window to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if fail, None if error
    Examples:
        >>> click_suspended_transaction()
        True
        >>> click_suspended_transaction("$5.00")
        True
        >>> click_suspended_transaction(instance=3)
        True
        >>> click_suspended_transaction("$999999.99")
        False
    """
    logger.debug("Entered click_suspended_transaction() method")
    logger.debug("Checking if the suspended transaction list is opened already")
    # Click suspended transaction button if the list of suspended transactions is not opened
    if not _is_element_present(TRANSACTIONS['transaction']):
        logger.debug("Clicking suspended transaction button")
        click_status_line_key('Transactions', verify=False)
    
    # Get a list with suspended transactions
    logger.debug("Obtaining a list with suspended transactions")
    if price is None:
        trans_list = _find_elements(TRANSACTIONS['transaction'], timeout=timeout)
    else:
        trans_list = _find_elements(TRANSACTIONS['transaction_by_price'] % price, timeout = timeout)

    if trans_list == None:
        # Nothing was found
        logger.error("Unable to resume the transaction since no suspended transactions were found")
        return False
    else:
        # Try to click on the target instance
        logger.debug("Trying to click on the transaction with instance [%d]"%(instance))
        trans_list[instance - 1].click()
            
        logger.debug("Checking for popup message about resuming transaction")
        msg = read_message_box()
        if msg and "Do you want to resume" in msg:
            logger.debug("Trying to accept the popup message")
            return click_message_box_key('Yes', verify=False)
        else:
            logger.error(f"Encountered unexpected message while trying to resume a transaction: {read_message_box()}")
            return False

@test_func
def select_receipt(num, timeout=default_timeout):
    """
    Select a receipt from the receipt list.
    Args:
        num: (str) Position of the receipt to select in the list.
        timeout: (int) How long to wait for the window to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> select_receipt(1)
        True
        >>> select_receipt(4)
        True
        >>> select_receipt(9999999999)
        False
    """
    # TODO: Select by reg/time/trans#/amount    
    return click_key(RECEIPTS['item_by_index'] % num)

@test_func
def select_list_item(list_item, timeout=default_timeout):
    """
    Select an item from a list prompt, such as qualifiers or reason codes.
    Delegates to click_message_box_key()
    Args:
        list_item: (str) The item in the list to select.
        timeout: (int) How long to wait for the window to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: Whether or not the item was successfully selected
    Examples:
        >>> select_list_item("EMPLOYEE DISCOUNT")
        True
        >>> select_list_item("6-PACK")
        True
        >>> select_list_item("NotAListItem")
        False
    """
    return click_message_box_key(list_item, timeout = timeout, verify=False)

@test_func
def select_dispenser(disp_num, timeout=default_timeout):
    """
    Select a dispenser in the POS dispenser GUI.
    Args:
        disp_num: (int) The number of the dispenser to select.
        timeout: (int) How long to wait for the window to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True for success, False for failure.
    Examples:
        >>> select_dispenser(3)
        True
        >>> select_dispenser(65)
        False
    """
    return click_key(FORECOURT['dispenser'] % disp_num, timeout)

@test_func
def click_fuel_buffer(buffer_id, timeout=default_timeout):
    """
    Click on a fuel buffer
    Args:
        buffer_id: (char) The buffer to select, A or B
        timeout: (int) How long to wait for the window to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: Success/failure
    Examples:
        >>> click_fuel_buffer('A')
        True
        >>> click_fuel_buffer('B')
        False
        >>> click_fuel_buffer('C')
        None
    """
    logger.debug("Entered click_fuel_buffer() method")
    try:
        return click_key(FORECOURT[f"buffer {buffer_id.lower()}"], timeout)
    except KeyError:
        logger.error(f"Buffer should be A or B and not {buffer_id}")
        return False

"""
Scanner functions
"""
@test_func
def scan_item(barcode, timeout=default_timeout):
    """
    Scans an item using IP bar code scanner
    Args:
        barcode : (str) The barcode you wish to send
        timeout: (int) How many seconds to keep retrying for if the scan fails.
    Returns:
        bool: True if success, False if failure
    """
    start_time = time.time()
    while time.time() - start_time <= timeout:
        if scanner.scan(barcode):
            return True
        time.sleep(1)
    else:
        logger.warning(f"Unable to successfully scan {barcode} after trying for {timeout} seconds.")
        return False
 
@test_func
def scan_id(barcode, timeout=default_timeout):
    """
    Scans driver's license or some form of ID using IP bar code scanner
    Args:
        barcode : (str) The barcode you wish to send
        timeout: (int) How many seconds to keep retrying for if the scan fails.
    Returns:v
        bool: True if success, False if failure
    """
    return scan_item(barcode, timeout)

"""
Click helper functions.
"""
@test_func
def click_function_key(key, timeout=default_timeout):
    """
    Click a key in the POS function key window.
    Args:
        key: (str) The key to click.
        timeout: (int) How long to wait for the window to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> click_function_key("CLOSE TILL")
        True
        >>> click_function_key("GENERIC ITEM")
        False
    """
    
    logger.debug(f"Click in function key {key}")

    try: # Support alternate mappings, for WPF cross-compatibility and future proofing
        key = FUNC_KEYS['re-map'][key.lower()]
    except KeyError:
        pass

    # Function key sub-menus that we will automatically switch to when needed
    autoswitch_menus = ["cashier", "store", "transaction"]
    
    # Switch to sub-menu if needed
    for menu in autoswitch_menus:
        if key.lower() in FUNC_KEYS[menu]:
            if click_key(FUNC_KEYS['key_by_text'] % menu, timeout):
                break

    return click_key(FUNC_KEYS['key_by_text'] % key.lower(), timeout)

@test_func
def click_till_key(key, timeout=default_timeout):
    """
    Click a key in the keypad window. This function is for cross-compatibility with WPF POS.
    Args:
        key: (str) The key that will be clicked. 
        timeout: (int) How long to wait for the window to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> click_till_key("1")
        True
        >>> click_till_key("Enter")
        True
        >>> click_till_key("durp")
        False
    """
    return click_keypad(key, timeout, verify=False)

@test_func
def click_tender_key(key, timeout=default_timeout):
    """
    Click a key in the POS tender window.
    Args:
        key: (str) The tender key to be clicked. Must be a string may represent a number.
        timeout: (int) How long to wait for the window to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> click_tender_key("Cash")
        True
        >>> click_tender_key("Exact Change")
        True
        >>> click_tender_key("NotATender")
        False
    """
    logger.debug("Entered click_tender_key() method")
    if key.lower() == "exact change":
         return click_key(PAYMENT['exact_amount'])
    elif key.startswith('$'):
        return click_key(PAYMENT['preset_amount'] % key.lower())
    else:
        return click_key(PAYMENT['type'] % key.lower())

@test_func
def click_speed_key(key, timeout=key_timeout, case_sens=False):
    """
    Click on a speed key. Switches to speed keys if POS is in dept key mode.              
    Args:
        key: (str) The text of the speed key to click on.
        timeout: (int) How long to wait for the window to be available.
        case_sens (bool): Whether to use a case sensitive search. Not yet implemented.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> click_speed_key("Generic Item")
        True
        >>> click_speed_key("Not A Speed Key")
        False
    """
    # Check if we need to switch to speed keys
    if _is_element_present(FUNC_KEYS['key_by_text'] % "speed keys", timeout):
        click_function_key("Speed Keys", timeout=1, verify=False)
    return click_key(ITEM_KEYS['key_by_text'] % key.lower(), timeout=1)

@test_func
def click_dept_key(key, timeout=key_timeout, case_sens=False):
    """
    Click on a department key. Switches to dept keys if POS is in speed key mode.
    Args:
        key: (str) The text of the dept key to click on.
        timeout: (int) How long to wait for the window to be available.
        case_sens (bool): Whether to use a case sensitive search. Not yet implemented.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> click_dept_key("Dept 8")
        True
        >>> click_dept_key("Not A Dept")
        False
    """
    # This timeout loop is kinda dumb. Do we even really need custom timeouts for everything?
    start_time = time.time()
    while time.time() - start_time <= timeout:
        if _is_element_present(FUNC_KEYS['selected_key'], 1):
            # If we're in Pay or Transaction (the button will be selected), we need to click Speed Keys and then Dept Keys
            if not click_function_key("speed keys", timeout=1, verify=False) or not click_function_key("dept keys", timeout=1, verify=False):
                continue
        elif _is_element_present(FUNC_KEYS['key_by_text'] % 'dept keys'):
            # If we're on speed keys, we need to click Dept Keys
            if not click_function_key("dept keys", timeout=1, verify=False):
                continue      
        
        if click_key(ITEM_KEYS['key_by_text'] % key.lower(), timeout=1):
            return True

    return False

@test_func
def click_message_box_key(key, timeout=default_timeout):
    """
    Click a key on the red popup message on the POS, if it exists.
    Args:
        key: (str) The key to click.
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
    logger.debug("Entered click_message_box_key() method")
    return click_key(PROMPT['key_by_text'] % key.lower(), timeout)

@test_func
def click_status_line_key(key, timeout=default_timeout):
    """
    Click the key on the top bar of the Edge POS
    Args:
        key: (str) The name of the key being clicked
        timeout: (int) How long to wait for the window to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> click_status_line_key("HELP")
        True
        >>> click_status_line_key("PRICE CHECK")
        False
    """
    return click_key(MENU_BAR[key.lower()], timeout=timeout)

@test_func
def click_receipt_key(key, timeout=default_timeout):
    """
    Click a key in the receipt search window.
    Args:
        key: (str) The key to be clicked.
        timeout: (int) How long to wait for the window to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> click_receipt_key("calendar")
        True
        >>> click_receipt_key("print")
        True
        >>> click_receipt_key("prev")
        True
        >>> click_receipt_key("hello")
        False
    """
    try:
        return click_key(RECEIPTS[key.lower()], timeout)
    except KeyError:
        return click_receipt_calendar_key(key, timeout, verify=False)

@test_func
def click_receipt_calendar_key(key, timeout=default_timeout):
    """
    Click a key in the receipt selection calendar.
    Args:
        key: (str) The key to be clicked.
        timeout: (int) How long to wait for the window to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> click_receipt_calendar_key("prev")
        True
        >>> click_receipt_calendar_key("next")
        True
        >>> click_receipt_calendar_key("23")
        True
        >>> click_receipt_calendar_key("hello")
        False
    """
    if key.isdigit():
        return click_key(RECEIPTS['calendar elements']['date'] % key.lower())
    return click_key(RECEIPTS['calendar elements'][key.lower()])

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
    try:
        if click_key(KEYPAD[key.lower()]):
            return True
    except KeyError:
        pass

    logger.debug(f"Couldn't click {key} in standard keypad. Trying login keypad...")
    try:
        if click_key(LOGIN[key.lower()]):
            return True
    except KeyError:
        pass

    logger.debug(f"Couldn't click {key} in login keypad. Trying keyboard...")
    try:
        if click_key(KEYBOARD[key.lower()]):
            return True
    except KeyError:
        pass

    logger.warning(f"Unable to click keypad key {key}.")
    return False

@test_func
def click_keyboard(key, timeout=default_timeout):
    """
    Click a single key in the keyboard.
    Args:
        key: (int/str) The keyboard key that will be clicked. Must be for a single key, if the
                key is '00' then it needs to be a string in the first place.
        timeout: (int) How long to wait for the window to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> click_keyboard('T')
        True
        >>> click_keyboard('2')
        True
        >>> click_keyboard('spacebar')
        True
        >>> click_keyboard('cancel')
        True
        >>> click_keyboard('yo')
        False
    """
    logger.debug("Entered click_keyboard() method")
    if key.lower() == 'spacebar':
        key = ' '
    return click_key(KEYBOARD[key.lower()], timeout=timeout)

@test_func
def click_forecourt_key(key, timeout=default_timeout):
    """
    Click a key in the POS forecourt GUI.
    Args:
        key: The text of the key to click.
        timeout: (int) How long to wait for the window to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True for success, False for failure.
    Examples:
        >>> click_forecourt_key("PREPAY")
        True
        >>> click_forecourt_key("MOVE PREPAY")
        True
        >>> click_forecourt_key('Durp')
        False
    """
    key = key.lower()
    logger.debug("Entered click_forecourt_key() method")
    # Most of these are function keys in Edge. Check there first
    if key in FUNC_KEYS["dispenser"]:
        return click_function_key(key, timeout, verify=False)
    return click_key(FORECOURT[key], timeout)

@test_func
def click_login_keypad(key, timeout=default_timeout):
    """
    Clicks on the login keypad.
    Args:
        key: (str) The key to be clicked.
        timeout: (int) How long to wait for the window to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> click_login_keypad("1")
        True
        >>> click_login_keypad("durp")
        False
    """
    return click_key(LOGIN[key.lower()], timeout)

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

"""
Click functions that are only for cross compatibility with WPF POS
"""
@test_func
def click_prepay_key(key, timeout=default_timeout):
    """
    Click an amount preset key when adding a prepay. This is for cross-compatibility with WPF POS.
    Note: grade selection is not supported for prepay on Edge.
    Args:
        key (str): The text of the key to click.
        timeout: (int) How long to wait for the window to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True for success, False for failure.
    Examples:
        >>> click_prepay_key("$10.00")
        True
        >>> click_prepay_key("PREMIUM")
        False
        >>> click_prepay_key("$-5.00")
        False
    """
    return click_key(KEYPAD['preset_by_text'] % key.lower(), timeout)

@test_func
def click_preset_key(key, timeout=default_timeout):
    """
    Click an amount preset key when presetting a dispenser, or a pricing level/grade/amount key when adding manual fuel. This is for cross-compatibility with WPF POS.
    Note: grade selection is not supported for preset on Edge.
    Args:
        key: The text of the key to click.
        timeout: (int) How long to wait for the window to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> click_preset_key("CREDIT LEVEL")
        True
        >>> click_preset_key("$20.00")
        True
        >>> click_preset_key("-$10.00")
        False
    """
    key = key.lower()
    if "level" in key:
        key.replace("level", "pricing") # Text changes from WPF to Edge
   
    if key.startswith('$'):
        return click_key(KEYPAD['preset_by_text'] % key.lower(), timeout)
    return click_key(PROMPT['key_by_text'] % key.lower(), timeout)

@test_func
def click_reminder_box_key(key, timeout=default_timeout):
    """
    Click a key in the prompt box. This is for cross-compatibility with POS.
    Args:
        key: (str) The key that will be select.
        timeout: (int) How long to wait for the window to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> click_reminder_box_key("OK")
        True
        >>> click_reminder_box_key("NOT OK")
        False
    """
    return click_message_box_key(key, timeout, verify=False)

@test_func
def click_info_key(key, timeout=default_timeout):
    """
    Click a key in the Info window. This is for cross-compatibility with WPF POS.
    Args:
        key: (str) The key to be clicked.
        timeout: (int) How long to wait for the window to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> click_info_key("Cancel")
        True
    """
    logger.debug("Edge does not have keys in the Info window. Doing nothing.")
    return True

@test_func
def click_restriction_keypad(key, timeout=default_timeout):
    """
    Click a key in the keypad. This is here for WPF cross-compatibility.
    Args:
        key: (int/str) The keypad key that will be clicked.
             Must be for a single key.
        timeout: (int) How long to wait for the window to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> click_restriction_keypad("Default")
        True
        >>> click_restriction_keypad("jkl;")
        False
    """
    return click_key(KEYPAD[key.lower()], timeout)

@test_func            
def click_restriction_key(key, timeout=default_timeout):
    """
    Click a key in the keypad. This is here for WPF cross-compatibility.
    Args:
        key: (str) Text describing the key to click. Please note that calendar dates and the Deny key are not supported on Edge.
        timeout: (int) How long to wait for the window to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> click_restriction_key("Deny")
        True
        >>> click_restriction_key("7 JULY")
        True
        >>> click_restriction_key("asdf")
        False
    """
    if key.upper() == "MANUAL":
        logger.info("Manual key is not supported for Edge. Skipping it since we can still enter birth date.")
        return True
    elif key.upper() == "DENY":
        raise FeatureNotSupported("Deny key is not supported for restriction handling on Edge.")

    return click_key(KEYPAD[key.lower()], timeout)

@test_func
def click_pwd_key(key, timeout=default_timeout):
    """
    Click a key in the password entry keyboard. This is for cross compatibility with WPF POS.
    Args:
        key: (str) the key that has been requested. Will only do ONE key at a time.
        timeout: (int) How long to wait for the window to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> click_pwd_key("Z")
        True
        >>> click_pwd_key("asdf")
        False
        >>> click_pwd_key("\\") # Watch out for escape characters!
        True
    """
    return click_keypad(key, timeout=1, verify=False)


"""
Prompt Helper Functions.
"""
def _is_element_present(locator, timeout=prompt_timeout, type = By.XPATH):
    """
    Helper function. Waits for the element/button to be present on the screen.
    Args:
        locator (str): Element's CSS locator
        timeout (int): How long to wait for the window and key to be available.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> _is_element_present(SOME_VALID_LOCATOR)
        True
        >>> _is_element_present(SOME_INVALID_LOCATOR)
        False
    """
    try:
        WebDriverWait(driver, timeout).until(lambda x: x.find_element(type, locator).is_displayed())
        return True
    except TimeoutException:
        logger.debug("Element with locator [%s] is not present within %s seconds." % (locator, timeout))
        return False
    except StaleElementReferenceException: # Sometimes raised if the DOM is modified while we check visibility. Just try again
        return _is_element_present(locator, timeout, type)

def _is_till_closed(timeout=prompt_timeout):
    """
    Helper function. Checks to see if the till is closed or not.
    Args:
        timeout (int): How long to wait for the window and key to be available.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> _is_till_closed()
        True
        >>> _is_till_closed()
        False
    """
    try:
        return _is_element_present(KEYPAD['description'])
    except:
        return False

"""
Helper Functions.
"""
def _sign_in(credentials):
    """
    Helper function for sign_on. Signs in to the Edge POS using credentials.
    Args:
        credentials: (tuple) The users sign on credentials (username, password)
    Returns:
        True if success, False if failure
    Examples:
        >>> _sign_in(('91', '91'))
        True
        >>> _sign_in(('123', 'TheWrongPassword'))
        False
    """
    logger.debug("Entered _sign_in() method")
    logger.debug(f"Entering id: {credentials[0]}")
    #Variable wait to ensure the prompt for the 'User ID' is displayed before the id is entered
    user_start_time = time.time()
    while (time.time() - user_start_time <= 30):
        if (read_keypad_prompt() == "User ID"):
            break
    else:
        logger.error("User prompt never showed on login keypad")
        return False

    for value in credentials[0]:
        time.sleep(0.70) # Has to be slowed down, otherwise failures raise
        if not click_login_keypad(str(value), verify=False):
            logger.error(f"Unable to click {value}")
            return False
    
    if not click_login_keypad('Enter', verify=False):
        logger.error("Unable to click Enter")
        return False

    #Variable wait to ensure the prompt for 'Password' is showing before it is entered.
    password_time = time.time()
    while (time.time() - password_time <= 30):
        if (read_keypad_prompt() == "Please enter your password." or read_keyboard_prompt() == "Please enter your password."):
            break
    else:
        logger.error("Password prompt never showed on login keypad")
        return False
    
    logger.debug(f"Entering pass: {credentials[1]}")
    # Sometimes, the keyboard is shown after entering the user, so checking if it is present
    if not credentials[1].isdigit() or not read_keyboard_prompt() is None:
        if read_keyboard_prompt() is None:
            logger.debug("Opening the on screen keyboard")
            click_key(LOGIN['keyboard'])
        logger.debug("Trying to enter the keyboard pass")
        for value in credentials[1]:
            time.sleep(0.70)
            if not click_keyboard(str(value), verify=False):
                logger.warning(f"Unable to click {value}")
                return False
        click_keyboard('Ok', verify=False)
    else:
        logger.debug("Trying to type the password")
        for value in credentials[1]:
            if not click_login_keypad(str(value), verify=False):
                time.sleep(0.70)
                logger.warning(f"Unable to click {value}")
                return False
        click_login_keypad('Enter', verify=False)

    return True

def _expired_pwd(credentials, reason=None):
    """
    Helper function for sign_on. Changes expired password when prompted.
    Args:
        credentials: (tuple) The users sign on credentials (username, password)
        reason: (str) Clock in reason code
    Returns:
        True if success, False if failure
    Examples:
        >>> _expired_pwd(('91', '91'))
        True
    """
    try:
        if not click_prompt_key('Ok', verify=False):
            logger.warning(f"Unable to click OK for expired password prompt")
            return False
        if not _enter_new_password(credentials[1]):
            logger.warning(f"Unable to enter new password: {credentials[1]}")
            return False
        return click_keyboard_key('ok', verify=False)
    except:
        logger.warning("Unable to change expired password.")
        return False

def _change_pwd(credentials, reason=None):
    """
    Helper function for sign_on. Changes password when prompted.
    Args:
        credentials: (tuple) The users sign on credentials (username, password)
        reason: (str) Clock in reason code
    Returns:
        True if success, False if failure
    Examples:
        >>> _change_pwd(('91', '91'))
        True
    """
    try:
        if not click_message_box_key('ok', verify=False):
            logger.error(f"Unable to click OK for change password prompt")
            return False
        if not _enter_new_password(credentials[1]):
            logger.error(f"Unable to enter new password: {credentials[1]}")
            return False
        return click_message_box_key('ok', verify=False)
    except:
        logger.error("Unable to change password.")
        return False

def _operator_not_found(credentials=None, reason=None):
    """
    Helper function for sign_on. Clicks OK when Operator not Found prompt is displayed.
    Args:
        credentials: (tuple) The users sign on credentials (username, password)
        reason: (str) Clock in reason code
    Returns:
        True if success, False if failure
    Examples:
        >>> _operator_not_found()
        True
    """
    try:
        return click_message_box_key('ok', verify=False)
    except:
        logger.error("Unable to click Ok on 'Operator not found'")
        return False

def _enter_reason(credentials, reason):
    """
    Helper function for sign_on. Enters Clock In reason when logging in.
    Args:
        credentials: (tuple) The users sign on credentials (username, password)
        reason: (str) Clock in reason code
    Returns:
        True if success, False if failure
    Examples:
        >>> _enter_reason(('91', '91', "some reason"))
        True
    """
    try:
        return click_message_box_key(reason, verify=False)
    except:
        logger.error("Unable to click on Clock in reason.")
        return False

def _is_signed_on(timeout=prompt_timeout):
    """
    Helper function. Checks to see if the user is signed into Edge POS or not.
    Args:
        timeout (int): How long to wait for the window and key to be available.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> _is_signed_on()
        True
        >>> _is_signed_on()
        False
    """
    start_time = time.time()
    while time.time() - start_time <= timeout:
        if not _is_element_present(LOGIN['display'], timeout=0) and not _is_element_present(controls['splash'], timeout=0):
            return True
    return False

def _handle_qualifier(qualifier):
    """
    Helper function for add_item. Select desired item's qualifier.
    Args:
        qualifier: (str) The name of the qualifier you want to select. Price need not be included.
                         If None, selects the unqualified item.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> _handle_qualifier("6-Pack")
        True
        >>> _handle_qualifier("7-Pack")
        False       
    """
    if qualifier is None:
        logger.info("No qualifier specified. Selecting the unqualified item.")
        return click_key(PROMPT["key 1"])

    qualifiers = _get_texts(PROMPT['keys'])
    qualifiers_noprice = [q[:q.rfind(' ($')] for q in qualifiers] # Remove prices from button texts
    for i in range(len(qualifiers_noprice)):
        if qualifiers_noprice[i].lower() == qualifier.lower():
            return click_message_box_key(qualifiers[i], verify=False)
    else:
        logger.warning(f"Unable to find the qualifier {qualifier}.")
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
    # logger.debug("Entered _get_text() method")
    button = _find_element(locator, type = type, timeout = timeout)
    if button:
        try:
            return button.text
        except StaleElementReferenceException: # Element changed after we found it. Try again
            return _get_text(locator, timeout, type)
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
    # logger.debug("Entered _get_texts() method")
    elts = _find_elements(locator, type = type, timeout = timeout)
    if elts:
        return [elt.text for elt in elts]
    return None

def _find_element(locator, timeout=1, type = By.XPATH):
    """
    Helper function. Searches the DOM to find the element you are looking for.
    If multiple elements will match, use _find_elements instead.
    Args:
        locator (str): Element's locator (CSS or XPATH)
        timeout (int): How long to wait for the window and element to be available.
        type: the locator type (By.CSS_SELECTOR or By.XPATH)
    Returns:
        (WebElement) The element matching the locator.
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
    # logger.debug("Looking for elements with locator [%s]"%(locator))
    try:
        return WebDriverWait(driver, timeout).until(EC.visibility_of_any_elements_located((type, locator)))
    except TimeoutException:
        logger.warning(f"No elements with locator {locator} were visible within {timeout} seconds.")
        return None
    except StaleElementReferenceException: # Sometimes raised if the DOM is modified while we check visibility. Just try again
        return _find_elements(locator, timeout, type)

def _enter_new_password(password):
    """
    Helper function. Enters new password at the Edge POS.
    Args:
        password (str): The password you want to enter.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> _enter_new_password('91')
        True
        >>> _enter_new_password('91')
        False
    """
    logger.debug("Entered _enter_new_password() method")
    try:
        enter_keyboard_value(password)
        click_keyboard('ok', verify=False)
        enter_keyboard_value(password)
        click_keyboard('ok', verify=False)
        click_message_box_key('ok', verify=False)
        return True
    except:
        logger.error("Unable to enter new password")
        return False

def _strip_currency(amount):
    """
    Helper function. Strips dollar sign and decimal from a currency string.
    Args:
        amount (str): The currency amount you wish to strip.
    Returns:
        str of amount stripped of currency signs or None if the amount is None
    Examples:
        >>> _strip_currency('$10.00')
        '1000'
        >>> _strip_currency('10.00')
        '1000'
        >>> _strip_currency('1000')
        '1000'
    """
    if amount == None:
        return amount
    amount = str(amount)
    return amount.replace("$", "").replace(",", "").replace(".", "")

def _process_payment(card_name, payload, timeout=5):
    logger.debug("Entered _process_payment() method")
    # Wait for the payment process to finish
    logger.debug("Initiating timeout loop. Waiting for payment process to finish. Looking for Pinpad panel in POS to go away")
    start_time = time.time()
    temp_level = logger.getEffectiveLevel()
    logger.setLevel(999)
    while time.time() - start_time <= timeout:
        # Check if the pinpad screen is still present. When it's gone, the transaction is completed
        if not _is_element_present(PAYMENT_PROC['panel'], timeout = 0.35):            
            logger.setLevel(temp_level)
            break
    else:
        # Timed out
        logger.setLevel(temp_level)
        logger.error("Transaction is taking too long and we didn't go back to idle screen. - _process_payment")
        system.takescreenshot()
        return False
    logger.info("Transaction finished.")

    # Check for messages
    logger.debug("Checking for popup after the transaction is finished")
    prompt_msg = read_message_box(timeout = 1.5)
    if prompt_msg:
        if "pinpad offline" in prompt_msg.lower():
            logger.error(f"Unable to pay with {card_name}. Pinpad is offline")
            # TODO Do we want to really dismiss it??
            logger.debug('Trying to hit [Ok] to dismiss the message')
            click_message_box_key('Ok', verify=False)
            return False
        else:
            logger.error(f"Unable to pay with {card_name}. Received unexpected message: '{prompt_msg}'")
            # TODO Do we want to really dismiss it??
            logger.debug('Trying to hit [Ok] to dismiss the message')
            click_message_box_key('Ok', verify=False)
            return False

    return True

def _process_gift_card(card_name, payload, timeout=pinpad_timeout):
    success = False
    
    if payload['success']:
        success = True
    else:
        logger.warning(f"PINPad payload: {payload}")
        return False
    
    # TODO: For Activation and Recharge, this is not waiting for prompt_msg to show up, it returns True too quickly.
    declined = None
    pinpad_offline = None
    prompt_msg = read_message_box(timeout=pinpad_timeout)

    if prompt_msg != None:
        declined = "DECLINED" in prompt_msg.upper()
        pinpad_offline = "OFFLINE" in prompt_msg.upper()

    if success:
        if declined or pinpad_offline:
            logger.warning(f"{prompt_msg}")
            return False
        else:
            return True
    else:
        return False

"""
Deprecated functions
"""
@test_func
def insert_card(brand='Core', card_name='EMVVisaCredit', debit_fee=False, cashback_amount=None, zip_code=None, cvn=None, custom=None, split_tender=False):
    """
    DEPRECATED - USE PAY_CARD INSTEAD

    Pay out tranaction with inserting EMV card.
    Args:
        brand   : (str) String representation of the Brand (found in CardData.json)
        card_name : (str) The key/name of the card you wish to use located in the CardData.json file.
        debit_fee : (bool) If Debit Fee is prompted and set to True, we click OK; otherwise, we click No.
        cashback_amount: (str) The cashback amount you wish to enter
        zip_code : (str) The ZIP code value you wish to enter
        custom : (str) The Custom prompt value you wish to enter
        split_tender: (bool) Set True if you are expecting the host to trigger split payment (i.e. gift card with insufficient balance)
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
    return pay_card(
        brand = brand,
        card_name = card_name,
        debit_fee=debit_fee,
        cashback_amount=cashback_amount,
        zip_code=zip_code,
        cvn=cvn,
        custom=custom,
        split_tender=split_tender
    )   

"""
Features not supported in Edge.
"""
def read_local_subaccount_list(sub_account_id=None, timeout=default_timeout):
    """
    FEATURE NOT SUPPORTED.
    Local Accounts is not supported on Edge.
    """
    raise FeatureNotSupported("Local Accounts not supported in Edge")

def read_local_account_details(timeout=default_timeout):
    """
    FEATURE NOT SUPPORTED.
    Local Accounts is not supported on Edge.
    """
    raise FeatureNotSupported("Local Accounts not supported in Edge")

def select_local_account(account, sub_account=None, timeout=default_timeout):
    """
    FEATURE NOT SUPPORTED.
    Local Accounts is not supported on Edge.
    """
    raise FeatureNotSupported("Local Accounts not supported in Edge")

def click_local_account_key(key, timeout=default_timeout):
    """
    FEATURE NOT SUPPORTED.
    Local Accounts is not supported on Edge.
    """
    raise FeatureNotSupported("Local Accounts not supported in Edge")

def click_local_account_details_key(key, timeout=default_timeout):
    """
    FEATURE NOT SUPPORTED.
    Local Accounts is not supported on Edge.
    """
    raise FeatureNotSupported("Local Accounts not supported in Edge")

def read_status_line(timeout=default_timeout):
    """
    FEATURE NOT SUPPORTED.
    Status Line is not a feature on Edge.
    """
    raise FeatureNotSupported("Status Line not supported in Edge")

def read_date(timeout=default_timeout):
    """
    FEATURE NOT SUPPORTED.
    Date icon is not a feature on Edge.
    """
    raise FeatureNotSupported("Date icon is not in Edge")

def read_time(timeout=default_timeout):
    """
    FEATURE NOT SUPPORTED.
    Time icon is not a feature on Edge.
    """
    raise FeatureNotSupported("Time icon is not in Edge")

def read_hardware_status(timeout=default_timeout):
    """
    FEATURE NOT SUPPORTED.
    Hardware status is not a feature on Edge.
    """
    raise FeatureNotSupported("Hardware Status is not in Edge")

def read_reminder_box(timeout=default_timeout):
    """
    FEATURE NOT SUPPORTED.
    Reminders are not a feature on Edge.
    """
    raise FeatureNotSupported("Reminders are not supported on Edge systems")

def click_tools_key(key, timeout=default_timeout):
    """
    FEATURE NOT SUPPORTED.
    Tools key is not a feature on Edge.
    """
    raise FeatureNotSupported("Tools key is not in Edge")

def click_dispenser_key(key, timeout=default_timeout):
    """
    FEATURE NOT SUPPORTED.
    Dispenser menu is not a feature on Edge.
    """
    raise FeatureNotSupported("No dispenser menu in Edge")

def click_attendant_key(key, timeout=default_timeout):
    """
    FEATURE NOT SUPPORTED.
    Attendant is not supported on Edge.
    """
    raise FeatureNotSupported("Attendant not supported in Edge")
