"""
    File name: GenericLogTest.py
    Tags: Core, Logging 
    Description: Test basic logging functionality.
    Author: John Smith
    Date created: 01/24/2019
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import mws, pos, system
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class LogTest():
    """
    Test class that that provides an interface for testing.
    """
    def __init__(self):
        """Initializes the Template class.
        Params: None
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
        pass

    @test
    def test_case_1(self):
        """Log something to the info log.
        Args: None
        Returns: None
        """
        self.log.info("Hi from tc1 in GenericItemSale.py!")

    @test
    def test_case_2(self):
        """Simulates a failed test case.
        Args: None
        Returns: None
        """
        tc_fail("This is a simulated failure reason")

    @test
    def test_case_3(self):
        """Simulates a handled exception.
        Args: None
        Returns: None
        """
        try:
            if a:
                pass
        except:
            self.log.critical("Handled Exception")
            tc_fail("Failed because of Handled Exception")
        
    # @test
    def test_case_4(self):
        """Simulates an unhandled exception.
        Args: None
        Returns: None
        """
        if b:
            pass
        else:
            tc_fail("b was False")
            
    # @test
    def test_case_5(self):
        """Restore a missing snapshot.
        Args: None
        Returns: None
        """
        if not system.restore_snapshot("Incorrect Snapshot"):
            tc_fail("Failed to restore snapshot")
        
    @test
    def test_case_6(self):
        """Take a screenshot.
        Args: None
        Returns: None
        """
        system.takescreenshot()

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends. 
        Args: None
        Returns: None
        """
        pass
        # if not system.restore_snapshot():
        #     raise Exception
