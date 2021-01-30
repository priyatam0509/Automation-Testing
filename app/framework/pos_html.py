"""
Name: pos_html
Description: A module for interacting with the HTML CWS.

Date created: 12/16/2019
Modified By:
Date Modified:
"""

import time
import json
import logging, re
import requests
import functools
import winreg
from html.parser import HTMLParser

# Selenium modules
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, SessionNotCreatedException, ElementClickInterceptedException, StaleElementReferenceException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait

# In house modules
from app.simulators.ip_scanner import IPScanner
from app.simulators import printersim
from app import pinpad
from app import mws
from app.util import constants, system
from app.framework.tc_helpers import test_func, tc_fail

BRAND   = system.get_brand()
VERSION = system.get_version()

# Log object
logger = logging.getLogger(__name__)

# Retry and Timeouts
driver_timeout  = 2
default_timeout = 10
prompt_timeout  = 2
key_timeout     = 2
till_timeout    = 7
pinpad_timeout  = 10

# JSON file paths
json_user_credentials   = constants.USER_CREDENTIALS # Change this when we finalize where to store temporary data files
pos_controls_path      = r"D:\automation\app\data\pos_controls.json" # TODO: replace this with a constant

try:
    with open(pos_controls_path) as f:
        controls = json.load(f)
except Exception as e:
    logger.warning(e)

# Exceptions
class FeatureNotSupported(Exception):
    def __init__(self, message):
        self.message = message

class FailedToInitialize(Exception):
    def __init__(self, message):
        self.message = message

# Selenium objects
driver  = None

# Scanner object
scanner = IPScanner()

# Printer object
# If we cannot setup printer sim then there will be cascading failures, we probably just want to exit out.
if not printersim.setup(): # TODO: Determine performance impact of checking if sim is setup on every import
    raise FailedToInitialize("Failed to setup printer simulator")

printer = printersim.PrinterSim()

# Silence logging from HTTP requests
selenium_logger = logging.getLogger('selenium.webdriver.remote.remote_connection')
selenium_logger.propagate = False
urllib_logger = logging.getLogger('urllib3.connectionpool')
urllib_logger.propagate = False

"""
HTML CWS locators and button names.
"""
MENU_BAR = controls['header']
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
LOC_ACCTS = controls['local accounts']

page_title = "Passport"

@test_func
def connect(timeout=120, recover=False, url = 'https://127.0.0.1:7500/', printer_timeout=60):
    """
    Initializes Chrome driver instance and navigates to HTML POS.
    Args:
        timeout: (int) How many seconds to wait for the POS GUI to connect and load.
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
    global driver, wait, printer    
    already_connected = False

    if driver is not None:
        try: # We have a driver, make sure it's connected to Chrome
            driver.title
            already_connected = True
        except:
            logger.info("We have a driver but no connection to Chrome. Re-creating the driver.")
            driver = None # Chrome was probably closed by something else, need to re-create the driver

    if not already_connected:
        options = webdriver.ChromeOptions()
        try:
            options.add_argument("start-maximized")
            options.add_argument("ignore-certificate-errors")
            options.add_experimental_option('w3c', False)
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

        # Verify CWS page loads
        if page_title not in driver.title:
            logger.warning("Opened a web page, but it wasn't the POS. Check Passport status and URL.")
            return False

        driver.maximize_window()

        # Wait for the GUI to finalize
        if not _is_element_present(controls['header']['datetime'], timeout=timeout - (time.time()-start_time)):
            logger.warning("Opened the POS web page, but the GUI didn't load.")
            return False

        # Wait for the printer sim to start talking
        if printer:
            start_time = time.time()
            while time.time() - start_time <= printer_timeout:
                if printer.connected:
                    break
            else:
                logger.warning(f"Printer sim did not start communicating with the POS within {printer_timeout} seconds. Automation may encounter errors.")
                return False
        else:
            logger.warning("Printer sim was not created. Automation may encounter errors.")
            return False

        return True
    else:
        logger.debug(f"Already connected to a chrome driver instance")
        return True

def close():
    """
    Closes chrome driver instance and sets it to None.
    Args:
        None
    Returns:
        None
    """
    global driver
    try:
        driver.close()
    except AttributeError:
        logger.warning("[close] No Chrome driver exists to close.")
    except WebDriverException:
        logger.warning("[close] Chrome seems to have already been closed by an external source.")
    except Exception as e:
        logger.warning(f"[close] Got an unknown exception while closing chrome driver. {type(e).__name__}: {e}")
    finally:
        driver = None # Guarantee that the next connect() will start a new driver

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

#################################
## Decorators and Workarounds  ##
#################################
def pinpad_retry(func):
    """
    Decorator for test methods
    Defines an optional verify parameter that, if set to True, will cause tc_fail to be invoked if the decorated function returns False or None
    The parameter defaults to True
    TODO: Add parameter to allow temporary changes in logging level
    TODO: Add parameter for timeouts?
    """

    @functools.wraps(func)  # Preserve func attributes like __name__ and __doc__
    def pinpad_retry_wrapper(*args, **kwargs):

        try:
            retry = kwargs['retry']
            del kwargs['retry']
        except KeyError:
            retry = True

        try:
            verify = kwargs['verify']
            del kwargs['verify']
        except KeyError:
            verify = True

        if retry:
            # Tracks if the pinpad has been reset yet to loop back through 3 swipe attempts
            reset_count = 0
            while (reset_count < 2):
                # counts the number of failed pay attempts for the pinpad reset
                fail_counter = 0
                while fail_counter < 3:
                    ret = func(*args, **kwargs)
                    if ret:
                        return True
                    else:
                        # tracks if none of the message box prompts or function key were used
                        # if none are used, we assume it is edge case prompt that takes longer to show (No response from host)
                        failure_flag = False
                        fail_counter += 1
                        logger.debug(f"Trying pay_card for {fail_counter} attempt")
                        # Handles message box fails
                        if click_message_box_key("Ok", verify=False):
                            failure_flag = True
                        # Handles hanging prompt fails
                        if click_keypad("Cancel", verify=False):
                            failure_flag = True
                        # Clears message of canceled payment if hanging prompt fail
                        if click_message_box_key("Ok", verify=False):
                            failure_flag = True
                        # If none of the prompts or function key were clicked, assume edge case prompt (no response from host)
                        if not failure_flag:
                            time.sleep(20)  # sleep for 20 seconds for prompt to be visible
                            click_message_box_key("Ok", verify=False)
                logger.debug("Resetting pinpad after 3 transaction failures")
                requests.get(url='http://10.80.31.212/api/tools/start')
                time.sleep(120)  # Sleep for 2 mins for pinpad to redownload
                reset_count += 1
            # Failed 3 attempts before and after a pinpad reset
            if verify and (ret is None or not ret):
                tc_fail(f"{func.__module__}.{func.__name__} failed.")
            void_transaction()  # If all attempts failed, must void to have next test receipt be correct
            return ret
        else:
            ret = func(*args, **kwargs)

        if verify and (ret is None or not ret):
            tc_fail(f"{func.__module__}.{func.__name__} failed.")
        void_transaction()  # If all attempts failed, must void to have next test receipt be correct
        return ret

    return pinpad_retry_wrapper

##########################
## High-level functions ##
##########################

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
    logger.debug(f"Trying to press keypad buttons: {values}")
    for value in str(values):
        if not click_keypad(str(value), timeout=timeout, verify=False):
            return False
    if after:
        ret = click_keypad(after, verify=False)
        time.sleep(.1) # We probably hit Enter/Cancel. Wait for POSState to process
        return ret

    return True

@test_func
def enter_keyboard(values, timeout=default_timeout, after=None):
    """
    Enter a string on the keyboard. Mostly for entering passwords.
    Args:
        values: (str) The value you want to enter into keyboard.
        timeout: (int) How long to wait for the keyboard to be accessible.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
        after: (str) A key to press after entering characters, such as Ok or Cancel.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> enter_keyboard("91")
        True
        >>> enter_keyboard("password123", after="Ok")
        True
        >>> enter_keyboard("[]{}<>,")
        False
    """
    logger.debug("Entered enter_keyboard() method")
    time.sleep(.2) # Give UIBlocker a bit to get out the way - increases consistancy - possibly improve?
    for value in str(values):
        if not click_keyboard(value, timeout=timeout, verify=False):
            return False
    if after:
        ret = click_keyboard(after, verify=False)
        time.sleep(.1) # We probably hit Ok/Cancel. Wait for POSState to process
        return ret

    return True

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
    logger.debug(f"Entering PLU: {plu}")
    return enter_keypad(plu, after="Enter", timeout = timeout, verify=False)

@test_func
def add_item(item="Generic Item", method="SPEED KEY", quantity=1, price=None, dob=None, qualifier=None, timeout = 10, cash_card_action=None):
    """
    Adds an item to the HTML POS transaction journal via SpeedKey, PLU, or Dept.
    Args:
        item: (str) The item you want to add (text associated with the method). For PLU, use PLU num.
        method: (str) The way you are going to add an item (Speed Key, Dept, PLU)
        quantity: (str) The amount of items you want to add
        price: (str) The item's cost
        dob: (str) The DOB you wish to enter for the item. MM/DD/YYYY
        qualifier: (str) The qualifier's text
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
    logger.debug("Entered add_item() method")
    price = _strip_currency(price) if price else price

    # TODO: Something to hit Back if we're in forecourt menu?
    logger.debug(f"Adding {item}")
    if method.upper() == "DEPT KEY":
        if price is None:
            logger.warning(f"price must be specified with {method} method.")
            return False
        if not click_dept_key(item, verify=False):
            logger.warning("Unable to add [%s] via dept key" %(item))
            return False

    elif method.upper() == "SPEED KEY":
        if not click_speed_key(item, verify=False):
            logger.warning("Unable to add [%s] via speed key" %(item))
            return False

    elif method.upper() == "PLU":
        if not enter_plu(plu=item, verify=False):
            logger.warning("Unable to add [%s] via PLU" %(item))
            return False

    else:
        logger.warning("Received: %s for method. Method needs to be <PLU|DEPT KEY|SPEED KEY>." %(method))
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
        logger.debug("Checking for popups")
        pop_up_prompt      = is_element_present(PROMPT['body'], timeout=0.5, type = By.XPATH)
        status_line_prompt = is_element_present(MENU_BAR['message'], timeout=0.5, type = By.XPATH)
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

            elif cash_card_text == pop_up_prompt_msg:
                logger.debug("Handling cash card prompt")
                if cash_card_action.lower() == "activate" or cash_card_action.lower() == "activation":
                    click_message_box_key("Yes", verify=False)
                elif cash_card_action.lower() == "recharge":
                    click_message_box_key("No", verify=False)
                else:
                    logger.error(f"{cash_card_action} is invalid for cash_card_action. Please specify Recharge or Activation.")
            else:
                logger.error("Encountered unexpected popup message. Header: %s. Body: %s" % (get_text(PROMPT['header']), pop_up_prompt_msg))
                return False

        if status_line_prompt:
            msg_success = False
            # Prompt Handling
            birthday_text   = ["Enter birthday or scan Id"]
            price_text      = ["Enter price for", "requires a price"]
            quantity_text   = ["Enter quantity for"]
            plu_text        = ["Enter PLU"]
            qualifier_text  = ["Select a qualifier and press enter"]

            logger.debug("Reading keypad propmpt")
            text_on_prompt  = read_keypad_prompt(2)

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

            if any([ x in text_on_prompt for x in qualifier_text]):
                logger.debug("Found qualifier prompt")
                if qualifier is None:
                    logger.warning(f"{item} has a required qualifer. Please specify a qualifer.")
                    click_keypad("Cancel")
                    if method.upper == "DEPT":
                        click_message_box_key("Ok") # Clear unable to sell item popup
                    return False
                select_list_item(qualifier, partial=True)
                click_keypad("Enter")

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

            elif any([ x in text_on_prompt for x in plu_text]):
                msg_success = True # This is a done condition

            else:
                logger.warning(f"[add_item] Unknown status line prompt: {text_on_prompt}. Trying to finish item add process...")
                msg_success = True

    if price is not None and not price_req: # Override price
        click_function_key("Override", verify=False)
        enter_keypad(price, after="Enter", verify=False)

    if quantity != 1 and not quantity_req: # Override quantity
        click_function_key('Change Item Qty', verify=False)
        enter_keypad(quantity, after='Enter', verify=False)

    return True

def void_item(item=None, instance=1, timeout=default_timeout):
    """
    Void an item in the current transaction.
    Args:
        item: (str) Text identifying the item or transaction to select.
                This can be the name, price, etc.
        instance: (int) Which instance of the item to select if there are multiple matches.
        timeout: (int) How many seconds to try for before failing.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Return: (bool) True on success, False on failure.
    Examples:
        >>> void_item("Generic Item")
        True
        >>> void_item("$12.34", 3)
        True
        >>> void_item() # Voids the first item
        True
    """
    start_time = time.time()
    if not click_journal_item(item, instance, timeout, verify=False):
        return False
    # Create expected journal contents after void
    journal = read_transaction_journal()
    item_index = _locate_journal_item(item, instance)
    journal.pop(item_index)

    timeout -= (time.time() - start_time)
    if not click_function_key("Void Item", timeout, verify=False):
        return False

    # Try to verify success
    if not system.wait_for(read_transaction_journal, journal, timeout=10):
        logger.warning("[void_item] The item was not removed from the journal after voiding.")
        return False

    return True

def void_transaction(reason=None, timeout=default_timeout):
    """
    Void the current transaction.
    Args:
        reason: (str) The reason code to select, if any. The first code will be selected by default.
        timeout: (int) How many seconds to wait for the Void Transaction button to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    """
    if not click_function_key("Void Transaction", timeout, verify=False):
        return False
    if reason == None:
        msg = read_message_box(timeout=2)
        if msg and "Are you sure" in msg and not click_message_box_key("Yes", verify=False):
            return False
    if is_element_present(controls['selection list']['list'], timeout=2):
        if reason and not select_list_item(reason, timeout=1):
            return False
        if not click_keypad('Enter', timeout=2):
            return False
    elif reason:
        logger.warning("[void_transaction] Reason arg was specified but no reason code prompt appeared.")
        click_message_box_key("No", verify=False, timeout=1) # Clear confirmation prompt
        return False

    # Verify transaction voided
    if not system.wait_for(read_journal_watermark, "TRANSACTION VOIDED", timeout=5):
        logger.warning("[void_transaction] Reached the end of the process, but the journal did not reflect a voided transaction.")
        return False

    return True

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
        card_name : (str) The key/name of the card you wish to use located in the CardData.json file
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
    if not(_check_trans_state()):
        logger.warning(f"Transaction is in progress, unable to proceed")
        return False
    click_status = click_function_key("Network")
    if not (click_status):
        logger.error(f"Function Key 'Network' unable to perform @ de_activate_gift_card")
        return False

    # Need to check the Network status before proceeding the steps
    nw_status = get_text(NETWORK['status'])
    logger.warning(f"Network Status : [{nw_status}]")
    if not(nw_status == 'Network Online'):
        logger.error(f"Network is Offline, unable to perform @ de_activate_gift_card")
        click_function_key("Back")
        return False
    time.sleep(1)
    click_status = click_function_key("De-Activate Card")
    if not (click_status):
        logger.error(f"Function Key 'De-Activate Card' unable to perform @ de_activate_gift_card")
        return False
    time.sleep(1)
    click_keypad("1")
    click_keypad("00")
    time.sleep(1)
    click_keypad("Enter")
    time.sleep(3)
    try:
        payload = pinpad.swipe_card(
            brand=brand,
            card_name=card_name)
        logger.warning(f"payload value : [{payload}]")
        if (payload['success']):
            _check_message("OK")
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
        click_message_box_key(action)
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
        fuel_type: (str) This is just used in Commercial Diesel Transactions and it is provided, also def_type should provided. One of the three possible fuel types presented in the prompt
        def_type: (str) This is just used in Commercial Diesel Transactions and it is provided, also fuel_type should provided.This is a prompt that just allows Yes or No
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
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

    level += " PRICING"

    if mode.upper() == "MANUAL" or mode.upper() == "MANUAL SALE":
        click_forecourt_key("MANUAL SALE", timeout=5, verify=False)
        select_list_item(grade, timeout=5, verify=False)
        if read_message_box(timeout=3):
            select_list_item(level, verify=False)
    else:
        click_forecourt_key(mode, timeout=5, verify=False)

    stripped_amount = amount.replace("$", "").replace(".", "")

    #Checking if the commercial values were provided, if not assume that this isn't a commercial transaction
    if not fuel_type is None  and not def_type is None:
        msg = read_message_box(timeout=10)
        if msg == "Select fuel products to dispense":
            if click_message_box_key(fuel_type, verify=False, timeout=5):
                logger.info("[%s] was selected." %(fuel_type))
            
            else:
            
                logger.error(f"Failed attempting to select {fuel_type}")
            time.sleep(1) #giving time to remove the prompts
            msg = read_message_box(timeout=1)

        msg = read_message_box(timeout=10)
        start_time = time.time()    
        while msg == "DEF?" and time.time() - start_time < 10:
            
            if click_message_box_key(def_type, verify=False, timeout=5):
            
                logger.info("[%s] was selected for DEF prompt." %(def_type))
            
            else:
            
                logger.error(f"Failed attempting to select {fuel_type}")
            
            time.sleep(1) #giving time to remove the prompts
            msg = read_message_box(timeout=1)
    
    elif not fuel_type is None or not def_type is None:

        self.log.error("If either fuel_type or def_type is provided, the other one must be provided also")
        return False

    msg = read_message_box()
    if msg:
        logger.warning(f"Couldn't add fuel. Message: {msg}") # Probably already has a prepay
        click_message_box_key("Ok", verify=False)
        return False
    enter_keypad(stripped_amount, timeout=5, verify=False)
    click_keypad('ENTER', verify=False)
    msg = read_message_box()
    if msg:
        logger.warning(f"Couldn't add fuel: Message: {msg}")
        click_message_box_key("Ok", verify=False)
        return False
    return True

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
def wait_for_disp_status(status, dispenser = 1, timeout=60):
    """
    Wait for a dispenser to have a given status. Use None or empty string for blank status.
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

    select_dispenser(dispenser)
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
def pay(amount=None, tender_type="cash", cash_card="GiftCard", prompts = None, timeout_transaction=False):
    """
    Pay out transaction using a non-card tender type.
    Args:
        amount: (str) How much to pay, if the tender type supports it. Default is exact change.
        tender_type: (str) Type of tender to select. Set to None if paying out a zero-balance transaction.
        cash_card: (str) If activating a cash card, the name of the card in CardData.json.
        prompts: (dict) A dictionary to handle all the commercial prompts
        timeout_transaction: (bool) Used for waiting for the time out message shown after a host does not answer for a period of time (between 30 and 45 second is most of the networks)
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
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
    if tender_type and tender_type.lower() == "card":
        logger.warning(f"Use pay_card function for card tenders")
        return False

    logger.debug("Trying to click Pay")
    if not click_function_key('Pay', verify=False):
        logger.error(f"Unable to click Pay")
        return False

    logger.debug("Checking for popups")
    if is_element_present(PROMPT['body']):
        click_message_box_key(key='No', verify=False)

    if tender_type == None: # Zero-balance transaction
        if not system.wait_for(lambda: "transaction complete" in read_journal_watermark().lower(), verify=False):
            logger.error("No-tender (zero balance) transaction did not complete after clicking Pay.")
            return False
        return True

    amount = _strip_currency(amount)

    # Find requested key
    if amount == None:

        #Paper check tender from commercial, do not need to enter an amount but it has a check number prompt
        if not prompts is None:

            logger.debug(f"Trying to click {tender_type}")
            if not click_tender_key(tender_type, verify=False):
                logger.error(f"Unable to click tender {tender_type}")
                return False 

            logger.debug(f"Handeling commercial prompts, these are the provided prompts: {prompts}")
            
            if not commercial_prompts_handler(prompts, timeout_transaction=timeout_transaction, verify=False):
                
                logger.error("The displayed prompt was not provided")
                return False
        else:                
            logger.debug("Trying to click on exact change button")
            if not click_tender_key("exact change", verify=False):
                logger.error(f"Unable to click exact change key")
                return False
    else:
        logger.debug(f"Trying to click {tender_type}")
        if not click_tender_key(tender_type, verify=False):
            logger.error(f"Unable to click tender {tender_type}")
            return False       

        logger.debug("Trying to enter the amount")
        if not enter_keypad(amount, after="Enter"):
            return False

    # Handle cash card swipe if needed
    status = read_status_line().lower()
    if "activation" in status or "recharge" in status:
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
    logging.disable()
    while time.time() - start_time <= 20:
        # Check if the processing screen is still present. When it's gone, the transaction is completed
        if not is_element_present(PAYMENT_PROC['panel'], timeout = 0.35):
            logging.disable(logging.NOTSET)
            break
    else:
        logging.disable(logging.NOTSET)
        # Timed out
        logger.error("Transaction is taking too long and we didn't go back to idle screen.")
        return False
    logger.info("Transaction finished.")

    return True

def verify_idle(timeout=10):
    """
    NYI
    """
    logger.error("verify_idle is not implemented")

@pinpad_retry
def pay_card(brand='Core', card_name='Visa', debit_fee=False, cashback_amount=None, zip_code=None, cvn=None, custom=None, split_tender=False, cash_card="GiftCard", invoice_number=None, force_swipe=False, prompts = None, timeout_transaction=False, decline_transaction = False):
    """
    Pay out tranaction using a card.
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
        invoice_number: (str) Invoice number to be entered for refund
        force_swipe : (bool) Force an EMV card to be swiped instead of inserted.
        prompts: (dict) A dictionary to handle all the commercial prompts
        timeout_transaction: (bool) Used for waiting for the time out message shown after a host does not answer for a period of time (between 30 and 45 second is most of the networks)
        decline_transaction: (bool) Used to decide whether or not will validate decline message in host decline scenario.
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
    logger.debug("Entered pay_card() method")

    if not click_function_key('Pay', verify=False):
        return False  

    logger.debug("Looking for Loyalty popup message")
    if is_element_present(PROMPT['body']):
        click_message_box_key(key='No', verify=False)

    if not click_tender_key("Card", verify=False):
        return False

    # Verify that pinpad payment is initiated
    logger.debug("Verifying the card type transaction is initiated. Looking for pinpad panel in POS")
    if not ( is_element_present(PAYMENT_PROC['panel'], timeout = pinpad_timeout) or \
            get_text(PAYMENT_PROC['text']) != "Insert/Swipe/Tap Card"):
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
        click_keypad("Cancel", verify=False)
        return False

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

    # Handle cash card swipe if needed
    status = read_processing_text()
    if status is not None:
        if "activation" in status.lower() or "recharge" in status.lower():
            try: 
                pinpad.swipe_card(brand=system.get_brand(), card_name=cash_card)
            except Exception as e:
                logger.warning(f"Cash card swipe in pay failed. Exception: {e}")
                click_keypad("CANCEL", verify=False)
                click_message_box_key("YES", verify=False)
                return False

    # Handle refund
    if invoice_number:
        status = read_processing_text().lower()
        if "enter invoice number" in status:
            logger.info(f"{status}")
            enter_keypad(invoice_number)
            click_keypad("ENTER")

    return _process_payment(card_name, payload, decline_transaction)

@pinpad_retry
def manual_entry(brand='Core', card_name='Visa', expiration_date=None, zip_code=None, custom=None, split_tender=False, invoice_number=None):
    """
    Pay out tranaction using Manual card entry.
    Args:
        brand   : (str) String representation of the Brand (found in CardData.json)
        card_name : (str) The key/name of the card you wish to use located in the CardData.json file.
        expiration_date : (str) The string representation of expiration date for card that'll be entered on POS.
        zip_code : (str) The ZIP code value you wish to enter
        custom : (str) The Custom prompt value you wish to enter
        split_tender: (bool) Set True if this payment will not complete the transaction.
        invoice_number: (str) Invoice number to be entered for refund
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

    if is_element_present(PROMPT['body']): # Loyalty
        click_message_box_key(key='No', verify=False)
    
    if not click_keypad("Manual", verify=False):
        logger.warning("Unable to click Manual button")
        return False
    
    payload = pinpad.manual_entry(
            brand=brand,
            card_name=card_name,           
            zip_code=zip_code,
            custom=custom,
        )
    if not payload:
        logger.warning(f"Manual entry failed. Canceling transaction.")
        click_function_key("Cancel", verify=False)
        return False

    if not click_message_box_key(key='Yes', verify=False):
        logger.warning("Unable to click yes for confirming Account Number")
        return False
    
    try:
        click_message_box_key(key="No", verify=False)
    except:
        logger.warning("Unable to click no for auxiliary network card")

    if card_name == "VisaPurchase" or card_name == "MasterCardPurchase":
        msg = read_message_box(timeout=3)
        if msg is not None and msg == f"Is this a {card_name[:len(card_name)-8]} card?":
            if not click_message_box_key(key='No', verify=False):
                return False

        msg = read_message_box(timeout=3)
        if msg is not None and msg == f"Is this a {card_name[:len(card_name)-8]} Purchase card?":
            if not click_message_box_key(key='Yes', verify=False):
                return False

    if expiration_date == None:
        if not enter_keypad("1230", verify=False):
            return False
    else:
        if expiration_date[2] == '/':
            expiration_date = expiration_date.replace('/', '')
        if not enter_keypad(expiration_date, verify=False):
            return False

    if not click_keypad('Enter', verify=False):
        return False

    msg = read_message_box(timeout=pinpad_timeout)
    if msg is not None and "split pay" in msg.lower():
        if not split_tender:
            logger.warning("Got an unexpected split pay prompt when paying out transaction.")
            click_message_box_key("NO", verify=False)
            click_message_box_key("OK", timeout=pinpad_timeout, verify=False)
            return False
        else:
            return click_message_box_key("YES", verify=False)
    elif split_tender:
        logger.warning("Expected split payment prompt but didn't get one.")
        click_function_key("Cancel", verify=False)
        return False

    # Handle cash card swipe if needed
    status = read_processing_text()
    if status is not None:
        if "activation" in status.lower() or "recharge" in status.lower():
            try: 
                pinpad.swipe_card(brand=system.get_brand(), card_name=cash_card)
            except Exception as e:
                logger.warning(f"Cash card swipe in pay failed. Exception: {e}")
                click_keypad("CANCEL", verify=False)
                click_message_box_key("YES", verify=False)
                return False

    # Handle refund
    if invoice_number:
        status = read_processing_text().lower()
        if "enter invoice number" in status:
            logger.info(f"{status}")
            enter_keypad(invoice_number)
            click_keypad("ENTER")

    return _process_payment(card_name, payload)

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
            if is_element_present(FUNC_KEYS['receipt'], timeout=10):
                click_function_key("Back", timeout, verify=False)
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
            click_function_key("Back")
            return ret

    #Removing duplicates
    lines_not_found = list(dict.fromkeys(lines_not_found))
    logger.info(f"The current receipt is: {actual_rcpt}")
    logger.warning(f"Did not find {lines_not_found} in the receipt within {timeout} seconds. ({attempts} attempts)")
    click_function_key("Back")
    return False

@test_func
def sign_off(user_id=None):
    """
    Signs off from the POS.
    Args:
        user_id: (str) The id of the user that is signing off of the POS.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> sign_off()
        True
    """
    if not click_function_key('Sign-off', verify=False):
        return False
    return click_message_box_key('Yes', verify=False)

@test_func
def sign_on(user_credentials=None, till_amount=None, reason=None):
    """
    Sign on to the POS. Handles clock in and till opening if necessary.
    Args:
        user_credentials: (tuple) The username and password to log in with (strings). 
                          Defaults to the last set of credentials used with this function on the system, or 91/91 on first use.
        till_amount: (str) The amount to open the till with. Defaults to 0.
        reason: (str) The reason code to select if one is needed for clock in. Selects the first available code by default.
    Returns: (bool) True if the process completes successfully.
    """

    logger.debug("[sign_on] Signing on...")
    signed_on = _is_signed_on()
    if _is_signed_on():
        if user_credentials or till_amount or reason: # If args are specified, let's assume the user cares about the full process going through
            logger.warning("[sign_on] Already signed on. Unable to sign on with the args provided.")
            return False
        logger.debug("[sign_on] Already signed on. Doing nothing.") # Otherwise we'll assume they just wanted to be signed on (is this okay?)
        return True
    elif signed_on == None:
        logger.warning("[sign_on] Unknown state. Cannot sign on. Please ensure the Sign On button is visible.")
        return False

    json_creds = {}
    if user_credentials is None:
        logger.debug("[sign_on] Checking for saved credentials.")
        try:
            with open(json_user_credentials) as creds_file:
                json_creds = json.load(creds_file) # Check for existing credentials
                user_credentials = [json_creds['ID'], json_creds['Password']]
        except (FileNotFoundError, json.decoder.JSONDecodeError): # Nonexistent or empty credentials file
            user_credentials = ('91', '91')
            logger.info(f"[sign_on] No saved credentials, defaulting to {user_credentials}.")

    logger.debug("[sign_on] Entering username and password.")
    if not click_function_key("Sign On", verify=False):
        if not click_function_key("unlock", verify=False):
            return False
    if not system.wait_for(read_status_line, "Enter User ID", verify=False) or not enter_keypad(user_credentials[0], after='Enter', verify=False):
        return False
    if not system.wait_for(read_keyboard_prompt, "Enter Password", verify=False) or not enter_keyboard(user_credentials[1], after='Ok', verify=False):
        return False

    if _is_signed_on(timeout=1): # We might be done at this point, return quickly if so
        if till_amount:
            logger.warning("[sign_on] Till amount was specified for sign on, but did not get a till opening prompt. Aborting.")
            return False
        if reason:
            logger.warning("[sign_on] Reason was specified for sign on, but did not get a reason code prompt. Aborting.")
            return False
        return True

    logger.debug("[sign_on] Handling clock in prompts.")
    header = None
    msg = read_message_box()
    if msg != None:
        header = read_message_box(text='header')
    if msg and "clock in" in msg.lower():
        if not click_message_box_key('Yes', verify=False):
            return False
    elif header and "select a reason" in header.lower():
        if reason:
            if not click_message_box_key(reason, verify=False):
                return False
        else:
            logger.info("[sign_on] Got a reason code prompt but no reason was specified. Defaulting to the first reason code.")
            if not click_key(PROMPT["key 1"]):
                return False

    if _is_signed_on(timeout=1): # We might be done at this point, return quickly if so
        if till_amount:
            logger.warning("[sign_on] Till amount was specified for sign on, but did not get a till opening prompt. Aborting.")
            return False
        return True

    logger.debug("[sign_on] Handling till opening.")
    start_time = time.time()
    while time.time() - start_time <= 10:
        msg = read_message_box()
        if "Enter Opening Amount" in read_status_line():
            if till_amount:
                till_amount = _strip_currency(till_amount)
                if not enter_keypad(till_amount, after='Enter', verify=False):
                    return False
            else:
                if not click_keypad('Enter', verify=False):
                    return False
            break
        elif msg != None and "new till?" in msg:
            if till_amount:
                logger.warning("[sign_on] Till amount was specified for sign on, but only got Yes/No prompt (opening amount is probably suppressed in register Group Maintenance). Aborting.")
                return False
            if not click_message_box_key("Yes", verify=False):
                return False
            break
    else:
        if till_amount:
            logger.warning("[sign_on] Till amount was specified for sign on, but did not get a till opening prompt. Aborting.")
            return False
    
    # We should be done by now. Verify success
    if not _is_signed_on():
        msg = read_message_box()
        logger.warning(f"Did not successfully sign on. The POS says: {msg}")
        return False
    else:
        logger.debug("[sign_on] Successfully signed on. Saving credentials.")
        #Creating last user logged in JSON file
        with open(json_user_credentials, 'w+') as creds_file:
            json_creds['ID'] = user_credentials[0]
            json_creds['Password'] = user_credentials[1]
            json.dump(json_creds, creds_file)
        return True

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

    # Map of functions and the keys they may be used to click on.
    map = { "click_function_key": controls['function keys'].keys(),
            "click_message_box_key": [WILD, "ok", "yes", "no", "cancel"] + list(controls['prompt box'].values()),
            "click_speed_key": ['generic item', WILD],
            "click_dept_key": [f"dept {i}" for i in range(1,16)] + [WILD],
            "click_forecourt_key": controls['forecourt'].keys(),
            "click_preset_key": ['$5.00', '$10.00', '$20.00', '$50.00', 'regular', 'plus', 'supreme', WILD],
            "click_tender_key": ['$1.00', '$5.00', '$10.00', '$20.00', '$50.00', 'card', 'check', 'cash', 'imprinter', 'other', WILD],
            "click_keypad": list(set(controls['keypad'].keys()) | set(controls['login'].keys())),
            "click_keyboard": controls['keyboard'].keys(),
            "click_status_line_key": controls['header'].keys()
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
        # Requested key doesn't match any known menus, try menus that can have custom key
        funcs_to_try = build_func_list(WILD) # Menus that can contain buttons with any text
    
    # Invoke the functions repeatedly until success or timeout
    log_level = logger.getEffectiveLevel()
    if log_level > logging.DEBUG:
        logging.disable() # Temporarily disable logging to prevent spam, unless we're at debug level
    start_time = time.time()
    while time.time() - start_time <= timeout:
        for func in funcs_to_try:
            try:
                if func(key, timeout=0, verify=False):    
                    return True
            except:
                raise
            finally:
                logging.disable(logging.NOTSET)
    else:
        logger.warning("Couldn't find %s within %d seconds." % (key, timeout))
        return False

@test_func
def click_function_key(key, timeout=default_timeout):
    """
    Click a key in the POS function key window.
    Args:
        key: (str) The key to click.
        timeout: (int) How long to wait for the element to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> click_function_key("CLOSE TILL")
        True
        >>> click_function_key("GENERIC ITEM")
        False
    """ 
    autoswitch_menus = [key for key, value in FUNC_KEYS.items() if type(value) == dict]

    # We may need to switch menus
    for menu in autoswitch_menus:
        if key.lower() in FUNC_KEYS[menu]:
            start_time = time.time()
            while time.time() - start_time <= timeout:
                menu_key = menu.replace(' keys', '')
                if is_element_present(FUNC_KEYS[menu_key], 0):
                    click_key(FUNC_KEYS[menu_key], 0)
                if click_key(controls['function keys'][menu][key.lower()], 1):
                    return True
            else:
                return False

    return click_key(controls['function keys'][key.lower()], timeout)

@test_func
def click_tender_key(key, timeout=default_timeout):
    """
    Click a key in the POS tender window.
    Args:
        key: (str) The tender key to be clicked.
        timeout: (int) How long to wait for the element to be available.
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
    logger.debug(f"Entered click_tender_key() method: pressing key {key}")
    if key.lower() == "exact change":
         return click_key(controls['pay']['exact_amount'], timeout)
    elif key.startswith('$'):
        return click_key(controls['pay']['preset_amount'] % key.lower(), timeout)
    else:
        return click_key(controls['pay']['type'] % key.lower(), timeout)

@test_func
def click_speed_key(key, timeout=key_timeout, case_sens=False):
    """
    Click on a speed key. Switches to speed keys if needed.            
    Args:
        key: (str) The text of the speed key to click on.
        timeout: (int) How long to wait for the element to be available.
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
    if is_element_present(controls['function keys']['speed keys'], timeout):
        click_function_key("Speed Keys", timeout=1, verify=False)
    return click_key(controls['item keys']['key_by_text'] % key.lower(), timeout=1)

@test_func
def click_dept_key(key, timeout=key_timeout, case_sens=False):
    """
    Click on a department key. Switches to dept keys if needed.
    Args:
        key: (str) The text of the dept key to click on.
        timeout: (int) How long to wait for the element to be available.
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
    click_function_key("Dept Keys", timeout=timeout, verify=False)
    return click_key(controls['item keys']['key_by_text'] % key.lower(), timeout=3)

@test_func
def click_message_box_key(key, timeout=default_timeout):
    """
    Click a key on the popup message on the POS, if there is one.
    Args:
        key: (str) The key to click.
        timeout: (int) How long to wait for the element to be available.
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
    return click_key(controls['prompt box']['key_by_text'] % key.lower(), timeout)

@test_func
def click_keypad(key, timeout=default_timeout):
    """
    Click a key in the numeric keypad, or one of the keys controlling it (Enter/Cancel/etc).
    Also covers the keyboard's keypad.
    Args:
        key: (int/str) The keypad key that will be clicked. Must be for a single key, if the
                key is '00' then it needs to be a string in the first place.
        timeout: (int) How long to wait for the element to be available.
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
    logger.info(f'Click in keypad "{key}"')
    start_time = time.time()
    while time.time() - start_time <= timeout:
        try:
            if click_key(controls['keypad'][key.lower()]):
                return True
        except KeyError:
            pass

        logger.debug(f"Couldn't click {key} in login keypad. Trying keyboard...")
        try:
            if click_key(controls['keyboard'][key.lower()]):
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
        timeout: (int) How long to wait for the element to be available.
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
    return click_key(controls['keyboard'][key.lower()], timeout=timeout)

@test_func
def click_forecourt_key(key, timeout=default_timeout):
    """
    Click a key in the POS forecourt GUI.
    Args:
        key: The text of the key to click.
        timeout: (int) How long to wait for the element to be available.
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
    # Most of these are function keys in HTML POS. Check there first
    if key in controls['function keys']:
        return click_function_key(key, timeout, verify=False)
    return click_key(controls['forecourt'][key], timeout)

@test_func
def click_login_keypad(key, timeout=default_timeout): # TODO Move me to cross-compat functions
    """
    Clicks on the login keypad.
    Args:
        key: (str) The key to be clicked.
        timeout: (int) How long to wait for the element to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> click_login_keypad("1")
        True
        >>> click_login_keypad("durp")
        False
    """
    return click_key(controls['login'][key.lower()], timeout)

@test_func
def click_preset_key(key, timeout=default_timeout):
    """
    Click an amount preset key when presetting a dispenser, or a pricing level/grade/amount key when adding manual fuel. This is for cross-compatibility with WPF POS.
    Note: grade selection is not supported for preset on HTML POS.
    Args:
        key: The text of the key to click.
        timeout: (int) How long to wait for the element to be available.
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
        key.replace("level", "pricing") # Text changes from WPF to HTML POS
   
    if key.startswith('$'):
        return click_key(controls['keypad']['preset_by_text'] % key.lower(), timeout)
    return click_key(controls['prompt']['key_by_text'] % key.lower(), timeout)

@test_func
def click_status_line_key(key, timeout=default_timeout):
    """
    Click a key on the top bar of the POS.
    Args:
        key: (str) The name of the key being clicked
        timeout: (int) How long to wait for the element to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> click_status_line_key("HELP")
        True
        >>> click_status_line_key("PRICE CHECK")
        False
    """
    return click_key(controls['header'][key.lower()], timeout=timeout)

@test_func
def select_local_account(account, sub_account=None, timeout=default_timeout):
    """
    Select a local account from the list, as well as one of its subaccounts if desired.
    Args:
        account: (str) Account ID, name, or VAT number.
        subaccount: (str) Subaccount ID, vehicle ID, or description.
        timeout: (int) How long to wait for the window to be available.       
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: Whether or not the item was successfully selected
    Examples:
        >>> select_local_account('2')
        True
        >>> select_local_account('JOHN DOE', 'JOHN'S SUBACCOUNT 2')
        True
        >>> select_local_account('NotARealAccount')
        False
    """
    if not click_key(LOC_ACCTS['acct_by_text'] % account.lower()):
        logger.warning(f"Unable to select local account {account}.")
        return False
    if sub_account and not click_key(LOC_ACCTS['subacct_by_text'] % sub_account.lower()):
        logger.warning(f"Unable to select subaccount {sub_account} of local account {account}.")
        return False
    return True

####################
## Read functions ##
####################

def read_balance(timeout=default_timeout):
    """
    Get the transaction totals: basket count, total, change, etc.
    Args:
        timeout: (int) How many seconds. to try for before failing.
    Returns:
        dict: A dictionary mapping each text element to its corresponding
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
        contents = get_text(balance_locator)
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

def read_message_box(timeout=default_timeout, text = 'body'):
    """
    Read the text of the popup message on the POS, if there is one.
    Args:
        timeout: (int) The time (in seconds) that the function will look for the window's visibility.
        text: (str) the string indicating the container the text should be read from: body or header
    Returns:
        str: The message in the message box
    Examples:
        >>> read_message_box()
        'Are you sure you want to void the transaction?'
        >>> read_message_box() # While no message box is visible
        None
    """
    valid_containers = ['body', 'header']
    if text not in valid_containers:
        logger.warning("Please specify 'body' or 'header' for the text arg to read_message_box.")
        return None

    return get_text(controls['prompt box'][text], timeout=timeout)

def read_messageboxbuttons_text(timeout=default_timeout):
    """
    Read the texts of the buttons on prompt on the POS, if there is one, and returns a list of strings.
    Args:
        timeout: (int) The time (in seconds) that the function will look for the button's visibility.
    Returns:
        list: The list of texts from the buttons on the prompt.
    Examples:
        >>> read_messageboxbuttons_text()
        '[Yes, No]'
    """
    prompt_title = read_message_box(timeout=timeout)

    buttons = get_texts(controls['prompt box']['button'], timeout=timeout)
    
    logger.debug(f"The text of the buttons shown in the prompt '{prompt_title}', are {buttons}")
    
    return buttons

def read_status_line(timeout=default_timeout):
    """
    Read the status text that appears in the top left of the POS.
    Args:
        timeout: (int) How many seconds to wait for the status line to appear.
    Returns:
        str: The contents of the status line
    Examples:
        >>> read_status_line()
        "Department 'Dept 1' requires a price to be entered."
        >>> read_status_line()
        ""
    """
    text = get_text(controls['header']['message'], timeout=timeout)
    if text is None:
        return ''
    return text

def read_processing_text(timeout=default_timeout):
    try:
        return get_text(PAYMENT_PROC['text'], timeout=timeout)
    except Exception as e:
        logger.warning(f"Unable to read processing text : {e}")
        return ""

def read_reminder_box(timeout=default_timeout):
    """
    NYI
    """
    logger.error("read_reminder_box is not yet implemented")

def read_transaction_journal(element=None, only_selected=False, timeout=default_timeout):
    """
    Get the text of the transaction journal.
    Args:
        element: (int) The index of the element to read, if a specific one is desired (1-indexed).
        only_selected: (bool) Whether or not to return only the selected/highlighted item in the transaction journal.
        timeout: (int) How long to wait for the element to be available.
    Returns:
        list: The strings contained in the journal element, or a list of lists containing each element.
    Examples:
        >>> read_transaction_journal()
        [['Generic Item', '$0.01'], ['Item 4', '$3.00'], ['Item 1', '$5.00']]
        >>> read_transaction_journal(1)
        ['Item 4', '$3.00']
    """
    if only_selected:
        line = get_text(controls['receipt journal']['selected_line'], timeout)
        if line is None:
            return []
        return line.split('\n')

    if element:
        line = get_text(controls['receipt journal']['line_by_instance'] % element, timeout)
        if line is None:
            return []
        return line.split('\n')
    
    texts = []
    lines = _find_elements(JOURNAL['lines'], timeout=timeout, visible_only=False)
    if not lines:
        return []
    # Scroll through the list to display the text of each element
    try:
        for line in lines:
            driver.execute_script("arguments[0].scrollIntoView(true);", line)
            texts.append(line.text)    
    except StaleElementReferenceException:
        logger.debug("Got a stale element reference exception while reading receipt journal. Retrying.")
        return read_transaction_journal(element=element, only_selected=only_selected, timeout=timeout) # Sometimes happens if the page updates, just try again
 
    return [text.split('\n') for text in texts]

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
    wm = get_text(JOURNAL["watermark"], timeout)
    return '' if wm is None else wm.replace('\n', ' ')

def read_suspended_transactions(timeout=default_timeout):
    """
    Read the contents of the suspended transactions list. Automatically opens it if necessary.
    Args:
        timeout: (int) How long to wait for the suspended transaction list button to be available.
    Returns:
        list: The reg #, transaction #, and amount of each transaction.
    Examples:
        >>> read_suspended_transactions()
        [['1', '11', '$0.01'], ['1', '15', '$5.00']]
        >>> read_suspended_transactions()
        []
    """
    result = []
    texts = get_texts(controls['suspended transactions']['transaction'], timeout=1)
    if not texts:
        if not click_status_line_key('transactions', timeout, verify=False):
            logger.warning("There are no suspended transactions.")
            return []
        texts = get_texts(controls['suspended transactions']['transaction'])
        click_status_line_key('transactions', verify=False)

    return [text.split('\n') for text in texts]

def read_receipt(timeout=default_timeout):
    """
    Gets the text from the currently open receipt.
    Args:
        timeout: (int) How long to wait for the element to be available.
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
        timeout: (int) How long to wait for the element to be available.
    Returns:
        str: The contents of the field.
    Examples:
        >>> read_keypad_entry()
        '10.00'
        >>> read_keypad_entry()
        ''
    """
    text = get_text(KEYPAD['display'], timeout=timeout)
    if text is None:
        return ''

    return text

def read_keyboard_entry(timeout=default_timeout):
    """
    Read the current entry in the text field above the keyboard.
    Args:
        timeout: (int) How long to wait for the element to be available.
    Returns:
        str: The contents of the field.
    Examples:
        >>> read_keyboard_entry()
        'Some text'
        >>> read_keyboard_entry()
        ''
    """
    text = get_text(KEYBOARD['entry'], timeout=timeout)
    if text is None:
        return ''

    return text

def read_fuel_buffer(buffer_id='A', timeout=default_timeout):
    """
    Get the current contents of a fuel buffer.
    Args:
        buffer_id: (char) Letter of the buffer to read.
        timeout: (int) How long to wait for the element to be available.
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

    return get_text(loc, timeout=timeout).split("\n")[1:]

def read_local_account_list(account_id=None, timeout=default_timeout):
    """
    Read the contents of the local accounts list.
    Args:
        account_id: (int) The ID of the account to retrieve information for. Retrieve all accounts by default.
        timeout: (int) How long to wait for the list to be available.
    Returns:
        list: The contents of the local accounts table.
    Examples:
        >>> read_local_account_list()
        [['1', 'DG, Inc.', '1234'],
         ['2', 'KK Company', '5678']]
        >>> read_local_account_list(2)
        ['2', 'KK Company', '5678']
    """
    texts = []
    items = _find_elements(LOC_ACCTS['rows'], timeout=timeout, visible_only=False)
    if not items:
        return None
    # Scroll through the list to display the text of each element
    try:
        for item in items:
            if not item.text:
                driver.execute_script("arguments[0].scrollIntoView(true);", item)
            texts.append(item.text)    
    except StaleElementReferenceException:
        logger.debug("Got a stale element reference exception while reading local accounts. Retrying.")
        return read_list_items(timeout) # Sometimes happens if the page updates, just try again
            
    lines = [text.split('\n') for text in texts]
    if account_id:
        account_id=str(account_id)
        for line in lines:
            if line[0] == account_id:
                return line
        else:
            logger.warning(f"Couldn't find a local account with id {account_id}.")
            return None

    return lines

def read_local_subaccount_list(sub_account_id=None, timeout=default_timeout):
    """
    Read the contents of the local subaccounts list.
    Args:
        sub_account_id: (int) The ID of the subaccount to retrieve information for. Retrieve all subaccounts by default.
        timeout: (int) How long to wait for the list to be available.
    Returns:
        list: The contents of the local accounts table.
    Examples:
        >>> read_local_subaccount_list()
        [['00000000000', '123456', 'SUBACCOUNT 1'], ['00000000001', '222222', 'SECOND SU
        BACCOUNT'], ['00000000002', '9832741984', 'ANOTHER SUBACCOUNT']]
        >>> read_local_subaccount_list('00000000001')
        ['00000000001', '222222', 'SECOND SUBACCOUNT']
    """
    texts = []
    items = _find_elements(LOC_ACCTS['subacct rows'], timeout=timeout, visible_only=False)
    if not items:
        return None
    # Scroll through the list to display the text of each element
    try:
        for item in items:
            if not item.text:
                driver.execute_script("arguments[0].scrollIntoView(true);", item)
            texts.append(item.text)    
    except StaleElementReferenceException:
        logger.debug("Got a stale element reference exception while reading local accounts. Retrying.")
        return read_list_items(timeout) # Sometimes happens if the page updates, just try again
            
    lines = [text.split('\n') for text in texts]
    lines = [[line[0], '', ''] if len(line) < 3 else line for line in lines] # Special case for when subacct ID/description are both blank - split isn't sufficient because no \n divides the two blank elements
    if sub_account_id:
        sub_account_id = str(sub_account_id)
        for line in lines:
            if line[0] == sub_account_id:
                return line
        else:
            logger.warning(f"Couldn't find a local account with id {account_id}.")
            return None

    return lines

def read_local_account_details(timeout=default_timeout):
    """
    Read the local account details and organize them into a dict.
    Args:
        timeout: (int) How many seconds to wait for the message box to be displayed.
    Returns:
        dict: A map of account details to their values.
    Examples:
        >>> read_local_account_details()
        {'Account ID': '1', 'Account Name': 'asdf', 'Sub-Account ID': '00000000000', 'De
        scription': 'Subaccount 1', 'Status': 'Enabled', 'Vehicle ID': '123456', 'Accoun
        t Balance': '$0.00', 'Account Credit Limit': '$100.00'}
        >>> read_local_account_details()['Vehicle ID']
        '123456'
    """
    text = read_message_box(timeout)
    if text is None:
        logger.warning(f"Message box not open within {timeout} seconds.")
        return None
    if "Account ID" not in text:
        logger.warning(f"Message box contains something other than local account details: {text}")
        return None
    text_lines = text.split('\n')
    text_lines_split = [line.split(': ') for line in text_lines]
    return {line[0]: line[1] for line in text_lines_split}

def read_date(timeout=default_timeout):
    """
    Get the date currently displayed on the POS.
    Args:
        timeout: (int) How many seconds to wait for the element to be visible.
    Returns:
        str: The date text displayed on the POS.
    Examples:
        >>> read_date()
        "Jan 14"
    """
    return get_text(controls['header']['datetime'], timeout=timeout).split('\n')[0]

def read_time(timeout=default_timeout):
    """
    Get the time currently displayed on the POS.
    Args:
        timeout: (int) How many seconds to wait for the element to be visible.
    Returns:
        str: The time text displayed on the POS.
    Examples:
        >>> read_date()
        "15:47"
    """
    return get_text(controls['header']['datetime'], timeout=timeout).split('\n')[1]

def read_info(timeout=default_timeout):
    """
    Read the table on the POS Info screen.
    Args:
        timeout: (int) How long to wait for the element to be available.
    Returns:
        (dict) Left column labels mapped to their corresponding values in the right column.
    Examples:
        >>> read_info()
        {'Operator ID': '55', 'Register ID': '1', 'Store ID': '299', 'Store Phone': '(919) 555-5555',
         'Help Desk Phone': '(919) 555-5555', 'Passport Version': '99.99.23.01_DB1902211018', 
         'Support Enabled': 'No', 'Model #': '0', 'Serial #': '0', 
         'NTEP CC No.': '02-039'}
    """
    # TODO: Let this open info automatically? May pose cross-compatibility problems
    keys = _get_texts(INFO['column_1'], timeout=timeout)
    values = _get_texts(INFO['column_2'], timeout=1)
    
    if keys == None or values == None:
        logger.warning(f"Info table not available within {timeout} seconds.")
        return None
    
    return dict(zip(keys, values))

def read_keypad_prompt(timeout=default_timeout):
    """
    Read the prompt text from the status line or login keypad.
    # TODO Move me to cross-compatibility functions
    Args:
        timeout: (int) How long to wait for the element to be available.
    Returns:
        str: the text in the display in the keypad window
    Example:
        >>> read_keypad_prompt()
        "Department 'Dept 16' requires a price to be entered."
    """
    logging.disable(logging.WARNING)
    start_time = time.time()
    while time.time() - start_time <= timeout:
        text = read_status_line(timeout=1) # Keypad prompts on Edge become status line text here
        if not text:
            # Try login keypad
            text = get_text(LOGIN['display'], timeout=1)      
        if text:
            logging.disable(logging.NOTSET)
            logger.info(f"The keypad prompt is {text}")
            return text
    else:
        logging.disable(logging.NOTSET)
        logger.warning(f"Keypad prompt not available within {timeout} seconds.")

def read_keyboard_prompt(timeout=default_timeout):
    """
    Read the prompt text from the login keyboard.
    Args:
        timeout: (int) How long to wait for the element to be visible.
    Returns:
        str: The text of the prompt, if any.
    Example:
        >>> read_keyboard_prompt()
        "Enter Password"
    """
    return get_text(KEYBOARD['prompt'], timeout=timeout)

def read_hardware_status(timeout=default_timeout):
    """
    Not supported
    """
    raise FeatureNotSupported("[read_hardware_status] Hardware status is not supported on HTML POS")

def read_list_items(timeout=default_timeout):
    """
    Read the items in the list area (i.e. reason codes).
    Args:
        timeout: (int) How long to wait for the list area to be visible.
    Returns:def
        list: The text of each item in the list area.
    Example:
        >>> read_list_items()
        ['Cashier error', 'Customer changed mind/left', 'Get Change']
    """
    texts = []
    items = _find_elements(controls['selection list']['options'], timeout=timeout, visible_only=False)
    # Scroll through the list to display the text of each element
    try:
        for item in items:
            if not item.text:
                driver.execute_script("arguments[0].scrollIntoView(true);", item)
            if item.text:
                texts.append(item.text)    
    except StaleElementReferenceException:
        logger.debug("Got a stale element reference exception while reading list items. Retrying.")
        return read_list_items(timeout) # Sometimes happens if the page updates, just try again
            
    return texts

def read_dispenser_diag(timeout=default_timeout):
    """
    Read diagnostic and error text for a dispenser, if there are any.
    Args:
        timeout: (int) How long to wait for the status and error text to be available before returning 'IDLE' and None, respectively. (IDLE is returned for WPF cross-compatibility)
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
    start_time = time.time()
    contents = _get_text(status_loc, timeout=timeout)
    contents = contents.split("\n") if contents else ['IDLE']
    errors = _get_text(error_loc, timeout=timeout-(time.time()-start_time))
    errors = errors.split("\n") if errors else [None]

    result = {}
    result.update({'Status' : contents[0].upper(), 'Errors' : errors[0]})
    return result

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
    processing_text = None

    start_time = time.time()    

    while keypad_text is None and keyboard_text is None and prompt_text is None and processing_text is None and (time.time() - start_time < timeout):

        # Given that we don't know the order or the type of the prompt, we check all types
        
        prompt_text = read_message_box(timeout=1)

        logger.debug(f"The prompt text is {prompt_text}")

        if prompt_text is None:

            keypad_text = read_keypad_prompt(timeout=1)

            logger.debug(f"The keypad text is {keypad_text}")

            if keypad_text is None:
            
                keyboard_text = read_keyboard_prompt(timeout=1)

                logger.debug(f"The keyboard text is {keyboard_text}")

                if keyboard_text is None:

                    processing_text = read_processing_text(timeout=1)
                    logger.debug(f"The processing text is {processing_text}")
        
    
    # We loop until we do not get more prompts
    while keypad_text is not None or keyboard_text is not None or prompt_text is not None or processing_text is not None :
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
                break
                
            except IndexError as e:
                logger.error(f"No buttons or entries were provided for prompt: {keyboard_text}, please check if your prompts appear more than one time ")
                logger.error(e)
                return False
            
            if not enter_keyboard(entry, verify=False):
                logger.error(f"Unable to type {entry} in the keyboard")
                return False

            if not click_keyboard(buttons, verify=False):
                logger.error(f"Unable to click {buttons} in the keyboard")
                return False
            
            logger.debug("Waiting 1 second to allow the app to remove the prompt")
            time.sleep(1)

        elif keypad_text is not None or processing_text is not None:

            if keypad_text is not None:
                current_prompt = keypad_text
            else: 
                current_prompt = processing_text

            if processing_text == "Insert/Swipe/Tap Card":
                
                logger.warning("The pinpad is still processing, waiting it finish")
                start_time =  time.time()
                while processing_text == "Insert/Swipe/Tap Card" and time.time() - start_time < 60:
                    
                    logger.warning("still waiting the pinpad, waiting it finish")
                    processing_text = read_processing_text(timeout=1)
                    logger.debug(f"The processing text is {processing_text}")
                
                if processing_text == "Insert/Swipe/Tap Card":
                    logger.error(f"The pinpad is stuck in {processing_text}")
                    return False

            else:

                logger.debug(f"Attempting to handle prompt: {current_prompt}")

                try:

                    entry = prompts[current_prompt]['entry'].pop(0)
                    buttons = prompts[current_prompt]['buttons'].pop(0) #remove the fisrt in the list so next time we pick the following one
                    keypad_text = None
                    processing_text = None

                except KeyError as e:
                    logger.error(f"The terminal is prompting for {current_prompt} and it is not expected")
                    logger.error(e)
                    break
                    
                except IndexError as e:
                    logger.error(f"No buttons or entries were provided for prompt: {current_prompt}, please check if your prompts appear more than one time ")
                    logger.error(e)
                    return False
                
                logger.info(f"Attempting to enter {entry} in the keypad and then {buttons}")
                if not enter_keypad(entry, after=buttons,verify=False):
                    logger.error(f"Unable to type {entry} in the keypad")
                    return False
                
                logger.debug("Waiting 1 second to allow the app to remove the prompt")
                time.sleep(1)            

        elif prompt_text is not None:
            
            logger.debug(f"Attempting to handle prompt: {prompt_text}")

            try:
                
                buttons = prompts[prompt_text]['buttons'].pop(0) #remove the fisrt in the list so next time we pick the following one
                old_prompt = prompt_text    
                
            except KeyError as e:
                logger.error(f"The terminal is prompting for {prompt_text} and it is not expected")
                logger.error(e)
                break
                
            except IndexError as e:
                logger.error(f"No buttons were provided for prompt: {prompt_text}, please check if your prompts appear more than one time ")
                logger.error(e)
                return False

            start_time = time.time()    

            #prompt_text = read_message_box(timeout=1)

            while old_prompt == prompt_text and time.time() - start_time < 5:
                
                logger.debug(f"trying to click {prompt_text} with {buttons}")
                if click_message_box_key(buttons, verify=False):
                    logger.debug("Waiting 1 second to allow the app to remove the prompt")
                    time.sleep(1)
                
                prompt_text = read_message_box(timeout=1)
            
            if old_prompt == prompt_text:
                    logger.error(f"Unable to click {buttons} in the prompt")
                    return False

            prompt_text = None
        
        # Reading again to realize if we have more prompts

        prompt_text = read_message_box(timeout=2)

        logger.debug(f"The prompt text is {prompt_text}")

        if prompt_text is None:

            keypad_text = read_keypad_prompt(timeout=2)

            logger.debug(f"The keypad text is {keypad_text}")

            if keypad_text is None:
            
                keyboard_text = read_keyboard_prompt(timeout=2)

                logger.debug(f"The keyboard text is {keyboard_text}")

                if keyboard_text is None:

                    processing_text = read_processing_text(timeout=2)
                    logger.debug(f"The processing text is {keyboard_text}")
    
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

def read_dispenser_indicators(timeout=default_timeout):
    """
    Get information about the appearance of the status indicators that appear on the dispenser via their CSS attributes, as well as their HTML class names.
    Args:
        timeout: (int) How many seconds to wait for the indicators to be accessible.
    Returns:
        list: A list of dicts containing relevant CSS properties and class name of the indicator for each dispenser.
    Example:
        >>> read_dispenser_indicators()
        [ {'background-color': 'rgba(200, 77, 77, 1)', 'animation': '1s linear 0s infinite normal none running blinker', 'visibility': 'visible', 'class': 'forecourt_navigator_item dispenserState_CrindPaymentReject selected'},
          {'background-color': 'rgba(0, 0, 0, 0)', 'animation': 'none 0s ease 0s 1 normal none running', 'visibility': 'hidden', 'class': 'forecourt_navigator_item dispenserState_Inoperative'} ]
    """
    ret = []
    css_properties_to_return = ["background-color", "animation", "visibility"]
    attributes_to_return = ["class"]
    indicator_elts = _find_elements(FORECOURT['status indicators'], timeout=timeout, visible_only=False)
    if not indicator_elts:
        logger.warning(f"Dispenser status indicators were not accessible within {timeout} seconds.")
        return None

    for elt in indicator_elts:
        indicator_data = {prop: elt.value_of_css_property(prop) for prop in css_properties_to_return}
        indicator_data.update({attr: elt.get_attribute(attr) for attr in attributes_to_return})
        ret.append(indicator_data)

    # ret = [{**{prop: elt.value_of_css_property(prop) for prop in css_properties_to_return}, **{attr: elt.get_attribute(attr) for attr in attributes_to_return}} for elt in indicator_elts] # Same as the above for loop

    return ret

##################################
## Misc. click/select functions ##
##################################

# For clicking things other than POS keys.
@test_func
def click_journal_item(item=None, instance=1, timeout=default_timeout):
    """
    Click on an item in the transaction journal.
    Args:
        item: (str) Text identifying the item or transaction to select.
                This can be the name, price, etc.
        instance: (int) Index of item to select if there are multiple matches
                    or if no text is specified. Note that Begin/End Transaction
                    count as items in the journal.
        timeout: (int) How long to wait for the element to be available.
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
    if item is None:
        return click_key(controls['receipt journal']['line_by_instance'] % instance, timeout=timeout)

    return click_key(controls['receipt journal']['line_by_text_and_instance'] % (item.lower(), instance), timeout=timeout)

@test_func
def click_suspended_transaction(price=None, instance=1, timeout=default_timeout):
    """
    Select a suspended transaction.
    Args:
        price: (str) The price of the transaction to resume, i.e. $0.01
        instance: (int) Which transaction to select if there are multiple matches
            or if no price is specified.
        timeout: (int) How long to wait for the element to be available.
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
    if not is_element_present(controls['suspended transactions']['transaction']):
        logger.debug("Clicking suspended transaction button")
        click_status_line_key('transactions', verify=False)
    
    # Get a list with suspended transactions
    logger.debug("Obtaining a list with suspended transactions")
    if price is None:
        trans_list = _find_elements(controls['suspended transactions']['transaction'], timeout=timeout)
    else:
        trans_list = _find_elements(controls['suspended transactions']['transaction_by_price'] % price, timeout = timeout)

    if trans_list == None:
        # Nothing was found
        logger.error("Unable to resume the transaction since no suspended transactions were found")
        return False
    else:
        # Try to click on the target instance
        logger.debug("Trying to click on the transaction with instance [%d]"%(instance))
        trans_list[instance - 1].click()
            
        logger.debug("Checking for popup message about resuming transaction")
        if "Do you want to resume" in read_message_box():
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
        timeout: (int) How long to wait for the element to be available.
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
    return click_key(controls['receipt search']['item_by_index'] % num, timeout=timeout)

@test_func
def select_list_item(list_item, timeout=default_timeout, partial=False):
    """
    Select an item from a list prompt, such as qualifiers or reason codes.
    Args:
        list_item: (str) The item in the list to select.
        timeout: (int) How long to wait for the element to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
        partial: (bool) If True, accept the first partial match rather than requiring an exact match.
    Returns:
        bool: Whether or not the item was successfully selected
    Examples:
        >>> select_list_item("EMPLOYEE DISCOUNT")
        True
        >>> select_list_item("6-PACK")
        True
        >>> select_list_item("Quarter\n5\n$ 1.25")
        True
        >>> select_list_item("Quarter", partial=True)
        True
        >>> select_list_item("NotAListItem")
        False
    """
    list_item = list_item.lower()
    items = _find_elements(controls['selection list']['options'], timeout=timeout, visible_only=False)
    # Scroll through the list to display the text of each element
    try:
        for item in items:
            if not item.text:
                driver.execute_script("arguments[0].scrollIntoView(true);", item)
            if (partial and list_item in item.text.lower()) or item.text.lower() == list_item:
                item.click()
                return True
    except StaleElementReferenceException:
        logger.debug("Got a stale element reference exception while trying to select a list item. Retrying.")
        return select_list_item(list_item, timeout, partial) # Sometimes happens if the page updates, just try again
    
    logger.warning(f"Unable to find and select list item {list_item}.")
    return False

@test_func
def select_dispenser(disp_num, timeout=default_timeout):
    """
    Select a dispenser in the POS dispenser GUI.
    Args:
        disp_num: (int) The number of the dispenser to select.
        timeout: (int) How long to wait for the element to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True for success, False for failure.
    Examples:
        >>> select_dispenser(3)
        True
        >>> select_dispenser(65)
        False
    """
    return click_key(controls['forecourt']['dispenser'] % disp_num, timeout)

@test_func
def click_dispenser_indicator(disp_num, timeout=default_timeout):
    """
    Click on the scrollbar status indicator for a given dispenser, if it's currently visible.
    Args:
        disp_num: (int) The number of the dispenser to click the indicator for.
        timeout: (int) How many seconds to wait for the indicator to be visible.
    Returns:
        bool: True if success, False if failure
    Example:
        >>> click_dispenser_indicator(5)
        True
    """
    return click_key(FORECOURT["status_indicator_by_id"] % disp_num, timeout)

@test_func
def click_fuel_buffer(buffer_id, timeout=default_timeout):
    """
    Click on a fuel buffer
    Args:
        buffer_id: (char) The buffer to select, A or B
        timeout: (int) How long to wait for the element to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: Success/failure
    Examples:
        >>> click_fuel_buffer('A')
        True
        >>> click_fuel_buffer('B')
        False
        >>> click_fuel_buffer('C')
        False
    """
    logger.debug("Entered click_fuel_buffer() method")
    try:
        return click_key(controls['forecourt'][f"buffer {buffer_id.lower()}"], timeout)
    except KeyError:
        logger.error(f"Buffer should be A or B and not {buffer_id}")
        return False

#################
# Miscellaneous #
#################

def swap_to_console():
    """
    Switch from HTML POS to cashier control console.
    Automate the console using the console module after calling this.
    Switch back using console.swap_to_pos() when done (warning: the POS will break if Chrome
    is closed without doing this). Use of this method is only recommended when
    specifically testing POS swap functionality.
    Args: Nones
    Returns:
        bool: Success/failure
    Examples:
        >>> swap_to_console()
        True
    """
    logger.info("Swapping from POS to cashier control console.")
    if not click_function_key("Control Console", verify=False):
        return False
    driver.switch_to_frame(_find_element(controls['console']))
    from app import console
    console.driver = driver # Pass our Chrome driver to checkout module
    return True

#################################
# Cross compatibility functions #
#################################

@test_func
def click_prepay_key(key, timeout=default_timeout):
    """
    Click an amount preset key when adding a prepay. This is for cross-compatibility with WPF POS.
    Args:
        key (str): The text of the key to click.
        timeout: (int) How long to wait for the element to be available.
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
    return click_key(controls['keypad']['preset_by_text'] % key.lower(), timeout)

@test_func
def click_preset_key(key, timeout=default_timeout):
    """
    Click an amount preset key when presetting a dispenser, or a pricing level/grade/amount key when adding manual fuel. This is for cross-compatibility with WPF POS.
    Args:
        key: The text of the key to click.
        timeout: (int) How long to wait for the element to be available.
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
        key.replace("level", "pricing") # Text changes from WPF to HTML POS
   
    if key.startswith('$'):
        return click_key(controls['keypad']['preset_by_text'] % key.lower(), timeout)
    return click_key(controls['prompt box']['key_by_text'] % key.lower(), timeout)

@test_func
def click_reminder_box_key(key, timeout=default_timeout):
    """
    Click a key in the prompt box. This is for cross-compatibility with POS.
    Args:
        key: (str) The key that will be select.
        timeout: (int) How long to wait for the element to be available.
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
        timeout: (int) How long to wait for the element to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> click_info_key("Cancel")
        True
    """
    logger.info("HTML CWS does not have keys in the Info window. Doing nothing.")
    return True

@test_func
def click_restriction_keypad(key, timeout=default_timeout):
    """
    Click a key in the keypad. This is here for WPF cross-compatibility.
    Args:
        key: (int/str) The keypad key that will be clicked.
             Must be for a single key.
        timeout: (int) How long to wait for the element to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> click_restriction_keypad("Default")
        True
        >>> click_restriction_keypad("jkl;")
        False
    """
    return click_key(controls['keypad'][key.lower()], timeout)

@test_func            
def click_restriction_key(key, timeout=default_timeout):
    """
    Click a key in the keypad. This is here for WPF cross-compatibility.
    Args:
        key: (str) Text describing the key to click. Please note that calendar dates and the Deny key are not supported on HTML POS.
        timeout: (int) How long to wait for the element to be available.
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
        logger.info("Manual key is not supported for HTML CWS. Skipping it since we can still enter birth date.")
        return True
    elif key.upper() == "DENY":
        raise FeatureNotSupported("Deny key is not supported for restriction handling on HTML CWS.")

    return click_key(controls['keypad'][key.lower()], timeout)

@test_func
def click_pwd_key(key, timeout=default_timeout):
    """
    Click a key in the password entry keyboard. This is for cross compatibility with WPF POS.
    Args:
        key: (str) the key that has been requested. Will only do ONE key at a time.
        timeout: (int) How long to wait for the element to be available.
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
    return click_keypad(key, timeout=timeout, verify=False)

@test_func
def click_tools_key(key, timeout=default_timeout):
    """
    Click a key in the Tools submenu. This is for cross compatibility with WPF POS.
    """
    return click_function_key(key, timeout, verify=False)

def click_key(xpath, timeout=default_timeout):
    """
    Click the HTML element in self checkout that matches the given XPATH.
    Args:
        xpath: XPATH for the desired key. See console_controls.json for pre-mapped paths.
        timeout: How many seconds to wait for the desired key to be available.
    Returns: (bool) True if success, False if failure
    Examples:
        >>> click_key(controls['function keys']["User Options"])
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
Helper Functions.
"""
def _process_payment(card_name, payload, decline_transaction_flag, timeout=5):
    logger.debug("Entered _process_payment() method")
    # Wait for the payment process to finish
    logger.debug("Initiating timeout loop. Waiting for payment process to finish. Looking for Pinpad panel in POS to go away")
    start_time = time.time()
    temp_level = logger.getEffectiveLevel()
    logger.setLevel(999)
    while time.time() - start_time <= timeout:
        # Check if the pinpad screen is still present. When it's gone, the transaction is completed
        if not _is_element_present(PAYMENT_PROC['panel'], timeout = 0.35):
            pinpad.reset() #TODO: Remove once pinpad is updated
            logger.setLevel(temp_level)
            break
        # Check if there is a decline message box and if this test case will validate host decline scenario
        decline_msg = read_message_box(timeout = 1.5)
        if decline_msg and decline_transaction_flag:
            logger.warning(f"Returning true because we expect that the transaction receives a Decline from host: {decline_msg}")
            return True
    else:
        # Timed out
        logger.setLevel(temp_level)
        logger.error("Transaction is taking too long and we didn't go back to idle screen.")
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

def _is_signed_on(timeout=default_timeout):
    """
    Helper function. Checks to see if the user is signed into HTML POS or not.
    Does not work if a function key submenu (i.e. Tools) is open.
    Args:
        timeout: (int) How many seconds to wait for the signed on state.
    Returns:
        bool: True if signed on, False if not, None if unknown
    Examples:
        >>> _is_signed_on()
        True
        >>> _is_signed_on()
        False
    """
    logger.debug("Checking if signed on.")

    start_time = time.time()
    while time.time() - start_time <= timeout:
        if is_element_present(FUNC_KEYS['sign-off'], timeout=0) or is_element_present(FUNC_KEYS['pay'], timeout=0) or is_element_present(FUNC_KEYS['receipt'], timeout=0):
            logger.debug("POS is currently signed on.")
            return True
    if is_element_present(FUNC_KEYS['sign on'], timeout=0) or is_element_present(FUNC_KEYS['unlock'], timeout=0):
        logger.debug("POS is currently signed off.")
        return False

    logger.debug("Could not determine signed on/off state.")
    return None

def _handle_qualifier(qualifier):
    """
    Helper function for add_item. Select on desired item's qualifier.
    Args:
        qualifier: (str) The qualifier you want to select.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> _handle_qualifier("11/30/1992")
        True
        >>> _handle_qualifier("11.30.1992")
        False       
    """
    if qualifier and not select_list_item(qualifier, verify=False):
        return False
    return click_keypad("Enter", verify=False)

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

def _locate_journal_item(item=None, instance=1, timeout=default_timeout):
    """
    Helper function. Get a journal item's position within the journal.
    Args:
        item: (str) Text identifying the item or transaction to select.
                This can be the name, price, etc.
        instance: (int) Index of item to select if there are multiple matches
                    or if no text is specified.
        timeout: (int) How long to wait for the item to be present in the journal.
    Returns: (int) The item's position in the journal, zero-indexed.
    Example:
        >>> _locate_journal_item("Generic Item", 3)
        5
    """
    if item is None:
        return instance

    element = _find_element(controls['receipt journal']['line_by_text_and_instance'] % (item.lower(), instance), timeout=timeout)
    if not element:
        logger.warning(f"[_locate_journal_item] Instance {instance} of item {item} not in the journal within {timeout} seconds.")
        return None
    elements = _find_elements(controls['receipt journal']['lines'])

    try:
        return elements.index(element)
    except ValueError:
        logger.warning("[_locate_journal_item] Found journal item but could not match it to the list of journal items.")
        return None


def get_text(locator, timeout=default_timeout, type = By.XPATH):
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
        try:
            return button.text
        except StaleElementReferenceException: # Element changed after we found it. Try again
            return get_text(locator, timeout, type)
    return None

def _get_text(*args, **kwargs):
    return get_text(*args, **kwargs)

def get_texts(locator, timeout=default_timeout, type = By.XPATH):
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
        try:
            return [elt.text for elt in elts]
        except StaleElementReferenceException: # Elements changed after we found them. Try again
            return get_texts(locator, timeout, type)

    return None

def _get_texts(*args, **kwargs):
    return get_texts(*args, **kwargs)

def _find_element(locator, timeout=1, type = By.XPATH):
    """
    Helper function. Finds the element matching the given locator.
    If more than one element matches, use _find_elements instead.
    Args:
        locator (str): Element's locator (CSS or XPATH)
        timeout (int): How long to wait for the window and element to be available.
        type: the locator type (By.CSS_SELECTOR or By.XPATH)
    Returns:
        WebElement: The found element.
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

def _find_elements(locator, timeout=1, type = By.XPATH, visible_only=True):
    """
    Helper function. Searches the DOM to find the elements you are looking for.
    Args:
        locator (str): Element's locator (CSS or XPATH)
        timeout (int): How long to wait for the element to be visible/existent.
        type: the locator type (By.CSS_SELECTOR or By.XPATH)
        visible_only: (bool) If True, return only visible elements.
    Returns:
        The list of selenium webelements or None
    Examples:
        >>> _find_element(SOME_VALID_LOCATOR)
        <selenium.webdriver.remote.webelement.WebElement (session="80f1a1ebe8220157e9d2f394e913db02", element="0.05045595521012469-1")>
        >>> _find_element(SOME_INVALID_LOCATOR)
        None
    """
    condition = EC.visibility_of_any_elements_located((type, locator)) if visible_only else EC.presence_of_all_elements_located((type, locator))
    try:
        logger.debug("Looking for elements with locator [%s]"%(locator))
        return WebDriverWait(driver, timeout).until(condition)
    except TimeoutException:
        logger.warning(f"No elements with locator {locator} were visible within {timeout} seconds")
        return None
    except StaleElementReferenceException: # Sometimes raised if the DOM is modified while we check visibility. Just try again
        return _find_elements(locator, timeout, type)

def is_element_present(locator, timeout=prompt_timeout, type = By.XPATH):
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
    logger.debug("Checking if the element with locator [%s] is present"%(locator))
    try:
        WebDriverWait(driver, timeout).until(lambda x: x.find_element(type, locator).is_displayed())
        return True
    except TimeoutException:
        logger.debug("Element with locator [%s] is not present within %s seconds." % (locator, timeout))
        return False
    except StaleElementReferenceException: # Sometimes raised if the DOM is modified while we check visibility. Just try again
        return is_element_present(locator, timeout, type)

def _is_element_present(*args, **kwargs):
    return is_element_present(*args, **kwargs)