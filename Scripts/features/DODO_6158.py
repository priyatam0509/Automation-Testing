"""
    File name: DODO_6159.py
    Tags:
    Description: Test scripts meant to verify correct prossesing of customer information
    and correct printing on receipts.
    Author: Javier Sandoval
    Date created: 2020-04-23 14:00:00
    Date last modified: 2020-04-27 17:00:00
    Python Version: 3.7
"""

import logging
from app import Navi, mws, pos, system, forecourt_installation, networksim, crindsim, runas, network_site_config
from app.framework import EDH
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app.features import feature_activation
from Scripts.features import NGFC_Helpers
import time

class DODO_6158():
    """
    Description: Process customer information and print it in the inside
    NGFC cards transactions receipts
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

        # The main crind sim object
        self.crindsim = crindsim

        # Customer information values
        self.customerInfo = ["AB TRUCKING", "DENVER", "CO", "234W987"]

 
    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        """

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

        # Set specif config for this script
        networksim.set_commercial_customer_information(self.customerInfo[0], self.customerInfo[1], self.customerInfo[2], self.customerInfo[3])
        networksim.set_commercial_product_limit("True","CADV","Company funds cash advance",20.00)
        networksim.set_commercial_product_limit("True", "MERC", "Default category for merchandise", 30.00)        
        networksim.set_commercial_fuel_limit("True", self.helpers.grade_1_Product, 50.00)
        networksim.set_commercial_fuel_limit("True", self.helpers.grade_2_Product, 50.00)
        networksim.set_commercial_fuel_limit("True", self.helpers.grade_3_Product, 50.00)
        networksim.set_commercial_fuel_limit_send_mode("fuel product configuration based",110,True)

        crindsim.set_mode("auto")
        crindsim.set_sales_target()
        crindsim.select_grade(1)

        #open Browser
        self.pos.connect()
        self.pos.sign_on()
    
    @test
    def NGFC_CustomerInformation_DataBAse(self): #1
        """
        Prepay transactions with NGFC cards with customer information
        sent from the host, the information should be stores in data base:
        FDC_TransactionData table, WexOTRSegData field.
        """
        #Input constants

        tractor_fuel_type = 'Tractor fuel' # this is tractor fuel,  because is the objective of this testcase
        def_type_no = 'No' # this is "no",  because is the objective of this testcase
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts        
        generic_trans_amount = "$5.00"
        default_dispenser = '1' # we need just one dispenser in this test case
        customer_information = self.customerInfo[0] + (' ' * 14) + self.customerInfo[1] +(' ' * 9) + self.customerInfo[2] + self.customerInfo[3]
        commercial_prompts = {              
                    "Additional Products Y/N?": {                    
                        "buttons": ["No"]
                    }
                }
        amounts_to_dispense = {
            "buffer_1":{
                "grade": 1,
                "value": "5"
            }
        }
        
        #Output verifications

        self.preauth_request_verifications = {
            'Fuel Purchase': '500', 
            '001 - Wex OTR Flags': 'C - Commercial'}

        self.preauth_response_verifications = {
            'Response Code': '2', 
            'Approved Amount': '000000500',
            '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 0.00',
            '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',
            f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_1_Product}': 'Product limit: 50.00',
            f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_2_Product}': 'Product limit: 50.00',
            f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_3_Product}': 'Product limit: 50.00',
            '005 - Wex OTR Customer Information': customer_information}

        self.capture_request_verifications = {
            'Fuel Purchase': '500',
            'Number of Products': '01',
            'Prod 1 product Amount': '500',
            'Prod 1 product Code': f'{self.helpers.grade_1_Product}',
            '001 - Wex OTR Flags': 'C - Commercial'}

        self.capture_response_verifications = {
            'Response Code': '0', 
            'Approved Amount': '000000500',
            '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 20.00',
            '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',
            f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_1_Product}': 'Product limit: 50.00',
            f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_2_Product}': 'Product limit: 50.00',
            f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_3_Product}': 'Product limit: 50.00',
            '005 - Wex OTR Customer Information': customer_information}
        
        self.log.debug("Trying to set crind to dispense automatically")
        crindsim.set_mode("manual")

        self.log.debug("look for the last message before start, so then messages involved in the transaction will be known.")
        last_msg = self.edh.get_last_msg_id(pspid='23')

        self.log.debug("Geting last record on FDC_TransactionData table")
        query = "Select top 1 GPTransactionCookie from FDC_TransactionData order by GPTransactionCookie desc"
        output = runas.run_sqlcmd(query, database="network", cmdshell=False)['output']
        #Turning string into list of strings that have \n delimitation
        output_list = output.split("\n")
        output_list = output_list[2:-3]
        if len(output_list) != 0:
            transaction_cookie = output_list[0].replace(" ", "")
        else:
            self.log.debug("This transaction is the first one that would be stored at FDC_TransactionData table.")
            transaction_cookie = '0'

        self.log.debug("Selecting dispenser and starting a prepay transaction")
        self.pos.select_dispenser(default_dispenser)
        self.pos.add_fuel(generic_trans_amount,fuel_type = tractor_fuel_type, def_type = def_type_no)

        self.log.debug("Paying prepay")
        self.pos.pay_card(brand="Exxon", card_name = card_to_use_NGFC, prompts=commercial_prompts)

        self.log.debug("Wait for fueling ends.")
        self.helpers.fuel_handler(amounts_to_dispense)

        """ 
         Clarification:
         Get the last 8 messages in the DB after payment. There is 
         some stuff that is not exactly a message and it will be removed,
         just 4 messages ares needed: preauth and completion request and response.
         These will be get all together because transaction end inside
         since there is no cash advance and the answer for additional
         products was NO.
        """

        self.log.debug("Try to get 4 messages (preauth and completion)")
        messages = self.edh.get_network_messages(8,start_in=last_msg)
        start_time = time.time()
        while len(messages) < 4 and (time.time() - start_time < 60):
            self.log.debug("There are messages pending to be generated, retrying to get all of them.")
            messages = self.edh.get_network_messages(8,start_in=last_msg)
        if len(messages) < 4:
            tc_fail("The messages obtained from the EDH do not contain all requests and responses messages")
        
        ### PREAUTH MESSAGES ###
        self.log.debug("Validation of message # 3, it should be the preauth request")
        msg_translated = self.edh.translate_message(messages[3])

        if msg_translated: # If different of False, it is understood as True
            self.edh.verify_field(msg_translated, self.preauth_request_verifications)
        else:
            tc_fail('Unable to translate the network message')

        self.log.debug("Validation of message # 2, it should be the preauth response")
        msg_translated = self.edh.translate_message(messages[2])

        if msg_translated: # If different of False, it is understood as True            
            self.edh.verify_field(msg_translated, self.preauth_response_verifications)
        else:
            tc_fail('Unable to translate the network message')
        #########################
        
        ### COMPLETION MESSAGES ###        
        self.log.debug("Validation of message # 1, it should be the completion request")
        msg_translated = self.edh.translate_message(messages[1])

        if msg_translated: # If different of False, it is understood as True
            self.edh.verify_field(msg_translated, self.capture_request_verifications)
        else:
            tc_fail('Unable to translate the network message')

        # Message # 0 should be the preauth response (order desc)
        self.log.debug("Validation of message # 0, it should be the completion response")
        msg_translated = self.edh.translate_message(messages[0])

        if msg_translated: # If different of False, it is understood as True    
            self.edh.verify_field(msg_translated, self.capture_response_verifications)
        else:
            tc_fail('Unable to translate the network message')
        ############################

        query = "Select top 1 GPTransactionCookie, '/', WexOTRCustomerInfo from FDC_TransactionData order by GPTransactionCookie desc"
        output = runas.run_sqlcmd(query, database="network", cmdshell=False)['output']
        #Turning string into list of strings that have \n delimitation
        output_list = output.split("\n")
        output_list = output_list[2:-3]
        #Separating transaction cookie from customer information
        for value in output_list:
            keyValue = value.split("/")
            keyValue[0] = keyValue[0].replace(" ", "")
            keyValue[1] = keyValue[1].rstrip()
            keyValue[1] = keyValue[1].lstrip()
        
        if keyValue[0] != transaction_cookie:
            if not customer_information == keyValue[1]: #Compare customer information set with a posibly store value at DB
                tc_fail('Customer information was not stored correctly on data base')
        else:
            tc_fail(f'No new records, transaction cookie at beginning: {transaction_cookie}')

        #self.pos.click_function_key("Back")
    
    @test
    def NGFC_CustomerInformation_Receipt(self): #2
        """
        Prepay transactions with NGFC cards with customer information
        sent from the host, the information should be printed on receipt.
        """
        #Input constants

        generic_trans_amount = "$5.00" # any value that gets an approval from the host
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts
        customer_information = self.customerInfo[0] + (' ' * 14) + self.customerInfo[1] +(' ' * 9) + self.customerInfo[2] + self.customerInfo[3]
        
        amounts_to_dispense = {
            "buffer_1":{
                "grade": 1,
                "value": "5"
            }
        }

        prompts = {

            "Additional Products Y/N?": {                    
                "buttons": ["No"]
            },
            "Do you want to print a receipt?": {
                "buttons": ["No"]
            },
            "Select fuel products to dispense": {
                "buttons": ["Tractor fuel"]
            },
            "DEF?": {
                "buttons": ["No"]
            }
        }

        #Output verifications

        receipt_data = [f"{self.helpers.grade_1_Name} CA   PUMP# 1",
                        "5.000 GAL @ $1.000/GAL         $5.00  99",
                        "Subtotal =   $5.00",
                        "Tax  =    $0.00",
                        "Total =   $5.00",
                        "Credit                          $5.00",
                        "Customer Information",
                        "Name: " + self.customerInfo[0],
                        "City: " + self.customerInfo[1],
                        "State: " + self.customerInfo[2],
                        "Acc.: " + self.customerInfo[3]]

        messages_to_verify = {
            'preauth_request_verifications' : {
                'Fuel Purchase': '500', 
                '001 - Wex OTR Flags': 'C - Commercial'},
            'preauth_response_verifications': {
                'Response Code': '2', 
                'Approved Amount': '000000500',
                '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 0.00',
                '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_1_Product}': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_2_Product}': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_3_Product}': 'Product limit: 50.00',
                '005 - Wex OTR Customer Information': f'{customer_information}'},
            'capture_request_verifications': {
                'Fuel Purchase': '500',
                'Number of Products': '01',
                'Prod 1 product Amount': '500',
                'Prod 1 product Code': f'{self.helpers.grade_1_Product}',
                '001 - Wex OTR Flags': 'C - Commercial'},
            'capture_response_verifications': {
                'Response Code': '0', 
                'Approved Amount': '000000500',
                '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 20.00',
                '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_1_Product }': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_2_Product }': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_3_Product }': 'Product limit: 50.00',
                '005 - Wex OTR Customer Information': f'{customer_information}'}
        }

        self.helpers.prepay_transaction(
            card=card_to_use_NGFC,
            prepay_amount=generic_trans_amount,
            prompts=prompts,
            amounts_to_dispense=amounts_to_dispense,
            messages_to_verify=messages_to_verify,
            receipt_data=receipt_data
            )
    
    '''
    #TODO: Removing this test case given that the simulator allways return a value so the lines are always printed
    @test
    def NGFC_CustomerInformation_AllEmptyFields(self): #3
        """
        For the inside transactions with NGFC Cards, if all the customer information fields
        are empty, the data base should not save any data about customer information and the
        receipt should not show any information about that.
        table -> FDC_TransactionData
        field -> WexOTRSegData
        """

        tractor_fuel_type = 'Tractor fuel' # this is tractor fuel,  because is the objective of this testcase
        def_type_no = 'No' # this is "no",  because is the objective of this testcase
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts
        generic_trans_amount = "$5.03"
        default_dispenser = '1' # we need just one dispenser in this test case
        customer_information = ''
        commercial_prompts = {              
                    "Additional Products Y/N?": {                    
                        "buttons": ["No"]
                    }
                }

        #Output verifications

        receipt_data = [f"{self.helpers.grade_1_Name} CA   PUMP# 1",
                        "5.030 GAL @ $1.000/GAL         $5.03  99",
                        "Subtotal =   $5.03",
                        "Tax  =    $0.00",
                        "Total =   $5.03",
                        "Change Due  =    $0.00",
                        "Credit                          $5.03"]

        self.preauth_request_verifications = {
            'Fuel Purchase': '503', 
            '001 - Wex OTR Flags': 'C - Commercial'}

        self.preauth_response_verifications = {
            'Response Code': '2', 
            'Approved Amount': '000000503',
            '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 0.00',
            '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',
            f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_1_Product}': 'Product limit: 50.00',
            f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_2_Product}': 'Product limit: 50.00',
            f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_3_Product}': 'Product limit: 50.00',
            '005 - Wex OTR Customer Information': customer_information}

        self.capture_request_verifications = {
            'Fuel Purchase': '503', 
            '001 - Wex OTR Flags': 'C - Commercial'}

        self.capture_response_verifications = {
            'Response Code': '0', 
            'Approved Amount': '000000503',
            '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 20.00',
            '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',
            f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_1_Product}': 'Product limit: 50.00',
            f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_2_Product}': 'Product limit: 50.00',
            f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_3_Product}': 'Product limit: 50.00',
            '005 - Wex OTR Customer Information': customer_information}
        
        self.log.debug("Trying to set crind to dispense automatically")
        crindsim.set_mode("auto")
        crindsim.set_sales_target("auth")

        self.log.debug("Set customer information fields on the host simulator with no value")
        networksim.set_commercial_customer_information("", "", "", "")

        self.log.debug("look for the last message before start, so then messages involved in the transaction will be known.")
        last_msg = self.edh.get_last_msg_id(pspid='23')

        self.log.debug("Geting last record on FDC_TransactionData table")
        query = "Select top 1 GPTransactionCookie from FDC_TransactionData order by GPTransactionCookie desc"
        output = runas.run_sqlcmd(query, database="network", cmdshell=False)['output']
        #Turning string into list of strings that have \n delimitation
        output_list = output.split("\n")
        output_list = output_list[2:-3]
        if len(output_list) != 0:
            transaction_cookie = output_list[0].replace(" ", "")
            self.log.debug(f"Transaction cookie is: {transaction_cookie}")
        else:
            self.log.debug("This transaction is the first one that would be stored at FDC_TransactionData table.")
            transaction_cookie = '0'

        self.log.debug("Selecting dispenser and starting a prepay transaction")
        self.pos.select_dispenser(default_dispenser)
        self.pos.add_fuel(generic_trans_amount,fuel_type = tractor_fuel_type, def_type = def_type_no)

        self.log.debug("Paying prepay")
        self.pos.pay_card(brand="Exxon", card_name = card_to_use_NGFC, prompts=commercial_prompts)

        self.log.debug("Wait for fueling ends.")
        self.pos.select_dispenser(default_dispenser)
        self.pos.wait_for_disp_status("fueling", timeout=10, verify=False)
        self.pos.wait_for_fuel(default_dispenser, timeout=60)

        """ 
         Clarification:
         Get the last 8 messages in the DB after payment. There is 
         some stuff that is not exactly a message and it will be removed,
         just 4 messages ares needed: preauth and completion request and response.
         These will be get all together because transaction end inside
         since there is no cash advance and the answer for additional
         products was NO.
        """

        # get the last 4 messages in the DB after payment
        # there is some stuff that is not exactly a message and 
        # we will remove them, we just need 2, preauth and completion
        
        self.log.debug("Try to get 4 messages (preauth and completion)")
        messages = self.edh.get_network_messages(8,start_in=last_msg)
        start_time = time.time()
        while len(messages) < 4 and (time.time() - start_time < 60):
            self.log.debug("There are messages pending to be generated, retrying to get all of them.")
            messages = self.edh.get_network_messages(8,start_in=last_msg)
        if len(messages) < 4:
            tc_fail("The messages obtained from the EDH do not contain all requests and responses messages")
        
        ### PREAUTH MESSAGES ###
        self.log.debug("Validation of message # 3, it should be the preauth request")
        msg_translated = self.edh.translate_message(messages[3])

        if msg_translated: # If different of False, it is understood as True
            self.edh.verify_field(msg_translated, self.preauth_request_verifications)
        else:
            tc_fail('Unable to translate the network message')

        self.log.debug("Validation of message # 2, it should be the preauth response")
        msg_translated = self.edh.translate_message(messages[2])

        if msg_translated: # If different of False, it is understood as True            
            self.edh.verify_field(msg_translated, self.preauth_response_verifications)
        else:
            tc_fail('Unable to translate the network message')
        #########################
        
        ### COMPLETION MESSAGES ###        
        self.log.debug("Validation of message # 1, it should be the completion request")
        msg_translated = self.edh.translate_message(messages[1])

        if msg_translated: # If different of False, it is understood as True
            self.edh.verify_field(msg_translated, self.capture_request_verifications)
        else:
            tc_fail('Unable to translate the network message')

        # Message # 0 should be the preauth response (order desc)
        self.log.debug("Validation of message # 0, it should be the completion response")
        msg_translated = self.edh.translate_message(messages[0])

        if msg_translated: # If different of False, it is understood as True    
            self.edh.verify_field(msg_translated, self.capture_response_verifications)
        else:
            tc_fail('Unable to translate the network message')
        ############################

        self.log.debug("Verifying correct values are stored at FDC_TransactionData table")
        query = "Select top 1 GPTransactionCookie, '/', WexOTRCustomerInfo from FDC_TransactionData order by GPTransactionCookie desc"
        output = runas.run_sqlcmd(query, database="network", cmdshell=False)['output']
        #Turning string into list of strings that have \n delimitation
        output_list = output.split("\n")
        output_list = output_list[2:-3]
        #Separating transaction cookie from customer information
        for value in output_list:
            keyValue = value.split("/")
            keyValue[0] = keyValue[0].replace(" ", "")
            keyValue[1] = keyValue[1].rstrip()
            keyValue[1] = keyValue[1].lstrip()
        
        if keyValue[0] != transaction_cookie:
            if not customer_information == keyValue[1]: #Compare customer information set with a posibly store value at DB
                tc_fail('Customer information was not stored correctly on data base')
        else:
            tc_fail(f'No new records, transaction cookie at beginning: {transaction_cookie}')
        
        self.log.debug("Verifying correct values are printed on the receipt")
        self.pos.check_receipt_for(receipt_data, timeout=10)
        
        self.log.debug("Verifying customer information fields are not printed on the receipt")
        # self.pos.select_dispenser(default_dispenser, verify=False)
        # self.pos.click_forecourt_key("Receipt", timeout=60, verify=False)
            
        self.pos.select_receipt(1, verify=False)

        receipt_list = self.pos.read_receipt()

        inside_receipt_data = {"Customer Information": '',
                                "Name": ':',
                                "City": ':',
                                "State": ':',
                                "Acc.": ':'}

        for key, value in inside_receipt_data.items():
            if value == "":
                line = key + value
                if line in receipt_list:
                    self.log.error(receipt_list)
                    tc_fail(f'The line "{line}" was found on the receipt printed inside and it is not expected.')    
            else:
                line = key + value
                if not line in receipt_list:
                    self.log.error(receipt_list)
                    tc_fail(f'The line "{line}" was not found on the receipt printed inside and it is not expected.')
    '''
    
    @test
    def NGFC_CustomerInformation_SomeEmptyFields(self): #4
        """
        inside tranasctions with NGFC cards, when the customer information fields are empty,
        the data base should not save any data about customer information and the receipt
        should not shown any information about that.
        """

        tractor_fuel_type = 'Tractor fuel' # this is tractor fuel,  because is the objective of this testcase
        def_type_no = 'No' # this is "no",  because is the objective of this testcase
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts
        generic_trans_amount = "$5.00"
        default_dispenser = '1' # we need just one dispenser in this test case
        customerInformation = ["", "DENVER", "", "234W987"]
        customer_information = customerInformation[0] + customerInformation[1] +(' ' * 11) + customerInformation[2] + customerInformation[3]
        commercial_prompts = {              
                    "Additional Products Y/N?": {                    
                        "buttons": ["No"]
                    }
                }
        amounts_to_dispense = {
            "buffer_1":{
                "grade": 1,
                "value": "5"
            }
        }

        #Output verifications

        receipt_data = [f"{self.helpers.grade_1_Name} CA  PUMP# 1",
                        "5.000 GAL @ $1.000/GAL         $5.00  99",
                        "Subtotal =   $5.00",
                        "Tax  =    $0.00",
                        "Total =   $5.00",
                        "Change Due  =    $0.00",
                        "Credit                          $5.00",
                        "Customer Information",
                        "City: " + self.customerInfo[1],
                        "Acc.: " + self.customerInfo[3]]

        self.preauth_request_verifications = {
            'Fuel Purchase': '500', 
            '001 - Wex OTR Flags': 'C - Commercial'}

        self.preauth_response_verifications = {
            'Response Code': '2', 
            'Approved Amount': '000000500',
            '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 0.00',
            '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',
            f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_1_Product}': 'Product limit: 50.00',
            f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_2_Product}': 'Product limit: 50.00',
            f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_3_Product}': 'Product limit: 50.00',
            '005 - Wex OTR Customer Information': customer_information}

        self.capture_request_verifications = {
            'Fuel Purchase': '500', 
            '001 - Wex OTR Flags': 'C - Commercial'}

        self.capture_response_verifications = {
            'Response Code': '0', 
            'Approved Amount': '000000500',
            '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 20.00',
            '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',
            f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_1_Product}': 'Product limit: 50.00',
            f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_2_Product}': 'Product limit: 50.00',
            f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_3_Product}': 'Product limit: 50.00',
            '005 - Wex OTR Customer Information': customer_information}
        
        self.log.debug("Trying to set crind to dispense automatically")
        crindsim.set_mode("manual")

        self.log.debug("Set some customer information fields on the host simulator with no value")
        networksim.set_commercial_customer_information("", self.customerInfo[1], "", self.customerInfo[3])

        self.log.debug("look for the last message before start, so then messages involved in the transaction will be known.")
        last_msg = self.edh.get_last_msg_id(pspid='23')

        self.log.debug("Geting last record on FDC_TransactionData table")
        query = "Select top 1 GPTransactionCookie from FDC_TransactionData order by GPTransactionCookie desc"
        output = runas.run_sqlcmd(query, database="network", cmdshell=False)['output']
        #Turning string into list of strings that have \n delimitation
        output_list = output.split("\n")
        output_list = output_list[2:-3]
        if len(output_list) != 0:
            transaction_cookie = output_list[0].replace(" ", "")
            self.log.debug(f"Transaction cookie is: {transaction_cookie}")
        else:
            self.log.debug("This transaction is the first one that would be stored at FDC_TransactionData table.")
            transaction_cookie = '0'

        self.log.debug("Selecting dispenser and starting a prepay transaction")
        self.pos.select_dispenser(default_dispenser)
        self.pos.add_fuel(generic_trans_amount,fuel_type = tractor_fuel_type, def_type = def_type_no)

        self.log.debug("Paying prepay")
        self.pos.pay_card(brand="Exxon", card_name = card_to_use_NGFC, prompts=commercial_prompts)

        self.log.debug("Wait for fueling ends.")
        self.helpers.fuel_handler(amounts_to_dispense)

        """ 
         Clarification:
         Get the last 8 messages in the DB after payment. There is 
         some stuff that is not exactly a message and it will be removed,
         just 4 messages ares needed: preauth and completion request and response.
         These will be get all together because transaction end inside
         since there is no cash advance and the answer for additional
         products was NO.
        """

        # get the last 4 messages in the DB after payment
        # there is some stuff that is not exactly a message and 
        # we will remove them, we just need 2, preauth and completion
        
        self.log.debug("Try to get 4 messages (preauth and completion)")
        messages = self.edh.get_network_messages(8,start_in=last_msg)
        start_time = time.time()
        while len(messages) < 4 and (time.time() - start_time < 60):
            self.log.debug("There are messages pending to be generated, retrying to get all of them.")
            messages = self.edh.get_network_messages(8,start_in=last_msg)
        if len(messages) < 4:
            tc_fail("The messages obtained from the EDH do not contain all requests and responses messages")
        
        ### PREAUTH MESSAGES ###
        self.log.debug("Validation of message # 3, it should be the preauth request")
        msg_translated = self.edh.translate_message(messages[3])

        if msg_translated: # If different of False, it is understood as True
            self.edh.verify_field(msg_translated, self.preauth_request_verifications)
        else:
            tc_fail('Unable to translate the network message')

        self.log.debug("Validation of message # 2, it should be the preauth response")
        msg_translated = self.edh.translate_message(messages[2])

        if msg_translated: # If different of False, it is understood as True            
            self.edh.verify_field(msg_translated, self.preauth_response_verifications)
        else:
            tc_fail('Unable to translate the network message')
        #########################
        
        ### COMPLETION MESSAGES ###        
        self.log.debug("Validation of message # 1, it should be the completion request")
        msg_translated = self.edh.translate_message(messages[1])

        if msg_translated: # If different of False, it is understood as True
            self.edh.verify_field(msg_translated, self.capture_request_verifications)
        else:
            tc_fail('Unable to translate the network message')

        # Message # 0 should be the preauth response (order desc)
        self.log.debug("Validation of message # 0, it should be the completion response")
        msg_translated = self.edh.translate_message(messages[0])

        if msg_translated: # If different of False, it is understood as True    
            self.edh.verify_field(msg_translated, self.capture_response_verifications)
        else:
            tc_fail('Unable to translate the network message')
        ############################

        self.log.debug("Verifying correct values are stored at FDC_TransactionData table")
        query = "Select top 1 GPTransactionCookie, '/', WexOTRCustomerInfo from FDC_TransactionData order by GPTransactionCookie desc"
        output = runas.run_sqlcmd(query, database="network", cmdshell=False)['output']
        #Turning string into list of strings that have \n delimitation
        output_list = output.split("\n")
        output_list = output_list[2:-3]
        #Separating transaction cookie from customer information
        for value in output_list:
            keyValue = value.split("/")
            keyValue[0] = keyValue[0].replace(" ", "")
            keyValue[1] = keyValue[1].rstrip()
            keyValue[1] = keyValue[1].lstrip()
        
        if keyValue[0] != transaction_cookie:
            if not customer_information == keyValue[1]: #Compare customer information set with a posibly store value at DB
                tc_fail('Customer information was not stored correctly on data base')
        else:
            tc_fail(f'No new records, transaction cookie at beginning: {transaction_cookie}')
        
        self.log.debug("Verifying correct values are printed on the receipt")
        self.pos.check_receipt_for(receipt_data, timeout=10)

        self.log.debug("Verifying customer information fields are not printed on the receipt")
        self.pos.click_function_key("Receipt Search")
        self.pos.select_receipt(1, verify=False)

        receipt_list = self.pos.read_receipt()

        inside_receipt_data = {"Name": customerInformation[0],
                                "City": customerInformation[1],
                                "State": customerInformation[2],
                                "Acc.": customerInformation[3]}

        #result = False
        for key, value in inside_receipt_data.items():
            if value == "":
                line = key + ":" + value
                if line in receipt_list:
                    self.log.debug(receipt_list)
                    tc_fail(f'The line "{line}" was found on the receipt printed inside and it is not expected.')    
            else:
                line = key + ": " + value
                if not line in receipt_list:
                    self.log.debug(receipt_list)
                    tc_fail(f'The line "{line}" was not found on the receipt printed inside and it is not expected.')

        
        self.pos.click_function_key("Back")
    
    @test
    def NonNGFC_CustomerInformation_DB_Receipt_EmptyFields(self): #5
        """
        For the prepay transactions with non NGFC cards, when the customer information
        fields are empty, the data base should not save any data about customer information 
        and the receipt should not shown any information about that
        """

        tractor_fuel_type = 'Tractor fuel' # this is tractor fuel,  because is the objective of this testcase
        def_type_no = 'No' # this is "no",  because is the objective of this testcase
        card_to_use_NonNGFC = 'Debit'        
        generic_trans_amount = "$5.00" # any value that gets an approval from the host
        default_dispenser = '1' # we need just one dispenser in this test case
        amounts_to_dispense = {
            "buffer_1":{
                "grade": 1,
                "value": "5"
            }
        }
        
        #Output verifications

        receipt_data = [f"{self.helpers.grade_1_Name} CA  PUMP# 1",
                        "5.000 GAL @ $1.000/GAL         $5.00  99",
                        "Cash Back                      $2.00",
                        "Subtotal =   $7.00",
                        "Tax  =    $0.00",
                        "Total =   $7.00",
                        "Debit                          $7.00"]

        self.preauth_request_verifications = {
            'Fuel Purchase': '500'}

        self.preauth_response_verifications = {
            'Response Code': '2', 
            'Approved Amount': '000000700'}

        self.preauth_response_negative_verifications = [
            '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)',
            '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)',
            '003 - Wex OTR Fuel Product Limits - Product Code: 001',
            '003 - Wex OTR Fuel Product Limits - Product Code: 002',
            '003 - Wex OTR Fuel Product Limits - Product Code: 003',
            '005 - Wex OTR Customer Information']

        self.capture_request_verifications = {
            'Fuel Purchase': '500'}

        self.capture_response_verifications = {
            'Response Code': '0', 
            'Approved Amount': '000000700'}
        
        self.capture_response_negative_verifications = [
            '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)',
            '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)',
            '003 - Wex OTR Fuel Product Limits - Product Code: 001',
            '003 - Wex OTR Fuel Product Limits - Product Code: 002',
            '003 - Wex OTR Fuel Product Limits - Product Code: 003',
            '005 - Wex OTR Customer Information']
        
        self.log.debug("Trying to set crind to dispense automatically")
        crindsim.set_mode("manual")

        self.log.debug("Set customer information fields on the host simulator with no value")
        networksim.set_commercial_customer_information("", "", "", "")

        self.log.debug("look for the last message before start, so then messages involved in the transaction will be known.")
        last_msg = self.edh.get_last_msg_id(pspid='23')

        self.log.debug("Geting last record on FDC_TransactionData table")
        query = "Select top 1 GPTransactioCookie from FDC_TransactionData order by GPTransactionCookie desc"
        output = runas.run_sqlcmd(query, database="network", cmdshell=False)['output']
        #Turning string into list of strings that have \n delimitation
        output_list = output.split("\n")
        output_list = output_list[2:-3]
        if len(output_list) != 0:
            transaction_cookie = output_list[0].replace(" ", "")
        else:
            self.log.debug("This transaction is the first one that would be stored at FDC_TransactionData table.")
            transaction_cookie = '0'

        self.log.debug("Selecting dispenser and starting a prepay transaction")
        self.pos.select_dispenser(default_dispenser)
        self.pos.add_fuel(generic_trans_amount,fuel_type = tractor_fuel_type, def_type = def_type_no)

        self.log.debug(f"Paying prepay with {card_to_use_NonNGFC}")
        self.pos.pay_card(brand="CORE", card_name = card_to_use_NonNGFC, cashback_amount="2.00")

        self.log.debug("Wait for fueling ends.")
        self.helpers.fuel_handler(amounts_to_dispense)

        """ 
         Clarification:
         Get the last 8 messages in the DB after payment. There is 
         some stuff that is not exactly a message and it will be removed,
         just 4 messages ares needed: preauth and completion request and response.
         These will be get all together because transaction end inside
         since there is no cash advance and the answer for additional
         products was NO.
        """

        # get the last 4 messages in the DB after payment
        # there is some stuff that is not exactly a message and 
        # we will remove them, we just need 2, preauth and completion
        
        self.log.debug("Try to get 4 messages (preauth and completion)")
        messages = self.edh.get_network_messages(8,start_in=last_msg)
        start_time = time.time()
        while len(messages) < 4 and (time.time() - start_time < 60):
            self.log.debug("There are messages pending to be generated, retrying to get all of them.")
            messages = self.edh.get_network_messages(8,start_in=last_msg)
        if len(messages) < 4:
            tc_fail("The messages obtained from the EDH do not contain all requests and responses messages")
        
        ### PREAUTH MESSAGES ###
        self.log.debug("Validation of message # 3, it should be the preauth request")
        msg_translated = self.edh.translate_message(messages[3])

        if msg_translated: # If different of False, it is understood as True
            self.edh.verify_field(msg_translated, self.preauth_request_verifications)
        else:
            tc_fail('Unable to translate the network message')

        self.log.debug("Validation of message # 2, it should be the preauth response")
        msg_translated = self.edh.translate_message(messages[2])

        if msg_translated: # If different of False, it is understood as True            
            self.edh.verify_field(msg_translated, self.preauth_response_verifications)
        else:
            tc_fail('Unable to translate the network message')
        
        self.log.debug("Specific negative verification of fields present on preauth message.")
        for field_to_verify in self.preauth_response_negative_verifications:
                if field_to_verify in msg_translated.keys():
                    tc_fail(f"Please check your validations, the field {field_to_verify} was found and it is not expected.")
    
        #########################
        
        ### COMPLETION MESSAGES ###        
        self.log.debug("Validation of message # 1, it should be the completion request")
        msg_translated = self.edh.translate_message(messages[1])

        if msg_translated: # If different of False, it is understood as True
            self.edh.verify_field(msg_translated, self.capture_request_verifications)
        else:
            tc_fail('Unable to translate the network message')

        # Message # 0 should be the preauth response (order desc)
        self.log.debug("Validation of message # 0, it should be the completion response")
        msg_translated = self.edh.translate_message(messages[0])

        if msg_translated: # If different of False, it is understood as True    
            self.edh.verify_field(msg_translated, self.capture_response_verifications)
        else:
            tc_fail('Unable to translate the network message')

        self.log.debug("Specific negative verification of fields present on completion message.")
        for field_to_verify in self.capture_response_negative_verifications:
                if field_to_verify in msg_translated.keys():
                    tc_fail(f"Please check your validations, the field {field_to_verify} was found and it is not expected.")
        
        ############################

        self.log.debug("Verifying correct values are stored at FDC_TransactionData table")
        query = "Select top 1 GPTransactionCookie, '/', WexOTRCustomerInfo from FDC_TransactionData order by GPTransactionCookie desc"
        output = runas.run_sqlcmd(query, database="network", cmdshell=False)['output']
        #Turning string into list of strings that have \n delimitation
        output_list = output.split("\n")
        output_list = output_list[2:-3]
        #Separating transaction cookie from customer information
        for value in output_list:
            keyValue = value.split("/")
            keyValue[0] = keyValue[0].replace(" ", "")
            keyValue[1] = keyValue[1].rstrip()
            keyValue[1] = keyValue[1].lstrip()
        
        if keyValue[0] != transaction_cookie:    
            if not (keyValue[1] == "" or keyValue[1] == "NULL"): # Compare customer information set with a posibly store value at DB
                tc_fail(f'Customer information was stored with {keyValue[1]}.')
        else:
            tc_fail(f'No new records, transaction cookie at beginning: {transaction_cookie}')
        
        self.log.debug("Verifying correct values are printed on the receipt")
        self.pos.check_receipt_for(receipt_data, timeout=10)
        
        self.log.debug("Verifying customer information fields are not printed on the receipt")
        self.pos.click_function_key("Receipt Search")
        self.pos.select_receipt(1, verify=False)

        receipt_list = self.pos.read_receipt()

        inside_receipt_data = ["Name:",
                                "City:",
                                "State:",
                                "Acc.:"]

        for value in inside_receipt_data:
            if value in receipt_list:
                self.log.debug(receipt_list)
                tc_fail(f'The line "{value}" was found on the receipt printed inside and it is not expected')        

        self.pos.click_function_key("Back")
    
    @test
    def NonNGFC_CustomerInformation_DB_Receipt_FullFields(self): #6
        """
        For the inside transactions with non NGFC cards, when the customer information
        fields are full, the data base should not save any data about customer information 
        and the receipt should not shown any information about that
        """

        tractor_fuel_type = 'Tractor fuel' # this is tractor fuel,  because is the objective of this testcase
        def_type_no = 'No' # this is "no",  because is the objective of this testcase
        card_to_use_NonNGFC = 'Debit'        
        generic_trans_amount = "$5.00" # any value that gets an approval from the host
        default_dispenser = '1' # we need just one dispenser in this test case
        amounts_to_dispense = {
            "buffer_1":{
                "grade": 1,
                "value": "5"
            }
        }

        #Output verifications

        receipt_data = [f"{self.helpers.grade_1_Name} CA   PUMP# 1",
                        "5.000 GAL @ $1.000/GAL         $5.00  99",
                        "Cash Back                      $2.00",
                        "Subtotal =   $7.00",
                        "Tax  =    $0.00",
                        "Total =   $7.00",
                        "Debit                          $7.00"]

        self.preauth_request_verifications = {
            'Fuel Purchase': '500'}

        self.preauth_response_verifications = {
            'Response Code': '2', 
            'Approved Amount': '000000700'}

        self.preauth_response_negative_verifications = [
            '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)',
            '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)',
            '003 - Wex OTR Fuel Product Limits - Product Code: 001',
            '003 - Wex OTR Fuel Product Limits - Product Code: 002',
            '003 - Wex OTR Fuel Product Limits - Product Code: 003',
            '005 - Wex OTR Customer Information']

        self.capture_request_verifications = {
            'Fuel Purchase': '500'}

        self.capture_response_verifications = {
            'Response Code': '0', 
            'Approved Amount': '000000700'}
        
        self.capture_response_negative_verifications = [
            '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)',
            '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)',
            '003 - Wex OTR Fuel Product Limits - Product Code: 001',
            '003 - Wex OTR Fuel Product Limits - Product Code: 002',
            '003 - Wex OTR Fuel Product Limits - Product Code: 003',
            '005 - Wex OTR Customer Information']
        
        self.log.debug("Trying to set crind to dispense automatically")
        crindsim.set_mode("manual")

        self.log.debug("Reset host simulator values to original state")
        networksim.set_commercial_customer_information(self.customerInfo[0], self.customerInfo[1], self.customerInfo[2], self.customerInfo[3])

        self.log.debug("look for the last message before start, so then messages involved in the transaction will be known.")
        last_msg = self.edh.get_last_msg_id(pspid='23')

        self.log.debug("Geting last record on FDC_TransactionData table")
        query = "Select top 1 GPTransactioCookie from FDC_TransactionData order by GPTransactionCookie desc"
        output = runas.run_sqlcmd(query, database="network", cmdshell=False)['output']
        #Turning string into list of strings that have \n delimitation
        output_list = output.split("\n")
        output_list = output_list[2:-3]
        if len(output_list) != 0:
            transaction_cookie = output_list[0].replace(" ", "")
        else:
            self.log.debug("This transaction is the first one that would be stored at FDC_TransactionData table.")
            transaction_cookie = '0'

        self.log.debug("Selecting dispenser and starting a prepay transaction")
        self.pos.select_dispenser(default_dispenser)
        self.pos.add_fuel(generic_trans_amount,fuel_type = tractor_fuel_type, def_type = def_type_no)

        self.log.debug(f"Paying prepay with {card_to_use_NonNGFC}")
        self.pos.pay_card(brand="CORE", card_name = card_to_use_NonNGFC, cashback_amount="2.00")

        self.log.debug("Wait for fueling ends.")
        self.helpers.fuel_handler(amounts_to_dispense)

        """ 
         Clarification:
         Get the last 8 messages in the DB after payment. There is 
         some stuff that is not exactly a message and it will be removed,
         just 4 messages ares needed: preauth and completion request and response.
         These will be get all together because transaction end inside
         since there is no cash advance and the answer for additional
         products was NO.
        """

        # get the last 4 messages in the DB after payment
        # there is some stuff that is not exactly a message and 
        # we will remove them, we just need 2, preauth and completion
        
        self.log.debug("Try to get 4 messages (preauth and completion)")
        messages = self.edh.get_network_messages(8,start_in=last_msg)
        start_time = time.time()
        while len(messages) < 4 and (time.time() - start_time < 60):
            self.log.debug("There are messages pending to be generated, retrying to get all of them.")
            messages = self.edh.get_network_messages(8,start_in=last_msg)
        if len(messages) < 4:
            self.log.debug("Reset host simulator values to previous state, since test case failed")
            networksim.set_commercial_customer_information(self.customerInfo[0], self.customerInfo[1], self.customerInfo[2], self.customerInfo[3])
            tc_fail("The messages obtained from the EDH do not contain all requests and responses messages")
        
        ### PREAUTH MESSAGES ###
        self.log.debug("Validation of message # 3, it should be the preauth request")
        msg_translated = self.edh.translate_message(messages[3])

        if msg_translated: # If different of False, it is understood as True
            self.edh.verify_field(msg_translated, self.preauth_request_verifications)
        else:
            self.log.debug("Reset host simulator values to previous state, since test case failed")
            networksim.set_commercial_customer_information(self.customerInfo[0], self.customerInfo[1], self.customerInfo[2], self.customerInfo[3])
            tc_fail('Unable to translate the network message')

        self.log.debug("Validation of message # 2, it should be the preauth response")
        msg_translated = self.edh.translate_message(messages[2])

        if msg_translated: # If different of False, it is understood as True            
            self.edh.verify_field(msg_translated, self.preauth_response_verifications)
        else:
            self.log.debug("Reset host simulator values to previous state, since test case failed")
            networksim.set_commercial_customer_information(self.customerInfo[0], self.customerInfo[1], self.customerInfo[2], self.customerInfo[3])
            tc_fail('Unable to translate the network message')
        
        self.log.debug("Specific negative verification of fields present on preauth message.")
        for field_to_verify in self.preauth_response_negative_verifications:
                if field_to_verify in msg_translated.keys():
                    self.log.debug("Reset host simulator values to previous state, since test case failed")
                    networksim.set_commercial_customer_information(self.customerInfo[0], self.customerInfo[1], self.customerInfo[2], self.customerInfo[3])
                    tc_fail(f"Please check your validations, the field {field_to_verify} was found and it is not expected.")
    
        #########################
        
        ### COMPLETION MESSAGES ###        
        self.log.debug("Validation of message # 1, it should be the completion request")
        msg_translated = self.edh.translate_message(messages[1])

        if msg_translated: # If different of False, it is understood as True
            self.edh.verify_field(msg_translated, self.capture_request_verifications)
        else:
            self.log.debug("Reset host simulator values to previous state, since test case failed")
            networksim.set_commercial_customer_information(self.customerInfo[0], self.customerInfo[1], self.customerInfo[2], self.customerInfo[3])
            tc_fail('Unable to translate the network message')

        # Message # 0 should be the preauth response (order desc)
        self.log.debug("Validation of message # 0, it should be the completion response")
        msg_translated = self.edh.translate_message(messages[0])

        if msg_translated: # If different of False, it is understood as True    
            self.edh.verify_field(msg_translated, self.capture_response_verifications)
        else:
            self.log.debug("Reset host simulator values to previous state, since test case failed")
            networksim.set_commercial_customer_information(self.customerInfo[0], self.customerInfo[1], self.customerInfo[2], self.customerInfo[3])
            tc_fail('Unable to translate the network message')

        self.log.debug("Specific negative verification of fields present on completion message.")
        for field_to_verify in self.capture_response_negative_verifications:
                if field_to_verify in msg_translated.keys():
                    self.log.debug("Reset host simulator values to previous state, since test case failed")
                    networksim.set_commercial_customer_information(self.customerInfo[0], self.customerInfo[1], self.customerInfo[2], self.customerInfo[3])
                    tc_fail(f"Please check your validations, the field {field_to_verify} was found and it is not expected.")
        
        ############################

        self.log.debug("Verifying correct values are stored at FDC_TransactionData table")
        query = "Select top 1 GPTransactionCookie, '/', WexOTRCustomerInfo from FDC_TransactionData order by GPTransactionCookie desc"
        output = runas.run_sqlcmd(query, database="network", cmdshell=False)['output']
        #Turning string into list of strings that have \n delimitation
        output_list = output.split("\n")
        output_list = output_list[2:-3]
        #Separating transaction cookie from customer information
        for value in output_list:
            keyValue = value.split("/")
            keyValue[0] = keyValue[0].replace(" ", "")
            keyValue[1] = keyValue[1].rstrip()
            keyValue[1] = keyValue[1].lstrip()
        
        if keyValue[0] != transaction_cookie:    
            if not (keyValue[1] == "" or keyValue[1] == "NULL"): # Compare customer information set with a posibly store value at DB
                self.log.debug("Reset host simulator values to previous state, since test case failed")
                networksim.set_commercial_customer_information(self.customerInfo[0], self.customerInfo[1], self.customerInfo[2], self.customerInfo[3])
                tc_fail(f'Customer information was stored with {keyValue[1]}.')
        else:
            self.log.debug("Reset host simulator values to previous state, since test case failed")
            networksim.set_commercial_customer_information(self.customerInfo[0], self.customerInfo[1], self.customerInfo[2], self.customerInfo[3])
            tc_fail(f'No new records, transaction cookie at beginning: {transaction_cookie}')
        
        self.log.debug("Verifying correct values are printed on the receipt")
        self.pos.check_receipt_for(receipt_data, timeout=10)
        
        self.log.debug("Verifying customer information fields are not printed on the receipt")
        self.pos.click_function_key("Receipt Search")
        self.pos.select_receipt(1, verify=False)

        receipt_list = self.pos.read_receipt()

        inside_receipt_data = ["Name: " + self.customerInfo[0],
                                "City: " + self.customerInfo[1],
                                "State: " + self.customerInfo[2],
                                "Acc.: " + self.customerInfo[3]]

        for value in inside_receipt_data:
            if value in receipt_list:
                self.log.debug(receipt_list)
                tc_fail(f'The line "{value}" was found on the receipt printed inside')
        
        self.pos.click_function_key("Back")
    
    @test
    def NGFC_CustomerInformation_DataBase_receipt_R(self): #7
        """
        A regressioned test case to validate that all prompts and customer information are
        displayed correctly in a commercial transaction.
        """
        # Setting the prompt that we need for this test case
        networksim.set_commercial_prompt(True, 'BDAY', 'Birthday information', 'A;TS;M=3;X=6')
        
        #Input constants
        card_to_use = 'NGFC' # using this card to get all commercial prompts        
        generic_trans_amount = "$5.00"# any value that gets an approval from the host
        customer_information = self.customerInfo[0] + (' ' * 14) + self.customerInfo[1] +(' ' * 9) + self.customerInfo[2] + self.customerInfo[3]
        birthday = '120170'
        amounts_to_dispense = {
            "buffer_1":{
                "grade": 1,
                "value": "5"
            }
        }

        prompts = {
            "Additional Products Y/N?": {                    
                "buttons": ["Yes"]
            },
            "Do you want to print a receipt?": {
                "buttons": ["No"]
            },
            "Select fuel products to dispense": {
                "buttons": ["Tractor fuel"]
            },
            "DEF?": {
                "buttons": ["No"]
            },
            "ENTER BIRTHDAY IN MMDDYY FORMAT": {
                "entry": [birthday],
                "buttons": ["Ok"] # This allow us to have answer differently to the same prompt in the same transaction
            },
        }
                
        #Output verifications

        receipt_data = [f"{self.helpers.grade_1_Name} CA  PUMP# 1",
                        "5.000 GAL @ $1.000/GAL         $5.00  99",
                        "Subtotal =   $5.00",
                        "Tax  =    $0.00",
                        "Total =   $5.00",
                        "Credit                          $5.00",
                        "Customer Information",
                        "Name: " + self.customerInfo[0],
                        "City: " + self.customerInfo[1],
                        "State: " + self.customerInfo[2],
                        "Acc.: " + self.customerInfo[3]]

        self.preauth_request_verifications = {
            'Fuel Purchase': '500', 
            '001 - Wex OTR Flags': 'C - Commercial'}

        messages_to_verify= {
            'preauth_request_verifications': {
                'Fuel Purchase': '500', 
                '001 - Wex OTR Flags': 'C - Commercial'
            },
            'preauth_response_verifications': {
                'Response Code': '2', 
                'Approved Amount': '000000500',
                '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 0.00',
                '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_1_Product}': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_2_Product}': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_3_Product}': 'Product limit: 50.00',
                '004 - Wex OTR Prompt Data - Prompt: BDAY': 'Format: A;TS;M=3;X=6',
                '005 - Wex OTR Customer Information': customer_information
            },
            'capture_request_verifications': {
                'Fuel Purchase': '500',
                'Number of Products': '01',
                'Prod 1 product Amount': '500',
                'Prod 1 product Code': f'{self.helpers.grade_1_Product}',
                '001 - Wex OTR Flags': 'C - Commercial',
                '004 - Wex OTR Prompt Data - Prompt: BDAY (Birthday information in MMDDYY format)': 'Response: ' + birthday
            },
            'capture_response_verifications': {
                'Response Code': '0', 
                'Approved Amount': '000000500',
                '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 20.00',
                '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_1_Product }': 'Product limit: 50.00',
                '004 - Wex OTR Prompt Data - Prompt: BDAY': 'Format: A;TS;M=3;X=6',
                '005 - Wex OTR Customer Information': customer_information}
        }

        receipt_data = [f"{self.helpers.grade_1_Name} CA  PUMP# 1",
                        "5.000 GAL @ $1.000/GAL         $5.00  99",
                        "Subtotal =   $5.00",
                        "Tax  =    $0.00",
                        "Total =   $5.00",
                        "Credit                          $5.00",
                        "Customer Information",
                        "Name: " + self.customerInfo[0],
                        "City: " + self.customerInfo[1],
                        "State: " + self.customerInfo[2],
                        "Acc.: " + self.customerInfo[3]]
        #################                       
        self.helpers.prepay_transaction(
            card=card_to_use,
            prepay_amount=generic_trans_amount,
            prompts=prompts,
            amounts_to_dispense=amounts_to_dispense,
            messages_to_verify=messages_to_verify,
            receipt_data=receipt_data
            )
        
        networksim.set_commercial_prompt(False, 'BDAY', 'Birthday information', '')
        networksim.set_commercial_prompt(False, 'BLID', 'Billing ID', '')
    
    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """

        self.pos.close()

    ### Helpers ###

    def set_cash_advance_on_mws(self, cash_advance):
        '''
        '''
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

    
