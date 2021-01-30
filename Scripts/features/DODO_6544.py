"""
    File name: DODO-6544.py
    Tags:
    Description: Test scripts meant to run end to end testing for commercial transaction,
    to verify alternate product are correctly printed on receipt and POS.    Author: Javier H Sandoval
    Date created: 2020-08-18 09:00:00
    Date last modified: 2020-19-13 19:00:00
    Python Version: 3.7
"""

import logging
from app import Navi, mws, pos, system, forecourt_installation, networksim, crindsim, runas
from app.framework import EDH
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app.features import feature_activation
from Scripts.features import NGFC_Helpers
import time

class DODO_6544():
    """
    Description: DODO-6324_Run commercial diesel transactions using the alternate product code for reefer
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
        networksim.set_commercial_product_limit("True","CADV","Company funds cash advance",0.00)
        networksim.set_commercial_product_limit("True", "MERC", "Default category for merchandise", 30.00)        
        networksim.set_commercial_fuel_limit("True", self.helpers.grade_1_Product , 50.00)
        networksim.set_commercial_fuel_limit("True", self.helpers.grade_2_Product , 50.00)
        networksim.set_commercial_fuel_limit("True", self.helpers.grade_3_Product , 50.00)
        networksim.set_commercial_fuel_limit_send_mode("fuel product configuration based",110,True)

        # Set Dispenser Config

        crindsim.set_mode("auto")
        crindsim.set_sales_target()        
        crindsim.select_grade(1) # Setting Disel 1 as default grade

        #open Browser
        self.pos.connect()

        self.pos.sign_on()
    
    @test
    def Prepay_TractorReefer_1(self):
        """
        To validate that in a prepay fuel transaction with tractor
        and reefer fuel, the basket and receipt display the reefer
        product name.
        """   
        #Input constants
        generic_trans_amount = "$5.00" # any value that gets an approval from the host
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts
        amounts_to_dispense = {
            self.helpers.grade_1_Name:{
                "grade": 1,
                "value": "2"
            },
            self.helpers.grade_1_Name_reefer:{
                "grade": 1,
                "value": "3"
            }
        }

        prompts = {
            f"Total Fuel limit: $110\nGrade {self.helpers.grade_1_Name} limit: 10\nGrace {self.helpers.grade_2_Name} limit: 50\nGrade {self.helpers.grade_3_Name} limit: 50":{
                "buttons": ["Ok"]
            },
            self.helpers.inside_prompts['fuel type']: {
                "buttons": ["Both fuels"]
            },
            "DEF?": {
                "buttons": ["No"]
            },
            "Additional Products Y/N?": {                    
                "buttons": ["Yes"]
            },
            "Do you want to print a receipt?": {
                "buttons": ["Yes"]
            }
        }

        #Output verifications
        receipt_data = [f"{self.helpers.grade_1_Name} CA   PUMP# 1",
                        "2.000 GAL @ $1.000/GAL         $2.00  99",
                        f"{self.helpers.grade_1_Name_reefer} CA   PUMP# 1",
                        "3.000 GAL @ $1.000/GAL         $3.00  99",
                        "Subtotal =   $5.00",
                        "Tax  =    $0.00",
                        "Total =   $5.00",
                        "Change Due  =    $0.00",
                        "Credit                          $5.00"]
        
        messages_to_verify = {
            'preauth_request_verifications' : {
                'Fuel Purchase': '500',
                'Prod 1 product Code': self.helpers.grade_1_Product,
                'Prod 2 product Code': self.helpers.grade_2_Product,
                'Prod 3 product Code': self.helpers.grade_1_Product_reefer,
                'Prod 4 product Code': self.helpers.grade_2_Product_reefer,
                'Prod 5 product Code': self.helpers.grade_3_Product,
                '001 - Wex OTR Flags': 'C - Commercial'},
            'preauth_response_verifications': {
                'Response Code': '2', 
                'Approved Amount': '000000500',
                '005 - Wex OTR Customer Information': 'ABC TRUCKING             DENVER         CO234W987'},
            'capture_request_verifications': {
                'Fuel Purchase': '500', 
                'Prod 1 product Code': self.helpers.grade_1_Product,
                'Prod 1 product Amount': '200',
                'Prod 2 product Code': self.helpers.grade_1_Product_reefer,
                'Prod 2 product Amount': '300',
                '001 - Wex OTR Flags': 'C - Commercial'},
            'capture_response_verifications': {
                'Response Code': '0', 
                'Approved Amount': '000000500',
                '005 - Wex OTR Customer Information': 'ABC TRUCKING             DENVER         CO234W987'}
        }

        self.helpers.prepay_transaction(
            card=card_to_use_NGFC,
            prepay_amount=generic_trans_amount,
            prompts=prompts,
            amounts_to_dispense=amounts_to_dispense,
            fixed_product=False,
            messages_to_verify=messages_to_verify,
            receipt_data=receipt_data
            )
    
    @test
    def Prepay_Tractor_2(self):
        """
        To validate a prepay fuel transaction with tractor fuel,
        the reefer not display in the basket and receipts.
        """   
        #Input constants
        generic_trans_amount = "$2.00" # any value that gets an approval from the host
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts
        amounts_to_dispense = {
            self.helpers.grade_1_Name:{
                "grade": 1,
                "value": "2"
            }
        }

        prompts = {
            f"Total Fuel limit: $110\nGrade {self.helpers.grade_1_Name} limit: 10\nGrace {self.helpers.grade_2_Name} limit: 50\nGrade {self.helpers.grade_3_Name} limit: 50":{
                "buttons": ["Ok"]
            },
            self.helpers.inside_prompts['fuel type']: {
                "buttons": ["Tractor fuel"]
            },
            "DEF?": {
                "buttons": ["No"]
            },
            "Additional Products Y/N?": {                    
                "buttons": ["Yes"]
            },
            "Do you want to print a receipt?": {
                "buttons": ["Yes"]
            }
        }

        #Output verifications
        receipt_data = [f"{self.helpers.grade_1_Name} CA   PUMP# 1",
                        "2.000 GAL @ $1.000/GAL         $2.00  99",
                        "Subtotal =   $2.00",
                        "Tax  =    $0.00",
                        "Total =   $2.00",
                        "Change Due  =    $0.00",
                        "Credit                          $2.00"]
        
        messages_to_verify = {
            'preauth_request_verifications' : {
                'Fuel Purchase': '200',
                'Prod 1 product Code': self.helpers.grade_1_Product,
                'Prod 2 product Code': self.helpers.grade_2_Product,
                'Prod 3 product Code': self.helpers.grade_1_Product_reefer,
                'Prod 4 product Code': self.helpers.grade_2_Product_reefer,
                'Prod 5 product Code': self.helpers.grade_3_Product,
                '001 - Wex OTR Flags': 'C - Commercial'},
            'preauth_response_verifications': {
                'Response Code': '2', 
                'Approved Amount': '000000200',
                '005 - Wex OTR Customer Information': 'ABC TRUCKING             DENVER         CO234W987'},
            'capture_request_verifications': {
                'Fuel Purchase': '200', 
                'Prod 1 product Code': self.helpers.grade_1_Product,
                'Prod 1 product Amount': '200',
                '001 - Wex OTR Flags': 'C - Commercial'},
            'capture_response_verifications': {
                'Response Code': '0', 
                'Approved Amount': '000000200',
                '005 - Wex OTR Customer Information': 'ABC TRUCKING             DENVER         CO234W987'}
        }

        self.helpers.prepay_transaction(
            card=card_to_use_NGFC,
            prepay_amount=generic_trans_amount,
            prompts=prompts,
            amounts_to_dispense=amounts_to_dispense,
            fixed_product=False,
            messages_to_verify=messages_to_verify,
            receipt_data=receipt_data
            )
    
    @test
    def Prepay_TractorDEF_3(self):
        """
        To validate a prepay fuel transaction with tractor and DEF fuel,
        the reefer should not be displayed in the basket and receipts.
        """   
        #Input constants
        generic_trans_amount = "$5.00" # any value that gets an approval from the host
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts
        amounts_to_dispense = {
            self.helpers.grade_1_Name:{
                "grade": 1,
                "value": "2"
            },
            self.helpers.grade_3_Name:{
                "grade": 3,
                "value": "3"
            }
        }

        prompts = {
            f"Total Fuel limit: $110\nGrade {self.helpers.grade_1_Name} limit: 10\nGrace {self.helpers.grade_2_Name} limit: 50\nGrade {self.helpers.grade_3_Name} limit: 50":{
                "buttons": ["Ok"]
            },
            self.helpers.inside_prompts['fuel type']: {
                "buttons": ["Tractor fuel"]
            },
            "DEF?": {
                "buttons": ["Yes"]
            },
            "Additional Products Y/N?": {                    
                "buttons": ["Yes"]
            },
            "Do you want to print a receipt?": {
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
                'Prod 1 product Code': self.helpers.grade_1_Product,
                'Prod 2 product Code': self.helpers.grade_2_Product,
                'Prod 3 product Code': self.helpers.grade_1_Product_reefer,
                'Prod 4 product Code': self.helpers.grade_2_Product_reefer,
                'Prod 5 product Code': self.helpers.grade_3_Product,
                '001 - Wex OTR Flags': 'C - Commercial'},
            'preauth_response_verifications': {
                'Response Code': '2', 
                'Approved Amount': '000000500',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_1_Product }': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_2_Product }': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_3_Product }': 'Product limit: 50.00',
                '005 - Wex OTR Customer Information': 'ABC TRUCKING             DENVER         CO234W987'},
            'capture_request_verifications': {
                'Fuel Purchase': '500', 
                'Prod 1 product Code': self.helpers.grade_1_Product,
                'Prod 1 product Amount': '200',
                'Prod 2 product Code': self.helpers.grade_3_Product,
                'Prod 2 product Amount': '300',
                '001 - Wex OTR Flags': 'C - Commercial'},
            'capture_response_verifications': {
                'Response Code': '0', 
                'Approved Amount': '000000500',
                '005 - Wex OTR Customer Information': 'ABC TRUCKING             DENVER         CO234W987'}
        }

        self.helpers.prepay_transaction(
            card=card_to_use_NGFC,
            prepay_amount=generic_trans_amount,
            prompts=prompts,
            amounts_to_dispense=amounts_to_dispense,
            fixed_product=False,
            messages_to_verify=messages_to_verify,
            receipt_data=receipt_data
            )
    
    #TODO: uncomment when it is fixed DODO-6575
    '''
    @test
    def Prepay_NoReeferDispenser_4(self):
        """
        To validate a prepay fuel transaction with tractor fuel
        and without reefer configurated in dispenser tab (forecourt),
        the reefer not display in the basket and receipt.
        """   
        #Input constants
        generic_trans_amount = "$2.00" # any value that gets an approval from the host
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts
        amounts_to_dispense = {
            self.helpers.grade_1_Name:{
                "grade": 1,
                "value": "2"
            }
        }

        prompts = {
            f"Total Fuel limit: $110\nGrade {self.helpers.grade_1_Name} limit: 10\nGrace {self.helpers.grade_2_Name} limit: 50\nGrade {self.helpers.grade_3_Name} limit: 50":{
                "buttons": ["Ok"]
            },
            self.helpers.inside_prompts['fuel type']: {
                "buttons": ["Tractor fuel"]
            },
            "Additional Products Y/N?": {                    
                "buttons": ["Yes"]
            },
            "Do you want to print a receipt?": {
                "buttons": ["Yes"]
            }
        }

        #Output verifications
        receipt_data = [f"{self.helpers.grade_1_Name} CA   PUMP# 1",
                        "2.000 GAL @ $1.000/GAL         $2.00  99",
                        "Subtotal =   $2.00",
                        "Tax  =    $0.00",
                        "Total =   $2.00",
                        "Change Due  =    $0.00",
                        "Credit                          $2.00"]
        
        messages_to_verify = {
            'preauth_request_verifications' : {
                'Fuel Purchase': '200',
                'Prod 1 product Code': {'present': True, 'value': self.helpers.grade_1_Product},
                'Prod 2 product Code': {'present': True, 'value': self.helpers.grade_2_Product},
                'Prod 3 product Code': self.helpers.grade_3_Product,
                'Prod 4 product Code': {'present': False, 'value': self.helpers.grade_1_Product_reefer},
                'Prod 5 product Code': {'present': False, 'value': self.helpers.grade_2_Product_reefer},
                '001 - Wex OTR Flags': 'C - Commercial'},
            'preauth_response_verifications': {
                'Response Code': '2', 
                'Approved Amount': '000000200',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_1_Product }': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_2_Product }': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_3_Product }': 'Product limit: 50.00',
                '005 - Wex OTR Customer Information': 'ABC TRUCKING             DENVER         CO234W987'},
            'capture_request_verifications': {
                'Fuel Purchase': '200', 
                'Prod 1 product Code': self.helpers.grade_1_Product,
                'Prod 1 product Amount': '200',
                'Prod 2 product Code': {'present': False, 'value': self.helpers.grade_3_Product},
                '001 - Wex OTR Flags': 'C - Commercial'},
            'capture_response_verifications': {
                'Response Code': '0', 
                'Approved Amount': '000000200',
                '005 - Wex OTR Customer Information': 'ABC TRUCKING             DENVER         CO234W987'}
        }

        self.pos.minimize_pos()
        
        if not self.dispenser_type_config(reefer_enable=False):
            tc_fail("Disabling 'Reefer' allowing on forecourt installation, could not be made.")
        
        self.pos.maximize_pos()

        self.helpers.prepay_transaction(
            card=card_to_use_NGFC,
            prepay_amount=generic_trans_amount,
            prompts=prompts,
            amounts_to_dispense=amounts_to_dispense,
            fixed_product=False,
            messages_to_verify=messages_to_verify,
            receipt_data=receipt_data
            )

        self.log.info("Reseting forecourt products to original values")
        self.pos.minimize_pos()
        
        if not self.dispenser_type_config(reefer_enable=True):
            tc_fail("Re-enabling 'Reefer' allowing on forecourt installation, could not be made.  Following test cases will fail.")

        self.pos.maximize_pos()
    '''
    @test
    def Prepay_NoReeferProduct_5(self):
        """
        To validate a prepay fuel transaction with tractor fuel and without
        reefer configurated in product (forecourt), the reefer not display
        in the basket and receipt.
        """   
        #Input constants
        generic_trans_amount = "$5.00" # any value that gets an approval from the host
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts
        amounts_to_dispense = {
            self.helpers.grade_1_Name:{
                "grade": 1,
                "value": "2"
            },
            self.helpers.grade_3_Name:{
                "grade": 3,
                "value": "3"
            }
        }

        prompts = {
            f"Total Fuel limit: $110\nGrade {self.helpers.grade_1_Name} limit: 10\nGrace {self.helpers.grade_2_Name} limit: 50\nGrade {self.helpers.grade_3_Name} limit: 50":{
                "buttons": ["Ok"]
            },
            self.helpers.inside_prompts['fuel type']: {
                "buttons": ["Both fuels"]
            },
            "Additional Products Y/N?": {                    
                "buttons": ["Yes"]
            },
            "Do you want to print a receipt?": {
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
                'Prod 1 product Code': {'present': True, 'value': self.helpers.grade_1_Product},
                'Prod 2 product Code': {'present': True, 'value': self.helpers.grade_2_Product},
                'Prod 3 product Code': self.helpers.grade_3_Product,
                'Prod 4 product Code': {'present': False, 'value': self.helpers.grade_1_Product_reefer},
                'Prod 5 product Code': {'present': False, 'value': self.helpers.grade_2_Product_reefer},
                '001 - Wex OTR Flags': 'C - Commercial'},
            'preauth_response_verifications': {
                'Response Code': '2', 
                'Approved Amount': '000000500',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_1_Product }': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_2_Product }': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_3_Product }': 'Product limit: 50.00',
                '005 - Wex OTR Customer Information': 'ABC TRUCKING             DENVER         CO234W987'},
            'capture_request_verifications': {
                'Fuel Purchase': '500', 
                'Prod 1 product Code': self.helpers.grade_1_Product,
                'Prod 1 product Amount': '200',
                'Prod 2 product Code': self.helpers.grade_3_Product,
                'Prod 2 product Amount': '300',
                '001 - Wex OTR Flags': 'C - Commercial'},
            'capture_response_verifications': {
                'Response Code': '0', 
                'Approved Amount': '000000500',
                '005 - Wex OTR Customer Information': 'ABC TRUCKING             DENVER         CO234W987'}
        }
        self.log.debug("Wait for the last update in previous test case is applied")
        self.pos.wait_disp_ready(idle_timeout=120)

        products_changes = {
            self.helpers.grade_1_Name: {
                "grade": self.helpers.grade_1_Name,
                "reefer_grade": "" 
            },
            self.helpers.grade_2_Name: {
                "grade": self.helpers.grade_2_Name,
                "reefer_grade": ""
            }
        }

        self.pos.minimize_pos()

        self.change_forecourtinstallation_product(products_changes)

        self.pos.maximize_pos()

        self.helpers.prepay_transaction(
            card=card_to_use_NGFC,
            prepay_amount=generic_trans_amount,
            prompts=prompts,
            amounts_to_dispense=amounts_to_dispense,
            fixed_product=False,
            messages_to_verify=messages_to_verify,
            receipt_data=receipt_data
            )

        self.log.info("Reseting forecourt products to original values")
        self.pos.minimize_pos()

        products_changes = {
            self.helpers.grade_1_Name: {
                "grade": self.helpers.grade_1_Name,
                "reefer_grade": self.helpers.grade_1_Name_reefer
            },
            self.helpers.grade_2_Name: {
                "grade": self.helpers.grade_2_Name,
                "reefer_grade": self.helpers.grade_2_Name_reefer
            }
        }

        self.change_forecourtinstallation_product(products_changes)

        self.pos.maximize_pos()
    
    #TODO: uncomment when it is fixed TN-864
    '''
    @test
    def Outside_Tractor_6(self):
        """
        To validate an outside fuel transaction with tractor fuel,
        the reefer not display in the basket and receipt.
        """   
        #Input constants
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts
        amounts_to_dispense = {
            self.helpers.grade_1_Name:{
                "grade": 1,
                "value": "2"
            }
        }

        prompts = {
            "Make selection":{
                "entry": [""],
                "buttons": ['Tractor']
            },
            "Need DEF?": {
                "entry": [""],
                "buttons": ['No']
            },
            "Additional Products Y/N?": {                    
                "entry": [""],
                "buttons": ['Yes']
            },
            "Want receipt?": {
                "entry": [""],
                "buttons": ['No']
            },
            "Carwash today?": {
                "entry": [""],
                "buttons": ['No']
            }
        }

        #Output verifications
        receipt_data = [f"{self.helpers.grade_1_Name} CA   PUMP# 1",
                        "2.000 GAL @ $1.000/GAL         $2.00  99",
                        "Subtotal =   $2.00",
                        "Tax  =    $0.00",
                        "Total =   $2.00",
                        "Change Due  =    $0.00",
                        "Credit                          $2.00"]
        
        messages_to_verify = {
            'preauth_request_verifications' : {
                'Fuel Purchase': '5000',
                'Prod 1 product Code': {'present': True, 'value': self.helpers.grade_1_Product},
                'Prod 2 product Code': {'present': True, 'value': self.helpers.grade_2_Product},
                'Prod 3 product Code': {'present': True, 'value': self.helpers.grade_1_Product_reefer},
                'Prod 4 product Code': {'present': True, 'value': self.helpers.grade_2_Product_reefer},
                'Prod 5 product Code': {'present': True, 'value': self.helpers.grade_3_Product},
                '001 - Wex OTR Flags': 'C - Commercial'},
            'preauth_response_verifications': {
                'Response Code': '2', 
                'Approved Amount': '000005000',
                '005 - Wex OTR Customer Information': 'ABC TRUCKING             DENVER         CO234W987'},
            'capture_request_verifications': {
                'Fuel Purchase': '200', 
                'Prod 1 product Code': self.helpers.grade_1_Product,
                'Prod 1 product Amount': '200',
                '001 - Wex OTR Flags': 'C - Commercial'},
            'capture_response_verifications': {
                'Response Code': '0', 
                'Approved Amount': '000000200',
                '005 - Wex OTR Customer Information': 'ABC TRUCKING             DENVER         CO234W987'}
        }

        self.helpers.dispenser_transaction(
            card=card_to_use_NGFC,
            prompts=prompts,
            amounts_to_dispense=amounts_to_dispense,
            fixed_product=False,
            messages_to_verify=messages_to_verify,
            receipt_data=receipt_data
            )
    '''
    #TODO: uncomment when it is fixed TN-864
    '''
    @test
    def Outside_TractorReefer_7(self):
        """
        To validate an outside fuel transaction with tractor and
        reefer fuel, the basket and receipts should display the reefer
        product name.
        """   
        #Input constants
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts
        amounts_to_dispense = {
            self.helpers.grade_1_Name:{
                "grade": 1,
                "value": "2"
            },
            self.helpers.grade_1_Name_reefer:{
                "grade": 1,
                "value": "3"
            }
        }

        prompts = {
            "Make selection":{
                "entry": [""],
                "buttons": ['Both']
            },
            "Need DEF?": {
                "entry": [""],
                "buttons": ['No']
            },
            "Additional Products Y/N?": {                    
                "entry": [""],
                "buttons": ['Yes']
            },
            "Want receipt?": {
                "entry": [""],
                "buttons": ['No']
            },
            "Carwash today?": {
                "entry": [""],
                "buttons": ['No']
            }
        }

        #Output verifications
        receipt_data = [f"{self.helpers.grade_1_Name} CA   PUMP# 1",
                        "2.000 GAL @ $1.000/GAL         $2.00  99",
                        f"{self.helpers.grade_1_Name_reefer} CA   PUMP# 1",
                        "3.000 GAL @ $1.000/GAL         $3.00  99",
                        "Subtotal =   $5.00",
                        "Tax  =    $0.00",
                        "Total =   $5.00",
                        "Change Due  =    $0.00",
                        "Credit                          $5.00"]
        
        messages_to_verify = {
            'preauth_request_verifications' : {
                'Fuel Purchase': '5000',
                'Prod 1 product Code': self.helpers.grade_1_Product,
                'Prod 2 product Code': self.helpers.grade_2_Product,
                'Prod 3 product Code': self.helpers.grade_1_Product_reefer,
                'Prod 4 product Code': self.helpers.grade_2_Product_reefer,
                'Prod 5 product Code': self.helpers.grade_3_Product,
                '001 - Wex OTR Flags': 'C - Commercial'},
            'preauth_response_verifications': {
                'Response Code': '2', 
                'Approved Amount': '000005000',
                '005 - Wex OTR Customer Information': 'ABC TRUCKING             DENVER         CO234W987'},
            'capture_request_verifications': {
                'Fuel Purchase': '500', 
                'Prod 1 product Code': self.helpers.grade_1_Product,
                'Prod 1 product Amount': '200',
                'Prod 2 product Code': 'self.helpers.grade_1_Product_reefer,
                'Prod 2 product Amount': '300',
                '001 - Wex OTR Flags': 'C - Commercial'},
            'capture_response_verifications': {
                'Response Code': '0', 
                'Approved Amount': '000000500',
                '005 - Wex OTR Customer Information': 'ABC TRUCKING             DENVER         CO234W987'}
        }

        self.helpers.dispenser_transaction(
            card=card_to_use_NGFC,
            prompts=prompts,
            amounts_to_dispense=amounts_to_dispense,
            fixed_product=False,
            messages_to_verify=messages_to_verify,
            receipt_data=receipt_data
            )
    '''
    #TODO: uncomment when it is fixed TN-864
    '''
    @test
    def Outside_TractorDEF_8(self):
        """
        To validate an outside fuel transaction with tractor and
        reefer fuel, the reefer should not be displayed in the basket
        and receipt.
        """   
        #Input constants
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts
        amounts_to_dispense = {
            self.helpers.grade_1_Name:{
                "grade": 1,
                "value": "2"
            },
            self.helpers.grade_3_Name:{
                "grade": 3,
                "value": "3"
            }
        }

        prompts = {
            "Make selection":{
                "entry": [""],
                "buttons": ['Tractor']
            },
            "Need DEF?": {
                "entry": [""],
                "buttons": ['Yes']
            },
            "Additional Products Y/N?": {                    
                "entry": [""],
                "buttons": ['Yes']
            },
            "Want receipt?": {
                "entry": [""],
                "buttons": ['No']
            },
            "Carwash today?": {
                "entry": [""],
                "buttons": ['No']
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
                'Fuel Purchase': '5000',
                'Prod 1 product Code': self.helpers.grade_1_Product,
                'Prod 2 product Code': self.helpers.grade_2_Product,
                'Prod 3 product Code': self.helpers.grade_1_Product_reefer,
                'Prod 4 product Code': self.helpers.grade_2_Product_reefer,
                'Prod 5 product Code': self.helpers.grade_3_Product,
                '001 - Wex OTR Flags': 'C - Commercial'},
            'preauth_response_verifications': {
                'Response Code': '2', 
                'Approved Amount': '000005000',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_1_Product }': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_2_Product }': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_3_Product }': 'Product limit: 50.00',
                '005 - Wex OTR Customer Information': 'ABC TRUCKING             DENVER         CO234W987'},
            'capture_request_verifications': {
                'Fuel Purchase': '500', 
                'Prod 1 product Code': self.helpers.grade_1_Product,
                'Prod 1 product Amount': '200',
                'Prod 2 product Code': self.helpers.grade_3_Product,
                'Prod 2 product Amount': '300',
                '001 - Wex OTR Flags': 'C - Commercial'},
            'capture_response_verifications': {
                'Response Code': '0', 
                'Approved Amount': '000000500',
                '005 - Wex OTR Customer Information': 'ABC TRUCKING             DENVER         CO234W987'}
        }

        self.helpers.dispenser_transaction(
            card=card_to_use_NGFC,
            prompts=prompts,
            amounts_to_dispense=amounts_to_dispense,
            fixed_product=False,
            messages_to_verify=messages_to_verify,
            receipt_data=receipt_data
            )
    '''
    #TODO: uncomment when it is fixed TN-863
    '''
    @test
    def Outside_NoReeferProduct_9(self):
        """
        To validate an outside fuel transaction with tractor fuel
        and without reefer configurated int product (forecourt),
        the reefer not display in the basket and receipt.
        """   
        #Input constants
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts
        amounts_to_dispense = {
            self.helpers.grade_1_Name:{
                "grade": 1,
                "value": "2"
            },
            self.helpers.grade_3_Name:{
                "grade": 3,
                "value": "3"
            }
        }

        prompts = {
            "Make selection":{
                "entry": [""],
                "buttons": ['Both']
            },
            "Additional Products Y/N?": {                    
                "entry": [""],
                "buttons": ['Yes']
            },
            "Want receipt?": {
                "entry": [""],
                "buttons": ['No']
            },
            "Carwash today?": {
                "entry": [""],
                "buttons": ['No']
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
                'Fuel Purchase': '5000',
                'Prod 1 product Code': {'present': True, 'value': self.helpers.grade_1_Product},
                'Prod 2 product Code': {'present': True, 'value': self.helpers.grade_2_Product},
                'Prod 3 product Code': self.helpers.grade_3_Product,
                'Prod 4 product Code': {'present': False, 'value': self.helpers.grade_1_Product_reefer},
                'Prod 5 product Code': {'present': False, 'value': self.helpers.grade_2_Product_reefer},
                '001 - Wex OTR Flags': 'C - Commercial'},
            'preauth_response_verifications': {
                'Response Code': '2', 
                'Approved Amount': '000005000',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_1_Product }': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_2_Product }': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_3_Product }': 'Product limit: 50.00',
                '005 - Wex OTR Customer Information': 'ABC TRUCKING             DENVER         CO234W987'},
            'capture_request_verifications': {
                'Fuel Purchase': '500', 
                'Prod 1 product Code': self.helpers.grade_1_Product,
                'Prod 1 product Amount': '200',
                'Prod 2 product Code': self.helpers.grade_3_Product,
                'Prod 2 product Amount': '300',
                '001 - Wex OTR Flags': 'C - Commercial'},
            'capture_response_verifications': {
                'Response Code': '0', 
                'Approved Amount': '000000500',
                '005 - Wex OTR Customer Information': 'ABC TRUCKING             DENVER         CO234W987'}
        }
        self.log.debug("Wait for the last update in previous test case is applied")
        self.pos.wait_disp_ready(idle_timeout=120)

        products_changes = {
            self.helpers.grade_1_Name: {
                "grade": self.helpers.grade_1_Name,
                "reefer_grade": ""
            },
            self.helpers.grade_2_Name: {
                "grade": self.helpers.grade_2_Name,
                "reefer_grade": ""
            }
        }

        self.pos.minimize_pos()

        self.change_forecourtinstallation_product(products_changes)
       
        self.pos.maximize_pos()

        self.helpers.dispenser_transaction(
            card=card_to_use_NGFC,
            prompts=prompts,
            amounts_to_dispense=amounts_to_dispense,
            fixed_product=False,
            messages_to_verify=messages_to_verify,
            receipt_data=receipt_data
            )

        self.log.info("Reseting forecourt products to original values")
        self.pos.minimize_pos()
        
        products_changes = {
            self.helpers.grade_1_Name: {
                "grade": self.helpers.grade_1_Name,
                "reefer_grade": self.helpers.grade_1_Name_reefer
            },
            self.helpers.grade_2_Name: {
                "grade": self.helpers.grade_2_Name,
                "reefer_grade": self.helpers.grade_2_Name_reefer
            }
        }

        self.pos.minimize_pos()

        self.change_forecourtinstallation_product(products_changes)

        self.pos.maximize_pos()
    '''
    #TODO: uncomment when it is fixed TN-864
    '''
    @test
    def Outside_NoReeferDispenser_10(self):
        """
        To validate an outside fuel transaction ith tractor fuel and
        without reefer configurated in dispenser (forecourt),
        the reefer not display in the basket and receipt.
        """   
        #Input constants
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts
        amounts_to_dispense = {
            self.helpers.grade_1_Name:{
                "grade": 1,
                "value": "5"
            }
        }

        prompts = {
            "Make selection":{
                "entry": [""],
                "buttons": ['Tractor']
            },
            "Need DEF?": {
                "entry": [""],
                "buttons": ['No']
            },
            "Additional Products Y/N?": {                    
                "entry": [""],
                "buttons": ['Yes']
            },
            "Want receipt?": {
                "entry": [""],
                "buttons": ['No']
            },
            "Carwash today?": {
                "entry": [""],
                "buttons": ['No']
            }
        }

        #Output verifications
        receipt_data = [f"{self.helpers.grade_1_Name} CA   PUMP# 1",
                        "5.000 GAL @ $1.000/GAL         $5.00  99",
                        "Subtotal =   $5.00",
                        "Tax  =    $0.00",
                        "Total =   $5.00",
                        "Change Due  =    $0.00",
                        "Credit                          $5.00"]
        
        messages_to_verify = {
            'preauth_request_verifications' : {
                'Fuel Purchase': '5000',
                'Prod 1 product Code': {'present': True, 'value': self.helpers.grade_1_Product},
                'Prod 2 product Code': {'present': True, 'value': self.helpers.grade_2_Product},
                'Prod 3 product Code': self.helpers.grade_3_Product,
                'Prod 4 product Code': {'present': False, 'value': self.helpers.grade_1_Product_reefer},
                'Prod 5 product Code': {'present': False, 'value': self.helpers.grade_2_Product_reefer},
                '001 - Wex OTR Flags': 'C - Commercial'},
            'preauth_response_verifications': {
                'Response Code': '2', 
                'Approved Amount': '000005000',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_1_Product }': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_2_Product }': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_3_Product }': 'Product limit: 50.00',
                '005 - Wex OTR Customer Information': 'ABC TRUCKING             DENVER         CO234W987'},
            'capture_request_verifications': {
                'Fuel Purchase': '500', 
                'Prod 1 product Code': self.helpers.grade_1_Product,
                'Prod 1 product Amount': '500',
                'Prod 2 product Code': {'present': False, 'value': self.helpers.grade_3_Product},
                '001 - Wex OTR Flags': 'C - Commercial'},
            'capture_response_verifications': {
                'Response Code': '0', 
                'Approved Amount': '000000500',
                '005 - Wex OTR Customer Information': 'ABC TRUCKING             DENVER         CO234W987'}
        }

        self.pos.minimize_pos()
        
        if not self.dispenser_type_config(reefer_enable=False):
            tc_fail("Disabling 'Reefer' allowing on forecourt installation, could not be made.")
        
        self.pos.maximize_pos()

        self.helpers.dispenser_transaction(
            card=card_to_use_NGFC,
            prompts=prompts,
            amounts_to_dispense=amounts_to_dispense,
            fixed_product=False,
            messages_to_verify=messages_to_verify,
            receipt_data=receipt_data
            )

        self.log.info("Reseting forecourt products to original values")
        self.pos.minimize_pos()
        
        if not self.dispenser_type_config(reefer_enable=True):
            tc_fail("Re-enabling 'Reefer' allowing on forecourt installation, could not be made.  Following test cases will fail.")

        self.pos.maximize_pos()
    '''
    '''
    @test
    def Offline_Prepay_TractorReefer_13(self):
        """
        To validate and offline prepay fuel transaction with tractor
        and reefer fuel, the reefer is display in the basket and receipt.
        """   
        #Input constants
        generic_trans_amount = "$5.00" # any value that gets an approval from the host
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts
        amounts_to_dispense = {
            self.helpers.grade_1_Name:{
                "grade": 1,
                "value": "2"
            },
            self.helpers.grade_1_Name_reefer:{
                "grade": 1,
                "value": "3"
            }
        }

        prompts = {
            f"Total Fuel limit: $110\nGrade {self.helpers.grade_1_Name} limit: 10\nGrace {self.helpers.grade_2_Name} limit: 50\nGrade {self.helpers.grade_3_Name} limit: 50":{
                "buttons": ["Ok"]
            },
            self.helpers.inside_prompts['fuel type']: {
                "buttons": ["Both fuels"]
            },
            "DEF?": {
                "buttons": ["No"]
            },
            "Additional Products Y/N?": {                    
                "buttons": ["Yes"]
            },
            "Do you want to print a receipt?": {
                "buttons": ["Yes"]
            }
        }

        #Output verifications
        receipt_data = [f"{self.helpers.grade_1_Name} CA   PUMP# 1",
                        "2.000 GAL @ $1.000/GAL         $2.00  99",
                        f"{self.helpers.grade_1_Name_reefer} CA   PUMP# 1",
                        "3.000 GAL @ $1.000/GAL         $3.00  99",
                        "Subtotal =   $5.00",
                        "Tax  =    $0.00",
                        "Total =   $5.00",
                        "Change Due  =    $0.00",
                        "Credit                          $5.00"]
        
        messages_to_verify = {
            'capture_request_verifications': {
                'Fuel Purchase': '500', 
                'Prod 1 product Code': self.helpers.grade_1_Product,
                'Prod 1 product Amount': '200',
                'Prod 2 product Code': self.helpers.grade_1_Product_reefer,
                'Prod 2 product Amount': '300',
                'Prod 3 product Code': {'present': False, 'value':''},
                '001 - Wex OTR Flags': 'C - Commercial'},
            'capture_response_verifications': {
                'Response Code': '0', 
                'Approved Amount': '000000500',
                '005 - Wex OTR Customer Information': 'ABC TRUCKING             DENVER         CO234W987'}
        }
        
        self.log.debug(f"Try to set new values for XOM_Restrictions table.")
        setProductRestrictions = self.set_products_restriction('EXXON', card_to_use_NGFC)

        self.log.debug("Get Hot simulator stopped")
        networksim.stop_simulator()
        simulator_status = networksim.get_network_status()
        self.log.debug("stop: " + simulator_status["payload"]["status"])

        self.log.debug("Save previous valued for the amount")
        MaxAmtList = self.helpers.get_saf_MaxAmt(brand='EXXON', card=card_to_use_NGFC)
        self.log.debug("Apply new value for the amount")
        setMaxAmtValue = self.helpers.set_saf_MaxAmt(brand='EXXON', card=card_to_use_NGFC, limit='9999.99')
        if not setMaxAmtValue.find(f"{len(MaxAmtList)} row"): #validate that new values were applied
            tc_fail('Unable to set max amount limits in XOM_SAF table')

        self.log.debug("Save previous valued for the number")
        MaxNumList = self.helpers.get_saf_MaxNum(brand='EXXON', card=card_to_use_NGFC)
        self.log.debug("Apply new value for the number")
        setMaxNumValue = self.helpers.set_saf_MaxNum(brand='EXXON', card=card_to_use_NGFC, limit='99')

        if not setMaxNumValue.find(f"{len(MaxNumList)} row"): #validate that new values were applied
            tc_fail('Unable to set max num limits in XOM_SAF table')

        self.helpers.prepay_transaction(
            card=card_to_use_NGFC,
            prepay_amount=generic_trans_amount,
            prompts=prompts,
            amounts_to_dispense=amounts_to_dispense,
            fixed_product=False,
            receipt_data=receipt_data
            )

        self.log.debug("Restart Host simulator")
        networksim.start_simulator()
        simulator_status = networksim.get_network_status()
        self.log.debug("start: " + simulator_status["payload"]["status"])
        start_time = time.time()
        tiempo = time.time() - start_time
        while (simulator_status["payload"]["status"] != 'Online') and (tiempo < 60):
            simulator_status = networksim.get_network_status()
            self.log.debug(simulator_status["payload"]["status"])
            tiempo = time.time() - start_time
        
        if simulator_status["payload"]["status"] != 'Online':
            tc_fail('Unable to get host simulator online')

        self.log.debug("Check the last message in the EDH before start")
        last_msg = self.edh.get_last_msg_id(pspid='23')

        setMaxAmtValue = self.helpers.set_saf_MaxAmt(brand='EXXON', card=card_to_use_NGFC, limit=MaxAmtList)
        self.log.debug(f"Go back previous values for the amount; result: {setMaxAmtValue}")
        if not setMaxAmtValue.find(f"{len(MaxAmtList)} row"): #validate that previous values were applied
            tc_fail('Unable to reset previous value for total amount limit in XOM_SAF table')
        
        setMaxNumValue = self.helpers.set_saf_MaxNum(brand='EXXON', card=card_to_use_NGFC, limit=MaxNumList)
        self.log.debug(f"Go back previous values for the number; result: {setMaxNumValue}")
        if not setMaxNumValue.find(f"{len(MaxNumList)} row"): #validate that previous values were applied
            tc_fail('Unable to reset previous value for total transacions limit in XOM_SAF table')

        self.log.debug(f"Try to back original values for XOM_Restrictions table.")
        self.reset_products_restriction(setProductRestrictions[0], setProductRestrictions[1], setProductRestrictions[2])

        #Validate send messages after host gets online
        message_types = [
            "capture_request_verifications",
            "capture_response_verifications"
        ]

        if not messages_to_verify is None:

            self.log.debug("Try to get 2 messages (completion)")
            messages = self.edh.get_network_messages(4,start_in=last_msg)
            
            start_time = time.time()
            while len(messages) < 2 and (time.time() - start_time < 60):
                self.log.debug("There are messages pending to be generated, retrying to get all of them.")
                messages = self.edh.get_network_messages(8,start_in=last_msg)
            if len(messages) < 2:
                tc_fail("The messages obtained from the EDH do not contain all requests and responses messages")

            messages_num = 2

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
                    
                except KeyError:
                    tc_fail('Unable to verify the network messages')
    '''
    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """

        self.pos.close()
    
    def change_forecourtinstallation_product(self, changes):
        self.log.info(f"Trying to set {changes}")
        fc = forecourt_installation.ForecourtInstallation()

        mws.click("Set Up")

        for item in changes:

            mws.select_tab("Tank - Product to")

            if not fc.change(item,
                    "Product", 
                    config={"Name": changes[item]['grade'],
                            "Reefer": changes[item]['reefer_grade']
                    }):
                return False
            
        if not mws.click_toolbar("Save"):
            self.log.error("Unable to save Dispenser Options")
            return False
        
        if not mws.click_toolbar("Save"):
            self.log.error("Unable to save Dispenser Options")
            return False
        self.log.info(f"{changes} already set")
                
        self.mws.wait_for_button("Forecourt Installation")
        
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

        mws.wait_for_button("Forecourt Installation")

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

        mws.wait_for_button("Forecourt Installation")

        return True
    
    def set_products_restriction(self, brand, card):

        """
        Set new restriction key with limits for cash advance and non fuel products
        Args:
            brand(str): brand name to identify the card which is used.
            card(str): the card name to identify the track to be used.

        Returns:
            restrictions_key: new sa restrictions key added to this test case purpouses
            rulesKeyValue[0]: rules key affected
            safRestrictionsKey[0]: original saf restrictions key.
        """
        #parameters
        product_list=['0**','***','955']
        #find the correct ruleskey value
        cardNumber = crindsim._get_card_data(brand=brand, card_name = card)['Track2']
        cardNumber = cardNumber.split('=')
        query = f"select RulesKey from XOM_Bin where beginrange <= left('{cardNumber[0]}', len(BeginRange)) and EndRange >= left('{cardNumber[0]}', len(Endrange)) and Mode = 'C'"
        rulesKeyValue = runas.run_sqlcmd(query, database="network", cmdshell=False)['output']
        rulesKeyValue = rulesKeyValue.split("\n")
        rulesKeyValue = rulesKeyValue[2:-3]
        
        #find the correct safrestrictionskey value
        query = f"select SAFRestrictionsKey from XOM_Rules where ruleskey = '{rulesKeyValue[0]}'"
        safRestrictionsKey = runas.run_sqlcmd(query, database="network", cmdshell=False)['output']
        safRestrictionsKey = safRestrictionsKey.split("\n")
        safRestrictionsKey = safRestrictionsKey[2:-3]

        query = "select RestrictionsKey from XOM_Restrictions"

        output = runas.run_sqlcmd(query, database="network", cmdshell=False)['output']

        # Turning string into list of strings that have \n delimitation
        output_list = output.split("\n")
        output_list = output_list[2:-3]
        current_list = len(output_list)
        restrictions_key= int(output_list[current_list - 1]) + 1
        restriction_index = len(output_list)
        for i in range(len(product_list)):
            restriction_index = restriction_index + 1
            product_code = product_list[i]
            query = f"insert into xom_restrictions values ('{restriction_index}', '{restrictions_key}', '{product_code}', '250.00', '1')"
            insert_result = runas.run_sqlcmd(query, database="network", cmdshell=False)['output']
            if not insert_result == '\n(1 rows affected)\n':
                tc_fail("New product could not be set on restrictions table")
            
        query = f"update xom_rules set SAFRestrictionsKey = '{restrictions_key}' where ruleskey = '{rulesKeyValue[0]}'"
        rules_update_result = runas.run_sqlcmd(query, database="network", cmdshell=False)['output']
        if not rules_update_result == '\n(1 rows affected)\n':
                tc_fail("SAF restriction key could not be set on rules table")

        return [restrictions_key, rulesKeyValue[0], safRestrictionsKey[0]]

    def reset_products_restriction(self, restrictions_key, rulesKeyValue, safRestrictionsKey):
        """
        Reset original restriction key with limits for cash advance and non fuel products,
        It should be executed after set_products_restriction()
        Args:
            brand(str): brand name to identify the card which is used.
            card(str): the card name to identify the track to be used.

        Returns:
            restrictions_key: new sa restrictions key added to this test case purpouses
            rulesKeyValue[0]: rules key affected
            safRestrictionsKey[0]: original saf restrictions key.
        """
        
        query = f"update xom_rules set SAFRestrictionsKey = '{safRestrictionsKey}' where ruleskey = '{rulesKeyValue}'"
        output = runas.run_sqlcmd(query, database="network", cmdshell=False)['output']
        if not output == '\n(1 rows affected)\n':
                tc_fail("Rules table could not be reset to the original values")

        query = f"delete xom_restrictions where restrictionskey = '{restrictions_key}'"
        output = runas.run_sqlcmd(query, database="network", cmdshell=False)['output']
        if not output == '\n(3 rows affected)\n':
                tc_fail("Rules table could not be reset to the original values")
        
        return True
