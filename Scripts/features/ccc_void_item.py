"""
    File name: ccc_void_item.py
    Tags:
    Description: This script tests the ability to void individual itmes in the Cashier Control Console (CCC).
    Author: Christopher Haynes and Gene Todd
    Date created: 2019-12-20
    Date last modified: 
    Python Version: 3.7
"""

import logging, time, math
from app import system, checkout, console
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from Scripts.features import EL_PaymentTest

class ccc_void_item():
    """
    Description: Testing authentication in the CCC.
    """

    def __init__(self):
        """
        Description:
                Initializes the test class.
        Args:
                None
        Returns:
                None
        """
        # The logging object.
        # Example: self.log.info(f"Current value of var: {my_var}")
        self.log = logging.getLogger()
        self.connection_timeout = 30 #time to wait for connection to 
        self.button_sleep_time = 0.5

    @setup
    def setup(self):
        """
        Description:
                Performs any initialization that is not default.
        Args:
                None
        Returns:
                None
        """
        pass

    @test
    def void_single_item_1(self):
        """
        Description:
                Checks for the correct behavior when voiding an item from a transaction with a single item.
                This automates M-90716.
        Args:
                None
        Returns:
                None
        """

        self.start_transaction()
        console.connect()
       
        if console._get_text("//*[@id='terminal_list']/div/div[4]/div/div[2]") != "In Transaction":
            console.click_function_key("In Transaction")
        self.log.info("Voiding the item.")
        console.click("Void Item")
        time.sleep(self.button_sleep_time) #gives it time to finish working
        if not len(console.read_journal(terminal="1")) == 0:
            tc_fail("The item was not correctly voided.")

        console.close()

    @test
    def void_multiple_items_2(self):
        """
        Description:
                Checks for the correct behavior when voiding items from a transaction with multiple items.
                This automates M-90716.
        Args:
                None
        Returns:
                None
        """

        self.start_transaction(items_to_add=["002", "003", "004", "005", "006"])
        console.connect()
        items = console.read_journal(terminal="1")
        self.log.info("Voiding the first item.")
        console.click_journal_item(items[0][0])
        console.click("Void Item")
        time.sleep(self.button_sleep_time) #gives it time to finish working
        if not len(console.read_journal(terminal="1")) == len(items)-1:
            tc_fail("The item was not correctly voided.")
        
        items = console.read_journal(terminal="1")
        self.log.info("Voiding the last item.")
        console.click_journal_item(items[len(items)-1][0])
        console.click("Void Item")
        time.sleep(self.button_sleep_time) #gives it time to finish working
        if not len(console.read_journal(terminal="1")) == len(items)-1:
            tc_fail("The item was not correctly voided.")
        
        items = console.read_journal(terminal="1")

        self.log.info("Voiding the middle item.")
        console.click_journal_item(items[math.floor((len(items))/2)][0])
        console.click("Void Item")
        time.sleep(self.button_sleep_time) #gives it time to finish working
        if not len(console.read_journal(terminal="1")) == len(items)-1:
            tc_fail("The item was not correctly voided.")

        console.close()
        
        self.log.info("Paying out remaining transaction")
        self.prep_checkout()
        checkout.pay_card()
        checkout.close()

    @teardown
    def teardown(self):
        """
        Description:
                Performs cleanup after this script ends.
        Args:
                None
        Returns:
                None
        """
        # Suspend Transaction if any test case is fail due to payment issue
        EL_PaymentTest.suspend_transaction()


# ##########################################################################################
# #################################### HELPER FUNCTIONS ####################################
# ##########################################################################################


    def prep_checkout(self):
        """
        Description:
            Gets the Express Lane ready for use.
        Args:
            None
        Returns:
            None
        """
        checkout.connect()
        #waiting for express lane to come up
        system.wait_for(checkout._is_element_present, desired_result=False, timeout = self.connection_timeout, args = ["//div[@id='disabled_screen']"])

        try:
            checkout.click_message_box_key("OK")
        except:
            pass #I only want the message box out of the way.  If it doesn't exist to click, this isn't a problem.

        #ensuring the welcome screen is not in the way
        if checkout._is_element_present("//div[@id = 'welcomescreen']"):
            checkout.click_welcome_key("Start")


    def start_transaction(self, items_to_add = ["002"]):
        """
        Description:
            Adds items to the transaction.
        Args:
            items_to_add: a list of the item PLUs to add to the transaction.
        Returns:
            None
        """
        self.prep_checkout()
        count = 0
        for i in items_to_add:
            time.sleep(1.5)
            self.log.info("Adding PLU {} to a transaction.".format(i))
            checkout.enter_plu(i)
            # ensure each item added successfully
            count+=1
            if not (len(checkout.read_transaction_journal()) == count):
                tc_fail("Failed to add item to list")
        checkout.close()