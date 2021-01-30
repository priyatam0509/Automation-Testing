"""
    File name : DA_VerifyHelpTextMessageForAdvertisementPage.py
    Tags:
    Description : Display help text for sorting media images and supported files
    Story ID: SL-1655
    Author: Paresh
    Date created: 2020-01-27 13:31:37
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import Navi, mws
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from pywinauto import Application
from Scripts.features import DA_LoadMediaFileFromUSB

class DA_VerifyHelpTextMessageForAdvertisementPage():
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
        """SL-1655: Display help text for sorting media images and supported files
        Performs any initialization that is not default.
        Args: None
        Returns: None
        """
		
        DA_LoadMediaFileFromUSB.copy_mediaFiles()
        Navi.navigate_to("Express Lane Maintenance")
        mws.select_tab("Advertisement")

    @test
    def verfiyMessageAfterDragAndDropMediaFiles(self):
        """
		Testlink Id: Verify we are able to drag nd drop 1 media file from available media list to selected media list and validate the message.
        Args: None
        Returns: None
        """
		
        app1 = Application().connect(path="expresslanemaintenance.exe")
        window = app1.windows()[0]

        #Drag and drop media file
        if not window.drag_mouse_input(dst=(268,284), src=(69,247), button="left"):
            tc_fail("Failed to drag and drop file")
        
        obj_getMessage = mws.get_top_bar_text()
       
        if "Selected media files are displayed in the order they appear." not in obj_getMessage:
            tc_fail("Message is not displayed for selected media files")
        
        mws.click("Selected Media Files")
        if "Selected media files are displayed in the order they appear." not in obj_getMessage:
            tc_fail("Message is not displayed for selected media files")
        
        mws.click_toolbar("Exit")
        mws.click_toolbar("No")

        return True
		
    @test
    def dragAndDrop_availableMediaFiles(self):
        """
		Testlink Id: Verify we are able to drag nd drop 1 media file from available media list to selected media list.
        Args: None
        Returns: None
        """
		 
        Navi.navigate_to("Express Lane Maintenance")
        mws.select_tab("Advertisement")
        app1 = Application().connect(path="expresslanemaintenance.exe")
        window = app1.windows()[0]

        #Drag and drop media file
        if not window.drag_mouse_input(dst=(268,284), src=(69,247), button="left"):
            tc_fail("Failed to drag and drop .gif file")
        
        obj_getMessage = mws.get_top_bar_text()
        if "Selected media files are displayed in the order they appear." not in obj_getMessage:
            tc_fail("Message is not displayed for selected media files")
    
        mws.click_toolbar("Exit")
        mws.click_toolbar("No")
        
        return True

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        Args: None
        Returns: None
        """

        #Delete all the files from folder
        DA_LoadMediaFileFromUSB.delete_mediaFiles()     