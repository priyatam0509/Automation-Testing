"""
    File name: EmpMng_IS360_ValidateFromI360.py
    Tags:
    StoryID: STARFINCH-3477
    Description: Employee configuration command received from Insite360 and
                 Validate at Passport.
    Author: Pavan Kumar Kantheti
    Date created: 2020-04-28 18:37:07
    Date last modified:
    Python Version: 3.7
"""
from app.features import insite360web
from Scripts.features import FromInsite360
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from datetime import datetime
import sys
import logging


class EmpMng_IS360_ValidateFromI360():
    """
        Description: Test class that provides an interface for testing.
    """
    insite360_enabled = False
    timeout_min = 3
    # Generate the operator ID based on the current date.
    operator_id = datetime.now().strftime("%Y%m%d%H")
    proceed_to_test = False

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
    def add_new_employee_TC1(self):
        """
        Zephyr Id : Add a new employee from insite360 and validate the
                    .json object at passport
        Args: None
        Returns: None
        """
        try:
            connect_status = insite360web.connect()
            self.log.info(f"Insite360 connection status = [{connect_status}]")
            if not (connect_status):
                tc_fail("Failed, Unable to connect insite360.")
            else:
                login_status = insite360web.login('automationpassport@gmail.com', 'pmcs382000')
                self.log.info(f"Insite360 login status = [{login_status}]")
                if not(login_status):
                    tc_fail("Failed, Unable to login insite360.")
                else:
                    self.add_employee()
        except:
            self.log.error(f"add_new_employee_TC1 - [{sys.exc_info()[0]}]")
            tc_fail("Failed, unable to add the new employee/ update assigned stores")

    @test
    def change_employee_LastName_TC2(self):
        """
        Zephyr Id : Change only employee last name at Insite360 for existing employee and check the
                    .json object is received from Insite360 or not
        Args: None
        Returns: None
        """
        self.update_employee("Last Name")

    @test
    def change_employee_FirstName_TC3(self):
        """
        Zephyr Id : Change only employee first name at Insite360 for existing employee and check the
                    .json object is received from Insite360 or not
        Args: None
        Returns: None
        """
        self.update_employee("First Name")

    @test
    def change_employee_BirthDate_TC4(self):
        """
        Zephyr Id : Change only employee Birth Date at Insite360 for existing employee and check the
                    .json object is received from Insite360 or not
        Args: None
        Returns: None
        """
        self.update_employee("Birth Date")

    @test
    def change_employee_AddressLine1_TC5(self):
        """
        Zephyr Id : Change only employee Address Line 1 at Insite360 for existing employee and check the
                    .json object is received from Insite360 or not
        Args: None
        Returns: None
        """
        self.update_employee("Address Line 1")

    @test
    def change_employee_AddressLine2_TC6(self):
        """
        Zephyr Id : Change only employee Address Line 2 at Insite360 for existing employee and check the
                    .json object is received from Insite360 or not
        Args: None
        Returns: None
        """
        self.update_employee("Address Line 2")

    @test
    def change_employee_AddressLine3_TC7(self):
        """
        Zephyr Id : Change only employee Address Line 3 at Insite360 for existing employee and check the
                    .json object is received from Insite360 or not
        Args: None
        Returns: None
        """
        self.update_employee("Address Line 3")

    @test
    def change_employee_City_TC8(self):
        """
        Zephyr Id : Change only employee City at Insite360 for existing employee and check the
                    .json object is received from Insite360 or not
        Args: None
        Returns: None
        """
        self.update_employee("City")

    @test
    def change_employee_State_TC9(self):
        """
        Zephyr Id : Change only employee State at Insite360 for existing employee and check the
                    .json object is received from Insite360 or not
        Args: None
        Returns: None
        """
        self.update_employee("State")

    @test
    def change_employee_PostalCode_TC10(self):
        """
        Zephyr Id : Change only employee Postal Code at Insite360 for existing employee and check the
                    .json object is received from Insite360 or not
        Args: None
        Returns: None
        """
        self.update_employee("Postal Code")

    @test
    def change_employee_Phone_TC11(self):
        """
        Zephyr Id : Change only employee Phone at Insite360 for existing employee and check the
                    .json object is received from Insite360 or not
        Args: None
        Returns: None
        """
        self.update_employee("Phone")

    @test
    def change_employee_SecurityGroup_TC12(self):
        """
        Zephyr Id : Change only employee Security Group at Insite360 for existing employee and check the
                    .json object is received from Insite360 or not
        Args: None
        Returns: None
        """
        self.update_employee("Security Group")

    @test
    def change_employee_TotalBalancing_TC13(self):
        """
        Zephyr Id : Change only employee Preferences "View Total On Blind Balance" option at Insite360 for existing employee and check the .json object is received from Insite360 or not
        Swith between "Allow"/"Not Allow"
        Args: None
        Returns: None
        """
        self.update_employee("View Total On Blind Balance")

    @test
    def change_employee_TotalBalancing_TC14(self):
        """
        Zephyr Id : Change only employee Preferences "View Total On Blind Balance" option at Insite360 for existing employee and check the .json object is received from Insite360 or not
        Swith between "Allow"/"Not Allow"
        Args: None
        Returns: None
        """
        self.update_employee("View Total On Blind Balance")

    @test
    def change_employee_OvverrideBalance_TC15(self):
        """
        Zephyr Id : Change only employee Preferences Ovverride balancing option at Insite360 for existing employee 
                    and check the .json object is received from Insite360 or not
        Args: None
        Returns: None
        """
        self.update_employee("Override the Blind Balancing store option")

    @test
    def change_employee_Theme_TC16(self):
        """
        Zephyr Id : Change only employee Preferences theme (Use Site Theme / Passport Retro) option at Insite360 for existing employee and check the .json object is received from Insite360 or not
        Args: None
        Returns: None
        """
        self.update_employee("Theme")

    @test
    def change_employee_KeyPadPreference_TC17(self):
        """
        Zephyr Id : Change only employee Preferences KeyPadPreference (Calculator / Telephone) option at 
        Insite360 for existing employee and check the .json object is received from Insite360 or not. 
        Switch between Calculator / Telephone options
        Args: None
        Returns: None
        """
        self.update_employee("Keypad Calculator")

    @test
    def change_employee_KeyPadPreference_TC18(self):
        """
        Zephyr Id : Change only employee Preferences KeyPadPreference (Calculator / Telephone) option at 
        Insite360 for existing employee and check the .json object is received from Insite360 or not. 
        Switch between Calculator / Telephone options
        Args: None
        Returns: None
        """
        self.update_employee("Keypad Calculator")

    @test
    def change_employee_HandPreference_TC19(self):
        """
        Zephyr Id : Change only employee Preferences HandPreference (Right / Left) option at Insite360 for 
        existing employee and check the .json object is received from Insite360 or not. 
        Switch between Right / Left options
        Args: None
        Returns: None
        """
        self.update_employee("Hand Preference Right")

    @test
    def change_employee_HandPreference_TC20(self):
        """
        Zephyr Id : Change only employee Preferences HandPreference (Right / Left) option at Insite360 for 
        existing employee and check the .json object is received from Insite360 or not. 
        Switch between Right / Left options
        Args: None
        Returns: None
        """
        self.update_employee("Hand Preference Right")

    @test
    def change_employee_Clock_In_Out_TC21(self):
        """
        Zephyr Id : Change only employee Clock In/Out Required at Insite360 for existing employee and check the
                    .json object is received from Insite360 or not
        Args: None
        Returns: None
        """
        self.update_employee("Clock InOut Required")

    @test
    def change_employee_Clock_In_Out_TC22(self):
        """
        Zephyr Id : Change only employee Clock In/Out Required at Insite360 for existing employee and check the
                    .json object is received from Insite360 or not
        Args: None
        Returns: None
        """
        self.update_employee("Clock InOut Required")

    @test
    def unChange_employee_withCancel_TC23(self):
        """
        Zephyr Id : Unchange the values of the employee and click on cancel button and check
                    .json object is received from Insite360 or not
        Args: None
        Returns: None
        """
        self.update_employee("")

    @test
    def unChange_employee_withCancel_TC24(self):
        """
        Zephyr Id : Unchange the values of the employee and click on Save button and check
                    .json object is received from Insite360 or not
        Args: None
        Returns: None
        """
        self.update_employee("", True)

    @test
    def change_employee_ActiveOperator_TC25(self):
        """
        Zephyr Id : Change only employee active operator for existing employee and check the
                    .json object is received from Insite360 or not
        Args: None
        Returns: None
        """
        self.update_employee("Activate")

    @test
    def change_employee_ActiveOperator_TC26(self):
        """
        Zephyr Id : Change only employee active operator for existing employee and check the
                    .json object is received from Insite360 or not
        Args: None
        Returns: None
        """
        self.update_employee("Activate")

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        insite360web.close()
        FromInsite360.DeleteRMSLog()

    def add_employee(self):
        """
        Adding a new employee at insite360.
        """
        try:
            self.log.info("Check wether the insite 360 is enabled or not")
            insite360_enabled = FromInsite360.Check_I360_Connected()
            self.log.info(f"Insite 360 is enabled [{insite360_enabled}]")

            if not(insite360_enabled):
                FromInsite360.insite360_configure()
                self.proceed_to_test = FromInsite360.Register_UnRegister_Insite360(insite360_enabled)
                insite360_enabled = FromInsite360.Check_I360_Connected()
                self.log.info(f"After Register_UnRegister_Insite360, latest Insite 360 is enabled [{insite360_enabled}]")
                self.log.info("Calling refresh_site_after_connect method")
                try:
                    if (insite360web.refresh_site_after_connect()):
                        tc_fail("Failed, Site is not Online, try after some time...")
                except:
                    self.log.error("Issue with local function..")
                self.log.info("After register validate at passport.")

            startime_from_script = datetime.now()
            status = False

            addStatus = insite360web.is_employee_exists_by_id(self.operator_id)
            if (addStatus == 0):
                # Add new employee with id operator ID
                config = {
                            "First Name" : "Auto", "Last Name" : "Manager",
                            "Operator Id" : "", "Birth Date" : "07-02-1982",
                            "Address Line 1" : "786 Fake Street", "Address Line 2" : "Bldg 1",
                            "Address Line 3" : "Suite 234", "City" : "Greensboro",
                            "State" : "NORTH CAROLINA", "Postal Code" : "27410",
                            "Phone" : "(897) 867-7737", "Security Group" : "Manager",
                            "Assigned Stores" : "TestAutoSite1", "Clock InOut Required" : "False",
                            "Override the Blind Balancing store option" : "True",
                            "Language" : "US English", "Theme" : "Passport Retro",
                            "Keypad Calculator" : "True", "Hand Preference Left" : "True"
                        }
                status = insite360web.add_new_employee(self.operator_id, config)
            elif (addStatus == 1):
                # Check and update the assigned stores value
                self.proceed_to_test = True
                self.log.info("Employee already exist(s) in insite360.")
                self.log.info("Check and updated the 'Assigned stores' value")
                status = insite360web.set_assigned_store_validate(self.operator_id, "TestAutoSite1")
                # Check the command received from Insite360 or not? if not modify the test auto site

            if (status):
                self.proceed_to_test = True
                emp_timeout_status = FromInsite360.JSONReceivedTimeOutStatus("employees", startime_from_script, self.timeout_min, 60, self.operator_id)
                if (emp_timeout_status and addStatus == 0):
                    tc_fail("Failed, .json data command not received from I360/ event status not sent to I360.")
            else:
                tc_fail("Failed, Unable to add/update the employee from insite360.")
        except:
            self.log.error(f"add_new_employee_TC1 - [{sys.exc_info()[0]}]")
            tc_fail("Failed, unable to add new employee/ update assigned stores")

    def update_employee(self, field_name, on_save=False):
        """
        Update the employee details based on the field_name and on_save parameters
        Args : field_name and on_save
        Return: None
        """
        if (self.proceed_to_test):
            data_check = True
            try:
                startime_from_script = datetime.now()
                if (field_name == ""):
                    changeStatus = insite360web.update_employee(self.operator_id, field_name, "TestAutoSite1", on_save)
                else:
                    if (field_name == 'Activate'):
                        changeStatus = True
                        data_check = False
                    else:
                        changeStatus = insite360web.update_employee(self.operator_id, field_name, "TestAutoSite1")
                if (not changeStatus):
                    tc_fail("Failed, unable to modify the '{field_name}' at Insite360")
                else:
                    if (data_check):
                        emp_timeout_status = FromInsite360.JSONReceivedTimeOutStatus("employees", startime_from_script, self.timeout_min, 60, self.operator_id)
                        if not(field_name == ""):
                            if (emp_timeout_status):
                                tc_fail("Failed, .json data not generated/command received from I360/ event status sent to I360.")
            except:
                self.log.error(f"update_employee [{field_name}] - [{sys.exc_info()[0]}]")
                tc_fail("Failed, .json data command received from I360/ event status sent to I360.")
        else:
            self.log.error(f"update_employee [{field_name}] - unable to proceed...")
            tc_fail(f"Failed, update_employee [{field_name}] - unable to proceed...")

