"""
    File name : DA_DragAndDropMediaFilesForPinPad.py
    Tags:
    Description : Verify we are able to drag and drop media files and populate all the fields on pin pad advertisement page.
	Story ID: SL-1478
    Author: Paresh
    Date created: 2019-08-11 13:31:37
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import Navi, mws
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from pywinauto import Application
from Scripts.features import DA_Verify_UI_Of_PinPadAdvertisement

class DA_DragAndDropMediaFilesForPinPad():
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
        DA_Verify_UI_Of_PinPadAdvertisement.copy_mediaFiles()
        Navi.navigate_to("PIN Pad Advertisement")

    @test
    def dragAndDrop_availableImageFiles(self):
        """
	    Testlink Id: Verify we are able to drag and drop 1 image file from available image list to selected image list.
        Args: None
        Returns: None
        """
		
        app1 = Application().connect(path="pinpadAdvertisement.exe")
        window = app1.windows()[0]

        #Drag and drop image file
        for i in range(1,5):
            if not window.drag_mouse_input(dst=(384,299), src=(176,240), button="left"):
                tc_fail("Failed to drag and drop image file")

        return True
    
    @test
    def verify_sorting_for_selectedImageFiles(self):
        """
	    Testlink Id: Verify we are able to perform sorting in selected image file list
        Args: None
        Returns: None
        """
		
        app1 = Application().connect(path="pinpadAdvertisement.exe")
        window = app1.windows()[0]

        #sort image file from first position to last position
        if not window.drag_mouse_input(dst=(370,292), src=(357,237), button="left"):
            tc_fail("Failed to sort the image file")

        #sort image file from second position to third position
        if not window.drag_mouse_input(dst=(369,274), src=(371,249), button="left"):
            tc_fail("Failed to sort the image file")

        return True
   
    @test
    def dragAndDrop_selectedImageFiles(self):
        """
	    Testlink Id: Verify we are able to drag and drop 1 image file from selected image list to available image list.
        Args: None
        Returns: None
        """
		
        app1 = Application().connect(path="pinpadAdvertisement.exe")
        window = app1.windows()[0]

        #Drag and drop image file
        if not window.drag_mouse_input(dst=(184,324), src=(364,239), button="left"):
            tc_fail("Failed to drag and drop image file")
       
        return True
    
    @test
    def verify_selectedImageFilesNotVisibleInAvailableImageList(self):
        """
	    Testlink Id: Verify selected image files are not visible in available image list.
        Args: None
        Returns: None
        """
		
        flag = 0

        available_imageList = mws.get_value("Pinpad Available Media Files")
        if len(available_imageList) == 0:
            tc_fail("Available image list view is not displayed")
        
        selected_imageList = mws.get_value("Pinpad Selected Media Files")
        if len(selected_imageList) == 0:
            tc_fail("Selected image list view is not displayed")

        #Check if selected image files are visible in available image list
        for image_file in available_imageList:
            if image_file in selected_imageList:
                flag = 1
        if flag == 1:
            tc_fail("image files are visible in available image list also")
        
        return True

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
		
        mws.recover()
        
        #Delete all the files from folder
        DA_Verify_UI_Of_PinPadAdvertisement.delete_mediaFiles()