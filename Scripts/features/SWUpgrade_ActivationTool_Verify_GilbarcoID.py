"""
    File name: SWUpgrade_ActivationTool_Verify_GilbarcoID.py
    Tags:
    Description: SL-1744: Auto populate GVR ID in upgrade blocker screen
    Brand: Concord
    Author: Paresh
    Date created: 2020-03-04 19:11:00
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import Navi, mws
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from Scripts.features import SWUpgrade_ActivationTool_Verify_UI


class SWUpgrade_ActivationTool_Verify_GilbarcoID():
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
        """
        Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        pass
        
    @test
    def verify_gilbarcoID_is_Editable(self):
        """
        Testlink Id: SL-1744: Auto populate GVR ID in upgrade blocker screen
		Description: Verify gilbarco ID is Editable if gilbarco id value is not present in DB
        Args: None
        Returns: None
        """

        # Update null date value in DB
        if not SWUpgrade_ActivationTool_Verify_UI.connect_mws_db():
            tc_fail("Unable to connect with DB and failed to update the data")

        # Update null gilbarco id in DB
        if not SWUpgrade_ActivationTool_Verify_UI.connect_mws_db(data_value='', id='10352'):
            tc_fail("Unable to connect with DB and failed to update the data")
        
        # Verify Gilbarco ID is visilbe and we can edit the data in Gilbarco ID field
        Navi.navigate_to("Software Upgrade Manager")

        if not mws.click_toolbar("Install Software"):
            tc_fail("Install software button is not visible")
        
        gilbarco_id = mws.get_value("GVR ID")
        if gilbarco_id != "":
            tc_fail("Gibarco id value is not empty")
        
        if not mws.set_value("GVR ID", "123456"):
            tc_fail("Unable to set gilbarco id")

        mws.click_toolbar("Exit")

        return True
    
    @test
    def verify_gilbarcoID_is_not_Editable(self):
        """
        Testlink Id: SL-1744: Auto populate GVR ID in upgrade blocker screen
		Description: Verify gilbarco ID is not editable if gilbarco id value present in DB
        Args: None
        Returns: None
        """

        # Update gilbarco id in DB
        if not SWUpgrade_ActivationTool_Verify_UI.connect_mws_db(data_value='123456', id='10352'):
            tc_fail("Unable to connect with DB and failed to update the data")
        
        # Verify Gilbarco ID is visilbe and value is same as DB value, and we can not edit the data in Gilbarco ID field
        Navi.navigate_to("Software Upgrade Manager")

        if not mws.click_toolbar("Install Software"):
            tc_fail("Install software button is not visible")
        
        gilbarco_id = mws.get_value("GVR ID")
        
        if gilbarco_id != "123456":
            tc_fail("Gibarco id value is not same as DB")
        
        if mws.set_value("GVR ID", "012345"):
            tc_fail("Gilbarco id field is editable")
            
        mws.click_toolbar("Exit")
            
        return True

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        # Update null gilbarco id in DB
        if not SWUpgrade_ActivationTool_Verify_UI.connect_mws_db(data_value='', id='10352'):
            self.log.error("Unable to connect with DB and failed to update the data")