"""
    File name: SWUpgrade_ActivationTool_UI_OnStore_Close.py
    Tags:
    Description: SL-1746/SL-1862: Upgrade blocker pop up on installation via store close
    Brand: Concord
    Author: Paresh
    Date created: 2020-19-04 19:11:00
    Date last modified:
    Python Version: 3.7
"""

import logging, time
from datetime import datetime, timedelta
from app import Navi, mws, pos, initial_setup
from app.features import register_setup
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from Scripts.features import SWUpgrade_ActivationTool_Verify_UI


log = logging.getLogger()

def verify_softwareUpgradeActivation_tool_UI(buttonName="MWS"):
    """
    Description: Help function to validate UI is visible or not
    Args:
        buttonName: Pass the button name, from which way we are performing store close via MWS or POS
    Returns: None 
    """
    if buttonName is "MWS":
        if not Navi.navigate_to("Store Close"):
            log.error("Unable to navigate to Store close")
        
        if not mws.click_toolbar("Start"):
            log.error("Unable to click on Start button")
        
        if not mws.click_toolbar("Install Software"):
            log.error("Unable to click on install software button")

    
    elif buttonName is "POS":
        #Navigate to POS screen
        if not Navi.navigate_to("POS"):
            log.error("Unable to navigate on POS")
        
        start_time = time.time()
        while time.time()-start_time <= 120:
            # Sign on to POS screen if not already sign-on
            if not pos.sign_on():
                log.error("Unable to perform sign on")
        
        if not pos.click_function_key("MORE"):
            log.error("Unable to click on More button")
        
        if not pos.click_function_key("MORE"):
            log.error("Unable to click on More button")
        
        if not pos.click_function_key("TOOLS"):
            log.error("Unable to click on Tools button")

        if not pos.click_tools_key("STORE CLOSE"):
            log.error("Unable to click on Store close")
        
        if not pos.click_message_box_key("YES"):
            log.error("Unable to click on message box")
        
        if not pos.click_local_account_details_key("INSTALL"):
            log.error("Unable to click on install button")

    
    if not mws.click("GVR ID"):
        log.error("GVR ID text box is not visible")
        
    for i in range(1, 5):
        if not mws.click("Approval Code"+str(i)):
            log.error("Approval code text box is not visible")
        
    if not mws.click_toolbar("Exit"):
        log.error("Exit button is not visible")
        
    return True


class SWUpgrade_ActivationTool_UI_OnStore_Close():
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
        # Perform register setup to add POS cofiguration
        obj = initial_setup.Initial_setup("passport")
        obj.configure_register()
        
    @test
    def verify_ui_for_null_date_on_store_close(self):
        """
        Testlink Id: SL-1746/SL-1862: Upgrade blocker pop up on installation via store close
		Description: Verify Activation tool UI is visible if date is null in DB when we are doing store close via MWS
        Args: None
        Returns: None
        """

        # Update null date value in DB
        if not SWUpgrade_ActivationTool_Verify_UI.connect_mws_db():
            tc_fail("Unable to update date value in DB")
        
        # Verify UI is visble after updating the null date value in DB on store close
        if not verify_softwareUpgradeActivation_tool_UI():
            tc_fail("Unable to see Sofware Activation Tool UI")
            
        return True
    
    @test
    def verify_ui_for_past_date_on_store_close(self):
        """
        Testlink Id: SL-1746/SL-1862: Upgrade blocker pop up on installation via store close
		Description: Verify Activation tool UI is visible if date is past in DB when we are doing store close via MWS
        Args: None
        Returns: None
        """

        past_date = datetime.strftime(datetime.now() - timedelta(1), '%m-%d-%Y')

        # Update past date value in DB
        if not SWUpgrade_ActivationTool_Verify_UI.connect_mws_db(data_value=past_date):
            tc_fail("Unable to update date value in DB")
    
        # Verify UI is visble after updating the past date value in DB on store close
        if not verify_softwareUpgradeActivation_tool_UI():
            tc_fail("Unable to see Sofware Activation Tool UI")
            
        return True
    
    @test
    def verify_ui_for_invalid_date_on_store_close(self):
        """
        Testlink Id: SL-1746/SL-1862: Upgrade blocker pop up on installation via store close
		Description: Verify Activation tool UI is not visible if date is invalid(date>today+365) in DB when we are doing store close via MWS
        Args: None
        Returns: None
        """

        invalid_date = datetime.strftime(datetime.now()- timedelta(-370), '%m-%d-%Y')

        # Update invalid date(date>today+365) value in DB
        if not SWUpgrade_ActivationTool_Verify_UI.connect_mws_db(data_value=invalid_date):
            tc_fail("Unable to update date value in DB")
            
        # Verify UI is visble after updating the invalid date value in DB on store close
        if not verify_softwareUpgradeActivation_tool_UI():
            tc_fail("Unable to see Sofware Activation Tool UI")
            
        return True
    
    @test
    def verify_ui_for_null_date_on_store_close_via_pos(self):
        """
        Testlink Id: SL-1746/SL-1862: Upgrade blocker pop up on installation via store close
		Description: Verify Activation tool UI is visible if date is null in DB when we are doing store close via POS
        Args: None
        Returns: None
        """

        # Update null date value in DB
        if not SWUpgrade_ActivationTool_Verify_UI.connect_mws_db():
            tc_fail("Unable to update date value in DB")
        
        # Verify UI is visble after updating the null date value in DB on store close
        if not verify_softwareUpgradeActivation_tool_UI(buttonName="POS"):
            tc_fail("Unable to see Sofware Activation Tool UI")
            
        return True
    
    @test
    def verify_ui_for_past_date_on_store_close_via_pos(self):
        """
        Testlink Id: SL-1746/SL-1862: Upgrade blocker pop up on installation via store close
		Description: Verify Activation tool UI is visible if date is past in DB when we are doing store close via POS
        Args: None
        Returns: None
        """

        past_date = datetime.strftime(datetime.now() - timedelta(1), '%m-%d-%Y')

        # Update past date value in DB
        if not SWUpgrade_ActivationTool_Verify_UI.connect_mws_db(data_value=past_date):
            tc_fail("Unable to update date value in DB")
    
        # Verify UI is visble after updating the past date value in DB on store close
        if not verify_softwareUpgradeActivation_tool_UI(buttonName="POS"):
            tc_fail("Unable to see Sofware Activation Tool UI")
            
        return True
    
    @test
    def verify_ui_for_invalid_date_on_store_close_via_pos(self):
        """
        Testlink Id: SL-1746/SL-1862: Upgrade blocker pop up on installation via store close
		Description: Verify Activation tool UI is not visible if date is invalid(date>today+365) in DB when we are doing store close via POS
        Args: None
        Returns: None
        """

        invalid_date = datetime.strftime(datetime.now()- timedelta(-370), '%m-%d-%Y')

        # Update invalid date(date>today+365) value in DB
        if not SWUpgrade_ActivationTool_Verify_UI.connect_mws_db(data_value=invalid_date):
            tc_fail("Unable to update date value in DB")
            
        # Verify UI is visble after updating the invalid date value in DB on store close
        if not verify_softwareUpgradeActivation_tool_UI(buttonName="POS"):
            tc_fail("Unable to see Sofware Activation Tool UI")
            
        return True

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        pass