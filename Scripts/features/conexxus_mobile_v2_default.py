"""
    File name: conexxus_mobile_v2_default.py
    Brand : CHEVRON
    Description: conexxus mobile payment version 2.0, inside transacion
    Author: Pavan Kumar Kantheti
    Date created: 2020-6-11 14:23:24
    Date last modified:
    Python Version: 3.7
"""
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from Scripts.features import conexxus_pay_inside


class conexxus_mobile_v2_default():
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
        pass

    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        pass

    @test
    def set_site_version(self):
        """
        """
        # Set the site Schema version as "2.0"
        # at MWS ->Mobile Payment Configuration screen
        status = conexxus_pay_inside.load_conexxus("2.0")
        if not(status == ""):
            tc_fail(status)

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        pass
