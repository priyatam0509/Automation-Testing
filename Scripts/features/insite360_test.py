"""
    File name: insite360_test.py
    Tags:
    Description: 
    Author: 
    Date created: 2019-06-10 10:26:11
    Date last modified: 
    Python Version: 3.7
"""

import logging,time
from app import mws, pos, system, insite360
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class insite360_test():
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

        self.insite_info = {
            "General": {
                "Enable Insite360": True,
                "Export price book when third party changes are made to items or departments": True,
                "Gilbarco ID": "123456",
                "Apply only to this register group": True,
                "Apply to only this register group combo box": "POSGroup1"
            },
            "Summary Files": {
                "Fuel Grade Movement": [True, True],
                "Fuel Product Movement": [True, False],
                "Item Sales Movement": [True, True]
            }
        }
        

    @setup
    def setup(self):
        """Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        if not system.restore_snapshot():
            raise Exception

        self.is360 = insite360.Insite360Interface()

    @test
    def insite360_configure(self):
        """Tests whether the Insite 360 Interface can be configured correctly.
        Args: None
        Returns: None
        """
        self.is360.navigate_to()
        if not self.is360.configure(self.insite_info):
            tc_fail("Could not configure Insite 360 Interface correctly")

    @test
    def insite360_config_register(self):
        """Tests whether the Insite 360 Interface can be configured then registered correctly.
        Args: None
        Returns: None
        """
        self.is360.navigate_to()
        if not self.is360.configure(self.insite_info,register=True):
            tc_fail("Could not configure/register Insite 360 Interface correctly")

    @test
    def insite360_register(self):
        """Tests whether the Insite 360 Interface is registered correctly.
        Args: None
        Returns: None
        """
        self.is360.navigate_to()
        if not self.is360.register():
            tc_fail("Could not register Insite 360 Interface correctly")
    

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        # delete pass after you implement.
        pass