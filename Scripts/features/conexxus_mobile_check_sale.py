"""
    File name: conexxus_mobile_check_sale.py
    Brand : CHEVRON
    Description: conexxus mobile payment version inside transacion - Check one dry item sale
    Author: Pavan Kumar Kantheti
    Date created: 2020-6-11 14:23:24
    Date last modified:
    Python Version: 3.7
"""
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from Scripts.features import conexxus_pay_inside


class conexxus_mobile_check_sale():
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
    def pdl_status(self):
        """
        """
        proceed_card_trans = conexxus_pay_inside.process_pdl()
        if not(proceed_card_trans):
            tc_fail("Failed, PDL is not successful, unable to proceed card transactions.")

    @test
    def drysale_inside_payment_Check(self):
        """
        Performing the Dry sale transaction sale and pay inside mobile payment
        Args: None
        Returns: None
        """
        conexxus_pay_inside.pos_load()
        conexxus_pay_inside.get_settings_data()
        status = conexxus_pay_inside.drysale_inside_payment("ITEM 2")
        conexxus_pay_inside._pos_wait(on_load=True)
        if (not status):
            tc_fail("Failed, unable to perform drysale_inside_payment.")

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        pass
