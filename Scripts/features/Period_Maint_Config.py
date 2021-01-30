"""
    File name: Period_Maint_Config.py
    Tags:
    Description: Tets period_maint.py module
    Author: Alex Rudkov
    Date created: 2019-06-05 14:11:57
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import Navi, mws, pos, system
from app.framework.tc_helpers import setup, test, teardown, tc_fail

from app.features import period_maint

class Period_Maint_Config():
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
        # self.log = system.setup_logging(f"test_harness.%s"%(__name__))
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
        """Sets up the General Tab of Period Maintenance
        Args: None
        Returns: None
        """
        pm = period_maint.PeriodMaintenance()

        pm_info = {
            "General" : {
                "Yearly": True,
                "Quarterly": False,
                "Monthly": False,
                "Calendar Day": True,
                "Store Close": True,
                "Variable Shift": True
            }
        }

        self.log.info("Editing Period Maintenance")
        if not pm.setup(pm_info):
            tc_fail("Failed to edit Period Maintenance")

        pm.navigate_to()

        pm_info = {
            "Something Else" : {
                "Yearly": False,
                "Quarterly": False,
                "Monthly": False,
                "Calendar Day": False,
                "Store Close": False,
                "Variable Shift": True
            }
        }

        self.log.info("Editing Period Maintenance with incorrect params")
        if pm.setup(pm_info):
            tc_fail("Failed to edit Period Maintenance")

    @test
    def test_case_2(self):
        """Sets up Weekly option in the General Tab of Period Maintenance
        Args: None
        Returns: None
        """
        pm = period_maint.PeriodMaintenance()

        pm_info = {
            "General" : {
                "Weekly" : [True, "Saturday"]
            }
        }

        self.log.info("Editing Period Maintenance")
        if not pm.setup(pm_info):
            tc_fail("Failed to edit Period Maintenance")

        pm_info = {
            "General" : {
                "Weekly" : [False]
            }
        }

        self.log.info("Editing Period Maintenance")
        if not pm.setup(pm_info):
            tc_fail("Failed to edit Period Maintenance")

        pm_info = {
            "General" : {
                "Weekly" : [True]
            }
        }

        self.log.info("Editing Period Maintenance")
        if not pm.setup(pm_info):
            tc_fail("Failed to edit Period Maintenance")
        
        pm_info = {
            "General" : {
                "Weekly" : [False]
            }
        }

        self.log.info("Editing Period Maintenance")
        if not pm.setup(pm_info):
            tc_fail("Failed to edit Period Maintenance")

        pm_info = {
            "General" : {
                "Weekly" : [True, "Monday", "Sunday"]
            }
        }

        self.log.info("Editing Period Maintenance")
        if not pm.setup(pm_info):
            tc_fail("Failed to edit Period Maintenance")

    @test
    def test_case_3(self):
        """Sets up Shift Close Options Tab of Period Maintenance
        Args: None
        Returns: None
        """
        pm = period_maint.PeriodMaintenance()

        pm_info = {
            "General" : {
                "Variable Shift" : False
            },
            "Shift Close Options" : {
                "Shift Close Reporting": [
                    ["Store Sales Summary", False, True],
                    ["Price Override Report", False, True],
                    ["Pump Totals Report", True, True]
                ]
            }
        }

        self.log.info("Editing Period Maintenance")
        if pm.setup(pm_info):
            tc_fail("Editing of Period Maintenance should have failed but it did not")

        pm.navigate_to()

        pm_info = {
            "General" : {
                "Variable Shift" : True
            },
            "Shift Close Options" : {
                "Shift Close Reporting": [
                    ["Store Sales Summary", False, True],
                    ["Price Override Report", False, True],
                    ["Pump Totals Report", True, True]
                ]
            }
        }

        self.log.info("Editing Period Maintenance")
        if not pm.setup(pm_info):
            tc_fail("Failed to edit Period Maintenance")
    
    @test
    def test_case_4(self):
        """Sets up Till Close Tab of Period Maintenance
        Args: None
        Returns: None
        """
        # period_maint.PeriodMaintenance.navigate_to()
        pm = period_maint.PeriodMaintenance()

        pm_info = {
            "Till Close" : {
                "Till Close Reports" : [
                    ["Till PLU Sales Report", True],
                    ["Till Fuel Discount Summary Report", False]
                ] 
            }
        }

        self.log.info("Editing Period Maintenance")
        if not pm.setup(pm_info):
            tc_fail("Failed to edit Period Maintenance")

    @test
    def test_case_5(self):
        """Sets up Store Close Options Tab of Period Maintenance
        Args: None
        Returns: None
        """
        period_maint.PeriodMaintenance.navigate_to()
        pm = period_maint.PeriodMaintenance()

        pm_info = {
            "Store Close Options": {
                "Allow store closes from POS Registers to start at": "12:00 AM",
                "Force the store closed at this time": "12:00 PM",
                "Force Store Close" : True,
                "Start sending reminder messages to POS Registers at": "12:00 PM",
                "Display store close reminder every": "10:00",
                "Store close reminder message": "Some message"
            }
        }

        self.log.info("Editing Period Maintenance")
        if not pm.setup(pm_info):
            tc_fail("Failed to edit Period Maintenance")
        
    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        Navi.navigate_to("MWS")
        pass