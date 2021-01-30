"""
    File name: ASU_LogFiles.py
    Tags:
    Description: 
    Author: 
    Date created: 2019-07-30
    Date last modified: 
    Python Version: 3.7
"""

import datetime
import logging
import json
import os

from app import runas
from app import system
from app.framework.tc_helpers import setup, test, teardown, tc_fail

from test_harness import RUN_DATA_FILE


class ASU_LogFiles():
    """
    Description: Test class that provides and interface for testing.
    """

    def __init__(self):
        """Initializes the Template class."""
        # The logging object. 
        # Example: self.log.info(f"Current value of var: {my_var}")
        self.log = logging.getLogger()
        
        self.logs = r"D:\Gilbarco\logs"
        self.packages = r"C:\Gilbarco\PACKAGES"
        self.cws_logs = r"X:\Gilbarco\logs"

        try:
            with open(RUN_DATA_FILE) as rdf:
                run_info = json.load(rdf)
                self.patch_file = run_info["Patch"]
        except KeyError as e:
            self.log.error(e)
            self.log.error("Failed to find the Patch variable. "\
            "Please use -var to pass in the Patch parameter")
            raise     

    @setup
    def setup(self):
        """Performs any initialization that is not default."""
        # delete pass after you implement.
        pass

    @test
    def asu_mws(self):
        """M-40273 : LogFilesMWS_F32
        
        No critical errors in D:\Gilbarco\logs\asus_date.log
        """
        Failure = False
        now = datetime.datetime.now()

        for line in open(f'{self.logs}\\ASU_{now.strftime("%Y%m%d")}.log'):
            if 'critical' in line:
                self.log.error("Found a critical failure")
                self.log.error(line)
                Failure = True

        if Failure:
            tc_fail("Found a critical error")

    #This one only passes up on the day you upgraded
    @test
    def runsql_mws(self):
        """M-40274 : LogFilesMWS_F33
        
        View D:\Gilbarco\logs\ASU_RUNSQL_date.log and verify there are no critical errors.
        """
        failure = False
        now = datetime.datetime.now()
        log_file = f'{self.logs}\\ASURUNSQL_{now.strftime("%Y%m%d")}.log'

        if not os.path.exists(log_file):
            tc_fail("The ASURUNSQL log file was not found")
    
        for line in open():
            if 'critical' in line:
                self.log.error("Found a critical failure")
                self.log.error(line)
                failure = True

        if failure:
            tc_fail("Found a critical error")
    
    @test
    def asu_cws(self):
        """M-40276 : LogFilesCWS_F35
        
        No critical errors in x:\Gilbarco\logs\asus_date.log.
        """
        failure = False
        tc_fail("Waiting on a response about the name of the log")
        log_file = "asus_date.log"
        result = runas.run_sqlcmd(destination="POSCLIENT001",
                                user="PassportTech",
                                password="911Tech",
                                cmd=(f'type {self.cws_logs}\{log_file}'))

        output = runas.parse_output(result)
        if not runas.error_check(output):
            tc_fail("There was an issue with the SQLCMD")

        for _line in output:
            if "critical" in _line:
                self.log.error("Found a critical failure")
                self.log.error(_line)
                failure = True

        if failure:
            tc_fail("Found a critical error")

    @test
    def asu_edh(self):
        """M-40277 : LogFilesEDH_F36
        
        No critical errors in D:\Gilbarco\logs\asus_date.log.
        """
        failure = False
        now = datetime.datetime.now()
        log_file = f'{self.logs}\\ASU_{now.strftime("%Y%m%d")}.log'
        
        result = runas.run_sqlcmd(f'type {log_file}')

        output = runas.parse_output(result)
        if not runas.error_check(output):
            tc_fail("There was an issue with the SQLCMD")

        for _line in output:
            if "critical" in _line:
                self.log.error("Found a critical failure")
                self.log.error(_line)
                failure = True

        if failure:
            tc_fail("Found a critical error")

    #@NOTE: There has been no new file since January
    @test
    def runsql_edh(self):
        """M-40278 : LogFilesEDH_F37
        
        No critical errors in D:\Gilbarco\logs\ASU_RUNSQL_date.log.
        """
        failure = False
        now = datetime.datetime.now()
        result = runas.run_sqlcmd(f'type {self.logs}\\ASURUNSQL_{now.strftime("%Y%m%d")}.log')

        output = runas.parse_output(result)
        if not runas.error_check(output):
            tc_fail("There was an issue with the SQLCMD")

        for _line in output:
            if "critical" in _line:
                self.log.error("Found a critical failure")
                self.log.error(_line)
                failure = True

        if failure:
            tc_fail("Found a critical error")

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends."""
        # delete pass after you implement.
        pass