"""
    File name: EmpMng_IS360_SecurityGrp.py
    Tags:
    StoryID: STARFINCH-3474
    Description: Employee Management from IS360,
                 json object generation and send for Security group to IS360
    Author: Pavan Kumar Kantheti
    Date created: 2020-01-16 01:23:45
    Date last modified: 2020-03-28 12:34:56
    Python Version: 3.7
"""
from app import mws
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app.features import security_grp_maint
from Scripts.features import FromInsite360
from datetime import datetime
import logging


class EmpMng_IS360_SecurityGrp():
    """
        Description: Test class that provides an interface for testing.
    """

    insite360Enabled = False

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

    def DeleteSecurityGroup(self, securityGroupName):
        """
        Delete selected (securityGroupName) security group from the list
        Args: securityGroupName
        Returns: True/False
        """
        securityGroupMainObj = security_grp_maint.SecurityGroupMaintenance()
        deleteStat = securityGroupMainObj.delete(securityGroupName)
        return deleteStat

    @test
    def add_new_securitygroup_TC1(self):
        """
        Zephyr Id : Add a new security group to the list and check the
                    .json file is generated or not to send i360
        Args: None
        Returns: None
        """
        self.log.info("Check wether the insite 360 is enabled or not")
        self.insite360Enabled = FromInsite360.Check_I360_Connected()
        self.log.info(f"Insite 360 is enabled [{self.insite360Enabled}]")

        startTimeFromAuto = datetime.now()
        self.log.info("Navigate to -> Security Group Maintenance")
        securityGroupMainObj = security_grp_maint.SecurityGroupMaintenance()

        # Add new Securty group with details Cashier1, 40
        cfg = {
                "Security Group Description": "Cashier1",
                "Security Level": "40",
                "Point Of Sale": "Select All",
                "Reboot POS": True,
                "Safe Drop": {"Operator Till Only": True}
            }
        group1Status = securityGroupMainObj.add(cfg)

        # If the security group already exists
        # then come back to security group maintenance screen
        if (not group1Status):
            mws.click_toolbar("No")
            group1Status = True
        # If security group is added already no need to generate the file
        # If we added the new security group, json data has to be generate.
        if (group1Status):
            # Restart the Service and check the JSON Data generated or NOT
            jsonTimeout = FromInsite360.json_generate_status(startTimeFromAuto, "securitygroups")
            if (self.insite360Enabled):
                if (jsonTimeout):
                    jsonTimeout = FromInsite360.restart_rmservice_max("securitygroups")
                    if (jsonTimeout):
                        tc_fail("Failed, .json data is not sent to I360")
            else:
                if (not jsonTimeout):
                    tc_fail("Failed, .json data is generated")

    @test
    def copy_securitygroup_TC2(self):
        """
        Zephyr Id : copy the existing security group from the list.
                    and check the .json file is generated or not to send i360
        Args: None
        Returns: None
        """
        self.log.info(f"Insite 360 is enabled [{self.insite360Enabled}]")
        startTimeFromAuto = datetime.now()
        securityGroupMainObj = security_grp_maint.SecurityGroupMaintenance()
        deletestatus = securityGroupMainObj.delete("Cashier2")
        self.log.info(f"Delete status for cashier2 [{deletestatus}]")
        # copy Securty group with details from Cashier1
        cfg = {
            "Security Group Description": "Cashier2",
            "Security Level": "40",
            "Accounting Reports": True,
            "Back Office": True
            }
        copyStatus = securityGroupMainObj.copy("Cashier1", cfg)

        # If the security group already exists
        # then come back to security group maintenance screen
        if (not copyStatus):
            mws.click_toolbar("No")

        if (copyStatus):
            # Restart the Service and check the JSON Data generated or NOT
            jsonTimeout = FromInsite360.json_generate_status(startTimeFromAuto, "securitygroups")
            if (self.insite360Enabled):
                if (jsonTimeout):
                    jsonTimeout = FromInsite360.restart_rmservice_max("securitygroups")
                    if (jsonTimeout):
                        tc_fail("Failed, .json data is not sent to I360")
            else:
                if (not jsonTimeout):
                    tc_fail("Failed, .json data is generated")
        else:
            tc_fail("Failed, unable to copy the security group")

    @test
    def modify_securitygroup_SecurityLevel_TC3(self):
        """
        Zephyr Id : Modify the security group only security level.
                    and check the .json file is generated or not to send i360
        Args: None
        Returns: None
        """
        self.log.info(f"Insite 360 is enabled [{self.insite360Enabled}]")
        startTimeFromAuto = datetime.now()
        securityGroupMainObj = security_grp_maint.SecurityGroupMaintenance()
        # update new Securty group with details Cashier2, 37
        cfg = {
            "Security Group Description": "Cashier2",
            "Security Level": "37",
            "Accounting Reports": True,
            "Back Office": False
            }
        modifyStatus = securityGroupMainObj.change("Cashier2", cfg)
        if (not modifyStatus):
            mws.click_toolbar("No")

        # If only system applications are modified no need to generate the file
        # if file(.json) is generate then the test case is failed
        # If we modifiy only security level then file has to be generate.

        if (modifyStatus):
            # Restart the Service and check the JSON Data generated or NOT
            jsonTimeout = FromInsite360.json_generate_status(startTimeFromAuto, "securitygroups")
            if (self.insite360Enabled):
                if (jsonTimeout):
                    jsonTimeout = FromInsite360.restart_rmservice_max("securitygroups")
                    if (jsonTimeout):
                        tc_fail("Failed, .json data is not sent to I360")
            else:
                if (not jsonTimeout):
                    tc_fail("Failed, .json data is generated")
        else:
            tc_fail("Failed, unable to modify the security group")

    @test
    def modify_securitygroup_description_TC4(self):
        """
        Zephyr Id : Modify the security group only description.
                    and check the .json file is generated or not to send i360
        Args: None
        Returns: None
        """
        self.log.info(f"Insite 360 is enabled [{self.insite360Enabled}]")
        startTimeFromAuto = datetime.now()
        securityGroupMainObj = security_grp_maint.SecurityGroupMaintenance()

        # update new Securty group with details Cashier7
        cfg = {
            "Security Group Description": "Cashier7",
            "Security Level": "37",
            "Accounting Reports": True,
            "Back Office": False
            }

        modifyStatus = securityGroupMainObj.change("Cashier2", cfg)

        # If only system applications are modified no need to generate the file
        # if file(.json) is generate then the test case is failed
        # If we modifiy only security level then file has to be generate.
        if (modifyStatus):
            # Restart the Service and check the JSON Data generated or NOT
            jsonTimeout = FromInsite360.json_generate_status(startTimeFromAuto, "securitygroups")
            if (self.insite360Enabled):
                if (jsonTimeout):
                    jsonTimeout = FromInsite360.restart_rmservice_max("securitygroups")
                    if (jsonTimeout):
                        tc_fail("Failed, .json data is not sent to I360")
            else:
                if (not jsonTimeout):
                    tc_fail("Failed, .json data is generated")
        else:
            tc_fail("Failed, unable to modify the security group")

    @test
    def modify_securitygroup_systemApplications_TC5(self):
        """
        Zephyr Id : Modify the security group only systemApplications.
                    and check the .json file is generated or not to send i360
        Args: None
        Returns: None
        """
        self.log.info(f"Insite 360 is enabled [{self.insite360Enabled}]")
        startTimeFromAuto = datetime.now()
        securityGroupMainObj = security_grp_maint.SecurityGroupMaintenance()
        cfg = {
            "Security Group Description": "Cashier1",
            "Security Level": "40",
            "Accounting Reports": True,
            "Back Office": True,
            "Backup Journals": True
            }
        modifyStatus = securityGroupMainObj.change("Cashier1", cfg)
        self.log.info(f"Updating Security Group with systemApplications [{modifyStatus}]")

        if (not modifyStatus):
            mws.click_toolbar("No")

        # if file(.json) is generate then the test case is failed
        # If modifiy only name or security level then file has to be generate.
        if not(self.insite360Enabled):
            # Restart the Service and check the JSON Data generated or NOT
            jsonTimeout = FromInsite360.json_generate_status(startTimeFromAuto, "securitygroups")
        else:
            jsonTimeout = FromInsite360.json_generate_status(startTimeFromAuto, "securitygroups", no_reset=True)
        if (not jsonTimeout):
            tc_fail("Failed, .json data is generated with out security group changes")

    @test
    def modify_securitygroup_NoChanges_TC6(self):
        """
        Zephyr Id : Modify the security group with out any changes.
                    and check the .json file is generated or not to send i360
        Args: None
        Returns: None
        """
        self.log.info(f"Insite 360 is enabled [{self.insite360Enabled}]")
        startTimeFromAuto = datetime.now()
        securityGroupMainObj = security_grp_maint.SecurityGroupMaintenance()
        cfg = {
            "Security Group Description": "Cashier7",
            "Security Level": "37",
            "Accounting Reports": True,
            "Back Office": False
            }
        modifyStatus = securityGroupMainObj.change("Cashier7", cfg)
        self.log.info(f"Updating Security Group with systemApplications [{modifyStatus}]")

        if (not modifyStatus):
            mws.click_toolbar("No")

        # if file(.json) is generate then the test case is failed
        # If modifiy only name or security level then file has to be generate.
        if not(self.insite360Enabled):
            # Restart the Service and check the JSON Data generated or NOT
            jsonTimeout = FromInsite360.json_generate_status(startTimeFromAuto, "securitygroups")
        else:
            jsonTimeout = FromInsite360.json_generate_status(startTimeFromAuto, "securitygroups", no_reset=True)
        if (not jsonTimeout):
            tc_fail("Failed, .json data is generated with out security group changes")

    @test
    def delete_securitygroup_TC7(self):
        """
        Zephyr Id : Delete the existing security group from the list.
                    and check the .json file is generated or not to send i360
        Args: None
        Returns: None
        """
        self.log.info(f"Insite 360 is enabled [{self.insite360Enabled}]")
        startTimeFromAuto = datetime.now()
        deletestatus = self.DeleteSecurityGroup("Cashier7")

        if (deletestatus):
            # Restart the Service and check the JSON Data generated or NOT
            jsonTimeout = FromInsite360.json_generate_status(startTimeFromAuto, "securitygroups")
            if (self.insite360Enabled):
                if (jsonTimeout):
                    jsonTimeout = FromInsite360.restart_rmservice_max("securitygroups")
                    if (jsonTimeout):
                        tc_fail("Failed, .json data is not sent to I360")
            else:
                if (not jsonTimeout):
                    tc_fail("Failed, .json data is generated")
        else:
            tc_fail("Failed, unable to delete the security group")

    @test
    def delete_assignedsecuritygroup_TC8(self):
        """
        Zephyr Id : Delete the existing security group from the list.
                    and check the .json file is generated or not to send i360
        Args: None
        Returns: None
        """
        self.log.info(f"Insite 360 is enabled [{self.insite360Enabled}]")
        startTimeFromAuto = datetime.now()
        deletestatus = self.DeleteSecurityGroup("Cashier")

        if not(self.insite360Enabled):
            # Restart the Service and check the JSON Data generated or NOT
            jsonTimeout = FromInsite360.json_generate_status(startTimeFromAuto, "securitygroups")
        else:
            jsonTimeout = FromInsite360.json_generate_status(startTimeFromAuto, "securitygroups", no_reset=True)

        if (not jsonTimeout):
            tc_fail("Failed, .json data is generated")

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        self.log.info("Setting back to MWS home page")
        mws.click_toolbar("Exit")

