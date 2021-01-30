"""
    File name : DA_LoadMediaFileFromUSB.py
    Tags:
    Description : Verify we are able to load media file from USB and can see in list view.
    Story ID: SL-1479
    Author: Paresh
    Date created: 2019-08-11 13:31:37
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import Navi, mws
from app.framework.tc_helpers import setup, test, teardown, tc_fail
import os
from shutil import copyfile
from pywinauto import application

local_dir = "D:/Automation/Scripts/data/DigitalAd/"
branding_imageDir = "D:/gilbarco/BrandingImages/DigitalAdvertising/ExpressLane/"
log = logging.getLogger()

def copy_mediaFiles():
    """
    Description: Help function to copy media file from local folder to USB drive
    Args: None
    Returns: None
    """
    #Create a driectory if not exists
    if not os.path.exists(branding_imageDir):
        os.makedirs(branding_imageDir)
        log.info("Branding image directory created")
    else:
        log.info("Branding image directory already exists")
        
    get_file_list = len(os.listdir(local_dir))
    if get_file_list != 0:
        try:
            for files in os.listdir(local_dir):
                file_list = os.path.join(local_dir,files)
                if os.path.isfile(file_list):
                    copyfile(local_dir + files, branding_imageDir + files)
                    log.info(f"Copied [{local_dir}{files}] to [{branding_imageDir}]")
                else:
                    log.error(f"Failed to copy [{local_dir}{files}] to [{branding_imageDir}]")
        except Exception as e:
            log.error("File Not Found in directory")
            raise e
    else:
        log.error("Local file directory is empty.")

    return True

def delete_mediaFiles():
    """
    Description: Delete all the files from folder
    Args: None
    Returns: None
    """
    
    for files in os.listdir(branding_imageDir):
        file_path = os.path.join(branding_imageDir,files)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            log.error("Media files are not deleted from directory" +e)
            raise e
    
    return True
    
class DA_LoadMediaFileFromUSB():
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
        """SL-1479: Load media file from USB.
        Performs any initialization that is not default.
        Args: None
        Returns: None
        """
		
        Navi.navigate_to("Express Lane Maintenance")
        mws.select_tab("Advertisement")

    @test
    def verify_message_for_empty_usb(self):
        """
        TestLink Id: Verify validation message if we are inserting an empty USB.
        Args: None
        Returns: None
        """
		
        mws.click_toolbar("Download From USB")
        obj_message = mws.get_top_bar_text()
        if "Failed to locate any Advertisement Media." in obj_message:
            self.log.info("USB drive is empty.")
        else:
            tc_fail("Message is not displayed for Empty USB")
        mws.click_toolbar("Cancel")
        
        return True
    
    @test
    def copy_mediaFilesFromLocalToUSB(self):
        """
	    Testlink Id: Copy all types of files from local directory to Brandin Image Directory.
        Args: None
        Returns: None
        """
		
        if not copy_mediaFiles():
            tc_fail("media files are not copied.")
        mws.click_toolbar("Exit")
        if mws.wait_for_button("No"):
            mws.click_toolbar("No")
        
        return True
    
    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        Args: None
        Returns: None
        """      
		
        delete_mediaFiles()