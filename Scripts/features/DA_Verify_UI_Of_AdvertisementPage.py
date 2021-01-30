"""
    File name: DA_Verify_UI_Of_AdvertisementPage.py
    Tags:
    Description: Verify UI validation of Advertisement page
    Story ID: SL-1471
    Author: Paresh
    Date created: 2019-15-11 13:31:37
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import Navi, mws
from app.features import feature_activation
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from pywinauto import application

class DA_Verify_UI_Of_AdvertisementPage():
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
        """SL-1471: Verify UI validation of Advertisement page.
        Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        FA = feature_activation.FeatureActivation()
        FA.activate(feature_activation.DEFAULT_EXPRESS)
        Navi.navigate_to("Express Lane Maintenance")
        mws.select_tab("Advertisement")
    
    @test
    def verify_elementIsVisibleonAdvertisement_page(self):
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
        if not mws.wait_for_button("Delete Media"):
            tc_fail("Delete Media button is not visible.")
        if not mws.click("Media Display Interval"):
            tc_fail("Media Display Interval textbox is not visible.")
        mws.click_toolbar("Download from USB")
        if not mws.wait_for_button("Cancel"):
            tc_fail("Cancel button is not visible.")
        if not mws.wait_for_button("Refresh"):
            tc_fail("Refresh button is not visible.")
        mws.click_toolbar("Cancel")
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
        pass