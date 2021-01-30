"""
    File name: negative_item.py
    Tags:
    Description: Negative Items on HTML POS
    Author: Kevin Walker
    Date created: 2020-08-06 10:57:22
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import Navi, mws, pos, system
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class negative_item():
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
    def negative_item(self):
        """
        Verify Item linked to negative department rings up as negative price
        """
        pos.add_item("Negative Item")
        pos.pay()
        if not pos.check_receipt_for("$-5.00", verify=False):
            tc_fail("Item did not ring up as $-5.00")
        if not pos.check_receipt_for("Refund Cash", verify=False):
            tc_fail("Refund Cash was not found on receipt")

    @test
    def regular_item(self):
        """
        Verify Item not linked to a negative department does not ring up as a negative price
        """
        pos.add_item("Item 2")
        pos.pay()
        if not pos.check_receipt_for("$5.00", verify=False):
            tc_fail("Item did not ring up as $5.00")

    @test
    def negative_department(self):
        """
        Verify doing sale to a negative department rings up at a negative price
        """
        pos.click_dept_key("Dept 2")
        pos.enter_keypad("500", after = "Enter")
        pos.pay()
        if not pos.check_receipt_for("$-5.00", verify=False):
            tc_fail("Department Item did not ring up as $-5.00")
        if not pos.check_receipt_for("Refund Cash", verify=False):
            tc_fail("Refund Cash was not found on receipt")

    @test
    def regular_department(self):
        """
        Verify doing a sale to a non-negative department does not ring up as a negative price
        """
        pos.click_dept_key("Dept 1")
        pos.enter_keypad("500", after = "Enter")
        pos.pay()
        if not pos.check_receipt_for("$5.00", verify=False):
            tc_fail("Department Item did not ring up as $5.00")

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        pos.sign_off()
        pos.close()
