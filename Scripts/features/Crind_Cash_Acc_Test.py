"""
    File name: Crind_Cash_Acc_Test.py
    Tags:
    Description: Tests the crind_cash_options.CrindCashAcceptorOptions module
    Author: Alex Rudkov
    Date created: 2019-06-28 08:56:52
    Date last modified: 
    Python Version: 3.7
"""

import logging, time
from app import Navi, mws, pos, system, crind_cash_options
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class Crind_Cash_Acc_Test():
    """
    Test class that provides an interface for testing.
    """

    def __init__(self):
        """
        Initializes the Template class.
        """
        # The logging object. 
        # Example: self.log.info(f"Current value of var: {my_var}")
        self.log = logging.getLogger()

    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        """
        # if not system.restore_snapshot():
        #     raise Exception

    @test
    def test_case_1(self):
        """
        Configures the CRIND Cash Acceptor Options without accepted bills
        """
        ca = crind_cash_options.CrindCashAcceptorOptions()

        params = {
            "Max cash accepted per transaction": "900",
            "Max Bill Insertion Retries": "5",
            "Total $ amount in vault exceeds": "600",
            "Total number of bills in vault exceeds": "400",
            "Min $ amount reserved for fuel purchase": "2"
        }

        if not ca.setup(params):
            tc_fail("Failed to setup CRIND Cash Acceptor Options")

        # Check
        # Wait before goind back in
        time.sleep(2)
        ca.navigate_to()
        error = False
        for field, value in params.items():
            set_value = mws.get_value(field)
            if set_value.find(value) == -1:
                self.log.error(f"The field '{field}' was set successfully, but upon check had value '{set_value}' when '{value}' was expected")
                error = True
        if error:
            tc_fail("The test failed a check after configuration")
        mws.click_toolbar("Cancel")

        params = {
            "Max cash accepted per transaction": "500",
            "Max Bill Insertion Retries": "5",
            "Total $ amount in vault exceeds": "500",
            "Total number of bills in vault exceeds": "500",
            "Min $ amount reserved for fuel purchase": "1"
        }

        # Wait before goind back in
        time.sleep(2)
        ca.navigate_to()

        if not ca.setup(params):
            tc_fail("Failed to setup CRIND Cash Acceptor Options")

        # Check
        # Wait before goind back in
        time.sleep(2)
        ca.navigate_to()
        error = False
        for field, value in params.items():
            set_value = mws.get_value(field)
            if set_value.find(value) == -1:
                self.log.error(f"The field '{field}' was set successfully, but upon check had value '{set_value}' when '{value}' was expected")
                error = True
        if error:
            tc_fail("The test failed a check after configuration")

        mws.click_toolbar("Cancel")
    

    @test
    def test_case_2(self):
        """
        Configures the CRIND Cash Acceptor Options with accepted bills
        """
        # Check
        # Wait before goind back in
        time.sleep(2) 
        ca = crind_cash_options.CrindCashAcceptorOptions()

        params = {
            "Max cash accepted per transaction": "900",
            "Max Bill Insertion Retries": "5",
            "Total $ amount in vault exceeds": "600",
            "Total number of bills in vault exceeds": "400",
            "Min $ amount reserved for fuel purchase": "2",
            "Bills Accepted" : ["$1", "$2", "$5", "$10", "$20", "$50", "$100"]
        }

        if not ca.setup(params):
            tc_fail("Failed to setup CRIND Cash Acceptor Options")

        # Check
        # Wait before goind back in
        time.sleep(2)
        ca.navigate_to()
        error = False
        for field, value in params.items():
            if field == "Bills Accepted":
                continue
            set_value = mws.get_value(field)
            if set_value.find(value) == -1:
                self.log.error(f"The field '{field}' was set successfully, but upon check had value '{set_value}' when '{value}' was expected")
                error = True

        # Check accepted bills separately
        for bill in ca.BILLS:
            if bill in params['Bills Accepted']:
                if not mws.get_value(bill):
                    self.log.error(f"The checkbox '{bill}' was set successfully, but it is unchecked during verification of the results")
                    error = True
            else:
                # Check that it is disabled
                if mws.get_value(bill):
                    self.log.error(f"The checkbox '{bill}' is checked but it should be disabled")
                    error = True

        if error:
            tc_fail("The test failed a check after configuration")
        mws.click_toolbar("Cancel")

        params = {
            "Max cash accepted per transaction": "500",
            "Max Bill Insertion Retries": "5",
            "Total $ amount in vault exceeds": "500",
            "Total number of bills in vault exceeds": "500",
            "Min $ amount reserved for fuel purchase": "1",
            "Bills Accepted" : ["$1"]
        }

        # Wait before goind back in
        time.sleep(2)
        ca.navigate_to()

        if not ca.setup(params):
            tc_fail("Failed to setup CRIND Cash Acceptor Options")

        # Check
        # Wait before goind back in
        time.sleep(2)
        ca.navigate_to()
        error = False
        for field, value in params.items():
            if field == "Bills Accepted":
                continue
            set_value = mws.get_value(field)
            if set_value.find(value) == -1:
                self.log.error(f"The field '{field}' was set successfully, but upon check had value '{set_value}' when '{value}' was expected")
                error = True

        # Check accepted bills separately
        for bill in ca.BILLS:
            if bill in params['Bills Accepted']:
                if not mws.get_value(bill):
                    self.log.error(f"The checkbox '{bill}' was set successfully, but it is unchecked during verification of the results")
                    error = True
            else:
                # Check that it is disabled
                if mws.get_value(bill):
                    self.log.error(f"The checkbox '{bill}' is checked but it should be disabled")
                    error = True
        if error:
            tc_fail("The test failed a check after configuration")

        mws.click_toolbar("Cancel")

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        # delete pass after you implement.
        pass