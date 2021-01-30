"""
    File name: DODO_6113.py
    Tags:
    Description: 
    Author: 
    Date created: 2020-05-26 13:48:16
    Date last modified: 
    Python Version: 3.7
"""

import logging
import time
from app import Navi, mws, pos, system, forecourt_installation, networksim, crindsim
from app.framework import EDH
from app import network_site_config
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app.features import feature_activation
from Scripts.features import NGFC_Helpers

class DODO_6113():
    """
    Description: Test class that provides an interface for testing.
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

        #Commercial Diesel checkbox activation in forecourt installation 
        #self.helpers.set_commercial_on_forecourt()

        # back cash advance to 0
        self.set_cash_advance_on_mws('000')

        # HostSim Response mode
        networksim.set_response_mode("Approval")

        # Disable all promtps

        networksim.disable_commercial_fuel_limits()
        networksim.disable_product_limits()
        networksim.disable_prompts() 

        # Set merchant limit so we can deal with additional product prompt
        networksim.set_commercial_product_limit("True", "MERC", "Default category for merchandise", 30.00)        
        
        # Set Dispenser in auto

        self.log.info("Setting the CRIND in manual mode")
        crindsim.set_mode("manual")
        crindsim.set_sales_target()
        crindsim.select_grade(1)

        #open Browser
        self.pos.connect()

        self.pos.sign_on()        

        self.pos.maximize_pos()
        
    @test
    def DODO_6113_11_Outside_NFGC_AdditionalProducts(self):
        """
        To validate that Passport prompt for cash advance  when using NFGC Cards in outside commercial transactions
        """
        tractor_fuel_type = 'tractor' 
        def_type_yes = 'No' 
        cash_advance = "3000" # value without decimals(.)
        fuel_amount = '5.00'
        accept_cash_advance = 'No'
        dispenser_number = "1"
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts        
        Host_sim_mode = "Approval" #the scripts is about new response code, we are testing all of them
        
        # Dispenser prompts
        dispenser_prompts = {
            "Make selection":{
                "entry": [""],
                "buttons": [tractor_fuel_type]
            },
            "Need DEF?":{
                "entry": [""],
                "buttons": [def_type_yes]
            },
            "Is this a Debit/ATM card?":{
                "entry": [""],
                "buttons": ["No"]
            },
            "Additional Products Y/N?":{
                "entry": [""],
                "buttons": ["Yes"]
            },
            "Do you want a receipt?":{
                "entry": [""],
                "buttons": ["No"]
            },
            f"Do you want cash advance up to ${cash_advance[:2]}?":{
                "entry": [""],
                "buttons": [accept_cash_advance]
            },
            "Carwash today?":{
                "entry": [""],
                "buttons": ["No"]
            }
        }

        amounts_to_dispense = {
            "buffer_1":{
                "grade": 1,
                "value": fuel_amount[:3]
            }
        }

        #Output verifications
        
        receipt_data = [
            f"{self.helpers.grade_1_Name} CA   PUMP# 1",
            f"{fuel_amount}0 GAL @ $1.000/GAL           ${fuel_amount}  99",
            f"Subtotal =    ${fuel_amount}",
            "Tax  =    $0.00",
            f"Total =    ${fuel_amount}",
            "Change Due  =    $0.00",
            f"Credit                           ${fuel_amount}"]

        # HostSim Response mode
        networksim.set_response_mode(Host_sim_mode)

        self.log.info(f"Configure the mws with cash advance {cash_advance}")
        self.set_cash_advance_on_mws(cash_advance)

        self.log.info(f"Set the host sim with cash advance {cash_advance[:2]}")
        networksim.set_commercial_product_limit("True","CADV","Company funds cash advance",cash_advance[:2])

        self.helpers.dispenser_transaction(
            prompts=dispenser_prompts, 
            amounts_to_dispense=amounts_to_dispense, 
            receipt_data=receipt_data, 
            inside_receipt="Yes"    
        )
    
    @test    
    def DODO_6113_12_Outside_NFGC_CashAdvance(self):
        """
        To validate that Passport prompt for cash advance  when using NFGC Cards in outside commercial transactions12_Outside_NFGC_CashAdvance 
        """
        tractor_fuel_type = 'Both'
        def_type_yes = 'Yes' 
        cash_advance_mws = "3000" # value without decimals(.)
        cash_advance_host = "15"
        accept_cash_advance = 'Yes'
        cash_advance_amt = "1000"        
        dispenser_number = "1"
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts        
        Host_sim_mode = "Approval" #the scripts is about new response code, we are testing all of them
        amounts_to_dispense = [3, 4, 5] #amount to dispense on each fuel, at a multidispensing transaction        
        
        amounts_to_dispense = {
            "buffer_1":{
                "grade": 1,
                "value": "3"
            },
            "buffer_2":{
                "grade": 3,
                "value": "4"
            },
            "buffer_3":{
                "grade": 1,
                "value": "5"
            }
        }
        # Dispenser prompts
        dispenser_prompts = {
            "Make selection":{
                "entry": [""],
                "buttons": [tractor_fuel_type]
            },
            "Need DEF?":{
                "entry": [""],
                "buttons": [def_type_yes]
            },
            "Is this a Debit/ATM card?":{
                "entry": [""],
                "buttons": ["No"]
            },
            "Additional Products Y/N?":{
                "entry": [""],
                "buttons": ["Yes"]
            },
            "Do you want a receipt?":{
                "entry": [""],
                "buttons": ["No"]
            },
            f"Do you want cash advance up to ${cash_advance_host}?":{
                "entry": [""],
                "buttons": [accept_cash_advance]
            },            
            "Press ENTER/OK when done CANCEL to Cancel Enter Cash Advance Amount":{
                "entry": [cash_advance_amt],
                "buttons": ["Enter"]
            },
            "Carwash today?":{
                "entry": [""],
                "buttons": ["No"]
            }
        }

        #Output verifications
        
        receipt_data = [
            f"{self.helpers.grade_1_Name} CA   PUMP# 1",
            "3.000 GAL @ $1.000/GAL           $3.00  99",
            f"{self.helpers.grade_3_Name} CA   PUMP# 1",
            "4.000 GAL @ $1.000/GAL           $4.00  99",
            f"{self.helpers.grade_1_Name} CA   PUMP# 1",
            "5.000 GAL @ $1.000/GAL           $5.00  99",
            "Cash Advance                    $10.00    ",
            "                   Subtotal =   $22.00    ",
            "                       Tax  =    $0.00    ",
            "                      Total =   $22.00    ",
            "Credit                          $22.00    "
        ]

        self.log.info("Setting the CRIND in manual mode")
        crindsim.set_mode("manual")
        
        # HostSim Response mode
        networksim.set_response_mode(Host_sim_mode)

        self.log.info(f"Configure the mws with cash advance {cash_advance_mws}")
        self.set_cash_advance_on_mws(cash_advance_mws)

        self.log.info(f"Set the host sim with cash advance {cash_advance_host}")
        networksim.set_commercial_product_limit("True","CADV","Company funds cash advance",cash_advance_host)

        self.pos.maximize_pos()

        self.helpers.dispenser_transaction(
            prompts=dispenser_prompts, 
            amounts_to_dispense=amounts_to_dispense, 
            receipt_data=receipt_data, 
            inside_receipt="Yes"    
        )
    
    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        self.pos.close()

        self.set_cash_advance_on_mws(0)        
        
    ### Helpers ###

    def set_cash_advance_on_mws(self, cash_advance):
        
        nsc_info = {
            'Global Information' : {
                'Page 2' : {
                    'Cash Advance Limit': cash_advance
                }
            }
        }

        self.pos.minimize_pos()
        CA = network_site_config.NetworkSetup()

        self.log.info(f'Checking cash advance value and configuring with ${str(int(cash_advance) / 100)}, if it is necesary.')
        if not CA.configure_network(config=nsc_info):
            tc_fail("Failed to configure cash advance into network configuration.")

        self.pos.maximize_pos()
 
