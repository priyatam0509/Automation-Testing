"""
    File name: conexxus_mobile_v2_site_loyalty.py
    Brand : CHEVRON
    Description: Disable fuel reward and enable site level loyalty
    Author: Pavan Kumar Kantheti
    Date created: 2020-6-11 14:23:24
    Date last modified:
    Python Version: 3.7
"""
from app.simulators import mobilepay_inside
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from Scripts.features import conexxus_pay_inside


class conexxus_mobile_v2_site_loyalty():
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
    def disable_fuel_discount(self):
        """
        Configure the "Default Fuel Discount" at "Mobile Payment Configuration"
        for conexxus mobile
        Args: None
        Returns: None
        """
        status = conexxus_pay_inside.change_default_discount(False)
        if (not status):
            tc_fail("Failed, unable to perform disable_fuel_discount")

    @test
    def config_loyalty(self):
        """
        Configure the "Loyalty" Enabled at MWS loyalty interface screen
        Args: None
        Returns: None
        """
        status = conexxus_pay_inside.loyalty_setting()
        if (not status):
            tc_fail("Failed, unable to perform loyalty_setting at [config_loyalty].")

        status = mobilepay_inside.update_settings("2.0", "True")
        if (not status):
            tc_fail("Failed, unable to perform update_settings at [config_loyalty].")

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        pass
