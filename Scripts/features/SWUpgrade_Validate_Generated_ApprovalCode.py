"""
    File name: SWUpgrade_Validate_Generated_ApprovalCode.py
    Tags:
    Description: SL-1685: Entering generated upgrade code on upgrade blocker screen
    Brand: Concord
    Author: Paresh
    Date created: 2020-13-04 19:11:00
    Date last modified: 
    Python Version: 3.7
"""

import logging, pywinauto, time
from app import Navi, mws
from datetime import datetime, timedelta
from app.util import constants
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from Scripts.features import SWUpgrade_ActivationTool_Verify_UI

activation_tool_path = constants.TESTING_TOOLS + r'\HDActivation.exe'

Controls = {
            "Software Upgrade Approval Code": "Software Upgrade Approval Code",
            "Generate Approval Code": "Generate Approval Code",
            "Clear": "Clear",
            "Gilbarco ID": "Edit5",
            "Approval Code 1": "Edit3",
            "Approval Code 2": "Edit4",
            "Approval Code 3": "Edit2",
            "Approval Code 4": "Edit1"
        }

class SWUpgrade_Validate_Generated_ApprovalCode():
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
        """
        Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        # Update null value for gilbarco id in DB
        SWUpgrade_ActivationTool_Verify_UI.connect_mws_db(data_value='', id='10352')

    def wait_for_msg(self, exp_msg):
        """
        This is helper method to wait till message pops up in mws top bar
        """
        start_time = time.time()
        while time.time() - start_time < 30:
            get_message = mws.get_top_bar_text()
            if exp_msg in get_message:
                return True

        return False

    @test
    def verify_ui_not_visible_for_valid_date(self):
        """
        Testlink Id: SL-1685: Entering generated upgrade code on upgrade blocker screen
		Description: Verify software upgrade activation tool Ui is not visible if date is today+365/today+350 days in DB
        Args: None
        Returns: None
        """

        date = datetime.strftime(datetime.now() - timedelta(-365), '%m-%d-%Y')
        
        # Update today+365 days date value in DB
        if not SWUpgrade_ActivationTool_Verify_UI.connect_mws_db(data_value=date):
            tc_fail("Unable to connect with DB and failed to update the data")

        # Verify software upgrade activation tool ui is not visible
        Navi.navigate_to("Software Upgrade Manager")

        if not mws.click_toolbar("Install Software"):
            tc_fail("Install software button is not visible")
        
        exp_msg = "While installing updates all dispensers and registers will be out of service."
        self.wait_for_msg(exp_msg)
        
        if exp_msg not in mws.get_top_bar_text():
            tc_fail("Required Message is not displayed")
        
        if not mws.click_toolbar("No"):
            tc_fail("Unable to click on No button")

        date1 = datetime.strftime(datetime.now() - timedelta(-350), '%m-%d-%Y')

        # Update today+350 days date value in DB
        if not SWUpgrade_ActivationTool_Verify_UI.connect_mws_db(data_value=date1):
            tc_fail("Unable to connect with DB and failed to update the data")
        
        # Verify software upgrade activation tool ui is not visible
        if not mws.click_toolbar("Install Software"):
            tc_fail("Install software button is not visible")
        
        exp_msg = "While installing updates all dispensers and registers will be out of service."
        self.wait_for_msg(exp_msg)

        if exp_msg not in mws.get_top_bar_text():
            tc_fail("Message is not displayed")
        
        if not mws.click_toolbar("No"):
            tc_fail("Unable to click on No button")

        mws.click_toolbar("Exit")

        # Wait for 2 second to complete process
        time.sleep(2)

        return True
    
    @test
    def verify_ui_visible_for_invalid_date(self):
        """
        Testlink Id: SL-1685: Entering generated upgrade code on upgrade blocker screen
		Description: Verify software upgrade activation tool Ui is visible if date is today+370 days in DB
        Args: None
        Returns: None
        """

        date = datetime.strftime(datetime.now() - timedelta(-370), '%m-%d-%Y')
        
        # Update today+370 days date value in DB
        if not SWUpgrade_ActivationTool_Verify_UI.connect_mws_db(data_value=date):
            tc_fail("Unable to connect with DB and failed to update the data")

        # Verify software upgrade activation tool ui is not visible
        Navi.navigate_to("Software Upgrade Manager")

        if not mws.click_toolbar("Install Software"):
            tc_fail("Install software button is not visible")
        
        if not mws.click("GVR ID"):
            tc_fail("GVR ID text box is not visible")
        
        for i in range(1, 5):
            if not mws.click("Approval Code"+str(i)):
                tc_fail("Approval Code text box is not visible")

        return True

    @test
    def validation_message_for_empty_gvrID(self):
        """
        Testlink Id: SL-1685: Entering generated Approval Code on upgrade blocker screen
		Description: Verify error message for empty GVR ID
        Args: None
        Returns: None
        """

        # Validate error message for empty GVR ID
        if not mws.set_value("GVR ID", ""):
            tc_fail("Unable to set value for GVR ID")

        if not mws.click("Install"):
            tc_fail("Unable to click on install button")
        
        exp_msg = "GVR ID is a required field."
        self.wait_for_msg(exp_msg)
                
        if exp_msg not in mws.get_top_bar_text():
            tc_fail("Message is not displayed")
        
        if not mws.click_toolbar("OK"):
            tc_fail("Unable to click on OK button")

        return True
    
    @test
    def validation_message_for_invalid_gvrID(self):
        """
        Testlink Id: SL-1685: Entering generated Approval Code on upgrade blocker screen
		Description: Verify error message for invalid GVR ID
        Args: None
        Returns: None
        """

        # Validate error message for invalid GVR ID
        if not mws.set_value("GVR ID", "12345"):
            tc_fail("Unable to set value for GVR ID")

        if not mws.click("Install"):
            tc_fail("Unable to click on install button")
        
        exp_msg = "GVR ID must be 6 digits."
        self.wait_for_msg(exp_msg)

        if exp_msg not in mws.get_top_bar_text():
            tc_fail("Message is not displayed")
        
        if not mws.click_toolbar("OK"):
            tc_fail("Unable to click on OK button")

        return True
    
    @test
    def validation_message_for_empty_approvalcode(self):
        """
        Testlink Id: SL-1685: Entering generated Approval Code on upgrade blocker screen
		Description: Verify error message for empty approval code
        Args: None
        Returns: None
        """
        
        if not mws.set_value("GVR ID", "123456"):
            tc_fail("Unable to set value for GVR ID")

        # Validate error message for empty approval code
        if not mws.set_value("Approval Code1", ""):
            tc_fail("Unable to set value for approval code")

        if not mws.click("Install"):
            tc_fail("Unable to click on install button")
        
        exp_msg = "Approval Code is a required field."
        self.wait_for_msg(exp_msg)

        if exp_msg not in mws.get_top_bar_text():
            tc_fail("Required Message is not displayed")
        
        if not mws.click_toolbar("OK"):
            tc_fail("Unable to click on OK button")

        return True
    
    @test
    def validation_message_for_invalid_approvalcode(self):
        """
        Testlink Id: SL-1685: Entering generated Approval Code on upgrade blocker screen
		Description: Verify error message for invalid approval code
        Args: None
        Returns: None
        """
        
        # Validate error message for invalid approval code
        for i in range(4):
            if not mws.set_text(f"Approval Code{i+1}", "1234"):
                tc_fail("Unable set value for approval code")

        if not mws.click("Install"):
            tc_fail("Unable to click on install button")
        
        exp_msg = "Approval Code is incorrect. Please verify the Approval Code and re-enter"
        self.wait_for_msg(exp_msg)
        
        if exp_msg not in mws.get_top_bar_text():
            tc_fail("Message is not displayed")
        
        if not mws.click_toolbar("OK"):
            tc_fail("Unable to click on OK button")

        return True
    
    @test
    def validation_message_for_16digit_approvalcode(self):
        """
        Testlink Id: SL-1685: Entering generated Approval Code on upgrade blocker screen
		Description: Verify error message for 16 digit approval code
        Args: None
        Returns: None
        """
        
        # Validate error message for 16 digit approval code
        
        for i in range(3):
            if not mws.set_text(f"Approval Code{i+1}", "1234"):
                tc_fail("Unable set value for approval code")
        
        if not mws.set_text("Approval Code4", "123"):
                tc_fail("Unable set value for approval code")

        if not mws.click("Install"):
            tc_fail("Unable to click on install button")
        
        exp_msg = "Approval Code must be 16 digits"

        self.wait_for_msg(exp_msg)
        
        if exp_msg not in mws.get_top_bar_text():
            tc_fail("Message is not displayed")
        
        if not mws.click_toolbar("OK"):
            tc_fail("Unable to click on OK button")

        return True

    @test
    def validation_for_valid_approvalcode(self):
        """
        Testlink Id: SL-1685: Entering generated Approval Code on upgrade blocker screen
		Description: Verify no error message is displayed if we are entering valid approval code
        Args: None
        Returns: None
        """

        # Open HD activation tool
        hdpassportactivation = pywinauto.application.Application().start(activation_tool_path)
        app = hdpassportactivation['Passport Activation Utility']
        app.wait('ready', 5)

        # Verify Software Upgrade Aprroval Code radio button is visible
        app[Controls["Software Upgrade Approval Code"]].click()
        time.sleep(.5)
        
        # Enter gilbarco id
        app[Controls["Gilbarco ID"]].type_keys("123456")
        time.sleep(.5)
        if app[Controls["Gilbarco ID"]].texts()[0] != "123456":
            tc_fail("Unable to find gilbarco id text box")

        # Generate approval code
        app[Controls["Generate Approval Code"]].click()
        time.sleep(.5)
        
        site_code = [app[Controls[f"Approval Code {i}"]].texts()[0] for i in range(1,5) ]
        hdpassportactivation.kill()
        
        # Enter Site Code in MWS
        for i in range(4):
            if not mws.set_text(f"Approval Code{i+1}", site_code[i]):
                tc_fail("Unable to set approval code in MWS")
        
        if not mws.click("Install"):
            tc_fail("Unable to click on install button")
        
        if not mws.click_toolbar("No"):
            tc_fail("Unable to click on No button")

        return True

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        pass