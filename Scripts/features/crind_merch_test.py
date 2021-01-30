"""
    File name: crind_merch_test.py
    Tags:
    Description: 
    Author: 
    Date created: 2019-06-24 14:27:37
    Date last modified: 
    Python Version: 3.7
"""

import logging, time
from app import mws, system, crind_merch
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class crind_merch_test():
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
        """Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        if not system.restore_snapshot():
            raise Exception
        
        self.cm = crind_merch.CRINDMerchandising()

    @test
    def configure_crindmerch(self):
        """Verifies the fields in the CRIND Merchandising feature module can be filled.
        Args: None
        Returns: None
        """
        crind_merch_info = {
            "General": {
                "CRIND Merchandising is Enabled": True,
                "Vendor Name": "Test Name",
                # "Prompt Location": "Before Fueling"
            },
            "Categories": ["TestCategory1", "TestCategory2"],
            "Items": {
                "TestCategory1": ["1","Item 7","004"],
                "TestCategory2": ["Item 7", "Item 12"]
            }
        }
        if not self.cm.configure(crind_merch_info):
            tc_fail("Failed during configuration...")
            mws.recover()
    
    @test
    def change_category(self):
        """Verifies that the name of a category can be changed.
        Args: None
        Returns: None
        """
        self.cm.navigate_to()
        if not self.cm.change_category("TestCategory1", "TestCategoryEdit"):
            tc_fail("Failed during category changing...")
            mws.recover()

    @test
    def delete_category(self):
        """Verifies a category can be deleted.
        Args: None
        Returns: None
        """
        self.cm.navigate_to()
        if not self.cm.delete_category("TestCategoryEdit"):
            tc_fail("Failed during category deletion...")
            mws.recover()
    
    @test
    def change_item(self):
        """Verifies the properties of an item can be changed.
        Args: None
        Returns: None
        """
        self.cm.navigate_to()
        if not self.cm.change_item("TestCategory2", "Item 7", "Item 7 Edit", False):
            tc_fail("Failed during item changing...")
            mws.recover()

    @test
    def delete_item(self):
        """Verifies an item can be deleted from the item list.
        Args: None
        Returns: None
        """
        self.cm.navigate_to()
        if not self.cm.delete_item("TestCategory2", "Item 7 Edit"):
            tc_fail("Failed during item deletion...")
            mws.recover()

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        # delete pass after you implement.
        pass