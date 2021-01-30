"""
    File name: SWUpgrade_Activation_Tool_UI_ForHotFix.py
    Tags:
    Description: SL-1878: OS Hot fixes should not be blocked for upgrade
    Brand: Concord
    Author: Paresh
    Date created: 2020-01-06 19:11:00
    Date last modified:
    Python Version: 3.7
"""

import logging, time
import os, shutil
from app import runas
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from Scripts.features import SWUpgrade_ActivationTool_Verify_UI, SWUpgrade_ActivationTool_UI_OnStore_Close

root_dir = "D:/gilbarco/"
folder_name = "SWUpgrade"
hot_fix_dir = "//10.4.22.84/Passport_Media/OS HF Updates/2018 OS Hotfixes/HF2018.01.MWS.zip"
package_dir = "//10.4.22.84/EngData/SQA/AutomationTestData/20.01.XX.01A.zip"
log = logging.getLogger()

def perform_asu_operation():
    """
    Description: Help function to perform net stop asu, net start asu and copy packages
    Args: None
    Returns: None 
    """

    # Run cmd command to stop asu
    if not runas.run_as(cmd=r"net stop asu"):
        log.error("Unable to stop asu services")
        
    # Delete the download folder from swUpgardeManager folder
    time.sleep(2)
    path = os.path.join(root_dir, folder_name)
    if os.path.exists(root_dir):
        shutil.rmtree(path)
    else:
        log.error("Directory is not present "+root_dir)
        return False
        
    # Run cmd command to start asu
    if not runas.run_as(cmd=r"net start asu"):
        log.error("Unable to start asu services")
    
    return True

class SWUpgrade_Activation_Tool_UI_ForHotFix():
    """
    Description: Test class that provides an interface for testing.
    """
    def __init__(self):
        """Initializes the Template class.
        Args: None
        Returns: None
        """
        pass
        
    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        # Perform ASU operation
        if not perform_asu_operation():
            log.error("Unable to perform asu operation.")  

    @test
    def verify_ui_not_visible_for_hot_fix_package(self):
        """
        Testlink Id: SL-1878: OS Hot fixes should not be blocked for upgrade
		Description: Verify Activation tool UI is not visible, if expiry date is null in DB and only hot fix is in list for software upgrade manager
        Args: None
        Returns: None
        """

        # Copy package from hot fix dir to download folder
        if not SWUpgrade_ActivationTool_Verify_UI.copy_package(hot_fix_dir):
            tc_fail("Unable to copy package in dowload folder")
        
        # Wait for 90 second to updated pending.xml
        time.sleep(90)
        
        # Clear the alert
        if not SWUpgrade_ActivationTool_Verify_UI.serveralert_check():
            tc_fail("Failed to click on alert")
        
        # Verify UI is visble if we have only software package in list
        if not SWUpgrade_ActivationTool_Verify_UI.verify_softwareUpgradeActivation_tool_UI(isVisible=False):
            tc_fail("Unable to see Sofware Activation Tool UI")
            
        return True
    
    @test
    def verify_ui_for_sofwarepackage_and_hot_fix(self):
        """
        Testlink Id: SL-1878: OS Hot fixes should not be blocked for upgrade
		Description: Verify Activation tool UI is visible, if expiry date is null in DB and software and hot fix package are in list
        Args: None
        Returns: None
        """

        # Perform ASU operation
        if not perform_asu_operation():
            tc_fail("Unable to perform asu operation")
        
        # Copy package from local dir to download folder
        if not SWUpgrade_ActivationTool_Verify_UI.copy_package(package_dir):
            tc_fail("Unable to copy package in dowload folder")
        
        # Wait for 45 second to updated pending.xml
        time.sleep(45)
        
        # Clear the alert
        if not SWUpgrade_ActivationTool_Verify_UI.serveralert_check():
            tc_fail("Failed to click on alert")
                
        # Copy package from hot fix dir to download folder
        if not SWUpgrade_ActivationTool_Verify_UI.copy_package(hot_fix_dir):
            tc_fail("Unable to copy package in dowload folder")
        
        # Wait for 90 second to updated pending.xml
        time.sleep(90)
        
        # Clear the alert
        if not SWUpgrade_ActivationTool_Verify_UI.serveralert_check():
            tc_fail("Failed to click on alert")

        # Verify UI is visble if we have software package and hot fix package in list
        if not SWUpgrade_ActivationTool_Verify_UI.verify_softwareUpgradeActivation_tool_UI():
            tc_fail("Unable to see Sofware Activation Tool UI")
            
        return True
    
    @test
    def verify_ui_for_sofwarepackage_and_hot_fix_on_store_close(self):
        """
        Testlink Id: SL-1878: OS Hot fixes should not be blocked for upgrade
		Description: Verify Activation tool UI is visible via store close from mws and from pos, if expiry date is null in DB and software and hot fix package are in list
        Args: None
        Returns: None
        """
        
        # Verify UI is visble on store close from mws if we have software package and hot fix package in list
        if not SWUpgrade_ActivationTool_UI_OnStore_Close.verify_softwareUpgradeActivation_tool_UI():
            tc_fail("Unable to see Sofware Activation Tool UI")

        # Verify UI is visble on store close from pos if we have software package and hot fix package in list
        if not SWUpgrade_ActivationTool_UI_OnStore_Close.verify_softwareUpgradeActivation_tool_UI(buttonName="POS"):
            tc_fail("Unable to see Sofware Activation Tool UI")
            
        return True
    
    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        
        # Perform ASU operation
        if not perform_asu_operation():
            log.error("Unable to perform asu operation")
        