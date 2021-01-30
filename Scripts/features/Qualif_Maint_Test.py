"""
    File name: Qualif_Maint_Test.py
    Tags:
    Description: 
    Author: 
    Date created: 2019-06-13 13:07:51
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import Navi, mws, pos, system
from app.framework.tc_helpers import setup, test, teardown, tc_fail

from app.features import qualifier_maint

class Qualif_Maint_Test():
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
        """Adds new qualifier group and qualifier type. Normal flow
        Args: None
        Returns: None
        """
        qualifier_maint.QualifierMaintenance.navigate_to()
        
        qm_info = {
            "Groups" : [ "Totaly available name"]
        }

        qm = qualifier_maint.QualifierMaintenance()

        if not qm.add(qm_info):
            tc_fail("Could not add qualifier group")

        qm_info = {
            "Types" : ["Available name Type", "2"]
        }

        if not qm.add(qm_info):
            tc_fail("Could not add qualifier group")

    @test
    def test_case_2(self):
        """Changes the qualifier group and qualifier type. Normal flow
        Args: None
        Returns: None
        """
        qualifier_maint.QualifierMaintenance.navigate_to()
        
        qm_info = {
            "Groups" : [ "Not anymore" ]
        }

        qm = qualifier_maint.QualifierMaintenance()

        if not qm.change("Totaly available name", qm_info):
            tc_fail("Could not change qualifier group")

        qm_info = {
            "Groups" : [ "" ]
        }

        if not qm.change("Not anymore", qm_info):
            tc_fail("Could not change qualifier group")

        qm_info = {
            "Types" : ["New Type", "11"]
        }

        if not qm.change("Available name Type", qm_info):
            tc_fail("Could not change qualifier group")
        
        qm_info = {
            "Types" : ["", "21"]
        }

        if not qm.change("New Type", qm_info):
            tc_fail("Could not change qualifier group")

        qm_info = {
            "Types" : ["Some Type", ""]
        }

        if not qm.change("New Type", qm_info):
            tc_fail("Could not change qualifier group")

        qm_info = {
            "Types" : ["", ""]
        }

        if not qm.change("Some Type", qm_info):
            tc_fail("Could not change qualifier group")

    @test
    def test_case_3(self):
        """Checks and unchecks the checkboxes 
        for the qualifier group. Normal flow
        Args: None
        Returns: None
        """
        qualifier_maint.QualifierMaintenance.navigate_to()

        qm_info = {
            "Groups" : {
                "030-Qual 1" : [
                    "Test Type",
                    "Test Type Type"
                ],
                "031-Qual 2" : [
                    "Test Type"
                ],
                "Not anymore" : [
                    "Some Type"
                ]
            },
            "Types" : {
                "Test Type" : [
                    "030-Qual 1",
                    "031-Qual 2",
                    "036-Qual 7"
                ]
            }
        }

        qm = qualifier_maint.QualifierMaintenance()

        if not qm.check(qm_info):
            tc_fail("Could not check qualifier group")

        qm_info = {
            "Groups" : {
                "030-Qual 1" : [
                    "Test Type",
                    "Test Type Type"
                ],
                "031-Qual 2" : [
                    "Test Type"
                ],
                "Not anymore" : [
                    "Some Type"
                ]
            },
            "Types" : {
                "Test Type" : [
                    "030-Qual 1",
                    "031-Qual 2",
                    "036-Qual 7"
                ]
            }
        }

        if not qm.uncheck(qm_info):
            tc_fail("Could not uncheck qualifier group")

    @test
    def test_case_4(self):
        """Deletes the qualifier group and qualifier type. Normal flow
        Args: None
        Returns: None
        """
        qualifier_maint.QualifierMaintenance.navigate_to()

        qm = qualifier_maint.QualifierMaintenance()

        if not qm.delete("Some Type", "Types"):
            tc_fail("Could not delete qualifier group")

        if not qm.delete("Not anymore", "Groups"):
            tc_fail("Could not delete qualifier group")

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        pass