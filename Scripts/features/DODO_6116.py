"""
    File name: Commercial_Prepay.py
    Tags:
    Description: 
    Author: 
    Date created: 2019-11-29 07:21:07
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import Navi, mws, pos, system, networksim, crindsim, pinpadsim, runas
from app.framework import EDH
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app.features import feature_activation, forecourt_installation
import time

class DODO_6116():
    """
    Description: NGFC and non NGFC transactions performed using a dispenser retail
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

        # The main crindsim object
        self.crindsim = crindsim

        # The main EDH object
        self.edh = EDH.EDH()

    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        """

        #Commercial feature activation
        #self.Commercial_feature_activation()

        #Commercial Diesel checkbox activation in forecourt installation 
        self.set_commercial_on_forecourt(enabled=False)

        # HostSim Response mode
        networksim.set_response_mode("Approval")

        # Disable commerical parameters
        networksim.disable_commercial_fuel_limits()
        networksim.disable_product_limits()
        networksim.disable_prompts()
        
        # Setting host sim information so we can validate this in the message
        networksim.set_commercial_customer_information("Gilbarco", "Greensboro", "NC", "27410")
        networksim.set_commercial_product_limit("True","CADV","Company funds cash advance",0.00)
        networksim.set_commercial_product_limit("True", "MERC", "Default category for merchandise", 30.00)
        networksim.set_commercial_fuel_limit("True", "001", 50.00)
        networksim.set_commercial_fuel_limit("True", "002", 50.00)
        networksim.set_commercial_fuel_limit("True", "003", 50.00)

        crindsim.set_mode("auto")
        crindsim.set_sales_target()

        #open Browser
        self.pos.connect()

        self.pos.sign_on()

        # Making reversals to be send to the host
        self.pos.add_item()
        self.pos.pay_card()


    def get_saf_MaxAmt(self, query, inside = True):
        """
        Retrieve SAFKey and Max amount of transactions allowed in SAF mode for inside or outside
        Args:
            query(str): the query that obtains the SAFKey from XOM_Rules table
            inside(bool): whether is an outside parameters or inside parameter the ones
                          which will be affected.
        Returns:
            dict: with SAFKey as index and max transaccions limit as value.
        """
        if inside:
            query = f"select SAFKey,'/',MaxAmtIn from XOM_SAF where SAFKey in ({query})"
            
        else:
            query = f"select SAFKey,'/',MaxAmtOut from XOM_SAF where SAFKey in ({query})"
        
        output = runas.run_sqlcmd(query, database="network", cmdshell=False)['output']

        # Turning string into list of strings that have \n delimitation
        output_list = output.split("\n")
        output_list = output_list[2:-3]
        output_dic = {}
        # create the dictionary with values from the list result
        for value in output_list:
            keyValue = value.replace(" ","")
            keyValue = keyValue.split("/")
            output_dic [keyValue[0]] = keyValue[1]

        #the first 2 lines are not important
        return output_dic

    def get_saf_MaxNum(self, query, inside = True):
        """
        Retrieve SAFKey and MaxNum of transactions allowed in SAF mode for inside or outside
        Args:
            query(str): the query that obtains the SAFKey from XOM_Rules table
            inside(bool): whether is an outside parameters or inside parameter the ones
                          which will be affected.
        Returns:
            dict: with SAFKey as index and max transaccions limit as value.
        """
        if inside:
            query = f"select SAFKey,'/',MaxNumIn from XOM_SAF where SAFKey in ({query})"
            
        else:
            query = f"select SAFKey,'/',MaxNumOut from XOM_SAF where SAFKey in ({query})"
        
        output = runas.run_sqlcmd(query, database="network", cmdshell=False)['output']

        # Turning string into list of strings that have \n delimitation
        output_list = output.split("\n")
        output_list = output_list[2:-3]
        output_dic = {}
        # create the dictionary with values from the list result
        for value in output_list:
            keyValue = value.replace(" ","")
            keyValue = keyValue.split("/")
            output_dic [keyValue[0]] = keyValue[1]

        #the first 2 lines are not important
        return output_dic

    def set_saf_MaxAmt(self, query, limit, inside = True):
        """
        Set a Max amount of transactions allowed in SAF mode for inside or outside
        Args:
            query(str): the query that obtains the SAFKey from XOM_Rules table
            limit(str or dict): it depends on whether set or reset values
            inside(bool): whether is an outside parameters or inside parameter the ones
                          which will be affected.
        Returns:
            str: query applying result.
        """
        if inside:
            if type(limit) == dict:
                for key, value in limit.items():
                    query = f"update XOM_SAF set MaxAmtIn = '{value}' where SAFKey = {key}"
                    output = runas.run_sqlcmd(query, database="network", cmdshell=False)['output']
            else:
                query = f"update XOM_SAF set MaxAmtIn = '{limit}' where SAFKey in ({query})"
                output = runas.run_sqlcmd(query, database="network", cmdshell=False)['output']
        else:
            if type(limit) == dict:
                for key, value in limit.items():
                    query = f"update XOM_SAF set MaxAmtOut = '{value}' where SAFKey = {key}"
                    output = runas.run_sqlcmd(query, database="network", cmdshell=False)['output']
            else:
                query = f"update XOM_SAF set MaxAmtOut = '{limit}' where SAFKey in ({query})"
                output = runas.run_sqlcmd(query, database="network", cmdshell=False)['output']
        
        return output

    def set_saf_MaxNum(self, query, limit, inside = True):
        """
        Set a MaxNum of transactions allowed in SAF mode for inside or outside
        Args:
            query(str): the query that obtains the SAFKey from XOM_Rules table
            limit(str or dict): it depends on whether set or reset values
            inside(bool): whether is an outside parameters or inside parameter the ones
                          which will be affected.
        Returns:
            str: query applying result.
        """
        if inside:
            if type(limit) == dict:
                for key, value in limit.items():
                    query = f"update XOM_SAF set MaxNumIn = '{value}' where SAFKey = {key}"
                    output = runas.run_sqlcmd(query, database="network", cmdshell=False)['output']
            else:
                query = f"update XOM_SAF set MaxNumIn = '{limit}' where SAFKey in ({query})"
                output = runas.run_sqlcmd(query, database="network", cmdshell=False)['output']
        else:
            if type(limit) == dict:
                for key, value in limit.items():
                    query = f"update XOM_SAF set MaxNumOut = '{value}' where SAFKey = {key}"
                    output = runas.run_sqlcmd(query, database="network", cmdshell=False)['output']
            else:
                query = f"update XOM_SAF set MaxNumOut = '{limit}' where SAFKey in ({query})"
                output = runas.run_sqlcmd(query, database="network", cmdshell=False)['output']
        
        return output

    def inititalize_dynamic_prompts(self):
        """
        Set all commercial dynamic prompt in false or disabled.
        """
        host_prompts_config = {'BDAY' : ['Birthday information','',False],
                            'BLID' : ['Billing ID','',False],
                            'CNTN' : ['Control number','',False],
                            'DLIC' : ['Drivers license number','',False],
                            'DLST' : ['Drivers license state','',False],
                            'DRID' : ['Driver ID','',False],
                            'DTKT' : ['Delivery ticket number','',False],
                            'FSTI' : ['First name initial','',False],
                            'HBRD' : ['Hubometer reading','',False],
                            'HRRD' : ['Reefer hour meter reading','',False],
                            'ISNB' : ['Issuer Number','',False],
                            'LCST' : ['Vehicle license plate state','',False],
                            'LICN' : ['Vehicle license plate number','',False],
                            'LSTN' : ['Last Name','',False],
                            'NAME' : ['Customer name','',False],
                            'ODRD' : ['Odometer reading','',False],
                            'PONB' : ['Purchase order number','',False],
                            'PPIN' : ['Non encrypted PIN','',False],
                            'RTMP' : ['Reefer temperature','',False],
                            'SSEC' : ['Social Security Number','',False],
                            'SSUB' : ['Sub fleet number','',False],
                            'TRIP' : ['Trip number','',False],
                            'TRLR' : ['Trailar number','',False],
                            'TRNB' : ['Transaction number','',False],
                            'UNIT' : ['Unit number','',False],
                            'VEHN' : ['Vehicle number','',False]}
        
        for token, description in host_prompts_config.items():
            networksim.set_commercial_prompt(description[2], token, description[0], description[1])
    
    def Commercial_feature_activation(self):
        
        #Set the features to activate
        DEFAULT_COMMERCIAL = ["Base Passport", "Enhanced Store", "Enhanced Reporting", "Advanced Merchandising",
                    "Employee Management", "Enhanced Card Services", "Enhanced Loyalty Interface",
                    "Multiple Loyalty Interface", "Play at the Pump", "Mobile Payment",
                    "Prepaid Card Services", "Windows 10 License",  "Commercial Diesel", "Tablet POS", "Car Wash"]
        
        #Instatiate Feature Activation
        FA = feature_activation.FeatureActivation()
        
        # Activate defined Features
        if not FA.activate(DEFAULT_COMMERCIAL, mode="Passport Individual Bundles"):
            tc_fail("Failed with Commercial Features installation")
    
    def set_commercial_on_forecourt(self, enabled=True):
        """
        Set the dispenser as commercial Diesel if it is enabled=True or set it as retail one if it is unchecked (enabled=False)
        """
        fc_config = {
            "Dispensers" : {
                "Commercial Diesel": enabled #Transponder is now Commercial Check
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
    
    @test
    def PrepayRetail_CommercialFuelProducts_NonNGFCCard(self):
        """
        When the commercial diesel check is disabled from forcourt installation,
        a transaction with a non NGFC card, should not show the fuel products prompts.
        """        
      
        #Input constants

        generic_trans_amount = "$5.00" # any value that gets an approval from the host
        card_to_use_NonNGFC = 'Visa' # using this card as a generci credit card
        default_dispenser = '1' # we need just one dispenser in this test case

        #Output verifications

        receipt_data = ["Regular CA   PUMP# 1",
                        "5.000 GAL @ $1.000/GAL         $5.00  99",
                        "Subtotal =   $5.00",
                        "Tax  =    $0.00",
                        "Total =   $5.00",
                        "Change Due  =    $0.00",
                        "Credit                          $5.00"]

        self.preauth_request_verifications = {
            'Fuel Purchase': '500'}

        self.preauth_response_verifications = {
            'Response Code': '2', 
            'Approved Amount': '000000500'}

        self.capture_request_verifications = {
            'Fuel Purchase': '500'}

        self.capture_response_verifications = {
            'Response Code': '0', 
            'Approved Amount': '000000500'}


        crindsim.set_mode("auto")
        crindsim.set_sales_target(sales_type = "auth")

        self.log.debug("Waiting for dispenser ready")
        self.pos.wait_disp_ready(dl_timeout=60)

        self.log.debug("Adding prepay")
        self.pos.add_fuel(generic_trans_amount)

        #look for the last message before payment so we know the messages involved in the transaction

        last_msg = self.edh.get_last_msg_id(pspid='23')

        # Pay the transaction 

        self.log.debug("Starting payment")
        self.pos.pay_card(brand="CORE", card_name = card_to_use_NonNGFC)

        self.log.debug("Waiting for fuel")
        self.pos.wait_for_fuel(default_dispenser, timeout=120)
        
        # Get messages the 4 messages (preauth and completion)
        messages = self.edh.get_network_messages(8,start_in=last_msg)        

        start_time = time.time()
        while len(messages) < 4 and (time.time() - start_time < 60):
            self.log.debug("The expected network messages are not still available, retrying...")
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
        
        self.pos.select_dispenser(default_dispenser)

        # verify that the information on the receipt is correct to be sure that the transaction
        # was approved and the information generated based on that is correct
        self.pos.check_receipt_for(receipt_data, timeout=10)
    
    @test
    def OutsideRetail_CommercialFuelProducts_OutsideNGFCCard(self): #MAKE OUTSIDE SALE
        """
        When the commercial diesel check is disabled from forcourt installation,
        even in a transaction with a NGFC card, should not show the fuel products prompts.
        """
        #Dispenser Prompts
        dispenser_prompts = {#"Commercial_prompt" is a dictionary in which are the dinamic prompts for commercial diesel
                    "Make selection":{
                        "entry": [""],
                        "buttons": ["Tractor"]
                    },
                    "Need DEF?":{
                        "entry": [""],
                        "buttons": ["Yes"]
                    },
                    "Is this a Debit/ATM card?":{
                        "entry": [""],
                        "buttons": ["No"]
                    },
                    "To Verify Age Enter Your Full Birthdate (MMDDYYYY)": {
                        "entry": ["02211980"],
                        "buttons": ["Yes"]
                    },
                    "Additional Products Y/N?": {
                        "entry": [""],
                        "buttons": ["Yes"]
                    },
                    "Please, go inside to  get the cash/buy products.":{
                        "entry": [""],
                        "buttons": ["Ok"]
                    }
                }

        #Input constants
        
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts
        default_dispenser = '1' # we need just one dispenser in this test case
        
        #Output verifications

        receipt_data = ["Regular CA   PUMP# 1",
                        "5.000 GAL @ $1.000/GAL         $5.00  99",
                        "Subtotal =   $5.00",
                        "Tax  =    $0.00",
                        "Total =   $5.00",
                        "Change Due  =    $0.00",
                        "Credit                          $5.00"]

        self.preauth_request_verifications = {
            'Fuel Purchase': '5000', 
            '001 - Wex OTR Flags': 'R- Retail'}

        self.preauth_response_verifications = {
            'Response Code': '2', 
            'Approved Amount': '000005000'}

        self.capture_request_verifications = {
            'Fuel Purchase': '500', 
            '001 - Wex OTR Flags': 'R- Retail'}

        self.capture_response_verifications = {
            'Response Code': '0', 
            'Approved Amount': '000000500'}

        crindsim.set_mode("auto")
        crindsim.set_sales_target("money", "5")

        #look for the last message before payment so we know the messages involved in the transaction
        last_msg = self.edh.get_last_msg_id(pspid='23')
        self.log.debug(f"Starting to filter networkmessages table from message id :{last_msg}")

        crindsim.swipe_card(card_name=card_to_use_NGFC, brand="EXXON")
        
        self.crind_prompts_handler(dispenser_prompts)

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
        
        self.pos.sign_on()   

        self.pos.select_dispenser(default_dispenser)        

        self.pos.wait_for_fuel(default_dispenser, timeout=60)

        # Getting the last message before starting the completion
        last_msg = self.edh.get_last_msg_id(pspid='23')

        # Select the buffer to complete the transaction, this happens because we said when we paid
        # that we will add addition products self.pos.pay_card(card_name='NGFC', additional_prod = 'Yes')
        self.pos.click_fuel_buffer('A')

        #Commercial transaction set with additional product need to hit pay to complete the transaction
        self.pos.click_function_key('Pay')
        
        #it will prompt asking to print receipt and the answer will be NO
        self.pos.click_message_box_key('No', timeout=10)

        # Waiting for completion messages are generated
        last_msg = self.wait_for_new_msg(last_msg, "23")    
        
        # Get messages to check the completion
        messages = self.edh.get_network_messages(4,start_in=last_msg)

        start_time = time.time()
        while len(messages) < 2 and (time.time() - start_time < 60):
            self.log.debug("The expected network messages are not still available, retrying...")
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
    
    '''
    TODO: enable this test case when DODO-6287 gets fixed
    @test
    def PrepayRetail_CommercialPrompts_NGFCCard(self):
        """
        When the commercial diesel check is disabled, for the NGFC Card, the system show the dynamic prompts,
        cash advance, additional products and fuel limits (if correspondent), the system doesn't show the fuel
        products for the inside transaction.
        """

        #Input constants

        self.birthday = "120270"
        self.billing = "12"

        generic_trans_amount = "$5.00" # any value that gets an approval from the host
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts
        default_dispenser = '1' # we need just one dispenser in this test case
        commercial_prompts = {              
                "ENTER BIRTHDAY IN MMDDYY FORMAT": {
                    "entry": [self.birthday],
                    "buttons": ["Ok"] # This allow us to have answer differently to the same prompt in the same transaction
                }, 
                "ENTER BILLING ID": {
                    "entry" : [self.billing],
                    "buttons": ["Enter"]                
                },
                "Additional Products Y/N?": {                    
                    "buttons": ["Yes"]
                }
            }

        #Output verificacions

        receipt_data = ["Regular CA   PUMP# 1",
                        "5.000 GAL @ $1.000/GAL         $5.00  99",
                        "Subtotal =   $5.00",
                        "Tax  =    $0.00",
                        "Total =   $5.00",
                        "Change Due  =    $0.00",
                        "Credit                          $5.00",
                        "Billing ID: " + self.billing]

        self.preauth_request_verifications = {
            'Fuel Purchase': '500', 
            '001 - Wex OTR Flags': 'R- Retail',
            '008 - Wex OTR Cash Advance Limit': '$0.00'}

        self.preauth_response_verifications = {
            'Response Code': '2', 
            'Approved Amount': '000000500',
            '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 0.00',
            '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',                            
            '003 - Wex OTR Fuel Product Limits - Product Code: 001': 'Product limit: 50.00',
            '003 - Wex OTR Fuel Product Limits - Product Code: 002': 'Product limit: 50.00',
            '003 - Wex OTR Fuel Product Limits - Product Code: 003': 'Product limit: 50.00',
            '005 - Wex OTR Customer Information': 'Gilbarco                 Greensboro     NC27410'}

        self.capture_request_verifications = {
            'Fuel Purchase': '500', 
            '001 - Wex OTR Flags': 'R- Retail'}

        self.capture_response_verifications = {
            'Response Code': '0', 
            'Approved Amount': '000000500',
            '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 0.00',
            '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',
            '003 - Wex OTR Fuel Product Limits - Product Code: 001': 'Product limit: 50.00',
            '003 - Wex OTR Fuel Product Limits - Product Code: 002': 'Product limit: 50.00',
            '003 - Wex OTR Fuel Product Limits - Product Code: 003': 'Product limit: 50.00',
            '005 - Wex OTR Customer Information': 'Gilbarco                 Greensboro     NC27410'}

        # Specific cofiguration - Host simulator
        networksim.set_commercial_prompt(True, 'BDAY', 'Birthday information', 'A;TS;M3;X6')
        networksim.set_commercial_prompt(True, 'BLID', 'Billing ID', 'N;TN;M0;X521')

        self.pos.add_fuel(generic_trans_amount)

        #look for the last message before payment so we know the messages involved in the transaction

        last_msg = self.edh.get_last_msg_id(pspid='23')
        self.log.debug(f"Starting to filter networkmessages table from message id :{last_msg}")

        # Pay the transaction 

        self.pos.pay_card(card_name = card_to_use_NGFC, brand="EXXON", prompts= commercial_prompts)
       
        # get the last 4 messages in the DB after payment
        # there is some stuff that is not exactly a message and 
        # we will remove them, we just need 2, preauth and completion

        messages = self.edh.get_network_messages(4,start_in=last_msg)
        self.log.debug(messages)

        start_time = time.time()
        while len(messages) < 2 and (time.time() - start_time < 10):
            self.log.debug("The expected network messages are not still available, retrying...")
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

        self.pos.wait_for_fuel()

        #look for the last message before payment so we know the messages involved in the transaction

        self.pos.select_dispenser(default_dispenser)

        # Select the buffer to complete the transaction, this happens because we said when we paid
        # that we will add addition products self.pos.pay_card(card_name='NGFC', additional_prod = 'Yes')
        self.pos.click_fuel_buffer('A')

        #Commercial transaction set with additional product need to hit pay to complete the transaction
        self.pos.click_function_key('Pay')
        
        #it will prompt asking to print receipt and the answer will be NO
        self.pos.click_message_box_key('No', timeout=10)

        # Waiting for completion messages are generated
        last_msg = self.wait_for_new_msg(last_msg, "23")

        messages = self.edh.get_network_messages(4,start_in=last_msg)

        start_time = time.time()
        while len(messages) < 2 and (time.time() - start_time < 10):
            self.log.debug("The expected network messages are not still available, retrying...")
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
        
        # reset prompt changes in host simulator
        networksim.disable_prompts()
        
        # verify that the information on the receipt is correct to be sure that the transaction
        # was approved and the information generated based on that is correct
        self.pos.check_receipt_for(receipt_data, dispenser= default_dispenser, timeout=10)
    '''
    @test
    def PrepayRetail_CommercialFuelProducts_NonNGFCCard_SAFMode(self):
        """
        For the SAF Mode, when the commercial diesel check is disabled,
        for the non NGFC Card, the system musnt'n show the fuel products for the inside transaction.
        """

        #Input constants

        generic_trans_amount = "$5.00" # any value that gets an approval from the host
        card_to_use_NonNGFC = 'Visa'
        default_dispenser = '1' # we need just one dispenser in this test case

        #Output verifications

        receipt_data = ["Regular CA   PUMP# 1",
                        "5.000 GAL @ $1.000/GAL         $5.00  99",
                        "Subtotal =   $5.00",
                        "Tax  =    $0.00",
                        "Total =   $5.00",
                        "Change Due  =    $0.00",
                        "Credit                          $5.00"]

        prompts = {#"Commercial_prompt" is a dictionary in which are the dinamic prompts for commercial diesel
                        "Host Time out": {                            
                            "buttons": ["Enter"]
                        }
                    }
        self.preauth_request_verifications = {
            'Fuel Purchase': '500'}

        #Specific configuration - Host simulator
        networksim.set_response_mode("Timeout")
        # reset prompt changes in host simulator
        networksim.disable_prompts()


        #find the correct ruleskey value
        cardNumber = crindsim._get_card_data(brand='CORE', card_name = card_to_use_NonNGFC)['Track2']
        cardNumber = cardNumber.split('=')
        query = f"select RulesKey from XOM_Bin where beginrange <= left('{cardNumber[0]}', len(BeginRange)) and EndRange >= left('{cardNumber[0]}', len(Endrange)) and Mode = 'C'"
        rulesKeyValue = runas.run_sqlcmd(query, database="network", cmdshell=False)['output']
        rulesKeyValue = rulesKeyValue.split("\n")
        rulesKeyValue = rulesKeyValue[2:-3]

        # Increse SAF mode transactions limit, to assure that this transaction is approved in offline mode.
        #save previous valued for the amount
        query = f"select SAFKey from XOM_Rules where Ruleskey = '{rulesKeyValue[0]}'"
        MaxAmtList = self.get_saf_MaxAmt(query)
        #apply new value for the amount
        setMaxAmtValue = self.set_saf_MaxAmt(query, '9999.99')

        if not setMaxAmtValue.find(f"{len(MaxAmtList)} row"): #validate that new values were applied
            tc_fail('Unable to set max amount limits in XOM_SAF table')
        
        #save previous valued for the number
        MaxNumList = self.get_saf_MaxNum(query)
        #apply new value for the number
        setMaxNumValue = self.set_saf_MaxNum(query, '99')

        if not setMaxNumValue.find(f"{len(MaxNumList)} row"): #validate that new values were applied
            tc_fail('Unable to set max num limits in XOM_SAF table')

        self.pos.add_fuel(generic_trans_amount)

        #look for the last message before payment so we know the messages involved in the transaction

        last_msg = self.edh.get_last_msg_id(pspid='23')
        
        self.pos.maximize_pos

        # Pay the transaction 

        self.pos.pay_card(brand="Core", card_name = card_to_use_NonNGFC, prompts=prompts, timeout_transaction=True)

        self.pos.wait_for_fuel()
        # Get messages the 4 messages (preauth and completion)
        messages = self.edh.get_network_messages(8,start_in=last_msg)

        last_msg = self.edh.get_last_msg_id(pspid='23')

       
        # Message # 0 should be the preauth request
        
        msg_translated = self.edh.translate_message(messages[0])

        if msg_translated: # If different of False, it is understood as True
            
            self.edh.verify_field(msg_translated, self.preauth_request_verifications)
        
        else:

            tc_fail('Unable to translate the network message')

        # HostSim Response mode
        networksim.set_response_mode("Approval")

        #reset previous value
        setMaxAmtValue = self.set_saf_MaxAmt(query, MaxAmtList)

        if not setMaxAmtValue.find(f"{len(MaxAmtList)} row"): #validate that previous values were applied
            tc_fail('Was unable to reset previous value for total amount limit in XOM_SAF table')
        
        #reset previous value
        setMaxNumValue = self.set_saf_MaxNum(query, MaxNumList)

        if not setMaxNumValue.find(f"{len(MaxNumList)} row"): #validate that previous values were applied
            tc_fail('Was unable to reset previous value for total transacions limit in XOM_SAF table')

        # verify that the information on the receipt is correct to be sure that the transaction
        # was approved and the information generated based on that is correct
        self.pos.check_receipt_for(receipt_data, timeout=10)
        
        self.pos.add_item()
        self.pos.pay_card()

        # Making reversal be send to the host
        self.log.info("Waiting for the reversal to be completed")
        
        start = time.time()
        reversal_found = False
        message_to_find= ""
        
        self.log.debug("Checking if the reversal was already placed")
        while not reversal_found or time.time() - start < 60:

            messages = self.edh.get_network_messages(12,start_in=last_msg)
            for message in messages:
                if "Reversal response" in message:
                    self.log.debug(f"The reversal was found: {message}")
                    message_to_find = message.split()
                    message_to_find = f"Response {message_to_find[9]}"
                    break
            
            self.log.debug("Checking if a local approved transaction was placed")
            messages = self.edh.get_network_messages(12,start_in=last_msg)            
            for message in messages:
                if message_to_find in message:
                    self.log.debug(f"Local Apporved transaction found: {message}")
                    reversal_found = True
                    break
    
    '''
    #TODO: uncomment when DODO-6276 get fixed
    @test
    def OutsideRetail_CommercialPrompts_NGFCCard_SAFMode(self):
        """
        For the SAF Mode, when the commercial diesel check is disabled, for the NGFC Card,
        the system show the dynamic prompts, cash advance, additional products and fuel limits
        (if correspondent), the system doesn't show the fuel products for the outside transaction.
        """

        #Input constants

        #Dispenser Prompts
        dispenser_prompts = {#"Commercial_prompt" is a dictionary in which are the dinamic prompts for commercial diesel
                    "Make selection":{
                        "entry": [""],
                        "buttons": ["Tractor"]
                    },
                    "Need DEF?":{
                        "entry": [""],
                        "buttons": ["Yes"]
                    },
                    "Is this a Debit/ATM card?":{
                        "entry": [""],
                        "buttons": ["No"]
                    },
                    "To Verify Age Enter Your Full Birthdate (MMDDYYYY)": {
                        "entry": ["02211980"],
                        "buttons": ["Yes"]
                    },
                    "Additional Products Y/N?": {
                        "entry": [""],
                        "buttons": ["Yes"]
                    },
                    "Please, go inside to  get the cash/buy products.":{
                        "entry": [""],
                        "buttons": ["Ok"]
                    },
                    "Want receipt?":{
                        "entry": [""],
                        "buttons": ["Yes"]
                    },
                    "Do you want cash advance up to $10?":{
                        "entry": [""],
                        "buttons": ["Yes"]
                    }

                }

        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts
        default_dispenser = '1' # we need just one dispenser in this test case

        #Output verifications
        
        receipt_data = ["Regular CA   PUMP# 1",
                        "5.000 GAL @ $1.000/GAL         $5.00  99",
                        "Subtotal =   $5.00",
                        "Tax  =    $0.00",
                        "Total =   $5.00",
                        "Change Due  =    $0.00",
                        "Credit                          $5.00"]
        
        self.preauth_request_verifications = {
            'Fuel Purchase': '5000', 
            '001 - Wex OTR Flags': 'R- Retail'}

        self.capture_request_verifications = {
            'Fuel Purchase': '500', 
            '001 - Wex OTR Flags': 'R- Retail'}

        self.log.debug("Find the correct ruleskey value")
        cardNumber = crindsim._get_card_data(brand='EXXON', card_name = card_to_use_NGFC)['Track2']
        cardNumber = cardNumber.split('=')
        query = f"select RulesKey from XOM_Bin where beginrange <= left('{cardNumber[0]}', len(BeginRange)) and EndRange >= left('{cardNumber[0]}', len(Endrange)) and Mode = 'C'"
        rulesKeyValue = runas.run_sqlcmd(query, database="network", cmdshell=False)['output']
        rulesKeyValue = rulesKeyValue.split("\n")
        rulesKeyValue = rulesKeyValue[2:-3]

        # Increse SAF mode transactions limit, to assure that this transaction is approved in offline mode.
        #save previous valued for the amount
        self.log.debug("Increse SAF mode transactions limit")
        query = f"select SAFKey from XOM_Rules where Ruleskey = '{rulesKeyValue[0]}'"
        MaxAmtList = self.get_saf_MaxAmt(query, inside = False)
        
        self.log.debug("Apply new value for the amount")
        setMaxAmtValue = self.set_saf_MaxAmt(query, '9999.99', inside = False)

        if not setMaxAmtValue.find(f"{len(MaxAmtList)} row"): #validate that new values were applied
            tc_fail('Unable to set max amount limits in XOM_SAF table')
        
        self.log.debug("Save previous maximum value")
        MaxNumList = self.get_saf_MaxNum(query, inside = False)
        
        self.log.debug("Set new max amount in 99")
        setMaxNumValue = self.set_saf_MaxNum(query, '99', inside = False)

        if not setMaxNumValue.find(f"{len(MaxNumList)} row"): #validate that new values were applied
            tc_fail('Unable to set max num limits in XOM_SAF table')

        crindsim.set_mode("auto")
        crindsim.set_sales_target("money", "5")
        
        #look for the last message before payment so we know the messages involved in the transaction
        last_msg = self.edh.get_last_msg_id(pspid='23')

        self.log.debug("Specific configuration - Host simulator")
        networksim.set_response_mode("Timeout")

        crindsim.swipe_card(card_name=card_to_use_NGFC, brand="EXXON")

        # get the last 4 messages in the DB after payment
        # there is some stuff that is not exactly a message and 
        # we will remove them, we just need 2, preauth and completion

        messages = self.edh.get_network_messages(4,start_in=last_msg)        

        start_time = time.time()
        while len(messages) < 1 and (time.time() - start_time < 10):
            self.log.debug("The expected network messages are not still available, retrying...")
            messages = self.edh.get_network_messages(4,start_in=last_msg)

        if len(messages) < 1:
            
            tc_fail("The messages obtained from the EDH do not contain request and response messages")        
        
        # Message # 0 should be the preauth request since respose is a timeout
        
        msg_translated = self.edh.translate_message(messages[0])

        if msg_translated: # If different of False, it is understood as True
            
            self.edh.verify_field(msg_translated, self.preauth_request_verifications)
        
        else:

            tc_fail('Unable to translate the network message')

        self.crind_prompts_handler(dispenser_prompts)

        # HostSim Response mode
        networksim.set_response_mode("Approval")

        #reset previous value
        setMaxAmtValue = self.set_saf_MaxAmt(query, MaxAmtList, inside = False)

        if not setMaxAmtValue.find(f"{len(MaxAmtList)} row"): #validate that previous values were applied
            tc_fail('Was unable to reset previous value for total amount limit in XOM_SAF table')
        
        #reset previous value
        setMaxNumValue = self.set_saf_MaxNum(query, MaxNumList, inside = False)

        if not setMaxNumValue.find(f"{len(MaxNumList)} row"): #validate that previous values were applied
            tc_fail('Was unable to reset previous value for total transacions limit in XOM_SAF table')
        
        self.pos.sign_on()

        self.log.debug("Waiting for fueling 120 seconds")
        self.pos.wait_for_fuel(timeout=120)

        self.log.debug("Select Buffer A")
        self.pos.click_fuel_buffer('A')

        self.log.debug("Commercial transaction set with additional product need to hit pay to complete the transaction")
        self.pos.click_function_key('Pay')
        
        #it will prompt asking to print receipt and the answer will be NO
        self.pos.click_message_box_key('No', timeout=5)

        # Making reversal be send to the host
        self.pos.click_function_key('Host Function')

        self.log.info("Accepting prompt: Do you want to perfrom a communication test?")
        self.pos.click_message_box_key('Yes', timeout=30)

        self.log.info("Accepting prompt: Do you really want to perfrom a communication test?")
        self.pos.click_message_box_key('Yes', timeout=30)

        self.log.info("Acceptiong comm test result")
        self.pos.click_message_box_key('Ok', timeout=30)

        self.pos.select_dispenser(default_dispenser)

        # verify that the information on the receipt is correct to be sure that the transaction
        # was approved and the information generated based on that is correct
        self.pos.check_receipt_for(receipt_data, dispenser= default_dispenser, timeout=10)
    '''
    @test
    def PrepayCommercial_CommercialPrompts_NGFCCard(self):
        """
        End to end commercial fuel prepay will be performed in order to verify the fuel type selection at beginig, both fuels and DEF should be selected and transaction ends without errors.
        """
        #Input constants

        generic_trans_amount = "$5.00" # any value that gets an approval from the host
        both_fuel_type = 'Both fuels.' # this is both fuels,  because is the objective of this testcase
        def_type_yes = 'Yes' # this is "yes",  because is the objective of this testcase
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts
        default_dispenser = '1' # we need just one dispenser in this test case
        commercial_prompts = {              
                            "Additional Products Y/N?": {                    
                                "buttons": ["Yes"]
                            }
                        }

        #Output verifications

        receipt_data = ["Regular CA   PUMP# 1",
                        "5.000 GAL @ $1.000/GAL         $5.00  99",
                        "Subtotal =   $5.00",
                        "Tax  =    $0.00",
                        "Total =   $5.00",
                        "Change Due  =    $0.00",
                        "Credit                          $5.00"]

        self.preauth_request_verifications = {
            'Fuel Purchase': '500', 
            '001 - Wex OTR Flags': 'C - Commercial',
            '008 - Wex OTR Cash Advance Limit': '$0.00'}

        self.preauth_response_verifications = {
            'Response Code': '2', 
            'Approved Amount': '000000500',
            '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 0.00',
            '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',
            '003 - Wex OTR Fuel Product Limits - Product Code: 001': 'Product limit: 50.00',
            '003 - Wex OTR Fuel Product Limits - Product Code: 002': 'Product limit: 50.00',
            '003 - Wex OTR Fuel Product Limits - Product Code: 003': 'Product limit: 50.00',
            '005 - Wex OTR Customer Information': 'Gilbarco                 Greensboro     NC27410'}

        self.capture_request_verifications = {
            'Fuel Purchase': '500', 
            '001 - Wex OTR Flags': 'C - Commercial'}

        self.capture_response_verifications = {
            'Response Code': '0', 
            'Approved Amount': '000000500',
            '002 - Wex OTR Non-Fuel Product Data - Product code: CADV (Company funds cash advance)': 'Amount: 0.00',
            '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',
            '003 - Wex OTR Fuel Product Limits - Product Code: 001': 'Product limit: 50.00',
            '003 - Wex OTR Fuel Product Limits - Product Code: 002': 'Product limit: 50.00',
            '003 - Wex OTR Fuel Product Limits - Product Code: 003': 'Product limit: 50.00',
            '005 - Wex OTR Customer Information': 'Gilbarco                 Greensboro     NC27410'}

        self.pos.minimize_pos()

        # set dispenser as a commercial one
        self.set_commercial_on_forecourt()

        self.pos.maximize_pos()        

        self.pos.select_dispenser(default_dispenser)

        self.pos.wait_disp_ready(idle_timeout=60)

        self.pos.add_fuel(generic_trans_amount, fuel_type= both_fuel_type, def_type = def_type_yes)

        #look for the last message before payment so we know the messages involved in the transaction

        last_msg = self.edh.get_last_msg_id(pspid='23')

        # Pay the transaction 

        self.pos.pay_card(brand="Exxon", card_name = card_to_use_NGFC, prompts= commercial_prompts)
       
        # get the last 4 messages in the DB after payment
        # there is some stuff that is not exactly a message and 
        # we will remove them, we just need 2, preauth and completion

        self.log.debug("Looking for the preauth request and response")
        messages = self.edh.get_network_messages(4,start_in=last_msg)

        start_time = time.time()
        while len(messages) < 2 and (time.time() - start_time < 20):
            self.log.debug("The expected network messages are not still available, retrying...")
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

        self.pos.wait_for_disp_status("Fueling", timeout=5, verify=False)

        self.pos.wait_for_fuel(default_dispenser)

        #look for the last message before payment so we know the messages involved in the transaction

        last_msg = self.edh.get_last_msg_id(pspid='23')

        self.pos.select_dispenser(default_dispenser)

        # Select the buffer to complete the transaction, this happens because we said when we paid
        # that we will add addition products self.pos.pay_card(card_name='NGFC', additional_prod = 'Yes')
        self.pos.click_fuel_buffer('commercial')

        #Commercial transaction set with additional product need to hit pay to complete the transaction
        self.pos.click_function_key('Pay')
        
        #it will prompt asking to print receipt and the answer will be NO
        self.pos.click_message_box_key('No', timeout=30)

        # Waiting for completion messages are generated
        last_msg = self.wait_for_new_msg(last_msg, "23")

        messages = self.edh.get_network_messages(4,start_in=last_msg)

        start_time = time.time()
        while len(messages) < 2 and (time.time() - start_time < 10):
            self.log.debug("The expected network messages are not still available, retrying...")
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
    
    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """

        self.pos.close()