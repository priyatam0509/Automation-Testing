"""
    File name: Repoll_XML_Files_Test.py
    Tags:
    Description: Tests back_office.XMLRepollFiles module
    Author: Alex Rudkov
    Date created: 2019-07-09 09:15:45
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import Navi, mws, pos, system, xml_repoll
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class Repoll_XML_Files_Test():
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
        """Tests the repoll with valid config
        Args: None
        Returns: None
        """
        
        xr = xml_repoll.XMLRepollFiles()

        # The backoffice should have the follwing files
        # enabled for repolling for it to work
        files = ['Fuel Grade Movement', 'Merchandise Code Movement']

        # There should be periods of time available for this to work
        if not xr.repoll('05/06/2019', ('11:50 AM', '11:59 PM'), files, 'shift close'):
            tc_fail('Failed to repoll the files')

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        # delete pass after you implement.
        pass