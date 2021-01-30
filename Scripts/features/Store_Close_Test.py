"""
    File name: Store_Close_Test.py
    Tags:
    Description: Tests the Store Close report
    Author: 
    Date created: 2019-06-10 14:15:56
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import Navi, mws, pos, system, store_close
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class Store_Close_Test():
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

    @test
    def test_case_1(self):
        """<Description here>
        Args: None
        Returns: None
        """
        store_close.StoreClose.navigate_to()
        sc = store_close.StoreClose()
        if not sc.begin_store_close():
            tc_fail("Could not generate report")

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        # delete pass after you implement.
        pass