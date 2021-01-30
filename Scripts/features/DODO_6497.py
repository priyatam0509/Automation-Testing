"""
    File name: DODO_64947.py
    Tags:
    Description: 
    Author: 
    Date created: 2020-09-28 14:58:16
    Date last modified: 
    Python Version: 3.7
"""

import logging
import time
from app import Navi, mws, pos, system, forecourt_installation, networksim, crindsim, host_function
from app.framework import EDH
from app import network_site_config
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app.features import feature_activation
from Scripts.features import NGFC_Helpers

class DODO_6497():
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

        # HostSim Response mode
        networksim.set_response_mode("Approval")

        # Disable all promtps

        networksim.disable_commercial_fuel_limits()
        networksim.disable_product_limits()
        networksim.disable_prompts() 

        # Set merchant limit so we can deal with additional product prompt
        networksim.set_commercial_product_limit("True", "MERC", "Default category for merchandise", 30.00)        
        networksim.set_commercial_customer_information("ABC TRUCKING", "DENVER", "CO", "234W987")
        
        
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
    def Outside_commercial_before_fueling_CANCEL(self):
        """
        To validate that Passport prompt for cash advance  when using NFGC Cards in outside commercial transactions
        """
        tractor_fuel_type = 'tractor' 
        def_type_yes = 'No' 
        cash_advance = "1500" # value without decimals(.)
        cash_advance_store = "3000"
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
                "buttons": ["No"]
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
            },
            "Lift handle to begin fueling Ready to fuel Tractor":{
                "entry": ["1"],
                "buttons": ["Cancel"]
            }
        }

        amounts_to_dispense = {
            "buffer_1":{
                "grade": 1,
                "value": fuel_amount[:3]
            }
        }

        message_types = [
                "preauth_request_verifications",
                "preauth_response_verifications", 
                "reversal_request"            
            ]

        #Output verifications
        messages_to_verify = {
            'preauth_request_verifications' : {
                'Fuel Purchase': '5000',
                'Prod 1 product Code': self.helpers.grade_1_Product,
                'Prod 2 product Code': self.helpers.grade_2_Product,
                'Prod 3 product Code': self.helpers.grade_1_Product_reefer,
                'Prod 4 product Code': self.helpers.grade_2_Product_reefer,
                'Prod 5 product Code': self.helpers.grade_3_Product,
                '001 - Wex OTR Flags': 'C - Commercial',
                '008 - Wex OTR Cash Advance Limit': '$30.00'},
            'preauth_response_verifications': {
                'Response Code': '2', 
                'Approved Amount': '000005000',
                '005 - Wex OTR Customer Information': 'ABC TRUCKING             DENVER         CO234W987'},
            'reversal_request': {
                'Prompt Code': 'S092',
                'Fuel Purchase': '5000'}            
        }
        

        # HostSim Response mode
        
        self.log.info(f"Configure the mws with cash advance {cash_advance_store}")
        self.helpers.set_cash_advance_on_mws(cash_advance_store)

        self.log.info(f"Set the host sim with cash advance {cash_advance[:2]}")
        networksim.set_commercial_product_limit("True","CADV","Company funds cash advance",cash_advance[:2])

        last_msg = self.edh.get_last_msg_id(pspid='23')

        self.helpers.dispenser_transaction(
            prompts=dispenser_prompts, 
            amounts_to_dispense=amounts_to_dispense,             
            inside_receipt="No",
            decline_scenario=True,
            messages_to_verify=messages_to_verify, 
            skip_fueling=True,
            message_types=message_types
        )

        self.pos.click_function_key("Back")
        self.pos.minimize_pos()
        # Making reversal be send to the host
        if not self.comm_test():
                self.log.error("There was an issue with comm test")
        
        self.pos.maximize_pos()
         
        self.log.info("Waiting for the reversal to be completed")
        
        start = time.time()
        reversal_found = False
        message_to_find= ""
        
        self.log.debug("Checking if the reversal was already placed")
        while not reversal_found and time.time() - start < 60:

            messages = self.edh.get_network_messages(12,start_in=last_msg)
            for message in messages:
                if "Reversal response" in message:
                    self.log.debug(f"The reversal was found: {message}")
                    message_to_find = message.split()
                    message_to_find = f"Response {message_to_find[9]}"
                    reversal_found = True
                    break
        
        if not reversal_found:
            tc_fail("Reversal not found")

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        self.pos.close()

        self.helpers.set_cash_advance_on_mws(0)

    def comm_test(self):
        #This will perform COMM test
        hf = host_function.HostFunction()
        if not hf.communications_test():  
            self.log.warning("Failed the Communications Test")
            return False
        return True
        