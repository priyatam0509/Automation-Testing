"""
    File name: EL_StressTest.py
    Tags:
    Description: 
    Author: 
    Date created: 2019-05-17 14:47:37
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import Navi, mws, pos, system, console, checkout
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app import pinpad

import time
import sys

class EL_StressTest():
    """
    Description: Test class that provides an interface for testing.
    """

    def __init__(self):
        # The logging object. 
        # Example: self.log.info(f"Current value of var: {my_var}")
        self.log = logging.getLogger()

    @setup
    def setup(self):
        self.log.info("Attempting to connect")
        checkout.connect()

    @test
    def rapid_transactions(self):
        """Attemps to perform rapid success transactions with various items
        Setting for only 100 incase accidently ran in automation suites
        Best ran manually after increasing transaction numbers
        Args: None
        Returns: None
        """
        # keep track of how often we succeed or fail
        self.success_count = 0
        self.failure_count = 0
        self.consec_fails = 0
        self.top_consec_fails = 0
        # attempt a LOT of sales
        for i in range(1, 5001):
            if (self.top_consec_fails >= 5):
                pass_rate = self.success_count / (self.success_count + self.failure_count)
                self.log.info("Test Results:\n\tSuccess - "+str(self.success_count)+
                    "\n\tFailure - "+str(self.failure_count)+"\n\tMost Consecutive Fails - "+
                    str(self.top_consec_fails)+"\n\tPass Rate - "+str(pass_rate*100)+"%")
                tc_fail("Too many consequetive failures for a transaction")
            temp = "attemp_sale() failed to return"
            try:
                temp = self.attempt_sale(i)
            except Exception as e:
                self.log.info("EXCEPTION CAUGHT: "+str(e))
            self.log.info(temp)
        # pass or fail depending on success rate
        pass_rate = self.success_count / (self.success_count + self.failure_count)
        self.log.info("Test Results:\n\tSuccess - "+str(self.success_count)+
            "\n\tFailure - "+str(self.failure_count)+"\n\tMost Consecutive Fails - "+
            str(self.top_consec_fails)+"\n\tPass Rate - "+str(pass_rate*100)+"%")
        if (pass_rate < 0.8) or (self.top_consec_fails >= 5):
            tc_fail("There were too many issues performing the transactions")


    """
    Attempt a single semi-randomized transaction
    return either "SUCCESS", or a string containing the failure reason
    If we fail at any point, we follow through to try and get back to a neutral state
    """
    def attempt_sale(self, transNo):
        results = ""
        fail = False
        # Hit Start
        try:
            if checkout.click_welcome_key("Start"):
                results = results + "\n\tClicked Start"
            else:
                results = results + "\n\tFailed to click start."
                fail = True
        except:
            results = results + "\n\tException on click start."
            fail = True

        # Add semi-random items
        try:
            if (transNo % 2 == 1):
                if checkout.click_speed_key("Item 2"):
                    results = results + "\n\tClicked Item 2"
                else:
                    results = results + "\n\tFailed to add Item 2"
                    fail = True
            if (transNo % 3 == 1):
                if checkout.click_speed_key("Item 3"):
                    results = results + "\n\tClicked Item 3"
                else:
                    results = results + "\n\tFailed to add Item 3"
                    fail = True
            if (transNo % 4 == 1):
                if checkout.click_speed_key("Item 4"):
                    results = results + "\n\tClicked Item 4"
                else:
                    results = results + "\n\tFailed to add Item 4"
                    fail = True
            if checkout.click_speed_key("Generic Item"):
                results = results + "\n\tClicked Generic Item"
            else:
                results = results + "\n\tFailed to add Generic Item"
                fail = True
        except:
            results = results + "\n\tException on add items"
            fail = True
        
        # Pay out the transaction
        try:
            if checkout.click_function_key("Pay"):
                results = results + "\n\tClicked the pay button"
            else:
                results = results + "\n\tFailed to find pay button"
                fail = True
        except:
            results = results + "\n\tException on finding Pay"
            fail = True
        try:
            if pinpad.swipe_card():
                results = results + "\n\tPayed out"
            else:
                results = results + "\n\tFailed to swipe card"
                fail = True
        except:
            results = results + "\n\tException on swiping card"
            fail = True
            
        # Hopefully handle failed to add credit
        self.log.info("Sleeping in case error pops up")
        time.sleep(5)
        self.log.info("Sleep ended")
        # Getting and cleaning the prompt
        msg = checkout.read_message_box()
        if msg:
            msg = " ".join(msg.split())
            fail = checkout.click_message_box_key("OK")
            results = results + "\n\tPrompt appeared: "+msg+"\n\tClicked 'OK'"
        else:
            results = results + "\n\tNo alert prompts."
        
        # Report Success if we still haven't reported a failure
        if (not fail):
            self.success_count = self.success_count + 1
            self.consec_fails = 0
            results = "SUCCESS:"+results
        else:
            self.failure_count = self.failure_count + 1
            self.consec_fails = self.consec_fails + 1
            if self.consec_fails > self.top_consec_fails:
                self.top_consec_fails = self.consec_fails
            results = "FAILURE:"+results

        # send back the results
        results = "Transaction "+str(transNo)+": "+results
        return results




    @teardown
    def teardown(self):
        time.sleep(5)
        checkout.close()
