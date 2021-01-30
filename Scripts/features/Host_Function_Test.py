"""
    File name: Comm_Test.py
    Tags: HPS-Dallas, Concord, Valero, Sunoco, Exxon, Phillips66
    Description: Tests the functionality of the Comms Test
    Author: Conor McWain
    Date created: 2019-06-28 14:45:56
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import Navi, mws, pos, system
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app import host_function

class Host_Function_Test():
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
    def comm_test(self):
        """Test the Communications Test Host Function
        Args: None
        Returns: None
        """
        hf = host_function.HostFunction()
        if not hf.communications_test(timeout=300):
            tc_fail("Failed the Communications Test")

    @test
    def mail_request(self):
        """Test the Mail Request Host Function
        Args: None
        Returns: None
        """
        hf = host_function.HostFunction()
        if not hf.mail_request(timeout=300):
            tc_fail("Failed the Mail Request Test")

    @test
    def mail_reset(self):
        """Test the Mail Reset Host Function
        Args: None
        Returns: None
        """
        hf = host_function.HostFunction()
        if not hf.mail_reset(timeout=300):
            tc_fail("Failed the Mail Reset Test")

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        # delete pass after you implement.
        pass