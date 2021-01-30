"""
    File name: DA_Verify_Validation_OnSaveAndExitButton.py
    Tags:
    Description: All validation on filed during Save and Exit button on Express Lane Maintenance
    Stroy ID: SL-1477
    Author: Paresh
    Date created: 2019-27-11 13:31:37
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import Navi, mws
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from pywinauto import Application

log = logging.getLogger()

def editDataInExpressLaneMaintenance(buttonName, config):
    """
    Description: Help function to edit the data on Expresss Lane Maintenance tab
    Args:
		buttonName: (str) The Name of button
		config: (str) Configuration data for edit the field
    Returns:
	   bool: True if succes, False if failure
    """
    for tab in config:
        mws.select_tab(tab)
        for key, value in config[tab].items():
            if not mws.set_value(key, value, tab):
                log.error(f"Could not set {key} with {value} on the {tab} tab.")
                return False
            mws.click_toolbar("Exit")
            if not mws.wait_for_button(buttonName):
                log.error(buttonName + " button is not visible")
            mws.click_toolbar(buttonName)
            if buttonName == "Cancel":
                if not mws.wait_for_button("Save"):
                    log.error("Exit from Express Lane Maintenance tab")
            elif not mws.wait_for_button("INFO"):
                log.error("Failed to exit from Express Lane Maintenance tab")
            Navi.navigate_to("Express Lane Maintenance")
    
    return True   

class DA_Verify_Validation_OnSaveAndExitButton():
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
        self.log = logging.getLogger()

    @setup
    def setup(self):
        """SL-1477: All validation on filed during Save and Exit button on Express Lane Maintenance
        Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        Navi.navigate_to("Express Lane Maintenance")

    
    @test
    def verifyExpressLaneMaintenancePage_afterClickOnCancelButton(self):
        """
		Testlink Id: Verify we are on express lane maintenance page after changing the data and clicking on Exit > Cancel
        Args: None
        Returns: None
        """
		
        config = {
            "General":{
                "Display thank you for" : 10
                },
            "Branding":{
                "Pre-Transaction" : "None"
                }
            }
        editDataInExpressLaneMaintenance("Cancel", config)
        
        return True

    @test
    def exitFromExpressLaneMaintenance_afterChangingData(self):
        """
		Testlink Id: Verify we are able to exit from express lane maintenance after changing the data and clicking on Exit > No
        Args: None
        Returns: None
        """
		
        config = {
            "General":{
                "Display thank you for" : 15
                },
            "Branding":{
                "Pre-Transaction" : "None"
                }
            }
        editDataInExpressLaneMaintenance("No", config)
        
        return True
    
    @test
    def exitFromExpressLaneMaintenance_afterSavingData(self):
        """
		Testlink Id: Verify we are able to exit from express lane maintenance after changing the data and clicking on Exit > Yes
        Args: None
        Returns: None
        """
		
        config = {
            "General":{
                "Display thank you for" : 20
                },
            "Branding":{
                "Pre-Transaction" : "None"
                }
            }
        editDataInExpressLaneMaintenance("Yes", config)
        mws.select_tab("General")
        get_displayThankYouForValue = mws.get_text("Display thank you for")
        if get_displayThankYouForValue != "20":
            tc_fail("Value is not updated as per config list")
        
        return True
    
    @test
    def saveDataAfterClickOnSaveButton(self):
        """
		Testlink Id: Verify we are able to save data and exit from express lane maintenance after changing the data and clicking on Save button
        Args: None
        Returns: None
        """
		
        config = {
            "General":{
                "Display thank you for" : 25
                },
            "Branding":{
                "Transaction" : "None"
                }
            }
        for tab in config:
            mws.select_tab(tab)
            for key, value in config[tab].items():
                if not mws.set_value(key, value, tab):
                    self.log.error(f"Could not set {key} with {value} on the {tab} tab.")
                    return False
                mws.click_toolbar("Save")
            if not mws.wait_for_button("Express Lane Maintenance"):
                tc_fail("Failed to save the data and exit from express lane maintenance")
            Navi.navigate_to("Express Lane Maintenance")
        
        mws.select_tab("General")
        get_displayThankYouForValue = mws.get_text("Display thank you for")
        if get_displayThankYouForValue != "25":
            tc_fail("Value is not updated as per config list")
        
        return True

    @test
    def verifyErrorMessageForBlankValue(self):
        """
		Testlink Id: Verify error message is displayed if we are putting blank value for any field.
        Args: None
        Returns: None
        """
		
        mws.set_value("Display thank you for", "")
        mws.click_toolbar("Save")
        
        errorMessage = mws.get_top_bar_text()
        if "The errors in red must be corrected" not in errorMessage:
            tc_fail("Error message is not displayed")
        mws.click_toolbar("OK")
        
        mws.select_tab("Branding")
        mws.click_toolbar("Save")
	    
        if "The errors in red must be corrected" not in errorMessage:
            tc_fail("Error message is not displayed")
        mws.click_toolbar("OK")
        mws.click_toolbar("Exit")
        mws.click_toolbar("Yes")
        if "The errors in red must be corrected" not in errorMessage:
            tc_fail("Error message is not displayed")
        mws.click_toolbar("OK")
        mws.click_toolbar("Exit")
        mws.click_toolbar("No")
        
        return True
    
    @test
    def verifyDataSavedFromOtherTab(self):
        """
		Testlink Id: Verify we are able to edit the data and save the data from other tab
        Args: None
        Returns: None
        """
		
        #verify data is saved after edit the data and saved from another tab by clicking on Save button
        Navi.navigate_to("Express Lane Maintenance")
        mws.select_tab("General")
        mws.set_value("Display thank you for", 30)
        mws.select_tab("Branding")
        mws.click_toolbar("Save")
	
        if not mws.wait_for_button("INFO"):
            tc_fail("Failed to exit from Express Lane Maintenance tab")
        
		#Verify data is updated after saving
        Navi.navigate_to("Express Lane Maintenance")
        mws.select_tab("General")
        get_displayThankYouForValue = mws.get_text("Display thank you for")
        if get_displayThankYouForValue != "30":
            tc_fail("Value is not updated as per config list")
        
        #verify data is saved after edit the data and saved from another tab by clicking on Exit>Yes button
        mws.set_value("Display thank you for", 35)
        mws.select_tab("Branding")
        mws.click_toolbar("Exit")
        mws.click_toolbar("Yes")
        if not mws.wait_for_button("INFO"):
            tc_fail("Failed to exit from Express Lane Maintenance tab")
        
		#Verify data is updated after saving
        Navi.navigate_to("Express Lane Maintenance")
        mws.select_tab("General")
        get_displayThankYouForValue = mws.get_text("Display thank you for")
        if get_displayThankYouForValue != "35":
            tc_fail("Value is not updated as per config list")
        
        return True

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
		
        #Restore Default Values
        mws.select_tab("Branding")
        mws.set_value("Pre-Transaction","DefaultPreTrans.png")
        mws.set_value("Transaction","DefaultTrans.png")
        mws.click_toolbar("Save")
        mws.click_toolbar("Yes")