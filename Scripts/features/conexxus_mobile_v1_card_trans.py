"""
    File name: conexxus_mobile_v1_card_trans.py
    Brand : CHEVRON
    Description: conexxus mobile payment version inside transacion
    Author: Pavan Kumar Kantheti
    Date created: 2020-6-11 14:23:24
    Date last modified:
    Python Version: 3.7
"""
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from Scripts.features import conexxus_pay_inside


class conexxus_mobile_v1_card_trans():
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
    def disable_v1_loyalty(self):
        """
        Configure the "Loyalty" Enabled at MWS loyalty interface screen
        Args: None
        Returns: None
        """
        status = conexxus_pay_inside.loyalty_setting(False)
        if (not status):
            tc_fail("Failed, unable to perform enable_site_reward.")

    @test
    def prepayPlus_VISA_payment_TC1(self):
        """
        Login at POS and Performing THE pre-pay fuel + Carwash + Dry item sale and pay by VISA card
        Args: None
        Returns: None
        """
        self.proceed_card_trans = conexxus_pay_inside.process_pdl()
        if (self.proceed_card_trans):
            conexxus_pay_inside.pos_load()
            conexxus_pay_inside.get_settings_data()
            status = conexxus_pay_inside.prepay_plus_inside_payment(self.disp, self.grade, "10", "ITEM 3", "Visa")
            if (not status):
                tc_fail("Failed, unable to perform prepayPlus_inside_payment.")
        else:
            tc_fail("Failed, PDL is not successful, unable to proceed card transactions.")

    @test
    def manualFuelPlus_VISA_payment_TC2(self):
        """
        Performing the Manual fuel + fractional quantity item sale and pay by VISA card
        Args: None
        Returns: None
        """
        # Add Manual fuel sale
        if (self.proceed_card_trans):
            status = conexxus_pay_inside.manualfuel_plus_inside_payment(self.disp, self.grade, "5", "ITEM 11", 9, "Visa")
            if (not status):
                tc_fail("Failed, unable to perform manualFuelPlus_inside_payment.")
        else:
            tc_fail("Failed, PDL is not successful, unable to proceed card transactions.")

    @test
    def postpayPlus_VISA_payment_TC3(self):
        """
        Login at POS and Performing post-pay fuel + Carwash + Dry item sale and pay by VISA card
        Args: None
        Returns: None
        """
        if (self.proceed_card_trans):
            status = conexxus_pay_inside.postpay_plus_inside_payment(self.disp, "A", "20", "ITEM 2", "Visa")
            if (not status):
                tc_fail("Failed, unable to perform postpayPlus_inside_payment.")
        else:
            tc_fail("Failed, PDL is not successful, unable to proceed card transactions.")

    @test
    def manualFuelPlus_VISA_payment_TC4(self):
        """
        Performing the Manual fuel + food stamp item sale and pay by VISA card
        Args: None
        Returns: None
        """
        if (self.proceed_card_trans):
            status = conexxus_pay_inside.manualfuel_plus_inside_payment(self.disp, self.grade, "10", "ITEM 7", 1, "Visa")
            if (not status):
                tc_fail("Failed, unable to perform manualFuelPlus_inside_payment.")
        else:
            tc_fail("Failed, PDL is not successful, unable to proceed card transactions.")

    @test
    def presetsalePlus_VISA_payment_TC5(self):
        """
        Performing the Preset fuel transaction + Drystock + Carwash sale and pay by VISA card
        Args: None
        Returns: None
        """
        # Add Preset fuel sale
        if (self.proceed_card_trans):
            status = conexxus_pay_inside.presetsale_plus_inside_payment(self.disp, "A", self.grade, "20", "ITEM 3", "Visa")
            if (not status):
                tc_fail("Failed, unable to perform presetsalePlus_inside_payment.")
        else:
            tc_fail("Failed, PDL is not successful, unable to proceed card transactions.")

    @test
    def prepayPlus_MasterCard_payment_TC1(self):
        """
        Login at POS and Performing THE pre-pay fuel + Carwash + Dry item sale and pay by MasterCard card
        Args: None
        Returns: None
        """
        if (self.proceed_card_trans):
            status = conexxus_pay_inside.prepay_plus_inside_payment(self.disp, self.grade, "10", "ITEM 3", "MasterCard")
            if (not status):
                tc_fail("Failed, unable to perform prepayPlus_inside_payment.")
        else:
            tc_fail("Failed, PDL is not successful, unable to proceed card transactions.")

    @test
    def manualFuelPlus_MasterCard_payment_TC2(self):
        """
        Performing the Manual fuel + fractional quantity item sale and pay by MasterCard card
        Args: None
        Returns: None
        """
        # Add Manual fuel sale
        if (self.proceed_card_trans):
            status = conexxus_pay_inside.manualfuel_plus_inside_payment(self.disp, self.grade, "5", "ITEM 11", 9, "MasterCard")
            if (not status):
                tc_fail("Failed, unable to perform manualFuelPlus_inside_payment.")
        else:
            tc_fail("Failed, PDL is not successful, unable to proceed card transactions.")

    @test
    def postpayPlus_MasterCard_payment_TC3(self):
        """
        Login at POS and Performing post-pay fuel + Carwash + Dry item sale and pay by MasterCard card
        Args: None
        Returns: None
        """
        if (self.proceed_card_trans):
            status = conexxus_pay_inside.postpay_plus_inside_payment(self.disp, "A", "20", "ITEM 2", "MasterCard")
            if (not status):
                tc_fail("Failed, unable to perform postpayPlus_inside_payment.")
        else:
            tc_fail("Failed, PDL is not successful, unable to proceed card transactions.")

    @test
    def manualFuelPlus_MasterCard_payment_TC4(self):
        """
        Performing the Manual fuel + food stamp item sale and pay by MasterCard card
        Args: None
        Returns: None
        """
        if (self.proceed_card_trans):
            status = conexxus_pay_inside.manualfuel_plus_inside_payment(self.disp, self.grade, "10", "ITEM 7", 1, "MasterCard")
            if (not status):
                tc_fail("Failed, unable to perform manualFuelPlus_inside_payment.")
        else:
            tc_fail("Failed, PDL is not successful, unable to proceed card transactions.")

    @test
    def presetsalePlus_MasterCard_payment_TC5(self):
        """
        Performing the Preset fuel transaction + Drystock + Carwash sale and pay by MasterCard card
        Args: None
        Returns: None
        """
        # Add Preset fuel sale
        if (self.proceed_card_trans):
            status = conexxus_pay_inside.presetsale_plus_inside_payment(self.disp, "A", self.grade, "20", "ITEM 3", "MasterCard")
            if (not status):
                tc_fail("Failed, unable to perform presetsalePlus_inside_payment.")
        else:
            tc_fail("Failed, PDL is not successful, unable to proceed card transactions.")

    @test
    def prepayPlus_AmEx_payment_TC1(self):
        """
        Login at POS and Performing THE pre-pay fuel + Carwash + Dry item sale and pay by AmEx card
        Args: None
        Returns: None
        """
        if (self.proceed_card_trans):
            status = conexxus_pay_inside.prepay_plus_inside_payment(self.disp, self.grade, "10", "ITEM 3", "AmEx")
            if (not status):
                tc_fail("Failed, unable to perform prepayPlus_inside_payment.")
        else:
            tc_fail("Failed, PDL is not successful, unable to proceed card transactions.")

    @test
    def manualFuelPlus_AmEx_payment_TC2(self):
        """
        Performing the Manual fuel + fractional quantity item sale and pay by AmEx card
        Args: None
        Returns: None
        """
        # Add Manual fuel sale
        if (self.proceed_card_trans):
            status = conexxus_pay_inside.manualfuel_plus_inside_payment(self.disp, self.grade, "5", "ITEM 11", 9, "AmEx")
            if (not status):
                tc_fail("Failed, unable to perform manualFuelPlus_inside_payment.")
        else:
            tc_fail("Failed, PDL is not successful, unable to proceed card transactions.")

    @test
    def postpayPlus_AmEx_payment_TC3(self):
        """
        Login at POS and Performing post-pay fuel + Carwash + Dry item sale and pay by AmEx card
        Args: None
        Returns: None
        """
        if (self.proceed_card_trans):
            status = conexxus_pay_inside.postpay_plus_inside_payment(self.disp, "A", "20", "ITEM 2", "AmEx")
            if (not status):
                tc_fail("Failed, unable to perform postpayPlus_inside_payment.")
        else:
            tc_fail("Failed, PDL is not successful, unable to proceed card transactions.")

    @test
    def manualFuelPlus_AmEx_payment_TC4(self):
        """
        Performing the Manual fuel + food stamp item sale and pay by AmEx card
        Args: None
        Returns: None
        """
        if (self.proceed_card_trans):
            status = conexxus_pay_inside.manualfuel_plus_inside_payment(self.disp, self.grade, "10", "ITEM 7", 1, "AmEx")
            if (not status):
                tc_fail("Failed, unable to perform manualFuelPlus_inside_payment.")
        else:
            tc_fail("Failed, PDL is not successful, unable to proceed card transactions.")

    @test
    def presetsalePlus_AmEx_payment_TC5(self):
        """
        Performing the Preset fuel transaction + Drystock + Carwash sale and pay by AmEx card
        Args: None
        Returns: None
        """
        # Add Preset fuel sale
        if (self.proceed_card_trans):
            status = conexxus_pay_inside.presetsale_plus_inside_payment(self.disp, "A", self.grade, "20", "ITEM 3", "AmEx")
            if (not status):
                tc_fail("Failed, unable to perform presetsalePlus_inside_payment.")
        else:
            tc_fail("Failed, PDL is not successful, unable to proceed card transactions.")

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        pass
