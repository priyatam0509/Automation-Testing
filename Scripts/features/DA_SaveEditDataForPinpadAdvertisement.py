"""
    File name : DA_SaveEditDataForPinpadAdvertisement.py
    Tags:
    Description : Save/Edit Pinpad
    Story ID: SL-1558
    Author: Sanjay
    Date created: 2019-03-12 13:31:37
    Date last modified: 
    Python Version: 3.7
"""

import logging
import time
from app import Navi, mws
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from pywinauto import Application
from Scripts.features import DA_Verify_UI_Of_PinPadAdvertisement
   	
class DA_SaveEditDataForPinpadAdvertisement():
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
        """SL-1558: Save/Edit on PIN Pad Advertisement tab.
        Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        DA_Verify_UI_Of_PinPadAdvertisement.copy_mediaFiles()
        Navi.navigate_to("PIN Pad Advertisement")
    
    @test
    def verify_MediaIntervalTimeDefualtValue(self):
        """
		Testlink Id: Verify media interval time default value is 10
        Args: None
        Returns: None
        """
		
        default_mediaIntervalValue = mws.get_value("Pinpad Media Display Interval")
        if default_mediaIntervalValue != "10":
            tc_fail("Pin pad Media interval time default value should be 10")

        return True

    @test
    def verify_noErrorMessageForEmptySelectedMediaList(self):
        """
		Testlink Id: Verify we are not getting error message for media interval time if we are not selecting any media files.
        Args: None
        Returns: None
        """
		
        mws.click("Pinpad Media Display Interval")
        ojb_helpTextDisplayMessage = mws.get_top_bar_text()
        if "Please enter time between" not in ojb_helpTextDisplayMessage:
            tc_fail("Help text message is not displayed for media interval time")   
        mws.set_value("Pinpad Media Display Interval", 0)
        mws.click_toolbar("Save")
        
        return True

    @test
    def verifyMediaIntervalValidationMessageForBlankValue(self):
        """
		Testlink Id: Verify validation message for blank value in media interval time
        Args: None
        Returns: None
        """
        if not mws.wait_for_button("INFO"):
            tc_fail("Info icon is not displaye")
        time.sleep(10)
        Navi.navigate_to("PIN Pad Advertisement")
        app1 = Application().connect(path="pinpadAdvertisement.exe")
        window = app1.windows()[0]

        #Drag and drop media file
        if not window.drag_mouse_input(dst=(384,299), src=(176,240), button="left"):
            tc_fail("Failed to drag and drop file")

        #Enter blank value in media display interval tab
        mws.set_value("Pinpad Media Display Interval", "")
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

    def verifyErrorMessageForZeroValue(media_interval_value):
        """
        Description: Help function to set zero value in media interval time
		Args:
            media_interval_value: (str) The value of media display interval time
		Returns:
            bool: True if succes, False if failure
		"""
		
        mws.set_value("Pinpad Media Display Interval", media_interval_value)
        mws.click_toolbar("Save")
        obj_verifyErroMessage = mws.get_top_bar_text()
        if "Please enter a number greater than zero for media display interval." not in obj_verifyErroMessage:
            tc_fail("Validation message for zero value is not displayed")
        mws.click_toolbar("OK")
        mws.click_toolbar("Exit")
        mws.click_toolbar("Yes")
        if "Please enter a number greater than zero for media display interval." not in obj_verifyErroMessage:
            tc_fail("Validation message for zero value is not displayed")
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
        if not DA_SaveEditDataForPinpadAdvertisement.verifyErrorMessageForZeroValue("0"):
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
        if not DA_SaveEditDataForPinpadAdvertisement.verifyErrorMessageForZeroValue("00"):
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
        if not DA_SaveEditDataForPinpadAdvertisement.verifyErrorMessageForZeroValue("000"):
            tc_fail("Validation message is not displayed")
        
        return True

   
    @test
    def verifyAdvertisementPageAfterClickOnCancelButton(self):
        """
		Testlink Id: Verify we are on PIN Pad Advertisement page if we are clicking on Exit > Cancel button
        Args: None
        Returns: None
        """
		
        mws.click_toolbar("Exit")
        mws.click_toolbar("Cancel")
        if not mws.wait_for_button("Save") and mws.wait_for_button("Exit"):
            tc_fail("Exit from PIN Pad Advertisement Page")
        
        return True
    
    @test
    def verifyDataIsNotSavedAfterClickOnNoButton(self):
        """
		Testlink Id: Verify we are on PIN Pad Advertisement page if we are clicking on Exit > Cancel button
        Args: None
        Returns: None
        """
		
        mws.click_toolbar("Exit")
        mws.click_toolbar("NO")
        if not mws.wait_for_button("INFO"):
            tc_fail("PIN Pad Advertisement icon is not displayed")
        
        Navi.navigate_to("PIN Pad Advertisement")
        mws.select_tab("PIN Pad Advertisement")
        getSelectedMediaList = mws.get_value("Pinpad Selected Media Files")
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
		
        app1 = Application().connect(path="pinpadAdvertisement.exe")
        window = app1.windows()[0]
        for i in range(1,12):
            if not window.drag_mouse_input(dst=(384,299), src=(176,240), button="left"):
                tc_fail("Failed to drag and drop file")
            if i >= 11:
                getValidationMessage = mws.get_top_bar_text()
                if "Selected media files cannot exceed 10." not in getValidationMessage:
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
            tc_fail("Inof button is not visible")
        time.sleep(10)
        Navi.navigate_to("PIN Pad Advertisement")
		
		#Store the value of selected media before drag and drop
        mediaListBeforeSave = len(mws.get_value("Pinpad Selected Media Files"))
        app1 = Application().connect(path="pinpadAdvertisement.exe")
        window = app1.windows()[0]
        if not window.drag_mouse_input(dst=(384,299), src=(176,240), button="left"):
            tc_fail("Failed to drag and drop file")
        mws.set_value("Pinpad Media Display Interval",10)
        mws.click_toolbar("Save")
		
		#Store the value of selected media after drag and drop
        
        if not mws.wait_for_button("INFO"):
            tc_fail("Inof button is not visible")
        time.sleep(10)
        Navi.navigate_to("PIN Pad Advertisement")
        mediaListAfterSave = len(mws.get_value("Pinpad Selected Media Files"))
        
        if mediaListBeforeSave != mediaListAfterSave:
            flag = 0
            available_mediaList = mws.get_value("Pinpad Available Media Files")
            selected_mediaList = mws.get_value("Pinpad Selected Media Files")
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
        
        app1 = Application().connect(path="pinpadAdvertisement.exe")
        window = app1.windows()[0]

        #Drag and drop image file
        if not window.drag_mouse_input(dst=(184,324), src=(364,239), button="left"):
            self.log.error("Failed to drag and drop image file")
        mws.click_toolbar("Save")

       
        #Delete all the files from folder
        DA_Verify_UI_Of_PinPadAdvertisement.delete_mediaFiles()