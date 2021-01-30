"""
    File name: conexxus_mobile_fuel_disc.py
    Brand : CHEVRON
    Description: Add fuel discount for conexxus mobile Payment
    Author: Pavan Kumar Kantheti
    Date created: 2020-6-11 14:23:24
    Date last modified:
    Python Version: 3.7
"""
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from Scripts.features import conexxus_pay_inside


class conexxus_mobile_fuel_disc():
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
    def enable_fuel_discount(self):
        """
        Configure the "Default Fuel Discount" at "Mobile Payment Configuration" for conexxus mobile
        Args: None
        Returns: None
        """
        conexxus_pay_inside.add_fuel_discount()
        status = conexxus_pay_inside.change_default_discount()

        if (not status):
            tc_fail("Failed, unable to perform enable_fuel_discount")

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        pass
