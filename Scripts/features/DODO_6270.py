"""
    File name: DODO_6270.py
    Tags: multidispensing, outside sales
    Description: Test scripts meant to verify correct prossesing
    multidispensing transaction outside.
    Author: Javier Sandoval
    Date created: 2020-05-14 14:00:00
    Date last modified: 2020-05-15 13:00:00
    Python Version: 3.7
"""

import logging
from app import Navi, mws, pos, system, forecourt_installation, networksim, crindsim, runas, network_site_config
from app.framework import EDH
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app.features import feature_activation
from Scripts.features import NGFC_Helpers

import time

class DODO_6270():
    """
    Description: Test scripts meant to verify correct prossesing
    multidispensing transaction outside.
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

        # back cash advance to 0
        #self.set_cash_advance_on_mws('000')

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

        # Set Dispenser in auto

        self.log.info("Setting the CRIND in manual mode")
        crindsim.set_mode("Auto")

        #open Browser
        self.pos.connect()
    
    @test
    def Outside_Commercial_3_buffers(self): #3
        """
        For the outside transactions with commercial dispenser,
        it allows up to 3 fuelings in a unic buffer.
        """
        #Input constants

        card_to_use = 'NGFC' # using this card to get all commercial prompts
        #default_dispenser = '1' # we need just one dispenser in this test case
        customer_information = self.customerInfo[0] + (' ' * 14) + self.customerInfo[1] +(' ' * 9) + self.customerInfo[2] + self.customerInfo[3]
        #amounts_to_dispense = [3, 4, 5] #amount to dispense on each fuel, at a multidispensing transaction

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
        
        # Dispenser prompts
        dispenser_prompts = {
            "Make selection":{
                "entry": [""],
                "buttons": ["Both"]
            },
            "Need DEF?":{
                "entry": [""],
                "buttons": ["Yes"]
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
                'Fuel Purchase': '1200',
                'Number of Products': '03',
                'Prod 1 product Amount': '300',
                f'Prod 1 product Code': f'{self.helpers.grade_1_Product}',
                'Prod 2 product Amount': '500',
                f'Prod 2 product Code': f'{self.helpers.grade_1_Product_reefer}',
                'Prod 3 product Amount': '400',
                'Prod 3 product Code': f'{self.helpers.grade_3_Product}',
                '001 - Wex OTR Flags': 'C - Commercial'
            },
            'capture_response_verifications': {
                'Response Code': '0', 
                'Approved Amount': '000001200',
                '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',
                '005 - Wex OTR Customer Information': customer_information
            }
        }

        receipt_data = [f"{self.helpers.grade_1_Name}          3.000G",
                        "PRICE/GAL     $1.000",
                        "FUEL TOTAL   $  3.00",
                        f"{self.helpers.grade_3_Name}       4.000G",
                        "PRICE/GAL     $1.000",
                        "FUEL TOTAL   $  4.00",
                        f"{self.helpers.grade_1_Name_reefer}       5.000G",
                        "PRICE/GAL     $1.000",
                        "FUEL TOTAL   $  5.00",
                        "TOTAL = $  12.00",
                        "CREDIT       $  12.00",
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

        # verify that the information on the receipt is correct to be sure that the transaction
        # was approved and the information generated based on that is correct
        # this validation should be commented since there is an issue about it
        # DODO-6284
        #self.pos.check_receipt_for(receipt_data, dispenser= default_dispenser, timeout=10)
    
    #TODO: Review why this is not failing if it is run manually
    '''
    @test
    def Outside_Commercial_3_buffers_SAF(self): #4
        """
        For the outside transactions with commercial dispenser,
        it allows up to 3 fuelings in a unic buffer, even in a 
        offline transaction.
        """
        #Input constants

        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts
        default_dispenser = '1' # we need just one dispenser in this test case
        customer_information = self.customerInfo[0] + (' ' * 14) + self.customerInfo[1] +(' ' * 9) + self.customerInfo[2] + self.customerInfo[3]
        #amounts_to_dispense = [3, 4, 5] #amount to dispense on each fuel, at a multidispensing transaction
        
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
        
        # Dispenser prompts
        dispenser_prompts = {
            "Make selection":{
                "entry": [""],
                "buttons": ["Both"]
            },
            "Need DEF?":{
                "entry": [""],
                "buttons": ["Yes"]
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

        receipt_data = [f"{self.helpers.grade_1_Name}          3.000G",
                        "PRICE/GAL     $1.000",
                        "FUEL TOTAL   $  3.00",
                        f"{self.helpers.grade_3_Name}       4.000G",
                        "PRICE/GAL     $1.000",
                        "FUEL TOTAL   $  4.00",
                        f"{self.helpers.grade_1_Name_reefer}       5.000G",
                        "PRICE/GAL     $1.000",
                        "FUEL TOTAL   $  5.00",
                        "TOTAL = $  12.00",
                        "CREDIT       $  12.00",
                        "Customer Information",
                        "Name: " + self.customerInfo[0],
                        "City: " + self.customerInfo[1],
                        "State: " + self.customerInfo[2],
                        "Acc.: " + self.customerInfo[3]]
        
        self.preauth_request_verifications = {
            'Fuel Purchase': '5000',
            'Number of Products': '03', #amount of fuel products configured at site.
            'Prod 1 product Code': f'{self.helpers.grade_1_Product}', #first fuel product configured
            'Prod 2 product Code': f'{self.helpers.grade_2_Product}', #second fuel product configured
            'Prod 3 product Code': f'{self.helpers.grade_3_Product}', #third fuel product configured
            '001 - Wex OTR Flags': 'C - Commercial',
            '008 - Wex OTR Cash Advance Limit': '$0.00'#amount of cash advance configured at site
            }
        self.preauth_response_verifications = {
            'Response Code': '2', 
            'Approved Amount': '000005000'              
        }
        self.capture_request_verifications = {
            'Fuel Purchase': '1200',
            'Number of Products': '03',
            'Prod 1 product Amount': '300',
            'Prod 1 product Code': f'{self.helpers.grade_1_Product}',
            'Prod 2 product Amount': '500',
            'Prod 2 product Code': f'{self.helpers.grade_1_Product_reefer}',
            'Prod 3 product Amount': '400',
            'Prod 3 product Code': f'{self.helpers.grade_3_Product}',
            '001 - Wex OTR Flags': 'C - Commercial'
        }
        self.capture_response_verifications = {
            'Response Code': '0', 
            'Approved Amount': '000001200',
            '002 - Wex OTR Non-Fuel Product Data - Product code: MERC (Default category for merchandise)': 'Amount: 30.00',
            '005 - Wex OTR Customer Information': customer_information
        }

        # HostSim Response mode
        networksim.stop_simulator()
        simulator_status = networksim.get_network_status()
        self.log.debug("stop: " + simulator_status["payload"]["status"])
        
        crindsim.set_mode("manual")
        
        

        #find the correct ruleskey value
        cardNumber = crindsim._get_card_data(brand='EXXON', card_name = card_to_use_NGFC)['Track2']
        cardNumber = cardNumber.split('=')
        query = f"select RulesKey from XOM_Bin where beginrange <= left('{cardNumber[0]}', len(BeginRange)) and EndRange >= left('{cardNumber[0]}', len(Endrange)) and Mode = 'C'"
        rulesKeyValue = runas.run_sqlcmd(query, database="network", cmdshell=False)['output']
        rulesKeyValue = rulesKeyValue.split("\n")
        rulesKeyValue = rulesKeyValue[2:-3]

        #set restriction saf key in xom_rules table to have fuel limits
        query = f"Update XOM_Rules set SAFRestrictionKey = 7 where Ruleskey = '{rulesKeyValue[0]}'"
        runas.run_sqlcmd(query, database="network", cmdshell=False)['output']

        # Increse SAF mode transactions limit, to assure that this transaction is approved in offline mode.
        #save previous valued for the amount
        query = f"select SAFKey from XOM_Rules where Ruleskey = '{rulesKeyValue[0]}'"
        MaxAmtList = self.get_saf_MaxAmt(query)
        #apply new value for the amount
        setMaxAmtValue = self.set_saf_MaxAmt(query, '9999.99', inside=False)

        if not setMaxAmtValue.find(f"{len(MaxAmtList)} row"): #validate that new values were applied
            tc_fail('Unable to set max amount limits in XOM_SAF table')
        
        #save previous valued for the number
        MaxNumList = self.get_saf_MaxNum(query)
        #apply new value for the number
        setMaxNumValue = self.set_saf_MaxNum(query, '99', inside=False)

        if not setMaxNumValue.find(f"{len(MaxNumList)} row"): #validate that new values were applied
            tc_fail('Unable to set max num limits in XOM_SAF table')

        #look for the last message before payment so we know the messages involved in the transaction
        last_msg = self.edh.get_last_msg_id(pspid='23')

        self.pos.select_dispenser(1) 

        #Iniciate outside transaction
        crindsim.swipe_card(card_name=card_to_use_NGFC, brand="EXXON")
        
        #Handle crind prompts
        self.helpers.crind_transaction_handler(dispenser_prompts, amounts_to_dispense)
        #crind_prompts_handler(dispenser_prompts, amounts_to_dispense)

        networksim.start_simulator()
        simulator_status = networksim.get_network_status()
        self.log.debug("start: " + simulator_status["payload"]["status"])
        start_time = time.time()
        
        while (simulator_status["payload"]["status"] != 'Online') and (time.time() - start_time < 60):
            simulator_status = networksim.get_network_status()
            self.log.debug(simulator_status["payload"]["status"])
                
        if simulator_status["payload"]["status"] != 'Online':
            tc_fail('Unable to get host simulator online')

        self.pos.select_dispenser(default_dispenser)

        self.pos.wait_for_fuel(default_dispenser, timeout=30)
        
        """ 
         Clarification:
         Get the last 6 messages in the DB after payment. There is 
         some stuff that is not exactly a message and it will be removed,
         just 2 messages are needed: preauth request and response.
        """
        
        self.log.debug("Try to get 1 message (preauth request), since host is unavailable")
        messages = self.edh.get_network_messages(6,start_in=last_msg)
        start_time = time.time()
        while len(messages) != 1 and (time.time() - start_time < 30):
            self.log.debug("There are messages pending to be generated, retrying to get all of them.")
            messages = self.edh.get_network_messages(6,start_in=last_msg)
        if len(messages) != 1:
            tc_fail("The messages obtained from the EDH do not contain preauth requests and responses messages")
        
        ### PREAUTH MESSAGES ###
        self.log.debug("Validation of message # 1, it should be the preauth request")
        msg_translated = self.edh.translate_message(messages[0])

        if msg_translated: # If different of False, it is understood as True
            self.edh.verify_field(msg_translated, self.preauth_request_verifications)
        else:
            tc_fail('Unable to translate the network message')

        #########################

        #look for the last message before payment so we know the messages involved in the transaction
        last_msg = self.edh.get_last_msg_id(pspid='23') 
        """ 
        Clarification:
        Get the last 4 messages in the DB after payment. There is 
        some stuff that is not exactly a message and it will be removed,
        just 2 messages ares needed: completion request and response.
        """
        
        self.log.debug("Try to get 2 messages (completion request and response), after host gets online")
        messages = self.edh.get_network_messages(4,start_in=last_msg)
        start_time = time.time()
        while len(messages) < 2 and (time.time() - start_time < 60):
            self.log.debug("There are messages pending to be generated, retrying to get all of them.")
            messages = self.edh.get_network_messages(4,start_in=last_msg)
        if len(messages) < 2:
            tc_fail("The messages obtained from the EDH do not contain completion requests and responses messages")
    
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


        #reset previous value
        setMaxAmtValue = self.set_saf_MaxAmt(query, MaxAmtList, inside=False)

        if not setMaxAmtValue.find(f"{len(MaxAmtList)} row"): #validate that previous values were applied
            tc_fail('Was unable to reset previous value for total amount limit in XOM_SAF table')
        
        #reset previous value
        setMaxNumValue = self.set_saf_MaxNum(query, MaxNumList, inside=False)

        if not setMaxNumValue.find(f"{len(MaxNumList)} row"): #validate that previous values were applied
            tc_fail('Was unable to reset previous value for total transacions limit in XOM_SAF table')

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

        # verify that the information on the receipt is correct to be sure that the transaction
        # was approved and the information generated based on that is correct
        # this validation should be commented since there is an issue about it
        # DODO-6284
        self.pos.check_receipt_for(receipt_data, dispenser= default_dispenser, timeout=10)
    '''
    
    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """

        self.pos.close()

        networksim.start_simulator()

        #Return the original values
        self.grade_1_Name_reefer = "Diesel 1" #This will be "RD Dsl 1" please update it when changes go mainline
        self.grade_1_Product_reefer = "019" #This will be "032" please update it when changes go mainline

    ### Helpers ###

    
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
    