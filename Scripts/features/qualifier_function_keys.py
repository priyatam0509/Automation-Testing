"""
    File name: qualifier_function_keys.py
    Tags: HTML POS
    Description: Verify function keys are hidden during qualifier selection
    Author: Kevin Walker
    Date created: 2020-08-10 14:06:52
    Date last modified: 
    Python Version: 3.7
"""

import logging, time
from app import Navi, mws, pos, system
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class qualifier_function_keys():
    """
    Description: Test class that provides an interface for testing.
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
        #     self.log.debug("No snapshot to restore, if this is not expected please contact automation team")
        pos.connect()
        pos.sign_on()

    @test
    def qualifier_enter(self):
        """
        Verify function keys are not present during qualifier selection but reappear after making selection
        """
        pos.enter_plu("030")
        timeout = 10
        start_time = time.time()
        #Allow time for the POS to switch screens before checking for element
        if not system.wait_for(lambda: pos.is_element_present(pos.controls['function keys']['price check'], timeout/20.0) == False, timeout=timeout, verify=False):
            pos.click("Cancel")
            pos.void_transaction()
            tc_fail("Function Keys should not be present during qualifier selection")

        pos.click("Enter")
        start_time2 = time.time()
        #Allow time for the POS to switch screens before checking for element
        if not system.wait_for(lambda: pos.is_element_present(pos.controls['function keys']['price check'], timeout), timeout=timeout, verify=False):
            pos.void_transaction()
            tc_fail("Function Keys should be present after cancelling qualifier selection")

        pos.pay()

    @test
    def qualifier_cancel(self):
        """
        Verify function keys are not present during qualifier selection but reappear after cancelling
        """
        pos.enter_plu("030")
        timeout = 10
        start_time = time.time()
        #Allow time for the POS to switch screens before checking for element
        if not system.wait_for(lambda: pos.is_element_present(pos.controls['function keys']['price check'], timeout/20.0) == False, timeout=timeout, verify=False):
            pos.click("Cancel")
            pos.void_transaction()
            tc_fail("Function Keys should not be present during qualifier selection")

        pos.click("Cancel")
        start_time2 = time.time()
        #Allow time for the POS to switch screens before checking for element
        if not system.wait_for(lambda: pos.is_element_present(pos.controls['function keys']['price check'], timeout), timeout=timeout, verify=False):
            pos.void_transaction()
            tc_fail("Function Keys should be present after cancelling qualifier selection")

        pos.void_transaction()

        

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        pos.sign_off()
        pos.close()
