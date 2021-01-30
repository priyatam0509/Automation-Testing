"""
    File name: IS360_UnRegister.py
    Tags:
    StoryID: STARFINCH-3477
    Description: Disconnect the insite360 interface from passport.
    Author: Pavan Kumar Kantheti
    Date created: 2020-04-28 18:37:07
    Date last modified:
    Python Version: 3.7
"""
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from Scripts.features import FromInsite360
import logging
from datetime import datetime


class IS360_UnRegister():
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
    def checkInsite360(self):
        """
        """
        self.log.info("Check wether the insite 360 is enabled or not")
        insite360Enabled = FromInsite360.Check_I360_Connected()
        self.log.info(f"Insite 360 is enabled [{insite360Enabled}]")
        ProceedToTest = True
        if (insite360Enabled):
            ProceedToTest = FromInsite360.Register_UnRegister_Insite360(insite360Enabled)
            insite360Enabled = FromInsite360.Check_I360_Connected()
            self.log.info(f"After Register_UnRegister_Insite360, latest Insite 360 is enabled [{insite360Enabled}]")

        if not(ProceedToTest):
            tc_fail("Failed, Unable to proceed due to register/un-register issue.")

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        # delete pass after you implement.
        pass
