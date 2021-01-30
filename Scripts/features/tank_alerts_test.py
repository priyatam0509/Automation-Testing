"""
    File name: tank_alert_test.py
    Tags:
    Description: 
    Author: 
    Date created: 2019-06-27 14:03:18
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import Navi, mws, system, tank_alerts
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class tank_alerts_test():
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
        self.ta = tank_alerts.TankAlerts()

    @test
    def configure_tank_alerts(self):
        """Verifies the fields in the Tank Alerts feature module can be set.
        Args: None
        Returns: None
        """
        if not self.ta.configure("1","500","2000"):
            tc_fail("Failed during configuration.")
            mws.recover()

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        # delete pass after you implement.
        pass