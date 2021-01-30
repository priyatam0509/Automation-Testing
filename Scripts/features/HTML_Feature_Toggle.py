"""
    File name: HTML_Feature_Toggle.py
    Tags: HTML_POS
    Description: Enables HTML_POS features
    Author: Logan Hornbuckle
    Date created: 03/26/2020
    Date last modified: 
    Python Version: 3.7
"""

import logging
import winreg as reg
import os
import re

# framework modules
from app.util import constants, runas, system
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class HTML_Feature_Toggle():
    """
    Description: Test class that provides an interface for testing.
    """

    def __init__(self):
        """
        Initialize reg values
        """
        # The logging object. 
        # Example: self.log.info(f"Current value of var: {my_var}")
        self.log = logging.getLogger()
        self.subkey = constants.CSOFT_PP_SUBKEY
        self.reg_key = reg.OpenKey(reg.HKEY_LOCAL_MACHINE, self.subkey, 0, reg.KEY_ALL_ACCESS)


    @setup
    def setup(self):
        """
        Setup
        """
        pass


    @test
    def test_addRegVals(self):
        """
        Modify reg values
        """
        # add necessary reg values for HTML_POS
        try:
            reg.SetValueEx(self.reg_key, "POSPathName",0,reg.REG_SZ,"C:\\Passport\\htmlpos\\bin\\startit.exe")
            reg.SetValueEx(self.reg_key, "POSType",0,reg.REG_SZ,"HTMLPos")
            reg.SetValueEx(self.reg_key, "RunHTMLPosProdMode",0,reg.REG_SZ,"False")
            reg.SetValueEx(self.reg_key, "DevMode",0,reg.REG_SZ,"False")
        except Exception as e:
            self.log.warning(e)
            tc_fail("Failed to Create new registry Values")

    @test
    def test_modifyHosts(self):
        """
        Modify hosts file
        """
        temp_file = "D:\\Temp\\hosts_temp.txt"
        file = "C:\\Windows\\System32\\drivers\\etc\\hosts"
        # new host file content: changed passportedge.com & www.passportedge.com to 127.0.0.1
        new_content = "# Copyright (c) 1993-2009 Microsoft Corp.\n#\n# This is a sample HOSTS file used by Microsoft TCP/IP for Windows.\n#\n# This file contains the mappings of IP addresses to host names. Each\n# entry should be kept on an individual line. The IP address should\n# be placed in the first column followed by the corresponding host name.\n# The IP address and the host name should be separated by at least one\n# space.\n#\n# Additionally, comments (such as these) may be inserted on individual\n# lines or following the machine name denoted by a '#' symbol.\n#\n# For example:\n#\n#      102.54.94.97     rhino.acme.com          # source server\n#       38.25.63.10     x.acme.com              # x client host\n#\n# localhost name resolution is handled within DNS itself.\n# 127.0.0.1       localhost\n# ::1             localhost\n#\n127.0.0.1 localhost\n10.5.50.2 passporteps\n127.0.0.1 sjremetrics.java.com\n127.0.0.1 crl.microsoft.com\n127.0.0.1 parityserver03\n127.0.0.1 teredo.ipv6.microsoft.com\n127.0.0.1 www.msftncsi.com\n12.202.103.72 edh.gilbarcosecureaccess.com\n12.202.103.86 readerauth.magensa.net\n127.0.0.1 passportedge.com\n127.0.0.1 www.passportedge.com\n"
        
        # Create temp txt file w/ new_content, copy to hosts file & delete temp txt file
        try:
            for line in str.splitlines(new_content):
                # write desired hosts file contents to temp file
                runas.run_as(f"echo {line} >> {temp_file}")
            # copy temp_file contents to hosts file
            runas.run_as(f"copy /Y {temp_file} {file}")
            #delete temp_file
            runas.run_as(f"del /F {temp_file}")
        except Exception as e:
            self.log.warning(e)
            tc_fail("Failed to Modify Hosts file")
            
        #restart passport
        if not system.restartpp():
            tc_fail("Failed to restart passport")

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        pass
