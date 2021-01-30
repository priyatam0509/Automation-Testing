"""
    File name: SWUpgrade_Validate_Default_GVR_ID.py
    Tags:
    Description: SL-1810: Default GVR ID
    Brand: Concord
    Author: Paresh
    Date created: 2020-29-04 19:11:00
    Date last modified: 
    Python Version: 3.7
"""

import logging, pywinauto, time
import winreg as reg
from app import Navi, mws
from datetime import datetime, timedelta
from app.util import constants
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from Scripts.features import SWUpgrade_ActivationTool_Verify_UI

activation_tool_path = constants.TESTING_TOOLS + r'\HDActivation.exe'

Controls = {
            "Software Upgrade Approval Code": "Software Upgrade Approval Code",
            "Generate Approval Code": "Generate Approval Code",
            "Clear": "Clear",
            "Gilbarco ID": "Edit5",
            "Approval Code 1": "Edit3",
            "Approval Code 2": "Edit4",
            "Approval Code 3": "Edit2",
            "Approval Code 4": "Edit1"
        }
log = logging.getLogger()

def generate_approval_code_from_hdactivation(gvrid):
    """
    Description: Help function to generate approval code
    Args:
        gvr id: Pass the value of GVR ID
    Returns: Return list of generated code
    """
    # Open HD activation tool
    hdpassportactivation = pywinauto.application.Application().start(activation_tool_path)
    app = hdpassportactivation['Passport Activation Utility']
    app.wait('ready', 5)

    # Verify Software Upgrade Aprroval Code radio button is visible
    app[Controls["Software Upgrade Approval Code"]].click()
    time.sleep(.5)
        
    # Enter gilbarco id
    app[Controls["Gilbarco ID"]].type_keys(gvrid)
    time.sleep(.5)

    # Generate approval code
    app[Controls["Generate Approval Code"]].click()
    
    # Validate the message for default GVR id
    app = hdpassportactivation['Help Desk Activation']
    app.wait('ready', 5)

    if not app["You have entered default GVR ID, are you sure you want to continue?"].is_visible():
        tc_fail("Validation message is not displayed")

    app["YES"].click()
    time.sleep(.5)
    
    if not app["Default GVR ID cannot be used to generate approvale code at the same site again. Do you want to continue?"].is_visible():
        tc_fail("Validation message is not displayed")

    app["YES"].click()
    time.sleep(.5)
    
    if not app["Software upgrades for only five days will be allowed with this ID. Do you want to continue?"].is_visible():
        tc_fail("Validation message is not displayed")

    app["YES"].click()
    time.sleep(.5)
    
    
    # Store generated approval code in list
    app = hdpassportactivation['Passport Activation Utility']
    app.wait('ready', 5)

    approval_code = [app[Controls[f"Approval Code {i}"]].texts()[0] for i in range(1,5)]
    hdpassportactivation.kill()      

    return approval_code

def verify_default_gvr_id(allowdefaultGVRID, generated_code):
    """
    Description: Help function to verfiy default GVR ID is used
    Args:
        allowdefaultGVRID: set the value if we can use default GVR id multiple times
        generated_code: Enter generated approval code
    Returns: True if method executed successfully
    """

    # Verify we are able to set the GVR id and approval code in activation tool UI
    Navi.navigate_to("Software Upgrade Manager")

    if not mws.click_toolbar("Install Software"):
        log.error("Install software button is not visible")
    
    if not mws.set_value("GVR ID", "239686"):
        log.error("Gilbarco ID text box is not visible")
        
    # Enter Site Code in MWS
    for i in range(4):
        if not mws.set_text(f"Approval Code{i+1}", generated_code[i]):
            log.error("Unable to set approval code in MWS")
            
    if not mws.click("Install"):
        log.error("Unable to click on install button")
    
    if allowdefaultGVRID is True:
        # Get installation message
        get_message = mws.get_top_bar_text()
        
        if "While installing updates all dispensers and registers will be out of service. Before continuing, ensure that there are no dispenser or register transactions in progress. Press YES when ready or NO to cancel" not in get_message:
            log.error("Message is not displayed")
        
        if not mws.click_toolbar("No"):
            log.error("Unable to click on No button")
    
    else:
        # Get validation message
        get_message = mws.get_top_bar_text()
        if "Please verify the GVR ID and re-enter. Default GVR ID cannot be used again." not in get_message:
            log.error("Validation message is not displayed")
        if not mws.click_toolbar("Ok"):
            log.error("Oka button is not working")
        
        if not mws.click_toolbar("Exit"):
            log.error("Unable to click on exit button")
    
    return True

class SWUpgrade_Validate_Default_GVR_ID():
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
        # Update null date value in DB
        if not SWUpgrade_ActivationTool_Verify_UI.connect_mws_db():
            log.error("Unable to update date value in DB")
        
        # Update null gilbarco id in DB
        if not SWUpgrade_ActivationTool_Verify_UI.connect_mws_db(data_value='', id='10352'):
            log.error("Unable to connect with DB and failed to update the data")

    @test
    def verify_default_gvrid_use_multiple_time(self):
        """
        Testlink Id: SL-1810: Default GVR ID
		Description: Verify if value of AllowDefaultGVRID is true in registry editor then verify we can use default gvr id multiple time to install software
        Args: None
        Returns: None
        """
        
        # Set allow default gvr id value as true in registry editor
        key = r'SOFTWARE\WOW6432Node\Gilbarco\Passport\MWS'
        open_regedit_path = reg.OpenKey(reg.HKEY_LOCAL_MACHINE, key, 0, reg.KEY_ALL_ACCESS)
        reg.SetValueEx(open_regedit_path,"AllowDefaultGVRID",0,reg.REG_SZ,"1")

        # Generate approval code from hdactivation tool
        approval_code = generate_approval_code_from_hdactivation(gvrid="239686")

        # Use default GVR id for 1st time
        if not verify_default_gvr_id(allowdefaultGVRID= True, generated_code=approval_code):
            tc_fail("Unable to use default GVR id")
        
        # Update null date value in DB
        if not SWUpgrade_ActivationTool_Verify_UI.connect_mws_db():
            tc_fail("Unable to update date value in DB")
        
        # Use default GVR id for 2nd time
        if not verify_default_gvr_id(allowdefaultGVRID= True, generated_code=approval_code):
            tc_fail("Unable to use default GVR id")
        
        return True
    
    @test
    def verify_default_gvrid_use_one_time(self):
        """
        Testlink Id: SL-1810: Default GVR ID
		Description: Verify if value of AllowDefaultGVRID is false in registry editor then verify we can not use default gvr id multiple time to install software
        Args: None
        Returns: None
        """
        
        # Set allow default gvr id value as false in registry editor
        key = r'SOFTWARE\WOW6432Node\Gilbarco\Passport\MWS'
        open_regedit_path = reg.OpenKey(reg.HKEY_LOCAL_MACHINE, key, 0, reg.KEY_ALL_ACCESS)
        reg.SetValueEx(open_regedit_path,"AllowDefaultGVRID",0,reg.REG_SZ,"0")

        # Generate approval code from hdactivation tool
        approval_code = generate_approval_code_from_hdactivation(gvrid="239686")

        # Update null date value in DB
        if not SWUpgrade_ActivationTool_Verify_UI.connect_mws_db():
            tc_fail("Unable to update date value in DB")

        # Validate message if we use default GVR ID 2nd time
        if not verify_default_gvr_id(allowdefaultGVRID= False, generated_code=approval_code):
            tc_fail("Default GVR ID used second time")
        
        return True

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        pass