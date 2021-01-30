"""
    File name: StressTest_POS.py
    Tags:
    Description: 
    Author: 
    Date created: 2020-02-26 14:00:16
    Date last modified: 
    Python Version: 3.7
"""

import logging, time
from app import Navi, mws, pos, system
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class StressTest_POS():
    """
    Description: Test class that provides an interface for testing.
    """

    def __init__(self):
        self.log = logging.getLogger()
        # keep track of how often we succeed or fail
        self.success_count = 0
        self.failure_count = 0
        self.consec_fails = 0
        self.top_consec_fails = 0

    @setup
    def setup(self):
        #if not system.restore_snapshot():
        #    self.log.debug("No snapshot to restore, if this is not expected please contact automation team")
        pos.connect()

    @test
    def rapidTransactions(self):
        """
        <Description here>
        """
        # attempt a LOT of sales
        for i in range(1, 5001):
            if (self.top_consec_fails >= 5):
                self.displayResults()
                tc_fail("Too many consequetive failures for a transaction")
            # default message incase something weird happens
            temp = "attempt_sale() failed to return"
            try:
                temp = self.attempt_sale(i)
            except KeyboardInterrupt:
                self.log.info("\n\n!!! Keyboard Interupt detected !!!\n\n")
                break
            except Exception as e:
                self.log.info(f"EXCEPTION CAUGHT:\n{type(e).__name__}\n{str(e)}")
            self.log.info(f"Transaction [{i}] result: {temp}")
        # pass or fail depending on success rate
        pass_rate = 0
        if (self.success_count + self.failure_count) > 0:
            pass_rate = self.success_count / (self.success_count + self.failure_count)
        self.displayResults()
        if (pass_rate < 0.8) or (self.top_consec_fails >= 5):
            tc_fail("There were too many issues performing the transactions")
    
    def attempt_sale(self, transNo):
        """
        Attempt a single semi-randomized transaction
        return either "SUCCESS" or "FAILURE" followed by the log string
        If we fail at any point, we follow through to try and get back to a neutral state
        """
        # TODO: Redo this weird mess I originally did
        results = ""
        fail = False
        
        # Make sure we're still signed on - might remove to save time
        pos.sign_on()
        
        # Add semi-random items
        try:
            self.log.info("Starting to add items")
            self.addItems(transNo)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            fail = True
            self.log.warning(f"EXCEPTION ADDING ITEMS: {e}")
        
        # Pay out the transaction
        try:
            self.log.info("Attempting to pay")
            self.payTrans(transNo)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            fail = True
            self.log.warning(f"EXCEPTION PAYING OUT: {e}")
        
        # Hopefully handle failed to add credit
        self.log.info("Sleeping in case error pops up")
        time.sleep(2)
        self.log.info("Sleep ended")
        # Getting and cleaning the prompt
        msg = pos.read_message_box()
        if msg:
            fail = True
            self.log.warning(f"UNEXPECTED MESSAGE: {msg}")
            pos.click_message_box_key("Ok", verify=False)
        else:
            self.log.info("No message found")
            
        # Report Success if we still haven't reported a failure
        if fail:
            self.failure_count = self.failure_count + 1
            self.consec_fails = self.consec_fails + 1
            if self.consec_fails > self.top_consec_fails:
                self.top_consec_fails = self.consec_fails
            return False
        else:
            self.success_count = self.success_count + 1
            self.consec_fails = 0
            return True
            
    def addItems(self, transNo):
        """
        Helper function that adds items at semi-random
        """
        self.log.info("Adding Generic Item")
        pos.add_item("Generic Item")
        if (transNo % 2 == 0):
            self.log.info("Adding Generic Item")
            pos.add_item("Generic Item")
        if (transNo % 3 == 0):
            self.log.info("Adding Generic Item")
            pos.add_item("Generic Item")
        if (transNo % 5 == 0):
            self.log.info("Adding Generic Item")
            pos.add_item("Generic Item")
        if (transNo % 7 == 0):
            self.log.info("Adding Generic Item")
            pos.add_item("Generic Item")
        if (transNo % 11 == 0):
            self.log.info("Adding Generic Item")
            pos.add_item("Generic Item")
        if (transNo % 13 == 0):
            self.log.info("Adding Generic Item")
            pos.add_item("Generic Item")
            
    def payTrans(self, transNo):
        """
        Helper function that pays out a transaction
        """
        # TODO: use transNo to alternate payment types
        pos.click("Pay")
        pos.click_tender_key("Exact Change")
        
    def displayResults(self):
        """
        Helper function responsible for formating and displaying test results
        """
        pass_rate = 0
        if (self.success_count + self.failure_count) > 0:
            pass_rate = self.success_count / (self.success_count + self.failure_count)
        self.log.info(f"Test Results:\n\t"+
            f"Success - {str(self.success_count)}\n\t"+
            f"Failure - {str(self.failure_count)}\n\t"+
            f"Most Consecutive Fails - {str(self.top_consec_fails)}\n\t"+
            f"Pass Rate - {str(pass_rate*100)}%")

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        pos.close()
