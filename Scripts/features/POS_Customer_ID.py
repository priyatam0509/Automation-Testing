"""
    File name: POS_Customer_ID.py
    Tags:
    Description: Script for testing the customer ID button/functionality in HTML POS
    Author: David Mayes
    Date created: 2020-04-08 14:29:26
    Date last modified: 2020-04-08
    Python Version: 3.7
"""

import logging, time
from app import Navi, mws, pos, system, pinpad
from app.framework.tc_helpers import setup, test, teardown, tc_fail
import xml.etree.ElementTree as ET
import glob, os, json

class POS_Customer_ID():
    """
    Class for testing the Customer ID button + functionality
    """

    def __init__(self):
        """
        Initializes the POS_Customer_ID
        """
        # The logging object. 
        # Example: self.log.info(f"Current value of var: {my_var}")
        self.log = logging.getLogger()
        self.wait_time = 2
        self.swipe_card_time = 5
        self.customer_id_button = pos.controls['function keys']['customer id']
        self.paid_in_button= pos.controls['function keys']['paid in']
        self.manual_button = pos.controls['keypad']['manual']
        self.initial_pjr_count = 0

    @setup
    def setup(self):
        # if not system.restore_snapshot():
        #     self.log.debug("No snapshot to restore, if this is not expected please contact automation team")
        pos.connect()
        pos.sign_on()

    @test
    def cancel_on_pos(self):
        """
        Cancel entering a customer ID on HTML POS
        and make sure it exits properly
        """
        # Start a transaction
        self.log.info("Starting a transaction...")
        pos.click('generic item')

        # Click customer id and then cancel
        self.log.info("Clicking the customer ID button...")
        if pos.is_element_present(self.customer_id_button, timeout = self.wait_time):
            pos.click('customer id')
        else:
            tc_fail("Customer ID button did not appear.")

        self.log.info("Clicking cancel...")
        if pos.is_element_present(self.manual_button, timeout = self.wait_time):
            pos.click('cancel')
        else:
            tc_fail("Did not change to the customer ID screen.")

        msg = pos.read_message_box(timeout = self.wait_time)
        if not msg:
            tc_fail("No popup appeared.")
        elif not "cancel" in msg.lower():
            tc_fail("Did not display the correct popup message after cancelling.")

        pos.click('ok')

        # Make sure we returned to the right screen after cancelling
        if pos.is_element_present(self.customer_id_button, timeout = self.wait_time):
            self.log.info("Successfully cancelled input of customer ID!")
        else:
            tc_fail("Did not return from customer ID screen.")


    @test
    def manual_entry(self):
        """
        Enter a customer ID manually on the HTML POS
        while in a transaction
        """
        # Bring up the customer ID screen
        self.log.info("Clicking the customer ID button...")
        if pos.is_element_present(self.customer_id_button, timeout = self.wait_time):
            pos.click('customer id')
        else:
            tc_fail("Customer ID button did not appear.")

        self.log.info("Entering the customer ID...")
        if pos.is_element_present(self.manual_button, timeout = self.wait_time):
            # TODO: Change this to the actual account number
            pos.enter_keypad('9999', after='enter')
        else:
            tc_fail("Did not change to the customer ID screen.")

        # Make sure we returned to the right screen
        if pos.is_element_present(self.customer_id_button, timeout = self.wait_time):
            self.log.info("Successfully entered customer ID manually on HTML POS!")
        else:
            tc_fail("Did not return from customer ID screen.")

        # Pay so that the customer ID will show up in a PJR to check
        pos.pay()

    # TODO: Uncomment this test case when pinpad sim is more reliable
    # @test
    # def swipe_card(self):
    #     """
    #     Simulate the swipe of a card on a pinpad
    #     to input the customer ID
    #     """
    #     # Start a transaction
    #     if pos.is_element_present(self.paid_in_button, timeout = self.wait_time):
    #         pos.click('generic item')
    #     else:
    #         tc_fail("Was not able to start a new transaction.")

    #     # Bring up the customer ID screen
    #     self.log.info("Clicking the customer ID button...")
    #     if pos.is_element_present(self.customer_id_button, timeout = self.wait_time):
    #         pos.click('customer id')
    #     else:
    #         tc_fail("Customer ID button did not appear.")

    #     # Simulate card swipe for customer ID
    #     if pos.is_element_present(self.manual_button, self.swipe_card_time):
    #         self.log.info("Swiping customer ID card...")
    #         pinpad.swipe_card(brand='Core', card_name='Loyalty')
    #     else:
    #         tc_fail("Unable to swipe customer ID card.")

    #     # Make sure we returned to the right screen
    #     if pos.is_element_present(self.customer_id_button, timeout = self.swipe_card_time):
    #         self.log.info("Successfully entered customer ID manually on HTML POS!")
    #     else:
    #         tc_fail("Did not return from customer ID screen.")

    #     # Pay so that the ID will show up in a PJR file to check
    #     pos.pay()


    @test
    def check_pjr(self):
        """
        Check that the pjr files properly record
        the two times that a customer ID was entered above
        (manually on the pos and on a "pinpad" with a card)
        """
        # Get the customer IDs from the PJR files
        if not self._pjr_file_generated(timeout = self.wait_time+5):
            tc_fail("PJR file did not generate.")
        self.log.info("Accessing PJR files...")
        pjr_files = glob.glob('C:\Passport\XMLGateway\BOOutbox\*')
        # TODO: uncomment when test case above is uncommented
        # swipe_pjr_file = max(pjr_files, key = os.path.getctime)
        # pjr_files.remove(swipe_pjr_file)
        manual_pjr_file = max(pjr_files, key = os.path.getctime)

        # swipe_customer_ID = self._get_customer_ID(swipe_pjr_file)
        manual_customer_ID = self._get_customer_ID(manual_pjr_file)

        if not manual_customer_ID == '9999':
            tc_fail("Manually-entered customer ID was not recorded correctly in the PJR file.")
        else:
            self.log.info("Manually-entered customer ID was correctly recorded in the PJR file...")
        
        # TODO: Uncomment when swipe_card gets uncommented
        # # Get the track data from the Loyalty card
        # # (in case it ever changes)
        # with open('app/data/CardData.json') as json_file:
        #     card_data = json.load(json_file)
        #     loyalty_ID = card_data['CORE']['Loyalty']['Track2']

        # # In case reading the file fails, just use this value (which likely won't change)
        # if loyalty_ID == None:
        #     loyalty_ID = '6008030000014791736=00000000000000000'

        # if not swipe_customer_ID == loyalty_ID:
        #     tc_fail("Customer ID entered by swiping a card was not recorded correctly in the PJR file.")
        # else:
        #     self.log.info("Customer ID entered by swiping a card was correctly recorded in the PJR file...")

        self.log.info("Successfully added the right customer IDs to the PJR files!")

        
    def _get_customer_ID(self, file):
        """
        Helper function for use in finding the customer ID
        in the PJR file
        """
        tree = ET.parse(file)
        root = tree.getroot()
        
        try:
            customer_ID = root.find('JournalReport').find('SaleEvent').find('TransactionDetailGroup').find('TransactionLine').find('CustomerID').find('PersonalID').text
        except:
            time.sleep(1)
            customer_ID = self._get_customer_ID(file)

        return customer_ID


    def _pjr_file_generated(self, timeout):
        """
        Helper function for determining when the PJR files
        have been created
        """
        # TODO: update this to work for 2 files once the stuff
        # above is uncommented when pinpad sim is more reliable
        start_time = time.time()
        while time.time() - start_time <= timeout:
            if len(glob.glob('C:\Passport\XMLGateway\BOOutbox\*')) > self.initial_pjr_count:
                return True
        else:
            return False


    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        pos.close()
