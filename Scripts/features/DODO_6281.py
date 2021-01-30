"""
    File name: DODO_6281.py
    Tags:
    Description: Update the store procedure to support the destination field for the dynamic prompts
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

class DODO_6281():
    """
    Description: As Passport, I need that the store procedure that is checked 
    for the available destination fields where the prompts data is sent in 
    the messages to the host is updated in order to properly support the new 
    dynamic prompts needed for the NGFC cards in commercial and retail transactions.
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

        #contants
        self.default_dispenser = 1

        self.helpers = NGFC_Helpers.NGFC_Helpers(self.log, self.mws, self.pos)

    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        """

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
        networksim.set_commercial_fuel_limit("True", "001", 50.00)
        networksim.set_commercial_fuel_limit("True", "002", 50.00)
        networksim.set_commercial_fuel_limit("True", "003", 50.00)
        networksim.set_commercial_fuel_limit_send_mode("fuel product configuration based",110,True)

        crindsim.set_sales_target()

        #open Browser
        self.pos.connect()
        self.pos.sign_on()
    
    @test
    def Prepay_NGFC_Prompts(self):
        """
        To validate that Passport makes new dynamic prompts requests to the client
        and validate them according to the rules received from the host correctly
        when using NGFC cards in prepay transactions.
        """
        # Setting the prompt that we need for this test case
        networksim.set_commercial_prompt(True, 'BDAY', 'Birthday information', 'N;TN;M1;X8')
        
        #Setting constant value

        generic_trans_amount = "$50.00" # any value that gets an approval from the host
        card_to_use = 'NGFC'
        refund_amount = "45.00"
        prompt_birthday = "2"

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
                "buttons": ["No"]
            },
            "ENTER BIRTHDAY IN MMDDYY FORMAT": {
                "entry": [prompt_birthday],
                "buttons": ["Enter"] # This allow us to have answer differently to the same prompt in the same transaction
            }
        }

        messages_to_verify= {
            'preauth_request_verifications': {
                'Fuel Purchase': '5000', 
                'Number of Products': '05', #amount of fuel products configured at site.
                'Prod 1 product Code': {'present': True, 'value': self.helpers.grade_1_Product},
                'Prod 2 product Code': {'present': True, 'value': self.helpers.grade_2_Product},
                'Prod 3 product Code': {'present': True, 'value': self.helpers.grade_1_Product_reefer},
                'Prod 4 product Code': {'present': True, 'value': self.helpers.grade_2_Product_reefer},
                'Prod 5 product Code': {'present': True, 'value': self.helpers.grade_3_Product},
                '001 - Wex OTR Flags': 'C - Commercial'
            },
            'preauth_response_verifications': {
                'Response Code': '2', 
                'Approved Amount': '000005000',
                '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 0.00',
                '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',                            
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_1_Product }': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_2_Product }': 'Product limit: 50.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_3_Product }': 'Product limit: 50.00',
                '005 - Wex OTR Customer Information': 'AB TRUCKING              DENVER         CO234W987'
            },
            'capture_request_verifications': {
                'Number of Products': '01',
                'Prod 1 product Amount': '500',
                'Prod 1 product Code': {'present': True, 'value': self.helpers.grade_1_Product},
                '001 - Wex OTR Flags': 'C - Commercial',
                '004 - Wex OTR Prompt Data - Prompt: BDAY (Birthday information in MMDDYY format)': 'Response: ' + prompt_birthday
            },
            'capture_response_verifications': {
                'Response Code': '0', 
                'Approved Amount': '000000500',
                '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 20.00',
                '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',
                f'003 - Wex OTR Fuel Product Limits - Product Code: {self.helpers.grade_1_Product }': 'Product limit: 50.00',
                '005 - Wex OTR Customer Information': 'AB TRUCKING              DENVER         CO234W987'}
        }

        receipt_data = [f"{self.helpers.grade_1_Name} CA   PUMP# 1",
                        "5.000 GAL @ $1.000/GAL         $5.00  99",
                        "Subtotal =   $5.00",
                        "Tax  =    $0.00",
                        "Total =   $5.00",
                        "Change Due  =    $0.00",
                        "Credit                          $50.00",
                        "Customer Information",
                        "Name: " + self.customerInfo[0],
                        "City: " + self.customerInfo[1],
                        "State: " + self.customerInfo[2],
                        "Acc.: " + self.customerInfo[3],                        
                        "Refund Credit $-" + refund_amount]
        
        self.helpers.prepay_transaction(
            card=card_to_use,
            prepay_amount=generic_trans_amount,
            prompts=prompts,
            amounts_to_dispense=amounts_to_dispense,
            messages_to_verify=messages_to_verify,
            receipt_data=receipt_data,
            underrun=True
            )
        
        networksim.set_commercial_prompt(False, 'BDAY', 'Birthday information', '')
    
    @test
    def Outside_NGFC_Prompts(self):
        #Input constants
        card_to_use = 'NGFC' # using this card to get all commercial prompts        
        customer_information = self.customerInfo[0] + (' ' * 14) + self.customerInfo[1] +(' ' * 9) + self.customerInfo[2] + self.customerInfo[3]
        prompt_birthday = "2"

        # Setting the prompt that we need for this test case
        networksim.set_commercial_prompt(True, 'BDAY', 'Birthday information', 'N;TN;M1;X8')

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
            "Want receipt?":{
                "entry": [""],
                "buttons": ["Yes"]
            },
            "Press ENTER/OK when done CANCEL to Cancel Enter Birthday information in MMDDYY format":{
                "entry": [prompt_birthday],
                "buttons": ["Enter"]
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
                'Number of Products': '05', #amount of fuel products configured at site.
                'Prod 1 product Code': f'{self.helpers.grade_1_Product}', #first fuel product configured
                'Prod 2 product Code': f'{self.helpers.grade_2_Product}', #second fuel product configured
                'Prod 3 product Code': f'{self.helpers.grade_1_Product_reefer}', #first alternate fuel product configured
                'Prod 4 product Code': f'{self.helpers.grade_2_Product_reefer}', #second alternate fuel product configured
                'Prod 5 product Code': f'{self.helpers.grade_3_Product}', #third fuel product configured
                '001 - Wex OTR Flags': 'C - Commercial',
                '008 - Wex OTR Cash Advance Limit': '$0.00'
            },
            'preauth_response_verifications': {
                'Response Code': '2', 
                'Approved Amount': '000005000',
                '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 0.00',
                '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',
                '005 - Wex OTR Customer Information': customer_information
            },
            'capture_request_verifications': {
                'Fuel Purchase': '500',
                'Number of Products': '01',
                'Prod 1 product Amount': '500',
                f'Prod 1 product Code': f'{self.helpers.grade_1_Product}',
                '001 - Wex OTR Flags': 'C - Commercial',
                '004 - Wex OTR Prompt Data - Prompt: BDAY (Birthday information in MMDDYY format)': 'Response: ' + prompt_birthday
            },
            'capture_response_verifications': {
                'Response Code': '0', 
                'Approved Amount': '000000500',
                '005 - Wex OTR Customer Information': customer_information
            }
        }

        receipt_data = [f"{self.helpers.grade_1_Name}          5.000G",
                        "PRICE/GAL     $1.000",
                        "FUEL TOTAL   $  5.00",
                        "TOTAL = $  5.00",
                        "CREDIT       $  5.00",
                        "Customer Information",
                        "Name: " + self.customerInfo[0],
                        "City: " + self.customerInfo[1],
                        "State: " + self.customerInfo[2],
                        "Acc.: " + self.customerInfo[3]]                        
        

        self.helpers.dispenser_transaction(
            card=card_to_use,
            prompts=dispenser_prompts, 
            amounts_to_dispense=amounts_to_dispense,
            messages_to_verify=messages_to_verify,
            receipt_data=receipt_data, 
            inside_receipt="Yes"    
        )

        networksim.set_commercial_prompt(False, 'BDAY', 'Birthday information', '')

        # verify outside receipt
        receipt = crindsim.get_receipt()

        if receipt:
            receipt_list = receipt.split("\n")
            for i in range(len(receipt_data)):
                receipt_data[i] = receipt_data[i].replace(" ","")
            for i in range(len(receipt_list)):
                receipt_list[i] = receipt_list[i].replace(" ","")

            for value in receipt_data:
                if not value in receipt_list:
                    # waiting for NDvR merging multidispensing features
                    # those include receipt for multidispensing outside.
                    tc_fail(f'The line "{value}" was not found on the receipt printed outside')
        else:
            tc_fail(f'No receipt was printed outside')

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

    def fuel_handler(self, amounts_to_dispense):
        self.log.info(f"Attempting to fuel manually: {amounts_to_dispense}")
        # Using a list to add latter more ways to start
        start_fueling = "Lift handle"
        
        crindsim.set_mode("manual")
        current_grade = 1       

        for amount in amounts_to_dispense:
            crindsim.set_sales_target("money", amount)
            start_time = time.time()
            display_text = crindsim.get_display_text()
            
            while not start_fueling in display_text and time.time() - start_time < 60:
                self.log.info(f"The Dispenser is showing: {display_text}, waiting 2 seconds before retry")
                time.sleep(1)
                display_text = crindsim.get_display_text()

            if not start_fueling in display_text :
                self.log.error(f"The Dispenser is showing: {display_text} after waiting 60 seconds for an update")
                return False
            else:
                
                change_grade = crindsim.select_grade(grade=current_grade)
                self.log.info(f"The grade was changed to {current_grade}, change grade result: {change_grade}")
                time.sleep(2)
                crindsim.lift_handle()
                crindsim.open_nozzle()                
                time.sleep(2)
                crindsim.close_nozzle()
                crindsim.lower_handle()
                self.log.info(f"Fuel {amount} in grade {current_grade} completed")
                current_grade = current_grade + 1
                time.sleep(5)
            
        crindsim.set_mode("auto")
        crindsim.set_sales_target()        
        crindsim.select_grade(1)

        return True

    def crind_transaction_handler(self, prompts, amounts_to_dispense=[5], decline_scenario=False ):
        """
        Handle the prompts used performed by the dispenser, it includes
        multidispensing handling.
        NOTE: The prompt in the dictionary IS CASE SENSITIVE
        Args:
            prompts (dictionary)
            amount_to_calculate (str) base amount to calculate amounts to dispense on each grade
            amounts_to_dispense (list) different amounts to be dispensed
            decline_scenario (bool) used to test decline scenarios, this 
                prevents the test case fail if the sale is declined by the host
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
        """
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
            if "Please see cashier" in display_text:
                if decline_scenario:
                    return True

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

            if "lift handle" in display_text.lower():
                self.log.info("Dispenser ready fo fueling")
                if not self.fuel_handler(amounts_to_dispense):
                    tc_fail("Something failed while fueling")
                last_display_text = display_text
                display_text = crindsim.get_display_text()
                self.log.info(f"The displey is ashowing after fueling: {display_text}")

            start_time = time.time()
            while last_display_text == display_text and time.time() - start_time <= 60:
                display_text = crindsim.get_display_text()
                self.log.info(f"Crind display was not updated yet, it is {display_text}")
                time.sleep(1)

            if last_display_text == display_text:
                tc_fail(f"Crind display was not updated during 1 minute, it keeps in {display_text}", exit=True)
                return False

        return True