"""
    File name : DA_Verify_UI_Of_PinPadAdvertisement.py
    Tags:
    Description : Need a new interface for advertisement on pin pad
    Story ID: SL-1557
    Author: Sanjay
    Date created: 2019-04-12 13:31:37
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
imageDir = "D:/gilbarco/BrandingImages/DigitalAdvertising/Pinpad/"
log = logging.getLogger()

def copy_mediaFiles():
    """
    Description: Help function to copy media file from local folder to Pin pad image directory
    Args: None
    Returns: None
    """
    #Create a driectory if not exists
    if not os.path.exists(imageDir):
        os.makedirs(imageDir)
        log.info("Pin pad image directory created")
    else:
        log.info("Pin pad image directory already exists")
    
    get_file_list = len(os.listdir(local_dir))
    if get_file_list != 0:
        try:
            for files in os.listdir(local_dir):
                file_list = os.path.join(local_dir,files)
                if os.path.isfile(file_list):
                    copyfile(local_dir + files, imageDir + files)
                    log.info(f"Copied [{local_dir}{files}] to [{imageDir}]")
                else:
                    log.error(f"Failed to copy [{local_dir}{files}] to [{imageDir}]")
        except Exception as e:
            log.error("File Not Found in directory")
            raise e
    else:
        log.error("Local file directory is empty.")
        return False

    return True
	
def delete_mediaFiles():
    """
    Description: Delete all the files from folder
    Args: None
    Returns: None
    """

    for files in os.listdir(imageDir):
        file_path = os.path.join(imageDir,files)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            log.error("Images are not deleted from directory" +e)
            raise e
    
    return True

class DA_Verify_UI_Of_PinPadAdvertisement():
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
        """SL-1557: Need a new interface for advertisement on pin pad.
        Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        Navi.navigate_to("PIN Pad Advertisement")
    
    @test
    def copy_imagesFromLocalToUSB(self):
        """
		Testlink Id: Copy all types of files from local directory to USB drive.
        Args: None
        Returns: None
        """
		
        if not copy_mediaFiles():
            tc_fail("Images are not uploaded")
            
        return True
        
    @test
    def verify_message_for_empty_usb(self):
        """
        TestLink Id: Verify validation message if we are inserting an empty USB.
        Args: None
        Returns: None
        """
		
        mws.click_toolbar("Download From USB")
        obj_message = mws.get_top_bar_text()
        if "Failed to locate any Advertisement Images." in obj_message:
            self.log.info("USB drive is empty.")  
        else:
            tc_fail("Message is not displayed for Empty USB")
        mws.click_toolbar("Cancel")
        
        return True
		
    @test
    def verify_elementIsVisibleonPinPadAdvertisement_page(self):
        """
		Testlink Id: Verify  all the elements are visible on page.
        Args: None
        Returns: None
        """
		
        if not mws.wait_for_button("Save"):
            tc_fail("Save button is not visible.")
        if not mws.wait_for_button("Exit"):
            tc_fail("Exit button is not visible.")
        if not mws.wait_for_button("Download from USB"):
            tc_fail("Download from USB button is not visible.")
        if not mws.wait_for_button("Delete Image"):
            tc_fail("Delete Media button is not visible.")
        if not mws.click("Pinpad Media Display Interval"):
            tc_fail("Media Display Interval textbox is not visible.")
        mws.click_toolbar("Download from USB")
        if not mws.wait_for_button("Cancel"):
            tc_fail("Cancel button is not visible.")
        if not mws.wait_for_button("Refresh"):
            tc_fail("Refresh button is not visible.")
        mws.click_toolbar("Cancel")
        mws.click_toolbar("Exit")
    
    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        delete_mediaFiles()