"""
    File name: report_test.py
    Tags:
    Description: 
    Author: 
    Date created: 2019-06-11 15:14:32
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import mws, system, report_maint
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class report_test():
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
        self.log = logging.getLogger()
        self.rm_info = {
            "Configuration":{
                "Generate PDF files": True,
                "Generate PDF with password": True,
                "Generate PDF with password edit": "password",
                "Print the report": True,
                "Copy reports to local XML Gateway Back Office share": False,
                "Copy reports to local PPXMLData share": True,
                "Copy reports to Insite360": False,
                "Copy reports to alternate destination": False
            },
            "FTP Options":{
                "Copy the Reports to FTP location": True,
                "Host Description": "Test Description",
                "Host Address": "Test Address",
                "Host Port": "7777",
                "User Name": "Test Username",
                "Password": "password",
                "FTP Folder": "Test Folder",
                "Use Secure FTP": True
            }
        }

    @setup
    def setup(self):
        """Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        # if not system.restore_snapshot():
        #     raise Exception

        self.rm = report_maint.ReportMaintenance()
        self.rm.navigate_to()

    @test
    def configure_report(self):
        """Attempts to configure a report according to specified inputs.
        Args: None
        Returns: None
        """
        if not self.rm.configure(self.rm_info):
            tc_fail("Could not configure Report")

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        # delete pass after you implement.
        pass