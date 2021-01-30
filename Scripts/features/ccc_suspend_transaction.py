"""
    File name: ccc_suspend_transaction.py
    Tags:
    Description: This script tests the suspend transaction functionality in the Cashier Control Console (CCC).
    Author: Christopher Haynes
    Date created: 2019-12-16
    Date last modified: 
    Python Version: 3.7
"""

import logging, time
from app import Navi, pos, mws, system, checkout, console
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from Scripts.features import EL_PaymentTest

class ccc_suspend_transaction():
    """
    Testing the ability to suspend transactions from the CCC.
    """

    def __init__(self):
        """
        Initializes the test class.
        """
        
        self.log = logging.getLogger()
        self.item_plu = "002"

    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        """
        mws.sign_on()

        self.log.info("Removing any pre-existing suspended transactions.")
        if not Navi.navigate_to("POS"):
            self.log.error("Unable to navigate on POS")
        
        # Sign on to POS screen if not already sign-on
        if not pos.sign_on():
            self.log.error("Unable to perform sign on")
        
        sus_trans = pos.read_suspended_transactions()
        pos.click_suspended_transaction()
        while len(sus_trans) > 0:
                num = len(sus_trans)
                pos.click_suspended_transaction(sus_trans[0])
                pos.click_function_key("void trans")
                pos.enter_reason()
                pos.click_message_box_key("yes", verify=False)
                sus_trans = pos.read_suspended_transactions()
                if num == len(sus_trans):
                        tc_fail(f"Unable to void {sus_trans[0]}")
        pos.sign_off()

    @test
    def suspend_transactions_from_ccc_1(self):
        """
        Checks for the ability to suspend a transaction from the CCC.  This automates M-90719.
        """
        
        self.log.info("Suspending a transaction for the second test to use.")
        self.prep_checkout()
        checkout.enter_plu(self.item_plu)
        time.sleep(1)
        checkout.enter_plu(self.item_plu)
        self.suspend_transaction()
        
        self.log.info("Suspending a transaction for the third test to use.")
        self.prep_checkout()
        checkout.enter_plu(self.item_plu)
        self.suspend_transaction()
        checkout.close()

    @test
    def resume_transaction_and_modify_2(self):
        """
        Checks for the ability for the CWS to resume and modify a transaction suspended in the CCC.
                This automates M-90719.
        """
        
        self.log.info("Resuming transaction.")
        Navi.get_to_pos(sign_on=True)
        sus_trans = pos.read_suspended_transactions()
        if sus_trans != ["$10.00", "$5.00"]:
                tc_fail("The suspended transaction list \"{}\" is not correct.".format(sus_trans))
        pos.click_suspended_transaction("$10.00")
        trans = pos.read_transaction_journal()
        expected = [['** Begin Transaction **'], ['Item 2', '99', '$5.00'], ['Item 2', '99', '$5.00']]
        if trans != expected:
                pos.pay()
                tc_fail("The transaction journal \"{}\" isn't correct. Expected: {}".format(trans, expected))

        self.log.info("Modifying quantity of first item.")
        pos.click_journal_item(instance = 2)
        pos.click_function_key("quantity")
        pos.enter_keypad("3", after = "enter")
        trans = pos.read_transaction_journal()
        expected = [['** Begin Transaction **'], ['Item 2', '3 @ $5.00', ' 99', '$15.00'], ['Item 2', ' 99', '$5.00']]
        if trans != expected:
                pos.pay()
                tc_fail("The transaction journal \"{}\" isn't correct. Expected: {}".format(trans, expected))

        self.log.info("Modifying price of second item.")
        pos.click_journal_item(instance = 3)
        pos.click_function_key("override")
        pos.enter_reason()
        pos.enter_keypad("200", after = "enter")
        trans = pos.read_transaction_journal()
        expected = [['** Begin Transaction **'], ['Item 2', '3 @ $5.00', ' 99', '$15.00'], ['Item 2', ' 99', '$2.00']]
        if trans != expected:
                pos.pay()
                tc_fail("The transaction journal \"{}\" isn't correct.".format(trans, expected))
        
        self.log.info("Paying cash.")
        pos.pay()
        pos.sign_off()

    @test
    def cancel_help_screen_3(self):
        """
        Checks for the ability for the CWS to resume and void a transaction suspended in the CCC.
                This automates M-90719.
        """
        
        self.log.info("Resuming transaction.")
        Navi.get_to_pos(sign_on=True)
        sus_trans = pos.read_suspended_transactions()
        if sus_trans != ["$5.00"]:
                tc_fail("The suspended transaction list \"{}\" is not correct.".format(sus_trans))
        pos.click_suspended_transaction("$5.00")
        
        self.log.info("Voiding transaction.")
        pos.click_function_key("void trans")
        pos.enter_reason()
        pos.click_message_box_key("yes", verify=False)
        pos.sign_off()
        Navi.get_to_mws()

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """

        # Suspend Transaction if any test case is fail due to payment issue
        EL_PaymentTest.suspend_transaction()


# ##########################################################################################
# #################################### HELPER FUNCTIONS ####################################
# ##########################################################################################


    def prep_checkout(self):
        """
        Gets the Express Lane ready for use.
        """

        checkout.connect()
        # Waiting for express lane to come up
        system.wait_for(checkout._is_element_present, desired_result=False, timeout = 30, args = ["//div[@id='disabled_screen']"])

        # Ensure welcome screen is either dismissed or not present after connecting to checkout.
        # TODO: what exact message box key is being dismissed here?
        try:
            checkout.click_message_box_key("OK")
        except:
            pass

        if checkout._is_element_present("//div[@id = 'welcomescreen']"):
            checkout.click_welcome_key("Start")


    def suspend_transaction(self):
        """
        Suspends the current transaction from the CCC.
        """

        self.log.info("Suspending the transaction.")
        console.connect()
        if console._get_text("//*[@id='terminal_list']/div/div[4]/div/div[2]") != "In Transaction":
            console.click_function_key("In Transaction")
        console.click("Suspend Transaction")
        console.close()