"""
    File name: DODO_6081.py
    Tags:
    Description: As Passport, I need to be able to add the paper check tender key at the POS for Exxon and use it.
    Author: 
    Date created: 2019-11-29 07:21:07
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import Navi, mws, pos, system, runas, networksim, crindsim
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app.features import tender,feature_activation
from Scripts.features import NGFC_Helpers
import time

class DODO_6081():
    """
    Description: PDL download and prepay transactions with
    money code prompting
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

        self.helpers = NGFC_Helpers.NGFC_Helpers(self.log, self.mws)

        # Constants
        self.money_code = "0123456789"        

    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        """ 
        
        # HostSim Response mode
        networksim.set_response_mode("Approval")
                
        # Disable all promtps

        networksim.disable_commercial_fuel_limits()
        networksim.disable_product_limits()
        networksim.disable_prompts()

        # Set Dispenser Config

        crindsim.set_mode("auto")
        crindsim.set_sales_target()        
        crindsim.select_grade(1) # Setting Disel 1 as default grade

        self.pos.connect()

        self.pos.sign_on()

        self.pos.minimize_pos()
    
    @test
    def DODO_6081_Paper_Check_Tender_Add(self):
        """
        Configuration of the new tender group in order to create the button to be used in case of Paper Check as a form of payment.
        """
        #Input constants 
        self.papercheck_tender_code = "1234"
        self.papercheck_tender_description = 'Paper Check'
        self.papercheck_tender_group = 'Integrated Commercial Check'
        self.papercheck_button_name = 'PAPER CHK'

        tender_info = {
                "Tender Code": self.papercheck_tender_code,
                "Tender Description": self.papercheck_tender_description,
                "General": {
                    "Tender group this tender belongs to": self.papercheck_tender_group,
                    "Receipt Description": self.papercheck_tender_description,
                    "Tender Button Description": self.papercheck_button_name,
                    "NACS Tender Code": "generic"
                },
                "Currency And Denominations": {
                    "Currency": "US Dollars"
                },
                "Functions": {
                    "Sale": {
                        "Show exact amount button": True,
                        "Show next highest button": True,
                    }  
                },
                "Min/Max": {
                    "Minimum Allowed": "0.00",
                    "Maximum Allowed": "100.00",
                    "Repeated Use Limit": "5",
                    "Maximum Refund": "25.00",
                    "Primary tender for change": "Cash",
                    "Maximum primary change allowed": "100000.00",
                    "Secondary tender for change": "Cash"
                },
                "Register Groups": {
                    "POSGroup1": {
                        "Sales": True
                    }
                }
            }
        # tender maintenance configuration for paper check
        tm = tender.TenderMaintenance()

        # Validate if tender maintenance configuration was performed correctly
        if not tm.configure(self.papercheck_tender_description , tender_info, True):
            tc_fail("Failed to configure tender: " + self.papercheck_tender_description )
        
        mws.click_toolbar("Exit")
    
    @test
    def DODO_6081_Paper_Check_Tender_Passport_Button(self):
        """
        Prepay sale with a commercial card in which will be verified the use of paper check tender, it will be verified that preauth and completion should contain specific value for this tender and the commercial diesel ones.
        """
        #Input constants

        self.papercheck_button_name = 'PAPER CHK'

        generic_trans_amount = "$5.00" #any value that gets an approval from the host
        generic_fuel_type = 'Tractor fuel' #any of the fuel types, since is not the objetive of the TC ("Tractor fuel.", "Reefer fuel.", "Both fuels.")
        def_type_no = 'No' #could be "yes" of "no",  because is not the objective of this TC

        check_number = "120174"

        amounts_to_dispense = {
            "buffer_1":{
                "grade": 1,
                "value": "5"
            }
        }

        commercial_prompts = {#"Commercial_prompt" is a dictionary in which are the dinamic prompts for commercial diesel
                        "Enter Check Number": {
                            "entry": [check_number],
                            "buttons": ["Enter"]
                        },
                        "Enter Money Code":{
                            "entry": [self.money_code],
                            "buttons": ["Enter"]
                        }#, "Insert Last Name and First Name": {"entry" : ["Juan Jose"],"buttons": ["Ok"]}
                    }

        crindsim.set_mode("manual")

        self.pos.maximize_pos()

        self.pos.add_fuel(generic_trans_amount,fuel_type = generic_fuel_type, def_type = def_type_no)

        self.pos.pay(tender_type=self.papercheck_button_name, prompts=commercial_prompts)

        self.pos.select_dispenser(1)

        self.helpers.fuel_handler(amounts_to_dispense)

        self.pos.wait_for_fuel(timeout=120)

        self.log.info("Hitting the back button, so the next test case can start from the idle screen")
        self.pos.click_function_key("Back")
    
    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """

        self.pos.close()

    