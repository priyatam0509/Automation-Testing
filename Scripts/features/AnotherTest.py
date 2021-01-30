"""
    File name: AnotherTest.py
    Tags:
    Description: 
    Author: 
    Date created: 2019-02-14 13:11:00
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import mws, pos
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class AnotherTest():
    """
    Description: Test class that provides and interface for testing.
    """

    def __init__(self):
        """Initializes the Template class.
        Args: None
        Returns: None
        """
        # The logging object. 
        # Example: self.log.info(f"Current value of var: {my_var}")
        self.log = logging.getLogger()

        # The main MWS object 
        self.mws = mws
        
        # The main POS object
        self.pos = pos

    @setup
    def setup(self):
        """Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        # delete pass after you implement.
        pass

    @test
    def test_case_1(self):
        """Says hi!
        Args: None
        Returns: None
        """
        # delete pass after you implement.
        self.log.info("Hi from tc1 in AnotherTest.py!")
    
    @test
    def test_case_2(self):
        """Fails another testcase
        Args: None
        Returns: None
        """
        tc_fail("This is failing another testcase. Boooo-urns.")

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        # delete pass after you implement.
        pass