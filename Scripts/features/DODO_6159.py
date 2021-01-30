"""
    File name: DODO_6159.py
    Tags:
    Description: Test scripts meant to verify correct prossesing of customer information
    and correct printing on receipts.
    Author: Javier Sandoval
    Date created: 2020-04-13 10:00:00
    Date last modified: 2020-04-17 17:00:00
    Python Version: 3.7
"""

import logging
from app import Navi, mws, pos, system, forecourt_installation, networksim, crindsim, runas, network_site_config
from app.framework import EDH
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app.features import feature_activation
from Scripts.features import NGFC_Helpers
import time

class DODO_6159():
    """
    Description: Process customer information and print it in the outside
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

        self.helpers.grade_1_Name_reefer = "RD Dsl 1" #This will be "RD Dsl 1" please update it when changes go mainline
        self.helpers.grade_1_Product_reefer = "032" #This will be "032" please update it when changes go mainline

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
    
        #open Browser
        self.pos.connect()
        self.pos.sign_on()
    
    @test
    def NGFC_CustomerInformation_DataBAse(self): #1
        """
        Outside tranasctions with NGFC cards, when the customer information fields is filled,
        the information must be saved in the data base:
        table -> FDC_TransactionData
        field -> WexOTRSegData
        """

        #Input constants

        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts
        #default_dispenser = '1' # we need just one dispenser in this test case
        customer_information = self.customerInfo[0] + (' ' * 14) + self.customerInfo[1] +(' ' * 9) + self.customerInfo[2] + self.customerInfo[3]
        #trans_amount = "5.01"

        amounts_to_dispense = {
            "buffer_1":{
                "grade": 1,
                "value": "5"
            }
        }
        
        # Dispenser prompts
        dispenser_prompts = {
            "Make selection":{
                "entry": [""],
                "buttons": ["Reefer"]
            },
            "Need DEF?":{
                "entry": [""],
                "buttons": ["No"]
            },
            "Is this a Debit/ATM card?":{
                "entry": [""],
                "buttons": ["No"]
            },
            "Additional Products Y/N?":{
                "entry": [""],
                "buttons": ["No"]
            },
            "Want receipt?":{
                "entry": [""],
                "buttons": ["Yes"]
            },
            "Carwash today?":{
                "entry": [""],
                "buttons": ["No"]
            }
        }

        #Output verifications

        messages_to_verify = {
            'preauth_request_verifications': {
                'Fuel Purchase': '5000', 
                '001 - Wex OTR Flags': 'C - Commercial'
            },
            'preauth_response_verifications': {
                'Response Code': '2', 
                'Approved Amount': '000005000',
                '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 0.00',
                '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_1_Product}': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_2_Product}': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_3_Product}': 'Product limit: 50.00',
                '005 - Wex OTR Customer Information': customer_information
            },
            'capture_request_verifications': {
                'Fuel Purchase': '500', 
                '001 - Wex OTR Flags': 'C - Commercial'
            },
            'capture_response_verifications': {
                'Response Code': '0', 
                'Approved Amount': '000000500',
                '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 20.00',
                '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_1_Product}': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_2_Product}': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_3_Product}': 'Product limit: 50.00',
                '005 - Wex OTR Customer Information': customer_information
            },
        }

        
        """
        crindsim.set_mode("auto")

        crindsim.set_sales_target("money", trans_amount)

        #look for the last message before payment so we know the messages involved in the transaction
        last_msg = self.edh.get_last_msg_id(pspid='23')
        """

        #Get last record on FDC_TransactionData table
        query = "Select top 1 GPTransactionCookie from FDC_TransactionData order by GPTransactionCookie desc"
        output = runas.run_sqlcmd(query, database="network", cmdshell=False)['output']
        #Turning string into list of strings that have \n delimitation
        output_list = output.split("\n")
        output_list = output_list[2:-3]
        if len(output_list) != 0:
            transaction_cookie = output_list[0].replace(" ","")
        else:
            transaction_cookie = "0"

        
        self.helpers.dispenser_transaction(
            card=card_to_use_NGFC,
            prompts=dispenser_prompts, 
            amounts_to_dispense=amounts_to_dispense,
            messages_to_verify=messages_to_verify, 
            inside_receipt="No"    
        )
       
        query = "Select top 1 GPTransactionCookie, '/', WexOTRCustomerInfo from FDC_TransactionData order by GPTransactionCookie desc"
        output = runas.run_sqlcmd(query, database="network", cmdshell=False)['output']
        
        #Turning string into list of strings that have \n delimitation
        output_list = output.split("\n")
        output_list = output_list[2:-3]

        # separating transaction cookie from customer information
        for value in output_list:
            keyValue = value.split("/")
            keyValue[0] = keyValue[0].replace(" ","")
            keyValue[1] = keyValue[1].rstrip()
            keyValue[1] = keyValue[1].lstrip()

        if keyValue[0] != transaction_cookie:    
            if not customer_information == keyValue[1]: # Compare customer information set with a posibly store value at DB       
                tc_fail('Customer information was not stored correctly on data base')
        else:
            tc_fail(f'No new records, transaction cookie at beginning: {transaction_cookie}')
    
    @test
    def NGFC_CustomerInformation_Receipt(self): #2
        """
        Outside tranasctions with NGFC cards, when the customer information fields is filled,
        the information must be printed on receipt:
        """

        #Input constants

        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts
        default_dispenser = '1' # we need just one dispenser in this test case
        customer_information = self.customerInfo[0] + (' ' * 14) + self.customerInfo[1] +(' ' * 9) + self.customerInfo[2] + self.customerInfo[3]

        amounts_to_dispense = {
            "buffer_1":{
                "grade": 1,
                "value": "5"
            }
        }

        # Dispenser prompts
        dispenser_prompts = {
            "Make selection":{
                "entry": [""],
                "buttons": ["Reefer"]
            },
            "Need DEF?":{
                "entry": [""],
                "buttons": ["No"]
            },
            "Is this a Debit/ATM card?":{
                "entry": [""],
                "buttons": ["No"]
            },
            "Additional Products Y/N?":{
                "entry": [""],
                "buttons": ["No"]
            },
            "Want receipt?":{
                "entry": [""],
                "buttons": ["Yes"]
            },
            "Carwash today?":{
                "entry": [""],
                "buttons": ["No"]
            }
        }

        messages_to_verify = {
            'preauth_request_verifications': {
                'Fuel Purchase': '5000', 
                '001 - Wex OTR Flags': 'C - Commercial'
            },
            'preauth_response_verifications': {
                'Response Code': '2', 
                'Approved Amount': '000005000',
                '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 0.00',
                '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_1_Product}': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_2_Product}': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_3_Product}': 'Product limit: 50.00',
                '005 - Wex OTR Customer Information': customer_information
            },
            'capture_request_verifications': {
                'Fuel Purchase': '500', 
                '001 - Wex OTR Flags': 'C - Commercial'
            },
            'capture_response_verifications': {
                'Response Code': '0', 
                'Approved Amount': '000000500',
                '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 20.00',
                '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_1_Product}': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_2_Product}': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_3_Product}': 'Product limit: 50.00',
                '005 - Wex OTR Customer Information': customer_information
            }
        }
        
        #Output verifications

        receipt_data = [f"{self.helpers.grade_1_Name_reefer}5.000G",
                        "PRICE/GAL     $1.000",
                        "FUEL TOTAL   $  5.00",
                        "TOTAL = $  5.00",
                        "CREDIT       $  5.00"
                        ]

        self.helpers.dispenser_transaction(
            card=card_to_use_NGFC,
            prompts=dispenser_prompts, 
            amounts_to_dispense=amounts_to_dispense,
            messages_to_verify=messages_to_verify, 
            receipt_data=receipt_data,
            inside_receipt="No"    
        )
        
        # verify outside receipt
        receipt = crindsim.get_receipt()

        if receipt:

            self.log.info(f"Receipt before turns it into a list -> '{receipt}'")
            receipt_list = receipt.split("\n")
            self.log.info(f"Receipt turned into a list -> '{receipt_list}'")

            outside_receipt_data = ["Name: " + self.customerInfo[0],
                                    "City: " + self.customerInfo[1],
                                    "State: " + self.customerInfo[2],
                                    "Acc.: " + self.customerInfo[3]]

            #result = False
            for value in outside_receipt_data:
                self.log.info(f"Value to look for in the list -> '{value}'")
                
                if not value in receipt_list:
                    tc_fail(f'The line "{value}" was not found on the receipt printed outside')
        else:
            tc_fail(f'No receipt was printed outside')

        # verify that the information on the receipt is correct to be sure that the transaction
        # was approved and the information generated based on that is correct
        self.pos.check_receipt_for(receipt_data, dispenser = default_dispenser, timeout=10)
    
    @test
    def NGFC_CustomerInformation_AllEmptyFields(self): #3 
        """
        For the outside transactions with NGFC Cards, if all the customer information fields
        are empty, the data base should not save any data about customer information and the
        receipt should not show any information about that.
        table -> FDC_TransactionData
        field -> WexOTRSegData
        """

        #Input constants

        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts
        #default_dispenser = '1' # we need just one dispenser in this test case
        customer_information = ''

        amounts_to_dispense = {
            "buffer_1":{
                "grade": 1,
                "value": "5"
            }
        }

        # Dispenser prompts
        dispenser_prompts = {
            "Make selection":{
                "entry": [""],
                "buttons": ["Reefer"]
            },
            "Need DEF?":{
                "entry": [""],
                "buttons": ["No"]
            },
            "Is this a Debit/ATM card?":{
                "entry": [""],
                "buttons": ["No"]
            },
            "Additional Products Y/N?":{
                "entry": [""],
                "buttons": ["No"]
            },
            "Want receipt?":{
                "entry": [""],
                "buttons": ["Yes"]
            },
            "Carwash today?":{
                "entry": [""],
                "buttons": ["No"]
            }
        }

        #Set customer information fields on the host simulator with no value
        networksim.set_commercial_customer_information("", "", "", "")
        
        #Output verifications

        messages_to_verify = {
            'preauth_request_verifications': {
                'Fuel Purchase': '5000', 
                '001 - Wex OTR Flags': 'C - Commercial'
            },
            'preauth_response_verifications': {
                'Response Code': '2', 
                'Approved Amount': '000005000',
                '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 0.00',
                '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_1_Product}': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_2_Product}': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_3_Product}': 'Product limit: 50.00'
            },
            'capture_request_verifications': {
                'Fuel Purchase': '500', 
                '001 - Wex OTR Flags': 'C - Commercial'
            },
            'capture_response_verifications': {
                'Response Code': '0', 
                'Approved Amount': '000000500',
                '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 20.00',
                '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_1_Product}': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_2_Product}': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_3_Product}': 'Product limit: 50.00'
            }
        }

        #Get last record on FDC_TransactionData table
        query = "Select top 1 GPTransactionCookie from FDC_TransactionData order by GPTransactionCookie desc"
        output = runas.run_sqlcmd(query, database="network", cmdshell=False)['output']
        #Turning string into list of strings that have \n delimitation
        output_list = output.split("\n")
        output_list = output_list[2:-3]
        if len(output_list) != 0:
            transaction_cookie = output_list[0].replace(" ","")
        else:
            transaction_cookie = "0"

        self.helpers.dispenser_transaction(
            card=card_to_use_NGFC,
            prompts=dispenser_prompts, 
            amounts_to_dispense=amounts_to_dispense,
            messages_to_verify=messages_to_verify, 
            inside_receipt="No"    
        )

        query = "Select top 1 GPTransactionCookie, '/', WexOTRCustomerInfo from FDC_TransactionData order by GPTransactionCookie desc"
        output = runas.run_sqlcmd(query, database="network", cmdshell=False)['output']
        self.log.info("Query result -> \n" + output)
        #Turning string into list of strings that have \n delimitation
        output_list = output.split("\n")
        output_list = output_list[2:-3]

        # separating transaction cookie from customer information
        self.log.info(output_list)
        for value in output_list:
            keyValue = value.split("/")
            self.log.info(keyValue)
            keyValue[0] = keyValue[0].replace(" ","")
            keyValue[1] = keyValue[1].rstrip()
            keyValue[1] = keyValue[1].lstrip()
        self.log.info("Transaction cookie is " + transaction_cookie)
        if keyValue[0] != transaction_cookie:    
            if not keyValue[1] == "NULL": # Compare customer information set with a posibly store value at DB       
                tc_fail(f'Customer information was not stored with {keyValue[1]}.')
        else:
            tc_fail(f'No new records, transaction cookie at beginning: {transaction_cookie}')
        
        # reset host simulator values to previous state
        networksim.set_commercial_customer_information(self.customerInfo[0], self.customerInfo[1], self.customerInfo[2], self.customerInfo[3])
    
    @test
    def NGFC_CustomerInformation_SomeEmptyFields(self): #4
        """
        Outside tranasctions with NGFC cards, when the customer information fields are empty,
        the data base should not save any data about customer information and the receipt
        should not shown any information about that.
        """

        #Input constants

        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts
        #default_dispenser = '1' # we need just one dispenser in this test case

        # Customer information values
        customerInformation = ["", "DENVER", "", "234W987"]
        customer_information = customerInformation[0] + customerInformation[1] +(' ' * 11) + customerInformation[2] + customerInformation[3]
        
        amounts_to_dispense = {
            "buffer_1":{
                "grade": 1,
                "value": "5"
            }
        }

        # Dispenser prompts
        dispenser_prompts = {
            "Make selection":{
                "entry": [""],
                "buttons": ["Reefer"]
            },
            "Need DEF?":{
                "entry": [""],
                "buttons": ["No"]
            },
            "Is this a Debit/ATM card?":{
                "entry": [""],
                "buttons": ["No"]
            },
            "Additional Products Y/N?":{
                "entry": [""],
                "buttons": ["No"]
            },
            "Want receipt?":{
                "entry": [""],
                "buttons": ["Yes"]
            },
            "Carwash today?":{
                "entry": [""],
                "buttons": ["No"]
            }
        }
        
        #Output verifications

        messages_to_verify = {
            'preauth_request_verifications': {
                'Fuel Purchase': '5000', 
                '001 - Wex OTR Flags': 'C - Commercial'
            },
            'preauth_response_verifications': {
                'Response Code': '2', 
                'Approved Amount': '000005000',
                '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 0.00',
                '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_1_Product}': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_2_Product}': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_3_Product}': 'Product limit: 50.00',
                '005 - Wex OTR Customer Information': customer_information
            },
            'capture_request_verifications': {
                'Fuel Purchase': '500', 
                '001 - Wex OTR Flags': 'C - Commercial'
            },
            'capture_response_verifications': {
                'Response Code': '0', 
                'Approved Amount': '000000500',
                '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 20.00',
                '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_1_Product}': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_2_Product}': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_3_Product}': 'Product limit: 50.00',
                '005 - Wex OTR Customer Information': customer_information
            }
        }
        receipt_data = [f"{self.helpers.grade_1_Name_reefer}5.000G",
                        "PRICE/GAL     $1.000",
                        "FUEL TOTAL   $  5.00",
                        "TOTAL = $  5.00",
                        "CREDIT       $  5.00"
                        ]

        
        networksim.set_commercial_customer_information("", self.customerInfo[1], "", self.customerInfo[3])
        
        self.helpers.dispenser_transaction(
            card=card_to_use_NGFC,
            prompts=dispenser_prompts, 
            amounts_to_dispense=amounts_to_dispense,
            messages_to_verify=messages_to_verify,
            receipt_data=receipt_data,
            inside_receipt="No"    
        )
        
        # verify outside receipt
        receipt = crindsim.get_receipt()

        if receipt:
            self.log.info(f"Receipt before turns it into a list -> '{receipt}'")
            receipt_list = receipt.split("\n")
            self.log.info(f"Receipt turned into a list -> '{receipt_list}'")

            outside_receipt_data = {"Name": customerInformation[0],
                                    "City": customerInformation[1],
                                    "State": customerInformation[2],
                                    "Acc.": customerInformation[3]}

            #result = False
            for key, value in outside_receipt_data.items():
                if value == "":
                    line = key + ": " + value
                    self.log.info(f"The line to look for in the list -> '{line}'")
                    if line in receipt_list:
                        tc_fail(f'The line "{line}" was found on the receipt printed outside and it is not expected.')    
                else:
                    line = key + ": " + value
                    if not line in receipt_list:
                        tc_fail(f'The line "{line}" was not found on the receipt printed outside and it is not expected.')
        else:
            tc_fail(f'No receipt was printed outside')

        networksim.set_commercial_customer_information(self.customerInfo[0], self.customerInfo[1], self.customerInfo[2], self.customerInfo[3])

        # verify that the information on the receipt is correct to be sure that the transaction
        # was approved and the information generated based on that is correct
        #self.pos.check_receipt_for(receipt_data, dispenser= default_dispenser, timeout=10)

    @test
    def NonNGFC_CustomerInformation_DB_Receipt_EmptyFields(self): #5
        """
        For the outside transactions with non NGFC cards, when the customer information
        fields are empty, the data base should not save any data about customer information 
        and the receipt should not shown any information about that
        """

        #Input constants

        card_to_use_NonNGFC = 'MasterCard' # using this card to get all commercial prompts
        default_dispenser = '1' # we need just one dispenser in this test case
        #trans_amount = "5.34"

        amounts_to_dispense = {
            "buffer_1":{
                "grade": 1,
                "value": "5.34"
            }
        }

        # Dispenser prompts
        dispenser_prompts = {
            "Make selection":{
                "entry": [""],
                "buttons": ["Reefer"]
            },
            "Need DEF?":{
                "entry": [""],
                "buttons": ["No"]
            },
            "Enter 5 Digit ZIP Code":{
                "entry": ["27420"],
                "buttons": ["ENTER"]
            },
            "Is this a Debit/ATM card?":{
                "entry": [""],
                "buttons": ["No"]
            },
            "Additional Products Y/N?":{
                "entry": [""],
                "buttons": ["No"]
            },
            "Want receipt?":{
                "entry": [""],
                "buttons": ["Yes"]
            },
            "Carwash today?":{
                "entry": [""],
                "buttons": ["No"]
            },
            "Press ENTER/OK when done CANCEL to Cancel Enter 5 Digit ZIP Code": {
                "entry": ["27420"],
                "buttons": ["ENTER"]
            }
        }
        
        #Output verifications

        self.preauth_request_verifications = {
            'Fuel Purchase': '5000'}

        self.preauth_response_verifications = {
            'Response Code': '2', 
            'Approved Amount': '000005000'}
        
        self.preauth_response_negative_verifications = [
            '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)',
            '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)',
            '003 - Wex OTR Fuel Product Limits - Product Code: 001',
            '003 - Wex OTR Fuel Product Limits - Product Code: 002',
            '003 - Wex OTR Fuel Product Limits - Product Code: 003',
            '005 - Wex OTR Customer Information']

        self.capture_request_verifications = {
            'Fuel Purchase': '534'}

        self.capture_response_verifications = {
            'Response Code': '0', 
            'Approved Amount': '000000534'}

        self.capture_response_negative_verifications = [
            '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)',
            '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)',
            '003 - Wex OTR Fuel Product Limits - Product Code: 001',
            '003 - Wex OTR Fuel Product Limits - Product Code: 002',
            '003 - Wex OTR Fuel Product Limits - Product Code: 003',
            '005 - Wex OTR Customer Information']

        #Get last record on FDC_TransactionData table
        query = "Select top 1 GPTransactionCookie from FDC_TransactionData order by GPTransactionCookie desc"
        output = runas.run_sqlcmd(query, database="network", cmdshell=False)['output']
        #Turning string into list of strings that have \n delimitation
        output_list = output.split("\n")
        output_list = output_list[2:-3]
        if len(output_list) != 0:
            transaction_cookie = output_list[0].replace(" ","")
        else:
            transaction_cookie = "0"
        
        if not crindsim.set_mode("manual"):
            self.log.error(f"Error setting the dispenser in manual mode")
            return False

        #Set customer information fields on the host simulator with no value
        networksim.set_commercial_customer_information("", "", "", "")

        #look for the last message before payment so we know the messages involved in the transaction
        last_msg = self.edh.get_last_msg_id(pspid='23')
        
        #Iniciate outside trnsaction
        crindsim.swipe_card(card_name=card_to_use_NonNGFC, brand="CORE")
        
        #Handle crind prompts
        self.helpers.crind_transaction_handler(prompts=dispenser_prompts, amounts_to_dispense=amounts_to_dispense)
        #self.crind_prompts_handler(dispenser_prompts)

        self.pos.select_dispenser(default_dispenser)

        self.pos.wait_for_fuel(default_dispenser, timeout=60)

        # get the last 8 messages in the DB after payment
        # there is some stuff that is not exactly a message and 
        # we will remove them, we just need 2, preauth and completion
        
        # Get messages the 4 messages (preauth and completion)
        messages = self.edh.get_network_messages(8,start_in=last_msg)        

        start_time = time.time()
        while len(messages) < 4 and (time.time() - start_time < 60):
            self.log.debug("There are messages pending to be generated, retrying to get all of them.")
            messages = self.edh.get_network_messages(8,start_in=last_msg)

        if len(messages) < 4:
        
            tc_fail("The messages obtained from the EDH do not contain request and response messages")

        # Message # 3 should be the preauth request
        
        msg_translated = self.edh.translate_message(messages[3])

        if msg_translated: # If different of False, it is understood as True
            
            self.edh.verify_field(msg_translated, self.preauth_request_verifications)
        
        else:

            tc_fail('Unable to translate the network message')
        
        # Message # 2 should be the preauth response (order desc)
                
        msg_translated = self.edh.translate_message(messages[2])

        if msg_translated: # If different of False, it is understood as True
            
            self.edh.verify_field(msg_translated, self.preauth_response_verifications)
        
        else:

            tc_fail('Unable to translate the network message')

        # Specific negative verification of fields present on preauth message #############################################
        for field_to_verify in self.preauth_response_negative_verifications:
                if field_to_verify in msg_translated.keys():
                    tc_fail(f"Please check your validations, the field {field_to_verify} was found and it is not expected.")
        ###################################################################################################################
        
        # Message # 1 should be the preauth request
        
        msg_translated = self.edh.translate_message(messages[1])

        if msg_translated: # If different of False, it is understood as True
            
            self.edh.verify_field(msg_translated, self.capture_request_verifications)
        
        else:

            tc_fail('Unable to translate the network message')

        # Message # 0 should be the preauth response (order desc)
        
        msg_translated = self.edh.translate_message(messages[0])

        if msg_translated: # If different of False, it is understood as True
            
            self.edh.verify_field(msg_translated, self.capture_response_verifications)
        
        else:
                                                 
            tc_fail('Unable to translate the network message')
        
        # Specific negative verification of fields present on completion message #############################################
        for field_to_verify in self.capture_response_negative_verifications:
                if field_to_verify in msg_translated.keys():
                    tc_fail(f"Please check your validations, the field {field_to_verify} was found and it is not expected.")
        ###################################################################################################################
        
        query = "Select top 1 GPTransactionCookie, '/', WexOTRCustomerInfo from FDC_TransactionData order by GPTransactionCookie desc"
        output = runas.run_sqlcmd(query, database="network", cmdshell=False)['output']
        
        #Turning string into list of strings that have \n delimitation
        output_list = output.split("\n")
        output_list = output_list[2:-3]

        # separating transaction cookie from customer information
        for value in output_list:
            keyValue = value.split("/")
            keyValue[0] = keyValue[0].replace(" ","")
            keyValue[1] = keyValue[1].rstrip()
            keyValue[1] = keyValue[1].lstrip()

        if keyValue[0] != transaction_cookie:    
            if not (keyValue[1] == "" or keyValue[1] == "NULL"): # Compare customer information set with a posibly store value at DB       
                tc_fail(f'Customer information was stored with {keyValue[1]}.')
        else:
            tc_fail(f'No new records, transaction cookie at beginning: {transaction_cookie}')
        
        # verify outside receipt
        receipt = crindsim.get_receipt()

        if receipt:
            receipt_list = receipt.split("\n")

            outside_receipt_data = ["Name:",
                                    "City:",
                                    "State:",
                                    "Acc.:"]

            for value in outside_receipt_data:
                if value in receipt_list:
                    tc_fail(f'The line "{value}" was found on the receipt printed outside and it is not expected')
        else:
            tc_fail(f'No receipt was printed outside')
    
    @test
    def NonNGFC_CustomerInformation_DB_Receipt_FullFields(self): #6
        """
        For the outside transactions with non NGFC cards, when the customer information
        fields are full, the data base should not save any data about customer information 
        and the receipt should not shown any information about that
        """

        #Input constants

        card_to_use_NonNGFC = 'MasterCard' # using this card to get all commercial prompts
        default_dispenser = '1' # we need just one dispenser in this test case
        #trans_amount = "5.35"

        amounts_to_dispense = {
            "buffer_1":{
                "grade": 1,
                "value": "5.35"
            }
        }

        # Dispenser prompts
        dispenser_prompts = {
            "Make selection":{
                "entry": [""],
                "buttons": ["Reefer"]
            },
            "Need DEF?":{
                "entry": [""],
                "buttons": ["No"]
            },
            "Is this a Debit/ATM card?":{
                "entry": [""],
                "buttons": ["No"]
            },
            "Enter 5 Digit ZIP Code":{
                "entry": ["27420"],
                "buttons": ["ENTER"]
            },
            "Additional Products Y/N?":{
                "entry": [""],
                "buttons": ["No"]
            },
            "Want receipt?":{
                "entry": [""],
                "buttons": ["Yes"]
            },
            "Carwash today?":{
                "entry": [""],
                "buttons": ["No"]
            },
            "Press ENTER/OK when done CANCEL to Cancel Enter 5 Digit ZIP Code": {
                "entry": ["27420"],
                "buttons": ["ENTER"]
            }
        }
        
        #Output verifications

        self.preauth_request_verifications = {
            'Fuel Purchase': '5000'}

        self.preauth_response_verifications = {
            'Response Code': '2', 
            'Approved Amount': '000005000'}
        
        self.preauth_response_negative_verifications = [
            '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)',
            '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)',
            '003 - Wex OTR Fuel Product Limits - Product Code: 001',
            '003 - Wex OTR Fuel Product Limits - Product Code: 002',
            '003 - Wex OTR Fuel Product Limits - Product Code: 003',
            '005 - Wex OTR Customer Information']

        self.capture_request_verifications = {
            'Fuel Purchase': '535'}

        self.capture_response_verifications = {
            'Response Code': '0', 
            'Approved Amount': '000000535'}

        self.capture_response_negative_verifications = [
            '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)',
            '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)',
            '003 - Wex OTR Fuel Product Limits - Product Code: 001',
            '003 - Wex OTR Fuel Product Limits - Product Code: 002',
            '003 - Wex OTR Fuel Product Limits - Product Code: 003',
            '005 - Wex OTR Customer Information']
        
        if not crindsim.set_mode("manual"):
            self.log.error(f"Error setting the dispenser in manual mode")
            return False

        self.log.debug(") reset host simulator values to previous state")
        networksim.set_commercial_customer_information(self.customerInfo[0], self.customerInfo[1], self.customerInfo[2], self.customerInfo[3])

        #look for the last message before payment so we know the messages involved in the transaction
        last_msg = self.edh.get_last_msg_id(pspid='23')

        #Get last record on FDC_TransactionData table
        query = "Select top 1 GPTransactionCookie from FDC_TransactionData order by GPTransactionCookie desc"
        output = runas.run_sqlcmd(query, database="network", cmdshell=False)['output']
        #Turning string into list of strings that have \n delimitation
        output_list = output.split("\n")
        output_list = output_list[2:-3]
        if len(output_list) != 0:
            transaction_cookie = output_list[0].replace(" ","")
        else:
            transaction_cookie = "0"

        #Iniciate outside trnsaction
        crindsim.swipe_card(card_name=card_to_use_NonNGFC, brand="CORE")
        
        #Handle crind prompts
        self.helpers.crind_transaction_handler(prompts=dispenser_prompts, amounts_to_dispense=amounts_to_dispense)
        #self.crind_prompts_handler(dispenser_prompts)

        self.pos.select_dispenser(default_dispenser)

        self.pos.wait_for_fuel(default_dispenser, timeout=60)

        # get the last 4 messages in the DB after payment
        # there is some stuff that is not exactly a message and 
        # we will remove them, we just need 2, preauth and completion
        
        # Get messages the 4 messages (preauth and completion)
        messages = self.edh.get_network_messages(8,start_in=last_msg)        

        start_time = time.time()
        while len(messages) < 4 and (time.time() - start_time < 60):
            self.log.debug("There are messages pending to be generated, retrying to get all of them.")
            messages = self.edh.get_network_messages(8,start_in=last_msg)

        if len(messages) < 4:
            
            tc_fail("The messages obtained from the EDH do not contain request and response messages")

        # Message # 3 should be the preauth request
        
        msg_translated = self.edh.translate_message(messages[3])

        if msg_translated: # If different of False, it is understood as True
            
            self.edh.verify_field(msg_translated, self.preauth_request_verifications)
        
        else:

            tc_fail('Unable to translate the network message')
        
        # Message # 2 should be the preauth response (order desc)
                
        msg_translated = self.edh.translate_message(messages[2])

        if msg_translated: # If different of False, it is understood as True
            
            self.edh.verify_field(msg_translated, self.preauth_response_verifications)
        
        else:

            tc_fail('Unable to translate the network message')

        # Specific negative verification of fields present on preauth message #############################################
        for field_to_verify in self.preauth_response_negative_verifications:
                if field_to_verify in msg_translated.keys():
                    tc_fail(f"Validating preauth response, the field {field_to_verify} was found and it is not expected.")
        ###################################################################################################################
        
        # Message # 1 should be the preauth request
        
        msg_translated = self.edh.translate_message(messages[1])

        if msg_translated: # If different of False, it is understood as True
            
            self.edh.verify_field(msg_translated, self.capture_request_verifications)
        
        else:

            tc_fail('Unable to translate the network message')

        # Message # 0 should be the preauth response (order desc)
        
        msg_translated = self.edh.translate_message(messages[0])

        if msg_translated: # If different of False, it is understood as True
            
            self.edh.verify_field(msg_translated, self.capture_response_verifications)
        
        else:
                                                 
            tc_fail('Unable to translate the network message')
        
        # Specific negative verification of fields present on completion message #############################################
        for field_to_verify in self.capture_response_negative_verifications:
                if field_to_verify in msg_translated.keys():
                    tc_fail(f"Validating completion response, the field {field_to_verify} was found and it is not expected.")
        ###################################################################################################################
        
        query = "Select top 1 GPTransactionCookie, '/', WexOTRCustomerInfo from FDC_TransactionData order by GPTransactionCookie desc"
        output = runas.run_sqlcmd(query, database="network", cmdshell=False)['output']
        
        #Turning string into list of strings that have \n delimitation
        output_list = output.split("\n")
        output_list = output_list[2:-3]

        # separating transaction cookie from customer information
        for value in output_list:
            keyValue = value.split("/")
            keyValue[0] = keyValue[0].replace(" ","")
            keyValue[1] = keyValue[1].rstrip()
            keyValue[1] = keyValue[1].lstrip()

        if keyValue[0] != transaction_cookie:    
            if not (keyValue[1] == "" or keyValue[1] == "NULL"): # Compare customer information set with a posibly store value at DB       
                tc_fail(f'Customer information was stored with {keyValue[1]}.')
        else:
            tc_fail(f'No new records, transaction cookie at beginning: {transaction_cookie}')
        
        # reset host simulator values to previous state
        networksim.set_commercial_customer_information(self.customerInfo[0], self.customerInfo[1], self.customerInfo[2], self.customerInfo[3])

        # verify outside receipt
        receipt = crindsim.get_receipt()

        if receipt:
            receipt_list = receipt.split("\n")

            outside_receipt_data = ["Name: " + self.customerInfo[0],
                                    "City: " + self.customerInfo[1],
                                    "State: " + self.customerInfo[2],
                                    "Acc.: " + self.customerInfo[3]]

            for value in outside_receipt_data:
                if value in receipt_list:
                    tc_fail(f'The line "{value}" was found on the receipt printed outside')
        else:
            tc_fail(f'No receipt was printed outside')
    
    @test
    def NGFC_CustomerInformation_DataBase_receipt_R(self): #7
        """
        A regressioned test case to validate that all prompts and customer information are
        displayed correctly in a commercial transaction.
        """
        
        #Input constants

        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts
        default_dispenser = '1' # we need just one dispenser in this test case
        customer_information = self.customerInfo[0] + (' ' * 14) + self.customerInfo[1] +(' ' * 9) + self.customerInfo[2] + self.customerInfo[3]
        trans_amount = "5.01"
        cash_advance_limit = "1000" # value without comma (,)
        prompt_for_cash_advance = "Do you want cash advance up to $" + cash_advance_limit[0:2] + "?"
        cash_advance = "500" # value without comma (,)
        prompt_birthday = "210280"

        amounts_to_dispense = {
            "buffer_1":{
                "grade": 1,
                "value": trans_amount
            }
        }

        # Dispenser prompts
        dispenser_prompts = {
            "Make selection":{
                "entry": [""],
                "buttons": ["Reefer"]
            },
            "Need DEF?":{
                "entry": [""],
                "buttons": ["No"]
            },
            "Is this a Debit/ATM card?":{
                "entry": [""],
                "buttons": ["No"]
            },
            "Additional Products Y/N?":{
                "entry": [""],
                "buttons": ["No"]
            },            
            "Press ENTER/OK when done CANCEL to Cancel Enter Birthday information in MMDDYY format":{
                "entry": [prompt_birthday],
                "buttons": ["Enter"]
            },
            prompt_for_cash_advance:{
                "entry": [""],
                "buttons": ["Yes"]
            },
            "Press ENTER/OK when done CANCEL to Cancel Enter Cash Advance Amount":{
                "entry": [cash_advance],
                "buttons": ["Enter"]
            },
            "Want receipt?":{
                "entry": [""],
                "buttons": ["Yes"]
            },
            "Carwash today?":{
                "entry": [""],
                "buttons": ["No"]
            }
        }
        
        #Output verifications

        receipt_data = [f"{self.helpers.grade_1_Name_reefer} CA   PUMP# 1",
                        "5.010 GAL @ $1.000/GAL         $5.01  99",
                        "Cash Advance                   $5.00", #This line will change in the future, will be Cash advance
                        "Subtotal =   $10.01",
                        "Tax  =    $0.00",
                        "Total =   $10.01",
                        "Credit                          $10.01",
                        "Customer Information",
                        "Name: " + self.customerInfo[0],
                        "City: " + self.customerInfo[1],
                        "State: " + self.customerInfo[2],
                        "Acc.: " + self.customerInfo[3]]

        self.preauth_request_verifications = {
            'Fuel Purchase': '5000', 
            '001 - Wex OTR Flags': 'C - Commercial'}

        self.preauth_response_verifications = {
            'Response Code': '2', 
            'Approved Amount': '000005000',
            '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 10.00',
            '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',
            f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_1_Product}': 'Product limit: 50.00',
            f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_2_Product}': 'Product limit: 50.00',
            f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_3_Product}': 'Product limit: 50.00',
            '004 - Wex OTR Prompt Data - Prompt: BDAY': 'Format: N;TS;M3;X6',
            '005 - Wex OTR Customer Information': customer_information}

        self.capture_request_verifications = {
            'Fuel Purchase': '501',
            'Cash Amount': cash_advance,
            'Number of Products': '02',
            'Prod 1 product Amount': '501',
            'Prod 1 product Code': f'{self.helpers.grade_1_Product_reefer}',
            'Prod 2 product Amount': '500',
            'Prod 2 product Code': '955',
            '001 - Wex OTR Flags': 'C - Commercial',
            '004 - Wex OTR Prompt Data - Prompt: BDAY (Birthday information in MMDDYY format)': 'Response: ' + prompt_birthday}

        self.capture_response_verifications = {
            'Response Code': '0', 
            'Approved Amount': '000010010',
            '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 20.00',
            '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',
            f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_1_Product}': 'Product limit: 50.00',
            f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_2_Product}': 'Product limit: 50.00',
            f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_3_Product}': 'Product limit: 50.00',
            '004 - Wex OTR Prompt Data - Prompt: BDAY': 'Format: N;TS;M3;X6',
            '005 - Wex OTR Customer Information': customer_information}

        

        self.pos.minimize_pos()
        # set cash advance limite on site

        self.set_cash_advance_on_mws(cash_advance_limit)        

        # wait for new crind configuration is loaded
        self.pos.wait_disp_ready(idle_timeout=120)

        #crindsim.set_sales_target("money", trans_amount)
        self.log.info("Set the CRIND in manual mode")
        crindsim.set_mode("manual")

        # set dynamic prompt on host simulator
        networksim.set_commercial_prompt(True, 'BDAY', 'Birthday information', 'N;TS;M3;X6')

        #look for the last message before payment so we know the messages involved in the transaction
        last_msg = self.edh.get_last_msg_id(pspid='23')

        #Iniciate outside trnsaction
        crindsim.swipe_card(card_name=card_to_use_NGFC, brand="EXXON")
        
        #Handle crind prompts
        self.helpers.crind_transaction_handler(prompts=dispenser_prompts, amounts_to_dispense=amounts_to_dispense)

        # get the last 4 messages in the DB after payment
        # there is some stuff that is not exactly a message and 
        # we will remove them, we just need 2, preauth and completion
        
        # Get messages the 2 messages (preauth)
        messages = self.edh.get_network_messages(4,start_in=last_msg)        

        start_time = time.time()
        while len(messages) < 2 and (time.time() - start_time < 60):
            self.log.debug("There are messages pending to be generated, retrying to get all of them.")
            messages = self.edh.get_network_messages(4,start_in=last_msg)

        if len(messages) < 2:
            
            tc_fail("The messages obtained from the EDH do not contain request and response messages")

        # Message # 1 should be the preauth request
        
        msg_translated = self.edh.translate_message(messages[1])

        if msg_translated: # If different of False, it is understood as True
            
            self.edh.verify_field(msg_translated, self.preauth_request_verifications)
        
        else:

            tc_fail('Unable to translate the network message')

        # Message # 0 should be the preauth response (order desc)
                
        msg_translated = self.edh.translate_message(messages[0])

        if msg_translated: # If different of False, it is understood as True
            
            self.edh.verify_field(msg_translated, self.preauth_response_verifications)
        
        else:

            tc_fail('Unable to translate the network message')
        
        self.pos.maximize_pos()

        self.pos.select_dispenser(default_dispenser)

        self.pos.wait_for_fuel(default_dispenser, timeout=60)

        # Getting the last message before starting the completion
        last_msg = self.edh.get_last_msg_id(pspid='23')

        # Select the buffer to complete the transaction, this happens because we said when we paid
        # that we will add addition products self.pos.pay_card(card_name='NGFC', additional_prod = 'Yes')
        self.pos.click_fuel_buffer('commercial')

        #Commercial transaction set with additional product need to hit pay to complete the transaction
        self.pos.click_function_key('Pay')
        
        #it will prompt asking to print receipt and the answer will be NO
        self.pos.click_message_box_key('Yes', timeout=15)

        # Waiting for completion messages are generated
        last_msg = self.helpers.wait_for_new_msg(last_msg, "23")

        # get the last 4 messages in the DB after payment
        # there is some stuff that is not exactly a message and 
        # we will remove them, we just need 2, preauth and completion
        
        # Get messages the 2 messages (completion)
        messages = self.edh.get_network_messages(4,start_in=last_msg)        

        start_time = time.time()
        while len(messages) < 2 and (time.time() - start_time < 60):
            self.log.debug("There are messages pending to be generated, retrying to get all of them.")
            messages = self.edh.get_network_messages(4,start_in=last_msg)

        if len(messages) < 2:
            
            tc_fail("The messages obtained from the EDH do not contain request and response messages")
        
        # Message # 1 should be the preauth request
        
        msg_translated = self.edh.translate_message(messages[1])

        if msg_translated: # If different of False, it is understood as True
            
            self.edh.verify_field(msg_translated, self.capture_request_verifications)
        
        else:

            tc_fail('Unable to translate the network message')

        # Message # 0 should be the preauth response (order desc)
        
        msg_translated = self.edh.translate_message(messages[0])

        if msg_translated: # If different of False, it is understood as True
            
            self.edh.verify_field(msg_translated, self.capture_response_verifications)
        
        else:
                                                 
            tc_fail('Unable to translate the network message')

        # verify that the information on the receipt is correct to be sure that the transaction
        # was approved and the information generated based on that is correct
        self.pos.check_receipt_for(receipt_data, dispenser= default_dispenser, timeout=10)

        # restoring initial value for cash advance.
        networksim.set_commercial_product_limit("True","CADV","Company funds cash advance",0.00)

        # disabling commercial prompt configured at test case beginning
        networksim.set_commercial_prompt(False, 'BDAY', 'Birthday information', '')

        # back cash advance to 0
        self.set_cash_advance_on_mws('000')
    
    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        
        self.pos.click_function_key("Back")
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
    
