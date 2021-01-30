"""
    File name : DA_SaveEditDataForAdvertisement.py
    Tags:
    Description : Save/Edit on advertisement tab
    Story ID: SL-1472
    Author: Paresh
    Date created: 2019-03-12 13:31:37
    Date last modified: 
    Python Version: 3.7
"""

import logging
import time
from app import Navi, mws
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from pywinauto import Application
from Scripts.features import DA_LoadMediaFileFromUSB

def verifyErrorMessageForBlankValue(media_interval_value):
    """
    Description: Help function to enter zero value in media display interval field
    Args: media_interval_value: (str) The value of media interval time
    Returns: bool: True if succes, False if failure
    """
    mws.set_value("Media Display Interval", media_interval_value)
    mws.click_toolbar("Save")
    obj_verifyErroMessage = mws.get_top_bar_text()
    if "Please enter a number greater than zero for media display interval." not in obj_verifyErroMessage:
        self.log.error("Validation message for zero value is not displayed")
    mws.click_toolbar("OK")
    mws.click_toolbar("Exit")
    mws.click_toolbar("Yes")
    if "Please enter a number greater than zero for media display interval." not in obj_verifyErroMessage:
        self.log.error("Validation message for zero value is not displayed")
    mws.click_toolbar("OK")
    return True

class DA_SaveEditDataForAdvertisement():
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
        """SL-1477: Save/Edit on advertisement tab.
        Performs any initialization that is not default.
        Args: None
        Returns: None
        """
		
        DA_LoadMediaFileFromUSB.copy_mediaFiles()
        Navi.navigate_to("Express Lane Maintenance")
        mws.select_tab("Advertisement")
    
    @test
    def verify_MediaIntervalTimeDefualtValue(self):
        """
		Testlink Id: Verify media interval time default value is 10
        Args: None
        Returns: None
        """
		
        default_mediaIntervalValue = mws.get_value("Media Display Interval")
        if default_mediaIntervalValue != "10":
            tc_fail("Media interval time default value should be 10")

        return True

    @test
    def verify_noErrorMessageForEmptySelectedMediaList(self):
        """
		Testlink Id: Verify we are not getting error message for media interval time if we are not selecting any media files.
        Args: None
        Returns: None
        """
		
        mws.click("Media Display Interval")
        ojb_helpTextDisplayMessage = mws.get_top_bar_text()
        if "Please enter time between" not in ojb_helpTextDisplayMessage:
            tc_fail("Help text message is not displayed fro media interval time")   
        if not mws.set_value("Media Display Interval", 0):
            tc_fail("Interval time value is not set")
        mws.click_toolbar("Save")
        
        return True

    @test
    def verifyMediaIntervalValidationMessageForBlankValue(self):
        """
		Testlink Id: Verify validation message on for blank value in media interval time
        Args: None
        Returns: None
        """
        if not mws.wait_for_button("INFO"):
            tc_fail("Express lane maintenance icon is not displayed")
        time.sleep(10)
        Navi.navigate_to("Express Lane Maintenance")
        mws.select_tab("Advertisement")
        app1 = Application().connect(path="expresslanemaintenance.exe")
        window = app1.windows()[0]

        #Drag and drop media file
        for i in range(1,5):
            if not window.drag_mouse_input(dst=(268,284), src=(69,247), button="left"):
                tc_fail("Failed to drag and drop file")

        #Enter blank value in media display interval tab
        mws.set_value("Media Display Interval", "")
        mws.click_toolbar("Save")

        #Verify error message for media time interval by entering blank value
        obj_verifyErroMessage = mws.get_top_bar_text()
        if "Media display interval cannot be blank." not in obj_verifyErroMessage:
            tc_fail("Validation message for blank value is not displayed")
        mws.click_toolbar("OK")
        mws.click_toolbar("Exit")
        mws.click_toolbar("Yes")
        if "Media display interval cannot be blank." not in obj_verifyErroMessage:
            tc_fail("Validation message for blank value is not displayed")
        mws.click_toolbar("OK")
    
        return True
    
    @test
    def verifyMediaIntervalValidationMessageForZeroValue(self):
        """
		Testlink Id: Verify validation message on for zero value in media interval time
        Args: None
        Returns: None
        """

        #Verify error message for media time interval by entering 0 value
        if not verifyErrorMessageForBlankValue("0"):
            tc_fail("Validation message is not displayed")

        return True

    @test
    def verifyMediaIntervalValidationMessageForDoubleZeroValue(self):
        """
		Testlink Id: Verify validation message for double zero value in media interval time
        Args: None
        Returns: None
        """

        #Verify error message for media time interval by entering 00 value
        if not verifyErrorMessageForBlankValue("00"):
            tc_fail("Validation message is not displayed")

        return True

    @test
    def verifyMediaIntervalValidationMessageForTripleZeroValue(self):
        """
		Testlink Id: Verify validation message on for triple zero value in media interval time
        Args: None
        Returns: None
        """

        #Verify error message for media time interval by entering 000 value
        if not verifyErrorMessageForBlankValue("000"):
            tc_fail("Validation message is not displayed")


        return True

    @test
    def verifyAdvertisementPageAfterClickOnCancelButton(self):
        """
		Testlink Id: Verify we are on advertisement page if we are clicking on Exit > Cancel button
        Args: None
        Returns: None
        """
		
        mws.click_toolbar("Exit")
        mws.click_toolbar("Cancel")
        if not mws.wait_for_button("Save") and mws.wait_for_button("Exit"):
            tc_fail("Exit from Advertisement Page")
        
        return True
    
    @test
    def verifyDataIsNotSavedAfterClickOnNoButton(self):
        """
		Testlink Id: Verify we are on advertisement page if we are clicking on Exit > Cancel button
        Args: None
        Returns: None
        """
		
        mws.click_toolbar("Exit")
        mws.click_toolbar("NO")
        Navi.navigate_to("Express Lane Maintenance")
        mws.select_tab("Advertisement")
        getSelectedMediaList = mws.get_value("Selected Media Files")
        if len(getSelectedMediaList) != 0:
            tc_fail("Media list is saved after click on Exit>No button")
        
        return True  

    @test
    def verifyOnlyTenMediaFileCanSelected(self):
        """
		Testlink Id: Verify we can only select 10 media files in selected media list
        Args: None
        Returns: None
        """
		
        app1 = Application().connect(path="expresslanemaintenance.exe")
        window = app1.windows()[0]
        for i in range(1,12):
            if not window.drag_mouse_input(dst=(268,284), src=(69,247), button="left"):
                tc_fail("Failed to drag and drop file")
            if i >= 11:
                getValidationMessage = mws.get_top_bar_text()
                if "Selected media files cannot exceed 10" not in getValidationMessage:
                    tc_fail("Validation message for selected media file limit is 10 is not displayed")
        mws.click_toolbar("OK")
        mws.click_toolbar("Exit")
        mws.click_toolbar("NO")        
        
        return True
    
    @test
    def verifyMediaFileIsSaveAfterClickOnSave(self):
        """
		Testlink Id: Verify we can able to save media files after click on Save button
        Args: None
        Returns: None
        """
        
        if not mws.wait_for_button("INFO"):
            tc_fail("Info button is not visible")
        time.sleep(10)
        Navi.navigate_to("Express Lane Maintenance")
        mws.select_tab("Advertisement")
		
	    #Store the value of selected media list before drag and drop
        mediaListBeforeSave = len(mws.get_value("Selected Media Files"))
        app1 = Application().connect(path="expresslanemaintenance.exe")
        window = app1.windows()[0]
        if not window.drag_mouse_input(dst=(268,284), src=(69,247), button="left"):
            tc_fail("Failed to drag and drop file")
        mws.set_value("Media Display Interval",10)
        mws.click_toolbar("Save")
		
		#Store the value of selected media list after drag and drop
        if not mws.wait_for_button("INFO"):
            tc_fail("Info button is not visible")
        time.sleep(10)
        Navi.navigate_to("Express Lane Maintenance")
        mws.select_tab("Advertisement")
        mediaListAfterSave = len(mws.get_value("Selected Media Files"))
        
        if mediaListBeforeSave != mediaListAfterSave:
            flag = 0
            available_mediaList = mws.get_value("Available Media Files")
            selected_mediaList = mws.get_value("Selected Media Files")
			#Check if selected media files are visible in available media list
            for media_file in available_mediaList:
                if media_file in selected_mediaList:
                    flag = 1
            if flag == 1:
                tc_fail("Media files are visible in available media list also")
        else:
            tc_fail("Media Files are not saved")  
		
        return True
		
    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
		
		#Drag and drop media files from selected media file list to available media file list
        app1 = Application().connect(path="expresslanemaintenance.exe")
        window = app1.windows()[0]
        if not window.drag_mouse_input(dst=(69,247), src=(281,247), button="left"):
            self.log.error("Failed to drag and drop media file")
        mws.click_toolbar("Save")
        
        #Delete all the files from folder
        DA_LoadMediaFileFromUSB.delete_mediaFiles()