import logging, pywinauto, time
from app.framework import mws, Navi
from app.util import constants, system

from pywinauto.keyboard import send_keys

BUNDLES = "Passport Individual Bundles"
SUITES = "Passport Suites"

DEFAULT_PASSPORT = ["Base Passport", "Enhanced Store", "Enhanced Reporting", "Advanced Merchandising",
                    "Employee Management", "Enhanced Card Services", "Enhanced Loyalty Interface",
                    "Multiple Loyalty Interface", "Mobile Payment", "Prepaid Card Services", "Windows 10 License", "Car Wash"]
DEFAULT_EDGE = ["Base Passport", "Windows 10 License", "Tablet POS"]
DEFAULT_EXPRESS = ["Base Passport", "Enhanced Store", "Enhanced Reporting", "Advanced Merchandising",
                    "Employee Management", "Enhanced Card Services", "Enhanced Loyalty Interface",
                    "Multiple Loyalty Interface", "Mobile Payment", "Prepaid Card Services", "Windows 10 License", "Car Wash", "Express Lane"]

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
    "Feature List": "ListView1"
}

done_msg = "New Passport features have been activated. "\
            "You will be signed off once you click ok. Please use "\
            "Security Group Maintenance to update security groups."

win10_error_msg = "Windows 10 License activation is required."

class FeatureActivation():
    def __init__(self):
        self.log = logging.getLogger()
        FeatureActivation.navigate_to()

    @staticmethod
    def navigate_to():
        return Navi.navigate_to("Feature Activation")

    def activate(self, features=DEFAULT_PASSPORT, mode=BUNDLES):
        """
        Activate Passport features.
        Args:
            features: (list) A list of the feature bundles or suites to activate.
            mode: (str) Whether to activate via individual bundles (BUNDLES) or suites (SUITES).
        Returns: (bool) True if activation succeeded, False if something went wrong.
        Examples:
            >>> feature_activation.FeatureActivation().activate()
            True
            >>> feature_activation.FeatureActivation().activate(feature_activate.DEFAULT_EDGE)
            True
            >>> feature_activation.FeatureActivation().activate(["Core Application Suite", "Store Management Suite",
                "Mobile Loyalty Suite"], feature_activate.SUITES)
            True
        """
        site_key = [ mws.get_text(f"Site Key {i}") for i in range(1,4) ]

        #Open the hdpassportactivation tool
        hdpassportactivation = pywinauto.application.Application().start(activation_tool_path)
        app = hdpassportactivation['Passport Activation Utility']
        app.wait('ready', 5)
        
        # Select Activation Mode
        app[controls[mode]].click()
        time.sleep(1)

        # Input Site Key
        [ app[controls[f"Site Key {i+1}"]].set_text(site_key[i]) for i in range(3) ]

        # Select feature bundles/suites
        for feature in features:
            app[controls["Feature List"]].select(feature).check()
        
        time.sleep(.5)

        # Generate and retrieve Site Code
        app[controls["Generate Site Code"]].click()
        time.sleep(.5)
        site_code = [ app[controls[f"Site Code {i}"]].texts()[0] for i in range(1,5) ]
        hdpassportactivation.kill()

        # Enter Site Code in MWS
        for i in range(4):
            if not mws.set_text(f"Site Code {i+1}", site_code[i]):
                return False

        # Finalize activation
        mws.click("Activate")
        start_time = time.time()
        while time.time()-start_time <= 60:
            get_activation_message = mws.get_top_bar_text()
            if (get_activation_message==done_msg) or (get_activation_message==win10_error_msg):
                mws.click_toolbar("OK", timeout=10)
        else:
            self.log.error("Feature activation or windows 10 activation error message didn't appear.")
             
        msg = mws.get_top_bar_text()
        if msg:
            self.log.error(f"Got an unexpected top bar message when exiting Feature Activation: {mws.get_top_bar_text()}")
            mws.recover()
            return False
        return True


