"""
    File name: HD_Activation_Test.py
    Tags:
    Description: SL-1865/SL-1877 - Consolidate feature bundles
    Brand:  NA
    Author: Paresh
    Date created: 2020-19-05 13:31:37
    Date last modified: 
    Python Version: 3.7
"""

import logging, pywinauto, time
from app.util import constants, system
from pywinauto import Application
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from pywinauto.keyboard import send_keys
from app.features import feature_activation

COMMON_BUNDLES = ["Base Passport", "Enhanced Store", "Enhanced Reporting", "Advanced Merchandising",
                "Employee Management", "Enhanced Card Services", "Prepaid Card Services", "Car Wash"]

activation_tool_path = constants.TESTING_TOOLS + r'\HDActivation.exe'

controls = {
    "Site Key 1": "Edit7",
    "Site Key 2": "Edit6",
    "Site Key 3": "Edit5",
    "Site Code 1": "Edit3",
    "Site Code 2": "Edit4",
    "Site Code 3": "Edit2",
    "Site Code 4": "Edit1",
    "Clear": "Clear",
    "Generate Site Code": "Generate Site Code",
    "Passport Individual Bundles": "Passport Individual Bundles",
    "Passport Suites": "Passport Suites",
    "Software Upgrade Approval Code": "Software Upgrade Approval Code",
    "Feature List": "ListView1"
}
log = logging.getLogger()

def select_multiple_suite(suites_list):
    """
    Description: Help function to select multiple suites from list
    Args:
        suites_list: list of suite name
    Returns: True if we are able to select multiple suite
    """
    app = Application().connect(path="HDActivation.exe")
    app1 = app['Passport Activation Utility']
    app1.wait('ready', 5)

    # Select Passport Individual Bundles radio button
    app1[controls["Passport Individual Bundles"]].click()
    time.sleep(.5)
    
    # Select Passport Suites radio button
    app1[controls["Passport Suites"]].click()
    time.sleep(.5)

    # Select multiple suites
    for suites in suites_list:
        app1[controls["Feature List"]].select(suites).check()

    # Verify multiple suite is selected
    for suites in suites_list:
        if not app1[controls["Feature List"]].is_checked(suites):
            log.error("Failed to select the feature list")

    # Click on clear button
    app1[controls["Clear"]].click()
    time.sleep(.5)
    
    # Verify deafult suite is selected after click on clear button
    if not app1[controls["Feature List"]].is_checked("Core Application Suite"):
        log.error("Feature list is not selected as per condition")

    return True

class HD_Activation_Test():
    """
    Description: Test class that provides an interface for testing.
    """
    def __init__(self):
        """Initializes the Template class.
        Args: None
        Returns: None
        """
        pass
    
    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        pass
    
    @test
    def verify_default_suite(self):
        """
        Testlink Id: SL-1865/SL-1877 - Consolidate feature bundles
		Description: Validate default suite(Core Application Suite) is selected when we are open the HD activation tool
        Args: None
        Returns: None
        """

        # Open the hdpassportactivation tool
        hdpassportactivation = pywinauto.application.Application().start(activation_tool_path)
        app = hdpassportactivation['Passport Activation Utility']
        app.wait('ready', 5)

        # Check if core application suite is selected or not
        if not app[controls["Feature List"]].is_checked("Core Application Suite"):
            tc_fail("Core Application Suite is not selected")
        
    @test
    def verify_bundle_for_core_application_suite(self):
        """
        Testlink Id: SL-1865/SL-1877 - Consolidate feature bundles
		Description: Validate passport individual list by selecting Core Application Suite
        Args: None
        Returns: None
        """

        app = Application().connect(path="HDActivation.exe")
        app1 = app['Passport Activation Utility']
        app1.wait('ready', 5)

        # Check if core application suite is selected or not and if not selected select suite
        if not app1[controls["Feature List"]].is_checked("Core Application Suite"):
            app1[controls["Feature List"]].select("Core Application Suite").check()

        # Select passport individual bundles radio button
        app1[controls["Passport Individual Bundles"]].click()
        time.sleep(.5)

        # Verify Core application suite related bundles are selected by default
        for bundle_list in COMMON_BUNDLES:
            if not app1[controls["Feature List"]].is_checked(bundle_list):
                tc_fail("Core application bundle list is not selected")
        
        return True
    
    @test
    def verify_bundle_for_mobile_loyalty_suite(self):
        """
        Testlink Id: SL-1865/SL-1877 - Consolidate feature bundles
		Description: Validate passport individual list by selecting Mobile Loyalty Suite
        Args: None
        Returns: None
        """

        # Add mobile loyalty suite related list in common bunlde list
        mobile_loyalty_list = ['Enhanced Loyalty Interface', 'Multiple Loyalty Interface', 'Mobile Payment']
        mobile_loyalty_list.extend(COMMON_BUNDLES)

        app = Application().connect(path="HDActivation.exe")
        app1 = app['Passport Activation Utility']
        app1.wait('ready', 5)

        # Select passport suites radio button
        app1[controls["Passport Suites"]].click()
        time.sleep(.5)
       
        # Check if mobile loyalty suite is selected or not and if not selected select suite
        if not app1[controls["Feature List"]].is_checked("Mobile Loyalty Suite"):
            app1[controls["Feature List"]].select("Mobile Loyalty Suite").check()

        # Select passport individual bundles radio button
        app1[controls["Passport Individual Bundles"]].click()
        time.sleep(.5)
        
        # Verify mobile loyalty suite related bundles are selected by default
        for bundle_list in mobile_loyalty_list:
            if not app1[controls["Feature List"]].is_checked(bundle_list):
                tc_fail("Mobile loyalty bundle list is not selected")

        return True
    
    @test
    def verify_bundle_for_tablet_pos_suite(self):
        """
        Testlink Id: SL-1865/SL-1877 - Consolidate feature bundles
		Description: Validate passport individual list by selecting Tablet POS Suite
        Args: None
        Returns: None
        """

        # Add tablet pos suite related list in common bunlde list
        tablet_pos_list = ['Base Passport', 'Enhanced Loyalty Interface', 'Tablet POS']

        app = Application().connect(path="HDActivation.exe")
        app1 = app['Passport Activation Utility']
        app1.wait('ready', 5)

        # Select passport suites radio button
        app1[controls["Passport Suites"]].click()
        time.sleep(.5)
       
        # Check if tablet pos suite is selected or not and if not selected select suite
        if not app1[controls["Feature List"]].is_checked("Tablet POS Suite"):
            app1[controls["Feature List"]].select("Tablet POS Suite").check()

        # Select passport individual bundles radio button
        app1[controls["Passport Individual Bundles"]].click()
        time.sleep(.5)

        # Verify tablet pos suite related bundles are selected by default
        for bundle_list in tablet_pos_list:
            if not app1[controls["Feature List"]].is_checked(bundle_list):
                tc_fail("Tablet POS bundle list is not selected")
        
        return True
    
    @test
    def verify_bundle_for_windows_10_suite(self):
        """
        Testlink Id: SL-1865/SL-1877 - Consolidate feature bundles
		Description: Validate passport individual list by selecting Windows 10 Suite
        Args: None
        Returns: None
        """

        # Add windows 10 suite related list in common bunlde list
        windows10_list = ['Windows 10 License']
        windows10_list.extend(COMMON_BUNDLES)

        app = Application().connect(path="HDActivation.exe")
        app1 = app['Passport Activation Utility']
        app1.wait('ready', 5)

        # Select passport suites radio button
        app1[controls["Passport Suites"]].click()
        time.sleep(.5)
       
        # Check if windows 10 suite is selected or not and if not selected select suite
        if not app1[controls["Feature List"]].is_checked("Windows 10 License"):
            app1[controls["Feature List"]].select("Windows 10 License").check()

        # Select passport individual bundles radio button
        app1[controls["Passport Individual Bundles"]].click()
        time.sleep(.5)
        
        # Verify windows 10 suite related bundles are selected by default
        for bundle_list in windows10_list:
            if not app1[controls["Feature List"]].is_checked(bundle_list):
                tc_fail("Windows 10 bundle list is not selected")
        
        return True

    @test
    def verify_bundle_for_express_lane_suite(self):
        """
        Testlink Id: SL-1865/SL-1877 - Consolidate feature bundles
		Description: Validate passport individual list by selecting Express Lane Suite
        Args: None
        Returns: None
        """

        # Add express lane suite related list in common bunlde list
        express_lane_list = ['Express Lane']
        express_lane_list.extend(COMMON_BUNDLES)

        app = Application().connect(path="HDActivation.exe")
        app1 = app['Passport Activation Utility']
        app1.wait('ready', 5)

        # Select passport suites radio button
        app1[controls["Passport Suites"]].click()
        time.sleep(.5)
       
        # Check if express lane suite is selected or not and if not selected select suite
        if not app1[controls["Feature List"]].is_checked("Express Lane Suite"):
            app1[controls["Feature List"]].select("Express Lane Suite").check()

        # Select passport individual bundles radio button
        app1[controls["Passport Individual Bundles"]].click()
        time.sleep(.5)
        
        # Verify express lane suite related bundles are selected by default
        for bundle_list in express_lane_list:
            if not app1[controls["Feature List"]].is_checked(bundle_list):
                tc_fail("Express lane bundle list is not selected")
                
        return True
    
    @test
    def verify_table_pos_not_select_with_core_application(self):
        """
        Testlink Id: SL-1865/SL-1877 - Consolidate feature bundles
		Description: Validate if we are selecting the core application suite not able to select tablet pos suite
        Args: None
        Returns: None
        """
        app = Application().connect(path="HDActivation.exe")
        app1 = app['Passport Activation Utility']
        app1.wait('ready', 5)

        # Select passport suites radio button
        app1[controls["Passport Suites"]].click()
        time.sleep(.5)
       
        # Select core application suite
        app1[controls["Feature List"]].select("Core Application Suite").check()
        
        # Select tablet pos suite
        app1[controls["Feature List"]].select("Tablet POS Suite").check()
        
        # Verify if we are selecting tablet pos suite core application suite is unchecked
        if app1[controls["Feature List"]].is_checked("Core Application Suite"):
            tc_fail("Core application suite is selected with tablet pos suite")
        
        return True
    
    @test
    def verify_table_pos_not_select_with_express_lane(self):
        """
        Testlink Id: SL-1865/SL-1877 - Consolidate feature bundles
		Description: Validate if we are selecting the express lane suite not able to select tablet pos suite
        Args: None
        Returns: None
        """

        app = Application().connect(path="HDActivation.exe")
        app1 = app['Passport Activation Utility']
        app1.wait('ready', 5)

        # Select tablet pos suite
        app1[controls["Feature List"]].select("Tablet POS Suite").check()
        
        # Select express lane suite
        app1[controls["Feature List"]].select("Express Lane Suite").check()
        
        # Verify if we are selecting express lane suite, tablet pos suite is unchecked
        if app1[controls["Feature List"]].is_checked("Tablet POS Suite"):
            tc_fail("Tablet POS Suite is selected with Express Lane Suite")
        
        # Click on clear button
        app1[controls["Clear"]].click()
        time.sleep(.5)
    
        return True
    
    @test
    def verify_multiple_suites_can_select(self):
        """
        Testlink Id: SL-1865/SL-1877 - Consolidate feature bundles
		Description: Validate we are able to select multiple suites combination
        Args: None
        Returns: None
        """
        app = Application().connect(path="HDActivation.exe")
        app1 = app['Passport Activation Utility']
        app1.wait('ready', 5)

        if not select_multiple_suite(["Core Application Suite", "Mobile Loyalty Suite"]):
            tc_fail("Unable to select multiple suites")

        if not select_multiple_suite(["Core Application Suite", "Windows 10 License"]):
            tc_fail("Unable to select multiple suites")

        if not select_multiple_suite(["Core Application Suite", "Express Lane Suite"]):
            tc_fail("Unable to select multiple suites")

        if not select_multiple_suite(["Tablet POS Suite", "Mobile Loyalty Suite"]):
            tc_fail("Unable to select multiple suites")
        
        if not select_multiple_suite(["Tablet POS Suite", "Windows 10 License"]):
            tc_fail("Unable to select multiple suites")

        if not select_multiple_suite(["Express Lane Suite", "Windows 10 License"]):
            tc_fail("Unable to select multiple suites")
        
        if not select_multiple_suite(["Express Lane Suite", "Mobile Loyalty Suite"]):
            tc_fail("Unable to select multiple suites")
        
        if not select_multiple_suite(["Mobile Loyalty Suite", "Windows 10 License"]):
            tc_fail("Unable to select multiple suites")
        
        if not select_multiple_suite(["Core Application Suite", "Mobile Loyalty Suite", "Windows 10 License", "Express Lane Suite"]):
            tc_fail("Unable to select multiple suites")
        
        app.kill()

        return True
     
    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        pass