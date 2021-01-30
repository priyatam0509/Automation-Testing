"""
    File name: Security_Camera_Test.py
    Tags:
    Description: Tests the security_camera module
    Author: Alex Rudkov
    Date created: 2019-07-01 14:54:22
    Date last modified: 
    Python Version: 3.7
"""

import logging, time, random
from app import Navi, mws, pos, system, security_camera
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class Security_Camera_Test():
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

    @setup
    def setup(self):
        """Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        # if not system.restore_snapshot():
        #     raise Exception

    @test
    def test_case_1(self):
        """"Tests the configuration with the valid and invalid config dictionaries without fields that require special values in other fields
        Args: None
        Returns: None
        """
        sc = security_camera.SecurityCamera()

        params = {
            "Data will be set via": "None",
            "Stand alone clients use COM": "9", # With COM Port set
            "Combined server use COM": "0", # With COM Port set
            "Data Format": "Field Delimited",
            "Field Separator": "|",
            "Include forecourt transactions in security camera feed": True
        }

        self.log.info("Configuring the SC with invalid config that disables the SC but tries to set fields")
        if sc.setup(params):
            tc_fail("The Security Camera Interface was configured successfully when failure was expected.")
        mws.recover()

        time.sleep(2)
        sc.navigate_to()

        params = {
            "Data will be set via": "COM Port",
            "Stand alone clients use COM": "0", # With COM Port set
            "Combined server use COM": "16", # With COM Port set
            "Data Format": "Field Delimited",
            "Field Separator": "|",
            "Include forecourt transactions in security camera feed": True
        }

        self.log.info("Configuring the SC with invalid config that results in error message in top bar")
        if sc.setup(params):
            tc_fail("The Security Camera Interface was configured successfully when failure was expected.")
        mws.recover()

        time.sleep(2)
        sc.navigate_to()

        params = {
            "Data will be set via": "COM Port",
            "Stand alone clients use COM": "9", # With COM Port set
            "Combined server use COM": "0", # With COM Port set
            "Data Format": "Field Delimited",
            "Field Separator": "|",
            "Include forecourt transactions in security camera feed": True
        }

        self.log.info("Configuring the SC with invalid config that results in error message in top bar")
        if sc.setup(params):
            tc_fail("The Security Camera Interface was configured successfully when failure was expected.")
        mws.recover()

        time.sleep(2)
        sc.navigate_to()

        params = {
            "Data will be set via": "COM Port",
            "Stand alone clients use COM": "7", # With COM Port set
            "Combined server use COM": "15", # With COM Port set
            "Data Format": "Field Delimited",
            "Field Separator": "|",
            "Include forecourt transactions in security camera feed": True
        }

        self.log.info("Configuring the SRC with valid config")
        if not sc.setup(params):
            tc_fail("Failed to configure the Security Camera window")

        # Check
        time.sleep(1)
        sc.navigate_to()
        error = False
        for field, value in params.items():
            set_value = mws.get_value(field)
            if field == "Data Format" or field == "Data will be set via":
                set_value = set_value[0]

            if set_value != value:
                self.log.error(f"The field '{field}' was set successfully, but upon check had value '{set_value}' when '{value}' was expected")
                error = True
        if error:
            tc_fail("The test failed a check after configuration")
        mws.recover()

    @test
    def test_case_2(self):
        """Tests the configuration with the valid config dictionary with force check fields that require special values in other fields
        Args: None
        Returns: None
        """
        sc = security_camera.SecurityCamera()

        params = {
            "Data will be set via": "COM Port",
            "Stand alone clients use COM": "9", # With COM Port set
            "Combined server use COM": "16", # With COM Port set
            "Data Format": "Field Delimited",
            "Field Separator": "|",
            "Include forecourt transactions in security camera feed": True,
            "Host Name": "POSSERVER01"
        }

        self.log.info("Configuring the SC with invalid config that tries to set the field that is inaccessible")
        if sc.setup(params):
            tc_fail("The Security Camera Interface was configured successfully when failure was expected.")
        mws.recover()

        time.sleep(1)
        sc.navigate_to()

        params = {
            "Data will be set via": "TCP",
            "Stand alone clients use COM": "9", # With COM Port set
            "Data Format": "Field Delimited",
            "Field Separator": "|",
            "Include forecourt transactions in security camera feed": True,
        }

        self.log.info("Configuring the SC with invalid config that tries to set the field that is inaccessible")
        if sc.setup(params):
            tc_fail("The Security Camera Interface was configured successfully when failure was expected.")
        mws.recover()

        time.sleep(1)
        sc.navigate_to()

        params = {
            "Data will be set via": "COM Port",
            "Stand alone clients use COM": "9", # With COM Port set
            "Combined server use COM": "16", # With COM Port set
            "Data Format": "XML",
            "Field Separator": "|",
            "Include forecourt transactions in security camera feed": True,
        }

        self.log.info("Configuring the SC with invalid config that tries to set the field that is inaccessible")
        if sc.setup(params):
            tc_fail("The Security Camera Interface was configured successfully when failure was expected.")
        mws.recover()

        time.sleep(1)
        sc.navigate_to()

        # Valid config with COM
        params = {
            "Data will be set via": "COM Port",
            "Stand alone clients use COM": "9", # With COM Port set
            "Combined server use COM": "16", # With COM Port set
            "Data Format": "XML",
            "Include forecourt transactions in security camera feed": True,
        }

        self.log.info("Configuring the SC with valid config for COM")
        if not sc.setup(params):
            tc_fail("Failed to configure the Security Camera Interface window")

        # Check
        time.sleep(2)
        sc.navigate_to()

        error = False
        for field, value in params.items():
            set_value = mws.get_value(field)
            if field == "Data Format" or field == "Data will be set via":
                set_value = set_value[0]

            if set_value != value:
                self.log.error(f"The field '{field}' was set successfully, but upon check had value '{set_value}' when '{value}' was expected")
                error = True
        if error:
            tc_fail("The test failed a check after configuration")
        
        # Valid config with TCP
        params = {
            "Data will be set via": "TCP",
            "Data Format": "XML",
            "Include forecourt transactions in security camera feed": False,
            "Host Name": "POSSERVER01", # With TCP set
            "Host Port": "10101" # With TCP set
        }

        self.log.info("Configuring the SC with valid config for TCP")
        if not sc.setup(params):
            tc_fail("Failed to configure the Security Camera Interface window")

        # Check
        time.sleep(2)
        sc.navigate_to()

        error = False
        for field, value in params.items():
            set_value = mws.get_value(field)
            if field == "Data Format" or field == "Data will be set via":
                set_value = set_value[0]

            if set_value != value:
                self.log.error(f"The field '{field}' was set successfully, but upon check had value '{set_value}' when '{value}' was expected")
                error = True
        if error:
            tc_fail("The test failed a check after configuration")
        
        # Valid config with Data Format
        params = {
            "Data will be set via": "TCP",
            "Data Format": "Field Delimited",
            "Field Separator": "|",            
            "Include forecourt transactions in security camera feed": True,
            "Host Name": "POSSERVER01", # With TCP set
            "Host Port": "10101" # With TCP set
        }

        self.log.info("Configuring the SC with valid config for TCP")
        if not sc.setup(params):
            tc_fail("Failed to configure the Security Camera Interface window")

        # Check
        time.sleep(2)
        sc.navigate_to()

        error = False
        for field, value in params.items():
            set_value = mws.get_value(field)
            if field == "Data Format" or field == "Data will be set via":
                set_value = set_value[0]

            if set_value != value:
                self.log.error(f"The field '{field}' was set successfully, but upon check had value '{set_value}' when '{value}' was expected")
                error = True
        if error:
            tc_fail("The test failed a check after configuration")

        mws.recover()

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        # delete pass after you implement.
        pass