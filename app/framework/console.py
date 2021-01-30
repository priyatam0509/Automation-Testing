"""
Name: console
Description: Module for automating interaction with the Cashier Control Console.

Date created: 08/22/2019
"""

"""
TODO:
 -Clean up timeout handling
 -Clean up logging
 -High level functions
"""

# Selenium modules
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import SessionNotCreatedException
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, InvalidSelectorException
from selenium.webdriver.support.ui import WebDriverWait

# Third party modules
import time
import json
import logging

# In house modules
from app import pinpad, runas, system
from app.util import constants
from app.simulators.ip_scanner import IPScanner
from app.framework.tc_helpers import test_func

# Log object
logger = logging.getLogger()

# JSON file paths
controls_path  = constants.CONTROLS_CCC
credentials_path = constants.USER_CREDENTIALS

# Retry and Timeouts
default_timeout = 3
prompt_timeout  = 0.5

# Selenium objects
driver  = None
wait    = None

# Edge element locators and button names
with open(controls_path) as f:
    controls = json.load(f)

TERMINALS = { "1": controls["Terminal 1"],
              "2": controls["Terminal 2"] }
INFO = controls["Terminal Info"]
FUNC_KEYS = controls["Function Keys"]
OPTIONS = controls["Options"]
KEYPAD = controls["Keypad"]
KEYBOARD = controls["Keyboard"]
PROMPT_BOX = controls["Prompt Box"]

def connect(url="https://127.0.0.1:8764"):
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
    #if not edit_sco_xml():
    #    logger.warning(f"Unable to edit the settings for {sco_xml}")
     
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
            logger.warning("Unable to connect to Cashier Control Console.")
            return False

        # Verify control console page loads
        if "Express Lane Control Console" not in driver.title:
            logger.warning("Opened a web page, but it wasn't Express Lane Control Console. Check Passport status and URL.")
            return False

        driver.maximize_window()
        return True
    else:
        logger.debug(f"Already connected to a chrome driver instance")
        return True

def close():
    """
    Closes current Chrome driver instance.

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
def add_postpay(dispenser=1, sale_num=1, terminal=None):
    """
    Add a pending postpay to the current transaction.
    Args:       
        dispenser: (int) The ID of the dispenser holding the postpay.
        sale_num: (int) If the dispenser is holding multiple postpays, use this to select the 1st/2nd/3rd.
        terminal: (int) Terminal to add postpay to. Defaults to currently selected terminal.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns: (bool) True/False for success/failure
    Examples:
        >>> add_postpay()
        True
        >>> add_postpay(2, 2)
        True
    """
    if terminal is not None:
        logger.info(f"switching to terminal {terminal}")
        if not select_terminal(terminal, timeout, verify=False):
            return False

    if not click_function_key("Fuel Postpay", verify=False):
        return False
    if not select_postpay(dispenser, sale_num, verify=False):
        click_options_key("Ok", verify=False)
        return False

    return True

@test_func
def add_prepay(amount, dispenser=1, terminal=None):
    """
    Add a prepay to the current transaction.
    Args:
        amount: (str) The dollar amount of fuel to purchase.
        dispenser: (int) The ID of the dispenser to put the prepay on.
        terminal: (int) Terminal to add postpay to. Defaults to currently selected terminal.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns: (bool) True/False for success/failure
    Examples:
        >>> add_prepay("$10.00")
        True
        >>> add_prepay("35.00", 2)
        True
    """
    if terminal is not None:
        logger.info(f"switching to terminal {terminal}")
        if not select_terminal(terminal, timeout, verify=False):
            return False

    amount = amount.replace("$", "").replace(".", "")
    if not click_function_key("Fuel Prepay", verify=False):
        return False
    # wait_disp_ready(dispenser, verify=False)
    if not select_dispenser(dispenser, verify=False):
        click_key(controls['Fuel']['X'])
        return False
    if not enter_keypad(amount, verify=False):
        return False

    return True

@test_func
def suspend_transaction(terminal=None, timeout=default_timeout):
    """
    High level Suspend Transaction function. Click "Suspend Transaction" button & verify
    transaction was successfully suspended by verifying journal is empty.

    Args:
        terminal: (int) Terminal to void transaction from. Defaults to currently selected terminal.
        timeout: (int) How long to wait for clicking "Suspend Transaction".

    Returns:
        True if success, False if failure

    Examples:
        >>> void_transaction()
        True
        >>> void_transaction(terminal=2, user_credentials=('91','91'), reason=3, timeout=5)
        True
        >>> void_transaction(user_credentials=('valid_username','invalid_pw'))
        False
    """
    # switch terminals if specified in method call
    if terminal is not None:
        logger.info(f"switching to terminal {terminal}")
        select_terminal(terminal, timeout)

    if not click_key(FUNC_KEYS["Suspend Transaction"], timeout):
        logger.error("Unable to click 'Suspend Transaction'")
        return False
 
    start_time = time.time()
    while time.time() - start_time <= 10:
        # ensure journal is empty (transaction suspended)
        if read_journal() == []:
            logger.info("Able to confirm susccessful suspension")
            break
    else:
        logger.error("Failed to confirm suspension")
        return False

    return True

@test_func
def void_transaction(terminal=None, user_credentials=None, reason=1, timeout=default_timeout):
    """
    High level Void Transaction function. Enters credentials if prompted, enter reason code
    if prompted, verify transaction was successfully void by verifying journal is empty.

    Args:
        terminal: (int) Terminal to void transaction from. Defaults to currently selected terminal.
        user_credentials: (tuple) the user's sign on credentials (username, passwowrd).
        reason: (int) Number that corresponds to a reason code button (top-down) on the Prompt Box
        during void. This will default to 1, the first (top) reason code button if not specified.
        timeout: (int) How long to wait for switching terminals, clicking "void transaction" and
        checking for the reason code prompt box.

    Returns:
        True if success, False if failure

    Examples:
        >>> void_transaction()
        True
        >>> void_transaction(terminal=2, user_credentials=('91','91'), reason=3, timeout=5)
        True
        >>> void_transaction(user_credentials=('valid_username','invalid_pw'))
        False
    """

    # switch terminals if specified in method call
    if terminal is not None:
        logger.info(f"switching to terminal {terminal}")
        select_terminal(terminal, timeout)

    # clicking void transaction button
    if not click_key(FUNC_KEYS["Void Transaction"], timeout):
        logger.error("Unbable to click 'Void Transaction'")
        return False

    # check if sign-in window present
    if is_element_present(KEYPAD["Window"], timeout):
        logger.info("Entering Credentials")
        # enter credentials
        sign_in(user_credentials)

    # check if reason code prompt box present
    if is_element_present(PROMPT_BOX["Heading"], timeout):
        logger.info("Clicking 1st Reason Code")
        # select first reason code by default, other select "reason" parameter
        if not click_key(PROMPT_BOX["key_by_index"]%reason):
            logger.error("couldn't click reason code")
            return False
    
    # ensure prompt box is dismissed before continuing
    if not system.wait_for(is_element_present, desired_result=False, timeout=timeout, args=[PROMPT_BOX["Window"]]):
        logger.error("Reason code prompt still present")
        return False

    start_time = time.time()
    while time.time() - start_time <= 10:
        # ensure journal is empty (transaction voided)
        if read_journal() == []:
            logger.info("Able to confirm susccessful void.")
            break           
    else:
        logger.error("Unable to confirm empty journal.")
        return False

    return True

@test_func
def sign_in(user_credentials=None, timeout=default_timeout):
    """
    Basic function used to enter user's credentials in the Cashier Command Console.

    Args:
        user_credentials: (tuple) the user's sign on credentials (username, passwowrd).
        Will default to ('91','91') if not specified or can't find store credentials. 
        timeout: (int) How long to wait for credentials to be entered.

    Returns: True if success, False if failure

    Examples:
        >>> sign_in()
        True
        >>> sign_in(('91','91))
        True
        >>> sign_in(('91', InvalidPassword'))
        False
    """

    global credentials
    # start_time = time.time()
    # TODO: protect against timing issues
    json_creds = {}
    
    # set to default credentials if not set
    if user_credentials != None:
        credentials = user_credentials
    else:
        try:
            with open(credentials_path) as creds_file:
                json_creds = json.load(creds_file)
                credentials = [json_creds['ID'], json_creds['Password']]
        except:
            credentials = ['91','91']
            logger.warning(f"Unable to find credentials file. Will use {str(credentials)}")

    # try to enter username
    logger.debug(f"Entering Username: {credentials[0]}")
    for value in credentials[0]:
        if not click_keypad_key(str(value), timeout):
            logger.debug(f"Unable to click {value}")
            return False
    if not click_keypad_key("Ok", timeout):
        logger.warning("Unable to click Ok")
        return False

    # try to enter password
    logger.debug(f"Entering Password: {credentials[1]}")
    for value in credentials[1]:
        if not click_keyboard_key(str(value), timeout):
            logger.debug(f"Unable to click {value}")
            return False
    if not click_keyboard_key("Ok", timeout):
        logger.warning("Unable to click Ok")
        return False
    
    return True

@test_func
def enter_keypad(values, after="Ok"):
    """
    Enter value on numerical keypad.
    Args:
        values: (str) The value you want to enter into keypad.
        after: (str) The key to press after entering digits.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
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
    logger.debug(f"Trying to press keypad buttons: {values}")
    for value in str(values):
        if not click_keypad_key(str(value), verify=False):
            return False
    if after:
        ret = click_keypad_key(after, verify=False)
        time.sleep(.1) # We probably hit Ok/Cancel. Wait for POSState to process
        return ret

    return True


###################
# Click Functions #
###################

@test_func
def click(key, timeout=default_timeout):
    """
    Click a button with text in the cashier control console. 
    Automatically picks relevant click methods based on input, then tries each
    one until a successful click. If this doesn't work for your desired key, you may
    need to use a more specialized function.

    Args:
        key: (str) The text of the key to click.
        timeout: (int) How long to search for the key before failing.

    Returns:
        bool: True if success, False if failure.

    Examples:
        >>> click("3")
        True
        >>> click("User Options")
        True
    """
    WILD = "**" # Indicates functions used to click keys that can have variable text
    map = { "click_function_key": FUNC_KEYS.keys(),
            "click_options_key": OPTIONS.keys(),
            "click_prompt_key": PROMPT_BOX.keys(),
            "click_keypad_key": KEYPAD.keys(),
            "click_keyboard_key": KEYBOARD.keys(),
            "click_prompt_key": [WILD]
          }

    # Figure out which functions might work for the desired key
    def build_func_list(key):
        import sys
        funcs_to_try = []
        for func in map:
            if key in map[func]:
                funcs_to_try.append(getattr(sys.modules[__name__], func))
        return funcs_to_try

    # Create list of functions to search with
    funcs_to_try = build_func_list(key)
    if len(funcs_to_try) == 0:
        # Requested key doesn't match any known menus, try menus that can have custom keys
        funcs_to_try = build_func_list(WILD)
    
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
def select_terminal(terminal, timeout=default_timeout):
    """
    Select a terminal.

    Args:
        terminal: (int) The number of the terminal to select.
        timeout: (int) How many seconds to wait for the terminal to be selectable.

    Returns: (bool) True if success, False if failure

    Example:
        >>> select_terminal(1)
        True
    """
    return click_key(TERMINALS[str(terminal)]["Window"], timeout)

@test_func
def select_dispenser(id=1, timeout=default_timeout):
    """
    Select a dispenser for prepay.
    Args:
        id: (int) The ID of the dispenser to select.
        timeout: (int) How many seconds to wait for the dispenser to be selectable.
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
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
        verify: (bool) Whether or not to fail the current test case if this function fails. Defaults to True.
    Returns: (bool) True/False for success/failure
    Examples:
        >>> select_postpay()
        True
        >>> select_postpay(2, 2)
        True
    """
    return click_key(controls['Fuel']['postpay_by_id_and_instance'] % (dispenser, sale_num), timeout=timeout)

@test_func
def click_journal_item(item='', instance=1, terminal=None, timeout=default_timeout):
    """
    Select a receipt item in the journal.

    Args:
        item: (str) Text identifying the item or transaction to select.
                This can be the name, price, etc.
        instance: (int) Index of item to select if there are multiple matches
                    or if no text is specified. Note that Begin/End Transaction
                    count as items in the journal.
        terminal: (int) The terminal to read the journal from. Defaults to currently selected terminal.
        timeout: (int) How long to wait for the window to be available.

    Returns: (bool) True if success, False if failure

    Examples:
        >>> click_journal_item("$5.00")
        True
        >>> click_journal_item("Generic Item", instance=2)
        True
        >>> click_journal_item(instance=3, terminal=2)
        True
        >>> click_journal_item("NotInTheJournal")
        False
    """
    if terminal is None:
        terminal = get_selected_terminal()

    return click_key(TERMINALS[str(terminal)]["line"].replace('<text>', item).replace('<instance>', str(instance)), timeout)

@test_func
def click_function_key(key, timeout=default_timeout):
    """
    Click a key in the function keys panel (right-hand side).

    Args:
        key: (str) The text of the key to click.
        timeout: (int) How many seconds to wait for the key to be clickable.

    Returns: (bool) True if success, False if failure

    Example:
        >>> click_function_key("Void Transaction")
        True
    """
    return click_key(FUNC_KEYS[key], timeout)

@test_func
def click_options_key(key, timeout=default_timeout):
    """
    Click a key in the User Options window.

    Args:
        key: (str) The text of the key to click.
        timeout: (int) How many seconds to wait for the key to be clickable.

    Returns: (bool) True if success, False if failure

    Example:
        >>> click_options_key("Activate Badge")
        True
    """
    return click_key(OPTIONS[key], timeout=default_timeout)

@test_func
def click_keypad_key(key, timeout=default_timeout):
    """
    Click a key in the login keypad. Also covers the keyboard keypad.

    Args:
        key: (str) The text of the key to click.
        timeout: (int) How many seconds to wait for the key to be clickable.

    Returns: (bool) True if success, False if failure

    Example:
        >>> click_keypad_key("5")
        True
        >>> click_keypad_key("Cancel")
        True
    """
    start_time = time.time()
    if not click_key(KEYPAD[key], timeout):
        return click_keyboard_key(key, timeout - (time.time() - start_time))
    return True

@test_func
def click_keyboard_key(key, timeout=default_timeout):
    """
    Click a key in the keyboard window.

    Args:
        key: (str) The text of the key to click.
        timeout: (int) How many seconds to wait for the key to be clickable.

    Returns: (bool) True if success, False if failure

    Example:
        >>> click_keyboard_key("A")
        True
        >>> click_keyboard_key("Back")
        True
    """
    return click_key(KEYBOARD[key], timeout)

@test_func
def click_prompt_key(key, timeout=default_timeout):
    """
    Click a key in the prompt box.

    Args:
        key: (str) The text of the key to click.
        timeout: (int) How many seconds to wait for the key to be clickable.

    Returns: (bool) True if success, False if failure

    Example:
        >>> click_prompt_key("Cashier error")
        True
        >>> click_prompt_key("Employee Discount")
        True
    """
    return click_key(PROMPT_BOX["Button"].replace('<text>', key), timeout)

def click_key(xpath, timeout=default_timeout, case_sens=False):
    """
    Click the HTML element in self checkout that matches the given XPATH.

    Args:
        xpath: XPATH for the desired key. See console_controls.json for pre-mapped paths.
        timeout: How many seconds to wait for the desired key to be available.
        case_sens: Not yet implemented. TODO

    Returns: (bool) True if success, False if failure

    Examples:
        >>> click_key(FUNC_KEYS["User Options"])
        True
        >>> click_key("//button[@id='login_enter']")
        True
    """
    start_time = time.time()
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath)))
    except TimeoutException:
        logger.warning(f"Element with xpath {xpath} was not found within {timeout} seconds.")
        return False

    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
    except TimeoutException:
        logger.warning(f"Element with xpath {xpath} was found but not clickable within {timeout} seconds.")
        return False   

    element.click()
    return True

##################
# Read functions #
##################

def read_timer(terminal=None, timeout=default_timeout):
    """
    Read the timer for a terminal.

    Args:
        terminal: (int) The terminal # to read the timer for. Defaults to currently selected terminal.
        timeout: (int) How many seconds to wait for the timer to be readable.

    Returns: (str) The current text of the timer.

    Example:
        >>> read_timer()
        "3:57"
        >>> read_timer(2)
        ""
    """
    if terminal is None:
        terminal = get_selected_terminal()
    return _get_text(TERMINALS[str(terminal)]["Timer"], timeout)

def read_journal(terminal=None, timeout=default_timeout):
    """
    Read the receipt journal for a terminal.

    Args:
        terminal: (int) The terminal # to read the journal for. Defaults to currently selected terminal.
        timeout: (int) How many seconds to wait for the timer to be readable.

    Returns: (list) A list of lists, with a receipt line in each list.
    """
    if terminal is None:
        terminal = get_selected_terminal()
    
    journal = []
    rcpt_items = _find_elements(TERMINALS[str(terminal)]["Items"]+"/div", timeout)
    for item in rcpt_items:
        journal.append(item.text.split('\n'))

    return journal

def read_notification(terminal=None, timeout=default_timeout):
    """"
    Read the notification area for a terminal.

    Args:
        terminal: (int) The terminal # to read the notification for. Defaults to currently selected terminal.
        timeout: (int) How many seconds to wait for the notification to be readable.

    Returns: (str) The current notification.

    Example:
        >>> read_notification()
        "Assistance request - Help has been requested. Staff will be with you shortly."
        >>> read_notification(2)
        ""
    """
    if terminal is None:
        terminal = get_selected_terminal()
    return _get_text(TERMINALS[str(terminal)]["Notification"], timeout)

def read_notification_list(terminal=None, timeout=default_timeout):
    """
    Read the notification history list for a terminal.
    Opens the list if needed, and returns it to the state it was in before this method was called.

    Args:
        terminal: (int) The terminal # to read the notification for. Defaults to currently selected terminal.
        timeout: (int) How many seconds to wait for the notifications to be readable.

    Returns: (list) The list of past notifications.

    Example:
        >>> read_notification_list()
        ['Assistance request-Help has been requested. Staff will be with you shortly.',
        'Item Entry Error-Customer selected speed key item 001. Failed to add: Customer
        tried to purchase price required item [001].']
    """
    if terminal is None:
        terminal = get_selected_terminal()

    opened_list = False
    notif_list = _find_element(TERMINALS[str(terminal)]["Notification List"], timeout)
    style = notif_list.get_attribute("style")
    if style == "" or style == "display: none;":
        # Display the notification list
        if not click_key(TERMINALS[str(terminal)]["Notification Button"], timeout=1):
            return False
        opened_list = True

    notif_text = notif_list.text
    # Close the notification list if we auto-opened it
    if opened_list and not click_key(TERMINALS[str(terminal)]["Notification Button"], timeout=1):
        return False
    return notif_text.split('\n')    

def read_balance(terminal=None, timeout=default_timeout):
    """
    Read the transaction totals for a terminal.

    Args:
        terminal: (int) The terminal # to read the totals for. Defaults to currently selected terminal.
        timeout: (int) How many seconds to wait for the timer to be readable.

    Returns: (dict) The contents of the totals window.

    Example:
        >>> read_balance()
        { "Transaction Total": "$15.00",
          "Balance Due": "$10.00" }
    """
    if terminal is None:
        terminal = get_selected_terminal()

    totals_list = _get_text(TERMINALS[str(terminal)]["Totals"], timeout).split('\n')
    totals_dict = {}
    for i in range(0, len(totals_list), 2):
        totals_dict.update({totals_list[i]: totals_list[i+1]})

    return totals_dict

def read_keypad_prompt(timeout=default_timeout):
    """
    Read the prompt box for the keypad/keyboard.

    Args:
        timeout: (int) How many seconds to wait for the prompt to be readable.

    Returns: (str) The text of the prompt.

    Example:
        >>> read_keypad_prompt()
        "Enter your password"
    """
    return _get_text(KEYBOARD["Prompt"], timeout)

def read_keyboard_prompt(*args, **kwargs):
    """Alternate name for read_keypad_prompt."""
    return read_keypad_prompt(*args, **kwargs)

def read_prompt_box(timeout=default_timeout):
    """
    Read the prompt box for the keypad/keyboard.

    Args:
        timeout: (int) How many seconds to wait for the prompt to be readable.

    Returns: (str) The text of the prompt.

    Example:
        >>> read_prompt_box()
        "Indicate a reason for voiding the transaction"
    """
    return _get_text(read_prompt_box["Text"])

def read_options(timeout=default_timeout):
    """
    Read the text of the options window.

    Args:
        timeout: (int) How many seconds to wait for the window to be readable.

    Returns: (list) The text elements of the window.

    Example:
        >>> read_options()
        ["Activate Badge", "Please scan your badge"]
    """
    return _get_text(OPTIONS["Text"], timeout).split('\n')

def get_selected_terminal():
    """
    Check which terminal is currently selected.

    Args: None

    Returns: (int) The number of the currently selected terminal.

    Example:
        >>> get_selected_terminal()
        2
    """
    for terminal, map in TERMINALS.items():
        if _find_element(map["Window"]).get_attribute("class").endswith("selected"):
            return int(terminal)
    return None

def is_terminal_calling(terminal=None):
    """
    Check if a terminal is calling for help (red flashing background).

    Args: 
        terminal: (int) The terminal # to check. Defaults to currently selected terminal.

    Returns: (bool) True if the terminal is requesting help, False if not.

    Example:
        >>> is_terminal_calling(2)
        True
    """
    if terminal is None:
        terminal = get_selected_terminal()
    
    help_animation_name = "blinkRed"
    return _find_element(TERMINALS[str(terminal)]["Receipt"]).value_of_css_property('animation-name') == help_animation_name
    

def read_terminal_info():
    """
    Read the contents of the info box in the top-right corner.

    Args: None

    Returns: (list) The strings contained in the info box.

    Example:
        >>> read_terminal_info()
        ["Terminal 1", "Item 6"]
    """
    return _get_text(INFO["Info"]).split('\n')

def swap_to_pos():
    """
    Swap from the cashier control console to the main POS.
    Automate the POS using the pos_html module (from app import pos) after calling this.
    When you're done, switch back using pos.swap_to_console() (the POS will break if Chrome
    is closed without doing so).
    Notes: this feature is only active after switching from POS to console.
    It should only be used when specifically testing POS swap functionality.
    Args: None
    Returns:
        bool: True/False for success or failure
    Examples:
        >>> swap_to_pos()
        True
    """
    logger.info("Swapping from cashier control console to POS.")
    if not click_function_key("Swap To POS", verify=False):
        return False
    driver.switch_to_default_content() # Switch back to the default frame
    from app import pos
    pos.driver = driver # Pass our Chrome driver to POS module
    return True

def is_element_present(xpath, timeout=prompt_timeout):
    """
    Waits for the element/button to be present on the screen.
    
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
        
"""
Helper Functions
"""
def _get_text(locator, timeout=default_timeout):
    """
    Helper function. Returns the button's text.

    Args:
        locator (str): Button's XPATH
        timeout (int): How long to wait for the window and key to be available.

    Returns:
        bool: True if success, False if failure

    Examples:
        >>> _get_text(SOME_VALID_LOCATOR)
        'Generic Item'
        >>> _get_text(SOME_INVALID_LOCATOR)
        None
    """
    try:
        button = WebDriverWait(driver, timeout).until(EC.presence_of_element_located
                        ((By.XPATH, locator)))
        return button.text
    except Exception as e:
        logger.warning(f"Could not get text of element with XPATH {locator} within {timeout} seconds. Error message: {e}")
        return None

def _find_element(locator, timeout=.5):
    """
    Helper function. Searches the DOM to find the element you are looking for.

    Args:
        locator (str): Button's XPATH
        timeout (int): How long to wait for the window and key to be available.

    Returns:
        bool: True if success, False if failure

    Examples:
        >>> _find_element(SOME_VALID_LOCATOR)
        (
            <selenium.webdriver.remote.webelement.WebElement (session="80f1a1ebe8220157e9d2f394e913db02", element="0.05045595521012469-1")>,
            True
        )
        >>> _find_element(SOME_INVALID_LOCATOR)
        (
            None,
            False
        )
    """
    try:
        element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located
                        ((By.XPATH, locator)))
        return element
    except Exception as e:
        logger.warning(f"Could not find element with XPATH {locator} within {timeout} seconds. Error message: {e}")
        return None

def _find_elements(locator, timeout=.5):
    """
    Helper function. Searches the DOM to find a list of elements you are looking for.
    Args:
        locator (str): Button's XPATH
        timeout (int): How long to wait for the window and key to be available.
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> _find_element(SOME_VALID_LOCATOR)
        (
            <selenium.webdriver.remote.webelement.WebElement (session="80f1a1ebe8220157e9d2f394e913db02", element="0.05045595521012469-1")>,
            True
        )
        >>> _find_element(SOME_INVALID_LOCATOR)
        (
            None,
            False
        )
    """
    start_time = time.time()
    while time.time() - start_time <= timeout:
        try:
            elements = driver.find_elements_by_xpath(locator)
            return elements
        except:
            continue
    else:
        logger.warning(f"Could not find elements with xpath {locator}.")
        return None