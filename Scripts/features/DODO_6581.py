"""
    File name: DODO_6581.py
    Tags:
    Description: Send the prompt code in the segment 100 with a 3093 value for paper checks
    Author: 
    Date created: 2020-09-25 14:56:30
    Date last modified: 
    Python Version: 3.7
"""

import logging
import time
from app import Navi, mws, pos, networksim, crindsim
from app.framework import EDH
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app.features import  tender
from Scripts.features import NGFC_Helpers


class DODO_6581():
    """
    Description: As Passport, I need to send the prompt code in the segment 100 to the host with a 3093 value for paper checks.
    """

    def __init__(self):
        """
        Initializes the Template class.
        """
        # The logging object. 
        # Example: self.log.info(f"Current value of var: {my_var}")
        # The logging object.         
        self.log = logging.getLogger()

        # The main NETWORK SIMULATOR object
        self.networksim = networksim

        # The main MWS object 
        self.mws = mws
        
        # The main POS object
        self.pos = pos

        # The main POS object
        self.tender = tender

        # The main EDH object
        self.edh = EDH.EDH()

        self.helpers = NGFC_Helpers.NGFC_Helpers(self.log, self.mws, self.pos)

        self.crindsim = crindsim

        self.check_number = "9873214560"

        self.money_code = "0654789321"

        self.paper_check = "Paper Check"

        self.papercheck_button_name = 'PAPER CHK'

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

        # Paper check tender verification
        self.verify_Paper_Check_Tender_Created()

        # HostSim Response mode
        networksim.set_response_mode("Approval")

        networksim.set_commercial_customer_information("Gilbarco", "Greensboro", "NC", "27410")
        networksim.set_commercial_product_limit("True", "CADV", "Company funds cash advance", 0.00)
        networksim.set_commercial_product_limit(
                            "True", 
                            "MERC", 
                            "Default category for merchandise",
                             30.00)
        
        crindsim.set_mode("manual")
        crindsim.set_sales_target()
        crindsim.select_grade(1)

        #open Browser
        
        self.pos.connect()

        self.pos.sign_on()

        self.pos.minimize_pos()

    
    @test
    def Papercheck_Cashadvance_Yes(self):
        """
        In a transaction with a paper check at a commercial dispenser, the prompt code is correctly reported to the host.
        """
        
        networksim.set_commercial_product_limit("True","CADV","Company funds cash advance",30.00)

        generic_fuel_type = 'Tractor fuel' #any of the fuel types, since is not the objetive of the TC ("Tractor fuel.", "Reefer fuel.", "Both fuels.")
        def_type_yes = 'No' #could be "yes" of "no",  because is not the objective of this TC
        generic_trans_amount = "$5.00" #any value that gets an approval from the host

        commercial_prompts = {#"Commercial_prompt" is a dictionary in which are the dinamic prompts for commercial diesel
                "Enter Check Number": {
                    "entry": [self.check_number],
                    "buttons": ["Enter"]
                },
                "Enter Money Code":{
                    "entry": [self.money_code],
                    "buttons": ["Enter"]
                },
                "Cash advance up to $30.00?": {
                    "buttons": ["Yes"]
                },
                "Enter cash advance amount": {
                    "entry": [200],
                    "buttons": ["Enter"]
                },
                "Your cash drawer WILL NOT OPEN until the printer is working.": {
                    "buttons": ["Ok"]
                }
        }

        amounts_to_dispense = {
            "buffer_1":{
                "grade": 1,
                "value": ""
            }
        }

        #Output verifications

        messages_to_verify = {
            'preauth_request_verifications': {
                            '007 - Wex OTR Money Code Check': '9873214560', 
                            'Prompt Code': '3093',
                            '001 - Wex OTR Flags': 'C - Commercial'
                            },
            'preauth_response_verifications': {                            
                            'Approved Amount': '000000700'
            }
        }
        
        message_types = [
            "preauth_request_verifications",
            "preauth_response_verifications",
        ]

        self.helpers.set_cash_advance_on_mws('3000')
        
        self.log.info("Setting the CRIND in manual mode")
        crindsim.set_mode("manual")

        # Start execution

        self.pos.maximize_pos()

        last_msg = self.edh.get_last_msg_id(pspid='23')
        
        self.pos.add_fuel(generic_trans_amount,fuel_type = generic_fuel_type, def_type = def_type_yes)

        self.pos.pay(tender_type=self.papercheck_button_name, prompts = commercial_prompts)

        self.helpers.fuel_handler(amounts_to_dispense)

        self.pos.wait_for_fuel(timeout=180)

        self.log.info("Select Commercial Buffer")
        self.pos.click_fuel_buffer('commercial')

        self.log.info("Select Pay Button")
        self.pos.click_function_key('Pay')  

        self.log.info("Answer no to Receipt prompt")            
        if not self.pos.click_message_box_key('No', timeout=30):
            tc_fail("The terminal din't prompt for receipt and it should be doing that")

        self.log.debug("Try to get 2 messages (sale)")
        messages = self.edh.get_network_messages(4,start_in=last_msg)
        
        start_time = time.time()
        while len(messages) < 2 and (time.time() - start_time < 60):
            self.log.debug("There are messages pending to be generated, retrying to get all of them.")
            messages = self.edh.get_network_messages(4,start_in=last_msg)
        if len(messages) < 2:
            tc_fail("The messages obtained from the EDH do not contain all requests and responses messages")

        messages_num = len(messages_to_verify)

        for x in message_types:
            
            try:
                self.log.debug(f"Validation of {x}")
                messages_num = messages_num - 1
                msg_translated = self.edh.translate_message(messages[messages_num])
                fields_to_verify = messages_to_verify[x]

                if msg_translated: # If different of False, it is understood as True
                    self.edh.verify_field(msg_translated, fields_to_verify)
                else:
                    tc_fail('Unable to translate the network message')
                
            except KeyError as e:
                tc_fail(f'Failed trying to translate a message: {e}')
    
    @test
    def Papercheck_DryStock_Cashadvance_Yes(self):
        """
        In a paper check transaction where dry stock is purchased and fuel is dispensed from a commercial dispenser, the prompt code is correctly reported to the host.
        """
        
        networksim.set_commercial_product_limit("True","CADV","Company funds cash advance",30.00)

        generic_fuel_type = 'Tractor fuel' #any of the fuel types, since is not the objetive of the TC ("Tractor fuel.", "Reefer fuel.", "Both fuels.")
        def_type_yes = 'No' #could be "yes" of "no",  because is not the objective of this TC
        generic_trans_amount = "$10.00" #any value that gets an approval from the host

        commercial_prompts = {#"Commercial_prompt" is a dictionary in which are the dinamic prompts for commercial diesel
                "Enter Check Number": {
                    "entry": [self.check_number],
                    "buttons": ["Enter"]
                },
                "Enter Money Code":{
                    "entry": [self.money_code],
                    "buttons": ["Enter"]
                },
                "Cash advance up to $30.00?": {
                    "buttons": ["Yes"]
                },
                "Enter cash advance amount": {
                    "entry": [200],
                    "buttons": ["Enter"]
                },
                "Your cash drawer WILL NOT OPEN until the printer is working.": {
                    "buttons": ["Ok"]
                }
        }

        amounts_to_dispense = {
            "buffer_1":{
                "grade": 1,
                "value": ""
            }
        }

        #Output verifications

        messages_to_verify = {
            'preauth_request_verifications': {
                            '007 - Wex OTR Money Code Check': '9873214560', 
                            'Prompt Code': '3093',
                            '001 - Wex OTR Flags': 'C - Commercial'
                            },
            'preauth_response_verifications': {                            
                            'Approved Amount': '000012010'
            }
        }
        
        message_types = [
            "preauth_request_verifications",
            "preauth_response_verifications",
        ]

        #self.helpers.set_cash_advance_on_mws('3000')
        
        self.log.info("Setting the CRIND in manual mode")
        crindsim.set_mode("manual")

        # Start execution

        self.pos.maximize_pos()

        self.pos.add_item()
        
        self.pos.add_fuel(generic_trans_amount,fuel_type = generic_fuel_type, def_type = def_type_yes)

        last_msg = self.edh.get_last_msg_id(pspid='23')

        self.pos.pay(tender_type=self.papercheck_button_name, prompts = commercial_prompts)

        self.helpers.fuel_handler(amounts_to_dispense)

        self.pos.wait_for_fuel(timeout=240)

        self.log.info("Select Commercial Buffer")
        self.pos.click_fuel_buffer('commercial')

        self.log.info("Select Pay Button")
        self.pos.click_function_key('Pay')  

        self.log.info("Answer no to Receipt prompt")            
        if not self.pos.click_message_box_key('No', timeout=30):
            tc_fail("The terminal din't prompt for receipt and it should be doing that")

        self.log.debug("Try to get 2 messages (sale)")
        messages = self.edh.get_network_messages(4,start_in=last_msg)
        
        start_time = time.time()
        while len(messages) < 2 and (time.time() - start_time < 60):
            self.log.debug("There are messages pending to be generated, retrying to get all of them.")
            messages = self.edh.get_network_messages(4,start_in=last_msg)
        if len(messages) < 2:
            tc_fail("The messages obtained from the EDH do not contain all requests and responses messages")

        messages_num = len(messages_to_verify)

        for x in message_types:
            
            try:
                self.log.debug(f"Validation of {x}")
                messages_num = messages_num - 1
                msg_translated = self.edh.translate_message(messages[messages_num])
                fields_to_verify = messages_to_verify[x]

                if msg_translated: # If different of False, it is understood as True
                    self.edh.verify_field(msg_translated, fields_to_verify)
                else:
                    tc_fail('Unable to translate the network message')
                
            except KeyError as e:
                tc_fail(f'Failed trying to translate a message: {e}')


    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        self.pos.close()
        self.helpers.set_cash_advance_on_mws('000')
        networksim.set_commercial_product_limit("True","CADV","Company funds cash advance",00.00)

    def verify_Paper_Check_Tender_Created(self):
        """
        it verifies if paper check tender is already created, if not, it creates it.
        """
        
        #Input constants 
        papercheck_tender_name = 'Paper Check'
        papercheck_tender_group = 'Integrated Commercial Check'
        papercheck_button_name = 'PAPER CHK'

        tender_info = {
                "Tender Code": "1234",
                "Tender Description": papercheck_tender_name,
                "General": {
                    "Tender group this tender belongs to": papercheck_tender_group,
                    "Receipt Description": papercheck_tender_name,
                    "Tender Button Description": papercheck_button_name,
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
        Navi.navigate_to("tender maintenance")

        # Check to see if tender to add already exists...
        if mws.set_value("Tenders", papercheck_tender_name):
            return True
        else:
            self.log.debug(f"Adding {papercheck_tender_name}, since it was not created previously.")
            
            # tender maintenance configuration for paper check
            tm = tender.TenderMaintenance()
            tm.configure(papercheck_tender_name, tender_info, True)
    
