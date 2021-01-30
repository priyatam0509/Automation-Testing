"""
    File name: TillAudit_POS.py.py
    Tags:
    Description: 
    Author: 
    Date created: 2020-04-30 16:08:11
    Date last modified: 
    Python Version: 3.7
"""

import logging, time
from app import Navi, mws, pos, system, employee
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class TillAudit_POS():
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
        self.log.info("Setting up Employee Maintenance feature")
        self.em = employee.Employee()
        # Turn off blind balancing override for user 91
        # Required for the report to generate
        self.em.change('91', {
            "Preferences": {
                "Override the \"Blind Balancing\" store option": False
            }
        })
        
        pos.connect()
        pos.sign_on()

    # @test
    # def test_TillAuditReport(self):
    #     """
    #     Perform a til audit and confirm we record the correct total in the report
    #     """
    #     # Perform a Till Audit with all types of denominations
    #     pos.click("Till Audit")
        
    #     # Coin denomination
    #     self.log.info("Adding 1 penny for $0.01")
    #     pos.enter_keypad("1", after="+")
        
    #     # Bill denomination
    #     self.log.info("Adding 10 $1 bills for $10.00")
    #     pos.click("Bills ->")
    #     pos.enter_keypad("10", after="+")
        
    #     # Other denomination
    #     self.log.info("Adding 'credit' tender for $1.10")
    #     pos.click_tender_key("credit")
    #     pos.enter_keypad("110", after="+")
        
    #     self.log.info("Finalizing till audit")
    #     pos.click("Finalize")
        
    #     # wait for report to be generated
    #     msg = pos.read_message_box(timeout=15)
    #     self.log.info(f"Message received: [{msg}]")
    #     if not "Till Audit Report" in msg:
    #         tc_fail("Expected message not found")
    #     pos.click("Ok")
        
    #     time.sleep(5) # wait for file to exist - no on screen queue its done
        
    #     # Processing the report
    #     self.log.info("Reading report")
    #     reportData = []
    #     with open(r"c:\passport\audit.txt", 'r') as report:
    #         reportData = list(report)
        
    #     # get only accounted for tenders
    #     for lineNo, line in enumerate(reportData):
    #         if "ACCOUNTED FOR" in line:
    #             reportData = reportData[lineNo:]
    #             break
              
    #     # Get cash/credt values
    #     cashVals = []
    #     creditVals = []
    #     for line in reportData:
    #         if "Cash" in line:
    #             line = line[line.index("$"):-1] # Get value without new line
    #             cashVals.append(line)
    #             self.log.info(f"Cash found: [{line}]")
    #         if "Credit" in line:
    #             line = line[line.index("$"):-1] # get value without new line
    #             creditVals.append(line)
    #             self.log.info(f"Credit found: [{line}]")
                
    #     if not "$0.01" in cashVals:
    #         tc_fail("Coin cash amout missing")
    #     if not "$10.00" in cashVals:
    #         tc_fail("Bill cash amount missing")
    #     if not "$1.10" in creditVals:
    #         tc_fail("Incorred credit amount recorded")

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        pos.close()
