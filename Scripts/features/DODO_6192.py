"""
    File name: DODO_6192.py
    Tags:
    Description: Check the PDL for paper checks acceptance and prompt for money code
    Author: 
    Date created: 2019-11-29 07:21:07
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import Navi, mws, pos, system, networksim, crindsim, runas, forecourt_installation
from app import initial_setup
from app.framework import EDH
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app.features import feature_activation, tender
from test_harness import site_type
from Scripts.features import NGFC_Helpers
import time

class DODO_6192():
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

        self.helpers = NGFC_Helpers.NGFC_Helpers(self.log, self.mws)

        self.crindsim = crindsim

        self.check_number = "120174"

        # Setting constants

        self.generic_trans_amount = "5.00"
        self.money_code = "0123456789"
        self.paper_check = "Paper Check"


    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        """
        #if not system.restore_snapshot(snapshot_name="Commercial_Diesel"):
        #    self.log.debug("Commercial Diesel snapshot not available, please run NGFC_setup.py")

        self.log.info("Checking if the newtowrk parser is available")
        comm_test = self.edh.translate_message("Comm Test")

        if not comm_test:
            self.log.error("Network Parser is not available")
            raise Exception
        
        self.log.debug("Enable commercial Checkbox in forecourt")
        self.helpers.set_commercial_on_forecourt()

        # Paper check tender verification
        self.verify_Paper_Check_Tender_Created()

        # HostSim Response mode
        networksim.set_response_mode("Approval")

        # Setting host sim information so we can validate this in the message
        networksim.set_commercial_customer_information("Gilbarco", "Greensboro", "NC", "27410")
        networksim.set_commercial_product_limit("True","CADV","Company funds cash advance",0.00)
        networksim.set_commercial_product_limit("True", "MERC", "Default category for merchandise", 30.00)

        crindsim.set_mode("manual")
        crindsim.set_sales_target()
        crindsim.select_grade(1)

        #open Browser
        
        self.pos.connect()

        self.pos.sign_on()

        self.pos.maximize_pos()
    
    @test
    def DODO_6192_Item_PaperCheck(self):
        """
        Item sale with the use of paper check tender, it will be verified that preauth and completion should contain
        specific value for this tender and the commercial diesel ones.
        """
        #Input constants

        self.check_number = "120175"        
        commercial_prompts = {#"Commercial_prompt" is a dictionary in which are the dinamic prompts for commercial diesel
                        "Enter Check Number": {
                            "entry": [self.check_number],
                            "buttons": ["Enter"]
                        },
                        "Enter Money Code":{
                            "entry": [self.money_code],
                            "buttons": ["Enter"]
                        }#, "Insert Last Name and First Name": {"entry" : ["Juan Jose"],"buttons": ["Ok"]}
                    }

        #Output verifications

        generic_item = '$0.01'
        tender = "PAPER CHK"

        receipt_data = ["Generic Item                     $0.01  99",                        
                        "Subtotal =   $0.01",
                        "Tax  =    $0.00",
                        "Total =   $0.01",
                        "Change Due  =    $0.00",
                        f"{self.paper_check}                      $0.01"]
        self.sale_request_verifications = {
                            'Account Number': self.money_code,
                            'Prompt Code': '3093',
                            '007 - Wex OTR Money Code Check': self.check_number
                            }
        self.sale_response_verifications = {'Response Code': '2', 
                            'Approved Amount': '000000001',
                            '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 0.00',
                            '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00'}
        
        # Setting the suite as commercial
        #self.pos.minimize_pos()

        #self.log.debug("Enable Commercial in forecourt")
        #self.helpers.set_commercial_on_forecourt(enabled=True)

        self.log.debug("Wainting for a idle dispenser to allow the next script to run")
        self.pos.wait_disp_ready(idle_timeout=120)

        self.log.debug("Select back to return to idle screen")      
        self.pos.click_function_key("Back")
        
        # Start execution
        
        self.log.debug("Adding a generic item") 
        self.pos.add_item()

        #look for the last message before payment so we know the messages involved in the transaction
        last_msg = self.edh.get_last_msg_id(pspid='23')

        self.log.debug(f"Pay the {generic_item} with {tender}")
        self.pos.pay(tender_type=tender, prompts=commercial_prompts)

        self.log.debug("Get request and reponse from the EDH")
        messages = self.edh.get_network_messages(4,start_in=last_msg)

        start_time = time.time()
        while len(messages) < 2 and (time.time() - start_time < 60):
            self.log.debug("The expected network messages are not still available, retrying...")
            messages = self.edh.get_network_messages(4,start_in=last_msg)

        if len(messages) < 2:
            
            tc_fail("The messages obtained from the EDH do not contain request and response messages")
  

        self.log.debug("Get last message after the getting the reponse form the host")
        last_msg = self.edh.get_last_msg_id()     
        
        self.log.debug("Translate Request")
        try:
            msg_translated = self.edh.translate_message(messages[1])
        except IndexError as e:
            self.log.error(e)
            tc_fail("Unable to get Request Message")

        current_seq_num = msg_translated ['Sequence Number']['value']

        if msg_translated: # If different of None, it is understood as True
            
            self.edh.verify_field(msg_translated, self.sale_request_verifications)
        
        else:

            tc_fail('Unable to translate the network message')

        self.log.debug("Translate the response")
        try:
            msg_translated = self.edh.translate_message(messages[0])
        except IndexError as e:
            self.log.error(e)
            tc_fail("Unable to get Request Message")

        if msg_translated: # If different of None, it is understood as True
            
            self.edh.verify_field(msg_translated, self.sale_response_verifications)
        
        else:

            tc_fail('Unable to translate the network message')        

        self.log.debug("Chech it there are new messages in NetworkMessages table")
        last_msg = self.helpers.wait_for_new_msg(last_msg, "23") #Waiting for completion messages are generated

        if not last_msg:
            self.log.debug("No new messages were generate since")
        else:
            messages = self.edh.get_network_messages(4,start_in=last_msg)                        
            msg_translated = self.edh.translate_message(messages[1])
            seq_num = msg_translated ['Sequence Number']['value']

            if (seq_num != current_seq_num):
                tc_fail("A completion or others messages were sent, and they should not be sent.")

        # verify that the information on the receipt is correct to be sure that the transaction
        # was approved and the information generated based on that is correct
        self.pos.check_receipt_for(receipt_data, timeout=10)
    
    @test
    def DODO_6192_Prepay_PaperCheck_ReEnterCheckNumber(self):
        """
        Prepay sale the use of paper check tender, it will be verified that the money code or check number is required.
        """
        #Input constants
        
        self.check_number_valid = "120180"

        generic_trans_amount = "$5.00" #any value that gets an approval from the host
        generic_fuel_type = 'Tractor fuel' #any of the fuel types, since is not the objetive of the TC ("Tractor fuel.", "Reefer fuel.", "Both fuels.")
        def_type_yes = 'Yes' #could be "yes" of "no",  because is not the objective of this TC
        papercheck_button_name = 'PAPER CHK'
        default_dispenser = '1' #we need just one dispenser in this test case
        amounts_to_dispense = {
            "buffer_1":{
                "grade": 1,
                "value": "2"
            },
            "buffer_2":{
                "grade": 2,
                "value": "3"
            }
        }
        
        commercial_prompts = {#"Commercial_prompt" is a dictionary in which are the dinamic prompts for commercial diesel
                        "Enter Check Number": {
                            "entry": [self.check_number],
                            "buttons": ["Enter"]
                        },
                        "Enter Money Code":{
                            "entry": [self.money_code],
                            "buttons": ["Enter"]
                        }#, "Insert Last Name and First Name": {"entry" : ["Juan Jose"],"buttons": ["Ok"]}
                    }
        
        #Output verifications

        receipt_data = [f"{self.helpers.grade_1_Name} CA   PUMP# 1",
                        "2.000 GAL @ $1.000/GAL         $2.00  99",
                        f"{self.helpers.grade_2_Name} CA   PUMP# 1",
                        "3.000 GAL @ $1.000/GAL         $3.00  99",
                        "Subtotal =   $5.00",
                        "Tax  =    $0.00",
                        "Total =   $5.00",
                        "Change Due  =    $0.00",
                        f"{self.paper_check}                          $5.00"]

        self.sale_request_verifications = {'Fuel Purchase': '500', 
                            'Account Number': self.money_code,
                            '001 - Wex OTR Flags': 'C - Commercial',
                            'Prompt Code': '3093',
                            '007 - Wex OTR Money Code Check': self.check_number
                            }
        self.sale_response_verifications = {'Response Code': '2', 
                            'Approved Amount': '000000500',
                            '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 0.00',
                            '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',
                            '005 - Wex OTR Customer Information': 'Gilbarco                 Greensboro     NC27410'}

        self.log.info("Setting the CRIND in manual mode")
        crindsim.set_mode("manual")

        # Start execution

        self.pos.maximize_pos()
        
        self.pos.add_fuel(generic_trans_amount,fuel_type = generic_fuel_type, def_type = def_type_yes)

        # Pay the transaction
        self.log.debug("Trying to click Pay")
        if not self.pos.click_function_key('Pay'):
            tc_fail("Unable to press Pay button",exit=True)

        # Find requested key
        self.log.debug(f"Trying to click {papercheck_button_name}")
        if not self.pos.click_tender_key(papercheck_button_name):
            tc_fail(f"Unable to click tender {papercheck_button_name}",exit=True)

        keypad_text = self.pos.read_keypad_prompt(timeout=10)
        self.log.debug(f"The keypad text is {keypad_text}")

        if keypad_text == 'Enter Check Number':
            #self.pos.enter_keyboard_value('')
            self.pos.click_keypad('Enter')

        # Check the invalid check number message
        msg = self.pos.read_message_box()

        # Check for popup about cancellation
        if msg == "Invalid Check Number, Please Try Again":
            self.pos.click_message_box_key("Ok")
        else:
            tc_fail("Wrong button or tender does not work interacting with the network",exit=True)
        
        #look for the last message before payment so we know the messages involved in the transaction
        last_msg = self.edh.get_last_msg_id(pspid='23')

        # Pay the transaction 

        self.log.info("Select cancel to back to the idle screen")
        self.pos.click_keypad('cancel', timeout=30)
        
        self.log.info("Completing the transaction with valid prompts")
        
        self.pos.pay(tender_type="PAPER CHK", prompts=commercial_prompts)

        self.pos.select_dispenser(default_dispenser)

        self.helpers.fuel_handler(amounts_to_dispense)
        # Get messages to check the preauth
        # get the last 4 messages in the DB after payment
        # there is some stuff that is not exactly a message and 
        # we will remove them, we just need 2, preauth and completion
        messages = self.edh.get_network_messages(4,start_in=last_msg)

        start_time = time.time()
        while len(messages) < 2 and (time.time() - start_time < 60):
            self.log.debug("The expected network messages are not still available, retrying...")
            messages = self.edh.get_network_messages(4,start_in=last_msg)

        if len(messages) < 2:
            
            tc_fail("The messages obtained from the EDH do not contain request and response messages")

        self.edh.get_last_msg_id(pspid='23')    

        # Message # 1 should be the preauth request
        msg_translated = self.edh.translate_message(messages[1])        

        if msg_translated: # If different of None, it is understood as True

            current_seq_num = msg_translated ['Sequence Number']['value']
            
            self.edh.verify_field(msg_translated, self.sale_request_verifications)
        
        else:

            tc_fail('Unable to translate the network message')

        # Message # 0 should be the preauth response (order desc)
        msg_translated = self.edh.translate_message(messages[0])

        if msg_translated: # If different of None, it is understood as True
            
            self.edh.verify_field(msg_translated, self.sale_response_verifications)
        
        else:

            tc_fail('Unable to translate the network message')        

        self.pos.select_dispenser(default_dispenser)

        #time.sleep(10) #The wait for fuel make the verifications before it start fueling

        self.pos.wait_for_fuel(default_dispenser, timeout=120)

        # Get messages to check the completion was not generated
        last_msg = self.helpers.wait_for_new_msg(last_msg, "23") #Waiting for completion messages are generated

        if not last_msg:
            self.log.debug("No new messages were generate since last paper check transaction")
        else:
            messages = self.edh.get_network_messages(4,start_in=last_msg)                        
            msg_translated = self.edh.translate_message(messages[1])
            seq_num = msg_translated ['Sequence Number']['value']

            if (seq_num != current_seq_num):
                tc_fail("A completion or others messages were sent, and they should not be sent.")

        # verify that the information on the receipt is correct to be sure that the transaction
        # was approved and the information generated based on that is correct
        self.pos.check_receipt_for(receipt_data, timeout=10)
    
    #TODO: Removing temporarily until PSC-3142 gets fixed
    @test
    def DODO_6192_Prepay_PaperCheck_NoCheckNumber(self):
        """
        Prepay sale the use of paper check tender, it will be verified that the money code or check number is required.
        """
        #Input constants

        generic_trans_amount = "$5.00" #any value that gets an approval from the host
        generic_fuel_type = 'Tractor fuel' #any of the fuel types, since is not the objetive of the TC ("Tractor fuel.", "Reefer fuel.", "Both fuels.")
        def_type_yes = 'Yes' #could be "yes" of "no",  because is not the objective of this TC
        papercheck_button_name = 'PAPER CHK'

        # Start execution
        
        self.pos.add_fuel(generic_trans_amount,fuel_type = generic_fuel_type, def_type = def_type_yes)

        # Pay the transaction
        self.log.debug("Trying to click Pay")
        if not self.pos.click_function_key('Pay'):
            tc_fail("Unable to press Pay button",exit=True)

        # Find requested key
        self.log.debug(f"Trying to click {papercheck_button_name}")
        if not self.pos.click_tender_key(papercheck_button_name):
            tc_fail(f"Unable to click tender {papercheck_button_name}",exit=True)

        keypad_text = self.pos.read_keypad_prompt(timeout=5)
        self.log.debug(f"The keypad text is {keypad_text}")

        if keypad_text == 'Enter Check Number':
            #self.pos.enter_keyboard_value('')
            self.pos.click_keypad('Enter')

        # Check the invalid check number message
        msg = self.pos.read_message_box(timeout=20)
        self.log.info(f"The displayed message after hit enter on 'Enter Check Number' prompt it {msg}")

        # Check for popup about cancellation
        if msg == "Invalid Check Number, Please Try Again":
            self.pos.click_message_box_key("Ok")
        else:
            tc_fail("Wrong button or tender does not work interacting with the network",exit=True)
        
        self.log.info("Select cancel to back to the idle screen")
        self.pos.click_keypad('cancel', timeout=30)

        # void transaction in order to go back to the initial state
        self.pos.void_transaction()
    
    @test
    def DODO_6192_Prepay_PaperCheck_MaxCheckNumber(self):
        """
        Prepay sale the use of paper check tender, it will be verified the max amount of character that
        the money code field can accept.
        """
        #Input constants

        self.check_number_invalid = "1234567890123456"
        self.check_number_valid_mask = "123456XXXXX2345"
        self.check_number_valid = "123456789012345"

        generic_trans_amount = "$5.00" #any value that gets an approval from the host
        generic_fuel_type = 'Tractor fuel' #any of the fuel types, since is not the objetive of the TC ("Tractor fuel.", "Reefer fuel.", "Both fuels.")
        def_type_yes = 'Yes' #could be "yes" of "no",  because is not the objective of this TC
        default_dispenser = '1' #we need just one dispenser in this test case
        amounts_to_dispense = {
            "buffer_1":{
                "grade": 1,
                "value": "2"
            },
            "buffer_2":{
                "grade": 2,
                "value": "3"
            }
        }
        commercial_prompts = {#"Commercial_prompt" is a dictionary in which are the dinamic prompts for commercial diesel
                        "Enter Check Number": {
                            "entry": [self.check_number_valid],
                            "buttons": ["Enter"]
                        },
                        "Enter Money Code":{
                            "entry": [self.money_code],
                            "buttons": ["Enter"]
                        }#, "Insert Last Name and First Name": {"entry" : ["Juan Jose"],"buttons": ["Ok"]}
                    }
        
        #Output verifications

        receipt_data = [f"{self.helpers.grade_1_Name} CA   PUMP# 1",
                        "2.000 GAL @ $1.000/GAL         $2.00  99",
                        f"{self.helpers.grade_2_Name} CA   PUMP# 1",
                        "3.000 GAL @ $1.000/GAL         $3.00  99",
                        "Subtotal =   $5.00",
                        "Tax  =    $0.00",
                        "Total =   $5.00",
                        "Change Due  =    $0.00",
                        f"{self.paper_check}                          $5.00"]

        self.sale_request_verifications = {'Fuel Purchase': '500', 
                            'Account Number': self.money_code,
                            'Prompt Code': '3093',
                            '007 - Wex OTR Money Code Check': self.check_number_valid
                            }
        self.sale_response_verifications = {'Response Code': '2', 
                            'Approved Amount': '000000500',
                            '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 0.00',
                            '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',
                            '005 - Wex OTR Customer Information': 'Gilbarco                 Greensboro     NC27410'}

        self.log.info("Setting the CRIND in manual mode")
        crindsim.set_mode("manual")

        # Start execution

        self.pos.maximize_pos()
        
        self.pos.add_fuel(generic_trans_amount,fuel_type = generic_fuel_type, def_type = def_type_yes)

        #look for the last message before payment so we know the messages involved in the transaction
        last_msg = self.edh.get_last_msg_id(pspid='23')

        # Pay the transaction 
        
        self.pos.pay(tender_type="PAPER CHK", prompts=commercial_prompts)

        self.pos.select_dispenser(default_dispenser)

        self.helpers.fuel_handler(amounts_to_dispense)

        # Get messages to check the preauth
        # get the last 4 messages in the DB after payment
        # there is some stuff that is not exactly a message and 
        # we will remove them, we just need 2, preauth and completion
        messages = self.edh.get_network_messages(4,start_in=last_msg)

        start_time = time.time()
        while len(messages) < 2 and (time.time() - start_time < 60):
            self.log.debug("The expected network messages are not still available, retrying...")
            messages = self.edh.get_network_messages(4,start_in=last_msg)

        if len(messages) < 2:
            
            tc_fail("The messages obtained from the EDH do not contain request and response messages")

        last_msg = self.edh.get_last_msg_id(pspid='23')        
        
        # Message # 1 should be the preauth request
        msg_translated = self.edh.translate_message(messages[1])

        current_seq_num = msg_translated ['Sequence Number']['value']

        if msg_translated: # If different of None, it is understood as True
            
            self.edh.verify_field(msg_translated, self.sale_request_verifications)
        
        else:

            tc_fail('Unable to translate the network message')

        # Message # 0 should be the preauth response (order desc)
        msg_translated = self.edh.translate_message(messages[0])

        if msg_translated: # If different of None, it is understood as True
            
            self.edh.verify_field(msg_translated, self.sale_response_verifications)
        
        else:

            tc_fail('Unable to translate the network message')        

        self.pos.select_dispenser(default_dispenser)

        self.pos.wait_for_fuel(default_dispenser, timeout=120)

        # Get messages to check the completion was not generated
        last_msg = self.helpers.wait_for_new_msg(last_msg, "23") #Waiting for completion messages are generated

        if not last_msg:
            self.log.debug("No new messages were generate since")
        else:
            messages = self.edh.get_network_messages(4,start_in=last_msg)                        
            msg_translated = self.edh.translate_message(messages[1])
            seq_num = msg_translated ['Sequence Number']['value']

            if (seq_num != current_seq_num):
                tc_fail("A completion or others messages were sent, and they should not be sent.")

        # verify that the information on the receipt is correct to be sure that the transaction
        # was approved and the information generated based on that is correct
        self.pos.check_receipt_for(receipt_data, timeout=10)
    
    @test
    def DODO_6192_Prepay_PaperCheck_Underrun(self):
        """
        Prepay sale the use of paper check tender, it will be verified that preauth and completion should contain
        specific value for this tender and the commercial diesel ones.
        """
        #Input constants

        self.check_number = "120178"

        generic_trans_amount = "$5.00" #any value that gets an approval from the host
        generic_fuel_type = 'Tractor fuel' #any of the fuel types, since is not the objetive of the TC ("Tractor fuel.", "Reefer fuel.", "Both fuels.")
        def_type_yes = 'Yes' #could be "yes" of "no",  because is not the objective of this TC
        default_dispenser = '1' #we need just one dispenser in this test case
        amounts_to_dispense = {
            "buffer_1":{
                "grade": 1,
                "value": "2"
            },
            "buffer_2":{
                "grade": 2,
                "value": "2"
            }
        }

        commercial_prompts = {#"Commercial_prompt" is a dictionary in which are the dinamic prompts for commercial diesel
                        "Enter Check Number": {
                            "entry": [self.check_number],
                            "buttons": ["Enter"]
                        },
                        "Enter Money Code":{
                            "entry": [self.money_code],
                            "buttons": ["Enter"]
                        }#, "Insert Last Name and First Name": {"entry" : ["Juan Jose"],"buttons": ["Ok"]}
                    }
        
        #Output verifications

        receipt_data = [f"{self.helpers.grade_1_Name} CA   PUMP# 1",
                        "2.000 GAL @ $1.000/GAL         $2.00  99",
                        f"{self.helpers.grade_1_Name} CA   PUMP# 1",
                        "2.000 GAL @ $1.000/GAL         $2.00  99",
                        "Subtotal =   $4.00",
                        "Tax  =    $0.00",
                        "Total =   $4.00",
                        "Change Due  =    $-1.00",
                        f"{self.paper_check}                          $5.00"]

        self.sale_request_verifications = {'Fuel Purchase': '500', 
                            'Account Number': self.money_code,
                            'Prompt Code': '3093',
                            '007 - Wex OTR Money Code Check': self.check_number
                            }
        self.sale_response_verifications = {'Response Code': '2', 
                            'Approved Amount': '000000500',
                            '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 0.00',
                            '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',
                            '005 - Wex OTR Customer Information': 'Gilbarco                 Greensboro     NC27410'}

        # Specific configuration Crindsim
        self.crindsim.set_sales_target("money", "2")

        # Start execution

        self.pos.maximize_pos()

        self.pos.add_fuel(generic_trans_amount,fuel_type = generic_fuel_type, def_type = def_type_yes)

        #look for the last message before payment so we know the messages involved in the transaction
        last_msg = self.edh.get_last_msg_id(pspid='23')

        # Pay the transaction 
        #self.pos.pay_card(brand = "EXXON", card_name = card_to_use_NGFC, commercial_prompts = commercial_prompt)
        #self.pos.pay_card(card_name = card_to_use, brand="Exxon", prompts= commercial_prompts)
        self.pos.pay(tender_type="PAPER CHK", prompts=commercial_prompts)
    
        self.pos.select_dispenser(default_dispenser)

        self.helpers.fuel_handler(amounts_to_dispense)
        # Get messages to check the preauth
        # get the last 4 messages in the DB after payment
        # there is some stuff that is not exactly a message and 
        # we will remove them, we just need 2, preauth and completion
        messages = self.edh.get_network_messages(4,start_in=last_msg)

        start_time = time.time()
        while len(messages) < 2 and (time.time() - start_time < 60):
            self.log.debug("The expected network messages are not still available, retrying...")
            messages = self.edh.get_network_messages(4,start_in=last_msg)

        if len(messages) < 2:
            
            tc_fail("The messages obtained from the EDH do not contain request and response messages")

        last_msg = self.edh.get_last_msg_id(pspid='23')                
        
        # Message # 1 should be the preauth request
        msg_translated = self.edh.translate_message(messages[1])
        
        if msg_translated: # If different of None, it is understood as True

            current_seq_num = msg_translated ['Sequence Number']['value']
            
            self.edh.verify_field(msg_translated, self.sale_request_verifications)
        
        else:

            tc_fail('Unable to translate the network message')

        # Message # 0 should be the preauth response (order desc)
        msg_translated = self.edh.translate_message(messages[0])

        if msg_translated: # If different of None, it is understood as True
            
            self.edh.verify_field(msg_translated, self.sale_response_verifications)
        
        else:

            tc_fail('Unable to translate the network message')        

        self.pos.select_dispenser(default_dispenser)

        #self.pos.wait_for_disp_status("Fueling", verify=False)

        #self.pos.wait_for_fuel(default_dispenser, timeout=120)
        self.pos.wait_disp_ready()

        #look for the last message before payment so we know the messages involved in the transaction

        last_msg = self.edh.get_last_msg_id(pspid='23')

        # Select the buffer to complete the transaction, this happens because we said when we paid
        # that we will add addition products self.pos.pay_card(card_name='NGFC', additional_prod = 'Yes')
        self.pos.click_fuel_buffer('Commercial')

        #Commercial transaction set with additional product need to hit pay to complete the transaction
        self.pos.click_function_key('Pay')

        self.pos.click_tender_key("exact change", verify=False)

        # Get messages to check the completion was not generated
        last_msg = self.helpers.wait_for_new_msg(last_msg, "23") #Waiting for completion messages are generated

        if not last_msg:
            self.log.debug("No new messages were generate since")
        else:
            messages = self.edh.get_network_messages(4,start_in=last_msg)                        
            msg_translated = self.edh.translate_message(messages[1])
            seq_num = msg_translated ['Sequence Number']['value']

            if (seq_num != current_seq_num):
                tc_fail("A completion or others messages were sent, and they should not be sent.")

        # verify that the information on the receipt is correct to be sure that the transaction
        # was approved and the information generated based on that is correct
        self.pos.check_receipt_for(receipt_data, timeout=10)
    
    #TODO: Removing Temporarily until PSC-3142 gets fixed
    @test
    def DODO_6192_Item_PaperCheck_Decline(self):
        """
        Item sale with the use of paper check tender, it will be verified that preauth and completion should contain
        specific value for this tender and the commercial diesel ones.
        """
        #Input constants

        check_number = "120174"
        generic_trans_amount = "$5.00" #any value that gets an approval from the host
        generic_fuel_type = 'Tractor fuel' #any of the fuel types, since is not the objetive of the TC ("Tractor fuel.", "Reefer fuel.", "Both fuels.")
        def_type_yes = 'Yes' #could be "yes" of "no",  because is not the objective of this TC
        commercial_prompts = {#"Commercial_prompt" is a dictionary in which are the dinamic prompts for commercial diesel
                        "Enter Check Number": {
                            "entry": [check_number],
                            "buttons": ["Enter"]
                        }, #"Insert Last Name and First Name": {"entry" : ["Juan Jose"],"buttons": ["Ok"]}
                        ".CALL AUTH CTR F3.": {
                            "buttons": ["Ok"]
                        },
                        "Enter Money Code":{
                            "entry": [self.money_code],
                            "buttons": ["Enter"]
                        },
                        "Enter Cash amount": {
                            "entry": ["0"],
                            "buttons": ["Cancel"]
                        }
                    }

        #Output verifications

        self.sale_request_verifications = {'Account Number': self.money_code,
                            'Prompt Code': '3093',
                            '001 - Wex OTR Flags': 'C - Commercial',
                            '007 - Wex OTR Money Code Check': check_number
                            }
        self.sale_response_verifications = {'Response Code': '1',
                            'Decline Code': 'F3',
                            'Approved Amount': '000000500'
                            }
        
        # Host specific configuration - Response mode
        networksim.set_response_mode('F3')
                
        # Adding a prepay
        self.pos.add_fuel(generic_trans_amount,fuel_type = generic_fuel_type, def_type = def_type_yes)

        #look for the last message before payment so we know the messages involved in the transaction
        last_msg = self.edh.get_last_msg_id(pspid='23')

        # Pay the transaction 
        self.pos.pay(tender_type="PAPER CHK", prompts=commercial_prompts)
 
        # Get messages to check the preauth
        # get the last 4 messages in the DB after payment
        # there is some stuff that is not exactly a message and 
        # we will remove them, we just need 2, preauth and completion
        messages = self.edh.get_network_messages(4,start_in=last_msg)

        start_time = time.time()
        while len(messages) < 2 and (time.time() - start_time < 60):
            self.log.debug("The expected network messages are not still available, retrying...")
            messages = self.edh.get_network_messages(4,start_in=last_msg)

        if len(messages) < 2:
            
            tc_fail("The messages obtained from the EDH do not contain request and response messages")
        
        last_msg = self.edh.get_last_msg_id(pspid='23')        

        self.log.debug("Translate the Request, the messages are obtined by id desc")
        try:
            msg_translated = self.edh.translate_message(messages[1])
        except IndexError as e:
            self.log.error(e)
            tc_fail("Unable to get Request Message")

        if msg_translated: # If different of None, it is understood as True
            
            self.edh.verify_field(msg_translated, self.sale_request_verifications)
        
        else:

            tc_fail('Unable to translate the network message')

        self.log.debug("Translate the Response, the messages are obtined by id desc")
        try:
            msg_translated = self.edh.translate_message(messages[0])
        except IndexError as e:
            self.log.error(e)
            tc_fail("Unable to get Response Message")

        if msg_translated: # If different of None, it is understood as True
            
            self.edh.verify_field(msg_translated, self.sale_response_verifications)
        
        else:

            tc_fail('Unable to translate the network message')
        
        self.pos.void_transaction()

        networksim.set_response_mode('Approval')
    
    @test
    def DODO_6192_Item_PaperCheck_Timeout(self):
        """
        Item sale with the use of paper check tender, it will be verified that preauth and completion should contain
        specific value for this tender and the commercial diesel ones.
        """
        #Input constants

        check_number = "120178"
        generic_trans_amount = "$5.00" #any value that gets an approval from the host
        generic_fuel_type = 'Tractor fuel' #any of the fuel types, since is not the objetive of the TC ("Tractor fuel.", "Reefer fuel.", "Both fuels.")
        def_type_yes = 'Yes' #could be "yes" of "no",  because is not the objective of this TC
        default_dispenser = '1' #we need just one dispenser in this test case
        commercial_prompts = {#"Commercial_prompt" is a dictionary in which are the dinamic prompts for commercial diesel
                        "Enter Check Number": {
                            "entry": [check_number],
                            "buttons": ["Enter"]
                        },
                        "No Response from Host. Please, contact WEX Customer Service": {
                            "buttons": ["Ok"]
                        },
                        "Enter Money Code":{
                            "entry": [self.money_code],
                            "buttons": ["Enter"]
                        }
                    }

        #Output verifications

        self.sale_request_verifications = {'Account Number': self.money_code,                            
                            '007 - Wex OTR Money Code Check': check_number
                            }
        self.sale_response_verifications = {'Response Code': '2', 
                            'Approved Amount': '000000500',
                            '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 0.00',
                            '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00'}
        
        # Host specific configuration - Response mode
        networksim.set_response_mode('Timeout')

        # Start execution

        self.pos.maximize_pos()
        
        # Adding a generic item
        self.pos.add_fuel(generic_trans_amount,fuel_type = generic_fuel_type, def_type = def_type_yes)

        #look for the last message before payment so we know the messages involved in the transaction
        last_msg = self.edh.get_last_msg_id(pspid='23')

        # Pay the transaction 
        self.pos.pay(tender_type="PAPER CHK", prompts=commercial_prompts, timeout_transaction= True)
        
        self.log.debug("Wait for new messages in the EDH so we can check the messages involved in the transaction")
        last_msg = self.helpers.wait_for_new_msg(last_msg, '23')
        
        messages = self.edh.get_network_messages(4,start_in=last_msg)

        start_time = time.time()
        while len(messages) < 1 and (time.time() - start_time < 60):
            self.log.debug("The expected network messages are not still available, retrying...")
            messages = self.edh.get_network_messages(2,start_in=last_msg)

        if len(messages) < 1:
            
            tc_fail("The messages obtained from the EDH do not contain request and response messages")

        
        last_msg = self.edh.get_last_msg_id(pspid='23')             
        
        # Message # 0 should be the preauth request
        msg_translated = self.edh.translate_message(messages[0])

        if msg_translated: # If different of None, it is understood as True
            
            self.edh.verify_field(msg_translated, self.sale_request_verifications)
        
        else:

            tc_fail('Unable to translate the network message')

        self.log.debug("Attempting to complete the transaction to leave temrinal in the initial state")
        
        response_mode_status = networksim.set_response_mode('Approval')
        
        response_mode = networksim.get_response_mode()
        
        if not response_mode['payload']['sim_mode'] == "Fixed 'Approval'" and response_mode_status['success']:
            tc_fail("Host simulator was unable to back to Approval mode")

        self.crindsim.set_sales_target()

        self.log.info("Select cancel to back to the idle screen")
        self.pos.click_keypad('Cancel')
        time.sleep(2)
        
        self.log.info("Trying to void transaction")
        result = self.pos.void_transaction()
        
        if not result:
            tc_fail("Transaction void failed")
            return False

        self.log.info(f"Result of void transaction: {result}")
    
    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        self.pos.close()

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
    
    

    
        