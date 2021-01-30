"""
    File name: SWUpgrade_ActivationTool_Verify_UI.py
    Tags:
    Description: SL-1653/SL-1767: Verify UI of software upgrade activation tool
    Brand: Concord
    Author: Paresh
    Date created: 2020-02-04 19:11:00
    Date last modified:
    Python Version: 3.7
"""

import logging, time
import pyodbc
import winreg as reg
import os, shutil
from pywinauto import Application
from datetime import datetime, timedelta
from app import Navi, mws
from app.framework.tc_helpers import setup, test, teardown, tc_fail

download_dir = "D:/gilbarco/SWUpgrade/Download/"
package_dir = "//10.4.22.84/EngData/SQA/AutomationTestData/20.01.XX.01A.zip"
log = logging.getLogger()

def serveralert_check():
    """
    Description: Check for, log, and dismiss any unexpected server alerts.
    Args: None
    Returns: None
    """
    start_time = time.time()
    while time.time()-start_time <= 180:
        try:
            app = Application().connect(title_re="SERVER ALERT")
        except Exception as ElementNotFoundError:
            return ElementNotFoundError
        win = app["SERVER ALERT"]
        msg = "%s\n%s" % (win['Static2'].texts()[0], win['Static3'].texts()[0].replace('\n', ' '))
        log.error(f"!!! Got a server alert: {msg}")
        win["Clear Alert"].click()
    else:
        log.error("Failed to conenct with server alret")
        return False

def copy_package(dir_name):
    """
    Description: Help function to copy package from local drive to dowload folder
    Args: 
        dir_name: name of local directory, from where we are copying the file
    Returns: None
    """

    # Create a directory if not exists
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
        log.info("Download directory created")
    else:
        log.info("Download directory already exists")

    if not shutil.copy(dir_name, download_dir):
        log.error("Failed to copy package from shared location to download folder")

    return True

def connect_mws_db(data_value='', id='19004', conServer="POSSERVER01", dbName="GlobalSTORE"):
    """
    Description: Help function to connect with database
    Args:
        data_value: Value of date or GVR ID in query
        id: Primary key id of query
		conServer: Connection server name
        dbName: database Name
    Returns: True if query successfully executed, False if fail
    """

    connstr = 'Driver={SQL Server};Server=' + conServer + ';Database='+ dbName +';Trusted_Connection=yes;'
    try:
        # connection through the connection string
        conn = pyodbc.connect(connstr)
        cursor = conn.cursor()

        queryString = "Update OPTIONS_STR Set OPT_VALUE='"+data_value+"' WHERE OPT_ID='"+id+"'"
        
        # executes the query
        cursor.execute(queryString)
        conn.commit()
        conn.close()

    except pyodbc.Error as ex:
        sqlstate = ex.args[1]
        log.error(sqlstate)
    
    return True


def verify_softwareUpgradeActivation_tool_UI(isVisible=True, toogle=1):
    """
    Description: Help function to validate UI is visible or not
    Args:
		isVisible: Pass the parameter if UI need to visible
		toogle: Set toogle value in registery editor either 0 or 1
    Returns: None 
    """

    if not Navi.navigate_to("Software Upgrade Manager"):
        log.error("Failed to navigate Software Upgrade Manager")
    
    if not mws.wait_for_button("Install Software"):
        log.error("Install Software button is not visible")

    if not mws.click_toolbar("Install Software"):
        log.error("Install software button is not visible")
    
    if isVisible is True and toogle is 1:
        if not mws.click("GVR ID"):
            log.error("GVR ID text box is not visible")
        
        for i in range(1, 5):
            if not mws.click("Approval Code"+str(i)):
                log.error("Approval code text box is not visible")
        
    else:
        exp_msg = "While installing updates all dispensers and registers will be out of service."
        start_time = time.time()
        while time.time() - start_time < 30:
            get_message = mws.get_top_bar_text()
            if exp_msg in get_message:
                break
        if exp_msg not in get_message:
            log.error("Message is not displayed")
        if not mws.click_toolbar("No"):
            log.error("Unable to click on No button")
    
    if not mws.click_toolbar("Exit"):
        log.error("Exit button is not visible")
    
    # Wait for 2 second to complete the process
    time.sleep(2)
    
    return True


class SWUpgrade_ActivationTool_Verify_UI():
    """
    Description: Test class that provides an interface for testing.
    """
    def __init__(self):
        """Initializes the Template class.
        Args: None
        Returns: None
        """
        # The logging object. 
        # Example: self.log.info(f"Current value of var: {my_var}")
        
    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        Args: None
        Returns: None
        """
    
        copy_package(package_dir)
        
        # Wait for 45 second to updated pending.xml
        time.sleep(45)

        # Clear the alert
        serveralert_check()
 
    @test
    def verify_ui_for_null_date(self):
        """
        Testlink Id: SL-1653/SL-1767: Verify UI of software upgrade activation tool
		Description: Verify Activation tool UI is visible if expiry date is null in DB
        Args: None
        Returns: None
        """
        # Update null date value in DB
        if not connect_mws_db():
            tc_fail("Unable to update date value in DB")
        
        # Verify UI is visble after updating the null value in DB
        if not verify_softwareUpgradeActivation_tool_UI():
            tc_fail("Unable to see Sofware Activation Tool UI")
            
        return True
    
    @test
    def verify_ui_for_past_date(self):
        """
        Testlink Id: SL-1653/SL-1767: Verify UI of software upgrade activation tool
		Description: Verify Activation tool UI is visible if expiry date is past in DB
        Args: None
        Returns: None
        """

        past_date = datetime.strftime(datetime.now() - timedelta(1), '%m-%d-%Y')

        # Update past date value in DB
        if not connect_mws_db(data_value=past_date):
            tc_fail("Unable to update date value in DB")
        
        # Verify UI is visble after updating the past date value in DB
        if not verify_softwareUpgradeActivation_tool_UI():
            tc_fail("Unable to see Sofware Activation Tool UI")
            
        return True
    
    @test
    def verify_ui_for_invalid_date(self):
        """
        Testlink Id: SL-1653/SL-1767: Verify UI of software upgrade activation tool
		Description: Verify Activation tool UI is visible if expiry date is today+365 in DB
        Args: None
        Returns: None
        """

        invalid_date = datetime.strftime(datetime.now() - timedelta(-370), '%m-%d-%Y')

        # Update today+365 date value in DB
        if not connect_mws_db(data_value=invalid_date):
            tc_fail("Unable to update date value in DB")
        
        # Verify UI is visble after updating the past date value in DB
        if not verify_softwareUpgradeActivation_tool_UI():
            tc_fail("Unable to see Sofware Activation Tool UI")
            
        return True
    
    @test
    def verify_ui_for_current_date(self):
        """
        Testlink Id: SL-1653/SL-1767: Verify UI of software upgrade activation tool
		Description: Verify Activation tool UI is not visible if expiry date is current in DB
        Args: None
        Returns: None
        """

        today_date = datetime.strftime(datetime.now(), '%m-%d-%Y')

        # Update today's date value in DB
        if not connect_mws_db(data_value=today_date):
            tc_fail("Unable to update date value in DB")
            
        # Verify UI is visble after updating the today's date value in DB
        if not verify_softwareUpgradeActivation_tool_UI(False):
            tc_fail("Sofware Activation Tool UI is displayed")
            
        return True
    
    @test
    def verify_ui_for_future_date(self):
        """
        Testlink Id: SL-1653/SL-1767: Verify UI of software upgrade activation tool
        Description: Verify Activation tool UI is not visible if expiry date is future in DB
        Args: None
        Returns: None
        """

        future_date = datetime.strftime(datetime.now() - timedelta(-1), '%m-%d-%Y')

        # Update future date value in DB
        if not connect_mws_db(data_value=future_date):
            tc_fail("Unable to update date value in DB")

        # Verify UI is visble after updating the future date value in DB
        if not verify_softwareUpgradeActivation_tool_UI(False):
            tc_fail("Sofware Activation Tool UI is displayed")
            
        return True
    
    @test
    def ui_is_not_visible_if_toogle_value_zero(self):
        """
        Testlink Id: SL-1653/SL-1767: Verify UI of software upgrade activation tool
		Description: Verify Activation tool UI is not visible if toogle value is 0 in registry editor
        Args: None
        Returns: None
        """
        # Update null date value in DB
        if not connect_mws_db():
            tc_fail("Unable to update date value in DB")
        
        # Set toogle value as 0 in registry editor
        key = r'SOFTWARE\WOW6432Node\Gilbarco\Passport\MWS'
        open_regedit_path = reg.OpenKey(reg.HKEY_LOCAL_MACHINE, key, 0, reg.KEY_ALL_ACCESS)
        reg.SetValueEx(open_regedit_path,"ToggleUpgradeBlockerFeature",0,reg.REG_SZ,"0")

        # Verify UI is not visble after updating the 0 value in registry editor
        if not verify_softwareUpgradeActivation_tool_UI(toogle=0):
            tc_fail("Sofware Activation Tool UI is visible")
    
        return True

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        # Set toogle value as 1 in registry editor
        key = r'SOFTWARE\WOW6432Node\Gilbarco\Passport\MWS'
        open_regedit_path = reg.OpenKey(reg.HKEY_LOCAL_MACHINE, key, 0, reg.KEY_ALL_ACCESS)
        reg.SetValueEx(open_regedit_path,"ToggleUpgradeBlockerFeature",0,reg.REG_SZ,"1")