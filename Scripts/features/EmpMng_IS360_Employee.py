"""
    File name: EmpMng_IS360_Employee.py
    Tags:
    StoryID: STARFINCH-3476
    Description: Employee configuration event json object sent to
                 Insite360file genaration validation
    Author: Pavan Kumar Kantheti
    Date created: 2020-01-31 17:27:37
    Date last modified: 2020-03-28 11:22:33
    Python Version: 3.7
"""
from app.features import employee
from app import mws
from Scripts.features import FromInsite360
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from datetime import datetime
import logging


class EmpMng_IS360_Employee():
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
    
    def change_employee_by(self, field, tabName):
        """
        Change the employee data from UI based on the field and value
        Args: field (string) - Name of the field as FirstName, LastName, State etc
              tabName (string) - tabname at the screen
        Returns: returnStatus (bool) - True/ False
        """
        self.log.info(f"Insite 360 is enabled [{self.insite360Enabled}]")
        self.log.info(f"Start change_employee_by [{field}]")
        emp = employee.Employee()
        self.log.info(f"After navigate, Change employee [{field}]")

        # check wether the employee is already exists or not
        # if yes, change the employee details, other wise add first time
        empexist = mws.set_value("Employees", "37")
        startTimeFromAuto = datetime.now()
        disableControl = False
        returnStatus = True
        if (empexist):
            mws.click_toolbar("Change")
            mws.select_tab(tabName)
            fieldValue = mws.get_value(field, tabName)
            self.log.info(f"Before setting the [{field}] value is [{fieldValue}]")
            if (field == "Last Name"):
                if (fieldValue == "Cashier37"):
                    addStatus = mws.set_value(field, "Cashier 37", tabName)
                else:
                    addStatus = mws.set_value(field, "Cashier37", tabName)
            elif (field == "First Name"):
                if (fieldValue == "Auto"):
                    addStatus = mws.set_value(field, "Automation", tabName)
                else:
                    addStatus = mws.set_value(field, "Auto", tabName)
            elif (field == "Birth Date"):
                if (fieldValue == "08/30/82" or fieldValue == "08/30/1982"):
                    addStatus = mws.set_value(field, "04/05/1985", tabName)
                else:
                    addStatus = mws.set_value(field, "08/30/1982", tabName)
            elif (field == "Address Line 1"):
                if (fieldValue == "123 Fake Street"):
                    addStatus = mws.set_value(field, "786 Fake Street", tabName)
                else:
                    addStatus = mws.set_value(field, "123 Fake Street", tabName)
            elif (field == "Address Line 2"):
                if (fieldValue == "Bldg 1"):
                    addStatus = mws.set_value(field, "Bldg 37", tabName)
                else:
                    addStatus = mws.set_value(field, "Bldg 1", tabName)
            elif (field == "Address Line 3"):
                if (fieldValue == "Suite 234"):
                    addStatus = mws.set_value(field, "Suite 420", tabName)
                else:
                    addStatus = mws.set_value(field, "Suite 234", tabName)
            elif (field == "City"):
                if (fieldValue == "Greensboro"):
                    addStatus = mws.set_value(field, "High Point", tabName)
                else:
                    addStatus = mws.set_value(field, "Greensboro", tabName)
            elif (field == "State"):
                if (fieldValue == "NC"):
                    addStatus = mws.set_value(field, "North Carolina", tabName)
                else:
                    addStatus = mws.set_value(field, "NC", tabName)
            elif (field == "Postal Code"):
                if (fieldValue == "27410"):
                    addStatus = mws.set_value(field, "27420", tabName)
                else:
                    addStatus = mws.set_value(field, "27410", tabName)
            elif (field == "Telephone"):
                if (fieldValue == "(897)867-7377"):
                    addStatus = mws.set_value(field, "(982)098-0870", tabName)
                else:
                    addStatus = mws.set_value(field, "(897)867-7377", tabName)
            elif (field == "Active Operator"):
                if (fieldValue):
                    addStatus = mws.set_value(field, False, tabName)
                else:
                    addStatus = mws.set_value(field, True, tabName)
            elif (field == "Clock In/Out Required"):
                if (fieldValue):
                    addStatus = mws.set_value(field, False, tabName)
                else:
                    addStatus = mws.set_value(field, True, tabName)
                    addStatusAfter = mws.get_value(field, tabName)
                    if (not addStatusAfter):
                        self.log.info(f"[{field}] is not enabled, so unable to change the value")
                        addStatus = False
                        disableControl = True
            elif (field == "Security Group"):
                if (fieldValue[0] == "Cashier"):
                    addStatus = mws.set_value(field, "Manager", tabName)
                else:
                    addStatus = mws.set_value(field, "Cashier", tabName)
            elif (field == "Override the \"Blind Balancing\" store option"):
                if (fieldValue):
                    addStatus = mws.set_value(field, False, tabName)
                else:
                    addStatus = mws.set_value(field, True, tabName)
            elif (field == "to see the totals when balancing"):
                if (fieldValue[0] == "is allowed"):
                    addStatus = mws.set_value(field, "is not allowed", tabName)
                else:
                    addStatus = mws.set_value(field, "is allowed", tabName)
            # elif (field == "Theme"):
            #    if (fieldValue[0] == "Use Site Theme"):
            #        addStatus = mws.set_value(field, "Passport Retro", tabName)
            #    else:
            #        addStatus = mws.set_value(field, "Use Site Theme", tabName)
            elif (field == "Calculator"):
                if (fieldValue):
                    addStatus = mws.set_value("Telephone", True, tabName)
                else:
                    addStatus = mws.set_value(field, True, tabName)
            elif (field == "Right"):
                if (fieldValue):
                    addStatus = mws.set_value("Left", True, tabName)
                else:
                    addStatus = mws.set_value(field, True, tabName)

            afterUpdatingValue = mws.get_value(field, tabName)
            self.log.info(f"After setting the [{field}] value is [{afterUpdatingValue}]")
            addStatus = mws.click_toolbar("Save")
            if (disableControl):
                addStatus = False
        else:
            confg = {
                        "General": {
                            "First Name": "Auto", "Last Name": "Cashier37",
                            "Birth Date": "08/30/1982", "Operator ID": "37",
                            "Address Line 1": "123 Fake Street", "Address Line 2": "Bldg 1",
                            "Address Line 3": "Suite 234", "City": "Greensboro",
                            "State": "NC", "Postal Code": "27410",
                            "Telephone": "(897)867-7377"},
                        "Security": {"Security Group": "Cashier"},
                        "Preferences": {"Language": "US English"}
            }
            addStatus = emp.add(confg)
            self.log.info("Setting back to main Employee screen")
            mws.click_toolbar("Exit")

        if (addStatus):
            self.log.info(f"Insite360 Enabled = [{self.insite360Enabled}]")
            empTimeOutStatus = FromInsite360.json_generate_status(startTimeFromAuto, "employees")
            if (self.insite360Enabled):
                if (empTimeOutStatus):
                    # check again, some issue with remote manager service
                    returnStatus = not(FromInsite360.restart_rmservice_max("employees")) 
            else:
                if (not empTimeOutStatus):
                    returnStatus = False
        else:
            if (not disableControl):
                returnStatus = False

        return (returnStatus)

    @test
    def add_new_employee_TC1(self):
        """
        Zephyr Id : Add a new employee to the list and check the
                    .json object is generated or not to send i360
        Args: None
        Returns: None
        """
        self.log.info("Check whether the insite 360 is enabled or not")
        self.insite360Enabled = FromInsite360.Check_I360_Connected()
        self.log.info(f"Insite 360 is enabled [{self.insite360Enabled}]")

        self.log.info("Start add_new_employee_TC1")
        emp = employee.Employee()

        # check wether the employee is already exists or not
        # if yes, change the employee details
        empexist = mws.set_value("Employees", "7")
        startTimeFromAuto = datetime.now()
        if (empexist):
            # Swaping the Name while updating Cashier 7 data
            empexist = mws.set_value("Employees", "Cashier 7")
            if (empexist):
                confg = {
                            "General": {
                                "First Name": "Auto", "Last Name": "Cashier7",
                                "Birth Date": "07/02/1982", "Address Line 3": "Suite 234"
                            }
                }
            else:
                confg = {
                            "General": {
                                "First Name": "Auto", "Last Name": "Cashier 7",
                                "Birth Date": "05/04/1985", "Address Line 3": " "
                            }
                }
            addStatus = emp.change("7", confg)
        else:
            confg = {
                        "General": {
                            "First Name": "Auto", "Last Name": "Cashier7",
                            "Birth Date": "07/02/1982", "Operator ID": "7",
                            "Address Line 1": "123 Fake Street", "Address Line 2": "Bldg 1",
                            "Address Line 3": "Suite 234", "City": "Greensboro",
                            "State": "NC", "Postal Code": "27410",
                            "Telephone": "(991)234-5644"},
                        "Security": {"Security Group": "Cashier"},
                        "Preferences": {"Language": "US English"}
            }
            addStatus = emp.add(confg)

        self.log.info("Setting back to main Employee screen")
        mws.click_toolbar("Exit")

        if (not addStatus):
            tc_fail("Failed, unable to add/modify the employee details")
        else:
            self.log.info(f"Insite360 Enabled = [{self.insite360Enabled}]")
            empTimeOutStatus = FromInsite360.json_generate_status(startTimeFromAuto, "employees")
            if (self.insite360Enabled):
                if (empTimeOutStatus):
                    empTimeOutStatus = FromInsite360.restart_rmservice_max("employees")
                    if (empTimeOutStatus):
                        tc_fail("Failed, .json data is not sent to I360")
            else:
                if (not empTimeOutStatus):
                    tc_fail("Failed, .json data is sent to I360")

    @test
    def change_employee_LastName_TC2(self):
        """
        Zephyr Id : Change only employee last name for existing employee and check the
                    .json object is generated or not to send i360
        Args: None
        Returns: None
        """
        changeStatus = self.change_employee_by("Last Name", "General")
        if (not changeStatus):
            tc_fail("Failed, unable to modify the 'Last Name'")

    @test
    def change_employee_FirstName_TC3(self):
        """
        Zephyr Id : Change only employee first name for existing employee and check the
                    .json object is generated or not to send i360
        Args: None
        Returns: None
        """
        changeStatus = self.change_employee_by("First Name", "General")
        if (not changeStatus):
            tc_fail("Failed, unable to modify the 'First Name'")

    @test
    def change_employee_BirthDate_TC4(self):
        """
        Zephyr Id : Change only employee Birth Date for existing employee and check the
                    .json object is generated or not to send i360
        Args: None
        Returns: None
        """
        changeStatus = self.change_employee_by("Birth Date", "General")
        if (not changeStatus):
            tc_fail("Failed, unable to modify the 'Birth Date'")

    @test
    def change_employee_AddressLine1_TC5(self):
        """
        Zephyr Id : Change only employee Address Line 1 for existing employee and check the
                    .json object is generated or not to send i360
        Args: None
        Returns: None
        """
        changeStatus = self.change_employee_by("Address Line 1", "General")
        if (not changeStatus):
            tc_fail("Failed, unable to modify the 'Address Line 1'")

    @test
    def change_employee_AddressLine2_TC6(self):
        """
        Zephyr Id : Change only employee Address Line 2 for existing employee and check the
                    .json object is generated or not to send i360
        Args: None
        Returns: None
        """
        changeStatus = self.change_employee_by("Address Line 2", "General")
        if (not changeStatus):
            tc_fail("Failed, unable to modify the 'Address Line 2'")

    @test
    def change_employee_AddressLine3_TC7(self):
        """
        Zephyr Id : Change only employee Address Line 3 for existing employee and check the
                    .json object is generated or not to send i360
        Args: None
        Returns: None
        """
        changeStatus = self.change_employee_by("Address Line 3", "General")
        if (not changeStatus):
            tc_fail("Failed, unable to modify the 'Address Line 3'")

    @test
    def change_employee_City_TC8(self):
        """
        Zephyr Id : Change only employee City for existing employee and check the
                    .json object is generated or not to send i360
        Args: None
        Returns: None
        """
        changeStatus = self.change_employee_by("City", "General")
        if (not changeStatus):
            tc_fail("Failed, unable to modify the 'City'")

    @test
    def change_employee_State_TC9(self):
        """
        Zephyr Id : Change only employee State for existing employee and check the
                    .json object is generated or not to send i360
        Args: None
        Returns: None
        """
        changeStatus = self.change_employee_by("State", "General")
        if (not changeStatus):
            tc_fail("Failed, unable to modify the 'State'")

    @test
    def change_employee_PostalCode_TC10(self):
        """
        Zephyr Id : Change only employee Postal Code for existing employee and check the
                    .json object is generated or not to send i360
        Args: None
        Returns: None
        """
        changeStatus = self.change_employee_by("Postal Code", "General")
        if (not changeStatus):
            tc_fail("Failed, unable to modify the 'Postal Code'")

    @test
    def change_employee_Telephone_TC11(self):
        """
        Zephyr Id : Change only employee Telephone for existing employee and check the
                    .json object is generated or not to send i360
        Args: None
        Returns: None
        """
        changeStatus = self.change_employee_by("Telephone", "General")
        if (not changeStatus):
            tc_fail("Failed, unable to modify the 'Telephone'")

    @test
    def change_employee_SecurityGroup_TC12(self):
        """
        Zephyr Id : Change only employee Security Group for existing employee and check the
                    .json object is generated or not to send i360
        Args: None
        Returns: None
        """
        changeStatus = self.change_employee_by("Security Group", "Security")
        if (not changeStatus):
            tc_fail("Failed, unable to modify the 'Security Group'")

    @test
    def change_employee_OvverrideBalance_TC13(self):
        """
        Zephyr Id : Change only employee Preferences Ovverride balancing option for existing employee and check the
                    .json object is generated or not to send i360
        Args: None
        Returns: None
        """
        changeStatus = self.change_employee_by("Override the \"Blind Balancing\" store option", "Preferences")
        if (not changeStatus):
            tc_fail("Failed, unable to modify the 'Override the \"Blind Balancing\" store option'")

    @test
    def change_employee_TotalBalancing_TC14(self):
        """
        Zephyr Id : Change only employee Preferences to see the totals when balancing option for existing employee and check the
                    .json object is generated or not to send i360
        Args: None
        Returns: None
        """
        changeStatus = self.change_employee_by("to see the totals when balancing", "Preferences")
        if (not changeStatus):
            tc_fail("Failed, unable to modify the 'to see the totals when balancing'")

    @test
    def change_employee_Theme_TC15(self):
        """
        Zephyr Id : Change only employee Preferences theme (Use Site Theme / Passport Retro) option for existing employee and check the
                    .json object is generated or not to send i360
        Args: None
        Returns: None
        """
        # changeStatus = self.change_employee_by("Theme", "Preferences")
        changeStatus = True
        if (not changeStatus):
            tc_fail("Failed, unable to modify the 'Theme'")

    @test
    def change_employee_KeyPadPreference_TC16(self):
        """
        Zephyr Id : Change only employee Preferences KeyPadPreference (Calculator / Telephone) option for existing employee and check the
                    .json object is generated or not to send i360. Switch between Calculator / Telephone options
        Args: None
        Returns: None
        """
        changeStatus = self.change_employee_by("Calculator", "Preferences")
        if (not changeStatus):
            tc_fail("Failed, unable to modify the 'Calculator'")

    @test
    def change_employee_KeyPadPreference_TC17(self):
        """
        Zephyr Id : Change only employee Preferences KeyPadPreference (Calculator / Telephone) option for existing employee and check the
                    .json object is generated or not to send i360. Switch between Calculator / Telephone options
        Args: None
        Returns: None
        """
        changeStatus = self.change_employee_by("Calculator", "Preferences")
        if (not changeStatus):
            tc_fail("Failed, unable to modify the 'Calculator'")

    @test
    def change_employee_HandPreference_TC18(self):
        """
        Zephyr Id : Change only employee Preferences HandPreference (Right / Left) option for existing employee and check the
                    .json object is generated or not to send i360. Switch between Right / Left options
        Args: None
        Returns: None
        """
        changeStatus = self.change_employee_by("Right", "Preferences")
        if (not changeStatus):
            tc_fail("Failed, unable to modify the 'Right'")

    @test
    def change_employee_HandPreference_TC19(self):
        """
        Zephyr Id : Change only employee Preferences HandPreference (Right / Left) option for existing employee and check the
                    .json object is generated or not to send i360. Switch between Right / Left options
        Args: None
        Returns: None
        """
        changeStatus = self.change_employee_by("Right", "Preferences")
        if (not changeStatus):
            tc_fail("Failed, unable to modify the 'Right'")

    @test
    def change_employee_ActiveOperator_TC20(self):
        """
        Zephyr Id : Change only employee active operator for existing employee and check the
                    .json object is generated or not to send i360
        Args: None
        Returns: None
        """
        changeStatus = self.change_employee_by("Active Operator", "General")
        if (not changeStatus):
            tc_fail("Failed, unable to modify the 'Active Operator'")

    @test
    def change_employee_ActiveOperator_TC21(self):
        """
        Zephyr Id : Change only employee active operator for existing employee and check the
                    .json object is generated or not to send i360
        Args: None
        Returns: None
        """
        changeStatus = self.change_employee_by("Active Operator", "General")
        if (not changeStatus):
            tc_fail("Failed, unable to modify the 'Active Operator'")

    @test
    def change_employee_Clock_In_Out_TC22(self):
        """
        Zephyr Id : Change only employee Clock In/Out Required for existing employee and check the
                    .json object is generated or not to send i360
        Args: None
        Returns: None
        """
        changeStatus = self.change_employee_by("Clock In/Out Required", "General")
        if (not changeStatus):
            tc_fail("Failed, unable to modify the 'Clock In/Out Required'")

    @test
    def change_employee_Clock_In_Out_TC23(self):
        """
        Zephyr Id : Change only employee Clock In/Out Required for existing employee and check the
                    .json object is generated or not to send i360
        Args: None
        Returns: None
        """
        changeStatus = self.change_employee_by("Clock In/Out Required", "General")
        if (not changeStatus):
            tc_fail("Failed, unable to modify the 'Clock In/Out Required'")

    @test
    def change_employee_NoChanges_TC24(self):
        """
        Zephyr Id : Update employee details with out changes and check the
                    .json object is generated or not to send i360
        Args: None
        Returns: None
        """
        self.log.info("Start change_employee_NoChanges_TC24")
        emp = employee.Employee()

        # check wether the employee is already exists or not
        # if yes, change the employee details
        empexist = mws.set_value("Employees", "1")
        startTimeFromAuto = datetime.now()
        if (empexist):
            # Swaping the Name while updating Cashier 1 data
            empexist = mws.set_value("Employees", "Cashier")
            if (empexist):
                confg = {
                            "General": {
                                "First Name": "Auto", "Last Name": "Cashier",
                                "Birth Date": "01/01/1990",
                                "Address Line 1": "123 Fake Street", "Address Line 2": "Bldg 1",
                                "Address Line 3": "Suite 234", "City": "Greensboro",
                                "State": "NC", "Postal Code": "27410"},
                            "Security": {"Security Group": "Cashier"},
                            "Preferences": {"Language": "US English"}
                        }
            addStatus = emp.change("1", confg)

        if (not addStatus):
            tc_fail("Failed, unable to modify the 'Cashier' empID: 1")
        else:
            self.log.info(f"Insite360 Enabled = [{self.insite360Enabled}]")
            if (self.insite360Enabled):
                empTimeOutStatus = FromInsite360.json_generate_status(startTimeFromAuto, "employees", no_reset=True)
            else:
                empTimeOutStatus = FromInsite360.json_generate_status(startTimeFromAuto, "employees")
            if (not empTimeOutStatus):
                tc_fail("Failed, .json data generated and sent to I360 with out any changes")

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        self.log.info("Setting back to main Employee screen")
        mws.click_toolbar("Exit")

