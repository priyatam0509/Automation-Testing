"""
    File name: reasoncode_test.py
    Tags:
    Description: 
    Author: 
    Date created: 2019-06-10 09:43:06
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import mws, system, reason_code
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class reasoncode_test():
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
        # if not system.restore_snapshot():
        #     raise Exception

        self.rc = reason_code.ReasonCodeMaintenance()

        self.rc.navigate_to()

    @test
    def add_reasoncode(self):
        """Tests whether a reason code can be added
        Args: None
        Returns: None
        """
        if not self.rc.add(["Test code 1","Test code 2"]):
            tc_fail("Could not successfully add both reason codes")

    @test
    def change_reasoncode(self):
        """Tests whether a reason code can be changed
        Args: None
        Returns: None
        """
        if not self.rc.change("Test code 1","Test code 1 (EDITED)"):
            tc_fail("Could not successfully change specified reason code")
    @test
    def delete_reasoncode(self):
        """Tests whether a reason code can be deleted
        Args: None
        Returns: None
        """
        if not self.rc.delete(["Test code 2","Test code 1 (EDITED)"]):
            tc_fail("Could not successfully delete reason code")

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        # delete pass after you implement.
        pass