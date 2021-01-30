"""
    File name: conexxus_mobile_payment_sales.py
    Brand : CHEVRON
    Description: conexxus mobile payment version inside transacion
    Author: Pavan Kumar Kantheti
    Date created: 2020-6-11 14:23:24
    Date last modified:
    Python Version: 3.7
"""
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from Scripts.features import conexxus_pay_inside


class conexxus_mobile_payment_sales():
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
        self.disp = 1
        self.grade = "UNL SUP CAN"

    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        pass

    @test
    def prepay_inside_payment_TC1(self):
        """
        Login at POS and Performing THE pre-pay fuel sale and pay inside mobile payment
        Args: None
        Returns: None
        """
        conexxus_pay_inside.pos_load()
        conexxus_pay_inside.get_settings_data()
        status = conexxus_pay_inside.prepay_inside_payment(self.disp, self.grade, "5")
        if (not status):
            tc_fail("Failed, unable to perform prepay_inside_payment.")

    @test
    def drysale_inside_payment_TC2(self):
        """
        Performing the Dry sale transaction sale and pay inside mobile payment
        Args: None
        Returns: None
        """
        status = conexxus_pay_inside.drysale_inside_payment("ITEM 2")
        if (not status):
            tc_fail("Failed, unable to perform drysale_inside_payment.")

    @test
    def presetsale_inside_payment_TC3(self):
        """
        Performing the Preset fuel transaction sale and pay inside mobile payment
        Args: None
        Returns: None
        """
        # Add Preset fuel sale
        status = conexxus_pay_inside.presetsale_inside_payment(self.disp, "A", self.grade, "10")
        if (not status):
            tc_fail("Failed, unable to perform presetsale_inside_payment.")

    @test
    def carwash_inside_payment_TC4(self):
        """
        Performing the cawash sale transaction sale and pay inside mobile payment
        Args: None
        Returns: None
        """
        status = conexxus_pay_inside.carwash_inside_payment()
        if (not status):
            tc_fail("Failed, unable to perform carwash_inside_payment.")

    @test
    def postpay_inside_payment_TC5(self):
        """
        Performing the POST-pay transaction sale and pay inside mobile payment
        Args: None
        Returns: None
        """
        # Add post pay sale
        status = conexxus_pay_inside.postpay_inside_payment(self.disp, "A", "20")
        if (not status):
            tc_fail("Failed, unable to perform postpay_inside_payment.")

    @test
    def prepayPlus_inside_payment_TC6(self):
        """
        Login at POS and Performing THE pre-pay fuel + Carwash + Dry item sale and pay inside mobile payment
        Args: None
        Returns: None
        """
        status = conexxus_pay_inside.prepay_plus_inside_payment(self.disp, self.grade, "10", "ITEM 3", "")
        if (not status):
            tc_fail("Failed, unable to perform prepayPlus_inside_payment.")

    @test
    def manualFuel_inside_payment_TC7(self):
        """
        Performing the Manual fuel transaction sale and pay inside mobile payment
        Args: None
        Returns: None
        """
        status = conexxus_pay_inside.manualfuel_inside_payment(self.disp, self.grade, "5")
        if (not status):
            tc_fail("Failed, unable to perform manualFuel_inside_payment.")

    @test
    def postpayPlus_inside_payment_TC8(self):
        """
        Login at POS and Performing post-pay fuel + Carwash + Dry item sale and pay inside mobile payment
        Args: None
        Returns: None
        """
        status = conexxus_pay_inside.postpay_plus_inside_payment(self.disp, "A", "20", "ITEM 2", "")
        if (not status):
            tc_fail("Failed, unable to perform postpayPlus_inside_payment.")

    @test
    def manualFuelPlus_inside_payment_TC9(self):
        """
        Performing the Manual fuel + food stamp item sale and pay inside mobile payment
        Args: None
        Returns: None
        """
        status = conexxus_pay_inside.manualfuel_plus_inside_payment(self.disp, self.grade, "10", "ITEM 7", 1, "")
        if (not status):
            tc_fail("Failed, unable to perform manualFuelPlus_inside_payment.")

    @test
    def presetsalePlus_inside_payment_TC10(self):
        """
        Performing the Preset fuel transaction + Drystock + Carwash sale and pay inside mobile payment
        Args: None
        Returns: None
        """
        # Add Preset fuel sale
        status = conexxus_pay_inside.presetsale_plus_inside_payment(self.disp, "A", self.grade, "20", "ITEM 3", "")
        if (not status):
            tc_fail("Failed, unable to perform presetsalePlus_inside_payment.")

    @test
    def manualFuelPlus_inside_payment_TC11(self):
        """
        Performing the Manual fuel + fractional quantity item sale and pay inside mobile payment
        Args: None
        Returns: None
        """
        # Add Preset fuel sale
        status = conexxus_pay_inside.manualfuel_plus_inside_payment(self.disp, self.grade, "5", "ITEM 11", 9, "")
        if (not status):
            tc_fail("Failed, unable to perform manualFuelPlus_inside_payment.")

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        pass
