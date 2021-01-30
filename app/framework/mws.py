"""
Description: This module is used to create connection to the mainwindow application
             and to connect to passport menu processes. It is also used to recover
             from falures

Original Author: Bryan Grant
Date Created: 11/23/2016

Modified By: Cassidy Garner
Date Modified: 10/9/2018
"""

from pywinauto import Application
import pywinauto
from win32gui import FindWindow
from PIL import ImageGrab
import time
import logging
import json
import re
import winreg

# In-House Modules
from app import OCR, system
from app.util import constants

file_path = constants.CONTROLS_WPF
current_menu = None
current_tab = None # This is only set when select_tab is called - won't be accurate for a newly loaded menu
controls = None
process = None
process2 = None
process_conn = None

default_timeout = 10
log = logging.getLogger()

def connect(menu):
    """Initialize the connection to the current MWS menu."""
    #Load the controls file and set the current_menu, controls, and process values
    load_controls(menu)
    #Set the process_con value
    create_connection()

def load_controls(menu):
    global current_menu, controls, process, process2

    if menu == None:
        log.warning("Attempted to load controls for 'None'")
        return False

    menu = menu.lower()

    report_menu =['sales','accounting', 'fuel','journal reports', 'backoffice reports', 'system events']
    reports_eng = ['car wash', 'cash acceptor reports', 'configuration reports', 'scheduled events']
    #Set the menu for the reports based on the lists above
    #if menu in report_menu:
    #    menu = 'reportmenu'
    #elif menu in reports_eng:
    #    menu = 'reportengine'

    #Can we get a comment for the below?
    if menu == 'coupon key maintenance' or menu == 'department key maintenance':
        if find_text_ocr('Speed Key Maintenance'):
            menu = 'speedkey maintenance'
        elif find_text_ocr('Level Number'):
            menu = 'speedkey maintenance'

    current_menu = menu
    #Load the controls.json file
    with open(file_path) as controls_file:
        controls = json.load(controls_file)
    try:
        controls = controls[menu]
    except KeyError:
        log.error(menu+" has not been added to the controls.json file")
        raise MWSMapException(f"{menu} is not mapped in controls.json.")

    # Handle network menus
    try:
        network = controls['network']
    except KeyError:
        network = False
    if network:
        log.debug("Loading controls for network menu")
        brand = system.get_brand()
        for key in controls.keys():
            if brand.upper() in key.upper():
                try:
                    controls = controls[key]
                except KeyError:
                    log.error("Failed to find the brand network controls")
                    raise MWSMapException(f"{brand} does not have a map for {menu} in controls.json.")
        log.debug("Reading the process from the controls.json file")
    try:
        #Read the process from the controls file
        process = controls['process']
    except KeyError:
        log.error("Failed to load menu process")
        raise MWSMapException(f"Process name is not mapped in controls.json for {menu}.")

    #Read process2 if it exists
    try:
        process2 = controls['process2']
    except KeyError:
        process2 = None

    current_tab = None # Reset current tab
    return controls

def create_connection():
    global process_conn
    p = get_active_window()
    if p is None:
        return False
    process_conn = p
    # Some menus don't have fixed control IDs until certain tabs are loaded. Handle this
    try:
        prev_tab = current_tab
        for tab in controls['load_tabs']:
            if not select_tab(tab):
                break
        else:
           if prev_tab is not None: 
                select_tab(prev_tab)
    except KeyError:
        pass
    return True

def is_high_resolution():
    """
    Check if the MWS has been set to high-resolution (1024x768) mode.
    Args: None
    Returns: (bool) True if high-res mode is enabled, False if not.
    Example:
        >>> is_high_resolution()
        True
    """
    try:
        resolution_subkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, constants.RES_SUBKEY, 0, winreg.KEY_ALL_ACCESS)
        return not bool(int(winreg.QueryValueEx(resolution_subkey, 'UseLowerResolution')[0]))
    except FileNotFoundError:
        return False

#@TODO: Move to test_harness?
class MWSMapException(Exception):
    def __init__(self, msg):
        self.message = msg

class ConnException(Exception):
    def __init__(self, msg):
        #@TODO: Make a more permanent solution to screenshots at failure
        system.takescreenshot()
        self.message = msg

def get_active_window(timeout=45):
    """Return a pywinauto connection to the currently active MWS window."""
    if not system.process_wait(process, timeout):
        log.warning("%s did not start within %s seconds."
                                    %(process, str(timeout)))
        return None
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            app = Application().connect(path = process)
            break
        except pywinauto.application.ProcessNotFoundError:
            continue
    else:
        log.warning(f"Process {process} was not found within {timeout} seconds.")
        return False

    activate_coords = [4,170]
    while time.time() - start_time < timeout:
        for window in app.windows():
            if window.is_visible() and float(window.style()) > 0:
                pywinauto.mouse.click(coords=activate_coords)
                try:
                    active = app.active()
                    if active is not None:
                        return active
                except RuntimeError:
                    log.debug(f"{window} not active after clicking {activate_coords}.")
                    pass
    else:
        log.warning(f"{process} was found, but couldn't activate and retrieve its window within {timeout} seconds.")    

def init_sub_menu2():
    """Connect to a submenu with a different process name from the top-level menu."""
    global process, process_conn
    if process2 is not None:
        process = process2
        p = get_active_window()
        if p is not None:
            process_conn = p
    elif current_menu == "card configuration":
        process_conn = Application().connect(path = process)
    else:
        log.debug("init_sub_menu2 not defined for %s menu." % current_menu)

def main_window():
    """
    This function returns a connection to mainWindow
    that can be used to navigate the MWS menu.
    """
    if FindWindow(None, 'MainWindow'):
        main = Application(backend = 'uia').connect(title_re = 'MainWindow')
        return main['MainWindow']
    else:
        return None  

def get_control(control, tab=None, timeout=default_timeout):
    """
    Directly access a control (text box, check box, button, etc) in the current menu.
    Args:
        control: (str) The key of the desired control in controls.json.
              This is usually whatever text the control is labeled with in Passport.
        tab: (str) Which tab the desired control lives in. You only need to specify this for controls
              which have the same name but are in different tabs/submenus. Use a list to specify multiple sublevels.
        timeout: (int) How many seconds to wait for the control to exist on the screen.
    Returns: (pywinauto.application.WindowSpecification) Wrapper object for the desired control,
             or None if the control can't be found or is inactive.
    Throws:
        ControlNotFoundError, ControlAmbiguousError
    Examples:
        >>> get_control("Store Number")
        <pywinauto.application.WindowSpecification object at 0x02BE9710>
        >>> get_control("Default System Theme", "International")
        <pywinauto.application.WindowSpecification object at 0x00B19250>
        >>> get_control("Not A Valid Control")
        app.framework.mws.ControlNotFoundError: Control name Not A Valid Control was not found.
        >>> get_control("Password Required") # while not on Password tab
        Password Required control is not currently on screen. Try switching to the top
        level submenu or ensure the correct tab is specified.
        >>> set("Loyalty Provider Name", ["General", "Page1"])
        <pywinauto.application.WindowSpecification object at 0x02CE65F0>
    """
    class ControlNotFoundError(Exception):
        pass
    class ControlAmbiguousError(Exception):
        pass
    def get_ctrl_wrapper(ctrl_id):
        # Differentiate between int control ID and str control name
        if type(ctrl_id) is int:
            return process_conn.window(control_id=ctrl_id)
        elif type(ctrl_id) is str:
            return process_conn[ctrl_id]
        else:
            raise ControlNotFoundError(f"{control} maps to an invalid control id type: {type(ctrl_id)}")

    data = controls
    # Look in desired submenu if specified
    if tab is not None:
        if type(tab) is not list:
            tab = [tab]
        for t in tab:
            data = data[t]

    # Get control ID
    try:
        resolved_control = data[control] # Prioritize a top level control
    except KeyError:
        resolved_control = search_dict(data, control) # Search through lower levels
        if len(resolved_control) == 0:
            raise ControlNotFoundError("Control name %s was not found." % control)
        elif len(resolved_control) > 1:
            raise ControlAmbiguousError("%s matched multiple control IDs: %s. Please specify the "
                                        "tab parameter for the desired control." % (control, resolved_control))
        resolved_control = resolved_control[0]

    ctrl_wrapper = get_ctrl_wrapper(resolved_control)

    start_time = time.time()
    while time.time() - start_time <= timeout:
        try:
            ctrl_wrapper.control_id()
            break
        except:
            create_connection()           
            try:
                ctrl_wrapper = get_ctrl_wrapper(resolved_control)
                ctrl_wrapper.control_id()
                break
            except:
                init_sub_menu2()                
                try:
                    ctrl_wrapper = get_ctrl_wrapper(resolved_control)
                    ctrl_wrapper.control_id()
                    break
                except Exception as e:
                    last_e = e
    else:
        log.warning(f"Couldn't get the control for {control}. Raising the most recent exception.")
        raise last_e

    # Special case to connect to submenu with different exe if it's available. Couldn't find a cleaner way to do it.
    # Check if a second exe exists, if the current exe is different from it, and if the exe is running.
    if process2 is not None and process != process2 and system.process_wait(process2, 0):
        init_sub_menu2()
        ctrl_wrapper = get_ctrl_wrapper(resolved_control)

    timeout = timeout - (time.time() - start_time)
    if timeout < 0 :
        timeout = 0 # So we won't time out without trying once
    start_time = time.time()
    while time.time() - start_time <= timeout:
        if is_inbounds(ctrl_wrapper.rectangle().mid_point()):
            break
    else:
        print(f"{control} control is not currently on screen. Please ensure you are on the correct tab or try specifying the tab parameter.")
        return None

    return ctrl_wrapper

def search_dict(data, key):
    """
    Recursively search a dictionary for the desired key.
    Helper function for get().
    Args:
        data: (dict) The dict to search.
        key: (str) The key to search for.
    Returns: 
        list: The value(s) associated with the key.
    Examples:
        >>> search_dict({"General": {"Store Number": 32, "Store Name": 31}, "Password": {"Password Required": "SSCheckWndClass16"}}, "Store Name")
        31
    """
    if type(data) is not dict:
        return []
    values = []
    try:
        ret = data[key]
        if type(ret) is not dict:
            values.append(ret)
    except KeyError:
        pass
    for submenu in data.keys():
        ret = search_dict(data[submenu], key)
        if ret is not None and type(ret) is not dict:
            values.extend(ret)
    return values

def recover():
    """
    Try to back out of the menu we are currently in by pressing navigation buttons,
    using controls.json for instructions on what to press.
    Returns: 
        bool: True if successful
    Examples:
        >>> recover()
        True
    """
    try:
        recover_seqs = controls["recover"]
    except (KeyError, TypeError):
        raise ConnException("Recover not implemented for %s menu." % current_menu)

    # Each recover method consists of one or more sequences of button clicks.
    # Try each sequence, checking for success at the end of each one.
    for i in range(len(recover_seqs)):
        success = False
        for j in range(len(recover_seqs[i])):
            main = False
            if j == len(recover_seqs[i]) - 1:
                # End of a recover sequence. See if we succeeded after clicking
                main = True
            try:
                success = click_toolbar(recover_seqs[i][j], main=main, main_wait=3) and main
            except Exception as e:
                if "Navigation to the main screen failed" in str(e):
                    break # Finished sequence and it didn't work, try the next sequence
                elif "Unable to find" in str(e):
                    continue # Couldn't find a button in the sequence, keep going (we might have started partway through a sequence)
                else:
                    log.warning(f"Unexpected error recovering from {current_menu}: {e}")
                    break
        if success:
            return True
    else:
        raise ConnException("Recovery from %s unsuccessful" % current_menu)

def set_value(control, value=None, tab=None, timeout=default_timeout, list=None):
    """
    Set the value of an editable control in the current MWS menu.
    Args:
        control: (str) The name of the control in controls.json
        value: (str/bool) The value to set the control to (a string for text fields/drop-downs, or a boolean for checkbox)
        tab: (str) Which tab the desired control lives in. You only need to specify this for controls
              which have the same name but are in different tabs/submenus. Use a list to specify multiple sublevels.
        timeout: (int) Time to wait for the control to be ready in seconds
        list: (str) The controls.json name of the list control that the checkbox lives in, if applicable
    Returns:
        bool: True if success, False if failure
    Examples:
        >>> set_value("Address Line 1", "7300 W Friendly Ave.")
        True
        >>> set_value("Minimum Password Length", 2, "Password")
        True
        >>> set_value("Default System Theme", "Passport Retro") # while not on International tab
        False
        >>> set_value("Loyalty Provider Name", "Tank Bank", ["General", "Page1"])
        True
        >>> set_value("Password Required", True)
        True
    """
    log.debug(f"Setting {control} with {value}")
    if list is not None:
        ctrl = get_control(list, tab, timeout=timeout)
    else:
        ctrl = get_control(control, tab, timeout=timeout)
    class_name = ctrl.friendly_class_name().lower()
    if class_name == 'edit' or class_name == 'msmaskwndclass' or class_name == 'richtextwndclass' or class_name == 'dtpicker20wndclass':
        return set_text(ctrl, value, tab, timeout)
    elif class_name == "sscheckwndclass" or class_name == 'checkbox' or list is not None:
        if type(value) is not bool:
            raise TypeError(f"{type(value)} is invalid for checkboxes. Please provide a boolean (True/False)")
        return select_checkbox(ctrl, value, tab, list) if list is None else select_checkbox(control, value, tab, list)
    elif class_name == 'listview' or class_name == 'listbox' or class_name == 'combobox':
        # Using type([]) here because we redefined list... maybe change the param name in future.
        if type(value) is not str and type(value) is not type([]) and type(value) is not tuple:
            raise TypeError(f"{type(value)} is invalid for lists/combo boxes. Please provide a string/list/tuple")
        return select(ctrl, value, tab)
    elif class_name == "ssoptionwndclass":
        if value is not None and value is not True:
            log.warning(f"Radio buttons cannot be set to {value}. Please specify True or leave the value blank.")
            return False
        return select_radio(ctrl, tab)
    else:
        log.warning(f"Unrecognized control class: {class_name}. Trying to set text anyway...") 
        return set_text(ctrl, value, tab, timeout)

def get_value(control, tab=None, timeout=default_timeout, list=None):
    """
    Get the value of an editable control in the current MWS menu.
    Args:
        control: (str) The name of the control in controls.json
        tab: (str) Which tab the desired control lives in. You only need to specify this for controls
              which have the same name but are in different tabs/submenus. Use a list to specify multiple sublevels.
        timeout: (int) Time to wait for the control to be ready in seconds
        list: (str) The controls.json name of the list control that the checkbox lives in, if applicable
    Returns: (str/list/bool) The current value of the control. For edits this is a string,
             for checkboxes/radio buttons a boolean, for list views a list containing its elements,
             for drop-downs a list containing the currently selected item followed by all of the items in the drop-down.
    Examples:
        >>> get_value("Address Line 1")
        '7300 W Friendly Ave.'
        >>> get_value("Default System Theme", tab="International")
        'Passport Modern'
        >>> get_value("Loyalty Provider Name", ["General", "Page1"])
        'Tank Bank'
        >>> get_value("Password Required")
        True
    """
    if list is not None:
        ctrl = get_control(list, tab, timeout=timeout)
    else:
        ctrl = get_control(control, tab, timeout=timeout)
    class_name = ctrl.friendly_class_name().lower()
    text_fields = ["edit", "listview", "listbox", "combobox", "richtextwndclass", "dtpicker20wndclass"]
    if class_name == "sscheckwndclass" or class_name == "checkbox" or list is not None:
        return status_checkbox(ctrl, tab, list) if list is None else status_checkbox(control, tab, list)
    elif class_name in text_fields:
        return get_text(ctrl, tab)
    elif class_name == "ssoptionwndclass":
        return status_radio(ctrl, tab)
    return ctrl.texts()[0]

def set_text(control, text, tab=None, timeout=1):
    """
    Set the text of a text box-type control in the current MWS menu.
    Args:
        control: (str) The name of the control in controls.json
        text: (str) The text to be sent to the control
        tab: (str) Which tab the desired control lives in. You only need to specify this for controls
              which have the same name but are in different tabs/submenus. Use a list to specify multiple sublevels.
        timeout: (int) Time to wait for a control to be ready in seconds
    Returns:
        bool: True if successful
    Examples:
        >>> set_text("Address Line 1", "7300 W Friendly Ave.")
        True
        >>> set_text("Pouch/Envelope Colors List", "White")
        True
        >>> set_text("Default System Theme", "Passport NotATheme")
        False
    """
    text = str(text)
    log.debug('Setting %s to value %s' %(control, text))
    if type(control) is not pywinauto.application.WindowSpecification:
        control = get_control(control, tab, timeout=timeout)
    try:
        class_name = control.friendly_class_name().lower()
    except Exception as e:
        log.warning(e)
        raise ConnException('Unable to set text for %s' %control)
    if class_name == 'msmaskwndclass' or class_name == 'richtextwndclass':
        try:
            # We have to manually create an EditWrapper around this control and click on it to set text
            control.wait('ready', timeout)
            pywinauto.controls.win32_controls.EditWrapper(control).click().set_text(text)
            return True
        except Exception as e:
            log.warning(e)
            return False
    elif class_name == 'dtpicker20wndclass': # No good way to interact with this. Set it manually...
        control.click(coords=(10,0)) # Click on the hour segment first
        control.send_keystrokes(text)
        # Check if the time string has AM/PM period
        # Matches HH:MM:SS AM and HH:MM PM
        if re.match(r'.+ [AP]M', text):
            period = text.split(' ')[1]

            # At this point we should be at the MM or SS block depending on the string type
            control.send_keystrokes('{VK_RIGHT}%s'%period)
    else:
        try:
            control.wait('ready', timeout).set_text(text)
            return True
        except Exception as e:
            log.warning(e)
            return False
    
def get_text(control, tab=None, timeout=default_timeout):
    """
    Get the text from an editable control in the current MWS menu.
    Args:
        control: (str) The name of the control in controls.json
        tab: (str) Which tab the desired control lives in. You only need to specify this for controls
              which have the same name but are in different tabs/submenus. Use a list to specify multiple sublevels.
        timeout: (int) Time to wait for a control to be ready in seconds
    Returns:
        (str/list) The text in the control. For edits this is a string, for list views a list containing its elements,
        for drop-downs a list containing the currently selected item followed by all of the items in the drop-down.
    Examples:
        >>> get_text("Address Line 1")
        '7300 W Friendly Ave.'
        >>> get_text("Pouch/Envelope Colors List")
        [['Black'], ['White'], ['Green']]
        >>> get_text("Default System Theme")
        ['Passport Modern', 'Passport Classic', 'Passport Modern', 'Passport Retro']
        >>> get_text("Departments") # in Department Maintenance
        [['         1', 'Dept 1'], ['         2', 'Dept 2'], ['         3', 'Dept 3'], [
        '         4', 'Dept 4'], ['         5', 'Dept 5'], ['         6', 'Dept 6'], ['
                7', 'Dept 7'], ['         8', 'Dept 8'], ['         9', 'Dept 9'], ['
             10', 'Dept 10'], ['        11', 'Dept 11'], ['        12', 'Dept 12'], ['
              13', 'Dept 13'], ['        14', 'Dept 14'], ['        15', 'Dept 15'], ['
               16', 'Dept 16'], ['        17', 'asdfasdfdsaf']]
    """
    if type(control) is not pywinauto.application.WindowSpecification:
        control = get_control(control, tab, timeout=timeout)
    class_name = control.friendly_class_name().lower()
    if class_name == 'edit':
        try:
            value = control.texts()[0]
            log.info('Current value for %s is %s.' %(control, value))
            return value
        except AttributeError:
            raise ConnException(f"{control} has no texts() method.")
    elif class_name == "listview":
        texts = control.texts()
        column_num = control.column_count()
        row_array = []
        for element in range(1, len(texts), column_num):
            column_array = []
            for col in range(1, column_num + 1):
                column_array.append(texts[element + col - 1])
            row_array.append(column_array)
        return row_array
    elif class_name == 'listbox':
        texts = control.texts()
        texts.remove('')
        return texts
    else:
        try:
            value = control.texts()
            log.info('Current value for %s is %s.' %(control, value))
            return value
        except AttributeError:
            raise ConnException(f"{control} has no texts() method.")

def select(name, text, tab=None, timeout=default_timeout):
    """
    Select an item from a list or drop-down menu.
    Args:
        control: (str) The name of the control in controls.json
        text: (str) The text of the list item to select
        tab: (str) Which tab the desired control lives in. You only need to specify this for controls
              which have the same name but are in different tabs/submenus. Use a list to specify multiple sublevels.
        timeout: (int) Time to wait for a control to be ready in seconds
    Returns: 
        bool: True if successful
    Examples:
        >>> select("Default System Theme", "Passport Modern")
        True
        >>> select("Pouch/Envelope Colors List", "White")
        True
        >>> select("Default System Theme", "Passport NotATheme")
        False
    """
    if type(name) is not pywinauto.application.WindowSpecification:
        control = get_control(name, tab, timeout=timeout)
    else: # We also accept a pywinauto object, but this is for the framework, not scripts
        control = name
    class_name = control.friendly_class_name().lower()
    if class_name == 'listview':
        if type(text) == list or type(text) == tuple:
            text = [item.strip() for item in text]
            row_list=[]
            row_text_list=[]
            #Going through each item in the listview and separating them by 
            #row
            for i in range(0, len(control.items()), control.column_count()):
                temp_row=[]
                temp_text_row=[]
                #Appending the row together into a list and appending into 
                #the big list (row_list and row_text_list)
                for j in range(i, i+control.column_count()):
                    temp_row.append(control.items()[j])
                    temp_text_row.append(control.items()[j].text().strip())
                row_list.append(temp_row)
                row_text_list.append(temp_text_row)
                temp_row = []
                temp_text_row = []
            #Checking to see if the user's list is a subset of a row.
            #If it is, then click the row.
            for i in range(len(row_text_list)):
                if all(text.count(item) <= row_text_list[i].count(item) for item in text):
                    log.debug("Elements %s were found in row %s. Clicking"
                                            "the list item." %(text, 
                                            row_text_list[i]))
                    row_list[i][0].click_input()
                    if control.get_selected_count() > 1:
                        #This is to try again for sanity's sake.
                        row_list[i][0].click_input()
                    return True
            log.warning("No list row contained all elements of %s." %text)
        else:
            try:
                control.wait('ready', timeout).item(text).click()
                return True
            except Exception as e:
                log.warning(e)
                return False
    else:
        try:
            control.wait('ready', timeout).select(text)
            return True
        except Exception as e:
            log.warning(e)
            return False

def get_checkbox_coords(name, tab=None, list=None):
    """
    Helper function to find coords of a checkbox from its control rectangle.
    Args:
        name: (str) The text of the checkbox in controls.json (should usually match the text in Passport),
                    or the exact text of the checkbox if it lives in a list
        tab: (str) Which tab the desired control lives in. You only need to specify this for controls
              which have the same name but are in different tabs/submenus. Use a list to specify multiple sublevels.
        list: (str) The controls.json name of the list control that the checkbox lives in, if applicable
    Returns:
        (tuple) Coordinates for the probable center of the checkbox
    Examples:
        >>> get_checkbox_coords("Password Required")
        (62, 263)
    """
    if list is not None:
        # Get the rectangles of both the list and the checkbox item within the list
        control = get_control(list, tab)
        left_offset = 12 # We also need a larger offset
        list_rect = control.rectangle()
        rect = control.select(name).rectangle()
        # List item's rect is relative to the list. Make it absolute by combining with the list's rect
        rect.left += list_rect.left
        rect.right += list_rect.left
        rect.top += list_rect.top
        rect.bottom += list_rect.top
    else:
        left_offset = 7
        # Get the rectangles of both the list and the checkbox item within the list
        if type(name) is not pywinauto.application.WindowSpecification:
            control = get_control(name, tab)
            if control is None:
                return None
        else: # We also accept a pywinauto object, but this is for the framework, not scripts
            control = name
        rect = control.get_properties()['rectangle']
    return (rect.left+left_offset, rect.mid_point().y)
    # Probably add a right-side param to this.

def wait_for_button(button, timeout = 30):
    """
    Helper function to wait until button is visible on screen.
    Args:
        button: (str) The button text
    Returns:
        (bool) Whether the button was found or timed out waiting
    Examples:
        >>> wait_for_button("Add")
        True
    """
    # Let's go ahead and wait in between
    start_time = time.time()

    main_window = Application(backend="uia").connect(path="Eclipse.exe")['MainWindow']

    while time.time() - start_time < timeout:
        try:
            if main_window.window(title_re=f"button(?i){button.replace(' ', '')}", control_type="Button").is_visible():
                break
        except pywinauto.findwindows.ElementNotFoundError:
            log.debug(f"Could not find {button} button")
    else:
        log.error(f"Timed out waiting for {button} to appear.")
        return False

    return True


def status_checkbox(name, tab=None, list=None, timeout=default_timeout, disabled=False):
    """
    Check the status of a checkbox or radio button.
    Args:
        name: (str) The text of the checkbox in controls.json (should usually match the text in Passport),
                    or the exact text of the checkbox if it lives in a list
        tab: (str) Which tab the desired control lives in. You only need to specify this for controls
              which have the same name but are in different tabs/submenus. Use a list to specify multiple sublevels.
        list: (str) The controls.json name of the list control that the checkbox lives in, if applicable
        timeout: (int) How many seconds to wait for the checkbox to be on screen
        disabled: (bool) Set to True if you want to read a disabled (greyed out) checkbox or radio.
    Returns:
        (bool) True if checked, False if not, None if checkbox isn't visible or is disabled
    Examples:
        >>> status_checkbox("Password Required")
        True
        >>> status_checkbox("Enable Enhanced Remote Support Passwords", tab="Password")
        False
        >>> status_checkbox("No Tax", list="Tax Rates")
        True
        >>> status_checkbox("Allow manual entry of birth date") # While not in Age Verification tab
        None
    """
    # Get coordinates of the checkbox from the control's rectangle
    if type(name) is not pywinauto.application.WindowSpecification and list is None:
        control = get_control(name, tab)
        if control is None:
            return None
    else: # We also accept a pywinauto object, but this is for the framework, not scripts
        control = name
    # We can get status directly from a ListBox control...
    if list is not None:
        list_ctrl = get_control(list, tab)
        if list_ctrl.friendly_class_name().lower() == "listbox":
            texts = list_ctrl.texts()
            for i in list_ctrl.selected_indices():
                if texts[i+1] == name:
                    return True
            else:
                return False

    coords = get_checkbox_coords(control, tab, list)

    # Check if control is off screen (means we are on the wrong tab)
    if not is_inbounds(coords, timeout=timeout):
        log.warning("Checkbox or radio button not visible")
        return None

    # Check for black pixels in the checkbox
    x = coords[0]
    y = coords[1]
    x2 = x + 3
    y2 = y + 3
    img = ImageGrab.grab()
    for vert in range(y, y2, 1):
        for horz in range(x, x2, 1):
            found_color = img.getpixel((horz, vert))
            found_color = '%02x%02x%02x' % found_color
            if found_color == "000000":
                if disabled:
                    return False
                else:
                    return True
            elif found_color == "808080":
                if disabled:
                    return True
                else:
                    print(f"{name} checkbox/radio is disabled.")
                    return None
            elif found_color == "d4d0c8":
                if disabled:
                    return False
                else:
                    print(f"{name} checkbox/radio is disabled.")
                    return None
    return False

def is_checkbox_enabled(name, tab=None, list=None, timeout=default_timeout):
    """
    Get the enabled/disabled status of a checkbox.
    Args:
        name: (str) The text of the checkbox in controls.json (should usually match the text in Passport),
                    or the exact text of the checkbox if it lives in a list
        tab: (str) Which tab the desired control lives in. You only need to specify this for controls
              which have the same name but are in different tabs/submenus. Use a list to specify multiple sublevels.
        list: (str) The controls.json name of the list control that the checkbox lives in, if applicable
        timeout: (int) How many seconds to wait for the checkbox to be on screen
    Returns:
        bool: True if the checkbox is enabled, False if disabled
    Examples:
        >>> is_checkbox_enabled("Alpha Numeric")
        True
        >>> is_checkbox_enabled("Embedded price is four digits in length")
        False
    """
    # Get coordinates of the checkbox from the control's rectangle
    if type(name) is not pywinauto.application.WindowSpecification:
        control = get_control(name, tab)
        if control is None:
            return None
    else: # We also accept a pywinauto object, but this is for the framework, not scripts
        control = name

    coords = get_checkbox_coords(control, tab, list)

    # Check for grey pixels in the checkbox
    x = coords[0]
    y = coords[1]
    x2 = x + 3
    y2 = y + 3
    img = ImageGrab.grab()
    for vert in range(y, y2, 1):
        for horz in range(x, x2, 1):
            found_color = img.getpixel((horz, vert))
            found_color = '%02x%02x%02x' % found_color
            if found_color == "808080" or found_color == "d4d0c8":
                return False
    return True

def select_checkbox(name, check=True, tab=None, list=None, timeout=default_timeout):
    """
    Set a checkbox to checked or unchecked.
    Args:
        name: (str) The text of the checkbox in controls.json (should usually match the text in Passport),
                    or the exact text of the checkbox if it lives in a list
        check: (bool) Whether to set the checkbox to checked or unchecked
        tab: (str) Which tab the desired control lives in. You only need to specify this for controls
              which have the same name but are in different tabs/submenus. Use a list to specify multiple sublevels.
        list: (str) The controls.json name of the list control that the checkbox lives in, if applicable
        timeout: (int) How many seconds to wait for the checkbox to be on screen
    Returns:
        (bool) Success/failure
    Examples:
        >>> select_checkbox("Password Required")
        True
        >>> select_checkbox("Enable Enhanced Remote Support Passwords", False, tab="Password")
        True
        >>> select_checkbox("No Tax", list="Tax Rates")
        True
        >>> select_checkbox("Allow manual entry of birth date") # While not in Age Verification tab
        False
    """
    # We can interact with ListBox checkboxes directly...
    if list is not None:
        list_ctrl = get_control(list, tab)
        if list_ctrl.friendly_class_name().lower() == "listbox":
            try:
               list_ctrl.select(name, check)
               return True
            except ValueError:
                log.warning(f"Unable to select {name} checkbox from {list}.")
                return False

    status = status_checkbox(name, tab, list, timeout)
    if status is None:
        return False
    elif status != check:
        if list is not None:
            pywinauto.mouse.click(coords = get_checkbox_coords(name, tab, list))
        else:
            if type(name) is pywinauto.application.WindowSpecification:
                name.click()
            else:
                get_control(name,tab).click()
    return True

def status_radio(name, tab=None, timeout=default_timeout):
    """
    Check the status of a radio button.
    Args:
        name: (str) The text of the radio button in controls.json (should match the text in Passport)
        tab: (str) Which tab the desired control lives in. You only need to specify this for controls
              which have the same name but are in different tabs/submenus. Use a list to specify multiple sublevels.
        timeout: (int) How many seconds to wait for the checkbox to be on screen
    Returns:
        (bool) True if checked, False if not
    Examples:
        >>> status_radio("Use coupon keys to track store coupons")
        True
        >>> status_radio("Track store coupons in a single department", tab="Store Coupon")
        False
        >>> status_radio("Embedded price is four digits in length") # While not in Embedded Barcode tab
        None
    """
    return status_checkbox(name, tab, timeout=timeout)

def select_radio(name, tab=None, timeout=default_timeout):
    """
    Click on a radio button.
    Args:
        name: (str) The text of the radio button in controls.json (should match the text in Passport)
        tab: (str) Which tab the desired control lives in. You only need to specify this for controls
              which have the same name but are in different tabs/submenus. Use a list to specify multiple sublevels.
        timeout: (int) How many seconds to wait for the checkbox to be on screen
    Returns:
        (bool) True if success, False if failure
    Examples:
        >>> select_radio("Use coupon keys to track store coupons")
        True
        >>> select_radio("Track store coupons in a single department", tab="Store Coupon")
        True
        >>> status_radio("Embedded price is four digits in length") # While not in Embedded Barcode tab
        False
    """
    if type(name) is not pywinauto.application.WindowSpecification:
        control = get_control(name, tab, timeout=timeout)
    else: # We also accept a pywinauto object, but this is for the framework, not scripts
        control = name
    if control is None:
        return False
    rect = control.get_properties()['rectangle']
    if not is_inbounds((rect.left+6, rect.mid_point().y), timeout=timeout):
        log.warning("Radio button not visible")
        return False
    control.click()
    return True

def is_inbounds(coords, res=(1024, 768) if is_high_resolution() else (800, 600), timeout=0):
    """
    Check if a point is on the screen (helper function for get_control)
    Args:
        coords: (tuple) Coordinates of the point to check
        res: (tuple) Resolution of the screen
        timeout: (int) How many seconds to wait for the point to be in-bounds
    Returns:
        bool: True if in-bounds within the time limit, else False
    Examples:
        >>> is_inbounds((254, 138))
        True
        >>> is_inbounds((938, 543))
        False
        >>> is_inbounds((938, 543), (1920, 1080))
        True
    """
    start_time = time.time()
    while time.time() - start_time <= timeout:
        if coords[0] > 0 and coords[1] > 0 and coords[0] < res[0] and coords[1] < res[1]:
            return True
    else:
        return False

def click(name, tab=None, timeout=default_timeout):
    """
    Click on a control. Uses a physical mouse click because not all buttons support click events.
    Args:
        name: (str) The text of the control in controls.json (should match the text in Passport)
        tab: (str) Which tab the desired control lives in. You only need to specify this for controls
              which have the same name but are in different tabs/submenus. Use a list to specify multiple sublevels.
        timeout: (int) How many seconds to wait for the control to be active and on screen
    Returns:
        (bool) True if success, False if failure
    Examples:
        >>> click("New")
        True
        >>> click("Change", tab="Pouch/Envelope Colors")
        True
        >>> click("Delete") # While not on pouch/envelope tab
        False
    """
    if type(name) is not pywinauto.application.WindowSpecification:
        control = get_control(name, tab, timeout=timeout)
    else: # We also accept a pywinauto object, but this is for the framework, not scripts
        control = name
    if control is None:
        return False
    control.click_input()
    return True

def config_flexgrid(control, config, offset, tab = None, max_dist = 0, instances = {}):
    """
    Configure a FlexGrid control (like the one in Department Maintenance > Tender Restrictions) using OCR.
    Note that Period Maintenance > Store Close Reports and similar grids are NOT FlexGrids.
    Args:
        control: (str) The name of the FlexGrid control in controls.json.
        config: (dict/list) A dictionary mapping the names of values (str) to their desired settings (bool/list of bools).
        offset: (int/list) Pixel distance from the left edge of the FlexGrid to the left edge of the Xs,
                or a list of offsets to configure multiple columns.
        tab: (str) The name of the tab the FlexGrid control is on. Defaults to None. It is required for some lists
        instances: (dict) A str: int map indicating which instance of each string to use. Needed to configure rows such as
                   "Fuel Grade Movement" whose text is present in multiple other rows. See examples.
    Returns:
        bool: True if all fields were found and configured. False if a field couldn't be found.
    Examples:
        >>> cfg = {"driveOff": True, "houseCharges": True, "outsideAuxilliaryDebit": True}
        >>> config_flexgrid("Tender Restrictions List", cfg, department.DEPT_FG_OFFSET)
        True
        >>> cfg = {"Fuel Grade Movement by Till": [True, True], "Item Sales Movement by Till": [True, False], "Tax Level Movement by Till": [False, True] }
        >>> config_flexgrid("Document list", cfg, [back_office_interface.BO_FG_STORE_OFFSET, back_office_interface.BO_FG_SHIFT_OFFSET])
        True
        >>> cfg = {"Fuel Grade Movement": [True, True], "Item Sales Movement": [True, False], "Tax Level Movement by Till": [False, True] }
        >>> instances = { "Fuel Grade Movement": 5, "Item Sales Movement": 2 }
        >>> config_flexgrid("Document list, cfg, [back_office_interface.BackOfficeInterface.FG_STORE_OFFSET,
            back_office_interface.BackOfficeInterface.FG_SHIFT_OFFSET], instances)
        True
    """
    offset = [offset] if type(offset) is not list else offset

    # Scroll up
    get_control(control, tab).scroll("up", "end")
    
    # Object storing the coordinates of the list on the screen
    rectangle = get_control(control, tab).get_properties()['rectangle']
    
    # Calculate the bbox for the list rows that are visible
    # The height of list header is about 21px
    # The width of field column if provided via offset
    list_bbox = (rectangle.left, rectangle.top + 21, rectangle.left + offset[0], rectangle.bottom)

    # bbox of the last row currently visible in the list
    # The top edge of the row is about 22px up the bottom of the list 
    bot_row_bbox = (rectangle.left, rectangle.bottom - 22, rectangle.left + offset[0], rectangle.bottom)

    # Find how many rows are on the screen for scrolling purposes
    fields = OCR.OCRRead(bbox=list_bbox).split('\n')

    # Remove empty strings
    fields = list(filter(None, fields))

    # We don't have means to interact directly with FlexGrid. Use OCR instead.
    for field, settings in config.items():
        settings = [settings] if type(settings) is not list else settings
        try:
            instance = instances[field]
        except KeyError:
            instance = 1

        row_coords = None

        while row_coords is None:
            # Obtain potential coordinates
            row_coords = search_click_ocr(field, click_loc=OCR.LEFT, clicks=0, instance=instance, bbox=list_bbox, max_dist=max_dist)

            if row_coords:
                # Construct a bbox for the selected field to verify full match
                field_bbox = (list_bbox[0], row_coords[1] - 10, list_bbox[2],  row_coords[1] + 8)

                if field.replace(' ', '').lower() != OCR.OCRRead(bbox=field_bbox, psm=3).replace(' ', '').lower():
                    # Try other instances
                    row_coords = None
                
                    # Starting from i = 1 does repeat instance = 1 in some cases, but guarantees correct functionality
                    for i in range(1, 12):
                        row_coords = search_click_ocr(field, click_loc=OCR.LEFT, clicks=0, instance=i, bbox=list_bbox, max_dist=max_dist)

                        if row_coords == None:
                            # No other instances are there
                            break

                        # Construct a bbox for the selected field to verify full match
                        field_bbox = (list_bbox[0], row_coords[1] - 10, list_bbox[2],  row_coords[1] + 8)

                        if field.replace(' ', '').lower() != OCR.OCRRead(bbox=field_bbox, psm=3).replace(' ', '').lower():
                            # Wrong entry
                            row_coords = None
                        else:
                            # Target entry acquired
                            break
                
            # Scroll down by the number of visible rows if nothing was found during first iteration
            if not row_coords:
                # Get the text from the bottom row to check if we already hit the bottom
                bottom_row_text = OCR.OCRRead(bbox=bot_row_bbox)

                for _ in range(len(fields)):
                    get_control(control, tab).scroll("down", "line")
            

                if bottom_row_text == OCR.OCRRead(bbox=bot_row_bbox):
                    # We are at the bottom and nothing was found
                    log.warning(f"Couldn't find {field} in the FlexGrid.")
                    return False

        for i in range(len(settings)):
            # Check for the type of action
            # True and False mean 'check' and 'uncheck'
            # Other types of argument mean double click and type
            if type(settings[i]) is bool:
                x_coords = (row_coords[0]+offset[i], row_coords[1])
                x_bbox = (x_coords[0], x_coords[1]-10, x_coords[0]+20, x_coords[1]+7)
                if find_text_ocr('X', bbox=x_bbox, psm=10):
                    if not settings[i]:
                        log.debug(f"{field} column {i} is checked. Clicking to uncheck.")
                        pywinauto.mouse.click(coords=x_coords)
                    else:
                        log.debug(f"{field} column {i} is checked. Leaving it alone.")
                elif settings[i]:
                    log.debug(f"{field} column {i} is unchecked. Clicking to check.")
                    pywinauto.mouse.click(coords=x_coords)
                else:
                    log.debug(f"{field} column {i} is unchecked. Leaving it alone.")
            else:
                x_coords = (row_coords[0]+offset[i], row_coords[1])

                # Send double click
                pywinauto.mouse.double_click(coords=x_coords)

                # Erase the input, type new input in and Send Enter
                pywinauto.keyboard.send_keys('{BS 20}' + str(settings[i]) + '{ENTER}')

        get_control(control, tab).scroll("up", "end")


    return True

def read_flexgrid(control, fields, offset, instances):
    """
    Get the status of one or more fields in a FlexGrid control (like the one in Department Maintenance > Tender Restrictions) using OCR.
    Note that Period Maintenance > Store Close Reports and similar controls are NOT FlexGrids.
    Args:
        control: (str) The name of the FlexGrid control in controls.json.
        fields: (str) The text(s) of the rows to get the status of.
        offset: (int/list) Pixel distance from the left edge of the FlexGrid to the left edge of the Xs.
                Use a list of ints to get multiple columns at once.
        instances: (dict) A str: int map indicating which instance of each string to use. Needed to configure rows such as
                   "Fuel Grade Movement" whose text is present in multiple other rows. See examples.
    Returns:
        dict: The requested fields and a list of their values. None if a requested field can't be found.
    Examples:
        >>> fields = ["driveOff", "houseCharges", "outsideAuxilliaryDebit", "credit"]
        >>> read_flexgrid("Tender Restrictions List", fields, department.DEPT_FG_OFFSET)
        {"driveOff": [True], "houseCharges": [True], "outsideAuxilliaryDebit": [True], "credit": [False]}
        >>> fields = ["Fuel Grade Movement by Till", "Item Sales Movement by Till", "Tax Level Movement by Till"]
        >>> read_flexgrid("Document list", fields, [back_office_interface.BO_FG_STORE_OFFSET, back_office_interface.BO_FG_SHIFT_OFFSET])
        {"Fuel Grade Movement by Till": [True, True], "Item Sales Movement by Till": [True, False],
         "Tax Level Movement by Till": [False, True]}
        >>> fields = ["Fuel Grade Movement", "Item Sales Movement", "Tax Level Movement by Till"]
        >>> instances = { "Fuel Grade Movement": 5, "Item Sales Movement": 2 }
        >>> read_flexgrid("Document list, fields, [back_office_interface.BackOfficeInterface.FG_STORE_OFFSET,
            back_office_interface.BackOfficeInterface.FG_SHIFT_OFFSET], instances)
        {"Fuel Grade Movement": [True, True], "Item Sales Movement": [True, False], "Tax Level Movement by Till": [False, True] }
    """
    offset = [offset] if type(offset) is not list else offset
    ret = { field: [] for field in fields }
    for field in fields:
        try:
            instance = instances[field]
        except KeyError:
            instance = 1
        row_coords = search_click_ocr(field, click_loc=OCR.LEFT, clicks=0, instance=instance)
        if row_coords is None: # Scroll down and try again
            get_control(control).scroll("down", "end")
            row_coords = search_click_ocr(field, click_loc=OCR.LEFT, clicks=0, instance=instance)
            if row_coords is None:
                log.error(f"Couldn't find {field} in the FlexGrid.")
                return None
        for col_offset in offset:
            x_coords = (row_coords[0]+col_offset, row_coords[1])
            x_bbox = (x_coords[0], x_coords[1]-10, x_coords[0]+20, x_coords[1]+7)
            if find_text_ocr('X', bbox=x_bbox):
                ret[field].append(True)
            else:
                ret[field].append(False)
        get_control(control).scroll("up", "end")
    return ret

def click_toolbar(button, timeout=2, main=False, main_wait=10, submenu=False):
    """
    A function to click buttons in the side/top bar of the MWS (WPF portions).
    Args:
        button: (str) The text of the button that needs to be clicked.
        timeout: (int) The time in seconds that we should wait on the button to appear.
        main: (boolean) The function will search for the main screen within
                a given amount of time.
        main_wait: (int) How many seconds to wait to reach the main screen, if main is set to True.
        submenu: (bool) If True, re-create the MWS connection after clicking the button. Use this
                 when clicking a button that will open a submenu, such as Add in Register Setup,
                 to help avoid timing issues.
    Returns:
        boolean: True/False
    Examples:
        >>> click_toolbar("Save")
        True
        >>> click_toolbar("Yes", main=True)
        True
        >>> click_toolbar("Change", main=True)
        False
        >>> click_toolbar("INFO")
        True
    """
    try:
        main_window = Application(backend='uia').connect(path='Eclipse.exe')
    except pywinauto.application.ProcessNotFoundError:
        log.warning("Eclipse.exe not found - Passport is probably not running.")
        return False
    button_name = 'button%s' %(button)
    box = main_window['MainWindow']
    msg_window = box.window(auto_id="mainMessageWindow")
    if not msg_window.exists():
        log.warning("Passport is running but MWS toolbar was not found.")
        return False
    
    found = False
    start_time = time.time()
    while time.time() - start_time < timeout:
        if msg_window.is_visible():
            for child in msg_window.children():
                if "button" in child.friendly_class_name().lower():
                    child_text = child.texts()[0].lower().replace(" ", "")
                    button_name = button_name.lower().replace(" ","")
                    if child_text == button_name and child.is_enabled():
                        child.click()
                        log.debug('Clicked %s.' %button)
                        if not main:
                            if submenu:
                                create_connection()
                            return True
                        found = True
                        break
        if not found:
            for child in box.children():
                if 'button' in child.friendly_class_name().lower():
                    child_text = child.texts()[0].lower()
                    child_text = child_text.replace(" ", "")
                    button_name = button_name.lower().replace(" ", "")
                    if child_text == button_name and child.is_enabled():
                        child.click()
                        log.debug('Clicked %s.' %button)
                        if not main:
                            if submenu:
                                create_connection()
                            return True
                        found = True
                        break
        if found:
            break
    else:
        raise ConnException("Unable to find %s." %button)

    log.debug("Looking for the MWS search bar.")
    try:
        box.edit1.wait('ready', main_wait)
        return True
    except pywinauto.timings.TimeoutError:
        raise ConnException(f"Navigation to the main screen failed. Could not find the MWS Search bar within {main_wait} seconds.")

def click_and_drag(start_name, end_name, tab=None, start_list=None, end_list=None):
    """
    Click and drag the mouse from one control to another. Use not recommended unless the application requires it.
    Args:
        start_name: (str) The controls.json name of the control to drag from, or the name of the list item.
        end_name: (str) The controls.json name of the control to drag to, or the name of the list item.
        tab: (str) The tab that the controls live in. Only needed if similarly named controls live in other tabs of the same application.
        start_list: (str) The controls.json name of the list control that the list item to drag from lives in, if applicable
        end_list: (str) The controls.json name of the list control that the list item to drag to lives in, if applicable
    Returns: 
        None (please do your own verification depending on use case)
    Examples:
        >>> click_and_drag("image.jpeg", "Selected Media File(s)", start_list="Available Media File(s)") # Drag image.jpeg from Selected Media Files to Available Media Files
        >>> click_and_drag("image2.jpeg", "image3.jpeg", start_list="Available Media File(s)", end_list="Available Media File(s)") # Drag image2.jpeg to image3.jpeg in Available Media Files (swaps their positions)
    """
    start_control = start_list if start_list else start_name
    end_control = end_list if end_list else end_name
    if type(start_control) is not pywinauto.application.WindowSpecification:
        start_control = get_control(start_control)
    if type(end_control) is not pywinauto.application.WindowSpecification:
        end_control = get_control(end_control)

    # Coords are relative to their controls. If dragging from/to a list item, need to do a little extra to get the item's coords.
    start_coords = start_control.get_item_rect(start_name).mid_point() if start_list else (0, 0)
    end_coords = end_control.get_item_rect(end_name).mid_point() if end_list else (0, 0)

    start_control.press_mouse_input(coords=start_coords, absolute=False)
    end_control.move_mouse_input(coords=end_coords, absolute=False) 
    end_control.release_mouse_input(coords=end_coords, absolute=False)
    
def get_top_bar_text():
    """
    Grab the text in the message box at the top of the MWS.
    Args:
        None
    Returns:
        str: The text contents of the message box.
    Example:
        >>> get_top_bar_text()
        'Do you want to save changes?'
    """
    app = Application(backend='uia').connect(path="Eclipse.exe")
    window = app['MainWindow']
    try:
        return window.window(auto_id="scrollViewerMessage").texts()[0]
    except pywinauto.findwindows.ElementNotFoundError:
        log.info("Can't get MWS top bar text because the top bar is not available.")
        return None

def verify_top_bar_text(text, timeout=10):
    """
    Check if a desired message is present in the top bar of the MWS.
    Args:
        text: (str) The desired message.
        timeout: (int) The amount of time to wait for the message to be present.
    Returns:
        bool: True if the desired message is found, else False
    Examples:
        >>> verify_top_bar_text("Do you want to save changes?")
        True
        >>> verify_top_bar_text("This text isn't in the top bar")
        False
    """
    app = Application(backend = 'uia').connect(path = "Eclipse.exe")
    window = app['MainWindow']
    text = text.lower()
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            msg_viewer_str = window.window(auto_id="scrollViewerMessage").texts()[0].lower()
        except pywinauto.findwindows.ElementNotFoundError:
            top_bar_found = False
            continue
        top_bar_found = True
        if text == msg_viewer_str:
            log.debug(f"'{text}' matches '{msg_viewer_str}' in the MWS top bar.")
            return True

    log.info(f"'{text}' was not found in the MWS top bar within {timeout} seconds.")
    log.info(f"The last message in the top bar was {msg_viewer_str}.")
    if not top_bar_found:
        log.info(f"The MWS top bar was not available at the end of the timeout.")

    return False
    

LOW_RES_TAB_BBOXES = ((8, 138, 640, 223), (10, 225, 640, 260))
HIGH_RES_TAB_BBOXES = ((76, 259, 742, 307), (76, 180, 742, 234), (76, 255, 742, 287))
def select_tab(tab, instance=1, bboxes=None, tolerance ='808080'):
    """
    Switch to another tab of the current menu.
    Uses OCR to decide where to click, as MWS tabs have no
    static unique identifiers on the back end.
    Args:
        tab: (str) Text of the tab to switch to.
        instance: (int) The instance number to use in case of ambiguity. Defaults to 1
        bbox: (tuple) Bounding box(es) to look for the tabs in. Can specify multiple (tuple of tuples) or just one. Defaults are provided.
    Returns: 
        bool: True/false for success/failure
    Examples:
        >>> select_tab("Password")
        True
        >>> select_tab("NotATab")
        False
    """
    if bboxes is None:
        bboxes = HIGH_RES_TAB_BBOXES if is_high_resolution() else LOW_RES_TAB_BBOXES
    elif isinstance(bboxes[0], int):
        bboxes = [bboxes]
    try:
        tab = controls[tab]["ocr_str"] # Check if OCR string differs from full text of the tab
    except KeyError:
        pass
    try:
        filter = controls[tab]["filter_str"] # Check if there is a tab or tab we need to ignore, i.e. "Tank - Product to Dispenser" when searching for "Product"
    except KeyError:
        filter = []
    for bbox in bboxes:
        if OCR.searchAndClick(tab, tolerance=tolerance, occurrence=instance, bbox=bbox, timeout=5, maxDist=1, filter_strings=filter) is not None:
            global current_tab
            current_tab = tab
            time.sleep(1) # Give the tab a moment to load. Helps with timing of other functions (esp. get_control)
            return True
    else:
        return False

#@TODO Make this support custom credentials...
def sign_on():
    """
    Sign on to the MWS as 91/91.
    Args:
        None
    Returns:
        bool: True/False for success/failure
    Examples:
        >>> mws.sign_in()
        True
    """
    log.debug("[sign_on] Signing on to MWS")
    # TODO: Make this dynamic
    un,pw = ['91','91']
    app = Application(backend='uia').connect(path='Eclipse.exe')
    main = app['MainWindow']
    msg_box = app['EclipseMessageBox']
    if not main.exists():
        log.warning("MWS main window not found. Unable to sign on.")
        return False

    try:
        # TODO : When trying to sign_on() it sits on buttonSignOFF "forever". The wait condition is not being met.
        main.window(title_re = 'buttonSignOFF', control_type = 'Button').wait('ready', 2)
        log.debug('User is already signed on to the MWS')
        return True
    except pywinauto.timings.TimeoutError:
        pass
    main.window(title_re = 'buttonSignOn', control_type = 'Button').wait('ready', 600).click_input()
    if system.get_brand().upper() == "EXXON":
        start = time.time()
        while time.time() - start <= 2:
            try:
                msgbox = Application(backend='uia').connect(title_re='EclipseMessageBox')
            except pywinauto.findwindows.ElementNotFoundError:
                continue
            diag = msgbox['EclipseMessageBox']
            diag['OK'].click_input()
            break
        else:
            log.debug("No pop up before sign in")
                
    sign_on = app['SignOnWindow']
    sign_on['Operator IDEdit'].wait('ready', 10).set_text(un)
    sign_on['PasswordEdit'].set_text(pw)
    sign_on['buttonSign OnButton'].click_input()

    # Handle clock in prompt
    try:
        msg = msg_box.window(auto_id='textBlockMessage').wait('ready', 3).texts()[0]
    except pywinauto.timings.TimeoutError:
        log.debug("No prompt after clicking Sign On.")
        msg = None
    if msg and 'You are not currently clocked in. Do you wish to clock in?' in msg:
        log.debug("Got clock in prompt. Clicking OK.")
        msg_box.window(title='OK', control_type='Text').wait('ready', 5).click_input()

    # Verify success
    try:
        main.window(title_re = 'buttonSignOFF', control_type = 'Button').wait('ready', 45)
        return True
    except pywinauto.timings.TimeoutError:
        log.warning("Sign off button was not found after signing on.")
        return False

def sign_off():
    """
    Sign off from the MWS.
    Args:
        None
    Returns:
        bool: True/False for success/failure
    Examples:
        >>> mws.sign_off()
        True
    """
    return click_toolbar("SIGN OFF")

def search_click_ocr(search_text, bbox=None, color='000000', tolerance='000000',
                     psm=[12, 6, 3, 11], timeout=0, clicks=1, instance=1,
                     max_dist=0, term=False, click_loc=0, offset=(0,0), filter_strings=[]):
    """
    Use OCR to locate a string on-screen, and click at its
    location.
    Args:
        search_text: (str) The text to search for.
        bbox: (list/tuple) The bounding box (left, top, right, bottom)
                in which to search for the text.
        color: (str/list) The hex color(s) of text to search for.
        tolerance: (str) The hex value of how much color variance
                    to allow in the text.
        psm: (int) The page segmentation mode(s) to use. Each
              mode will be tried in order until success. tesseract --help-psm
              for more information.
        timeout: (int) Approx. number of seconds to spend searching for
                   the text. All PSMs will be attmpted before timing out.
        clicks: (int) How many times to click on the string.
        instance: (int) Which instance of the string to click on if multiple
                   matches are found. Order from top to bottom, left to right.
        max_dist: (int) The max Levenshtein distance to accept between the
                     search text and OCR result.
        term: (bool) Whether or not to fail and terminate the test
               script if OCR can't find the requested text.
        click_loc: (int) which part of the string to click on. 
                    0 for center, -1 for left end, 1 for right end
        offset: (tuple) how much to offset the click relative to the 
                 string's location.
        filter_strings: (str/list) Strings to remove from OCR output before
                         searching it.
    Returns:
        tuple: The coordinates of the location clicked. None if the string wasn't found.
    Examples:
        >>> search_click_ocr("Password")
        True
        >>> search_click_ocr("Some text that's not on screen")
        False
        >>> search_click_ocr("Some greyed-out text", color="808080")
        True
        >>> search_click_ocr("Some black text with non-uniform color", tolerance="404040")
        True
    """
    log.debug("Searching for the string {search_text} on the screen to click it.")
    return OCR.searchAndClick(search_text, color, bbox, tolerance, psm, timeout,
                              clicks=clicks, occurrence=instance, maxDist=max_dist,
                              click_location=click_loc, offset=offset, filter_strings=filter_strings)

def find_text_ocr(search_text, bbox=None, color='000000', tolerance='000000',
                  psm=[12, 6, 3, 11], timeout=0, max_dist=0, term=False, filter_strings=[]):
    """
    Use OCR to verify the presence of one or more strings on the
    screen.
    Args:
        search_text: (str/list) The text(s) to search for.
        bbox: (tuple) The bounding box (left, top, right, bottom)
              in which to search for the text.
        color: (str/list) The hex color(s) of text to search for.
        tolerance: (str) The hex value of how much color variance
                  to allow in the text.
        psm: (int/tuple) The page segmentation mode(s) to use. Each
              mode will be tried in order until success. tesseract --help-psm
              for more information.
        timeout: (int) Approx. number of seconds to spend searching for
                 the text. All PSMs will be attempted before timing out.                
        max_dist: (int) The max Levenshtein distance to accept between the
                      search text and OCR result.
        term: (bool) Whether or not to fail and terminate the test
               script if OCR can't find the requested text.
        filter_strings: (str/list) Strings to remove from OCR output before
                         searching it.
    Returns:
        bool: Whether or not the search text was found successfully.
    Examples:
        >>> find_text_ocr("Password")
        True
        >>> find_text_ocr("Some text that's not on screen")
        False
        >>> find_text_ocr("Some greyed-out text", color="808080")
        True
        >>> find_text_ocr("Some black text with non-uniform color", tolerance="404040")
        True
        >>> find_text_ocr(["Some", "non-consecutive", "texts"])
        True
    """
    log.debug("Searching for the string {search_text} on the screen.")
    return OCR.findText(search_text, color, bbox, tolerance, psm, timeout, maxDist=max_dist, filter_strings=filter_strings)
