"""
Name: insite360web
Description: This is use for insite360 pages to perform actions.
Date created: 04/23/2020
Modified By:
Date Modified:
"""

# Selenium modules
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, SessionNotCreatedException, ElementClickInterceptedException, StaleElementReferenceException, WebDriverException


# Third party modules
import time
import json
import logging
import sys

# In house modules
from app.util import constants

# Log object
logger = logging.getLogger()

# Selenium objects
driver = None

try:
    with open(constants.CONTROL_PATH) as f:
        controls = json.load(f)
except Exception as e:
    logger.warning(e)

"""
Insite360 locators and button names.
"""
LOGIN = controls["Login"]
SECURITY = controls["Security"]
STORE_OPT = controls["Store Options"]
EMP_EDIT = controls["Employee Edit"]
EMPLOYEE = controls["Employees"]
EMP_DATA = controls["Employee Values"]


def connect():
    """
    Initializes Chrome driver instance and navigates to insite360.
    Args: None
    Returns: True if success, False if failure
    Examples:
        >>> connect()
        True
        >>> connect()
        False
    """
    global driver

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
            driver.get(constants.LOGIN_URL)
        except:
            logger.warning("Unable to open web page.")
            return False

        driver.maximize_window()
        return True
    else:
        logger.debug(f"Already connected to a chrome driver instance")
        return True


def close():
    """
    Close the Chrome browser instance through chrome driver.
    Args: None
    Returns: True if success, False if failure
    Examples:
        >>> close()
        True
        >>> close()
        False
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
        driver = None


def logout():
    """
    Logout the current Chrome browser instance through chrome driver.
    Args: None
    Returns: True if success, False if failure
    Examples:
        >>> logout()
        True
        >>> logout()
        False
    """
    global driver
    try:
        driver.maximize_window()
        driver.find_element_by_id(controls['Menu']).click()
        driver.find_element_by_id(controls['Logout']).click()
        return True
    except:
        logger.error(f"Unable to logout - [{sys.exc_info()[0]}]")
        return False


def login(username, password):
    """
    Login with user credentials at insite360.
    Args:   username (string) - employee email id
            password (string)
    Returns: True if success, False if failure
    Examples:
        >>> login('user@gilbarco.com', 'password')
        True
        >>> login('user@gilbarco.com', 'password')
        False
    """
    global driver
    try:
        driver.find_element_by_id(LOGIN["Email"]).send_keys(username)
        driver.find_element_by_id(LOGIN["Password"]).send_keys(password)
        driver.find_element_by_id(LOGIN["LOG IN"]).click()
        return_status = False
        max_attempts = 0
        while(return_status is False and max_attempts < 3):
            max_attempts = max_attempts + 1
            return_status = validate_after_login()
            if (max_attempts == 3):
                logger.error(f"Unable to Login....")
    except:
        logger.error(f"Unable to login with user[{username}] :: [{password}] credentails")
        return_status = False
    return return_status


def page_load_wait(time_out=30, xpath='//*[@id="page-title"]'):
    """
    Wait for the expected page load check based on the control
    Args:   time_out (int)
            xpath (string) - control id
    Returns: True/ False
    """
    status = True
    try:
        element = WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, xpath)))
    except TimeoutException:
        logger.error(f"Element with xpath {xpath} was not found within {time_out} seconds.")
        status = False
    return status


def validate_after_login():
    """
    Validate after login is successful or not, if any security question ask then provide the answer based on the question
    Args:   None
    Returns: True if success, False if failure
    """
    global driver
    try:
        return_status = False
        current_url = driver.current_url
        logger.info(f"current URL after login is [{current_url}]")
        if (current_url == constants.MAIN_PAGE):
            return_status = True
        elif (current_url.find('/login/config/') > 0):
            logger.info(f"Please, answer the security question...")
            question = driver.find_element_by_id(SECURITY["Question"]).text
            logger.info(f"question [{question}]")
            question = question.lower()
            driver.find_element_by_id(SECURITY["Answer"]).clear()
            time.sleep(2)
            if (question.find('street number') > 0):
                driver.find_element_by_id(SECURITY["Answer"]).send_keys("7300")
            elif (question.find('name of the company') > 0):
                driver.find_element_by_id(SECURITY["Answer"]).send_keys("Gilbarco")
            elif (question .find('your mothers middle') > 0):
                driver.find_element_by_id(SECURITY["Answer"]).send_keys("Automation")
            time.sleep(2)

            logger.info(f'answer : [{driver.find_element_by_id(SECURITY["Answer"]).get_attribute("value")}]')
            time.sleep(1)
            driver.find_element_by_id(SECURITY["Continue"]).click()
            return_status = page_load_wait()
    except:
        logger.error(f"Unable to login with user credentails at [validate_after_login]")
        return_status = False
    return return_status


def cancel(on_save=False):
    """
    Clear or cancel from the existing url page
    Args: on_save (boolean) - if True, without changes click on Save Button
    Returns: None (action will be taken at UI page)
    Examples:
        >>> cancel()
        >>> cancel(True)
    """
    global driver
    current_url = driver.current_url
    logger.info(f"current URL is [{current_url}]")
    if (current_url == constants.EMP_URL):
        # Set as default (Clear all the controls text and click on search)
        driver.find_element_by_id(EMPLOYEE["Operator Id"]).clear()
        time.sleep(2)
        driver.find_element_by_id(EMPLOYEE["Search"]).click()
    elif (current_url.find('employee-list/#/employee-edit/') > 0):
        # Click on cancel button for employee edit
        if (on_save):
            driver.find_element_by_id(EMP_EDIT["Save"]).click()
        else:
            driver.find_element_by_id(EMP_EDIT["Cancel"]).click()


def is_employee_exists_by_id(operator_id):
    """
    Check the either the employee data exists or not by operator id at insite360
    Args: operator_id (string value)
    Returns: 1 if exists, 0 if not exists, >1 Error while performing employee data check by id
    Examples:
        >>> is_employee_exists_by_id('737')
        1
        >>> is_employee_exists_by_id('7377')
        0
        >>> is_employee_exists_by_id('7377')
        100
    """
    global driver
    try:
        try:
            driver.get(constants.EMP_URL)
            driver.switch_to.window(driver.current_window_handle)
        except:
            logger.error("Unable to open web page.")
            return 2

        if (page_load_wait(xpath=EMPLOYEE["Display Records"])):
            logger.info(f"current URL is [{driver.current_url}]")
            localError = True
            max_cnt = 1
            while (localError and max_cnt <= 3):
                try:
                    driver.find_element_by_id(EMPLOYEE["Operator Id"]).clear()
                    time.sleep(2)
                    driver.find_element_by_id(EMPLOYEE["Operator Id"]).send_keys(operator_id)
                    time.sleep(1)
                    driver.find_element_by_id(EMPLOYEE["Search"]).click()
                    localError = False
                except:
                    logger.error(f"employeeSearch[{operator_id}] failed")
                    localError = True
                max_cnt = max_cnt + 1

            if not(localError):
                # After click on search button, wait for 3 seconds RSPK
                time.sleep(3)
                logger.info(f"current URL is [{driver.current_url}]")
                opp = driver.find_element_by_id(EMPLOYEE["Operator Id"]).get_attribute("value")
                logger.info(f"Operator ID from WEB : [{opp}]")
                recFound = driver.find_element_by_xpath(EMPLOYEE["Display Records"]).text
                logger.info(f"After search records found status for [{operator_id}] is [{recFound}]")
                if (recFound == '0 of 0'):
                    return 0
                else:
                    return 1
            else:
                return 100
        else:
            logger.error(f"Error at loading the page [{constants.EMP_URL}]")
            return 100
    except:
        logger.error(f"is_employee_exists_by_id({operator_id}) - [{sys.exc_info()[0]}]")
        return 100


def add_new_employee(operator_id, config):
    """
    Adding a new employee at insite360
    Args:   operator_id (string value)
            config (dictionary)
    Returns: True/False
    Examples:
    config = { "First Name" : "Auto", "Last Name" : "Manager", "Operator Id" : "737", "Birth Date" : "07-02-1997", "Address Line 1" : "786 Fake Street", "Address Line 2" : "Bldg 1", "Address Line 3" : "Suite 234", "City" : "Greensboro", "State" : "NORTH CAROLINA", "Postal Code" : "27410", "Phone" : "(897) 867-7737", "Security Group" : "Manager", "Assigned Stores" : "TestAutoSite1", "Clock InOut Required" : False, "Override the Blind Balancing store option" : True, "Language" : "US English", "Theme" : "Passport Retro", "Keypad Calculator" : True, "Keypad Telephone" : False, "Hand Preference Right" : False, "Hand Preference Left" : True }
        >>> add_new_employee('737', config)
        True
    """
    global driver
    status = False
    try:
        # click on Create New Employee button
        driver.find_element_by_id(EMPLOYEE["Create New Employee"]).click()
        status = page_load_wait(xpath=EMP_EDIT["Assigned Stores"]["ID"])
        if (status):
            for key, value in config.items():
                if (key == "Operator Id"):
                    value = operator_id
                logger.info(f"{key} value is [{value}]")
                if (value == "True" or value == "False"):
                    value = eval(value)
                set_employee_values(key, value)
            time.sleep(5)
            driver.find_element_by_id(EMP_EDIT["Save"]).click()
            logger.info(f"add_new_employee - Success[{operator_id}]")
            if not(page_load_wait(time_out=5, xpath=EMPLOYEE["Display Records"])):
                try:
                    logger.error(f'[{driver.find_element_by_xpath(EMP_EDIT["ErrorMsg"]).text}]')
                except:
                    logger.error(f'Error: while adding an employee, site is offline.')
                driver.find_element_by_id(EMP_EDIT["Cancel"]).click()
                status = False
            else:
                status = True
        else:
            logger.error(f"Error at loading the page [{constants.NEW_EMP_URL}]")
    except:
        logger.error(f"add_new_employee - [{sys.exc_info()[0]}]")
        status = False
    return status


def set_employee_values(field, field_value, control='', type_control='', set_clear=False):
    """
    Assign the employee field values at insite360 for each field based on the operator_id
    Args:   field (string value)
            field_value (string or boolean based on the field fetch from JSON object)
            control (string value) - Web UI control Id
            set_clear (boolean) - By default False, when it is True first clears the control text before setting the value
    Returns: None
    Examples:
        >>> set_employee_values("First Name", "Auto", "firstName", True)
        >>> set_employee_values("Phone", "(897) 867-7737", '//*[@id="phoneNumber"]/input')
        >>> set_employee_values("Keypad Calculator", True, "radioKeypadCalculator")
    """
    global driver

    if (control == ''):
        # control = get_control_id_for_emp(field)
        control = EMP_EDIT[field]["ID"]
        type_control = EMP_EDIT[field]["Type"]

    logger.info(f"get_control_id_for_emp({field}) control is [{control}] with value [{field_value}]")

    if (type_control == 'text'):
        if (set_clear):
            logger.info(f"Clear the text box [{field}]")
            driver.find_element_by_id(control).clear()
            time.sleep(1)
        driver.find_element_by_id(control).send_keys(field_value)
    elif (type_control == 'dropdown'):
        dropdownElement = Select(driver.find_element_by_id(control))
        dropdownElement.select_by_visible_text(field_value)
    elif (type_control == 'xpath'):
        driver.find_element_by_xpath(control).send_keys(field_value)
    elif (type_control == 'textselect'):
        driver.find_element_by_xpath(control).click()
        time.sleep(1)
        driver.find_element_by_xpath(control).send_keys(field_value)
        time.sleep(2)
        driver.find_element_by_xpath(control).send_keys(Keys.ENTER)
    elif (type_control == 'check' or type_control == 'radio'):
        is_checked = driver.find_element_by_id(control).get_attribute("checked")
        if (field_value):
            if (is_checked is None):
                logger.info(f"set_employee_values({field}, {field_value}, {control}) : value is {is_checked}")
                driver.find_element_by_id(control).click()
        else:
            if not(is_checked is None):
                logger.info(f"set_employee_values({field}, {field_value}, {control}) : value is not [{is_checked}]")
                driver.find_element_by_id(control).click()


def set_assigned_store_validate(operator_id, field_value):
    """
    Fetch the existing "assigned stores" value and update with the field value
    Args:   operator_id (string value)
            field_value (string value of "assigned stores")
    Returns: True/ False (return_status)
    Examples:
        >>> set_assigned_store_validate("737", "TestAutoSite1")
        True
        >>> set_assigned_store_validate("737", "TestAutoSite1")
        False
    """
    global driver
    return_status = set_assigned_store(operator_id, field_value)
    if (return_status):
        driver.find_element_by_id(EMP_EDIT["Save"]).click()
        check = True
        max_attempt = 1
        while (check and max_attempt <= 3):
            time.sleep(1)
            if (driver.current_url == constants.EMP_URL):
                check = False
            else:
                logger.info(f"Some Issue after save - [{field_value}] for operator ID [{operator_id}]")
                driver.find_element_by_id(EMP_EDIT["Cancel"]).click()
                time.sleep(2)
                if not(is_employee_exists_by_id(operator_id) <= 1):
                    logger.info(f"operator ID [{operator_id}] not exists")
                if not(set_assigned_store(operator_id, field_value)):
                    logger.info(f"Unable to set the [{field_value}] for operator ID [{operator_id}]")
                max_attempt = max_attempt + 1

            if (max_attempt > 3):
                driver.find_element_by_id(EMP_EDIT["Cancel"]).click()
                page_load_wait(xpath=EMPLOYEE["Display Records"])
                check = False
                return_status = False
    else:
        driver.find_element_by_id(EMP_EDIT["Cancel"]).click()
        page_load_wait(xpath=EMPLOYEE["Display Records"])
    return (return_status)


def set_assigned_store(operator_id, field_value, edit_screen=False):
    """
    Fetch the existing "assigned stores" value and update with the field value
    Args:   operator_id (string value)
            field_value (string value of "assigned stores")
            edit_screen (bool)
    Returns: True/ False (return_status)
    Examples:
        >>> set_assigned_store("737", "TestAutoSite1")
        True
        >>> set_assigned_store("737", "TestAutoSite1", True)
        False
    """
    global driver
    return_status = True

    try:
        if not(edit_screen):
            driver.find_element_by_id(EMPLOYEE["Edit Details"]).click()
            return_status = page_load_wait(xpath=EMP_EDIT["Assigned Stores"]["ID"])
        if (return_status):
            logger.info(f"current URL is [{driver.current_url}]")
            assignedStores = driver.find_element_by_xpath(EMP_EDIT["Assigned Stores List"]).text
            control = EMP_EDIT["Assigned Stores"]["ID"]
            string_to_search = field_value.lower()
            logger.info(f"set_assigned_store - assignedStores[{assignedStores}] for operator ID [{operator_id}] exists.")
            logger.info(f"set_assigned_store - string_to_search[{string_to_search}] for operator ID [{operator_id}] exists.")
            if not(string_to_search == ""):
                if not (string_to_search in assignedStores.lower()):
                    logger.info(f"set_assigned_store - [{field_value}] for operator ID [{operator_id}]")
                    driver.find_element_by_xpath(control).click()
                    time.sleep(1)
                    driver.find_element_by_xpath(control).send_keys(string_to_search)
                    time.sleep(2)
                    driver.find_element_by_xpath(control).send_keys(Keys.ENTER)
                else:
                    logger.info(f"Already set_assigned_store - [{string_to_search}] for operator ID [{operator_id}] exists.")
                    return_status = False
            else:
                logger.info(f"set_assigned_store - [{string_to_search}] for operator ID [{operator_id}]")
                driver.find_element_by_xpath(control).click()
                time.sleep(1)
                driver.find_element_by_xpath(control).send_keys(string_to_search)
                time.sleep(2)
                driver.find_element_by_xpath(control).send_keys(Keys.ENTER)
                time.sleep(2)
    except:
        logger.error(f"set_assigned_store - [{sys.exc_info()[0]}]")
        return_status = False

    return (return_status)


def get_field_value(control, type_control):
    """
    Get the existing field value based on the operator ID and control Name
    Args:   control (string value of control ID")
            type_control (string)
    Returns: field_value (string/ boolean based on the control ID)
    Examples:
        >>> get_field_value("firstName","text")
        Automation
        >>> get_field_value("radioKeypadTelephone","radio")
        True
    """
    global driver
    field_value = ''
    if (type_control == 'text'):
        field_value = driver.find_element_by_id(control).get_attribute("value")
    elif (type_control == 'dropdown'):
        dropdownElement = Select(driver.find_element_by_id(control))
        field_value = dropdownElement.first_selected_option.text
    elif (type_control == 'xpath'):
        field_value = driver.find_element_by_xpath(control).get_attribute("value")
    elif (type_control == 'textselect'):
        field_value = driver.find_element_by_xpath(EMP_EDIT["Assigned Stores List"]).text
    elif (type_control == 'check' or type_control == 'radio'):
        field_value = driver.find_element_by_id(control).get_attribute("checked")
        if (field_value is None):
            field_value = False
        else:
            field_value = True

    return field_value


def toggleActivate(operator_id, siteID):
    """
    Toggle the active/ de-activate of the employee based on operator ID
    Args:   operator_id (string value)
            siteID (string value of gilbarco_id/ SiteID)
    Returns: return_status (True / False)
    Examples:
        >>> toggleActivate("737", "857115")
        True
    """
    global driver
    return_status = False
    try:
        is_enabled = driver.find_element_by_id(EMPLOYEE["Edit Details"]).is_enabled()
        if (is_enabled):
            logger.info(f"toggleActivate({operator_id}, {siteID}) : value is {is_enabled}")
            driver.find_element_by_id(EMPLOYEE["De-activate"]).click()
            time.sleep(2)
            driver.find_element_by_xpath(EMPLOYEE["OK"]).click()
        else:
            logger.info(f"toggleActivate({operator_id}, {siteID}) : value is {is_enabled}")
            driver.find_element_by_id(EMPLOYEE["Re-activate"]).click()
            time.sleep(2)
            driver.find_element_by_xpath(EMPLOYEE["OK"]).click()
            time.sleep(2)
            set_assigned_store_validate(operator_id, siteID)
        time.sleep(3)
        is_enabled_after = driver.find_element_by_id(EMPLOYEE["Edit Details"]).is_enabled()
        if not(is_enabled == is_enabled_after):
            return_status = True
    except:
        logger.error(f"toggleActivate - [{sys.exc_info()[0]}]")
    return (return_status)


def update_employee(operator_id, element, gilbarco_id="", on_save=False):
    """
    Modify/update the employee field value based on the operator_id and element
    Args:   operator_id (string value)
            element (string value)
            gilbarco_id (string value) - gilbarco_id/ site_id
            on_save (boolean) - This parameter will use to unchange and click on save button
    Returns: return_status (boolean)
    Examples:
        >>> update_employee("737", "First Name")
        >>> update_employee("737", "Phone")
        >>> update_employee("737", "Activate", "857115")
        >>> update_employee("737", "")
        >>> update_employee("737", "", "", True)
    """
    global driver
    return_status = True
    try:
        empStatus = is_employee_exists_by_id(operator_id)
        if (empStatus == 1):
            if (element == ""):
                # Unchange the values and click on "Save Button"
                driver.find_element_by_id(EMPLOYEE["Edit Details"]).click()
                return_status = page_load_wait(xpath=EMP_EDIT["Assigned Stores"]["ID"])
                if (return_status):
                    cancel(on_save)
            elif (element == "Activate"):
                return_status = toggleActivate(operator_id, gilbarco_id)
            else:
                driver.find_element_by_id(EMPLOYEE["Edit Details"]).click()
                return_status = page_load_wait(xpath=EMP_EDIT["Assigned Stores"]["ID"])
                if (return_status):
                    time.sleep(5)
                    if not(element == "View Total On Blind Balance"):
                        control_id = EMP_EDIT[element]["ID"]
                        type_control = EMP_EDIT[element]["Type"]

                        # Get the existing field values from WEB
                        current_value = get_field_value(control_id, type_control)
                        logger.info(f"Operator id[{operator_id}] control_id = [{control_id}] current_value = [{str(current_value)}]")
                        # Toggle the field values
                        if (EMP_DATA[element]["Value1"] == str(current_value)):
                            field_value = EMP_DATA[element]["Value2"]
                        else:
                            field_value = EMP_DATA[element]["Value1"]

                        logger.info(f"After Toggle - Operator id[{operator_id}] control_id = [{control_id}] field_value = [{field_value}]")
                    if (element == "Keypad Calculator"):
                        if not(eval(field_value)):
                            # set keypad Telephone option as True
                            set_employee_values("Keypad Telephone", True, "radioKeypadTelephone", type_control)
                        else:
                            set_employee_values(element, True, control_id, type_control)
                    elif (element == "Hand Preference Right"):
                        if not(eval(field_value)):
                            set_employee_values("Hand Preference Left", True, "radioHandLeft", type_control)
                        else:
                            # set Hand Preference Left option as True
                            set_employee_values(element, True, control_id, type_control)
                    elif (element == "View Total On Blind Balance"):
                        # "View Total On Blind Balance" is depend on the "Override blind balance" option
                        # if "Override blind balance" is unchecked no need to update the value
                        control_id = EMP_EDIT["Override the Blind Balancing store option"]["ID"]
                        type_control = EMP_EDIT["Override the Blind Balancing store option"]["Type"]
                        is_checked = driver.find_element_by_id(control_id).get_attribute("checked")
                        if (is_checked is None):
                            set_employee_values("Override the Blind Balancing store option", True, control_id, type_control)
                        control_id = EMP_EDIT[element]["ID"]
                        type_control = EMP_EDIT[element]["Type"]
                        # Get the existing field values from WEB
                        current_value = get_field_value(control_id, type_control)
                        logger.info(f"Operator id[{operator_id}] control_id = [{control_id}] current_value = [{current_value}]")
                        # Toggle the field values
                        if (EMP_DATA[element]["Value1"] == current_value):
                            field_value = EMP_DATA[element]["Value2"]
                        else:
                            field_value = EMP_DATA[element]["Value1"]

                        logger.info(f"After Toggle - Operator id[{operator_id}] control_id = [{control_id}] field_value = [{field_value}]")
                        set_employee_values(element, field_value, control_id, type_control)
                    else:
                        if (element == "Clock InOut Required"):
                            field_value = eval(field_value)
                        set_employee_values(element, field_value, control_id, type_control, True)
                    # After setting the field values, click on Save Button to update the fields with toggle values
                    set_assigned_store(operator_id, gilbarco_id, True)
                    driver.find_element_by_id(EMP_EDIT["Save"]).click()
                    if not(page_load_wait(time_out=5, xpath=EMPLOYEE["Display Records"])):
                        try:
                            logger.error(f'[{driver.find_element_by_xpath(EMP_EDIT["ErrorMsg"]).text}]')
                        except:
                            logger.error(f'Error: while updating an employee....')
                        driver.find_element_by_id(EMP_EDIT["Cancel"]).click()
                        return_status = False
                    else:
                        return_status = True
        else:
            logger.info(f"No employee record found with operator id({operator_id})")
            return_status = False
    except:
        logger.error(f"update_employee - [{sys.exc_info()[0]}]")
        return_status = False

    return (return_status)


def refresh_site_after_connect():
    """
    After register at site need to refresh at insite360 for connectivity for 30 attempts.
    Args: None
    Returns: True/ False
    Examples:
        >>> refresh_site_after_connect()
        True
        >>> refresh_site_after_connect()
        False
    """
    global driver
    try:
        offline = True
        max_count = 1
        while (offline and max_count <= 30):
            driver.get(constants.STORE_URL)
            if page_load_wait(STORE_OPT["Options Text"]):
                time.sleep(10)
                driver.find_element_by_id(STORE_OPT["Clear"]).click()
                time.sleep(1)
                driver.find_element_by_id(STORE_OPT["Store Name"]).send_keys("AutomationSite1")
                driver.find_element_by_id(STORE_OPT["Search"]).click()
                time.sleep(1)
                driver.find_element_by_id(STORE_OPT["Options"]).click()
                time.sleep(1)
                options_text = driver.find_element_by_xpath(STORE_OPT["Options Text"]).text
                string_to_search = 'change fuel price'
                if (string_to_search in options_text.lower()):
                    offline = False
            max_count = max_count + 1
            if (max_count > 30):
                logger.info(f"refresh_site_after_connect Site [AutomationSite1] is not Online...")
    except:
        logger.error(f"refresh_site_after_connect - [{sys.exc_info()[0]}]")
    return offline
