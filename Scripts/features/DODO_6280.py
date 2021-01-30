"""
    File name: DODO_6280.py
    Tags:
    Description: Test scripts meant to verify correct prossesing of dynamic prompts inside
    and correct printing on receipts.
    Author: Javier Sandoval
    Date created: 2020-06-22 14:00:00
    Date last modified: 2020-04-26 17:00:00
    Python Version: 3.7
"""

import logging
from app import Navi, mws, pos, system, forecourt_installation, networksim, crindsim, runas, network_site_config
from app.framework import EDH
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app.features import feature_activation
from Scripts.features import NGFC_Helpers
import time

class DODO_6280():
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

        self.helpers = NGFC_Helpers.NGFC_Helpers(self.log, self.mws)

        # The main crind sim object
        self.crindsim = crindsim

        # Customer information values
        self.customerInfo = ["AB TRUCKING", "DENVER", "CO", "234W987"]

    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        """

        # cash advance to 0
        self.set_cash_advance_on_mws('000')

        # HostSim Response mode
        networksim.set_response_mode("Approval")
                
        # Disable all promtps
        networksim.disable_commercial_fuel_limits()
        networksim.disable_product_limits()

        # Set specif config for this script
        networksim.set_commercial_customer_information(self.customerInfo[0], self.customerInfo[1], self.customerInfo[2], self.customerInfo[3])
        networksim.set_commercial_product_limit("True","CADV","Company funds cash advance",20.00)
        networksim.set_commercial_product_limit("True", "MERC", "Default category for merchandise", 30.00)        
        networksim.set_commercial_fuel_limit("True", "019", 50.00)
        networksim.set_commercial_fuel_limit("True", "020", 50.00)
        networksim.set_commercial_fuel_limit("True", "021", 50.00)
        networksim.set_commercial_fuel_limit_send_mode("fuel product configuration based",110,True)

        crindsim.set_mode("auto")
        crindsim.set_sales_target()

        #open Browser
        self.pos.connect()
        self.pos.sign_on()
    
    @test
    def Prepay_BDAY(self): #1
        """
        Prepay transactions with NGFC cards with Birthday prompt
        in order to validate it.
        """

        prompt_value = '110287'
        prompt_code = 'BDAY'
        hostsim_prompt_text = 'Birthday information'
        hostsim_prompt_mask = 'A;TS;M=1;X=25' 
        pos_prompt_text = 'ENTER BIRTHDAY IN MMDDYY FORMAT'
        message_prompt_text = 'BDAY (Birthday information in MMDDYY format)'
        self.Prepay_Prompt(prompt_value, prompt_code, hostsim_prompt_text, hostsim_prompt_mask, pos_prompt_text, message_prompt_text)

    @test
    def Prepay_BLID(self): #2
        """
        Prepay transactions with NGFC cards with Billing ID prompt
        in order to validate it.
        """

        prompt_value = '100002'
        prompt_code = 'BLID'
        hostsim_prompt_text = 'Billing ID'
        hostsim_prompt_mask = 'N;TS;M=1;X=25'
        pos_prompt_text = 'ENTER BILLING ID'
        message_prompt_text = 'BLID (Billing ID)'
        self.Prepay_Prompt(prompt_value, prompt_code, hostsim_prompt_text, hostsim_prompt_mask, pos_prompt_text, message_prompt_text)

    @test
    def Prepay_CNTN(self): #3
        """
        Prepay transactions with NGFC cards with Control number prompt
        in order to validate it.
        """

        prompt_value = '245777'
        prompt_code = 'CNTN'
        hostsim_prompt_text = 'Control number'
        hostsim_prompt_mask = 'N;TS;M=1;X=25'
        pos_prompt_text = 'ENTER CONTROL NUMBER'
        message_prompt_text = 'CNTN (Control number)'
        self.Prepay_Prompt(prompt_value, prompt_code, hostsim_prompt_text, hostsim_prompt_mask, pos_prompt_text, message_prompt_text)
    
    @test
    def Prepay_DLIC(self): #4
        """
        Prepay transactions with NGFC cards with Drivers license number prompt
        in order to validate it.
        """

        prompt_value = '1254abc'
        prompt_code = 'DLIC'
        hostsim_prompt_text = 'Drivers license number'
        hostsim_prompt_mask = 'A;TS;M=1;X=25'
        pos_prompt_text = "ENTER DRIVER'S LICENSE NUMBER"
        message_prompt_text = 'DLIC (Driver’s license number)'
        self.Prepay_Prompt(prompt_value, prompt_code, hostsim_prompt_text, hostsim_prompt_mask, pos_prompt_text, message_prompt_text)

    @test
    def Prepay_DLST(self): #5
        """
        Prepay transactions with NGFC cards with Drivers license number prompt
        in order to validate it.
        """

        prompt_value = 'State'
        prompt_code = 'DLST'
        hostsim_prompt_text = 'Drivers license state'
        hostsim_prompt_mask = 'A;TS;M=1;X=25'
        pos_prompt_text = "ENTER DRIVER'S LICENSE STATE"
        message_prompt_text = 'DLST (Driver’s license state)'
        self.Prepay_Prompt(prompt_value, prompt_code, hostsim_prompt_text, hostsim_prompt_mask, pos_prompt_text, message_prompt_text)

    @test
    def Prepay_DRID(self): #6
        """
        Prepay transactions with NGFC cards with Driver ID prompt
        in order to validate it.
        """
        prompt_value = '321456'
        prompt_code = 'DRID'
        hostsim_prompt_text = 'Driver ID'
        hostsim_prompt_mask = 'N;TS;M=1;X=10' 
        pos_prompt_text = 'ENTER DRIVER ID'
        message_prompt_text = 'DRID (Driver ID)'
        self.Prepay_Prompt(prompt_value, prompt_code, hostsim_prompt_text, hostsim_prompt_mask, pos_prompt_text, message_prompt_text)

    @test
    def Prepay_DTKT(self): #7
        """
        Prepay transactions with NGFC cards with Delivery ticket number prompt
        in order to validate it.
        """
        prompt_value = '123456789'
        prompt_code = 'DTKT'
        hostsim_prompt_text = 'Delivery ticket number'
        hostsim_prompt_mask = 'N;TS;M=1;X=20'
        pos_prompt_text = 'ENTER DELIVERY TICKET NUMBER'
        message_prompt_text = 'DTKT (Delivery ticket number)'
        self.Prepay_Prompt(prompt_value, prompt_code, hostsim_prompt_text, hostsim_prompt_mask, pos_prompt_text, message_prompt_text)

    @test
    def Prepay_FSTI(self): #8
        """
        Prepay transactions with NGFC cards with First name initial prompt
        in order to validate it.
        """
        prompt_value = 'J'
        prompt_code = 'FSTI'
        hostsim_prompt_text = 'First name initial'
        hostsim_prompt_mask = 'A;TS;M=1;X=1'
        pos_prompt_text = 'ENTER FIRST NAME INITIAL'
        message_prompt_text = 'FSTI (First name initial)'
        self.Prepay_Prompt(prompt_value, prompt_code, hostsim_prompt_text, hostsim_prompt_mask, pos_prompt_text, message_prompt_text)

    @test
    def Prepay_HBRD(self): #9
        """
        Prepay transactions with NGFC cards with Hubometer prompt
        in order to validate it.
        """
        prompt_value = '20000'
        prompt_code = 'HBRD'
        hostsim_prompt_text = 'Hubometer reading'
        hostsim_prompt_mask = 'N;TS;M=1;X=6'
        pos_prompt_text = 'ENTER HUBOMETER READING'
        message_prompt_text = 'HBRD (Hubometer reading)'
        self.Prepay_Prompt(prompt_value, prompt_code, hostsim_prompt_text, hostsim_prompt_mask, pos_prompt_text, message_prompt_text)
    
    @test
    def Prepay_HRRD(self): #10
        """
        Prepay transactions with NGFC cards with Reefer hour meter reading prompt
        in order to validate it.
        """
        prompt_value = '183550'
        prompt_code = 'HRRD'
        hostsim_prompt_text = 'Reefer hour meter reading'
        hostsim_prompt_mask = 'N;TS;M=1;X=15'
        pos_prompt_text = 'ENTER REEFERHOUR METER READING'
        message_prompt_text = 'HRRD (Reefer hour meter reading; 1 implied decimal position)'
        self.Prepay_Prompt(prompt_value, prompt_code, hostsim_prompt_text, hostsim_prompt_mask, pos_prompt_text, message_prompt_text)
    
    @test
    def Prepay_ISNB(self): #11
        """
        Prepay transactions with NGFC cards with Issuer number reading prompt
        in order to validate it.
        """
        prompt_value = '2315'
        prompt_code = 'ISNB'
        hostsim_prompt_text = 'Issuer Number'
        hostsim_prompt_mask = 'N;TS;M=1;X=5'
        pos_prompt_text = 'ENTER ISSUER NUMBER'
        message_prompt_text = 'ISNB (Issuer Number (check authorizations))'
        self.Prepay_Prompt(prompt_value, prompt_code, hostsim_prompt_text, hostsim_prompt_mask, pos_prompt_text, message_prompt_text)
    
    @test
    def Prepay_LCST(self): #12
        """
        Prepay transactions with NGFC cards with License plate state prompt
        in order to validate it.
        """
        prompt_value = 'Melbourne'
        prompt_code = 'LCST'
        hostsim_prompt_text = 'Vehicle license plate state'
        hostsim_prompt_mask = 'A;TS;M=1;X=15'
        pos_prompt_text = 'ENTER LICENSE PLATE STATE'
        message_prompt_text = 'LCST (Vehicle license plate state)'
        self.Prepay_Prompt(prompt_value, prompt_code, hostsim_prompt_text, hostsim_prompt_mask, pos_prompt_text, message_prompt_text)
    
    @test
    def Prepay_LICN(self): #13
        """
        Prepay transactions with NGFC cards with License plate number prompt
        in order to validate it.
        """
        prompt_value = '12000025'
        prompt_code = 'LICN'
        hostsim_prompt_text = 'Vehicle license plate number'
        hostsim_prompt_mask = 'N;TS;M=1;X=10'
        pos_prompt_text = 'ENTER LICENSE PLATE NUMBER'
        message_prompt_text = 'LICN (Unkwnown)'
        self.Prepay_Prompt(prompt_value, prompt_code, hostsim_prompt_text, hostsim_prompt_mask, pos_prompt_text, message_prompt_text)
    
    @test
    def Prepay_ODRD(self): #14
        """
        Prepay transactions with NGFC cards with Odometer reading prompt
        in order to validate it.
        """
        prompt_value = '120000001'
        prompt_code = 'ODRD'
        hostsim_prompt_text = 'Odometer reading'
        hostsim_prompt_mask = 'N;TS;M=1;X=15'
        pos_prompt_text = 'ENTER ODOMETER READING'
        message_prompt_text = 'ODRD (Odometer reading)'
        self.Prepay_Prompt(prompt_value, prompt_code, hostsim_prompt_text, hostsim_prompt_mask, pos_prompt_text, message_prompt_text)
    
    @test
    def Prepay_PONB(self): #15
        """
        Prepay transactions with NGFC cards with Purchase order number prompt
        in order to validate it.
        """
        prompt_value = '12'
        prompt_code = 'PONB'
        hostsim_prompt_text = 'Purchase order number'
        hostsim_prompt_mask = 'N;TS;M=1;X=5'
        pos_prompt_text = 'ENTER PURCHASE ORDER NUMBER'
        message_prompt_text = 'PONB (Purchase order number)'
        self.Prepay_Prompt(prompt_value, prompt_code, hostsim_prompt_text, hostsim_prompt_mask, pos_prompt_text, message_prompt_text)
    
    @test
    def Prepay_PPIN(self): #16
        """
        Prepay transactions with NGFC cards with Non-Encrypted PIN prompt
        in order to validate it.
        """
        prompt_value = '4321'
        prompt_code = 'PPIN'
        hostsim_prompt_text = 'Non encrypted PIN'
        hostsim_prompt_mask = 'N;TS;M=1;X=4'
        pos_prompt_text = 'ENTER NON- ENCRYPTED PIN'
        message_prompt_text = 'PPIN (Non-encrypted PIN)'
        self.Prepay_Prompt(prompt_value, prompt_code, hostsim_prompt_text, hostsim_prompt_mask, pos_prompt_text, message_prompt_text)
    
    @test
    def Prepay_RTMP(self): #17
        """
        Prepay transactions with NGFC cards with Reefer temperature prompt
        in order to validate it.
        """
        prompt_value = '75'
        prompt_code = 'RTMP'
        hostsim_prompt_text = 'Reefer temperature'
        hostsim_prompt_mask = 'N;TS;M=1;X=3'
        pos_prompt_text = 'ENTER REEFER TEMPERATURE'
        message_prompt_text = 'RTMP (Reefer temperature)'
        self.Prepay_Prompt(prompt_value, prompt_code, hostsim_prompt_text, hostsim_prompt_mask, pos_prompt_text, message_prompt_text)
    
    @test
    def Prepay_SSUB(self): #18
        """
        Prepay transactions with NGFC cards with Sub fleet number prompt
        in order to validate it.
        """
        prompt_value = '254hj'
        prompt_code = 'SSUB'
        hostsim_prompt_text = 'Sub fleet number'
        hostsim_prompt_mask = 'A;TS;M=1;X=15'
        pos_prompt_text = 'ENTER SUB FLEET NUMBER'
        message_prompt_text = 'SSUB (Sub-fleet number)'
        self.Prepay_Prompt(prompt_value, prompt_code, hostsim_prompt_text, hostsim_prompt_mask, pos_prompt_text, message_prompt_text)
    
    @test
    def Prepay_TRIP(self): #19
        """
        Prepay transactions with NGFC cards with Trip number prompt
        in order to validate it.
        """
        prompt_value = '25477'
        prompt_code = 'TRIP'
        hostsim_prompt_text = 'Trip number'
        hostsim_prompt_mask = 'N;TS;M=1;X=5'
        pos_prompt_text = 'ENTER TRIP NUMBER'
        message_prompt_text = 'TRIP (Trip number)'
        self.Prepay_Prompt(prompt_value, prompt_code, hostsim_prompt_text, hostsim_prompt_mask, pos_prompt_text, message_prompt_text)
    
    @test
    def Prepay_TRLR(self): #20
        """
        Prepay transactions with NGFC cards with Trailer number prompt
        in order to validate it.
        """
        prompt_value = '254sd'
        prompt_code = 'TRLR'
        hostsim_prompt_text = 'Trailar number'
        hostsim_prompt_mask = 'A;TS;M=1;X=10'
        pos_prompt_text = 'ENTER TRAILER NUMBER'
        message_prompt_text = 'TRLR (Trailer number)'
        self.Prepay_Prompt(prompt_value, prompt_code, hostsim_prompt_text, hostsim_prompt_mask, pos_prompt_text, message_prompt_text)
    
    @test
    def Prepay_TRNB(self): #21
        """
        Prepay transactions with NGFC cards with Transaction number prompt
        in order to validate it.
        """
        prompt_value = '1254411123'
        prompt_code = 'TRNB'
        hostsim_prompt_text = 'Transaction number'
        hostsim_prompt_mask = 'N;TS;M=1;X=15'
        pos_prompt_text = 'ENTERTRANSACTION NUMBER'
        message_prompt_text = 'TRNB (Transaction number (check authorizations))'
        self.Prepay_Prompt(prompt_value, prompt_code, hostsim_prompt_text, hostsim_prompt_mask, pos_prompt_text, message_prompt_text)
    
    @test
    def Prepay_UNIT(self): #22
        """
        Prepay transactions with NGFC cards with Unit number prompt
        in order to validate it.
        """
        prompt_value = '1000001'
        prompt_code = 'UNIT'
        hostsim_prompt_text = 'Unit number'
        hostsim_prompt_mask = 'N;TS;M=1;X=7'
        pos_prompt_text = 'ENTER UNIT NUMBER'
        message_prompt_text = 'UNIT (Unit number)'
        self.Prepay_Prompt(prompt_value, prompt_code, hostsim_prompt_text, hostsim_prompt_mask, pos_prompt_text, message_prompt_text)
    
    @test
    def Prepay_VEHN(self): #23
        """
        Prepay transactions with NGFC cards with Vehicle number prompt
        in order to validate it.
        """
        prompt_value = '254441'
        prompt_code = 'VEHN'
        hostsim_prompt_text = 'Vehicle number'
        hostsim_prompt_mask = 'A;TS;M=1;X=10'
        pos_prompt_text = 'ENTER VEHICLE NUMBER'
        message_prompt_text = 'VEHN (Unkwnown)'
        self.Prepay_Prompt(prompt_value, prompt_code, hostsim_prompt_text, hostsim_prompt_mask, pos_prompt_text, message_prompt_text)
    
    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """

        self.pos.close()

    def set_commercial_on_forecourt(self):
        """
        Set the dispenser as commercial Diesel
        """
        fc_config = {
            "Dispensers" : {
                "Commercial Diesel": True #Transponder is now Commercial Check
            }
        }
        
        FC = forecourt_installation.ForecourtInstallation()
        mws.click("Set Up")

        # Set Commercial Diesel feature to the crind Configured as "Gilbarco"
        FC.change("Gilbarco", "Dispensers", fc_config.get("Dispensers"))

        mws.click_toolbar("Save")
        mws.click_toolbar("Save")
    
    def wait_for_new_msg(self, last_msg, psp_id, timeout=30):
        
        start = time.time()

        #check it a new message happened since the the last check
        while (last_msg == self.edh.get_last_msg_id(pspid=psp_id)) and (time.time() - start < timeout):
            
            self.log.debug("No new messages found")
            time.sleep(1) #seconds
        
        return last_msg 
    
    def crind_prompts_handler(self, prompts):
        '''
        Handle the prompts used performed by the dispenser
        NOTE: The prompt in the dictionary IS CASE SENSITIVE
        Args:
            prompts (dictionary)
        Returns:
            bool: True if success, False if fail
        Examples:
            >>> prompts = {
                    "Want receipt?": {
                        "buttons": ["Ok"]
                    },
                    "Zip Code": {
                        "entry": ["","12], #This allow us to have answer differently to the same prompt in the same transaction
                        "buttons": ["Ok", "Ok"] # This will hit enter both times
                    }
            }
            True
        '''
        stop_messages = ["Cashier has receipt Thank you",
                         "INSERT CARD To Pay Here or LIFT HANDLE To Pay Inside",
                         #"Authorizing...",
                         'Take receipt Thank you',
                         #"Replace nozzle when finished",
                         "Please, go inside to \nget the cash/buy products.",
                         #"Lift handle to begin fueling",
                         "Thank you for choosing"]

        self.log.info(f"Starting prompts handler the provide prompts are: {prompts} ")

        display_text = crindsim.get_display_text()

        self.log.info(f"Crind display = {display_text}")

        #Waiting that the dispenser starts the transaction
        while display_text in stop_messages:
            display_text = crindsim.get_display_text()
            time.sleep(2)
            self.log.info(f"The dispenser is still showing {display_text}")

        #We loop until we do not get on of the stopping messages
        while display_text not in stop_messages:
            self.log.info(f"Attempting to handle prompt: {display_text}")

            while display_text == "Please wait..." or display_text == "Authorizing...":
                display_text = crindsim.get_display_text()
                self.log.info(f"Crind is showng {display_text}, waiting 1 second to re-try")
                time.sleep(1)
            
            try:
                entry = prompts[display_text]['entry'].pop(0)
                for value in list(entry):
                    self.log.info(f"About to hit on keypad {value}")
                    crindsim.press_keypad(value)
                    time.sleep(1)
                
            except KeyError as e:
                if e not in stop_messages:
                    self.log.error(f"The dispenser is prompting for {display_text} and it is not expected")
                    self.log.warning(e)
                    return False
            except IndexError as e:
                self.log.warning(f"No entry provided for prompt {display_text}, probably the prompt does not need entries, please check")
                self.log.warning(e)

            try:
                button = prompts[display_text]['buttons'].pop(0) #remove the first in the list so next time we pick the following one
                if entry:    
                    self.log.info(f"About to hit keypad {button}")
                    crindsim.press_keypad(button)
                    time.sleep(1)
                else:
                    self.log.info(f"About to hit softkey {button}")
                    crindsim.press_softkey(button)
                    time.sleep(1)

            except KeyError as e:
                self.log.error(f"The terminal is prompting for {display_text} and it is not expected")
                self.log.error(e)
                return False
            except IndexError as e:
                self.log.error(f"No buttons were provide for prompt: {display_text}, please check if your prompts appears more than once")
                self.log.error(e)
                return False

            last_display_text = display_text
            display_text = crindsim.get_display_text()
            self.log.info(f"Crind display = {display_text}")
            # Lifting handle to begin fuieling if applies
            if display_text == "Lift handle to begin fueling":
                self.log.info(f"Lifting handle")
                crindsim.lift_handle()
                time.sleep(2)
                last_display_text = display_text
            display_text = crindsim.get_display_text()
            # lower handle to begin fuieling
            if display_text == "Replace nozzle when finished":
                self.log.info(f"Replacing nozzle")
                crindsim.lower_handle()
                time.sleep(2)
                last_display_text = display_text
                display_text = crindsim.get_display_text()
            start_time = time.time()
            while last_display_text == display_text and time.time() - start_time <= 60:
                display_text = crindsim.get_display_text()
                self.log.info(f"Crind display was not updated yet, it is {display_text}")
                time.sleep(1)
            if last_display_text == display_text:
                tc_fail(f"Crind display was not updated during 1 minute, it keeps in {display_text}", exit=True)
                return False
        return True
    
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
 
    def Prepay_Prompt(self, prompt_value, prompt_code, hostsim_prompt_text, hostsim_prompt_mask, pos_prompt_text, message_prompt_text): #6
        """
        Prepay transactions with NGFC cards with driver ID prompt
        in order to validate it.
        """
        #Input constants

        tractor_fuel_type = 'Tractor fuel' # this is tractor fuel,  because is the objective of this testcase
        def_type_no = 'No' # this is "no",  because is the objective of this testcase
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts
        generic_trans_amount = "$5.00"
        default_dispenser = '1' # we need just one dispenser in this test case
        if hostsim_prompt_mask[0] == 'N':
            button = 'Enter'
        else:
            button = 'Ok'
        commercial_prompts = {              
                    pos_prompt_text: {
                        "entry": [prompt_value],
                        "buttons": [button]
                    },
                    "Additional Products Y/N?": {                    
                        "buttons": ["No"]
                    }
                }
        
        #Output verifications

        receipt_data = [f"{self.helpers.grade_1_Name} CA   PUMP# 1",
                        "5.000 GAL @ $1.000/GAL         $5.00  99",
                        "Subtotal =   $5.00",
                        "Tax  =    $0.00",
                        "Total =   $5.00",
                        "Credit                          $5.00"]

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
            '004 - Wex OTR Prompt Data - Prompt: ' + prompt_code: 'Format: ' + hostsim_prompt_mask}

        self.capture_request_verifications = {
            'Fuel Purchase': '500',
            'Number of Products': '01',
            'Prod 1 product Amount': '500',
            'Prod 1 product Code': f'{self.helpers.grade_1_Product}',
            '001 - Wex OTR Flags': 'C - Commercial',
            '004 - Wex OTR Prompt Data - Prompt: ' + message_prompt_text: 'Response: ' + prompt_value}

        self.capture_response_verifications = {
            'Response Code': '0', 
            'Approved Amount': '000000500'}
        
        networksim.disable_prompts()

        networksim.set_commercial_prompt(True, prompt_code, hostsim_prompt_text, hostsim_prompt_mask)

        self.log.debug("Trying to set crind to dispense automatically")
        if not crindsim.select_grade():
                self.log.error(f"Select grade to 1 failed")
                return False
        if not crindsim.set_mode("auto"):
            self.log.error(f"Set mode to auto failed")
            return False
        if not crindsim.set_sales_target("auth"):
            self.log.error(f"Set sales target to auth failed")
            return False

        self.log.debug("look for the last message before start, so then messages involved in the transaction will be known.")
        last_msg = self.edh.get_last_msg_id(pspid='23')

        self.log.debug("Selecting dispenser and starting a prepay transaction")
        self.pos.select_dispenser(default_dispenser)
        time.sleep(2)
        self.pos.add_fuel(generic_trans_amount,fuel_type = tractor_fuel_type, def_type = def_type_no)

        self.log.debug("Paying prepay")
        time.sleep(2)
        self.pos.pay_card(brand="Exxon", card_name = card_to_use_NGFC, prompts=commercial_prompts)

        self.log.debug("Wait for fueling ends.")
        self.pos.select_dispenser(default_dispenser)
        self.pos.wait_for_fuel(timeout=120)

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
        self.log.debug("General receipt validation")
        self.pos.check_receipt_for(receipt_data, timeout=10)
        ############################
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
        self.pos.click_function_key("Receipt Search", 5, verify=False)
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
    