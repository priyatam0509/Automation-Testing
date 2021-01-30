from app.util import runas
from app.util import server
from app.simulators import networksim as N
from app.simulators import pinpadsim
from app.framework.tc_helpers import test_func

import ctypes
from datetime import datetime, timedelta
import logging
import inspect
import json
import os
from PIL import ImageGrab
import psutil
from pywinauto.keyboard import send_keys
from pywinauto import Application
import shutil
import subprocess
import time
import win32com.client
import win32gui, win32process, win32con
from win32gui import FindWindow
from winreg import HKEY_LOCAL_MACHINE, KEY_ALL_ACCESS, OpenKey, QueryValueEx

# In house modules
from app.util import constants

log = logging.getLogger()

def takescreenshot(img_name = None):
    send_keys("{PRTSC}")
    #Set default values in case we fail to set specific ones later and can't read the run_info.
    #These values are the last ones to be used.
    ss_path = "D:\\temp"
    image_name = "failure_screenshot_"
    #Attempt to read the run_info file to set a better filename and location
    try:
        #Read the run_info file and set the image name and path
        with open("C:\\Automation\\run_info.json", 'r') as fp:
            run_info = json.load(fp)
        ss_path = run_info['logs_dir']
        image_name = run_info['current test name']
    except FileNotFoundError:
        log.debug("Could not find run_info.json in C:\\Automation.")
        log.debug("Throwing all screenshots moving forward to D:\\temp.")
    #Overwrite the fallbacks with any provided variable
    if img_name:
        image_name = img_name
    #Set the date_time variable for the screenshots filename
    date_time = datetime.now().strftime("%m%d-%H%M%S")
    #If the intended dir of the ss doesn't exist, make it
    if not os.path.isdir(ss_path):
        os.makedirs(ss_path)
    #Timeout loop waiting for the clipboard to load
    starttime = time.time()
    while time.time() - starttime <= 30:
        img = ImageGrab.grabclipboard()
        if img != None:
            log.debug("Found the failure screenshot, saving %s"%(image_name+date_time))
            img.save("%s\\%s.png"%(ss_path, image_name+date_time))
            return True
    log.error("Failed to generate a failure screenshot")

def collect_logs(difference=10):
    """
    Collect Logs

    Collects the Gilbarco Logs on a Passport Site.

    Args:
        timeout: (int) The length (in minutes) of time delta used to verify zip timestamp.
    Return:
        bool: True if the operation is a success. Otherwise, returns False and logs the output.
    """
    #Set up default values if we can't read the run_info.json file
    date_time = datetime.now().strftime("%m%d-%H%M")
    log_name = f"collectlogs_{date_time}.zip"
    log_path = "D:\\temp"

    try:
        #Read the run_info file for what to name the collected log file
        with open("C:\\Automation\\run_info.json", 'r') as fp:
            run_info = json.load(fp)
        log_path = run_info['logs_dir']
        log_name = f"{run_info['current test name']}_{date_time}.zip"
    except FileNotFoundError:
        log.debug("Could not find run_info.json in C:\\Automation. Placing logs generated in D:\temp")
    try:
        os.makedirs(log_path)
    except FileExistsError:
        log.debug(f"{log_path} already exists. Moving forward")

    # Used for comparing the timestamp in the zip filename
    time = datetime.now()
    delta = timedelta(seconds=difference)

    res = runas.run_as('collectlogs')
    if res['pid'] == -1:
        log.error("collectlogs failed. The response was: %s"%(res['output']))
        return False

    log_zip = []
    for files in os.listdir(constants.COLLECTLOGS_DIR):
        if '.zip' in files:
            # convert the timestamp in the filename to datetime format
            ft = datetime.strptime(files[0:23], '%m.%d.%y_%I.%M.%S.%f%p')
            log_zip.append(files)

    # check if zip file was created within 10 seconds
    # (default value of difference) of "collectlogs" execution
    if not (ft <= time+delta):
        log.error("Zip filename timestamp not valid.")
        return False

    # ensure only one .zip file in dir
    if len(log_zip) != 1:
        log.error("There is more than one log zip folder.")
        return False
    shutil.copy(f"{constants.COLLECTLOGS_DIR}\\{log_zip[0]}", f"{log_path}\\{log_name}")

    return True

def get_version():
    pp_subkey = constants.PASSPORT_SUBKEY
    reg_key = OpenKey(HKEY_LOCAL_MACHINE, pp_subkey, 0, KEY_ALL_ACCESS)

    pp_version = QueryValueEx(reg_key, 'Version')[0]
    version = pp_version.strip()
    return version

def get_brand():
    pp_subkey = constants.PASSPORT_SUBKEY
    reg_key = OpenKey(HKEY_LOCAL_MACHINE, pp_subkey, 0, KEY_ALL_ACCESS)

    brand = QueryValueEx(reg_key, 'BrandSelected')[0]
    return brand

def save_snapshot(snapshot_name = 'Configured_Site'):
    #TODO: need to enhance snapshot for edh & mws
    save_snapshot_mws(snapshot_name)
    
def save_snapshot_mws(snapshot_name):
    log.debug("Saving a snapshot on the mws")
    runas.run_as('C:\\Gilbarco\\SR\\bin\\sr /action=backup /type=snapshot')

    log.debug("Removing previous snapshot if it exists")
    if os.path.exists(constants.APPDATA + "\\" + snapshot_name):
        shutil.rmtree(constants.APPDATA + "\\" + snapshot_name)
    
    log.debug("Attempting to copy the saved snapshot")
    shutil.copytree(constants.SNAPSHOT_PATH,
                    constants.APPDATA + "\\" + snapshot_name)

    log.debug("Done saving the snapshot on the mws")

def save_snapshot_edh(snapshot_name):

    log.debug("Saving a snapshot on the edh")

    # Backup a snapshot through System Recovery on the edh. 
    runas.run_sqlcmd('C:\\Gilbarco\\SR\\bin\\sr /action=backup /type=snapshot')

    # Delete the existing snapshot sharing snapshot_name in app\data.
    # Check if the snapshot exists before attempting to remove the directory.
    check = runas.run_sqlcmd(f'if exist {constants.APPDATA_EDH}\\{snapshot_name} echo found ')
    if 'found' in check['output']:
        runas.run_sqlcmd(f'rmdir /S /Q {constants.APPDATA_EDH}\\{snapshot_name}')
    
    log.debug("Attempting to copy the saved snapshot")
    # Copy the saved snapshot from F:\Gilbarco\snapshot to app\data.
    runas.run_sqlcmd(f'Xcopy /E /I {constants.SNAPSHOT_PATH_EDH} {constants.APPDATA_EDH}\\{snapshot_name}')
    
    log.debug("Done saving the snapshot on the edh")
    return True

def restore_snapshot(snapshot_name = 'Configured_Site'):
    #TODO: need to enhance snapshot for edh & mws
    restore_snapshot_mws(snapshot_name)

def restore_snapshot_mws(snapshot_name):
    log.debug("Attempting to restore a snapshot on the mws")

    if os.path.exists(constants.SNAPSHOT_PATH):
        log.debug("Cleaning out the existing snapshot")
        shutil.rmtree(constants.SNAPSHOT_PATH)
    
    log.debug("Copying the desired snapshot off the D drive")
    if os.path.exists(constants.APPDATA + "\\" + snapshot_name):
        shutil.copytree(constants.APPDATA + "\\" + snapshot_name,
                        constants.SNAPSHOT_PATH)
    else:
        log.error("Snapshot does not exist")
        return False
    
    # check if the snapshot is the correct passport version. 
    try:
        with open(constants.SNAPSHOT_PATH + "\\" + "version.txt") as file:
            data = file.read().strip()
            vsion = get_version().strip()
    except FileNotFoundError as e:
        log.error("Version.txt not found; couldn't verify snapshot")
        return False
    
    if data != vsion:
        log.error("Snapshot version does not correspond to installed Passport version.")
        return False
        
    runas.run_as(r'C:\Gilbarco\SR\bin\sr /action=restore '+
            r'/dir=C:\Gilbarco\snapshot /type=snapshot')
    log.debug("Done restoring the snapshot, restarting passport")

    restartpp()

    app = Application(backend='uia').connect(path='Eclipse.exe')
    main = app['MainWindow']
    main.window(title_re = 'buttonSignOn', control_type = 'Button').wait('ready', 60)
    
    # manually restart passport replication service
    os.system('net start PassportREPLAdmin')

    return True

def restore_snapshot_edh(snapshot_name):
    log.debug("Attempting to restore a snapshot on the edh")

    log.debug("Copying the desired snapshot off the D drive")

    # Copy the snapshot saved on D:\ to F:\Gilbarco.
    # First, check if this snapshot exists.
    check = runas.run_sqlcmd(f'if exist {constants.APPDATA_EDH}\\{snapshot_name} echo found ')
    if 'found' in check['output']:
        
        runas.run_sqlcmd(f'Xcopy /E /I {constants.APPDATA_EDH}\\{snapshot_name} {constants.SNAPSHOT_PATH_EDH}')
        
        # Clear the existing snapshot on F:\Gilbarco.
        log.debug("Cleaning out the existing snapshot")
        runas.run_sqlcmd(f'rmdir /S /Q {constants.SNAPSHOT_PATH_EDH}')
        
        log.debug('Restoring the snapshot')

        # Run the following command through sqlcmd.exe so as to restore the backup.
        runas.run_sqlcmd(r'C:\Gilbarco\SR\bin\sr /action=restore /dir=F:\Gilbarco\snapshot /type=snapshot')
        log.debug("Done restoring the snapshot, restarting the edh")

        # Restart the EDH. 
        runas.run_sqlcmd('net stop edh')
        runas.run_sqlcmd('net start edh')

        log.debug("Done restarting the edh")

        restartpp()
        return True
    else:
        log.error("Snapshot does not exist")
        return False

def print_full_stack():
    exceptLog = logging.getLogger("exceptionLog")
    exceptLog.critical("Traceback (most recent call last):")
    for item in reversed(inspect.stack()[2:]):
        exceptLog.critical(' File "{1}", line {2}, in {3}'.format(*item))
    for line in item[4]:
        exceptLog.critical('  ' + line.strip())
    for item in inspect.trace():
        exceptLog.critical(' File "{1}", line {2}, in {3}'.format(*item))
    for line in item[4]:
        exceptLog.critical('  ' + line.strip())

def _toggle_win_state(state, win_list = None):
    """
    Toggle Window State

    A function that will toggle the state of the windows provided. If no 
    windows are provided it will use the default list in the method.

    Args:
        state (str):    The state you wish to change the windows to. Currently supports: minimize, maximize, restore.
        win_list(list): The list of titles for the windows you wish to change the state of.
    """
    log = logging.getLogger()
    def pid_to_hwnd(pid):
        def cb(hwnd, hwnds):
            if win32gui.IsWindowVisible(hwnd) and \
               win32gui.IsWindowEnabled(hwnd):
               _, found = win32process.GetWindowThreadProcessId(hwnd)
               if found == pid:
                   hwnds.append(hwnd)
            return True
        hwnds = []
        win32gui.EnumWindows(cb, hwnds)
        return hwnds

    if 'minimize' in state:
        state = win32con.SW_MINIMIZE
    elif 'restore' in state:
        state = win32con.SW_RESTORE
    elif 'maximize' in state:
        state = win32con.SW_MAXIMIZE
    else:
        log.error(f"Unknown state provided: {state}.")
        log.error("Accepted states: 'minimize', 'maximize', 'restore'")
        return False

    ShowWindow = ctypes.windll.user32.ShowWindow
    GetWindowText = ctypes.windll.user32.GetWindowTextW
    GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW

    if win_list == None:
        win_list = ['Python',
                    'py',
                    'AutoIt',
                    'SciTE',
                    'Windows Command Processor',
                    'Notepad',
                    'Windows Task Manager',
                    'Administrator: cmd']
    
    running_processes = psutil.process_iter()
    for p in running_processes:
        for hwnd in pid_to_hwnd(p.pid):
            length = GetWindowTextLength(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            GetWindowText(hwnd, buff, length + 1)
            title = str(buff.value).strip()
            for verif in win_list:
                if title.find(verif) > -1:
                    try:
                        log.info(f"| Change the state of {title}")
                        ShowWindow(hwnd, state)
                    except Exception as e:
                        log.error(e)
                        print_full_stack()
                        pass

def restartpp(wpf = True):
    '''
    @Description: Function is used to restart passport
    @Return:
        >(boolen) True/False

    '''
    log = logging.getLogger()
    log.debug('*** RESTARTING PASSPORT ***')
    count = 0
    execute = subprocess.Popen("C:\\Passport\\tools\\RestartPassport.bat",
                shell=True, cwd='C:\\Windows\\System32')
    execute.wait()
    while not FindWindow(None, 'MainWindow') and wpf and count < 180:
        time.sleep(1)
        count += 1

    if count == 180:
        return False
    return True


def process_wait(proc_name, timeout):
    """
    Waits within a given amount of time for a process to exist.
    Args:
        proc_name: (str) The name of the process that the user is searching
                         for. It can be a partial name such was storec 
                         instead of storeclose.exe or STOREC~1.exe.
        timeout: (int) The length (in seconds) of time for the function to 
                        search for the process name.
    Returns:
        bool: True if the process is found, False if not
    Examples:
        >>> process_wait("storopt.exe", 10)
        True
        >>> process_wait("notaprocess.gif", 5)
        False
    """
    log = logging.getLogger()
    starttime = time.time()
    while time.time() - starttime <= timeout:
        wmi = win32com.client.GetObject('winmgmts:')
        for p in wmi.InstancesOf('win32_process'):
            if proc_name.lower() in p.Name.lower():
                log.debug("Found %s" % p.Name)
                return True
    log.warning("Could not find %s within %s seconds."
                                % (proc_name, str(timeout)))
    return False

@test_func
def wait_for(func, desired_result=True, timeout=10, args=[], kwargs={}, interval=None):
    """
    Repeatedly evaluate a function until it returns the desired
    result.
    Args:
        func: (function) The function to evaluate. This must be a function object, NOT a function call
        desired_result: The desired return value of the function
        timeout: (int) Seconds to wait for the function to evaluate to the desired result
        args: (list) Positional arguments to provide to the function
        kwargs: (dict) Keyword arguments to provide to the function
        interval: (int) Seconds to wait between evaluations
        verify: (bool) Whether or not to fail the current test case if this function return False. Defaults to True
    Returns: 
        bool: Whether or not the function evaluated to the desired
              result within the timeout
    Examples:
        >>> wait_for(pos.status_line_read, "Press the speed keys to enter items.")
        True
        >>> wait_for(lambda: "Press the speed keys" in pos.status_line_read)
        True
        >>> wait_for(pos.click, args=["Card"], kwargs={"timeout": 0})
        True
    """
    logger = logging.getLogger()
    if "verify" in func.__code__.co_varnames:
        kwargs.update({"verify": False}) # Prevent test_func decorated function from ending the test case if it fails
    start_time = time.time()
    log_level = logger.getEffectiveLevel()
    if log_level > logging.DEBUG:
        logger.setLevel(999) # Suppress logging from the repeated calls, unless debug level is set

    while func(*args, **kwargs) != desired_result:
        if time.time() - start_time > timeout:
            logger.setLevel(log_level) # Reset log level
            logger.warning(f"{func.__name__} did not return {desired_result} within {timeout} seconds.")
            return False
        if interval is not None:
            time.sleep(interval)

    logger.setLevel(log_level)
    return True

@test_func
def restart_eps():
    """
    Restarts EPS
    Args:
        None
    Return:
        bool: True if the operation is a success. Otherwise, returns False and logs
                the output
    Example:
    """

    res = runas.run_as(r'c:\Gilbarco\tools\epsdashboard.exe RESTART_EPS /HIDE_GUI')
    if res['pid'] == -1:
        log.error("Restart failed. The response was: %s"%(res['output']))
        return False
    return True

def new_test(test_name):
    """
    New Test Creation

    This method will take the test_name variable passed into it and create a new .py script by that name.
    This uses the new_test_template.tmpl located in the templates directory.

    Args:
        test_name (str):    The name you want to give the .py file.
    """
    file_name = test_name.replace(' ', '_')
    log = logging.getLogger()
    full_path = f'scripts/features/{file_name}.py'
    if os.path.exists(full_path):
        log.info("File already exists. Choose another name or modify the existing file.")
        return

    date_created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log.info(f"Creating a new test case named {file_name}")
    class_name = file_name.replace('.py', '')
    new_test_template = None
    with open("templates/new_test_template.tmpl", 'r') as ntt:
        new_test_template = ntt.read()
    new_test_template = new_test_template.replace("$CLASSNAME", class_name)
    new_test_template = new_test_template.replace("$DATECREATED", date_created)
    new_test_template = new_test_template.replace("$FILENAME", file_name)
    with open(full_path, 'w') as ntc:
        ntc.write(new_test_template)
    log.info(f"Test case {file_name} created successfully. ")