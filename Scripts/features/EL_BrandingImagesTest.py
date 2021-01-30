"""
    File name: EL_BrandingImagesTest.py
    Tags:
    Description: 
    Author: Gene Todd
    Date created: 2019-08-20 09:27:45
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import Navi, mws
from app.framework.tc_helpers import setup, test, teardown, tc_fail
import math, operator, os
from functools import reduce
from PIL import Image
from shutil import copyfile

client_dir = "//POSCLIENT001/Service/Passport/ExpressLane/www/expresslane/unsecure/images/"
server_dir = "C:/Passport/ExpressLane/www/expresslane/unsecure/images/"
branding_dir = "D:/Gilbarco/BrandingImages/"
img_dir = "./Scripts/features/"
img_name = "test_image.png"
test_img = None

# Helper function to compare a client image to the test image
def compareToTestImage(imgName):
    diff = -1
    temp_img = Image.open(imgName)
    hist1 = test_img.histogram()
    hist2 = temp_img.histogram()
    diff = math.sqrt(reduce(operator.add, map(
        lambda a,b: (a-b)**2, hist1, hist2))/len(hist1)
    )
    temp_img.close()
    return diff

class EL_BrandingImagesTest():

    def __init__(self):
        self.log = logging.getLogger()

    @setup
    def setup(self):
        # Load our teat image and copy it to the branding directory
        # This lets us skip download from USB
        global test_img
        try:
            test_img = Image.open(img_dir + img_name)
            self.log.info(f"Loaded image from [{img_dir}{img_name}]")
        except Exception as e:
            self.log.warning(f"Failed to open testing image: {e}")
        try:
            copyfile(img_dir + img_name, branding_dir + img_name)
            self.log.info(f"Copied [{img_dir}{img_name}] to [{branding_dir}]")
        except Exception as e:
            self.log.warning(f"Failed to copy [{img_dir}{img_name}] to [{branding_dir}]: {e}")
            raise

    def testBrandingImage(self, oStr, iStr):
        """Main testing function. Used to generalize the same test to all branding images.
        Args:
            oStr - The string next option for the branding image we want to test
            iStr - The string corresponding to the image in the directory
        Returns: None
        """
        # Compare to default to prove they are different at the start
        diff = compareToTestImage(server_dir + iStr)
        self.log.info(f"Original Image Differnce value: {diff}")
        if diff == 0:
            tc_fail(f"Original {oStr} failed difference check")

        # Navigation and prep
        Navi.navigate_to("Express Lane Maintenance")
        mws.select_tab("Branding")

        # Swap to the test image
        mws.set_value(oStr, img_name)
        if mws.get_value(oStr)[0] != img_name:
            tc_fail(f"{oStr} value not set to {img_name}")
        self.log.info(f"{img_name} set for {oStr}")
        mws.click_toolbar("Save", main=True)

        # Recompare to make sure it changed
        diff = compareToTestImage(server_dir + iStr)
        self.log.info(f"Server Image Differnce value: {diff}")
        if diff != 0:
            tc_fail(f"Server image did not match {img_name}")
        
        # Recheck the option to make sure it saved properly
        Navi.navigate_to("Express Lane Maintenance")
        mws.select_tab("Branding")
        if mws.get_value(oStr)[0] != img_name:
            tc_fail(f"{oStr} value not set to {img_name} after save")
        self.log.info(f"{img_name} still set for {oStr} after save")

        # Hopefully the client has updated its image by this point
        # Compare to the clients image to make sure it still matches
        diff = compareToTestImage(client_dir + iStr)
        self.log.info(f"Client Image Differnce value: {diff}")
        if diff != 0:
            tc_fail(f"Client image did not match {img_name}")

    @test
    def testPreTransImage(self):
        """Test Pre-Transaction image branding option in Express Lane Maintenance
        Args: None
        Returns: None
        """
        self.testBrandingImage("Pre-Transaction","BrandingPreTrans.png")

    @test
    def testTransactionImage(self):
        """Test Transaction image branding option in Express Lane Maintenance
        Args: None
        Returns: None
        """
        self.testBrandingImage("Transaction","BrandingTrans.png")

    @test
    def testTenderImage(self):
        """Test Tender image branding option in Express Lane Maintenance
        Args: None
        Returns: None
        """
        self.testBrandingImage("Tender","BrandingTender.png")

    @test
    def testLogoImage(self):
        """Test Logo image branding option in Express Lane Maintenance
        Args: None
        Returns: None
        """
        self.testBrandingImage("Logo","BrandingLogo.png")

    @teardown
    def teardown(self):
        # Remoe the image we copied over
        try:
            os.remove(branding_dir + img_name)
            self.log.info(f"Image deleted from: [{branding_dir}{img_name}]")
        except:
            self.log.warning(f"Failed to delete image: [{branding_dir}{img_name}]")
        # Clean up resources
        try:
            test_img.close()
            self.log.info(f"Closed image resource [{img_dir}{img_name}]")
        except:
            self.log.warning(f"Failed to close image resource")
        mws.click_toolbar("Exit")