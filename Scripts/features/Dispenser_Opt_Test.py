"""
    File name: Dispenser_Opt_Test.py
    Tags:
    Description: Tests Dispenser Options module
    Author: Alex Rudkov
    Date created: 2019-06-20 16:31:26
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import Navi, mws, pos, system, dispenser_options
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class Dispenser_Opt_Test():
    """
    Test class that provides an interface for testing.
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
        """Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        # if not system.restore_snapshot():
        #     raise Exception

    @test
    def test_case_1(self):
        """
        Configures Despensers
        """

        params = {
            "Mode" : ["Primary", "Secondary"],
            "Dispensers" : {
                "1 P" : {
                            "Modes": "Unattended",
                            "Service Level": "SELF",
                            "General Authorization": False,
                            "PrePay Only": False,
                            "Pre-Authorization Time Out": "100",
                            "Allow Outdoor Presets": False,
                            "Enable Unattended Operation": False,
                            "Payment Mode": "Payment First"
                        },
                "2 S" : {
                            "Modes": "Semi-Attended",
                            "Service Level": "SELF",
                            "General Authorization": True,
                            "Pre-Authorization Time Out": "120",
                            "Allow Outdoor Presets": True,
                            "Enable Unattended Operation": True,
                            "Payment Mode": "Payment First"
                        }
            }
        }

        do = dispenser_options.DispenserOptions()

        if not do.setup(params):
            tc_fail("Failed to configure dispensers")

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        # delete pass after you implement.
        pass