"""
    File name : DA_DragAndDropMediaFilesForAdvertisement.py
    Tags:
    Description : Verify we are able to drag and drop media files and populate all the fields on advertisement page
    Stroy ID: SL-1478
    Author: Paresh
    Date created: 2019-08-11 13:31:37
    Date last modified: 
    Python Version: 3.7
"""

import logging, time

from app import Navi, mws
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from pywinauto import Application
from Scripts.features import DA_LoadMediaFileFromUSB

class DA_DragAndDropMediaFilesForAdvertisement():
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
        """SL-1478: Populate all the fields with values and user can able to do drag and drop across list box.
        Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        DA_LoadMediaFileFromUSB.copy_mediaFiles()
        Navi.navigate_to("Express Lane Maintenance")
        mws.select_tab("Advertisement")
   
    @test
    def dragAndDrop_availableMediaFiles(self):
        """
	    Testlink Id: Verify we are able to drag and drop 1 media file from available media list to selected media list.
        Args: None
        Returns: None
        """
		
        app1 = Application().connect(path="expresslanemaintenance.exe")
        window = app1.windows()[0]

        #Drag and drop media file
        for i in range(1,5):
            if not window.drag_mouse_input(dst=(268,284), src=(69,247), button="left"):
                tc_fail("Failed to drag and drop media file")
        
        return True
    
    @test
    def verify_sorting_for_selectedMediaFiles(self):
        """
	    Testlink Id: Verify we are able to perform sorting in selected media file list
        Args: None
        Returns: None
        """
		
        app1 = Application().connect(path="expresslanemaintenance.exe")
        window = app1.windows()[0]

        #sort media file from first position to last position
        if not window.drag_mouse_input(dst=(275,297), src=(277,248), button="left"):
            tc_fail("Failed to sort the media file")

        #sort media file from second position to third position
        if not window.drag_mouse_input(dst=(271,285), src=(277,267), button="left"):
            tc_fail("Failed to sort the media file")

        return True
   
    @test
    def dragAndDrop_selectedMediaFiles(self):
        """
	    Testlink Id: Verify we are able to drag and drop 1 media file from selected media list to available media list.
        Args: None
        Returns: None
        """
		
        app1 = Application().connect(path="expresslanemaintenance.exe")
        window = app1.windows()[0]

        #Drag and drop media file
        if not window.drag_mouse_input(dst=(69,247), src=(281,247), button="left"):
            tc_fail("Failed to drag and drop media file")
       
        return True
    
    @test
    def verify_selectedMediaFiles_notVisibleInAvailableMediaList(self):
        """
	    Testlink Id: Verify selected media files are not visible in available media list.
        Args: None
        Returns: None
        """
		
        flag = 0

        available_mediaList = mws.get_value("Available Media Files")
        if len(available_mediaList) == 0:
            tc_fail("Available media list view is not displayed")
        
        selected_mediaList = mws.get_value("Selected Media Files")
        if len(selected_mediaList) == 0:
            tc_fail("Selected media list view is not displayed")

        #Check if selected media files are visible in available media list
        for media_file in available_mediaList:
            if media_file in selected_mediaList:
                flag = 1
        if flag == 1:
            tc_fail("Media files are visible in available media list also")
        
        mws.click_toolbar("Exit")
        time.sleep(5)
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