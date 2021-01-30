"""
    File name: EmpMng_IS360_RestartSvc.py
    Tags:
    StoryID: STARFINCH-3473
    Description: Employee Management from IS360, security group .json
                 generate from RemoteManager service
    Author: Pavan Kumar Kantheti
    Date created: 2020-01-20 15:26:37
    Date last modified: 2020-01-20 21:15:09
    Python Version: 3.7
"""
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from Scripts.features import FromInsite360
import logging
from datetime import datetime


class EmpMng_IS360_RestartSvc():
    """
        Description: Test class that provides an interface for testing.
    """

    def __init__(self):
        """
        Initializes the Template class.
        Args: None
        Returns: None
        """
        # The logging object.
        # Example: self.log.info(f"Current value of var: {my_var}")
        self.log = logging.getLogger()

    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        pass

    @test
    def restart_RemoteManager_Service(self):
        """
        Zephyr Id : Restart the "RemoteManagerSVC" service to check security group event .json is generated or not
        Args: None
        Returns: None
        """
        self.log.info("Check wether the insite 360 is enabled or not")
        insite360_enabled = FromInsite360.Check_I360_Connected()
        self.log.info(f"Insite 360 is enabled [{insite360_enabled}]")

        proceed_test = FromInsite360.insite360_configure()

        if (proceed_test):
            proceed_test = FromInsite360.Register_UnRegister_Insite360(insite360_enabled)
            insite360_enabled_status = FromInsite360.Check_I360_Connected()
            self.log.info(f"After Register_UnRegister_Insite360, latest Insite 360 is enabled [{insite360_enabled_status}]")
            if (insite360_enabled_status == insite360_enabled):
                proceed_test = False
            else:
                proceed_test = True
                insite360_enabled = insite360_enabled_status

        if (proceed_test):
            # Restart the service
            startTimeFromAuto = datetime.now()
            sgStatus = FromInsite360.json_generate_status(startTimeFromAuto, "securitygroups")
            self.log.info(f"Security group event send status [{ not sgStatus}] Time out[{sgStatus}]")
            empStatus = FromInsite360.json_generate_status(startTimeFromAuto, "employees", file_copied=True)
            self.log.info(f"Employees event send status [{ not empStatus}] Time out[{empStatus}]")
            if (insite360_enabled):
                if (sgStatus and empStatus):
                    sgStatus = FromInsite360.restart_rmservice_max("securitygroups")
                    if (not sgStatus):
                        startTimeFromAuto = datetime.now()
                        empStatus = FromInsite360.json_generate_status(startTimeFromAuto, "employees", file_copied=True)
                    if (sgStatus and empStatus):
                        tc_fail("Failed, .json file is not generated after restart service")                       
            else:
                if not(sgStatus and empStatus):
                    tc_fail("Failed, .json file is generated after restart service")
        else:
            tc_fail("Failed, Unable to proceed due to register/un-register issue.")

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        # delete pass after you implement.
        pass

