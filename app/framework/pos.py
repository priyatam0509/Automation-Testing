"""
Name: pos
Description: This is a process to use the keys for the Passport POS. This is
            for general use. However, it may be linked to other modules for
            transactions or navigation.

Date created: 08/17/2017
Modified By:
Date Modified:
"""


__author__ = "Philip Osborne"
__maintainer__ = "Jesse Thomas"

import functools
import time
import os
import json
import logging, requests
from pywinauto.application import Application
from pywinauto.timings import Timings, TimeoutError
from pywinauto.findwindows import ElementAmbiguousError, ElementNotFoundError
from pywinauto.keyboard import send_keys
from _ctypes import COMError
from PIL import Image, ImageGrab
import re

# In-House Modules
from app import system
from app.util import constants
from app.framework.tc_helpers import test_func, tc_fail
from app import pinpad

#Paths and script name.
script_path = os.path.dirname(os.path.realpath(__file__))
test_script_name = os.path.basename(__file__)

Timings.fast()

json_path = constants.USER_CREDENTIALS # Change this when we finalize where to store temporary data files
logger = logging.getLogger(__name__)

default_timeout = 10

BRAND = system.get_brand()

# POS connection objects
window = None
msg_bar = None
func_keys = None
msg_box = None
tender_keys = None
speedkey = None
dept_key = None
dispenser = None
prepay_keys = None
prepay_grades = None
preset_keys = None
preset_grades = None
trans_window = None
trans_queue = None
trans_journal = None
list_window = None
keypad = None
keypad_cmd = None
keypad_entry = None
pwd_keys = None
receipt_search = None
restr_window = None
till_keypad = None
credentials = ['91', '91']
pos_admin_keys = None
loc_acc_selection_window = None
loc_acc_detail_window = None
reminder_window = None
info_window = None
dispenser_menu = None
attendant = None
pinpad_timeout = default_timeout

class POSException(Exception):
    def __init__(self, arg):
        self.message = arg

def connect(timeout=60, recover=False):
    global window, msg_bar, func_keys, msg_box, tender_keys, speedkey, dept_key,\
    dispenser, prepay_keys, prepay_grades, preset_keys, preset_grades, trans_window,\
    trans_queue, trans_journal, list_window, keypad, keypad_cmd, keypad_entry,  pwd_keys,\
    receipt_search, restr_window, till_keypad, credentials, pos_admin_keys,\
    loc_acc_selection_window, loc_acc_detail_window, reminder_window, info_window,\
    dispenser_menu, attendant
    if not system.process_wait("RunIt.exe", timeout):
        raise POSException("The RunIt Process did not activate within %s"
                           " seconds." %(timeout))
    window = Application(backend='uia').connect(path='RunIt.exe')
    msg_bar = window["Status Line"]
    func_keys = window['POS function keys']
    msg_box = window['Window1']
    tender_keys = window["Andrew's tender t"]
    speedkey = window["Speedkey"]
    dept_key = window["DeptKey"]
    dispenser = window["DispenserWindow"]
    prepay_keys = window["FuelPrepayDialog"]
    prepay_grades = window["PrepayOptionsDialog"]
    preset_keys = window["FuelPreset"]
    preset_grades = window["PresetOptions"]
    trans_window = window["ListWindow"]
    trans_queue = trans_window['ListBox1']
    trans_journal = trans_window['ListBox2']
    # Trans window becomes 'ListWindowDialog2' when a list selection is open
    # (qualifier, reason code, etc)
    list_window = window["ListWindow"]
    keypad = window['POS keypad']
    keypad_cmd = window['Command form']
    keypad_entry = window[''] # Yes, this window has no name.
    pwd_keys = window["Keyboard"]
    receipt_search = window["Search List"]
    restr_window = window['RestrictionWindow']
    till_keypad = window['CommandKeyListWindow']
    credentials = ['91', '91']
    pos_admin_keys = window['POS Admin']
    loc_acc_selection_window = window['Local Accounts Selection']
    loc_acc_detail_window = window['WarningBox']
    reminder_window = window['ReminderBox']
    info_window = window['POS Status']
    dispenser_menu = window['DispenserMenuWindow']
    attendant = window['AttendantSetupWindow']
    if recover:
        wait_time = 10
    else:
        wait_time = 120
    if not read_status_line(wait_time):
        raise POSException("The Status Line did not become visible within "
                           "2 minutes time.")

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
                        if click_function_key("Cancel", verify=False):
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

#########################
## Key click function  ##
#########################

# For clicking pretty much any key with identifiable text.
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
    Creator: Cassidy Garner
    """
    WILD = "**" # Indicates places where keys can have variable text.
    WILDNUM = "##" # Variable number

    # Map of functions and the keys they may be used to click on.
    map = { "click_msg_bar": ['NW', 'HELP'],
            "click_function_key": ['PRICE CHECK', 'SAFE DROP', 'SPEED KEY', 'DEPT KEY', 'TIME CLOCK',
                         'PLAY AT THE PUMP', 'LOYALTY', 'NO SALE', 'REFUND', 'CHG/REF DUE', 'MORE',
                          'SIGN ON', 'SIGN OFF', 'PAID IN', 'LOC ACCT PAID IN', 'LOCK', 'SEARCH', 'CLEAN', 'NETWORK',
                          'LOAN', 'PAID OUT', 'CLOSE TILL', 'INFO', 'BACK', 'TOOLS', 'CHANGE PASS', 'TILL AUDIT',
                          'DISPENSER', 'TANK', 'CHANGE SPEEDKEYS', 'OVERRIDE', 'FS/NO FS', 'CONVERT', 'VOID ITEM',
                          'VOID TRANS', 'CUSTOMER ID', 'SUSPEND', 'QUANTITY', 'PAY', 'TAX MODIFY', 'TAX EXEMPT', 'DISCOUNT',
                          'RESET PASS'],
            "click_message_box_key": ['YES', 'NO', 'OK', 'CANCEL'],
            "click_speed_key": ['GENERIC ITEM', 'MORE', 'BACK', WILD],
            "click_dept_key": ['DEPT ' + WILDNUM, 'MORE', 'BACK', WILD],
            "click_forecourt_key": ['ALL STOP', 'AUTH', 'PREPAY', 'PRESET', 'MANUAL', 'RECEIPT', 'STOP', 'DIAG', 'CLEAR ERRORS', 'MORE', 'GO BACK'],
            "click_prepay_key": ['$5.00', '$10.00', '$20.00', '$50.00', 'BALANCE', 'REGULAR', 'PLUS', 'SUPREME', WILD], # probably need to add more grade names here and account for brand
            "click_preset_key": ['$5.00', '$10.00', '$20.00', '$50.00', 'REGULAR', 'PLUS', 'SUPREME', 'CASH LEVEL', 'CREDIT LEVEL', WILD],
            "click_tender_key": ['$1.00', '$5.00', '$10.00', '$20.00', '$50.00', 'CARD', 'CHECK', 'CASH', 'IMPRINTER', 'OTHER', 'BILLS->', 'COINS->', WILD],
            "click_keypad": ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '00', 'CLR', 'CANCEL', 'ENTER', 'SELL ITEM', '@', '+', '-', 'PLU'],
            "click_pwd_key": ['!', '@','#', '$', '%', '^', '&', '*', '(', ')', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', 'A', 'S', 'D',
                         'F', 'J', 'K', 'L', '\\', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', '/', ':', '.', 'SPACE', '1', '2', '3', '4', '5', '6',
                         '7', '8', '9', '0', 'CLR', 'BACK', 'CANCEL', 'OK'],
            "click_receipt_key": ['CANCEL', 'SEARCH'],
            "click_restriction_key": ['DENY', 'DEFAULT', 'CANCEL', 'ENTER', '1 JANUARY', '2 FEBRUARY', '3 MARCH', '4 APRIL', '5 MAY', '6 JUNE',
                             '7 July', '8 AUGUST', '9 SEPTEMBER', '10 OCTOBER', '11 NOVEMBER', '12 DECEMBER', '1', '2', '3', '4', '5',
                             '6', '7', '8', '9', '0', 'CLR'],
            "click_till_key": ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '00', 'CLR', '+', '-', 'CANCEL', 'FINALIZE'],
            "click_tools_key": ['STORE CLOSE', 'SHIFT CLOSE', 'DISABLE CAR WASH', 'ENABLE CAR WASH', 'DISABLE MERCH', 'ENABLE MERCH',
                               'BACK', 'MGR WKSTN', 'REBOOT', 'SUPPRT'],
            "click_local_account_key": ['MANUAL SEARCH', 'DETAILS', 'CANCEL', 'CONFIRM'],
            "click_local_account_details_key": ['OK'],
            "click_reminder_box_key": ['OK', 'OK ALL'],
            "click_dispenser_key": ['TEST FUEL', 'DISPENSER OPTIONS', 'FUEL PRICE CHANGE', 'ATTENDED OPTIONS', 'DISPENSER TOTALS', 'TANK MONITOR',
                               'GO BACK', 'UPDATE', 'CANCEL', 'PRINT'],
            "click_attendant_key": ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'CLR', 'CANCEL', 'ENTER', 'ASSIGN DISPENSER',
                          'UNASSIGN DISPENSER', 'ACTIVATE TOKEN', 'SAFE DROP', 'CLOSE TILL', 'GO BACK', 'DISP' + WILDNUM]
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
    log_level = logger.getEffectiveLevel()
    if log_level > logging.DEBUG:
        logger.setLevel(999) # Temporarily disable logging to prevent spam, unless we're at debug level
    while time.time() - start_time <= timeout:
        for func in funcs_to_try:
            if func(key, timeout=0, verify=False):
                logger.setLevel(log_level)
                return True
    else:
        logger.setLevel(log_level)
        logger.warning("Couldn't find %s within %d seconds." % (key, timeout))
        return False

##########################
## High-level functions ##
##########################

# High-level functions, mainly for running transactions.
@test_func
def enter_keypad(entry, timeout=default_timeout, after=None):
    """
    Enter a series of digits on the keypad.
    Args:
        entry: (str) The digits to enter.
        timeout: (int) How many seconds to wait for the keypad to be available.
        after: (str) The key to press after entering digits.
    Examples:
        >>> enter_keypad("1234")
        True
        >>> enter_keypad("789asdf")
        False
        >>> enter_keypad("4321", after="PLU")
        True
    """
    entry = str(entry)
    windows_to_try = [keypad, pwd_keys, restr_window, attendant]
    start_time = time.time()
    done = False
    while time.time() - start_time <= timeout:
        for window in windows_to_try:
            try:
                window.wait('ready', 0)
                done = True
                break
            except:
                continue
        if done:
            break
    else:
        logger.warning(f"No keypad available within {timeout} seconds.")
        return False
                
    for char in entry:
        if not click_keypad(char, verify=False):
            return False

    return click_keypad(after, verify=False) if after else True

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
    start_time = time.time()
    while time.time() - start_time <= timeout:
        # Make sure we're in speed key mode
        if not speedkey.exists():
            click_function_key("SPEED KEY", timeout=0, verify=False)
        try:
            keypad.wait('ready', 0)
            break
        except:
            continue
    else:
        logger.warning("Couldn't get to PLU entry within %s seconds." % timeout)
        return False

    if not enter_keypad(plu, 0, verify=False):
        return False
    return click_keypad('PLU')

@test_func
def add_item(item="Generic Item", method="Speed Key", quantity=1, price=None, qualifier=None, cash_card_action=None):
    """
    Add an item to the current transaction.
    Args:
        item: (str) The name or PLU of the item.
        method: (str) The method of item entry. Can be PLU, Speed Key, or Dept Key.
        quantity: (int) The quantity of the item to add.
        price: (str) The price to enter for the item, if any.
        qualifier: (str) The qualifier to select for the item, if it has any.
        cash_card_action: (str) The action to take if this item is a Cash Card. Can be Activate or Recharge.
    Return:
        bool: True on success, False on failure.
    Examples:
        >>> add_item()
        True
        >>> add_item("101", method="PLU")
        True
        >>> add_item("Dept 13", method="Dept Key", price="$10.00")
        True
        >>> add_item("Coke", method="Speed Key", qualifier="6-Pack", quantity=2)
        True
    """
    # Add the item
    if method.upper() == "SPEEDKEY" or method.upper() == "SPEED KEY":
        if not click_speed_key(item, verify=False):
            return False
    elif method.upper() == 'DEPT KEY':
        if price is None:
            logger.warning("Price must be specified for Department Key entry.")
            return False
        if not click_dept_key(item, verify=False):
            return False
    elif method.upper() == 'PLU':
        enter_keypad(item, verify=False)
        click_keypad("PLU", verify=False)
    else:
        logger.warning(f"Invalid method for add_item: '{method}'")
        return False

    # Handle qualifier
    if "Please select a qualifier" in read_status_line():
        if qualifier is None:
            logger.warning(f"Item {item} has qualifiers. Please specify a qualifier.")
        select_list_item(qualifier, verify=False)
        click_keypad("ENTER", verify=False)
        item = f"{item} with qualifier {qualifier}" # For clearer logging if something errors later

    # Handle cash card prompt if applicable
    msg = read_message_box()
    if msg and "Press Yes for Activation or No for Recharge" in msg:
        if cash_card_action is None:
            logger.warning("Please specify Activate or Recharge for cash_card_action.")
            return False
        if cash_card_action.lower() == "activate":
            click_message_box_key("YES", verify=False)
        elif cash_card_action.lower() == "recharge":
            click_message_box_key("NO", verify=False)

    # Handle price required
    price_req = "Please enter the amount" in read_status_line()
    if price_req:
        if price is None:
            logger.warning(f"Item {item} is Price Required. Please specify the price.")
            return False
        price = price.replace("$", "").replace(".", "")
        enter_keypad(price, verify=False)
        click_keypad('ENTER', verify=False)
    
    # Handle quantity required
    quantity_req = "Please enter the quantity" in read_status_line()
    if quantity_req:
        enter_keypad(quantity, verify=False)
        click_keypad("ENTER", verify=False)
    
    # Handle price override
    if price is not None and not price_req:
        price = price.replace("$", "").replace(".", "")
        click_function_key('OVERRIDE', verify=False)
        if "select a valid reason" in read_status_line().lower():
            click_keypad("ENTER", verify=False)
        enter_keypad(price, verify=False)
        click_keypad('ENTER', verify=False)

    # Handle quantity override
    if quantity != 1 and not quantity_req:
        click_function_key('QUANTITY', verify=False)
        enter_keypad(quantity, verify=False)
        click_keypad('ENTER', verify=False)

    return True
    #TODO: age verification

@test_func
def add_fuel(amount, dispenser=1, mode="Prepay", grade="REGULAR", level="CASH"):
    """
    Add fuel to the current transaction.

    Args:
        amount: (str) Dollar amount of fuel to purchase.
        dispenser: (int) Number of the dispenser to purchase fuel on.
        mode: (str) Prepay, preset, or manual.
        grade: (str) The fuel grade to select.
        level: (str) Cash/Credit pricing level.

    Return: 
        bool: True on success, False on failure.

    Examples:
        >>> add_fuel("$20.00", 3)
            True
        >>> add_fuel("$11.11", 4, "Manual", "SUPREME", "Credit")
            True
    """
    # Add fuel
    if not select_dispenser(dispenser, verify=False):
        return False
    if not click_forecourt_key(mode.upper(), verify=False):
        return False
    if mode.upper() != "PRESET" and not click_prepay_key(grade.upper()):
        return False
    stripped_amount = amount.replace("$", "").replace(".", "")
    if not enter_keypad(stripped_amount, verify=False):
        return False
    if not click_keypad('ENTER', verify=False):
        return False

    #Presets go straight into a suspended transaction. So no transaction journal check needed.
    if mode.upper() == "PRESET":  return True

    # Convert amount to journal format if needed
    if not amount.startswith('$'):
        amount = f"${amount}"
    if not amount[-2] == '.':
        amount = f"{amount[:-2]}.{amount[-2:]}"

    start_time = time.time()
    while time.time() - start_time < 3:
        # Verify fuel was added to the transaction
        journal = read_transaction_journal()
        for i in range(len(journal)): # So we don't have to worry about case sensitivity
            for j in range(len(journal[i])):
                journal[i][j] = journal[i][j].upper()
        
        item = f"{grade} {level[:2]} on {dispenser}"
        if any([item.upper() in line for line in journal]):
            logger.info(f"{item} was found in the journal after adding fuel.")
            return True
        if any([amount.upper() in line for line in journal]):
            logger.info(f"{amount} was found in the journal after adding fuel.")
            return True
    else:
        logger.warning(f"Could not find {item} within 3 seconds.")
        return False

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

    if not click_function_key("Void Trans", verify=False):
        return False

    # If prompted if we are sure
    if "are you sure" in read_message_box().lower():
        click_message_box_key("YES", verify=False)

    # If prompted for reason, move past.
    if "valid reason" in read_status_line().lower():
        click_keypad("ENTER", verify=False)

    return "press the speed keys" in read_status_line().lower()

@test_func
def void_item(item, timeout=default_timeout):
    """
    Voids the passed in item from a transaction.
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

    return click_function_key("Void Item", verify=False)

#If the below has issues, look into reading the dispenser diag instead
@test_func
def wait_for_fuel(buffer='A', timeout=30):
    '''
    Wait for the buffer to clear.

    Args:
        buffer: (str) The buffer you want to check. Either 'A' or 'B'.
        timeout: (int) How long you want to wait for the buffer to clear.

    Returns:
        True/False: (bool) True when the buffer clears, or False when it times out.
    '''
    logger.debug(f"Waiting for buffer {buffer} to clear")
    start_time = time.time()
    while time.time() - start_time <= timeout:
        #Read the Buffer
        if 'EMPTY' in read_fuel_buffer(buffer):
            logger.debug(f"Buffer {buffer} is Empty")
            return True
    logger.warning(f'Buffer {buffer} did not become "Empty" within {timeout} seconds')
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
    if not wait_for_disp_status('IDLE', dispenser, idle_timeout, verify=False):
        click_forecourt_key("DIAG", verify=False)
        status = read_dispenser_diag(timeout=120)['CRIND'] # We need a long timeout here because diag is hard to read during a download
        if 'DOWNLOAD' in status:
            logger.info(f"Dispenser {dispenser} is downloading. Waiting up to {dl_timeout} seconds for it to finish.")
            if not wait_for_disp_status('IDLE', dispenser, dl_timeout, verify=False):
                logger.warning("Download did not complete within {dl_timeout} seconds.")
                return False
        else:
            logger.warning(f"Dispenser {dispenser} did not become idle or start a download within {idle_timeout} seconds. Actual status: {status}")
            return False

    return True

@test_func
def wait_for_disp_status(status, dispenser = 1, timeout=60):
    """
    Wait for a dispenser to have a given CRIND status.
    Args:
        status: (str) The status to check for.
        dispenser: (int) The dispenser you want to check.
        timeout: (int) How many seconds to wait for the desired status.
    Returns: (bool) Whether or not the desired status occurred within the timeout.
    Examples:
        >>> wait_for_disp_status("Download", 2)
        True
        >>> wait_for_disp_status("IDLE")
        True
    """
    if not status:
        status = 'IDLE' # read_dispenser_diag returns IDLE if there is no status

    select_dispenser(dispenser, verify=False)
    if not read_dispenser_diag(timeout=0):
        click_forecourt_key('DIAG', verify=False)
    last_diag = ""
    start_time = time.time()
    while time.time() - start_time <= timeout:
        logging.disable(logging.WARNING) # Prevent log spam from failed reads
        try:
            diag = read_dispenser_diag()
        except:
            raise
        finally:
            logging.disable(logging.NOTSET)
        if diag is None: # Read can intermittently fail due to changing status, especially during a download
            continue
        if diag != last_diag:
            logger.info(f"[wait_for_disp_status] Current status is {diag}")
            last_diag = diag
        if status.upper() in diag['CRIND'].upper():
            click_forecourt_key('GO BACK', verify=False)
            return True
    logger.warning(f"[wait_for_disp_status] Dispenser did not have status {status} within {timeout} seconds.")
    click_forecourt_key('GO BACK', verify=False)
    return False

# TODO
@test_func
def add_item_to_pricebook(scan_code, item_price, item_description, item_dept, timeout=default_timeout):
    logger.warning("Not on Passport POS - do we even want this function?")

@test_func
def pay(amount=None, tender_type="cash", cash_card="GiftCard"):
        """
        Add and verify payment for the current transaction.
        Note that split tendering with the same tender type and amount
        may cause a false positive.
        Args:
            amount: (str) How much to pay if not using card. Default is exact change.
            tender_type: (str) Type of tender to select.
            cash_card: (str) If activating a cash card, the name of the card in CardData.json.
            verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
        Returns:
            bool: True if success, False if fail
        Examples:
            >>> pay()
            True
            >>> pay(amount="$5.00", tender_type="Check")
            True
            >>> pay(tender_type="Imprinter")
            False
        """
        def verify_journal(timeout=10):
            if refund:
                nonlocal tender_type
                tender_type = "Refund " + tender_type + " "
            start_time = time.time()
            while time.time() - start_time <= timeout:
                journal = read_transaction_journal()

                if ["Cash Card Activation"] in journal:
                    if any(['Approved' in item[0] for item in journal]):
                        return True
                    else:
                        logger.warning("Cash card activation was unsuccessful.")
                        return False

                for item in journal: # Find tender in journal
                    if (tender_type.lower() == item[0].lower() and
                        amount == item[1]):
                            return True
            else:
                logger.warning("Didn't find payment in transaction journal.")
                return False

        # Find out how much we need to pay
        refund = False
        balance = read_balance()
        try:
            total = balance['Balance']
        except KeyError:
            try:
                total = balance['Refund Due']
                refund = True
            except KeyError:
                logger.warning("There is no balance to pay out.")
                return False

        if amount is None:
            amount = total
            
        # Get to tender screen
        logger.debug("Attempting to click the Tender/Pay button")
        if not tender_keys.exists() and not click_function_key("pay", timeout=30, verify=False):
            return False
        # Handle loyalty
        msg = read_message_box(timeout=5)
        if msg is not None and "ID" in msg:
            if not click_message_box_key('NO', verify=False):
                click_keypad("CANCEL")
                return False
        # Select tender type
        logger.debug("Selecting the Tender Type")
        while not click_tender_key(tender_type, verify=False):
            if not click_tender_key('more', verify=False):
                logger.warning("The tender type %s does not exist."
                                             %(str(tender_type)))
                return False

        # Transaction ends immediately for Imprinter (maybe other tenders?), check for this
        temp_level = logger.getEffectiveLevel()
        logger.setLevel(999)
        if verify_idle(timeout=1) and verify_journal(timeout=1):
            logger.setLevel(temp_level)
            return True

        # Select or enter tender amount
        if not click_tender_key(amount, timeout=1, verify=False):
            amount_to_enter = amount.replace("$", "").replace(".", "")
            logger.setLevel(temp_level)
            for num in amount_to_enter:
                click_keypad(num, verify=False)
            click_keypad("ENTER", verify=False)      

        # Make sure we went back to idle (if not split tendering) and journal contains the paid tender
        logger.setLevel(temp_level)
        if amount < total: # Split tender case
            # TODO: Add status line verification for split tender case
            if not verify_journal():
                return False
            click_keypad("CANCEL")
            return verify_idle()
        
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
            logger.info("Journal verification for cash card transactions is not implemented in pay(). Please verify success in your script.")
            return verify_idle() # TODO: Success message varies by network. Find a way to verify?

        return (verify_idle() and verify_journal())

def verify_idle(timeout=10):
    start_time = time.time()
    while time.time() - start_time <= timeout:
        status = read_status_line()
        if (status == "Press the speed keys to enter items." or
                status == "Please enter the department items."):
            pinpad.reset() #TODO: Remove this call from this method
            return True
    else:
        logger.warning("Could not verify POS was idle")
        return False

@pinpad_retry
def pay_card(brand='Core', card_name='Visa', debit_fee=False, cashback_amount=None, zip_code=None, cvn=None, custom=None, split_tender=False, cash_card="GiftCard", invoice_number=None, force_swipe=False):
    """
    Pay out tranaction with swiping card.
    Args:
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
        >>> pay_card(
                card_name='MasterCard',
                invoice_number='1234'
            )
        True
    """
    if not tender_keys.exists() and not click_function_key("pay", verify=False):
            return False
    if not click_tender_key('CARD', timeout=30, verify=False):
        return False
    temp_level = logger.getEffectiveLevel()
    logger.setLevel(999)
    msg = read_message_box(timeout=3)
    logger.setLevel(temp_level)
    if msg is not None and "Loyalty ID" in msg: # Loyalty
        if not click_message_box_key('NO', verify=False):
            click_keypad("CANCEL")
            return False
    # TODO : get status code of pinpad and if it is a success, wait until we go back to idle (no more pinpad prompting), then return True.
    try: 
        result = pinpad.use_card(
            brand=brand,
            card_name=card_name,
            debit_fee=debit_fee,
            cashback_amount=cashback_amount,
            zip_code=zip_code,
            cvn=cvn,
            custom=custom,
            force_swipe=force_swipe
        )
    except Exception as e:
        logger.warning(f"Card swipe in pay_card failed. Exception: {e}")
        click_keypad("CANCEL")
        return False
    if not result['success']:
        logger.warning(f"Card swipe in pay_card failed. POST payload: {result}")
        return False

    # TODO: Add status line verification for split tender case
    # add journal verification?
    msg = read_message_box()
    if msg is not None and "split pay" in msg.lower():
        if not split_tender:
            logger.warning("Got an unexpected split pay prompt when paying out transaction.")
            click_message_box_key("NO")
            click_keypad("CANCEL")
            return False
        else:
            click_message_box_key("YES")
            click_keypad("CANCEL")
    elif split_tender:
        logger.warning("Expected split payment prompt but didn't get one.")
        click_keypad("CANCEL")
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

    # Handle refund
    if invoice_number:
        status = read_status_line().lower()
        if "enter invoice number" in status:
            logger.info(f"{status}")
            enter_keypad(invoice_number)
            click_pwd_key("OK")

    return verify_idle()

@test_func
def manual_entry(brand='Core', card_name='Visa', expiration_date=None, zip_code=None, custom=None, split_tender=False, cash_card="GiftCard", invoice_number=None):
    """
    Pay out tranaction using Manual entry.
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
    if not click_tender_key('CARD', verify=False):
        return False
    temp_level = logger.getEffectiveLevel()
    logger.setLevel(999)
    msg = read_message_box(timeout=3)
    logger.setLevel(temp_level)
    if msg is not None and "Loyalty ID" in msg: # Loyalty
        if not click_message_box_key('NO', verify=False):
            return False
        
    if not click_keypad("Manual", verify=False):
        return False

    # TODO : get status code of pinpad and if it is a success, wait until we go back to idle (no more pinpad prompting), then return True.
    try:
        result = pinpad.manual_entry(
            brand=brand,
            card_name=card_name,
            zip_code=zip_code,
            custom=custom
        )
        # TODO : answer expiration date prompt and aux card
    except Exception as e:
        logger.warning(f"PINpad manual entry failed. Exception: {e}")
        return False
    if not result['success']:
        logger.warning(f"Card swipe in manual_entry failed. POST payload: {result}")
        return False

    if not click_message_box_key(key='Yes', verify=False):
        return False

    temp_level = logger.getEffectiveLevel()
    logger.setLevel(999)
    msg = read_message_box(timeout=3)
    logger.setLevel(temp_level)
    if msg is not None and msg == "Is this an Auxiliary Network Card?":
        if not click_message_box_key(key='No', verify=False):
            return False
    
    if card_name == "VisaPurchase" or card_name == "MasterCardPurchase":
        temp_level = logger.getEffectiveLevel()
        logger.setLevel(999)
        msg = read_message_box(timeout=3)
        logger.setLevel(temp_level)
        if msg is not None and msg == f"Is this a {card_name[:len(card_name)-8]} card?":
            if not click_message_box_key(key='No', verify=False):
                return False

        temp_level = logger.getEffectiveLevel()
        logger.setLevel(999)
        msg = read_message_box(timeout=3)
        logger.setLevel(temp_level)
        if msg is not None and msg == f"Is this a {card_name[:len(card_name)-8]} Purchase card?":
            if not click_message_box_key(key='Yes', verify=False):
                return False

    if card_name == "VisaPurchase" or card_name == "MasterCardPurchase":
        temp_level = logger.getEffectiveLevel()
        logger.setLevel(999)
        msg = read_message_box(timeout=3)
        logger.setLevel(temp_level)
        if msg is not None and msg == f"Is this a {card_name[:len(card_name)-8]} card?":
            if not click_message_box_key(key='No', verify=False):
                return False

        temp_level = logger.getEffectiveLevel()
        logger.setLevel(999)
        msg = read_message_box(timeout=3)
        logger.setLevel(temp_level)
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

    # TODO: Add status line verification for split tender case
    # add journal verification?
    msg = read_message_box()
    if msg and "split pay" in msg.lower():
        if not split_tender:
            logger.warning("Got an unexpected split pay prompt when paying out transaction.")
            click_message_box_key("NO")
            click_keypad("CANCEL")
            return False
        else:
            click_message_box_key("YES")
            click_keypad("CANCEL")
    elif split_tender:
        logger.warning("Expected split payment prompt but didn't get one.")
        click_keypad("CANCEL")
        return False

    # Handle cash card swipe if needed
    if "activation" in read_status_line().lower():
        try: 
            pinpad.swipe_card(brand=system.get_brand(), card_name=cash_card)
        except Exception as e:
            logger.warning(f"Cash card swipe in pay failed. Exception: {e}")
            click_keypad("CANCEL", verify=False)
            click_message_box_key("YES", verify=False)
            return False

    # Handle refund
    if invoice_number:
        status = read_status_line().lower()
        if "enter invoice number" in status:
            logger.info(f"{status}")
            enter_keypad(invoice_number)
            click_pwd_key("OK")

    return verify_idle()

# TODO
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
    Returns:
        bool: True if success, False if fail
    Examples:
        >>> 
    """
    # Pay using card_name for Cash card item
    if not click_message_box_key("YES", verify=False): # Clicks Yes for Activation
        logger.warning("Unable to click Yes for Activation")
        return False
    # if not pay_card(brand, card_name, debit_fee, cashback_amount, zip_code, cvn, custom):
    #     logger.warning(f"Unable to purchase Cash Card Item using {card_name} card.")
    #     return False

    if not click_function_key('Pay', timeout=3, verify=False):
        return False
    temp_level = logger.getEffectiveLevel()
    logger.setLevel(999)
    msg = read_message_box(timeout=3)
    logger.setLevel(temp_level)
    if msg is not None and "Loyalty ID" in msg: # Loyalty
        if not click_message_box_key('NO', verify=False):
            return False
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
            if "swipe card for activation" in read_status_line().lower():
                payload = pinpad.swipe_card(
                    brand=BRAND,
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

# TODO
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
    Returns:
        bool: True if success, False if fail
    Examples:
        >>> 
    """
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

    temp_level = logger.getEffectiveLevel()
    logger.setLevel(999)
    msg = read_message_box(timeout=3)
    logger.setLevel(temp_level)
    if msg is not None and "Loyalty ID" in msg: # Loyalty
        if not click_message_box_key('NO', verify=False):
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

    # Swipe GiftCard for Recharge
    pinpad.reset()
    
    time.sleep(5) # TODO: need to fix to wait for processing text to have Recharge

    try:
        payload = pinpad.swipe_card(
            brand=BRAND,
            card_name=gift_card
        )
    except Exception as e:
        logger.warning(f"Card swipe in pinpad.swipe_card failed. Exception: {e}")
        click_function_key("Cancel", verify=False)
        return False

    return _process_gift_card(gift_card, payload)

@test_func
def check_receipt_for(values, rcpt_num=1, dispenser=None, timeout=default_timeout):
    """
    Verify that a receipt contains a specific value or set of values. Ignores whitespace.
    Args:
        values: (str/list) A string or list of strings to find in the receipt.
        rcpt_num: (int) Position of the receipt in the receipt list. Default is 1, the most recent receipt.
        dispenser: (int) Which dispenser to verify the receipt from, if any. None is indoor receipt search.
        timeout: (int) How long to wait for the window to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if all values are verified, False if not
    Examples:
        >>> check_receipt_for("Generic Item $0.01")
        True
        >>> check_receipt_for("Total = asdfjkl;")
        False
        >>> check_receipt_for(["PUMP#3", "REGULAR CR 5.000G", "PRICE/GAL $1.509"], dispenser=3)
        True
    """
    if type(values) is not list:
        values = [values]
    if dispenser is not None:
        select_dispenser(dispenser, verify=False)
        click_forecourt_key("RECEIPT", timeout, verify=False)
    else:
        click_function_key("SEARCH", timeout, verify=False)
    select_receipt(rcpt_num)
    actual_rcpt = read_receipt()
    ret = True
    for value in values:
        value = value.replace(' ', '')
        # List comprehension to search every line of the receipt while ignoring whitespace
        if not any([value in line.replace(' ', '') for line in actual_rcpt]):
            logger.warning("Did not find %s in the receipt." % value)
            ret = False
    click_receipt_key("CANCEL", verify=False)
    return ret

####################
## Read functions ##
####################

## For reading text from various parts of the POS.
def read_message_box(timeout=default_timeout):
    """
    Read the text of the red popup message on the POS, if it exists.
    Args:
        timeout: (int) The time (in seconds) that the function will look for the window's visibility.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        str: The message in the message box
    Examples:
        >>> read_message_box()
        'Are you sure you want to void the transaction?'
        >>> read_message_box() # While no message box is visible
        None
    """
    try:
        return msg_box.window(auto_id="textBlockError").wait('ready', timeout).texts()[0]
    # If there is no static child, then there is no text inside the message box.
    except Exception as e:
        logger.debug("Failed to read message box. Exception: %s %s" % (str(type(e)), str(e)))
        return None

def read_status_line(timeout=default_timeout):
    """
    Read the status line in the middle of the POS.
    Args:
        timeout: (int) How long to wait for the window to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        str: The current text of the status line
    Examples:
        >>> read_status_line()
        'Press the speed keys to enter items.'
        >>> read_status_line()
        'PRICE CHECK : Please enter the PLU.'
    """
    try:
        return msg_bar['Static3'].wait('ready', timeout).texts()[0]
    except Exception as e:
        logger.warning("Failed to read status line. Exception: %s %s" % (str(type(e)), str(e)))
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
        [['** Begin Transaction **'], ['Generic Item', '99', '$0.01'], ['Cash', '$0.01'], [' ** End Transaction **']]
        >>> read_transaction_journal(2)
        ['Generic Item', '99', '$0.01']
    """
    # Function to clean up journal elements for scripter use
    def process_journal_element(element):
        # Remove first text since it isn't visible in the journal (unless it's a one-text element like Begin Transaction)
        if len(element) > 1:
            element.pop(0)
        # Remove empty texts
        try:
            [element.remove('') for i in range(len(element))]
        except ValueError:
            pass # ValueError will occur after all blanks are removed, this is fine
        return element

    text = []
    try:
        journal_contents = trans_journal.wait('ready', timeout).items()
    except TimeoutError:
        logger.warning("Could not access the transaction journal "
                                    "within %s seconds." % timeout)
        return None

    # Return a single element of the journal
    if element is not None:
        return process_journal_element(journal_contents[element-1].texts())

    # Return the entire journal
    for item in journal_contents:
        text.append(process_journal_element(item.texts()))
    return text

def read_balance(timeout=default_timeout):
    """
    Get the transaction totals: basket count, total, and
    balance/change. Please note that this may not work
    if a list dialog is open (qualifiers, reason codes, etc).
    Args:
        timeout: (int) How long to wait for the window to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        dict: A dictionary mapping each text element to its corresponding
              value.
    Examples:
        >>> read_balance()
        {'Basket Count': '1', 'Total': '$0.01', 'Change': '$0.00'}
        >>> read_balance()
        {'Basket Count': '2', 'Total': '$10.00', 'Balance': '$10.00'}
    """
    # We have to explicitly define balance elements to pick out of the transaction journal window
    balance_strs = ['Basket Count', 'Total', 'Balance', 'Change', 'Refund Due']
    balance_elts = {}
    try:
        trans_elts = trans_window.wait('ready', timeout).children()
    except TimeoutError:
        logger.warning("Could not access the transaction window "
                                    "within %s seconds." % timeout)
        return None
    for i in range(len(trans_elts)):
        texts = trans_elts[i].texts()
        if len(texts) > 0 and texts[0] in balance_strs:
            balance_elts.update({trans_elts[i].texts()[0]: trans_elts[i+1].texts()[0]})
    return balance_elts

def read_suspended_transactions(timeout=default_timeout):
    """
    List the price of each suspended transaction.
    Please note that this may not work if a list
    dialog is open (qualifiers, reason codes, etc).
    Args:
        timeout: (int) How long to wait for the window to be available. 
    Returns:
        list: The price of each suspended transaction as a string.
    Examples:
        >>> read_suspended_transactions()
        ['$10.00', '$0.03']
        >>> read_suspended_transactions()
        []
    """
    susp_trans = []
    try:
        queue_contents = trans_queue.wait('ready', timeout).items()
    except TimeoutError:
        logger.warning("Could not access the transaction queue "
                                    "within %s seconds." % timeout)
        return None
    for item in queue_contents:
        susp_trans.append(item.texts()[1])
    return susp_trans

def read_receipt(timeout=default_timeout):
    """
    Gets the text from a receipt after clicking the Search key.
    Args:
        timeout: (int) How long to wait for the window to be available.
    Returns:
        list: Each line of the receipt, MINUS duplicates (they don't show up in the actual control)
    Examples:
        >>> read_receipt()
        ['                 Header                 ', '', 'Store Name,  299', 'asdfdsaf',
         'a, a  a', '                      ', '          03/01/2019 2:30:25 PM', '    Re
        gister: 1 Trans #: 64 Op ID: 91', '            Your cashier: Area', ' *** REPRIN
        T *** REPRINT *** REPRINT ***', 'Generic Item                     $0.01  99', '
                                   ----------    ', '                   Subtotal =    $0
        .01    ', '                       Tax  =    $0.00    ', '                      T
        otal =    $0.01    ', '                Change Due  =    $0.00    ', 'Cash
                              $0.01    ', '                 Footer                 ']
    """
    movement = 60
    try:
        receipt_search.ListBox.wait("ready", timeout)
    except TimeoutError:
        logger.warning("Couldn't access the receipt window "
                                    "within %s seconds.")
        return None
    receipt_search.ListBox.click_input()
    send_keys("{HOME}")
    send_keys("{DOWN %d}"%(movement))
    texts = receipt_search.ListBox.texts()
    result = []
    for line in texts:
        for txt in line:
            result.append(txt)
    return result

def read_keypad_entry(timeout=default_timeout):
    """
    Read the current entry in the text field above the keypad.
    Args:
        timeout: (int) How long to wait for the window to be available.
    Returns:
        str: The contents of the field.
    Examples:
        >>> read_keypad_entry()
        '1234'
        >>> read_keypad_entry()
        ''
    """
    start_time = time.time()
    while time.time() - start_time <= timeout:
        try:
            return keypad_entry.children()[0].texts()[0]
        except:
            continue
    else:
        logger.warning("Unable to connect to the keypad entry window within %d seconds." % timeout)
        return None

def read_dispenser_diag(timeout=default_timeout):
    """
    Read the diag lines for a dispenser.
    Args:
        timeout: (int) How many seconds to wait for the diag text to appear.
    Returns:
        dict: Each item in the dispenser diag.
    Example:
        >>> read_dispenser_diag()
        {'DISPENSER': 'IDLE', 'STATUS': 'OK', 'CRIND': 'IDLE', 'PRINTER': 'OK', 'DOOR/BILLS': 'OK'}
    """
    start_time = time.time()
    while time.time() - start_time <= timeout:
        status = {}
        status_lines = []
        success = True
        try:
            for i in range(1,6):
                status_lines.append(dispenser['DispDiagItemListItem' + str(i)].texts())
        except (ElementNotFoundError, COMError) as e:
            logger.debug(f"[read_dispenser_diag] Got {type(e).__name__}. Text probably updated while we tried to read it. Retrying.")
            continue
        for i in range(5):
            status_line = status_lines[i]
            if status_line[0] == '' or len(status_line) < 2:
                success = False
                break
            status.update({status_line[0].replace(':', ''): status_line[1]})
        if success:
            break
    else:
        logger.warning(f"Unable to find dispenser diag info within {timeout} seconds.")
        return None
    return status

def read_fuel_buffer(buffer_id='A', timeout=default_timeout):
    """
    Get the current contents of a fuel buffer.
    Args:
        buffer_id: (char) Letter of the buffer to read.
        timeout: (int) How many seconds to wait for the fuel buffer to be readable.
    Returns:
        list: The text contents of the buffer. In order:
              buffer status, amount dispensed (if fueling in progress),
              total amount, total volume, PPU, grade
    Examples:
        >>> read_fuel_buffer()
        ['EMPTY', ' ', None, None, None, None]
        >>> read_fuel_buffer('B')
        ['BUSY', '$9.77', None, None, None, None]
        >>> read_fuel_buffer()
        ['FUEL SALE', '', '$10.93', '7.290 GAL', '$1.499', 'REG']

    """
    try:
        dispenser['Edit1'].wait('ready', timeout)
    except TimeoutError:
        logger.warning(f"Couldn't access the fuel buffer within {timeout} seconds.")
        return None
    edits_to_read = []
    try:
        a_has_postpay = (dispenser['Edit7'].texts()[0] != 'B')
    except Exception as e:
        logger.warning("read_fuel_buffer: %s" % e)
        return None
    if buffer_id.upper() == 'A':
        edits_to_read.extend((1,4))
        if a_has_postpay:
            edits_to_read.extend(range(5, 9))
    elif buffer_id.upper() == 'B':
        if not a_has_postpay:
            edits_to_read.extend((5, 8))
            try:
                dispenser['Edit10'].texts()
                edits_to_read.extend(range(9, 13))
            except ElementAmbiguousError:
                pass
        else:
            edits_to_read.extend((9, 12))
            try:
                dispenser['Edit13'].texts()[0]
                edits_to_read.extend(range(13, 17))
            except ElementAmbiguousError:
                pass
    else:
        logger.warning("Invalid buffer name, please specify A or B.")
        return None
    buffer_contents = []
    # These repeated edit reads are slow. Can we do it faster somehow?
    for edit_id in edits_to_read:
            buffer_contents.append(dispenser['Edit%d' % edit_id].texts()[0])
    # Ensure consistent return length between complete/non-complete sale
    if len(buffer_contents) < 6:
        for _ in range(len(buffer_contents), 6):
            buffer_contents.append(None)
    return buffer_contents

def read_local_subaccount_list(sub_account_id=None, timeout=default_timeout):
    """
    Get the list of subaccounts from the local account selection window.
    Args:
        sub_account_id: (str) Optional Sub Account ID to return else return entire list.
        timeout: (int) How long to wait for the window to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        list: The text contents either single item or multiple items.
    Examples:
        >>> read_local_subaccount_list()
        [['00000000000', '123456', 'SUBACCOUNT 1'], ['00000000001', '222222', 'SECOND SU
        BACCOUNT'], ['00000000002', '9832741984', 'ANOTHER SUBACCOUNT']]
        >>> read_local_subaccount_list('00000000001')
        ['00000000001', '222222', 'SECOND SUBACCOUNT']
    """
    try:
        loc_sub_acc_data = loc_acc_selection_window['ListView2'].wait('ready', timeout)
    except TimeoutError:
        logger.warning("Could not access the local sub account datas "
                                    "within %s seconds." % timeout)
        return False

    if sub_account_id == None:
        return loc_sub_acc_data.texts()
    else:
        for item in loc_sub_acc_data.items():
            if sub_account_id in item.texts()[0]:
                return item.texts()
        logger.warning("Could not find the local sub account %s "
                                    "in local sub account listview window." %sub_account_id)
        return False

def read_local_account_details(timeout=default_timeout):
    """
    Get the text of the local account details pop-up window.
    Args:
        timeout: (int) How long to wait for the window to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        list: The text contents of the detail window.
    Examples:
        >>> read_local_account_details()
        {'Account ID': '1', 'Account Name': 'asdf', 'Sub-Account ID': '00000000000', 'De
        scription': 'Subaccount 1', 'Status': 'Enabled', 'Vehicle ID': '123456', 'Accoun
        t Balance': '$0.00', 'Account Credit Limit': '$100.00'}
        >>> read_local_account_details()['Vehicle ID']
        '123456'
    """
    start_time = time.time()
    last_e = None
    while time.time() - start_time <= timeout:
        try:
            for child in loc_acc_detail_window.children():
                if child.friendly_class_name() == 'Static' and 'Account ID' in child.texts()[0]:
                    texts = child.texts()[0].split('\n')
                    texts.remove('')
                    ret = {}
                    for text in texts:
                        split = text.split(': ')
                        ret.update({split[0]: split[1]})
                    return ret
        except Exception as e:
            last_e = e
    logger.warning("Failed to read the local account detail window. Last exception msg: %s" % last_e)
    return False

def read_reminder_box(timeout=default_timeout):
    """
    Read the text from the reminder pop-up.
    Args:
        timeout: (int) How long to wait for the window to be available.
    Returns:
        str: The text of the reminder, or False if no reminder is visible
    Examples:
        >>> read_reminder_box()
        'DON'T FORGET TO DO THE THING'
        >>> read_reminder_box()
        None
    """
    start_time = time.time()
    while time.time() - start_time <= timeout:
        try:
            return reminder_window.window(
                auto_id="textBlockReminder").wait('ready', timeout).texts()[0]
        except Exception as e:
            logger.warning(e)
    return None

def read_date(timeout=default_timeout):
    """
    Read the date from the POS status line.
    Args:
        timeout: (int) How long to wait for the status line to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        str: The date displayed on the status line
    Examples:
        >>> read_date()
        '03/01/2019'
    """
    try:
        return msg_bar['Static1'].wait('ready',timeout).texts()[0]
    except Exception as e:
        logger.warning("get_date: %s" % e)
    return None

def read_time(timeout=default_timeout):
    """
    Read the time from the POS status line.
    Args:
        timeout (int): How long to wait for the status line to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        str: The time displayed on the status line
    Examples:
        >>> read_time()
        '03:10 PM'
    """
    try:
        return msg_bar['Static2'].wait('ready',timeout).texts()[0].strip()
    except Exception as e:
        logger.warning("get_time: %s" % e)
    return None

def read_info(timeout=default_timeout):
    """
    Read the text information on the POS Info screen.
    Args:
        timeout: (int) How long to wait for the window to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        (dict) The text contents of the info screen. (NOT green/red status indicators)
    Examples:
        >>> read_info()
        {'Register Status': 'Register Open', 'Operator': '91 Area Manager', 'Till ID': '
        000000000070', 'Business Date': '01/30/2019 9:37:54 AM', 'Period Number': '1', '
        Register ID': '1', 'Register Group': 'POSGroup1', 'Store ID': '299', 'Store Phon
        e': '(123)456-7890', 'Help Desk Phone': '(222)222-2222', 'Passport Version': '99
        .99.23.01_DB181231 CONCORD', 'OS Hotfix Version:': '66.9.07', 'Gilbarco Model No
        .': '', 'Gilbarco Serial No.': '', 'NTEP CC No. 02-039': ''}
    """
    status = {}
    pair = []
    start_time = time.time()
    while time.time() - start_time <= timeout:
        try:
            for child in info_window.children():
                if (child.friendly_class_name() == 'Static'
                    and child.texts()[0].lower() != "status"):
                    pair.append(child.texts()[0])
                    if len(pair) == 2:
                        status.update({pair[0]: pair[1]})
                        pair = []
            return status
        except Exception as e:
            logger.warning(e)
    return None

def read_hardware_status(timeout=default_timeout):
    """
    Read the status indicators on the Info window
    by checking colors.
    Args:
        timeout: (int) How long to wait for the window to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        dict: A map of each status indicator's name to its status. True for green, False for red.
    Examples:
        >>> read_hardware_status()
        {'Online': True, 'Printer': False, 'Cash Drawer': True, 'Scanner': True, 'Car Wa
        sh': False, 'Display': False, 'MSR': False, 'RFID': False, 'Price Sign': True}
        >>> read_hardware_status()['Cash Drawer']
        True
    """

    # Here, the keys are placed before the name and hence the desired key will be
    # identified with the previous label. So, to avoid the name conflict the following
    # dictionary is used.
    controls = {
        "Online":"Status", "Printer":"Online", "Cash Drawer":"Printer"
        ,"Scanner":"Cash Drawer", "Car Wash":"Scanner", "Display":"Car Wash"
        ,"MSR":"Display", "RFID":"MSR", "Price Sign":"RFID"
        }

    try:
        info_window.wait('ready', timeout)
    except:
        logger.warning(f'Info window not found within {timeout} seconds.')  

    send_keys("{PRTSC}")
    img = ImageGrab.grabclipboard()
    img = img.convert('RGB')
    ret = {}
    for item in controls:
        control = info_window[controls[item]+"button"]
        control_position = control.rectangle()
        key_image = img.crop((control_position.left,
                            control_position.top,
                            control_position.right,
                            control_position.bottom))

        grnR, grnG, grnB = key_image.getpixel((30,10))
        redR, redG, redB = key_image.getpixel((50,10))

        if grnG > 250:
            ret.update({item: True})
        elif redR > 250:
            ret.update({item: False})
        else:
            print("Couldn't find the pixel for key: %s" % item)
            ret.update({item: None})

    return ret

##################################
## Misc. click/select functions ##
##################################

# For clicking things other than POS keys.

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
        True
        >>> click_journal_item("NotInTheJournal")
        False
    """
    i = 1
    try:
        journal_contents = trans_journal.wait('ready', timeout).items()
    except TimeoutError:
        logger.warning("Could not access the transaction journal "
                                    "within %s seconds." % timeout)
        return False
    for line in journal_contents:
        if item is None or item in line.texts():
            if i >= instance:
                line.click_input()
                return True
            else:
                i += 1
    return False

@test_func
def click_suspended_transaction(price=None, instance=1, timeout=default_timeout):
    """
    Select a suspended transaction. Please not that this may
    not work if a list dialog is open (qualifiers, restrictions,
    etc.)
    Args:
        item: (str) The price of the transaction to resume, i.e. $0.01
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
    i = 1
    ret = True
    start_time = time.time()
    while time.time() - start_time <= timeout:
        try:
            queue_contents = trans_queue.items()
        except:
            ret = None
            continue
        for item in queue_contents:
            if price is None or price in item.texts():
                if i >= instance:
                    logger.debug("Found %s" %(item.texts()[0]))
                    item.select()
                    return 1
                else:
                    i += 1
                    ret = False
    return ret

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
    try:
        items = receipt_search["ListView"].wait("ready", timeout).items()
    except TimeoutError:
        logger.warning("Couldn't access the receipt list "
              "within %s seconds." % timeout)
        return False
    if num == -1: # last one.
        num = len(items)
    elif num < 1 or num-1 > len(items):
        return False

    try:
        items[num-1].select()
    except IndexError:
        logger.error("Receipt number provided falls out of range of available receipts")
        return False
    return True

@test_func
def select_list_item(list_item, timeout=default_timeout):
    """
    Select an item from a list prompt, such as qualifiers or reason codes.
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
    try:
        list_window[list_item].wait('ready', timeout).select()
    except TimeoutError:
        logger.warning("Could not access the list item '%s' "
                                    "within %s seconds." % (list_item, timeout))
        return False
    return True

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
    try:
        dispenser['ListBox'].items()[disp_num-1].click_input()
        return True
    except Exception as e:
        logger.warning("select_dispenser: %s" % e)
        return False

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
    # Select the local account
    try:
        loc_acc_data = loc_acc_selection_window['ListView1'].wait('ready', timeout)
    except TimeoutError:
        logger.warning("Could not access the local account datas "
                                    "within %s seconds." % timeout)
        return False

    for item in loc_acc_data.items():
        if account in item.texts():
            item.select()
            break
    else:
        logger.warning("Could not find the local account %s "
              "in local account listview window." %account)
        return False

    # Select the sub-account, if specified
    if sub_account is not None:
        try:
            loc_sub_acc_data = loc_acc_selection_window['ListView2'].wait('ready', timeout)
        except TimeoutError:
            logger.warning("Could not access the local sub account datas "
                  "within %s seconds." % timeout)
        for item in loc_sub_acc_data.items():
            if sub_account in item.texts():
                item.select()
                return True
        else:
            logger.warning("Could not find the local sub account %s "
                  "in local sub account listview window." %sub_account)
    else:
        return True

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
    if buffer_id == 'A':
        try:
            dispenser['Edit1'].wait('ready',timeout).click_input()
            return True
        except Exception as e:
            logger.warning("select_fuel_buffer: %s" % e)
            return False
    elif buffer_id == 'B':
        # Control ID for buffer B changes if A has a postpay
        try:
            a_has_postpay = (dispenser['Edit7'].wait('ready', timeout).
                                texts()[0] != 'B')
        except Exception as e:
            logger.warning("select_fuel_buffer: %s" % e)
            return False       
        if a_has_postpay:
            edit_num = 9
        else:
            edit_num = 5
        try:
            # We already know buffer controls are ready, no need for wait here
            dispenser['Edit%d' % edit_num].click_input()
            return True
        except Exception as e:
            logger.warning("select_fuel_buffer: %s" % e)
            return False

#################
## Sign on/off ##
#################

# All-in-on sign on/sign off functions, plus their helpers.
@test_func
def sign_off(user_id=None):
    """
    Signs the defined user off and follows the scenarios according to the parameters. Until a POS
    navigator is built, this is assuming that the user is on the POS main page after a sign on.
    Args:
        user_id: (str) The id of the user that is signing off of the POS.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> sign_off()
        True
        >>> sign_off('91')
        True
        >>> sign_off('9821379748198347143')
        False
    """
    if user_id is None:
        try:
            with open(json_path) as creds_file:
                json_creds = json.load(creds_file) # Check for existing credentials
                user_id = json_creds['ID']
        except: # Nonexistent or empty credentials file
            user_id = '91'
    if type(user_id) != str:
        logger.warning("The user id %s is not a string." % (user_id))
        user_id = str(user_id)
    click_function_key('sign off', verify=False)
    for char in user_id:
        click_keypad(char, verify=False)
    click_keypad('enter', verify=False)
    if read_status_line().lower() != "please sign on.":
        logger.warning("Something went wrong, user did not "
                                    "properly sign off.")
        return False
    logger.debug("Sign off successful.")
    return True

@test_func
def sign_on(user_credentials=None, till_amount=None, reason=None):
    '''
    Smart sign-on function. Covers most typical scenarios encountered when signing on.
    Args:
        user_credentials: (tuple) The users sign on credentials (username, password)
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        True if success, False if failure
    Examples:
        >>> sign_on()
        True
        >>> sign_on(('91', '91'))
        True
        >>> sign_on(('123', 'TheWrongPassword'))
        False
    '''
    if is_signed_on():
        logger.debug("Already signed on to POS.")
        return True
        
    import time
    start_time = time.time()
    global credentials
    json_creds = {}
    if user_credentials != None:
        credentials = user_credentials
    else:
        try:
            with open(json_path) as creds_file:
                json_creds = json.load(creds_file) # Check for existing credentials
                credentials = [json_creds['ID'], json_creds['Password']]
        except: # Nonexistent or empty credentials file
            credentials = ['91', '91']

    operations ={'Please sign on.': sign_in,
                 'Please enter your operator number.': enter_operator_num,
                 'Enter Operator ID.': enter_operator_num,
                 'Please enter your password.': enter_pw,
                 'Do you want to start a new till?': start_till,
                 'Please enter pouch/envelope number.': enter_envelope_num,
                 'Please enter your opening balance.': opening_balance,
                 'You have entered an invalid password.': invalid_password,
                 'Your password must be changed.  Please enter a new password.': new_password,
                 'You are not clocked in.  Please clock in.': clock_in,
                 'Please select a valid reason and press enter.': enter_reason,
                 'Press the speed keys to enter items.': None,
                 'Please enter the department items.': None,
                 'Transaction voided.': None,
                 'Car Wash is offline.': sign_in,
                 'has locked the register': unlock,
                 #TODO: Make this click ok
                 'Your cash drawer WILL NOT OPEN until the printer is working.': None}
    args_to_pass = { 'Please enter your opening balance.': [till_amount],
                     'Please select a valid reason and press enter.': [reason] }

    # Use status line prompts to decide what to do until successfully signed on, or timed out
    while time.time() - start_time <= 90:
        temp_level = logger.getEffectiveLevel()
        logger.setLevel(999)
        msg = read_message_box(timeout = .5)
        logger.setLevel(temp_level)
        if msg == None:
            msg = read_status_line()

        for key, value in operations.items():
            if key in msg:
                operation = value
                break
        else:
            logger.warning("Unsupported sign on operation: %s" % msg)
            continue
            
        for key, value in args_to_pass.items():
            if key in msg:
                args = value
        else:
            args = [] # No args

        if operation is None:
            logger.debug('Log in ended successfully.')
            #Creating last user logged in JSON file
            with open(json_path, 'w+') as creds_file:
                json_creds['ID'] = credentials[0]
                json_creds['Password'] = credentials[1]
                json.dump(json_creds, creds_file)
            return True
        try:
            logger.debug('Starting ' + operation.__name__)
            operation(*args)
        except:
            logger.warning('Failure in %s' % operation.__name__)
            raise POSException('Failure in %s' % operation.__name__)

    raise POSException('Unable to sign on to the pos.')

def sign_in():
    """Click sign on"""
    try:
        func_keys['SIGN ON'].click()
    except:
        return False
    if BRAND.upper() == "EXXON":
        window['Dialog0']['Pane1'].wait('exists', 10).click_input() # Accept disclaimer

    return True

def unlock():
    """Handle locked register prompt for sign_on"""
    return click_function_key("UNLOCK")

def invalid_password():
    '''
    Handles the invalid password prompt for sign_on_pos
    @Creator: Bryan Grant
    '''
    try:
        click_message_box_key("Ok", verify=False)
        sign_in()
        enter_operator_num(credentials)
        enter_pw((credentials[0], '1234567'))
    except:
        raise POSException('sign on failed.')

def clock_in():
    '''
    Handles the clockin prompt for sign_on_pos
    @Creator: Bryan Grant
    '''
    try:
        click_message_box_key("Ok", verify=False)
        click_function_key(key = 'TIME CLOCK', timeout = 2, verify=False)
        if read_message_box(timeout = 1) != None:
                click_message_box_key("Yes")
    except:
        raise POSException('Clock in failed.')

def enter_reason(reason=None):
    '''
    Handles the clock in reason code for sign_on_pos
    @Creator: Bryan Grant
    '''
    if reason is not None and not select_list_item(reason):
        raise POSException("Enter reason code failed, couldn't find {reason}.")
    try:
        click_keypad("ENTER",2, verify=False)
        if read_message_box(timeout = 1) != None:
                click_message_box_key("Yes", verify=False)
    except:
        raise POSException('Enter reason code failed.')


def new_password():
    '''
    Handles the new password sequence for sign_on_pos
    @Creator: Bryan Grant
    '''
    try:
        click_message_box_key('Ok', verify=False)
        enter_pw()
        enter_pw()
    except:
        raise POSException('new password failed.')

def enter_operator_num(user_credentials = None):
    '''
    Handles the operator number prompt for sign_on_pos
    Args:
        user_credentials: (List/tuple) The users sign on credentials
    @Creator: Bryan Grant
    '''
    if user_credentials == None:
        operator_num = credentials[0]
    else:
        operator_num = user_credentials[0]

    try:
        for char in operator_num:
            click_keypad(char, verify=False)
        click_keypad('enter', verify=False)
    except:
        logger.warning('Inputting operator number failed.')
        raise POSException('Inputting operator number failed.')

def enter_pw(user_credentials = None):
    '''
    Handles entering the password for sign_on_pos
    Args:
        user_credentials: (List/tuple) The users sign on credentials
    @Creator: Bryan Grant
    '''
    if user_credentials == None:
        password = credentials[1]
    else:
        password = user_credentials[1]

    try:
        for char in password:
            click_pwd_key(char, verify=False)
        click_pwd_key('ok', verify=False)
    except:
        logger.warning('Inputting user password failed.')
        raise POSException('Inputting user password failed.')

def start_till(response = None):
    '''
    Handles starting a new till for sign_on_pos
    Args:
        response: (str) The response expected at the open till prompt
    @Creator: Bryan Grant
    '''
    try:
        if response == None:
            click_message_box_key("Yes", verify=False)
        else:
            click_message_box_key(response, verify=False)
    except:
        logger.warning('Starting new till failed.')
        raise POSException('Starting new till failed.')

def enter_envelope_num(envelope_num = None):
    '''
    Handles entering the envelope number for sign_on_pos
    Args:
        envelope_num: (int) Envelope number
    @Creator: Bryan Grant
    '''
    try:
        if envelope_num == None:
            click_keypad("Enter", verify=False)
        else:
            for char in envelope_num:
                click_keypad(char, verify=False)
            click_keypad("Enter", verify=False)
    except:
        logger.warning('Entering envelope number failed.')
        raise POSException('Entering envelope number failed.')

def opening_balance(balance = None):
    '''
    Handles entering the opening balance for sign_on_pos
    Args:
        balance: (int) Opening balance
    @Creator: Bryan Grant
    '''
    try:
        if balance != None:
            for char in balance:
                click_keypad(char, verify=False)
            click_keypad("+", verify=False)
            click_keypad("FINALIZE", verify=False)
        else:
            click_keypad("FINALIZE", timeout = 2, verify=False)
    except:
        logger.warning('Entering opening balance failed.')
        raise POSException('Entering opening balance failed.')

def is_signed_on():
    """
    Tries to determine if we are signed on to the POS by checking if SIGN ON/UNLOCK
    keys are present. May give a bad result if we are signed off and in a submenu.
    """
    try:
        func_keys['SIGN ON'].wait('ready')
    except:
        try:
            func_keys['BACK'].click()
            func_keys['SIGN ON'].wait('ready')
        except:
            try:
                func_keys['UNLOCK'].wait('ready')
            except:
                try:
                    func_keys['BACK'].click()
                    func_keys['UNLOCK'].wait('ready')
                except:
                    return True
    return False

############################
## Click helper functions ##
############################

## These are mainly helpers for click(). Only use them if click() absolutely won't work for some reason.
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
    # Wait for func keys to exist
    try:
        func_keys.wait('ready', timeout)
    except TimeoutError:
        logger.warning("Func keys not ready within %s seconds." % timeout)
        return False

    if msg_box.window(auto_id='textBlockError').exists():
        logger.warning("A message box is open. Func keys won't work.")
        return False

    temp_level = logger.getEffectiveLevel()
    logger.setLevel(999)
    if not click_key(func_keys, key, 1):
        i = 0
        # Navigate forward through pages to try and find the key
        while i < 2 and click_key(func_keys, 'MORE', 1):
            if click_key(func_keys, key, 1):
                logger.setLevel(temp_level)
                return True
            i += 1
        i = 0
        # Navigate backward
        while i < 2 and click_key(func_keys, 'BACK', 1):
            if click_key(func_keys, key, 1):
                logger.setLevel(temp_level)
                return True
            i += 1
    else:
        logger.setLevel(temp_level)
        return True
    logger.setLevel(temp_level)
    return False     

@test_func
def click_till_key(key, timeout=default_timeout):
    """
    Click a key in the POS till window.
    Args:
        key: (str) The key that will be clicked. 
        timeout: (int) How long to wait for the window to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> click_till_key("FINALIZE")
        True
        >>> click_till_key("REFUND")
        False
    """
    return click_key(till_keypad, key, timeout)

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
        >>> click_tender_key("CHECK")
        True
        >>> click_tender_key("NotATender")
        False
    """
    if key.lower() == "exact change":
        try:
            tender_keys.window(auto_id="buttonPreset4").wait('ready',timeout).click()
            return True
        except Exception as e:
            logger.warning("Failed to click %s.%s. Exception: %s %s"
                                        % (tender_keys.texts()[0], key, str(type(e)), str(e)))
            return False
    else:
        return click_key(tender_keys, key, timeout)

@test_func
def click_speed_key(key, timeout=default_timeout, case_sens=False):
    """
    Click on a speed key. Switches to speed keys if POS is in dept key mode.              
    Args:
        key: (str) The text of the speed key to click on.
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
    start_time = time.time()
    while time.time() - start_time <= timeout:
        try:
           speedkey.wait('exists', 2)
        except:
            if not click_function_key("SPEED KEY", timeout=0, verify=False):
                logger.warning("Unable to open speed keys.")
                return False
        speedkey.wait('exists', 2)
        if click_key(speedkey, key, 0, case_sens):
            return True
        else:
            key_15 = speedkey.children()[15]
            key_14 = speedkey.children()[14]
            while key_15.is_visible() and key_15.texts() == ['MORE']:
                key_15.click()
                if click_key(speedkey, key, 0, case_sens, False):
                    return True
            else:
                while key_14.is_visible() and key_14.texts() == ['BACK']:
                    key_14.click()
                    if click_key(speedkey, key, 0, case_sens, False):
                        return True
    else:
        logger.warning(f"Couldn't click the speed key {key}.")
        return False

@test_func
def click_dept_key(key, timeout=default_timeout, case_sens=False):
    """
    Click on a department key. Switches to dept keys if POS is in speed key mode.
    Args:
        key: (str) The text of the dept key to click on.
        timeout: (int) How long to wait for the window to be available.
        case_sens (bool): Whether to use a case sensitive search.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> click_dept_key("Dept 8")
        True
        >>> click_dept_key("Not A Dept")
        False
    """
    start_time = time.time()
    while time.time() - start_time <= timeout:
        try:
            dept_key.wait('exists', 2)
        except TimeoutError:
            if not click_function_key("DEPT KEY", timeout=0, verify=False):
                logger.warning("Unable to open dept keys.")
                return False
        try:
            dept_key.wait('exists', 5)
        except TimeoutError:
            logger.warning("Dept keys did not open within 5 seconds after clicking Dept Keys button.")
            return False
        if click_key(dept_key, key, 1, case_sens):
            return True
        else:
            key_15 = dept_key.children()[15]
            key_14 = dept_key.children()[14]
            while key_15.is_visible() and key_15.texts() == ['MORE']:
                key_15.click()
                if click_key(dept_key, key, 0, case_sens, False):
                    return True
            else:
                while key_14.is_visible() and key_14.texts() == ['BACK']:
                    key_14.click()
                    if click_key(dept_key, key, 0, case_sens, False):
                        return True
    else:
        logger.warning(f"Couldn't click the department key {key}.")
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
    return click_key(msg_box, key, timeout)

@test_func
def click_status_line_key(key, timeout=default_timeout):
    """
    Click the key entered by the user on the status line (aka yellow message bar)
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
    return click_key(msg_bar, key, timeout)

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
        >>> click_receipt_key("SEARCH")
        True
        >>> click_receipt_key("hello")
        False
    """
    return click_key(receipt_search, key, timeout)

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
    valid_keypad = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '00', 'CLR']
    if type(key) is int:
        key = str(key)
    # Note: menus that come later in these lists will be slower to click.
    if key in valid_keypad:
        windows_to_try = [keypad, pwd_keys, restr_window, attendant]
    else:
        windows_to_try = [keypad_cmd, till_keypad, pwd_keys, restr_window, attendant]

    # Try each possible menu until success
    start_time = time.time()
    temp_level = logger.getEffectiveLevel()
    logger.setLevel(999)
    while time.time() - start_time <= timeout:
        for window in windows_to_try:
            if click_key(window, key, 0, click_input=window is restr_window):
                logger.setLevel(temp_level)
                return True
    else:
        logger.setLevel(temp_level)
        logger.warning("Unable to click keypad key %s." % key)
        return False
@test_func
def click_pwd_key(key, timeout=default_timeout):
    """
    Click a key in the password entry keyboard.
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
    return click_key(pwd_keys, key, timeout)

@test_func
def click_restriction_keypad(key, timeout=default_timeout):
    """
    Click a key in the restriction/age verification window.
    Args:
        key: (int/str) The keypad key that will be clicked.
             Must be for a single key.
        timeout: (int) How long to wait for the window to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> click_restriction_keypad("MANUAL")
        True
        >>> click_restriction_keypad("jkl;")
        False
    """
    valid_keypad = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'CLR',
                    'CANCEL', 'ENTER', 'MANUAL']
    if str(key).upper() not in valid_keypad:
        logger.warning("%s is not a valid keypad key.")
        return False

    # Use click input if clicking a number key, because click throws a COMError for some reason
    try:
        int(key)
        click_input = True
    except ValueError:
        click_input = False

    return click_key(restr_window, key, timeout, click_input)

@test_func            
def click_restriction_key(key, timeout=default_timeout):
    """
    Click a key in the restriction (age verification) window.
    Args:
        key: (str) Text describing the key to click. For calendar date keys, provide
                the full date, i.e. 'Thursday, August 03, 2017'. For calendar month keys,
                provide the unabbreviated month name. For calendar arrow keys, use "previous"
                and "next".
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
    keys = ['DENY', 'DEFAULT', 'CANCEL', 'ENTER']
    radios = ['1 january', '2 february', '3 march', '4 april', '5 may',
                '6 june', '7 july', '8 august', '9 september', '10 october',
                '11 november', '12 december']
    #arrows = ['previous', 'next']
    try:
        if key.upper() in keys:
            return click_key(restr_window, key, timeout)
        elif key.lower() in radios:
            restr_window['%sRadio' % key].wait('visible', timeout).select()
        # These auto IDs don't seem to exist anymore
        #elif key.lower() in arrows:
        #    restr_window.window(auto_id="PART_%sButton" % key).wait('visible', timeout).click_input()
        else:
            restr_window[key].wait('visible', timeout).click_input()
    except Exception as e:
        logger.warning("Failed to click RestrictionWindow.%s. Exception: %s %s"
                                        % (key, str(type(e)), str(e)))
        return False
    return True

@test_func
def click_tools_key(key, timeout=default_timeout):
    """
    Click a key in the Tools sub-menu.
    Args:
        key: (str) The key that will be clicked.
        timeout: (int) How long to wait for the window to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> click_tools_key("STORE CLOSE")
        True
        >>> click_tools_key("jkl;")
        False
    """
    if key.upper() == "SHIFT CLOSE":
        key = "SHIFT  CLOSE" # Back end text doesn't match front end
    return click_key(pos_admin_keys, key, timeout)

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
        >>> click_forecourt_key("asdf")
        False
    """
    try:
        # All stop/clear stop don't have any text on the back end
        if key.upper() == 'ALL STOP':
            dispenser.window(auto_id='allStopButton').wait('ready', timeout).click()
        elif key.upper() == 'CLEAR STOP':
            dispenser.window(auto_id='clearAllStopButton').wait('ready', timeout).click()
        else:
            return click_key(dispenser, key, timeout)
        return True
    except Exception as e:
        logger.warning("click_forecourt_key: %s" % e)
        return False

@test_func
def click_prepay_key(key, timeout=default_timeout):
    """
    Click a key in the POS prepay window.
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
        True
        >>> click_prepay_key("$-5.00")
        False
    """
    # Money options and grade options are two separate windows; figure out which one the
    # requested key probably lives in and try it first
    if re.match(r"^\$\d{1,2}.\d\d$", key) or key.upper() == "BALANCE": # Regex matches the dollar amount keys
        windows = [prepay_keys, prepay_grades]
    else:
        windows = [prepay_grades, prepay_keys]

    # Try both possible windows
    start_time = time.time()
    temp_level = logger.getEffectiveLevel()
    logger.setLevel(999)
    while time.time() - start_time <= timeout:
        for window in windows:
            if click_key(window, key, 0):
                logger.setLevel(temp_level)
                return True
    else:
        logger.setLevel(temp_level)
        logger.warning("Unable to click %s within %d seconds." % (key, timeout))
        return False

@test_func
def click_preset_key(key, timeout=default_timeout):
    """
    Click a key in the POS preset window.
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
    # Special case because frontend text doesn't match backend
    if key.upper() == "CASH LEVEL":
        key = "CASH  LEVEL" # This is the actual text of the key on the backend

    # Money options and grade options are two separate windows; figure out which one the
    # requested key probably lives in and try it first
    if re.match(r"^\$\d{1,2}.\d\d$", key) or key.upper() == "CASH  LEVEL" or key.upper() == "CREDIT LEVEL":
        windows = [preset_keys, preset_grades]
    else:
        windows = [preset_grades, preset_keys]

    # Try both possible windows
    start_time = time.time()
    temp_level = logger.getEffectiveLevel()
    logger.setLevel(999)
    while time.time() - start_time <= timeout:
        for window in windows:
            if click_key(window, key, 0):
                logger.setLevel(temp_level)
                return True
    else:
        logger.setLevel(temp_level)
        logger.warning("Unable to click %s within %d seconds." % (key, timeout))
        return False

@test_func
def click_local_account_key(key, timeout=default_timeout):
    """
    Click a key in the local account selection window.
    Args:
        key: (str) The key that will be clicked.
        timeout: (int) How long to wait for the window to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> click_local_account_key("DETAILS")
        True
        >>> click_local_account_key("YES")
        False
    """
    return click_key(loc_acc_selection_window, key, timeout)

@test_func
def click_local_account_details_key(key, timeout=default_timeout):
    """
    Click a key in the local account details pop-up window.
    Args:
        key: (str) The key that will be clicked.
        timeout: (int) How long to wait for the window to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> click_local_account_details_key("OK")
        True
        >>> click_local_account_details_key("LiterallyAnythingThatIsntOK")
        False
    """
    return click_key(loc_acc_detail_window, key, timeout)

@test_func
def click_reminder_box_key(key, timeout=default_timeout):
    """
    Click a key in the reminder pop-up.
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
    return click_key(reminder_window, key, timeout)

@test_func
def click_info_key(key, timeout=default_timeout):
    """
    Click a key in the Info window.
    Args:
        key: (str) The key to be clicked.
        timeout: (int) How long to wait for the window to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> click_info_key("Cancel")
        True
        >>> click_info_key("LiterallyAnythingButCancel")
        False
    """
    start_time = time.time()
    while time.time() - start_time <= timeout:
        try:
            for child in info_window.children():
                if child.friendly_class_name() == 'Button':
                    if child.children_texts()[0].lower() == key.lower():
                        child.click()
                        return True
        except Exception as e:
            logger.warning(e)
    logger.warning("Couldn't find the key: %s" % key)
    return False

@test_func
def click_dispenser_key(key, timeout=default_timeout):
    """
    Click a key in the Dispenser menu (not the forecourt GUI).
    Args:
        key: (str) The text of the key to click
        timeout: (int) How long to wait for the window to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> click_dispenser_key("ATTENDED OPTIONS")
        True
        >>> click_dispenser_key("asdf")
        False
    """
    # Special cases for mismatched front/back end text
    if key.upper() == "TEST FUEL":
        key = ""
    if key.upper() == "ATTENDED OPTIONS":
        key = "ATTENDANT OPTIONS"
    return click_key(dispenser_menu, key, timeout)

@test_func
def click_attendant_key(key, timeout=default_timeout):
    """
    Click a key in the Dispenser  Attended Options sub-menu.
    This works for everything in this sub-menu EXCEPT for password entry.
    Use click_pwd_key for that.
    Args:
        key: (str) The text of the key to click. Use dispN to click
             dispenser N for attendant assignment.
        timeout: (int) How long to wait for the window to be available.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns:
        bool: True if success, False if failure
    Example:
        >>> click_attendant_key("ACTIVATE TOKEN")
        True
        >>> click_attendant_key("jkl;")
        False
    """
    # Buttons don't have text on the backend, so we need a map of automation IDs
    autoid_map = {
        "ASSIGN DISPENSER": "btnAssignDispenser",
        "ACTIVATE TOKEN": "btnActivateToken",
        "SAFE DROP": "btnSafeDrop",
        "CLOSE TILL": "btnCloseTill",
        "GO BACK": "btnGoBack"
    }
    if key.upper() in autoid_map:
        try:
            attendant.window(auto_id=autoid_map[key.upper()]).wait('ready', timeout).click()
            return True
        except Exception as e:
            logger.warning("Failed to click Attendant.%s. Exception: %s %s"
                                        % (key, str(type(e)), str(e)))
            return False
    elif type(key) == str and key.startswith('disp'):
        key = key.replace('disp', 'listview')
        try:
            attendant[key].wait('ready', timeout).click_input()
            return True
        except Exception as e:
            logger.warning("Failed to click Attendant.%s. Exception: %s %s"
                                        % (key, str(type(e)), str(e)))
            return False
    else:
        return click_key(attendant, key, timeout)

def click_key(window, key, timeout=default_timeout, case_sens=False, click_input=False):
    """
    Generic function for clicking (almost) any key on the POS.
    Args:
        window (pywinauto.application.WindowSpecification object):
            Which POS window object to look for the key in. 
        key (str): The text of the key to click.
        timeout (int): How long to wait for the window and key to be available.
        case_sens (bool): Whether or not to match key text with case sensitivity.
        log (bool): Whether or not to log a failure. Please set this to 
                        False if using this function in a timeout loop.
        click_input (bool): If True, use a 'physical' click instead of a software click.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> click_key(func_keys, "SIGN OFF")
        True
        >>> click_key(speedkey, "NotASpeedKey")
        False
        >>> click_key(func_keys, "sign off", case_sens=True)
        False
    """
    ci_flag = '(?i)'
    if type(key) != str:
        key = str(key)
    key_ = key
    # Escape characters that might mess with regex
    i = 0
    while i < len(key):
        if not key[i].isalnum():
            key = key[:i] + '\\' + key[i:]
            i += 1
        i += 1
    if not case_sens:
        key = ci_flag + key
    key = key + '$'

    # Wait for window existence
    start_time = time.time()
    try:
        window.wait('ready', timeout)
    except:
        logger.warning("%s window not ready within %s seconds." % (window.__dict__['criteria'][0]['best_match'], timeout))
        return False
    timeout = timeout - (time.time() - start_time)

    btn_ctrl = window.window(title_re=key, control_type='Button', found_index=0)

    try:
        if click_input:
            btn_ctrl.click = btn_ctrl.click_input
        # found_index=0 to handle duplicate keys, because those exist for some reason
        btn_ctrl.click()
        return True
    except:
        # Didn't find the key, let's wait to see if it appears
        try:
            btn_ctrl.wait('ready', timeout).click()
            return True
        except Exception as e:
            # Waited too long, time to fail
            logger.warning("Failed to click %s.%s. Exception: %s %s"
                                            % (window.__dict__['criteria'][0]['best_match'], key_, str(type(e)), str(e)))
            return False

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

#@TODO: This is not currently used anywhere. Do we keep it an start utilizing it?
def pos_recover():
    """
    @Name: recover
    @Description: Attempt to reset the POS to a default state by backing
                    out of menus, voiding transaction, clearing prompts, etc.
                    If unable to do so, restart Passport and sign back on to POS.
    """
    # Do stuff to try and reset the POS. Shotgun approach.
    import time
    start_time = time.time()

    while time.time() - start_time <= 180:
        temp_level = logger.getEffectiveLevel()
        logger.setLevel(999)
        msg = read_message_box(timeout = .5)
        logger.setLevel(temp_level)
        if msg != None:
            messages = {'cancel this transaction': 'YES',
                        'void the transaction': 'YES',
                        'not found': 'OK'}
            for message in messages:
                if msg in message:
                    read_message_box(messages[message])
                    break
            else: # Try to click OK if we don't recognize the message
                try:
                    click_message_box_key('OK')
                except:
                    pass

        try:
            func_keys.is_visible()
            f_keys_avail = True
        except:
            f_keys_avail = False

        if f_keys_avail:
            key_list = ['VOID TRANS','CHG/REF DUE', 'SIGN OFF' , 'TOOLS', 'UNLOCK', 'SIGN ON']
            for key in key_list:
                try:
                    func_keys[key].is_visible()
                except:
                    continue
                if key == 'CHG/REF DUE':
                    logger.debug("POS main screen found")
                    return True

                if key == 'UNLOCK' or key == 'SIGN ON':
                    try:
                        sign_on()
                    except Exception as e:
                        logger.warning(e)
                        break

                if key == 'VOID TRANS':
                    click_function_key(key, verify=False)
                    click_message_box_key('YES', verify=False)
                    try:
                        click_till_key('ENTER', verify=False)
                    except:
                        continue


                if key == 'SIGN OFF':
                    click_function_key('BACK', verify=False)

                if key == 'TOOLS':
                    click_function_key('BACK', verify=False)
                    click_function_key('BACK', verify=False)

        try:
            tender_keys.is_visible()
            click_till_key('CANCEL', verify=False)
        except:
            continue

        try:
            keypad_cmd.is_visible()
            click_keypad('CANCEL', timeout= 1, verify=False)
        except:
            continue

        try:
            window['DispenserMenuWindow'].is_visible()
            window['DispenserMenuWindow']['GO BACK'].click()
        except:
            continue

        try:
            window['AttendantSetup'].is_visible()
            att_setup = True
        except:
            att_setup = False
            continue

        if att_setup:
            buttons = ['CANCEL', 'Go Back']
            for button in buttons:
                try:
                    window['AttendantSetup'][button].is_visible()
                except:
                    continue
                window['AttendantSetup'][button].click()

        click_receipt_key('CANCEL', 1, verify=False)

    #TODO: This no longer signs on the to mws at the end
    return system.restartpp()