"""
    File name: Concord_PDL_Test.py
    Tags: Concord, Valero, Sunoco, Exxon, Phillips66
    Description: Tests the functionality of the PDL Module
    Author: Conor McWain
    Date created: 2019-06-28 14:45:56
    Date last modified: 2019-07-19 10:36 (Alex Rudkov)
    Python Version: 3.7
"""

import logging
from app import Navi, mws, pos, system
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app import pdl

class Concord_PDL_Test():
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
    def perform_pdl(self):
        """Request a PDL - Pass
        Args: None
        Returns: None
        """
        pd = pdl.ParameterDownload()
        if not pd.request():
            tc_fail("Failed the PDL")

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        # delete pass after you implement.
        pass