"""
    File name: NGFC_Helpers.py
    Tags:
    Description: This is a script wth helpers for NGFC project
    Author: 
    Date created: 2020-07-06 09:19:51
    Date last modified: 
    Python Version: 3.7
"""


from app import Navi, pos, system, forecourt_installation, crindsim, networksim, network_site_config, runas
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app.features import feature_activation
from app.framework import EDH

import time

class NGFC_Helpers():
    """
    Description: Test class that provides an interface for testing.
    """

    def __init__(self, log=None, mws=None, pos=None):
        """
        Initializes the Template class.
        """
        # The logging object. 
        # Example: self.log.info(f"Current value of var: {my_var}")
        if not log is None:
            self.log = log

        # The main EDH object
        self.edh = EDH.EDH()

        # The main MWS object 
        if not mws is None:
            self.mws = mws

        if not pos is None:
            self.pos = pos            

        self.crindsim = crindsim

        # Setting constants
        self.grade_1_Name = "Diesel 1"
        self.grade_1_Product = "019"
        self.grade_1_Name_reefer = "RD Dsl 1"
        self.grade_1_Product_reefer = "032"
        self.grade_2_Name = "Diesel 2"
        self.grade_2_Product = "020"
        self.grade_2_Name_reefer = "RD Dsl 2"
        self.grade_2_Product_reefer = "033"
        self.grade_3_Name = "DEF"
        self.grade_3_Product = "062"

        networksim.set_commercial_fuel_limit("True", self.grade_1_Product, 50.00)
        networksim.set_commercial_fuel_limit("True", self.grade_1_Product_reefer, 50.00)
        networksim.set_commercial_fuel_limit("True", self.grade_2_Product, 50.00)
        networksim.set_commercial_fuel_limit("True", self.grade_2_Product_reefer, 50.00)
        networksim.set_commercial_fuel_limit("True", self.grade_3_Product, 50.00)



        # The following dictionary is to have a single place to modify if a prompt is changed
        self.dispenser_prompts = {
            "make selection": "Make selection",
            "DEF": "Need DEF?",
            "debit prompt": "Is this a Debit/ATM card?",
            "additional products": "Additional Products Y/N?",
            "receipt": "Want receipt?",
            "carwash": "Carwash today?"
        }

        self.inside_prompts = {
            "fuel type": "Select fuel products to dispense",
            "DEF": "DEF?",
            "additional products": "Additional Products Y/N?",
            "receipt": "Do you want to print a receipt?"            
        }

        

    def features_handeling(self, features):
        
        #Instatiate Feature Activation
        FA = feature_activation.FeatureActivation()
        
        # Activate defined Features
        return FA.activate(features, mode="Passport Individual Bundles")
    
    def set_commercial_on_forecourt(self, enabled=True, reefer=True):
        """
        Set the dispenser as commercial Diesel
        """
        self.log.debug(f"Attempting to set commercial in {enabled} in forecourt installation")
        fc_config = {
            "Dispensers" : {
                "Commercial Diesel": enabled, #Transponder is now Commercial Check
                "Reefer": reefer
            }
        }
        
        FC = forecourt_installation.ForecourtInstallation()
        self.mws.click("Set Up")

        # Set Commercial Diesel feature to the crind Configured as "Gilbarco"
        FC.change("Gilbarco", "Dispensers", fc_config.get("Dispensers"))

        self.mws.click_toolbar("Save")
        self.mws.click_toolbar("Save")

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

    def wait_for_new_msg(self, last_msg, psp_id, timeout=30):
        
        start = time.time()

        #check it a new message happened since the the last check
        while (last_msg == self.edh.get_last_msg_id(pspid=psp_id)) and (time.time() - start < timeout):
            
            self.log.debug("No new messages found")
            time.sleep(1) #seconds
        if last_msg == self.edh.get_last_msg_id(pspid=psp_id):
            self.log.warning("No new messages were sent to the host")
            return False
            
        return last_msg

    def fuel_handler(self, amounts_to_dispense, print_receipt='No'):

        if amounts_to_dispense is None:
            
            self.log.info("Setting default configuration: amounts_to_dispense was not provided")
            amounts_to_dispense = {
                "buffer_1":{
                    "grade": 1,
                    "value": "5"
                }
            }

        self.log.info(f"Attempting to fuel manually: {amounts_to_dispense}")
        # Using a list to add latter more ways to start
        start_fueling = "Lift handle"
        auth_start_fueling = "BEGIN FUELING"
        
        idle_screen = [
            "INSERT CARD To Pay Here or LIFT HANDLE To Pay Inside",
            "Please, go inside to  get the cash/buy products."
        ]

        receipt = [
            "Want receipt?"
        ]
        
        if not crindsim.set_mode("manual"):
            self.log.error(f"Error setting the dispenser in manual mode")
            return False

        display_text = crindsim.get_display_text()
        self.log.info(f"The Dispenser is showing: {display_text}")
        start_time = time.time()
        while display_text in idle_screen and time.time() - start_time < 180:
            self.log.info(f"Waiting for the dispenser to start fueling, the Dispenser is showing: {display_text}, waiting 1 seconds before retry")
            time.sleep(1)
            display_text = crindsim.get_display_text()

        if display_text in idle_screen:
            self.log.error(f"The Dispenser is showing: {display_text} after waiting 180 seconds for an update")
            return False
        
        buffer = 1

        for item in amounts_to_dispense.values():
            
            #button = None # setting None to clean up the following grades

            try:
                current_grade = item['grade']
                amount = item['value']
                
            except KeyError as e:
                self.log.error(f"The followig key was not provided in the fuel_handler call: {e}")
            
            if amount == "":
                self.log.info("Setting the CRIND in Auth mode")
                if not crindsim.set_sales_target():
                    self.log.error(f"Error calling set_sales_target")
                    return False

            else:
                self.log.info(f"Setting the CRIND in money mode with an amoutn of: {amount}")
                
                if not crindsim.set_sales_target("money", amount):
                    self.log.error(f"Error calling set_sales_target for amount {amount}")
                    return False

            #try:
                # this button allows us to press a keypad button while fueling
            #    button = item['keypad_button']                
                
            #except KeyError as e:
            #    self.log.warning(f"The followig key was not provided in the fuel_handler call: {e}")         

            start_time = time.time()
            display_text = crindsim.get_display_text()
            
            while (not start_fueling in display_text and 
                    not auth_start_fueling in display_text and
                    time.time() - start_time < 180):
                    
                self.log.info(f"The Dispenser is showing: {display_text}, waiting 1 seconds before retry")
                time.sleep(1)
                display_text = crindsim.get_display_text()

            if not start_fueling in display_text and not auth_start_fueling in display_text:
                self.log.error(f"The Dispenser is showing: {display_text} after waiting 60 seconds for an update")
                return False

            else:

                #if not button is None:

                #    crindsim.press_keypad(button)
                
                if not crindsim.select_grade(grade=current_grade):
                    self.log.error(f"Change grade to {current_grade} failed")
                    return False            
                time.sleep(3)
                
                display_text = crindsim.get_display_text()
                self.log.debug(display_text)
                if "see cashier" in display_text:
                    self.log.error(f"see cashier displayed after select grade {current_grade}")

                if not crindsim.lift_handle():
                    self.log.error(f"Lift handle for {current_grade} on buffer {buffer} failed")
                    return False
                time.sleep(2)

                display_text = crindsim.get_display_text()
                self.log.debug(display_text)
                if "see cashier" in display_text:
                    self.log.error(f"see cashier displayed after lift handle for {current_grade} on buffer {buffer}")
                
                if not crindsim.open_nozzle():
                    self.log.error(f"Open nozzel for {current_grade} on buffer {buffer} failed")
                    return False
                time.sleep(5)
                
                display_text = crindsim.get_display_text()
                self.log.debug(display_text)
                if "see cashier" in display_text:
                    self.log.error(f"see cashier displayed after open nozzel for {current_grade} on buffer {buffer}")

                if not crindsim.close_nozzle():
                    self.log.error(f"Close nozzel for {current_grade} on buffer {buffer} failed")
                    return False
                time.sleep(3)
                
                display_text = crindsim.get_display_text()
                self.log.debug(display_text)
                if "see cashier" in display_text:
                    self.log.error(f"see cashier displayed after close nozzel for {current_grade} on buffer {buffer}")

                if not crindsim.lower_handle():
                    self.log.error(f"Lower hanlde for {current_grade} on buffer {buffer} failed")
                    return False

                display_text = crindsim.get_display_text()
                self.log.debug(display_text)
                if "see cashier" in display_text:
                    self.log.error(f"see cashier displayed after lower handle for {current_grade} on buffer {buffer}")

                self.log.info(f"Fuel ${amount} in buffer {buffer} of grade {current_grade} completed")
                buffer = buffer + 1                
                time.sleep(5)

        # Checking if the dispenser returned to idle or get stuck fueling
        display_text = crindsim.get_display_text()
        self.log.info(f"The Dispenser is showing: {display_text}")
        start_time = time.time()
        while not display_text in idle_screen and time.time() - start_time < 120:
            if display_text in receipt:
                self.log.info(f"About to hit {print_receipt} in receipt prompt")
                crindsim.press_softkey(f'{print_receipt}')
            self.log.info(f"Waiting for idle, the Dispenser is showing: {display_text}, waiting 1 seconds before retry")
            time.sleep(1)
            display_text = crindsim.get_display_text()

        if not display_text in idle_screen:
            self.log.error(f"The Dispenser is showing: {display_text} after waiting 60 seconds for an update")
            return False

        return True

    def crind_transaction_handler(self, 
                        prompts, 
                        amounts_to_dispense=None, 
                        decline_scenario=False, 
                        skip_fueling=False,
                        timeout= 120):
        
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
        idle_screen = [
            "INSERT CARD To Pay Here or LIFT HANDLE To Pay Inside",
            "Please, go inside to  get the cash/buy products."
        ]
        receipt = [
            "Want receipt?"
        ]
        stop_messages = ["Cashier has receipt Thank you",
                         "INSERT CARD To Pay Here or LIFT HANDLE To Pay Inside",
                         #"Authorizing...",
                         'Take receipt Thank you',
                         #"Replace nozzle when finished",
                         "Please, go inside to  get the cash/buy products.",
                         #"Lift handle to begin fueling",
                         "Thank you for choosing"]

        if amounts_to_dispense is None:
            
            self.log.info("Setting default configuration for outside fueling")
            amounts_to_dispense = {
                                    "buffer_1":{
                                        "grade": 1,
                                        "value": "5"
                                    }
                                }

        try:
            print_receipt = prompts[self.dispenser_prompts['receipt']]['buttons'][0]
                
        except KeyError:
            print_receipt = 'No'

        self.log.info(f"Starting prompts handler the provide prompts are: {prompts}")

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
                    self.log.info("This is a decline scenario. Quiting crind transaction handler")
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

            if "lift handle" in display_text.lower() and not skip_fueling:
                self.log.info("Dispenser ready fo fueling")
                if not self.fuel_handler(amounts_to_dispense, print_receipt=print_receipt):
                    tc_fail("Something failed while fueling")
                last_display_text = display_text
                display_text = crindsim.get_display_text()
                self.log.info(f"The displey is showing after fueling: {display_text}")

            if not skip_fueling:
                start_time = time.time()
                while last_display_text == display_text and time.time() - start_time <= 60:
                    display_text = crindsim.get_display_text()
                    self.log.info(f"Crind display was not updated yet, it is {display_text}")
                    time.sleep(1)

                if last_display_text == display_text:
                    tc_fail(f"Crind display was not updated during 1 minute, it keeps in {display_text}", exit=True)
                    return False

        # Checking if the dispenser returned to idle or get stuck fueling
        display_text = crindsim.get_display_text()
        self.log.info(f"The Dispenser is showing: {display_text}")
        start_time = time.time()
        while not display_text in idle_screen and time.time() - start_time < timeout:
            if display_text in receipt:
                self.log.info(f"About to hit {print_receipt} in receipt prompt")
                crindsim.press_softkey(f'{print_receipt}')
            self.log.info(f"Waiting for idle, the Dispenser is showing: {display_text}, waiting 1 seconds before retry")
            time.sleep(1)
            display_text = crindsim.get_display_text()

        if not display_text in idle_screen:
            self.log.error(f"The Dispenser is showing: {display_text} after waiting 60 seconds for an update")
            return False
            
        return True

    def dispenser_transaction(self,
                     card="NGFC", 
                     prompts=None, 
                     amounts_to_dispense=None, 
                     messages_to_verify=None, 
                     receipt_data=None, 
                     decline_scenario=False, 
                     inside_receipt='No', 
                     buffer='commercial', 
                     skip_fueling=False,
                     message_types=None,
                     timeout=120):

        try:
            if prompts[self.dispenser_prompts['additional products']]['buttons'][0].lower() == 'yes':

                complete_inside = True
            
            else:
                
                complete_inside = False
                
        except KeyError:
            complete_inside = False
        
        if message_types is None:
        
            message_types = [
                "preauth_request_verifications",
                "preauth_response_verifications",
                "capture_request_verifications",
                "capture_response_verifications"
            ]

        self.pos.wait_disp_ready(idle_timeout=120)

        self.log.info("Set the CRIND in manual mode")
        crindsim.set_mode("manual")

        self.log.debug("Check the last message in the EDH before start")
        last_msg = self.edh.get_last_msg_id(pspid='23')

        self.log.debug("Select dispenser 1")
        self.pos.select_dispenser(1)

        self.log.info(f"Swipe card {card} for brand EXXON")
        swiped = crindsim.swipe_card(card_name=card, brand="EXXON")
        start_time = time.time()
        while not swiped and time.time() - start_time < 60:
            self.log.info(f"Swipe card {card} for brand EXXON")
            swiped = crindsim.swipe_card(card_name=card, brand="EXXON")
        
        if not swiped:
            tc_fail("Was unable to perform swipe outside")

        self.log.info("Checking dispenser display get ready to start")
        display_text = crindsim.get_display_text()
        self.log.info("Dispenser is showing: " + display_text)
        start_time = time.time()
        while display_text == 'INSERT CARD To Pay Here or LIFT HANDLE To Pay Inside' and time.time() - start_time < 60:
            display_text = crindsim.get_display_text()
            self.log.info("Dispenser is showing: " + display_text + ", still wainting dispenser ready")
            
        if display_text == 'INSERT CARD To Pay Here or LIFT HANDLE To Pay Inside':
            tc_fail("Dispenser did not get ready to start transaction, it shows: " + display_text)

        self.log.info(f"Complete the dispenser prompts with {prompts}")
        if not self.crind_transaction_handler(prompts=prompts,
                                             amounts_to_dispense=amounts_to_dispense, 
                                             decline_scenario=decline_scenario, 
                                             skip_fueling=skip_fueling, 
                                             timeout=timeout):
            tc_fail("Something failed while processing the transaction in the dispenser")

        self.pos.wait_for_fuel(1, timeout=120)

        if complete_inside:

            self.log.info("Select Commercial Buffer")
            self.pos.click_fuel_buffer(buffer)

            self.log.info("Select Pay Button")
            self.pos.click_function_key('Pay')
        
            self.log.info(f"Answer {inside_receipt} to Receipt prompt")
            self.pos.click_message_box_key(inside_receipt, timeout=30)

        if not messages_to_verify is None:

            self.log.debug("Try to get 4 messages (preauth and completion)")
            messages = self.edh.get_network_messages(8,start_in=last_msg)
            
            messages_num = len(message_types)

            messages_to_get = messages_num * 2 #for each valid message, concord logs one that we don't care
            
            start_time = time.time()
            while len(messages) < messages_num and (time.time() - start_time < 60):
                self.log.debug("There are messages pending to be generated, retrying to get all of them.")
                messages = self.edh.get_network_messages(messages_to_get,start_in=last_msg)
            if len(messages) < messages_num:
                tc_fail("The messages obtained from the EDH do not contain all requests and responses messages")            

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
                    complete_inside = 'No'
        
        if not receipt_data is None:

            self.pos.check_receipt_for(receipt_data, dispenser= 1, timeout=10)
            
            self.log.debug("Select back to return to idle screen")
            self.pos.click_function_key("Back")

    def prepay_transaction(self, card="NGFC", prepay_amount="$5.00", prompts=None, amounts_to_dispense=None, fixed_product=True, messages_to_verify=None, receipt_data=None, decline_scenario=False, inside_receipt='No', buffer='commercial', items=None, underrun=False):
    
        try:
            if prompts[self.inside_prompts['additional products']]['buttons'][0].lower() == 'yes':

                additional_products = True
            
            else:
                
                additional_products = False
                
        except KeyError:
            additional_products = False

        try:
            fuel_type = prompts[self.inside_prompts['fuel type']]['buttons'][0]

        except KeyError:
            #If it is not provided, we set a default value
            fuel_type = "Tractor fuel."

        try:
            DEF = prompts[self.inside_prompts['DEF']]['buttons'][0]

        except KeyError:
            #If it is not provided, we set a default value
            DEF = "No"
        
        message_types = [
            "preauth_request_verifications",
            "preauth_response_verifications",
            "capture_request_verifications",
            "capture_response_verifications"
        ]

        tc_failed = False
        self.pos.wait_disp_ready(idle_timeout=120)

        self.log.info("Set the CRIND in manual mode")
        crindsim.set_mode("manual")

        self.log.info(f"Add a prepay for {prepay_amount} with fuel type = {fuel_type} and DEF = {DEF}" )
        self.pos.add_fuel(prepay_amount, fuel_type=fuel_type, def_type=DEF)

        self.log.debug("Check the last message in the EDH before start")
        last_msg = self.edh.get_last_msg_id(pspid='23')

        self.log.info(f"Pay with {card} for brand EXXON")
        self.pos.pay_card(brand="Exxon", card_name=card, prompts=prompts)

        self.pos.select_dispenser(1)

        self.log.info(f"Handle Fueling as follow: {amounts_to_dispense}")
        self.fuel_handler(amounts_to_dispense)

        self.pos.wait_for_fuel(1, timeout=120)

        if additional_products or underrun:
            
            if not fixed_product:
                self.log.info("Validate buffer texts using right fuel type.")
                commercial_buffer_texts=self.pos.read_fuel_buffer(buffer)
                self.log.debug(f"The buffers contain {commercial_buffer_texts}")
                for product in amounts_to_dispense:
                    product = product + ' CA'
                    if not product in commercial_buffer_texts:
                        tc_failed = True
                        failure_message  =f"{product} is not in commercial buffer, could mean that product was not dispensed"
                        

            self.log.info("Select Commercial Buffer")
            self.pos.click_fuel_buffer(buffer)
            
            time.sleep(5) #wait for POS screen gets updated
            
            if not fixed_product:
                self.log.info("Validate transaction journal list items with all fuel types.")
                transaction_journal_list = self.pos.read_transaction_journal()
                self.log.debug(f"The transaction journal is {transaction_journal_list}")
                item_in_journal = 0
                for product in amounts_to_dispense:
                    self.log.debug(f"Looking for {product} in {transaction_journal_list}")
                    if not product in transaction_journal_list[item_in_journal]:
                        tc_failed = True
                        failure_message = f"{product} is not in transaction journal, could mean that product was not dispensed"
                        
                    item_in_journal = item_in_journal + 1

            if additional_products:

                if not items is None:

                    for item in items:
                        
                        self.log.info(f"Adding {item}")
                        self.pos.add_item(item=item)

                self.log.info("Select Pay Button")
                self.pos.click_function_key('Pay')            
        
                self.log.info(f"Answer {inside_receipt} to Receipt prompt")            
                if not self.pos.click_message_box_key(inside_receipt, timeout=30):
                    tc_fail("The terminal din't prompt for receipt and it should be doing that")

            if tc_failed:
                tc_fail(failure_message)

        if not messages_to_verify is None:

            self.log.debug("Try to get 4 messages (preauth and completion)")
            messages = self.edh.get_network_messages(8,start_in=last_msg)
            
            start_time = time.time()
            while len(messages) < 4 and (time.time() - start_time < 60):
                self.log.debug("There are messages pending to be generated, retrying to get all of them.")
                messages = self.edh.get_network_messages(8,start_in=last_msg)
            if len(messages) < 4:
                tc_fail("The messages obtained from the EDH do not contain all requests and responses messages")

            messages_num = len(messages_to_verify)

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
                    
                except KeyError as e:
                    tc_fail(f'Failed trying to translate a message: {e}')
        
        if not receipt_data is None:

            self.pos.check_receipt_for(receipt_data, dispenser= 1, timeout=10)

            self.log.debug("Select back to return to idle screen")
            self.pos.click_function_key("Back")

    def get_saf_MaxAmt(self, brand, card, inside = True):
        """
        Retrieve SAFKey and Max amount of transactions allowed in SAF mode for inside or outside
        Args:
            brand(str): brand name to identify the card which is used.
            card(str): the card name to identify the track to be used.
            inside(bool): whether is an outside parameters or inside parameter the ones
                          which will be affected.
        Returns:
            dict: with SAFKey as index and max transaccions limit as value.
        """
        #find the correct ruleskey value
        cardNumber = crindsim._get_card_data(brand=brand, card_name = card)['Track2']
        cardNumber = cardNumber.split('=')
        query = f"select RulesKey from XOM_Bin where beginrange <= left('{cardNumber[0]}', len(BeginRange)) and EndRange >= left('{cardNumber[0]}', len(Endrange)) and Mode = 'C'"
        rulesKeyValue = runas.run_sqlcmd(query, database="network", cmdshell=False)['output']
        rulesKeyValue = rulesKeyValue.split("\n")
        rulesKeyValue = rulesKeyValue[2:-3]
        
        query = f"select SAFKey from XOM_Rules where Ruleskey = '{rulesKeyValue[0]}'"

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

    def get_saf_MaxNum(self, brand, card, inside = True):
        """
        Retrieve SAFKey and MaxNum of transactions allowed in SAF mode for inside or outside
        Args:
            brand(str): brand name to identify the card which is used.
            card(str): the card name to identify the track to be used.
            inside(bool): whether is an outside parameters or inside parameter the ones
                          which will be affected.
        Returns:
            dict: with SAFKey as index and max transaccions limit as value.
        """
        #find the correct ruleskey value
        cardNumber = crindsim._get_card_data(brand=brand, card_name = card)['Track2']
        cardNumber = cardNumber.split('=')
        query = f"select RulesKey from XOM_Bin where beginrange <= left('{cardNumber[0]}', len(BeginRange)) and EndRange >= left('{cardNumber[0]}', len(Endrange)) and Mode = 'C'"
        rulesKeyValue = runas.run_sqlcmd(query, database="network", cmdshell=False)['output']
        rulesKeyValue = rulesKeyValue.split("\n")
        rulesKeyValue = rulesKeyValue[2:-3]
        
        query = f"select SAFKey from XOM_Rules where Ruleskey = '{rulesKeyValue[0]}'"

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

    def set_saf_MaxAmt(self, brand, card, limit, inside = True):
        """
        Set a Max amount of transactions allowed in SAF mode for inside or outside
        Args:
            brand(str): brand name to identify the card which is used.
            card(str): the card name to identify the track to be used.
            limit(str or dict): it depends on whether set or reset values
            inside(bool): whether is an outside parameters or inside parameter the ones
                          which will be affected.
        Returns:
            str: query applying result.
        """
        #find the correct ruleskey value
        cardNumber = crindsim._get_card_data(brand=brand, card_name = card)['Track2']
        cardNumber = cardNumber.split('=')
        query = f"select RulesKey from XOM_Bin where beginrange <= left('{cardNumber[0]}', len(BeginRange)) and EndRange >= left('{cardNumber[0]}', len(Endrange)) and Mode = 'C'"
        rulesKeyValue = runas.run_sqlcmd(query, database="network", cmdshell=False)['output']
        rulesKeyValue = rulesKeyValue.split("\n")
        rulesKeyValue = rulesKeyValue[2:-3]
        
        query = f"select SAFKey from XOM_Rules where Ruleskey = '{rulesKeyValue[0]}'"

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

    def set_saf_MaxNum(self, brand, card, limit, inside = True):
        """
        Set a MaxNum of transactions allowed in SAF mode for inside or outside
        Args:
            brand(str): brand name to identify the card which is used.
            card(str): the card name to identify the track to be us
            limit(str or dict): it depends on whether set or reset values
            inside(bool): whether is an outside parameters or inside parameter the ones
                          which will be affected.
        Returns:
            str: query applying result.
        """
        #find the correct ruleskey value
        cardNumber = crindsim._get_card_data(brand=brand, card_name = card)['Track2']
        cardNumber = cardNumber.split('=')
        query = f"select RulesKey from XOM_Bin where beginrange <= left('{cardNumber[0]}', len(BeginRange)) and EndRange >= left('{cardNumber[0]}', len(Endrange)) and Mode = 'C'"
        rulesKeyValue = runas.run_sqlcmd(query, database="network", cmdshell=False)['output']
        rulesKeyValue = rulesKeyValue.split("\n")
        rulesKeyValue = rulesKeyValue[2:-3]
        
        query = f"select SAFKey from XOM_Rules where Ruleskey = '{rulesKeyValue[0]}'"

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

