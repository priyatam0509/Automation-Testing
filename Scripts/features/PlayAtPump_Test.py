"""
    File name: PlayAtPump_Test.py
    Tags:
    Description: 
    Author: 
    Date created: 
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import Navi, mws, pos, system, store, pricing
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app.features import play_at_pump

class PlayAtPump_Test():
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
        # delete pass after you implement.
        pass

    @test
    def configure(self):
        """Configure Play at the Pump
        Args: None
        Returns: None
        """
        config = {
            'Enabled': 'Yes',
            'Site ID': '999',
            'Host IP Address': '10.5.48.6',
            'Host IP Port': '7900'
            }
        patp = play_at_pump.PlayAtPump()
        if not patp.configure(config):
            mws.recover()
            tc_fail("Failed to configure Play at the Pump")

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        # if not system.restore_snapshot():
        #     raise Exception
        pass