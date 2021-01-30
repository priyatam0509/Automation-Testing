"""
    File name: Commercial_Prepay.py
    Tags:
    Description: Test scripts meant to run end to end testing for commercial prepays
    Author: 
    Date created: 2019-11-29 07:21:07
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import Navi, mws, pos, system, forecourt_installation, networksim, crindsim
from app.framework import EDH
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app.features import feature_activation
from Scripts.features import NGFC_Helpers
import time

class Commercial_Prepay():
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

        #Commercial Diesel checkbox activation in forecourt installation 
        #self.set_commercial_on_forecourt()

        # HostSim Response mode
        networksim.set_response_mode("Approval")
                
        # Disable all promtps

        networksim.disable_commercial_fuel_limits()
        networksim.disable_product_limits()
        networksim.disable_prompts() 

        # Set specif config for this script

        networksim.set_commercial_customer_information("ABC TRUCKING", "DENVER", "CO", "234W987")
        networksim.set_commercial_product_limit("True","CADV","Company funds cash advance",20.00)
        networksim.set_commercial_product_limit("True", "MERC", "Default category for merchandise", 30.00)        
        networksim.set_commercial_fuel_limit("True", self.helpers.grade_1_Product , 50.00)
        networksim.set_commercial_fuel_limit("True", self.helpers.grade_2_Product , 50.00)
        networksim.set_commercial_fuel_limit("True", self.helpers.grade_3_Product , 50.00)
        networksim.set_commercial_fuel_limit_send_mode("fuel product configuration based",110,True)

        # Set Dispenser Config

        crindsim.set_mode("manual")
        
        #open Browser
        self.pos.connect()

        self.pos.sign_on()
    
    #TODO: Enable this test case when TN-812 gets merged
    @test
    def Commercial_Prepay_Fuel_type_tractor_DEF(self):
        """
        Prepay sale with a commercial card in which will be verified the fuel type selection at beginig and additional products prompt which will be accepted         in order to make transaction ends inside, after fuelling, but no item will be added.
        """   
        #Input constants

        generic_trans_amount = "$5.00" # any value that gets an approval from the host
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts
        amounts_to_dispense = {
            "buffer_1":{
                "grade": 1,
                "value": "2"
            },
            "buffer_2":{
                "grade": 3,
                "value": "3"
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

        receipt_data = [f"{self.helpers.grade_1_Name} CA   PUMP# 1",
                        "2.000 GAL @ $1.000/GAL         $2.00  99",
                        f"{self.helpers.grade_3_Name} CA   PUMP# 1",
                        "3.000 GAL @ $1.000/GAL         $3.00  99",
                        "Subtotal =   $5.00",
                        "Tax  =    $0.00",
                        "Total =   $5.00",
                        "Change Due  =    $0.00",
                        "Credit                          $5.00"]
        
        messages_to_verify = {
            'preauth_request_verifications' : {
                'Fuel Purchase': '500', 
                '001 - Wex OTR Flags': 'C - Commercial'},
            'preauth_response_verifications': {
                'Response Code': '2', 
                'Approved Amount': '000000500',
                '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 0.00',
                '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_1_Product }': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_2_Product }': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_3_Product }': 'Product limit: 50.00',
                '005 - Wex OTR Customer Information': 'ABC TRUCKING             DENVER         CO234W987'},
            'capture_request_verifications': {
                'Fuel Purchase': '500', 
                '001 - Wex OTR Flags': 'C - Commercial'},
            'capture_response_verifications': {
                'Response Code': '0', 
                'Approved Amount': '000000500',
                '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 20.00',
                '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_1_Product }': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_2_Product }': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_3_Product }': 'Product limit: 50.00',
                '005 - Wex OTR Customer Information': 'ABC TRUCKING             DENVER         CO234W987'}
        }

        self.helpers.prepay_transaction(
            card=card_to_use_NGFC,
            prepay_amount=generic_trans_amount,
            prompts=prompts,
            amounts_to_dispense=amounts_to_dispense,
            messages_to_verify=messages_to_verify,
            receipt_data=receipt_data
            )
        
    @test
    def Fuel_type_tractor_NotDEF(self):
        """
        End to end commercial fuel prepay will be performed in order to 
        verify the fuel type selection at beginig, tractor fuel should be selected but 
        DEF should be rejected, and transaction ends without errors.
        """
        
        #Input constants

        generic_trans_amount = "$5.00" # any value that gets an approval from the host        
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts
        
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
            }
        }

        #Output verifications

        messages_to_verify = {
            'preauth_request_verifications': {
                'Fuel Purchase': '500', 
                '001 - Wex OTR Flags': 'C - Commercial'
            },
            'preauth_response_verifications': {
                'Response Code': '2', 
                'Approved Amount': '000000500',
                '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 0.00',
                '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',                            
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_1_Product }': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_2_Product }': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_3_Product }': 'Product limit: 50.00',
                '005 - Wex OTR Customer Information': 'ABC TRUCKING             DENVER         CO234W987'
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
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_1_Product }': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_2_Product }': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_3_Product }': 'Product limit: 50.00',
                '005 - Wex OTR Customer Information': 'ABC TRUCKING             DENVER         CO234W987'
            }
        }

        receipt_data = [f"{self.helpers.grade_1_Name} CA   PUMP# 1",
                        "5.000 GAL @ $1.000/GAL         $5.00  99",
                        "Subtotal =   $5.00",
                        "Tax  =    $0.00",
                        "Total =   $5.00",
                        "Change Due  =    $0.00",
                        "Credit                          $5.00"]

        self.helpers.prepay_transaction(
            card=card_to_use_NGFC,
            prepay_amount=generic_trans_amount,
            prompts=prompts,
            messages_to_verify=messages_to_verify,
            receipt_data=receipt_data
            )
                
    #TODO: Enable this test case when TN-812 gets merged
    @test
    def Fuel_type_reefer_DEF(self):
        """
        End to end commercial fuel prepay will be performed in order to 
        verify the fuel type selection at beginig, reefer fuel and 
        DEF should be selected and transaction ends without errors.
        """

        #Input constants

        generic_trans_amount = "$5.00" # any value that gets an approval from the host
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts
        
        amounts_to_dispense = {
            "buffer_1":{
                "grade": 3,
                "value": "3"
            },
            "buffer_2":{
                "grade": 1,
                "value": "2"
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
                "buttons": ["Reefer fuel"]
            },
            "DEF?": {
                "buttons": ["Yes"]
            }
        }

        messages_to_verify = {
            'preauth_request_verifications': {
                'Fuel Purchase': '500', 
                '001 - Wex OTR Flags': 'C - Commercial'
            },
            'preauth_response_verifications': {
                'Response Code': '2', 
                'Approved Amount': '000000500',
                '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 0.00',
                '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',                            
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_1_Product }': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_2_Product }': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_3_Product }': 'Product limit: 50.00',
                '005 - Wex OTR Customer Information': 'ABC TRUCKING             DENVER         CO234W987'
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
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_1_Product }': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_2_Product }': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_3_Product }': 'Product limit: 50.00',
                '005 - Wex OTR Customer Information': 'ABC TRUCKING             DENVER         CO234W987'}
        }

        #Output verificacions

        receipt_data = [f"{self.helpers.grade_1_Name_reefer} CA   PUMP# 1",
                        "2.000 GAL @ $1.000/GAL         $2.00  99",
                        f"{self.helpers.grade_3_Name} CA   PUMP# 1",
                        "3.000 GAL @ $1.000/GAL         $3.00  99",
                        "Subtotal =   $5.00",
                        "Tax  =    $0.00",
                        "Total =   $5.00",
                        "Change Due  =    $0.00",
                        "Credit                          $5.00"]

        self.helpers.prepay_transaction(
            card=card_to_use_NGFC,
            prepay_amount=generic_trans_amount,
            prompts=prompts,
            amounts_to_dispense=amounts_to_dispense,
            messages_to_verify=messages_to_verify,
            receipt_data=receipt_data
            )
        
    @test
    def Fuel_type_reefer_NotDEF(self):
        """
        End to end commercial fuel prepay will be performed in order to 
        verify the fuel type selection at beginig, reefer fuel should be selected but 
        DEF should be rejected, and transaction ends without errors.
        """
        
        #Input constants

        generic_trans_amount = "$5.00" # any value that gets an approval from the host
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts
        
        prompts = {
            "Additional Products Y/N?": {                    
                "buttons": ["Yes"]
            },
            "Do you want to print a receipt?": {
                "buttons": ["No"]
            },
            "Select fuel products to dispense": {
                "buttons": ["Reefer fuel"]
            },
            "DEF?": {
                "buttons": ["No"]
            }
        }

        messages_to_verify = {
            'preauth_request_verifications': {
                'Fuel Purchase': '500', 
                '001 - Wex OTR Flags': 'C - Commercial'
            },
            'preauth_response_verifications': {
                'Response Code': '2', 
                'Approved Amount': '000000500',
                '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 0.00',
                '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_1_Product }': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_2_Product }': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_3_Product }': 'Product limit: 50.00',
                '005 - Wex OTR Customer Information': 'ABC TRUCKING             DENVER         CO234W987'
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
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_1_Product }': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_2_Product }': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_3_Product }': 'Product limit: 50.00',
                '005 - Wex OTR Customer Information': 'ABC TRUCKING             DENVER         CO234W987'
            }
        }

        #Output verifications

        receipt_data = [f"{self.helpers.grade_1_Name_reefer} CA   PUMP# 1",
                        "5.000 GAL @ $1.000/GAL         $5.00  99",
                        "Subtotal =   $5.00",
                        "Tax  =    $0.00",
                        "Total =   $5.00",
                        "Change Due  =    $0.00",
                        "Credit                          $5.00"]

        self.helpers.prepay_transaction(
            card=card_to_use_NGFC,
            prepay_amount=generic_trans_amount,
            prompts=prompts,
            messages_to_verify=messages_to_verify,
            receipt_data=receipt_data
            )

    #TODO: Enable this test case when TN-812 gets merged
    @test
    def Fuel_type_both_DEF(self):
        """
        End to end commercial fuel prepay will be performed in order to 
        verify the fuel type selection at beginig, both fuels and 
        DEF should be selected and transaction ends without errors.
        """
        
        #Input constants

        generic_trans_amount = "$5.00" # any value that gets an approval from the host
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts
        
        amounts_to_dispense = {
            "buffer_1":{
                "grade": 1,
                "value": "2"
            },
            "buffer_2":{
                "grade": 2,
                "value": "1"
            },
            "buffer_3":{
                "grade": 1,
                "value": "2"
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
        #Output verifications

        messages_to_verify = {
            'preauth_request_verifications': {
                'Fuel Purchase': '500', 
                '001 - Wex OTR Flags': 'C - Commercial'
            },
            'preauth_response_verifications': {
                'Response Code': '2', 
                'Approved Amount': '000000500',
                '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 0.00',
                '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_1_Product }': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_2_Product }': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_3_Product }': 'Product limit: 50.00',
                '005 - Wex OTR Customer Information': 'ABC TRUCKING             DENVER         CO234W987'
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
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_1_Product }': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_2_Product }': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_3_Product }': 'Product limit: 50.00',
                '005 - Wex OTR Customer Information': 'ABC TRUCKING             DENVER         CO234W987'
            }
        }

        receipt_data = [f"{self.helpers.grade_1_Name} CA   PUMP# 1",
                        "2.000 GAL @ $1.000/GAL         $2.00  99",
                        f"{self.helpers.grade_2_Name} CA   PUMP# 1",
                        "1.000 GAL @ $1.000/GAL         $1.00  99",
                        f"{self.helpers.grade_1_Name_reefer} CA   PUMP# 1",
                        "2.000 GAL @ $1.000/GAL         $2.00  99",
                        "Subtotal =   $5.00",
                        "Tax  =    $0.00",
                        "Total =   $5.00",
                        "Change Due  =    $0.00",
                        "Credit                          $5.00"]
        
        self.helpers.prepay_transaction(
            card=card_to_use_NGFC,
            prepay_amount=generic_trans_amount,
            prompts=prompts,
            amounts_to_dispense=amounts_to_dispense,
            messages_to_verify=messages_to_verify,
            receipt_data=receipt_data
            )
        
    @test
    def Fuel_type_both_NotDEF(self):
        """
        End to end commercial fuel prepay will be performed in order to 
        verify the fuel type selection at beginig, both fuels should be selected but 
        DEF should be rejected, and transaction ends without errors.
        """
        
        #Input constants

        generic_trans_amount = "$5.00" # any value that gets an approval from the host        
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts
                
        amounts_to_dispense = {
            "buffer_1":{
                "grade": 1,
                "value": "2"
            },
            "buffer_2":{
                "grade": 1,
                "value": "3"
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
                "buttons": ["No"]
            }
        }

        #Output verifications

        messages_to_verify = {
            'preauth_request_verifications': {
                'Fuel Purchase': '500', 
                '001 - Wex OTR Flags': 'C - Commercial'
            },
            'preauth_response_verifications': {
                'Response Code': '2', 
                'Approved Amount': '000000500',
                '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 0.00',
                '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_1_Product }': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_2_Product }': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_3_Product }': 'Product limit: 50.00',
                '005 - Wex OTR Customer Information': 'ABC TRUCKING             DENVER         CO234W987'
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
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_1_Product }': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_2_Product }': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_3_Product }': 'Product limit: 50.00',
                '005 - Wex OTR Customer Information': 'ABC TRUCKING             DENVER         CO234W987'
            }
        }
        
        receipt_data = [f"{self.helpers.grade_1_Name} CA   PUMP# 1",
                        "2.000 GAL @ $1.000/GAL           $2.00  99",
                        f"{self.helpers.grade_1_Name_reefer} CA   PUMP# 1",
                        "3.000 GAL @ $1.000/GAL           $3.00  99",            
                        "Subtotal =   $5.00",
                        "Tax  =    $0.00",
                        "Total =   $5.00",
                        "Change Due  =    $0.00",
                        "Credit                          $5.00"]
        
        self.helpers.prepay_transaction(
            card=card_to_use_NGFC,
            prepay_amount=generic_trans_amount,
            prompts=prompts,
            amounts_to_dispense=amounts_to_dispense,
            messages_to_verify=messages_to_verify,
            receipt_data=receipt_data
            )
      
    #TODO: Enable this test case when TN-812 gets merged
    @test
    def NGFC_card_Notadd_prod(self):
        """
        Prepay sale with a commercial card that allows to enter additional products after prepay
        but doesn't select any item after prepay, in this case transaction should ends as a common fuel prepay transaction.
        """
        
        #Input constants

        generic_trans_amount = "$5.00" # any value that gets an approval from the host        
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts        
        amounts_to_dispense = {
            "buffer_1":{
                "grade": 1,
                "value": "2"
            },
            "buffer_2":{
                "grade": 3,
                "value": "3"
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
                "buttons": ["Yes"]
            }
        }

        #Output verifications

        messages_to_verify = {
            'preauth_request_verifications': {
                'Fuel Purchase': '500', 
                '001 - Wex OTR Flags': 'C - Commercial'
            },
            'preauth_response_verifications': {
                'Response Code': '2', 
                'Approved Amount': '000000500',
                '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 0.00',
                '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_1_Product }': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_2_Product }': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_3_Product }': 'Product limit: 50.00',
                '005 - Wex OTR Customer Information': 'ABC TRUCKING             DENVER         CO234W987'
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
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_1_Product }': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_2_Product }': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_3_Product }': 'Product limit: 50.00',
                '005 - Wex OTR Customer Information': 'ABC TRUCKING             DENVER         CO234W987'
            }
        }

        receipt_data = [f"{self.helpers.grade_1_Name} CA   PUMP# 1",
                        "2.000 GAL @ $1.000/GAL         $2.00  99",
                        f"{self.helpers.grade_3_Name} CA   PUMP# 1",
                        "3.000 GAL @ $1.000/GAL         $3.00  99",
                        "Subtotal =   $5.00",
                        "Tax  =    $0.00",
                        "Total =   $5.00",
                        "Change Due  =    $0.00",
                        "Credit                          $5.00"]
        
        self.helpers.prepay_transaction(
            card=card_to_use_NGFC,
            prepay_amount=generic_trans_amount,
            prompts=prompts,
            amounts_to_dispense=amounts_to_dispense,
            messages_to_verify=messages_to_verify,
            receipt_data=receipt_data
            )
       
    
    #TODO: Enebable this test case when DODO-6574 gets fixed
    #TODO: Enable this test case when TN-812 gets merged    
    '''
    @test
    def NGFC_add_prod_after_prepay(self):
        """
        Prepay sale with a commercial card that allows to enter additional products after 
        prepay and a generic item is purchased.

        Preconditions(these preconditions should be automated): 
        1- Have Passport Exxon site installed.
        2- Have Commercial diesel activated.
        3- Have a dispenser configured as Commercial one.
        4- NGFC Card
        5- Have an Item configured/setup for purchase on 
        """
        
        #setting the host sim with fuel limit $10 for regular

        networksim.set_commercial_fuel_limit(True, '019', 10.00)
        
        #Setting constant value

        generic_trans_amount = "$10.01" # any value that gets an approval from the host
        card_to_use = 'NGFC' # using this card to get all commercial prompts

        amounts_to_dispense = {
            "buffer_1":{
                "grade": 1,
                "value": "7"
            },
            "buffer_2":{
                "grade": 3,
                "value": "3"
            }
        }

        items = ['Generic Item']     
        
        prompts = {
            "Additional Products Y/N?": {                    
                "buttons": ["Yes"]
            },            
            f"Total Fuel limit: $110\nGrade {self.helpers.grade_1_Name} limit: 10\nGrade {self.helpers.grade_2_Name} limit: 50\nGrade {self.helpers.grade_3_Name} limit: 50":{
                "buttons": ["Ok"]
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

        messages_to_verify = {
            'preauth_request_verifications': {
                'Fuel Purchase': '1001', 
                '001 - Wex OTR Flags': 'C - Commercial'
            },
            'preauth_response_verifications': {
                'Response Code': '2', 
                'Approved Amount': '000001001',
                '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 0.00',
                '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',
                '003 - Wex OTR Fuel Product Limits - Product Code: 000': 'Product limit: 110.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_1_Product }': 'Product limit: 10.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_2_Product }': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_3_Product }': 'Product limit: 50.00',
                '005 - Wex OTR Customer Information': 'ABC TRUCKING             DENVER         CO234W987'
            },
            'capture_request_verifications': {
                'Fuel Purchase': '1000', 
                '001 - Wex OTR Flags': 'C - Commercial'
            },
            'capture_response_verifications': {
                'Response Code': '0', 
                'Approved Amount': '000001001',
                '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 20.00',
                '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',
                '003 - Wex OTR Fuel Product Limits - Product Code: 000': 'Product limit: 110.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_1_Product }': 'Product limit: 10.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_2_Product }': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_3_Product }': 'Product limit: 50.00',
                '005 - Wex OTR Customer Information': 'ABC TRUCKING             DENVER         CO234W987'
            }
        }

        receipt_data = [f"{self.helpers.grade_1_Name} CA   PUMP# 1",
                        "7.000 GAL @ $1.000/GAL         $7.00  99",
                        f"{self.helpers.grade_3_Name} CA   PUMP# 1",
                        "3.000 GAL @ $1.000/GAL         $3.00  99",
                        "Generic Item                     $0.01  99",
                        "Subtotal =   $10.01",
                        "Tax  =    $0.00",
                        "Total =   $10.01",
                        "Change Due  =    $0.00",
                        "Credit                          $10.01"]

        self.helpers.prepay_transaction(
            card=card_to_use,
            prepay_amount=generic_trans_amount,
            prompts=prompts,
            amounts_to_dispense=amounts_to_dispense,
            messages_to_verify=messages_to_verify,
            receipt_data=receipt_data,
            items=items
            )
        
        #Reset host sim with default settings
        
        networksim.set_commercial_fuel_limit(False, '019', 50)    
    '''
    #TODO: Enable this test case when DODO-6511 gets fixed
    @test
    def NGFC_Prepay_Dynamic_Prompt_Printed(self):
        """
        Description: Validate that dynamic prompts for prepay
        transaction with NGFC Cards are the printed on receipt 

        Preconditions(These preconditions should be automated): 
        1- Have Passport Exxon site installed.
        2- Have Commercial diesel activated.
        3- Have a dispenser configured as Commercial one.
        4- NGFC Card
        5- Have a Dynamic prompt setup on HostSim

        """

        # Setting the prompt that we need for this test case
        networksim.set_commercial_prompt(True, 'BDAY', 'Birthday information', 'A;TS;M=3;X=6')
        networksim.set_commercial_prompt(True, 'BLID', 'Billing ID', 'N;TN;M0;X521')
        
        #Setting constant value

        generic_trans_amount = "$5.00" # any value that gets an approval from the host
        card_to_use = 'NGFC'

        amounts_to_dispense = {
            "buffer_1":{
                "grade": 1,
                "value": "2"
            },
            "buffer_2":{
                "grade": 3,
                "value": "3"
            }
        }

        prompts = {
            "Additional Products Y/N?": {                    
                "buttons": ["Yes"]
            },            
            f"Total Fuel limit: $110\nGrade {self.helpers.grade_1_Name} limit: 10\nGrade {self.helpers.grade_2_Name} limit: 50\nGrade {self.helpers.grade_3_Name} limit: 50":{
                "buttons": ["Ok"]
            },
            "Do you want to print a receipt?": {
                "buttons": ["No"]
            },
            "Select fuel products to dispense": {
                "buttons": ["Tractor fuel"]
            },
            "DEF?": {
                "buttons": ["Yes"]
            },
            "ENTER BIRTHDAY IN MMDDYY FORMAT": {
                "entry": ["120170"],
                "buttons": ["Ok"] # This allow us to have answer differently to the same prompt in the same transaction
            }, 
            "ENTER BILLING ID": {
                "entry" : ["123456798", "12"],
                "buttons": ["Enter", "Enter"]                
            },
            "Invalid Reply": {                    
                "buttons": ["Ok"]
            }
        }

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
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_1_Product }': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_2_Product }': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_3_Product }': 'Product limit: 50.00',
                '005 - Wex OTR Customer Information': 'ABC TRUCKING             DENVER         CO234W987'
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
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_1_Product }': 'Product limit: 50.00',
                '005 - Wex OTR Customer Information': 'ABC TRUCKING             DENVER         CO234W987'}
        }

        receipt_data = [f"{self.helpers.grade_1_Name} CA   PUMP# 1",
                        "2.000 GAL @ $1.000/GAL         $2.00  99",
                        f"{self.helpers.grade_3_Name} CA   PUMP# 1",
                        "3.000 GAL @ $1.000/GAL         $3.00  99",
                        "Subtotal =   $5.00",
                        "Tax  =    $0.00",
                        "Total =   $5.00",
                        "Change Due  =    $0.00",
                        "Credit                          $5.00",
                        "Billing ID: 12"]
        
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
    
    '''
    #TODO: Enable this test case when crindsim handel properly fuel limits   
    @test
    def NGFC_Prepay_Product_Limit(self):
        """
        Description: To verify that product limit work as expected 
        even with fuel limits

        Preconditions(These preconditions should be automated): 
        1- Have Passport Exxon site installed.
        2- Have Commercial diesel activated.
        3- Have a dispenser configurated as commercial.
        4- Card to use should be a MSR NGFC.
        5- Have cash advance configured. #This will be activated once Vitual Pinpad is configured
        6- Have MERC limit with $5.
        7- Have 1 prompt configured on host simulator as follow: N;TN;M1;X122.
        8- Fuel limits from host simulator: trx limit=30; fuel limit=10; grades limit=5.

        """

        #Setting constant value

        networksim.set_commercial_fuel_limit_send_mode("Fuel Product Configuration Based", 30, True)
        networksim.set_commercial_fuel_limit(True, "019", 3.00)
        networksim.set_commercial_fuel_limit(True, "020", 2.00)
        networksim.set_commercial_fuel_limit(True, "021", 5.00)

        generic_trans_amount = "$10.00" # any value that gets an approval from the host
        fuel_type = 'Tractor fuel' # any of the 3 buttons are correct, they are used for nothing for now
        def_type = 'Yes' # Yes or No is correct, they are used for nothing for now
        default_dispenser = '1' # we need just one dispenser in this test case
        card_to_use = 'NGFC' # Card used to get all commercial features
        amounts_to_dispense = {
            "buffer_1":{
                "grade": 1,
                "value": ""
            },
            "buffer_2":{
                "grade": 3,
                "value": ""
            }
        }

        items = ['Generic Item']
        
        """
        commercial_prompts = {              
            "Additional Products Y/N?": {                    
                "buttons": ["Yes"]                
            },
            "Total Fuel limit: $30\nGrade Regular limit: 5\nGrade Plus limit: 5\nGrade Supreme limit: 5":{
                "buttons": ["Ok"]
            }
        }
        """

        prompts = {
            "Additional Products Y/N?": {                    
                "buttons": ["Yes"]
            },                        
            "Total Fuel limit: $30\nGrade Regular limit: 5\nGrade Plus limit: 5\nGrade Supreme limit: 5":{
                "buttons": ["Ok"]
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

        messages_to_verify= {
            'preauth_request_verifications': {
                'Fuel Purchase': '1000', 
                '001 - Wex OTR Flags': 'C - Commercial',
            },
            'preauth_response_verifications': {
                'Response Code': '2', 
                'Approved Amount': '000001000',
                '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 0.00',
                '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',                            
                '003 - Wex OTR Fuel Product Limits - Product Code: 019': 'Product limit: 3.00',
                '003 - Wex OTR Fuel Product Limits - Product Code: 020': 'Product limit: 2.00',
                '003 - Wex OTR Fuel Product Limits - Product Code: 021': 'Product limit: 5.00',
                '005 - Wex OTR Customer Information': 'ABC TRUCKING             DENVER         CO234W987'
            },
            'capture_request_verifications': {
                'Fuel Purchase': '500',
                '001 - Wex OTR Flags': 'C - Commercial'
            },            
            'capture_response_verifications': {
                'Response Code': '0', 
                'Approved Amount': '000000501',
                '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 20.00',
                '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',
                '003 - Wex OTR Fuel Product Limits - Product Code: 000': 'Product limit: 30.00',
                '003 - Wex OTR Fuel Product Limits - Product Code: 019': 'Product limit: 3.00',
                '003 - Wex OTR Fuel Product Limits - Product Code: 020': 'Product limit: 2.00',
                '003 - Wex OTR Fuel Product Limits - Product Code: 021': 'Product limit: 5.00',
                '005 - Wex OTR Customer Information': 'ABC TRUCKING             DENVER         CO234W987'
            }
        }

        receipt_data = [f"{self.helpers.grade_1_Name} CA   PUMP# 1",
                        "3.000 GAL @ $1.000/GAL         $3.00  99",
                        f"{self.helpers.grade_3_Name} CA   PUMP# 1",
                        "2.000 GAL @ $1.000/GAL         $2.00  99",
                        "Generic Item                     $0.01  99",
                        "Subtotal =    $5.01",
                        "Tax  =    $0.00",
                        "Total =    $5.01",
                        "Change Due  =    $0.00",
                        "Credit                    $10.00",
                        "Refund Credit                   $-4.99"
                        ]

        self.helpers.prepay_transaction(
            card=card_to_use,
            prepay_amount=generic_trans_amount,
            prompts=prompts,
            amounts_to_dispense=amounts_to_dispense,
            messages_to_verify=messages_to_verify,
            receipt_data=receipt_data,
            items=items
            )
        """
        #Messages verification
        self.preauth_request_verifications = {'Fuel Purchase': '1000', 
                            '001 - Wex OTR Flags': 'C - Commercial',
                            }

        self.preauth_response_verifications = {'Response Code': '2', 
                            'Approved Amount': '000001000',
                            '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 0.00',
                            '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',                            
                            '003 - Wex OTR Fuel Product Limits - Product Code: 019': 'Product limit: 3.00',
                            '003 - Wex OTR Fuel Product Limits - Product Code: 020': 'Product limit: 2.00',
                            '003 - Wex OTR Fuel Product Limits - Product Code: 021': 'Product limit: 5.00',
                            '005 - Wex OTR Customer Information': 'ABC TRUCKING             DENVER         CO234W987'}

        self.capture_request_verifications = {'Fuel Purchase': '500', 
                    '001 - Wex OTR Flags': 'C - Commercial'}

        self.capture_response_verifications = {'Response Code': '0', 
                            'Approved Amount': '000000501',
                            '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 20.00',
                            '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',
                            '003 - Wex OTR Fuel Product Limits - Product Code: 000': 'Product limit: 30.00',
                            '003 - Wex OTR Fuel Product Limits - Product Code: 019': 'Product limit: 3.00',
                            '003 - Wex OTR Fuel Product Limits - Product Code: 020': 'Product limit: 2.00',
                            '003 - Wex OTR Fuel Product Limits - Product Code: 021': 'Product limit: 5.00',
                            '005 - Wex OTR Customer Information': 'ABC TRUCKING             DENVER         CO234W987'}

        

        crindsim.set_mode("manual")

        self.pos.add_fuel(generic_trans_amount,fuel_type = fuel_type, def_type = def_type)

        #look for the last message before payment so we know the messages involved in the transaction

        last_msg = self.edh.get_last_msg_id(pspid='23')

        # Pay the transaction 

        self.pos.pay_card(card_name = card_to_use, brand="Exxon", prompts= commercial_prompts) 

        self.pos.select_dispenser(default_dispenser)
        
        # get the last 4 messages in the DB after payment
        # there is some stuff that is not exactly a message and 
        # we will remove them, we just need 2, preauth and completion

        messages = self.edh.get_network_messages(4,start_in=last_msg)

        start_time = time.time()
        while len(messages) < 2 and (time.time() - start_time < 60):
            self.log.debug("There are messages pending to be generated, retrying to get all of them.")
            messages = self.edh.get_network_messages(4,start_in=last_msg)
        if len(messages) < 2:
            tc_fail("The messages obtained from the EDH do not contain all requests and responses messages")               
        
        # Message # 1 should be the preauth request
        
        msg_transalted = self.edh.translate_message(messages[1])

        if msg_transalted: # If different of False, it is understood as True
            
            self.edh.verify_field(msg_transalted, self.preauth_request_verifications)
        
        else:

            tc_fail('Unable to translate the network message')

        # Message # 0 should be the preauth response (order desc)
        
        msg_transalted = self.edh.translate_message(messages[0])

        if msg_transalted: # If different of False, it is understood as True
            
            self.edh.verify_field(msg_transalted, self.preauth_response_verifications)
        
        else:

            tc_fail('Unable to translate the network message')        

        self.helpers.fuel_handler(amounts_to_dispense)

        self.pos.wait_for_fuel(default_dispenser, timeout=120)

        last_msg = self.edh.get_last_msg_id(pspid='23')

        self.pos.click_fuel_buffer('commercial', timeout=10)

        self.pos.add_item(timeout=10)

        self.pos.click_function_key('Pay')

        # It will prompt asking to print receipt and the answer will be NO
        if not self.pos.click_message_box_key('No', timeout=10):
            tc_fail("The terminal din't prompt for receipt and it should be doing that") 

        # Waiting for completion messages are generated
        last_msg = self.helpers.wait_for_new_msg(last_msg, "23") 

        # get the last 4 messages in the DB after payment
        # there is some stuff that is not exactly a message and 
        # we will remove them, we just need 2, preauth and completion

        messages = self.edh.get_network_messages(4,start_in=last_msg)

        start_time = time.time()
        while len(messages) < 2 and (time.time() - start_time < 60):
            self.log.debug("There are messages pending to be generated, retrying to get all of them.")
            messages = self.edh.get_network_messages(4,start_in=last_msg)
        if len(messages) < 2:
            tc_fail("The messages obtained from the EDH do not contain all requests and responses messages")              
        
        # Message # 1 should be the preauth request
        
        msg_transalted = self.edh.translate_message(messages[1])

        if msg_transalted: # If different of False, it is understood as True
            
            self.edh.verify_field(msg_transalted, self.capture_request_verifications)
        
        else:

            tc_fail('Unable to translate the network message')

        # Message # 0 should be the preauth response (order desc)
        
        msg_transalted = self.edh.translate_message(messages[0])

        if msg_transalted: # If different of False, it is understood as True
            
            self.edh.verify_field(msg_transalted, self.capture_response_verifications)
        
        else:

            tc_fail('Unable to translate the network message')
        
        networksim.set_commercial_fuel_limit_send_mode("Fuel Product Configuration Based", 30, False)
        networksim.set_commercial_fuel_limit(False, "001", 5.00)
        networksim.set_commercial_fuel_limit(False, "002", 5.00)
        networksim.set_commercial_fuel_limit(False, "003", 5.00)     

        # verify that the information on the receipt is correct to be sure that the transaction
        # was approved and the information generated based on that is correct
         
        self.pos.check_receipt_for(receipt_data, dispenser= default_dispenser, timeout=10)
        """
        '''
    
    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """

        self.pos.close()

    
    
