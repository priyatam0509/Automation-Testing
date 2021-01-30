__author__ = "Cassidy Garner"
#required modules
import time, logging, json
from pywinauto import Application

# In-House Modules
from app import mws, OCR, pos, system, Site_Type

JSON_DATA_PATH = "D:/Automation/app/data/controls.json"

log = logging.getLogger()

def navigate_to(end):
    """
    The main navigator of Passport.

    Args:
        end: (str) The location to navigate to.

    Returns:
        True: (bool) If Navi was able to successfully navigate to its end location.

    Raises:
        NaviException: If Navi could not navigate to its end location.

    Examples:
        >>> navigate_to("Store Options")
        True
        >>> navigate_to("Not Store Options")
        NaviException: Failed to navigate to Not Store Options.
    """
    if end.lower() == "pos":
        return get_to_pos()
    elif end.lower() == "mws":
        return get_to_mws()
    else:
        get_to_mws()

    # Load the current process. 
    # NOTE: Duplicates logic from mws.load_controls - clean this up at some point
    try:
        data = json.load(open(JSON_DATA_PATH))
        data = data[str(end).lower()]
    except FileNotFoundError:
        raise NaviException(f"Couldn't load controls file.")
    except KeyError:
        raise NaviException(f"Couldn't find {end} in controls file.")
    try:
        network = data['network']
    except KeyError:
        network = False
    if network:
        log.debug("Loading controls for network menu")
        brand = system.get_brand()
        for key in data.keys():
            if brand.upper() in key.upper():
                try:
                    data = data[key]
                except KeyError:
                    raise NaviException(f"Failed to find the brand network controls for {brand}")
    try:   
        process = str(data['process'])
    except KeyError:
        raise NaviException(f"Couldn't load process name for {end}")

    log.debug("Checking if already on the menu")
    if system.process_wait(process, 1):
        log.debug('Already in %s menu' %end)
        mws.load_controls(end)
        return mws.create_connection()

    log. debug("Connecting to Eclipse")
    app = Application(backend='uia').connect(path='Eclipse.exe')
    main = app['MainWindow']
    if main.exists():
        try:
            main.window(title_re = 'buttonSignOn', control_type = 'Button').wait('ready', 2)
            mws.sign_on()

            #If navigating to Feature Activate
            log.debug("Checking if on the menu")
            if system.process_wait(process, 1):
                log.debug('Already in %s menu' %end)
                mws.load_controls(end)
                return mws.create_connection()
        except:
            log.debug('A user is logged on to the MWS')

        log.debug("Attempting to select the MWS Search")
        try:
            use_search_bar(end)
            mws.load_controls(end)
            return mws.create_connection()
        except:
            log.debug("Attempting to recover the mws")
            try: 
                mws.recover()
            except mws.ConnException:
                system.restartpp(True)
                mws.sign_on()
            try:
                log.debug("Retrying search bar after restart")
                use_search_bar(end)
                mws.load_controls(end)
                return mws.create_connection()
            except Exception:
                raise NaviException("Navigation failed. Couldn't navigate to %s"%(end))
    else:
        log.error("Failed to connect to MainWindow")
    raise NaviException("Navigation failed. Couldn't navigate to %s"%(end))

def get_to_mws(sign_in=True):
    '''
    Navigates to the MWS.

    Args:
        sign_in: (bool) If the user is not signed onto the MWS, navi attempts to sign on if set to True.

    Returns:
        True: (bool) if successfully navigated to the MWS.

    Raises:
        NaviException: if there was an error of any kind.

    Examples:
        >>> get_to_mws()
        True
        >>> get_to_mws(False)
        True
        >>> get_to_mws()
        NaviException: Instance of pos could not be created. Must not be in a WPF theme.
    '''
    try:
        app = Application(backend='uia').connect(path='Eclipse.exe')
        main = app['MainWindow']
        if main.exists():
            log.debug('Currently in the mws.')
            return True
        pos.connect()
    except:
        raise NaviException("Instance of pos could not be created. Must not be in a WPF theme.")

    #@TODO: Make this more dynamic?
    pos.click_function_key('TOOLS', verify=False)
    if not pos.click_tools_key(key ='MGR WKSTN', timeout=5, verify=False):
        pos.click_keypad('9', verify=False)
        pos.click_keypad('1', verify=False)
        pos.click_keypad('ENTER', verify=False)
        pos.click_pwd_key('9', verify=False)
        pos.click_pwd_key('1', verify=False)
        pos.click_pwd_key('OK', verify=False)
        pos.click_tools_key('MGR WKSTN', verify=False)
    if sign_in:
        return mws.sign_on()
    else:
        return True

def get_to_pos(timeout=1, sign_on=False):
    '''
    Navigates to the POS.

    Args:
        sign_in: (bool) If the user is not signed onto the POS, navi attempts to sign on if set to True.

    Returns:
        True: (bool) if successfully navigated to the POS.

    Raises:
        NaviException: if there was an error of any kind.

    Examples:
        >>> get_to_pos()
        True
        >>> get_to_pos(False)
        True
        >>> get_to_pos()
        NaviException: Unable to navigate to the POS
     '''
    if Site_Type == "HTMLPos":
        return pos.connect() # No navigation needed, just open a browser

    '''Checks to see if you are already in the pos.
        if you are already in the pos it will return
        a pos instance. Otherwise it will log that it
        is trying to get to the pos.
    '''
    try:
        window = Application(backend='uia').connect(path='RunIt.exe')
        if window["Status Line"].is_visible():
            log.debug("Passport is already on the POS screen.")
            pos.connect()
            if sign_on:
                pos.sign_on()
            return True
    except:
        log.debug("Attempting to navigate to the POS")

    '''
    Creates a connection to MainWindow application
    If unable to connect to MainWindow passport is
    not running so we restart passport.
    '''

    try:
        app = Application(backend = 'uia').connect(path = 'Eclipse.exe')
        main_window = app['MainWindow']
    except:
        log.debug('Passport is not running. Attempting to restart passport')
        if not system.restartpp(True):
            log.warning('Restart passport failed')
            raise NaviException('Restart passport failed during get_to_pos')
        mws.click_toolbar('POS')
        pos.connect()
        if sign_on:
            pos.sign_on()
        return True


    '''Checks to see if you are on the mws main screen.
        if you are on the main screen it will click POS.
        It will see if you are just not signed on, sign on
        and then click the POS button, then return pos instance.
    '''
    try:
        main_window.window(auto_id='textBox').is_visible()
        mws.click_toolbar('POS')
        pos.connect()
        if sign_on:
            pos.sign_on()
        return True
    except:
        log.debug('Passport is not on the MWS main screen')

    '''Checks to see if the sign on buttton is present.
        If the button is present we will sign on, then
        click the POS button, then return to pos instance
    '''
    try:
        main_window.window(title = 'buttonSignOn', control_type = 'Button').wait('ready', timeout)
        mws.sign_on()
        mws.click_toolbar('POS')
        pos.connect()
        if sign_on:
            pos.sign_on()
        return True
    except:
        log.debug('The MWS is not signed off')

    '''Navigates out of the current MWS menu, clicks the POS button,
        and returns pos instance.
    '''
    if mws.recover():
        try:
            mws.click_toolbar('POS')
            pos.connect()
            if sign_on:
                pos.sign_on()
            return True
        except:
            raise NaviException('Unable to navigate to the POS')
    else:
        return False

def use_search_bar(text):
    '''
    A function to use the search bar on the MWS.

    Args:
        text: (string) The title of the menu that you are navigating to.

    Returns:
        True: (bool) True if the Search bar in the MWS was found and the text was successfully entered.

    Raises:
        NaviException: (Exception) In case navigation failed using the search bar.

    Examples:
        >>> use_search_bar("Store Options")
        True
        >>> use_search_bar("Store Options") #While on the POS instead of the MWS
        NaviException: Navigation failed. Couldn't navigate to Store Options
    '''
    try:
        main = Application(backend = 'uia').connect(title_re = 'MainWindow')
        box = main['MainWindow']
        box.window(auto_id='textBox').set_focus()
        box.window(auto_id='textBox').set_text(text)
        box.window(auto_id='textBox').type_keys("{ENTER}")
        log.debug('Sent %s to the search bar.' %text)
        return True
    except:
        raise NaviException("Navigation failed. Couldn't navigate to %s"%(text))

class NaviException(Exception):
    pass