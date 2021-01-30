"""
    File name: conexxus_mobile_v2_disable.py
    Brand : CHEVRON
    Description: Disable all - fuel reward, site level loyalty and site level above reward
    Author: Pavan Kumar Kantheti
    Date created: 2020-6-11 14:23:24
    Date last modified:
    Python Version: 3.7
"""
from app.simulators import mobilepay_inside
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from Scripts.features import conexxus_pay_inside


class conexxus_mobile_v2_disable():
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
        Configure the "Default Fuel Discount" at "Mobile Payment Configuration" for conexxus mobile
        Args: None
        Returns: None
        """
        status = conexxus_pay_inside.change_default_discount(False)
        if (not status):
            tc_fail("Failed, unable to perform disable_fuel_discount")

    @test
    def disable_loyalty(self):
        """
        Configure the "Loyalty" Enabled at MWS loyalty interface screen
        Args: None
        Returns: None
        """
        status = conexxus_pay_inside.loyalty_setting(False)
        if (not status):
            tc_fail("Failed, unable to perform enable_site_reward.")

    @test
    def disable_siteabove_discount(self):
        """
        Disable the "Site Level Fuel Reward" for conexxus mobile.
        Args: None
        Returns: None
        """
        status = mobilepay_inside.update_rewards(disable_reward="true")
        if (not status):
            tc_fail("Failed, unable to perform disable_siteabove_discount.")

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        pass
