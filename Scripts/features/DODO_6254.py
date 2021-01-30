"""
    File name: DODO-6254.py
    Tags:
    Description: Test scripts meant to run end to end testing for commercial prepays
    Author: Javier H Sandoval
    Date created: 2020-08-05 13:00:00
    Date last modified: 2020-08-06 19:00:00
    Python Version: 3.7
"""

import logging
from app import Navi, mws, pos, system, forecourt_installation, networksim, crindsim
from app.framework import EDH
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app.features import feature_activation
from Scripts.features import NGFC_Helpers
import time

class DODO_6254():
    """
    Description: Prepay transactions made on NGFC project
    """

    def __init__(self):
        """
        Initializes the Template class.
        """
        # The logging object.         
        self.log = logging.getLogger()

        # The main MWS object 
        self.mws = mws
        
        # The main POS object
        self.pos = pos

        # The main EDH object
        self.edh = EDH.EDH()

        self.helpers = NGFC_Helpers.NGFC_Helpers(self.log, self.mws, self.pos)

    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        """
        self.log.info("Checking if the newtowrk parser is available")
        comm_test = self.edh.translate_message("Comm Test")

        if not comm_test:
            self.log.error("Network Parser is not available")
            raise Exception

        #open Browser
        self.pos.connect()

        self.pos.sign_on()

    @test
    def Tractor_Only_1(self):
        """
        On a commercial dispenser and reefer check is activated but 
        it does not configured alternate fuel product for reefer and 
        it does not configurated DEF on product tab on forecourt.
        On POS, product type prompts should not appear, 
        since only tractor is selectable.
        """
        #Input parameters:
        product3_primary_fuel = "Regular"

        #Validation parameters:

        self.pos.minimize_pos()
        """Grade 1"""
        if not self.change_forecourtinstallation_product(self.helpers.grade_1_Name,self.helpers.grade_1_Name,""):
            tc_fail("Product 1 configuration on forecourt installation, could not be made.")
        """Grade 2"""
        if not self.change_forecourtinstallation_product(self.helpers.grade_2_Name,self.helpers.grade_2_Name,""):
            tc_fail("Product 2 configuration on forecourt installation, could not be made.")
        """Grade 3"""
        if not self.change_forecourtinstallation_product(self.helpers.grade_3_Name,product3_primary_fuel,""):
            tc_fail("Product 3 configuration on forecourt installation, could not be made.")
        
        self.pos.maximize_pos()
        
        self.pos.wait_disp_ready(idle_timeout=120)

        self.log.info("Starting a prepay transaction")

        if not pos.select_dispenser(1, timeout=3, verify=False):
            tc_fail("Unable to select dispenser 1")
        
        self.pos.click_forecourt_key("Prepay", timeout=5, verify=False)

        if self.pos.read_messageboxbuttons_text():
            self.pos.click_keypad("Cancel")
            tc_fail("A prompt is shown and it is not expected.") 

        self.pos.click_keypad("Cancel")

        self.pos.minimize_pos()

        self.log.info("Restoring forecourt products to original values")
        """Grade 1"""
        if not self.change_forecourtinstallation_product(self.helpers.grade_1_Name,self.helpers.grade_1_Name,self.helpers.grade_1_Name_reefer):
            tc_fail("Product 1 restoring configuration on forecourt installation, could not be made.  Following test cases will fail.")
        """Grade 2"""
        if not self.change_forecourtinstallation_product(self.helpers.grade_2_Name,self.helpers.grade_2_Name,self.helpers.grade_2_Name_reefer):
            tc_fail("Product 2 restoring configuration on forecourt installation, could not be made.  Following test cases will fail.")
        """Grade 3"""
        if not self.change_forecourtinstallation_product(product3_primary_fuel,self.helpers.grade_3_Name,""):
            tc_fail("Product 3 restoring configuration on forecourt installation, could not be made.  Following test cases will fail.")

        self.pos.maximize_pos()
    
    @test
    def DEF_Only_2(self):
        """
        On a commercial dispenser and reefer check is activated but only configurated DEF fuel product on product tab on forecourt installation.
        On POS, should appear only DEF prompt.
        """
        #Input parameters:
        
        #Validation parameters:
        
        self.pos.minimize_pos()

        if not self.change_forecourtinstallation_producttodispense("3 DEF","3 DEF","3 DEF"):
            tc_fail("Product to dispense configuration on forecourt installation, could not be made.")
        
        self.pos.maximize_pos()
        
        self.pos.wait_disp_ready(idle_timeout=120)

        self.log.info("Starting a prepay transaction")

        if not pos.select_dispenser(1, timeout=3, verify=False):
            tc_fail("Unable to select dispenser 1")
        
        self.pos.click_forecourt_key("Prepay", timeout=5, verify=False)

        if self.pos.read_messageboxbuttons_text():
            self.pos.click_keypad("Cancel")
            tc_fail("A prompt is shown and it is not expected.") 

        self.pos.click_keypad("Cancel")

        self.pos.minimize_pos()

        self.log.info("Reseting forecourt products to dispense to original values")
        
        if not self.change_forecourtinstallation_producttodispense("1 Diesel 1","2 Diesel 2","3 DEF"):
            tc_fail("Product to dispense restoring configuration on forecourt installation, could not be made.  Following test cases will fail.")

        self.pos.maximize_pos()
    
    @test
    def Tractor_and_Reefer_3(self):
        """
        On a commercial dispenser and reefer check is activated but 
        it does not configured alternate fuel product for reefer and 
        it does not configurated DEF on product tab on forecourt.
        On POS, shoudl only appear th tractor, reefer or both prompt;
        not the DEF one.
        """
        #Input parameters:
        product3_primary_fuel = "Desl Blnd"
        product3_reefer_fuel = "RD Dsl BL"

        #Validation parameters:
        prompt_buttons = ["Tractor fuel.",
                          "Reefer fuel.",
                          "Both fuels."
        ]

        self.pos.minimize_pos()

        """Grade 3"""
        if not self.change_forecourtinstallation_product(self.helpers.grade_3_Name,product3_primary_fuel,product3_reefer_fuel):
            tc_fail("Product 3 configuration on forecourt installation, could not be made.")
        
        self.pos.maximize_pos()
        
        self.pos.wait_disp_ready(idle_timeout=120)

        self.log.info("Starting a prepay transaction")

        if not pos.select_dispenser(1, timeout=3, verify=False):
            tc_fail("Unable to select dispenser 1")
        
        self.pos.click_forecourt_key("Prepay", timeout=5, verify=False)

        if self.pos.read_messageboxbuttons_text() != prompt_buttons:
            self.pos.click_message_box_key("Tractor fuel.", verify=False, timeout=5)
            self.pos.click_keypad("Cancel")
            tc_fail("The prompt is showing wrong buttons.")

        self.pos.click_message_box_key("Tractor fuel.", verify=False, timeout=5)

        self.pos.click_keypad("Cancel")

        self.pos.minimize_pos()

        self.log.info("Reseting forecourt products to original values")

        """Grade 3"""
        if not self.change_forecourtinstallation_product(product3_primary_fuel,self.helpers.grade_3_Name,""):
            tc_fail("Product 3 restoring configuration on forecourt installation, could not be made.  Following test cases will fail.")

        self.pos.maximize_pos()
    
    @test
    def Tractor_and_DEF_4(self):
        """
        On a commercial dispenser and reefer check is activated but 
        it does not configured alternate fuel product for reefer and 
        it does not configurated DEF on product tab on forecourt.
        On POS, shoudl only appear th tractor, DEF or both prompt;
        not the DEF one.
        """
        #Input parameters:

        #Validation parameters:
        prompt_buttons = ["Tractor fuel.",
                          "DEF fuel.",
                          "Both fuels."
        ]

        self.pos.minimize_pos()
        """Grade 1"""
        if not self.change_forecourtinstallation_product(self.helpers.grade_1_Name,self.helpers.grade_1_Name,""):
            tc_fail("Product 1 configuration on forecourt installation, could not be made.")
        """Grade 2"""
        if not self.change_forecourtinstallation_product(self.helpers.grade_2_Name,self.helpers.grade_2_Name,""):
            tc_fail("Product 2 configuration on forecourt installation, could not be made.")
        
        self.pos.maximize_pos()
        
        self.pos.wait_disp_ready(idle_timeout=120)

        self.log.info("Starting a prepay transaction")

        if not pos.select_dispenser(1, timeout=3, verify=False):
            tc_fail("Unable to select dispenser 1")
        
        self.pos.click_forecourt_key("Prepay", timeout=5, verify=False)

        if self.pos.read_messageboxbuttons_text() != prompt_buttons:
            self.pos.click_message_box_key("Tractor fuel.", verify=False, timeout=5)
            self.pos.click_keypad("Cancel")
            tc_fail("The prompt is showing wrong buttons.")

        self.pos.click_message_box_key("Tractor fuel.", verify=False, timeout=5)

        self.pos.click_keypad("Cancel")

        self.pos.minimize_pos()

        self.log.info("Reseting forecourt products to original values")
        """Grade 1"""
        if not self.change_forecourtinstallation_product(self.helpers.grade_1_Name,self.helpers.grade_1_Name,self.helpers.grade_1_Name_reefer):
            tc_fail("Product 1 restoring configuration on forecourt installation, could not be made.  Following test cases will fail.")
        """Grade 2"""
        if not self.change_forecourtinstallation_product(self.helpers.grade_2_Name,self.helpers.grade_2_Name,self.helpers.grade_2_Name_reefer):
            tc_fail("Product 2 restoring configuration on forecourt installation, could not be made.  Following test cases will fail.")

        self.pos.maximize_pos()
    
    @test
    def Tractor_Reefer_DEF_Fuel_Prompts_5(self):
        """
        On a commercial dispenser and reefer check is activated but 
        it does not configured alternate fuel product for reefer and 
        it does not configurated DEF on product tab on forecourt.
        On POS, should only appear the tractor, Reefer or both prompt and
        the DEF prompt.
        """
        #Input parameters:

        #Validation parameters:
        prompt_buttons = ["Tractor fuel.",
                          "Reefer fuel.",
                          "Both fuels."
        ]

        DEF_prompt_buttons = ["Yes",
                              "No"
        ]
        
        self.pos.wait_disp_ready(idle_timeout=120)

        self.log.info("Starting a prepay transaction")

        if not pos.select_dispenser(1, timeout=3, verify=False):
            tc_fail("Unable to select dispenser 1")
        
        self.pos.click_forecourt_key("Prepay", timeout=5, verify=False)

        if self.pos.read_messageboxbuttons_text() == prompt_buttons:
            self.pos.click_message_box_key("Tractor fuel.", verify=False, timeout=5)

            if self.pos.read_messageboxbuttons_text() == DEF_prompt_buttons:
                self.pos.click_message_box_key("No", verify=False, timeout=5)
                self.pos.click_keypad("Cancel")
            else:
                self.pos.click_message_box_key("Tractor fuel.", verify=False, timeout=5)
                self.pos.click_keypad("Cancel")
                tc_fail("The prompt is showing wrong buttons.")
        else:
            self.pos.click_message_box_key("Tractor fuel.", verify=False, timeout=5)
            prompt_title = self.pos.read_message_box(timeout=5)
            if prompt_title:
                self.pos.click_message_box_key("No", verify=False, timeout=5)
            self.pos.click_keypad("Cancel")
            tc_fail("The prompt is showing wrong buttons.")
    
    @test
    def Reefer_check_disable_6(self):
        """
        On a commercial dispenser and reefer check is disable,
        it configurated Tractor, reefer and DEF on product tab on forecourt
        installation.  On POS, must has fuel products prompts with Tractor,
        DEF, Both, because the reefer check is disable.
        """
        #Input parameters:

        #Validation parameters:
        prompt_buttons = ["Tractor fuel.",
                          "DEF fuel.",
                          "Both fuels."
        ]

        self.pos.minimize_pos()

        if not self.dispenser_type_config(reefer_enable=False):
            tc_fail("Disabling 'Reefer' allowing on forecourt installation, could not be made.")
        
        self.pos.maximize_pos()
        
        self.pos.wait_disp_ready(idle_timeout=120)

        self.log.info("Starting a prepay transaction")

        if not pos.select_dispenser(1, timeout=3, verify=False):
            tc_fail("Unable to select dispenser 1")
        
        self.pos.click_forecourt_key("Prepay", timeout=5, verify=False)

        if self.pos.read_messageboxbuttons_text() != prompt_buttons:
            self.pos.click_message_box_key("Tractor fuel.", verify=False, timeout=5)
            tc_fail("The prompt is showing wrong buttons.")

        self.pos.click_message_box_key("Tractor fuel.", verify=False, timeout=5)

        self.pos.click_keypad("Cancel")

        self.pos.minimize_pos()

        self.log.info("Reseting forecourt to original values")
        
        if not self.dispenser_type_config():
            tc_fail("Re-enabling 'Reefer' allowing on forecourt installation, could not be made.  Following test cases will fail.")
        
        self.pos.maximize_pos()
    
    @test
    def Retail_no_fuel_prompts_7(self):
        """
        On a retail dispenser, POS must not has fuel products prompt.
        """
        #Input parameters:

        #Validation parameters:

        self.pos.minimize_pos()
        
        if not self.dispenser_type_config(commercial_enable=False, reefer_enable=False):
            tc_fail("Disabling 'Commercial' and 'Reefer' allowing on forecourt installation, could not be made.")

        self.pos.maximize_pos()
        
        self.pos.wait_disp_ready(idle_timeout=120)

        self.log.info("Starting a prepay transaction")

        if not pos.select_dispenser(1, timeout=3, verify=False):
            tc_fail("Unable to select dispenser 1")
        
        self.pos.click_forecourt_key("Prepay", timeout=5, verify=False)

        if self.pos.read_messageboxbuttons_text():
           tc_fail("The prompt is showing wrong buttons.") 

        self.pos.click_keypad("Cancel")

        self.pos.minimize_pos()

        self.log.info("Reseting forecourt products to original values")

        if not self.dispenser_type_config():
            tc_fail("Re-enabling 'Commercial' and 'Reefer' allowing on forecourt installation, could not be made.  Following test cases will fail.")

        self.pos.maximize_pos()
    
    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """

        self.pos.close()

    def change_forecourtinstallation_product(self, existing_prod, new_prod, new_prod_reefer):
        self.log.info(f"Trying to set {new_prod}")
        fc = forecourt_installation.ForecourtInstallation()

        mws.click("Set Up")

        mws.select_tab("Tank - Product to")

        if not fc.change(existing_prod,
                "Product", 
                config={"Name": new_prod,
                        "Reefer": new_prod_reefer
                }):
            return False

        if not mws.click_toolbar("Save"):
            self.log.error("Unable to save Dispenser Options")
            return False
        
        if not mws.click_toolbar("Save"):
            self.log.error("Unable to save Dispenser Options")
            return False
        self.log.info(f"{new_prod} already set")
        
        time.sleep(5)
        
        return True

    def change_forecourtinstallation_producttodispense(self, tank1, tank2, tank3):
        self.log.info(f"Trying to set Tank - Product to dispense tab")
        fc = forecourt_installation.ForecourtInstallation()

        mws.click("Set Up")

        mws.select_tab("Tank - Product to")
        
        mws.click("Change", "Tank - Product to Dispensers")

        if not mws.set_value("Tank 1", tank1, "Tank - Product to Dispensers"):
            return False
        if not mws.set_value("Tank 2", tank2, "Tank - Product to Dispensers"):
            return False
        if not mws.set_value("Tank 3", tank3, "Tank - Product to Dispensers"):
            return False

        if not mws.click("Update List", "Tank - Product to Dispensers"):
            return False

        if not mws.click_toolbar("Save"):
            self.log.error("Unable to save Dispenser Options")
            return False
        
        if not mws.click_toolbar("Save"):
            self.log.error("Unable to save Dispenser Options")
            return False
        self.log.info("Tank - Product to dispense already set")

        time.sleep(5)

        return True

    def dispenser_type_config(self, commercial_enable=True, reefer_enable=True):
        """
        Set the dispenser as commercial Diesel
        """
        fc_config = {
            "Dispensers": {
                "Commercial Diesel": commercial_enable,
                "Reefer": reefer_enable
            }
        }
        fc = forecourt_installation.ForecourtInstallation()
        
        mws.click("Set Up")
        
        if not fc.change("Gilbarco", "Dispensers", fc_config.get("Dispensers")):
            return False

        if not mws.click_toolbar("Save"):
            self.log.error("Unable to save Dispenser Options")
            return False
        
        if not mws.click_toolbar("Save"):
            self.log.error("Unable to save Dispenser Options")
            return False
        self.log.info("Tank - Product to dispense already set")

        time.sleep(5)

        return True
    
    
