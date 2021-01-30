"""
    File name: conexxus_mobile_v1_fuel_loyalty.py
    Brand : CHEVRON
    Description: Disable fuel reward and enable site level loyalty (Fuel Level rewards)
    Author: Pavan Kumar Kantheti
    Date created: 2020-6-11 14:23:24
    Date last modified:
    Python Version: 3.7
"""
from app.simulators import mobilepay_inside
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from Scripts.features import conexxus_pay_inside


class conexxus_mobile_v1_fuel_loyalty():
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
    def disable_fuel_discount_v1(self):
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
    def config_fuel_loyalty(self):
        """
        Configure the fuel level "Loyalty" Enabled at MWS loyalty interface screen
        Args: None
        Returns: None
        """
        status = conexxus_pay_inside.loyalty_setting(apply=True, version="1.0", trans_level=False)
        if (not status):
            tc_fail("Failed, unable to perform loyalty_setting at [config_loyalty].")

        status = mobilepay_inside.update_settings("1.0", "True")
        if (not status):
            tc_fail("Failed, unable to perform update_settings at [config_loyalty].")

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        pass
