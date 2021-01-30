"""
    File name: DODO_6124_6020_6271.py
    Tags: multidispensing, prepay
    Description: Test scripts meant to verify correct prosessing multidispensing in
    prepay transaction.
    Author: Javier Sandoval
    Date created: 2020-05-08 16:00:00
    Date last modified: 2020-05-15 15:40:00
    Python Version: 3.7
"""

import logging
from app import Navi, mws, pos, networksim
from app.framework import EDH
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app.features import feature_activation
from Scripts.features import NGFC_Helpers

import time

class DODO_6124_6020_6271():
    """
    Description: regression test cases about prepay wiht multidispensing fuel.
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

        # Customer information values
        self.customerInfo = ["AB TRUCKING", "DENVER", "CO", "234W987"]

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
        #self.helpers.set_cash_advance_on_mws('000')

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
        networksim.set_commercial_fuel_limit_send_mode("fuel product configuration based",110,True)

        #open Browser
        self.pos.connect()
        self.pos.sign_on()
        self.pos.maximize_pos()
    
    @test
    def Prepay_NGFC_Prompts(self): #16
        """
        In an internal commercial transaction dispense two fuel products
        without cash advance and without additional products.
        """
        #Input constants

        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts
        amount_to_pay = '30' #amounts over 10 will make work better the set_sales_target method for crind simulator
        number_of_products = '02'
        generic_trans_amount = "$" + amount_to_pay + ".00" # any value that gets an approval from the host
        customer_information = self.customerInfo[0] + (' ' * 14) + self.customerInfo[1] +(' ' * 9) + self.customerInfo[2] + self.customerInfo[3]
        
        amounts_to_dispense = {
            "buffer_1":{
                "grade": 1,
                "value": "3"
            },
            "buffer_2":{
                "grade": 3,
                "value": "4"
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
                "buttons": ["Yes"]
            }
        }
                
        #Output verifications

        messages_to_verify = {
            'preauth_request_verifications': {
                'Fuel Purchase': '3000',
                'Number of Products': '05', #amount of fuel products configured at site.
                'Prod 1 product Code': f'{self.helpers.grade_1_Product}', #first fuel product configured
                'Prod 2 product Code': f'{self.helpers.grade_2_Product}', #second fuel product configured
                'Prod 3 product Code': f'{self.helpers.grade_1_Product_reefer}', #first fuel product configured
                'Prod 4 product Code': f'{self.helpers.grade_2_Product_reefer}', #second fuel product configured
                'Prod 5 product Code': f'{self.helpers.grade_3_Product}', #third fuel product configured
                '001 - Wex OTR Flags': 'C - Commercial',
                '008 - Wex OTR Cash Advance Limit': '$0.00' #amount of cash advance configured at site
            },
            'preauth_response_verifications': {
                'Response Code': '2', 
                'Approved Amount': '000003000',
                '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 0.00',
                '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',
                '005 - Wex OTR Customer Information': customer_information
            },
            'capture_request_verifications' : {
                'Fuel Purchase': '700',
                'Number of Products': number_of_products,
                'Prod 1 product Amount': '300',
                'Prod 1 product Code': f'{self.helpers.grade_1_Product}',
                'Prod 2 product Amount': '400',
                'Prod 2 product Code': f'{self.helpers.grade_3_Product}',
                '001 - Wex OTR Flags': 'C - Commercial'
            },
            'capture_response_verifications': {
                'Response Code': '0', 
                'Approved Amount': '000000700',
                '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 20.00',
                '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',
                '005 - Wex OTR Customer Information': customer_information
            }
        }

        total_amount = float(amount_to_pay)
        refund_amount = str("{0:.2f}".format(total_amount - 7.00))
        receipt_data = [f"{self.helpers.grade_1_Name} CA   PUMP# 1",
                        "3.000 GAL @ $1.000/GAL         $3.00  99",
                        f"{self.helpers.grade_3_Name} CA   PUMP# 1",
                        "4.000 GAL @ $1.000/GAL         $4.00  99",
                        "Subtotal =   $7.00",
                        "Tax  =    $0.00",
                        "Total =   $7.00",
                        "Credit                          $30.00",
                        "Customer Information",
                        "Name: " + self.customerInfo[0],
                        "City: " + self.customerInfo[1],
                        "State: " + self.customerInfo[2],
                        "Acc.: " + self.customerInfo[3],
                        "Refund Credit $-" + refund_amount]

        self.helpers.prepay_transaction(
            card=card_to_use_NGFC,
            prepay_amount=generic_trans_amount,
            prompts=prompts,
            amounts_to_dispense=amounts_to_dispense,
            messages_to_verify=messages_to_verify,
            receipt_data=receipt_data,
            underrun=True
            )
        
    
    #TODO: Enable the following test case when DODO-6299 gets fixed    
    @test
    def Prepay_Product(self): #2
        """
        In an internal transaction, the buffer will be shown as one,
        but three different fuels can be dispensed and at the same time
        buy a product from store
        """
        #Input constants

        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts
        amount_to_pay = '30' #amounts over 10 will make work better the set_sales_target method for crind simulator
        generic_trans_amount = "$" + amount_to_pay + ".00" # any value that gets an approval from the host
        customer_information = self.customerInfo[0] + (' ' * 14) + self.customerInfo[1] +(' ' * 9) + self.customerInfo[2] + self.customerInfo[3]
        items = ["Generic Item"]
        
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

        prompts = {
            "Additional Products Y/N?": {                    
                "buttons": ["Yes"]
            },
            "Do you want to print a receipt?": {
                "buttons": ["No"]
            },
            "Select fuel products to dispense": {
                "buttons": ["Both fuels"]
            },
            "DEF?": {
                "buttons": ["Yes"]
            }
        }

        messages_to_verify = {
            'preauth_request_verifications': {
                'Fuel Purchase': '3000',
                'Number of Products': '05', #amount of fuel products configured at site.
                'Prod 1 product Code': f'{self.helpers.grade_1_Product}', #first fuel product configured
                'Prod 2 product Code': f'{self.helpers.grade_2_Product}', #second fuel product configured
                'Prod 3 product Code': f'{self.helpers.grade_1_Product_reefer}', #first fuel product configured for reefer
                'Prod 4 product Code': f'{self.helpers.grade_2_Product_reefer}', #second fuel product configured for reefer
                'Prod 5 product Code': f'{self.helpers.grade_3_Product}', #third fuel product configured
                '001 - Wex OTR Flags': 'C - Commercial',
                '008 - Wex OTR Cash Advance Limit': '$0.00'#amount of cash advance configured at site
            },
            'preauth_response_verifications': {
                'Response Code': '2', 
                'Approved Amount': '000003000',
                '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 0.00',
                '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',
                '005 - Wex OTR Customer Information': customer_information
            },            
            'capture_request_verifications': {
                'Fuel Purchase': '1200',
                'NonFuel Amount': '001',
                'Number of Products': '04',
                'Prod 1 product Amount': '300',
                'Prod 1 product Code': f'{self.helpers.grade_1_Product}',
                'Prod 2 product Amount': '500',
                'Prod 2 product Code': f'{self.helpers.grade_1_Product_reefer}',
                'Prod 3 product Amount': '400',
                'Prod 3 product Code': f'{self.helpers.grade_3_Product}',
                'Prod 4 product Amount': '001',
                'Prod 4 product Code': '400',
                '001 - Wex OTR Flags': 'C - Commercial'
            },
            'capture_response_verifications': {
                'Response Code': '0', 
                'Approved Amount': '000001201',
                '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 20.00',
                '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',
                '005 - Wex OTR Customer Information': customer_information
            }
        }

        #Output verifications
        total_amount = float(amount_to_pay)
        refund_amount = str("{0:.2f}".format(total_amount - 12.01))
        receipt_data = [f"{self.helpers.grade_1_Name} CA   PUMP# 1",
                        "3.000 GAL @ $1.000/GAL         $3.00  99",
                        f"{self.helpers.grade_3_Name} CA PUMP# 1",
                        "4.000 GAL @ $1.000/GAL         $4.00  99",
                        f"{self.helpers.grade_1_Name_reefer} CA PUMP# 1",
                        "5.000 GAL @ $1.000/GAL         $5.00  99",
                        "Generic Item                   $0.01  99",
                        "Subtotal =   $12.01",
                        "Tax  =    $0.00",
                        "Total =   $12.01",
                        "Credit                          $30.00",
                        "Customer Information",
                        "Name: " + self.customerInfo[0],
                        "City: " + self.customerInfo[1],
                        "State: " + self.customerInfo[2],
                        "Acc.: " + self.customerInfo[3],
                        "Refund Credit $-" + refund_amount
                    ]

        self.helpers.prepay_transaction(
            card=card_to_use_NGFC,
            prepay_amount=generic_trans_amount,
            prompts=prompts,
            amounts_to_dispense=amounts_to_dispense,
            messages_to_verify=messages_to_verify,
            receipt_data=receipt_data,
            items=items,
            underrun=True
            )

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """

        self.pos.close()