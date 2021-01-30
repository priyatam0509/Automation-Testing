"""
    File name: Recovery_Config_Opt_Test.py
    Tags:
    Description: Tests the configuration of the recovery_config.RecoveryConfigurationOptions module
    Author: Alex Rudkov
    Date created: 2019-06-28 13:41:11
    Date last modified: 
    Python Version: 3.7
"""

import logging, time
from app import Navi, mws, pos, system, recovery_config
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class Recovery_Config_Opt_Test():
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
        """Tests the configuration with the valid and invalid config dictionaries without force check fields
        Args: None
        Returns: None
        """
        rc = recovery_config.RecoveryConfiguration()

        params = {
            "Start time": "3:00 AM",
                "Sunday": True,
                "Monday": True,
                "Tuesday": True,
                "Wednesday": True,
                "Thursday": True,
                "Friday": True,
                "Saturday": True,
                "Archive Backup Sets": True,
                "Run a transaction log backup once every": "10",
        }

        self.log.info("Configuring the SRC with invalid config that results in error message in top bar")
        if rc.setup(params):
            tc_fail("The System Recovery Configuration was configured successfully when failure was expected.")
        mws.recover()

        # Check
        time.sleep(2)
        rc.navigate_to()

        params = {
            "Start time": "3:00 AM",
                "Sunday": True,
                "Monday": True,
                "Tuesday": True,
                "Wednesday": True,
                "Thursday": True,
                "Friday": True,
                "Saturday": True,
                "Run Differential Backups on all other days": True,
                "Archive Backup Sets": True,
                "Run a transaction log backup once every": "30"
        }

        self.log.info("Configuring the SRC with invalid config that tries to set unavailable field")
        if rc.setup(params):
            tc_fail("The System Recovery Configuration was configured successfully when failure was expected.")

        # Check
        time.sleep(2)
        rc.navigate_to()
    
        params = {
            "Start time": "3:00 AM",
            "Sunday": True,
            "Monday": True,
            "Tuesday": True,
            "Wednesday": True,
            "Thursday": False,
            "Friday": True,
            "Saturday": True,
            "Run Differential Backups on all other days": True,
            "Archive Backup Sets": True,
            "Run a transaction log backup once every": "30"
        }

        self.log.info("Configuring the SRC with valid config")
        if not rc.setup(params):
            tc_fail("Failed to configure the System Recovery Configuration window")

        time.sleep(1)
        rc.navigate_to()
        error = False
        for field, value in params.items():
            set_value = mws.get_value(field)
            if set_value != value:
                self.log.error(f"The field '{field}' was set successfully, but upon check had value '{set_value}' when '{value}' was expected")
                error = True
        if error:
            tc_fail("The test failed a check after configuration")
        mws.recover()

    @test
    def test_case_2(self):
        """Tests the configuration with the valid config dictionary with force check fields
        Args: None
        Returns: None
        """
        rc = recovery_config.RecoveryConfiguration()

        # Set up a valid config first unchecking everythin that can be unchecked
        params = {
            "Sunday": False,
            "Monday": False,
            "Tuesday": False,
            "Wednesday": False,
            "Thursday": False,
            "Friday": False,
            "Saturday": True,
            "Archive Backup Sets": False
        }

        rc.setup(params)

        time.sleep(1)
        rc.navigate_to()

        params = {
            "Start time": "3:00 AM",
            "Sunday": True,
            "Monday": True,
            "Tuesday": True,
            "Wednesday": True,
            "Thursday": True,
            "Friday": True,
            "Saturday": True,
            "Delete Archived Backup Sets older than": "2",
            "Run a transaction log backup once every": "30",
        }

        if rc.setup(params):
            tc_fail("The System Recovery Configuration was configured successfully when a failure was expected.")
        
        time.sleep(2)
        rc.navigate_to()

        params = {
                "Start time": "3:00 AM",
                "Sunday": True,
                "Monday": True,
                "Tuesday": True,
                "Wednesday": True,
                "Thursday": True,
                "Friday": True,
                "Saturday": True,
                "Archive Backup Sets": True,
                "Delete Archived Backup Sets older than": "2",
                "Run a transaction log backup once every": "30",
            }

        if not rc.setup(params):
            tc_fail("Failed to configure the System Recovery Configuration window")

        # Check
        time.sleep(2)
        rc.navigate_to()

        error = False
        for field, value in params.items():
            set_value = mws.get_value(field)
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