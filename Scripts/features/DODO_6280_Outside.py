"""
    File name: DODO_6280_Outside.py
    Tags:
    Description: Test scripts meant to verify correct prossesing of dynamic prompts inside
    and correct printing on receipts.
    Author: Javier Sandoval
    Date created: 2020-06-22 14:00:00
    Date last modified: 2020-04-26 17:00:00
    Python Version: 3.7
"""

import logging
from app import Navi, mws, pos, system, networksim, crindsim, runas, network_site_config
from app.framework import EDH
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app.features import feature_activation
from Scripts.features import NGFC_Helpers
import time

class DODO_6280_Outside():
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

        # The main crind sim object
        self.crindsim = crindsim

        # Customer information values
        self.customerInfo = ["AB TRUCKING", "DENVER", "CO", "234W987"]

        self.helpers = NGFC_Helpers.NGFC_Helpers(self.log, self.mws)

    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        """

        #Commercial Diesel checkbox activation in forecourt installation 
        #self.helpers.set_commercial_on_forecourt()

        # cash advance to 0
        self.set_cash_advance_on_mws('000')

        # HostSim Response mode
        networksim.set_response_mode("Approval")
                
        # Disable all promtps
        networksim.disable_commercial_fuel_limits()
        networksim.disable_product_limits()

        # Set specif config for this script
        networksim.set_commercial_customer_information(self.customerInfo[0], self.customerInfo[1], self.customerInfo[2], self.customerInfo[3])
        networksim.set_commercial_product_limit("True","CADV","Company funds cash advance",0.00)
        networksim.set_commercial_product_limit("True", "MERC", "Default category for merchandise", 30.00)        
        networksim.set_commercial_fuel_limit("True", self.helpers.grade_1_Product, 50.00)
        networksim.set_commercial_fuel_limit("True", self.helpers.grade_2_Product, 50.00)
        networksim.set_commercial_fuel_limit("True", self.helpers.grade_3_Product, 50.00)
        networksim.set_commercial_fuel_limit_send_mode("fuel product configuration based",110,True)

        crindsim.set_mode("auto")
        crindsim.set_sales_target()

        #open Browser
        self.pos.connect()
        self.pos.sign_on()
    
    @test
    def Outside_BDAY(self): #1
        """
        Outside transactions with NGFC cards with Birthday prompt
        in order to validate it.
        """

        prompt_value = '110287'
        prompt_code = 'BDAY'
        hostsim_prompt_text = 'Birthday information'
        hostsim_prompt_mask = 'N;TS;M1;X25' 
        dispenser_prompt_text = 'Press ENTER/OK when done CANCEL to Cancel Enter Birthday information in MMDDYY format'
        message_prompt_text = '004 - Wex OTR Prompt Data - Prompt: BDAY (Birthday information in MMDDYY format)'        
        self.dispenser_transaction(
            prompt_value=prompt_value,
            prompt_code=prompt_code,
            hostsim_prompt_text=hostsim_prompt_text,
            hostsim_prompt_mask=hostsim_prompt_mask,
            prompt_text=dispenser_prompt_text,
            message_prompt_text=message_prompt_text
            )
    
    @test
    def Outside_BLID(self): #2
        """
        Outside transactions with NGFC cards with Billing ID prompt
        in order to validate it.
        """

        prompt_value = '100002'
        prompt_code = 'BLID'
        hostsim_prompt_text = 'Billing ID'
        hostsim_prompt_mask = 'N;TS;M=1;X=25'
        dispenser_prompt_text = 'Press ENTER/OK when done CANCEL to Cancel Enter Billing Id'
        message_prompt_text = '004 - Wex OTR Prompt Data - Prompt: BLID (Billing ID)'
        self.dispenser_transaction(
            prompt_value=prompt_value,
            prompt_code=prompt_code,
            hostsim_prompt_text=hostsim_prompt_text,
            hostsim_prompt_mask=hostsim_prompt_mask,
            prompt_text=dispenser_prompt_text,
            message_prompt_text=message_prompt_text
            )
    
    @test
    def Outside_CNTN(self): #3
        """
        Outside transactions with NGFC cards with Control number prompt
        in order to validate it.
        """

        prompt_value = '245777'
        prompt_code = 'CNTN'
        hostsim_prompt_text = 'Control number'
        hostsim_prompt_mask = 'N;TS;M=1;X=25'
        dispenser_prompt_text = 'Press ENTER/OK when done CANCEL to Cancel Enter Control Number'
        message_prompt_text = '004 - Wex OTR Prompt Data - Prompt: CNTN (Control number)'
        self.dispenser_transaction(
            prompt_value=prompt_value,
            prompt_code=prompt_code,
            hostsim_prompt_text=hostsim_prompt_text,
            hostsim_prompt_mask=hostsim_prompt_mask,
            prompt_text=dispenser_prompt_text,
            message_prompt_text=message_prompt_text
            )
    
    @test
    def Outside_DLIC(self): #4
        """
        Outside transactions with NGFC cards with Drivers license number prompt
        in order to validate it.
        """

        prompt_value = '1254'
        prompt_code = 'DLIC'
        hostsim_prompt_text = 'Drivers license number'
        hostsim_prompt_mask = 'N;TS;M=1;X=25'
        dispenser_prompt_text = "Press ENTER/OK when done CANCEL to Cancel Enter Driver's License Number"
        message_prompt_text = '004 - Wex OTR Prompt Data - Prompt: DLIC (Driver’s license number)'
        self.dispenser_transaction(
            prompt_value=prompt_value,
            prompt_code=prompt_code,
            hostsim_prompt_text=hostsim_prompt_text,
            hostsim_prompt_mask=hostsim_prompt_mask,
            prompt_text=dispenser_prompt_text,
            message_prompt_text=message_prompt_text
            )
    
    @test
    def Outside_DLST(self): #5
        """
        Outside transactions with NGFC cards with Drivers license number prompt
        in order to validate it.
        """

        prompt_value = '27420'
        prompt_code = 'DLST'
        hostsim_prompt_text = 'Drivers license state'
        hostsim_prompt_mask = 'N;TS;M=1;X=25'
        dispenser_prompt_text = "Press ENTER/OK when done CANCEL to Cancel Enter Driver's License State"
        message_prompt_text = "004 - Wex OTR Prompt Data - Prompt: DLST (Driver’s license state)"
        self.dispenser_transaction(
            prompt_value=prompt_value,
            prompt_code=prompt_code,
            hostsim_prompt_text=hostsim_prompt_text,
            hostsim_prompt_mask=hostsim_prompt_mask,
            prompt_text=dispenser_prompt_text,
            message_prompt_text=message_prompt_text
            )
    
    @test
    def Outside_DRID(self): #6
        """
        Outside transactions with NGFC cards with Driver ID prompt
        in order to validate it.
        """
        prompt_value = '321456'
        prompt_code = 'DRID'
        hostsim_prompt_text = 'Driver ID'
        hostsim_prompt_mask = 'N;TS;M=1;X=10' 
        dispenser_prompt_text = 'Press ENTER/OK when done CANCEL to Cancel Enter Driver ID'
        message_prompt_text = '004 - Wex OTR Prompt Data - Prompt: DRID (Driver ID)'
        self.dispenser_transaction(
            prompt_value=prompt_value,
            prompt_code=prompt_code,
            hostsim_prompt_text=hostsim_prompt_text,
            hostsim_prompt_mask=hostsim_prompt_mask,
            prompt_text=dispenser_prompt_text,
            message_prompt_text=message_prompt_text
            )
    
    @test
    def Outside_DTKT(self): #7
        """
        Outside transactions with NGFC cards with Delivery ticket number prompt
        in order to validate it.
        """
        prompt_value = '123456789'
        prompt_code = 'DTKT'
        hostsim_prompt_text = 'Delivery ticket number'
        hostsim_prompt_mask = 'N;TS;M=1;X=20'
        dispenser_prompt_text = 'Press ENTER/OK when done CANCEL to Cancel Enter Delivery Ticket Number'
        message_prompt_text = '004 - Wex OTR Prompt Data - Prompt: DTKT (Delivery ticket number)'
        self.dispenser_transaction(
            prompt_value=prompt_value,
            prompt_code=prompt_code,
            hostsim_prompt_text=hostsim_prompt_text,
            hostsim_prompt_mask=hostsim_prompt_mask,
            prompt_text=dispenser_prompt_text,
            message_prompt_text=message_prompt_text
            )
    
    @test
    def Outside_FSTI(self): #8
        """
        Outside transactions with NGFC cards with First name initial prompt
        in order to validate it.
        """
        prompt_value = '7'
        prompt_code = 'FSTI'
        hostsim_prompt_text = 'First name initial'
        hostsim_prompt_mask = 'N;TS;M=1;X=1'
        dispenser_prompt_text = 'Press ENTER/OK when done CANCEL to Cancel Enter First Name Initial'
        message_prompt_text = '004 - Wex OTR Prompt Data - Prompt: FSTI (First name initial)'
        self.dispenser_transaction(
            prompt_value=prompt_value,
            prompt_code=prompt_code,
            hostsim_prompt_text=hostsim_prompt_text,
            hostsim_prompt_mask=hostsim_prompt_mask,
            prompt_text=dispenser_prompt_text,
            message_prompt_text=message_prompt_text
            )
    
    @test
    def Outside_HBRD(self): #9
        """
        Outside transactions with NGFC cards with Hubometer prompt
        in order to validate it.
        """
        prompt_value = '20000'
        prompt_code = 'HBRD'
        hostsim_prompt_text = 'Hubometer reading'
        hostsim_prompt_mask = 'N;TS;M=1;X=6'
        dispenser_prompt_text = 'Press ENTER/OK when done CANCEL to Cancel Enter Hubometer Reading'
        message_prompt_text = '004 - Wex OTR Prompt Data - Prompt: HBRD (Hubometer reading)'
        self.dispenser_transaction(
            prompt_value=prompt_value,
            prompt_code=prompt_code,
            hostsim_prompt_text=hostsim_prompt_text,
            hostsim_prompt_mask=hostsim_prompt_mask,
            prompt_text=dispenser_prompt_text,
            message_prompt_text=message_prompt_text
            )
    
    @test
    def Outside_HRRD(self): #10
        """
        Outside transactions with NGFC cards with Reefer hour meter reading prompt
        in order to validate it.
        """
        prompt_value = '183550'
        prompt_code = 'HRRD'
        hostsim_prompt_text = 'Reefer hour meter reading'
        hostsim_prompt_mask = 'N;TS;M=1;X=15'
        dispenser_prompt_text = 'Press ENTER/OK when done CANCEL to Cancel Enter Reefer Hour Meter Reading'
        message_prompt_text = '004 - Wex OTR Prompt Data - Prompt: HRRD (Reefer hour meter reading; 1 implied decimal position)'
        self.dispenser_transaction(
            prompt_value=prompt_value,
            prompt_code=prompt_code,
            hostsim_prompt_text=hostsim_prompt_text,
            hostsim_prompt_mask=hostsim_prompt_mask,
            prompt_text=dispenser_prompt_text,
            message_prompt_text=message_prompt_text
            )
    
    @test
    def Outside_ISNB(self): #11
        """
        Outside transactions with NGFC cards with Issuer number reading prompt
        in order to validate it.
        """
        prompt_value = '2315'
        prompt_code = 'ISNB'
        hostsim_prompt_text = 'Issuer Number'
        hostsim_prompt_mask = 'N;TS;M=1;X=5'
        dispenser_prompt_text = 'Press ENTER/OK when done CANCEL to Cancel Enter Issuer Number'
        message_prompt_text = '004 - Wex OTR Prompt Data - Prompt: ISNB (Issuer Number (check authorizations))'
        self.dispenser_transaction(
            prompt_value=prompt_value,
            prompt_code=prompt_code,
            hostsim_prompt_text=hostsim_prompt_text,
            hostsim_prompt_mask=hostsim_prompt_mask,
            prompt_text=dispenser_prompt_text,
            message_prompt_text=message_prompt_text
            )
    
    @test
    def Outside_LCST(self): #12
        """
        Outside transactions with NGFC cards with License plate state prompt
        in order to validate it.
        """
        prompt_value = '0123456789'
        prompt_code = 'LCST'
        hostsim_prompt_text = 'Vehicle license plate state'
        hostsim_prompt_mask = 'N;TS;M=1;X=15'
        dispenser_prompt_text = 'Press ENTER/OK when done CANCEL to Cancel Enter Vehicle License Plate State'
        message_prompt_text = '004 - Wex OTR Prompt Data - Prompt: LCST (Vehicle license plate state)'
        self.dispenser_transaction(
            prompt_value=prompt_value,
            prompt_code=prompt_code,
            hostsim_prompt_text=hostsim_prompt_text,
            hostsim_prompt_mask=hostsim_prompt_mask,
            prompt_text=dispenser_prompt_text,
            message_prompt_text=message_prompt_text
            )
    
    @test
    def Outside_LICN(self): #13
        """
        Outside transactions with NGFC cards with License plate number prompt
        in order to validate it.
        """
        prompt_value = '12000025'
        prompt_code = 'LICN'
        hostsim_prompt_text = 'Vehicle license plate number'
        hostsim_prompt_mask = 'N;TS;M=1;X=10'
        dispenser_prompt_text = 'Press ENTER/OK when done CANCEL to Cancel Enter Vehicle License Plate Number'
        message_prompt_text = '004 - Wex OTR Prompt Data - Prompt: LICN (Unkwnown)'
        self.dispenser_transaction(
            prompt_value=prompt_value,
            prompt_code=prompt_code,
            hostsim_prompt_text=hostsim_prompt_text,
            hostsim_prompt_mask=hostsim_prompt_mask,
            prompt_text=dispenser_prompt_text,
            message_prompt_text=message_prompt_text
            )
    
    @test
    def Outside_ODRD(self): #14
        """
        Outside transactions with NGFC cards with Odometer reading prompt
        in order to validate it.
        """
        prompt_value = '120000001'
        prompt_code = 'ODRD'
        hostsim_prompt_text = 'Odometer reading'
        hostsim_prompt_mask = 'N;TS;M=1;X=15'
        dispenser_prompt_text = 'Press ENTER/OK when done CANCEL to Cancel Enter Odometer Reading'
        message_prompt_text = '004 - Wex OTR Prompt Data - Prompt: ODRD (Odometer reading)'
        self.dispenser_transaction(
            prompt_value=prompt_value,
            prompt_code=prompt_code,
            hostsim_prompt_text=hostsim_prompt_text,
            hostsim_prompt_mask=hostsim_prompt_mask,
            prompt_text=dispenser_prompt_text,
            message_prompt_text=message_prompt_text
            )
    
    @test
    def Outside_PONB(self): #15
        """
        Outside transactions with NGFC cards with Purchase order number prompt
        in order to validate it.
        """
        prompt_value = '12'
        prompt_code = 'PONB'
        hostsim_prompt_text = 'Purchase order number'
        hostsim_prompt_mask = 'N;TS;M=1;X=5'
        dispenser_prompt_text = 'Press ENTER/OK when done CANCEL to Cancel Enter Purchase Order Number'
        message_prompt_text = '004 - Wex OTR Prompt Data - Prompt: PONB (Purchase order number)'
        self.dispenser_transaction(
            prompt_value=prompt_value,
            prompt_code=prompt_code,
            hostsim_prompt_text=hostsim_prompt_text,
            hostsim_prompt_mask=hostsim_prompt_mask,
            prompt_text=dispenser_prompt_text,
            message_prompt_text=message_prompt_text
            )
    
    @test
    def Outside_PPIN(self): #16
        """
        Outside transactions with NGFC cards with Non-Encrypted PIN prompt
        in order to validate it.
        """
        prompt_value = '4321'
        prompt_code = 'PPIN'
        hostsim_prompt_text = 'Non encrypted PIN'
        hostsim_prompt_mask = 'N;TS;M=1;X=4'
        dispenser_prompt_text = 'Press ENTER/OK when done CANCEL to Cancel Enter Non-Encrypted PIN'
        message_prompt_text = '004 - Wex OTR Prompt Data - Prompt: PPIN (Non-encrypted PIN)'
        self.dispenser_transaction(
            prompt_value=prompt_value,
            prompt_code=prompt_code,
            hostsim_prompt_text=hostsim_prompt_text,
            hostsim_prompt_mask=hostsim_prompt_mask,
            prompt_text=dispenser_prompt_text,
            message_prompt_text=message_prompt_text
            )
    
    @test
    def Outside_RTMP(self): #17
        """
        Outside transactions with NGFC cards with Reefer temperature prompt
        in order to validate it.
        """
        prompt_value = '75'
        prompt_code = 'RTMP'
        hostsim_prompt_text = 'Reefer temperature'
        hostsim_prompt_mask = 'N;TS;M=1;X=3'
        dispenser_prompt_text = 'Press ENTER/OK when done CANCEL to Cancel Enter Reefer Temperature'
        message_prompt_text = '004 - Wex OTR Prompt Data - Prompt: RTMP (Reefer temperature)'
        self.dispenser_transaction(
            prompt_value=prompt_value,
            prompt_code=prompt_code,
            hostsim_prompt_text=hostsim_prompt_text,
            hostsim_prompt_mask=hostsim_prompt_mask,
            prompt_text=dispenser_prompt_text,
            message_prompt_text=message_prompt_text
            )
    
    @test
    def Outside_SSUB(self): #18
        """
        Outside transactions with NGFC cards with Sub fleet number prompt
        in order to validate it.
        """
        prompt_value = '254'
        prompt_code = 'SSUB'
        hostsim_prompt_text = 'Sub fleet number'
        hostsim_prompt_mask = 'N;TS;M=1;X=15'
        dispenser_prompt_text = 'Press ENTER/OK when done CANCEL to Cancel Enter Sub-Fleet Number'
        message_prompt_text = '004 - Wex OTR Prompt Data - Prompt: SSUB (Sub-fleet number)'
        self.dispenser_transaction(
            prompt_value=prompt_value,
            prompt_code=prompt_code,
            hostsim_prompt_text=hostsim_prompt_text,
            hostsim_prompt_mask=hostsim_prompt_mask,
            prompt_text=dispenser_prompt_text,
            message_prompt_text=message_prompt_text
            )
    
    @test
    def Outside_TRIP(self): #19
        """
        Outside transactions with NGFC cards with Trip number prompt
        in order to validate it.
        """
        prompt_value = '25477'
        prompt_code = 'TRIP'
        hostsim_prompt_text = 'Trip number'
        hostsim_prompt_mask = 'N;TS;M=1;X=5'
        dispenser_prompt_text = 'Press ENTER/OK when done CANCEL to Cancel Enter Trip Number'
        message_prompt_text = '004 - Wex OTR Prompt Data - Prompt: TRIP (Trip number)'
        self.dispenser_transaction(
            prompt_value=prompt_value,
            prompt_code=prompt_code,
            hostsim_prompt_text=hostsim_prompt_text,
            hostsim_prompt_mask=hostsim_prompt_mask,
            prompt_text=dispenser_prompt_text,
            message_prompt_text=message_prompt_text
            )
    
    @test
    def Outside_TRLR(self): #20
        """
        Outside transactions with NGFC cards with Trailer number prompt
        in order to validate it.
        """
        prompt_value = '9876543210'
        prompt_code = 'TRLR'
        hostsim_prompt_text = 'Trailar number'
        hostsim_prompt_mask = 'N;TS;M=1;X=10'
        dispenser_prompt_text = 'Press ENTER/OK when done CANCEL to Cancel Enter Trailer Number'
        message_prompt_text = '004 - Wex OTR Prompt Data - Prompt: TRLR (Trailer number)'
        self.dispenser_transaction(
            prompt_value=prompt_value,
            prompt_code=prompt_code,
            hostsim_prompt_text=hostsim_prompt_text,
            hostsim_prompt_mask=hostsim_prompt_mask,
            prompt_text=dispenser_prompt_text,
            message_prompt_text=message_prompt_text
            )
    
    @test
    def Outside_TRNB(self): #21
        """
        Outside transactions with NGFC cards with Transaction number prompt
        in order to validate it.
        """
        prompt_value = '1254411123'
        prompt_code = 'TRNB'
        hostsim_prompt_text = 'Transaction number'
        hostsim_prompt_mask = 'N;TS;M=1;X=15'
        dispenser_prompt_text = 'Press ENTER/OK when done CANCEL to Cancel Enter Transaction Number'
        message_prompt_text = '004 - Wex OTR Prompt Data - Prompt: TRNB (Transaction number (check authorizations))'
        self.dispenser_transaction(
            prompt_value=prompt_value,
            prompt_code=prompt_code,
            hostsim_prompt_text=hostsim_prompt_text,
            hostsim_prompt_mask=hostsim_prompt_mask,
            prompt_text=dispenser_prompt_text,
            message_prompt_text=message_prompt_text
            )
    
    @test
    def Outside_UNIT(self): #22
        """
        Outside transactions with NGFC cards with Unit number prompt
        in order to validate it.
        """
        prompt_value = '1000001'
        prompt_code = 'UNIT'
        hostsim_prompt_text = 'Unit number'
        hostsim_prompt_mask = 'N;TS;M=1;X=7'
        dispenser_prompt_text = 'Press ENTER/OK when done CANCEL to Cancel Enter Unit Number'
        message_prompt_text = '004 - Wex OTR Prompt Data - Prompt: UNIT (Unit number)'
        self.dispenser_transaction(
            prompt_value=prompt_value,
            prompt_code=prompt_code,
            hostsim_prompt_text=hostsim_prompt_text,
            hostsim_prompt_mask=hostsim_prompt_mask,
            prompt_text=dispenser_prompt_text,
            message_prompt_text=message_prompt_text
            )
    
    @test
    def Outside_VEHN(self): #23
        """
        Outside transactions with NGFC cards with Vehicle number prompt
        in order to validate it.
        """
        prompt_value = '254441'
        prompt_code = 'VEHN'
        hostsim_prompt_text = 'Vehicle number'
        hostsim_prompt_mask = 'N;TS;M=1;X=10'
        dispenser_prompt_text = 'Press ENTER/OK when done CANCEL to Cancel Enter Vehicle Number'
        message_prompt_text = '004 - Wex OTR Prompt Data - Prompt: VEHN (Unkwnown)'
        self.dispenser_transaction(
            prompt_value=prompt_value,
            prompt_code=prompt_code,
            hostsim_prompt_text=hostsim_prompt_text,
            hostsim_prompt_mask=hostsim_prompt_mask,
            prompt_text=dispenser_prompt_text,
            message_prompt_text=message_prompt_text
            )
    
    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """

        self.pos.close()
    
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
 
    def dispenser_transaction(self, prompt_value, prompt_code, hostsim_prompt_text, hostsim_prompt_mask, prompt_text, message_prompt_text): #6
        """
        Outside transactions with NGFC cards with driver ID prompt
        in order to validate it.
        """
        #Input constants
        
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts
  
        dispenser_prompts = {
            "Make selection":{
                "entry": [""],
                "buttons": ["Tractor"]
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
            prompt_text:{
                "entry": [prompt_value],
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

        receipt_data = [f"{self.helpers.grade_1_Name} 5.000G",
                        "PRICE/GAL     $1.000",
                        "FUEL TOTAL   $  5.00",
                        "TOTAL = $  5.00",
                        "CREDIT       $  5.00"]

        self.preauth_request_verifications = {
            'Fuel Purchase': '5000',
            '001 - Wex OTR Flags': 'C - Commercial'}

        self.preauth_response_verifications = {
            'Response Code': '2', 
            'Approved Amount': '000005000',
            '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 0.00',
            '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',
            f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_1_Product}': 'Product limit: 50.00',
            f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_2_Product}': 'Product limit: 50.00',
            f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_3_Product}': 'Product limit: 50.00',
            '004 - Wex OTR Prompt Data - Prompt: ' + prompt_code: 'Format: ' + hostsim_prompt_mask}

        self.capture_request_verifications = {
            'Fuel Purchase': '500',
            'Number of Products': '01',
            'Prod 1 product Amount': '500',
            'Prod 1 product Code': f'{self.helpers.grade_1_Product}',
            '001 - Wex OTR Flags': 'C - Commercial',
            f'{message_prompt_text}': 'Response: ' + prompt_value}

        self.capture_response_verifications = {
            'Response Code': '0', 
            'Approved Amount': '000000500'}
        
        self.pos.wait_disp_ready(idle_timeout=120)

        self.log.debug("Disabling all prompt and activating only one")
        networksim.disable_prompts()
        networksim.set_commercial_prompt(True, prompt_code, hostsim_prompt_text, hostsim_prompt_mask)

        self.log.info("Setting the CRIND in manual mode")
        crindsim.set_mode("manual")

        #look for the last message before payment so we know the messages involved in the transaction
        last_msg = self.edh.get_last_msg_id(pspid='23')

        #Iniciate outside trnsaction
        crindsim.swipe_card(card_name=card_to_use_NGFC, brand="EXXON")
        
        #Handle crind prompts
        if not self.helpers.crind_transaction_handler(dispenser_prompts):
            tc_fail("Something failed while processing the transaction in the dispenser")

        self.pos.select_dispenser(1)
        self.pos.wait_for_fuel(1, timeout=120)

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
        
        self.log.debug("General receipt validation")
        self.pos.check_receipt_for(receipt_data, dispenser=1, timeout=10)
        
        self.log.debug("Getting if prompt should be printed or not")
        query = f"Select ReceiptText,'/',PrintOnReceipt from XOM_Prompt where ExtendedPromptCode = '{prompt_code}'"
        output = runas.run_sqlcmd(query, database="network", cmdshell=False)['output']
        # Turning string into list of strings that have \n delimitation
        output_list = output.split("\n")
        output_list = output_list[2:-3]
        # create list with text and printing flag
        if len(output_list) == 1:
            keyValue = output_list[0].split("/")
            keyValue[0] = keyValue[0].strip()
            keyValue[1] = keyValue[1].strip()
            print_on_receipt = True if keyValue[1].replace(" ", "") == '1' else False
            self.log.debug(f"print on receipt value is: {print_on_receipt}")
        else:
            tc_fail(f"Print on receipt value, could not be retrieved for prompt code {prompt_code}.")

        self.log.debug("Prompt printing validation")
        self.pos.click_function_key("Receipt", 5, verify=False)
        self.pos.select_receipt(1, verify=False)
        receipt_list = self.pos.read_receipt()
        if print_on_receipt:
            self.log.debug(f"Validating that the prompt {prompt_code} should be printed")
            line = keyValue[0] + ": " + prompt_value
            if not line in receipt_list:
                tc_fail(f'The line "{line}" was not found on the receipt printed inside and it is not expected.')
            else:
                self.log.debug(f"The line '{line}', was printed on receipt.")
        else:
            self.log.debug(f"Validating that the prompt {prompt_code} should not be printed")
            line = keyValue[0] + ": " + prompt_value
            if line in receipt_list:
                tc_fail(f'The line "{line}" was found on the receipt printed inside and it is not expected.')
            else:
                self.log.debug(f"The line '{line}', was not printed on receipt as expected.")
    
        self.pos.click_function_key("Back")