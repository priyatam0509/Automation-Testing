"""
    File name: DODO_6193.py
    Tags:
    Description: Prompt for cash advance if apply for paper checks based on the site limit
    Author: 
    Date created: 2020-03-06 10:00:56
    Date last modified: 
    Python Version: 3.7
"""

import logging
import time
from app import Navi, mws, pos, system, forecourt_installation
from app import crindsim, networksim, network_site_config
from app.framework import EDH
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app.features import feature_activation, tender
from Scripts.features import NGFC_Helpers

class DODO_6193():
    """
    Description: As Passport, I need to be able to prompt for cash advance if apply for paper checks based on the site limit.
    """

    def __init__(self):
        """
        Initializes the Template class.
        """
        # The logging object. 
        
        self.log = logging.getLogger()

        # The main POS object
        
        self.mws = mws
        
        # The main POS object
        
        self.pos = pos

        # The main EDH object
        self.edh = EDH.EDH()

        self.helpers = NGFC_Helpers.NGFC_Helpers(self.log, self.mws)

        #Input constants 
        self.papercheck_tender_name = 'Paper Check'
        self.papercheck_tender_group = 'Integrated Commercial Check'
        self.papercheck_button_name = 'PAPER CHK'

        # Setting constants

        self.generic_trans_amount = "5.00"
        self.money_code = "0123456789"

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

        networksim.disable_commercial_fuel_limits()
        networksim.disable_product_limits()
        networksim.disable_prompts()

        #Create paper check tender
        self.verify_Paper_Check_Tender_Created()

        # HostSim Response mode
        networksim.set_response_mode("Approval")

        # Crind sim configuration

        crindsim.set_mode("auto")
        crindsim.set_sales_target()
        crindsim.select_grade(1)

        #open Browser
        self.pos.connect()

        self.pos.sign_on()

        self.pos.minimize_pos()    
    
    #TODO: Uncomment when DODO-6294 gets fixed
    @test
    def cash_advance_displayed(self):
        """
        Verify that cash advance is displayed for paper checks
        if cash advance is set with a value above 0
        """
        
        # Setting cash advance with $1.00, any value below the check
        # amount is valid
        nc_info = {
            "Global Information" : {
                "Page 2" :
                        {
                            "Cash Advance Limit": "100"
                        }
                    }
                }
        amounts_to_dispense = {
            "buffer_1":{
                "grade": 1,
                "value": "2"
            },
            "buffer_2":{
                "grade": 2,
                "value": "3"
            }
        }
        
        trans_amount = "$5.00" # any value that gets an approval from the host
        fuel_type = 'Tractor fuel' # is tractor fuel, because is the objective of this testcase
        def_type_yes = 'Yes' # this is "yes",  because is the objective of this testcase                   
        commercial_prompts = {#"Commercial_prompt" is a dictionary in which are the dinamic prompts for commercial diesel
                        "Enter Check Number": {
                            "entry": ["120170"],
                            "buttons": ["Enter"]
                        }, 
                        "Insert Last Name and First Name": {
                            "entry" : ["Juan Jose"],
                            "buttons": ["Ok"]                
                        },
                        "Enter Money Code":{
                            "entry": [self.money_code],
                            "buttons": ["Enter"]
                        },
                        "Cash advance up to $1.00?": {
                            "entry": [""],
                            "buttons": ["Yes"]
                        }
                    }
        #cash_advance_prompt = f"Cash advance up to {trans_amount} Y/N?" # setting as variable to fix easily if it changes
        self.log.info("Setting the CRIND in manual mode")
        crindsim.set_mode("manual")
        
        self.pos.minimize_pos()

        N = network_site_config.NetworkSetup()
        
        self.log.info('Configuring the cash advance with $1.00')
        if not N.configure_network(config=nc_info):
            tc_fail("Failed to configure the Network")

         # Start execution
        self.pos.maximize_pos()

        self.log.info(f"Adding prepay for {trans_amount}")
        self.pos.add_fuel(trans_amount,fuel_type = fuel_type, def_type = def_type_yes)

        # Pay the transaction
        self.log.info("Trying to click Pay")
        if not self.pos.click_function_key('Pay', timeout=10):
            tc_fail("Unable to press Pay button",exit=True)

        # Find requested key
        self.log.info(f"Trying to click {self.papercheck_button_name}")
        if not self.pos.click_tender_key(self.papercheck_button_name):
            tc_fail(f"Unable to click tender {self.papercheck_button_name}",exit=True)

        self.log.info(f"Attempting to handle commercial prompts: the provided prompts are {commercial_prompts}")
        if not self.pos.commercial_prompts_handler(prompts= commercial_prompts):
            tc_fail(f"Unable to handle the following commercial prompts {commercial_prompts}")

        # Get prompts

        msg = self.pos.read_processing_text(timeout=10)
        self.log.debug(f"The processing text is: {msg}")

        # Check for popup about cancellation
        if msg != "Enter cash advance amount":

            tc_fail("Cash advance prompt was not displayed",exit=True)

        self.log.info("Select cancel button")
        self.pos.click_keypad('cancel')

        """
        self.log.info("Select Ok button")
        self.pos.click_message_box_key("Ok")
        
        self.log.info("Select cancel to back to the idle screen")
        self.pos.click_keypad('cancel')
        
        self.log.info("Completing the transaction with cash")
        self.pos.pay()
        """
        self.pos.select_dispenser(1)

        self.helpers.fuel_handler(amounts_to_dispense)

        self.pos.wait_for_fuel(timeout=120)

        self.pos.click_function_key("Back")
    
    @test
    def cash_advance_not_displayed(self):
        """
        Verify that cash advance isn't displayed for paper checks if cash advance is set with  0
        """

        # Setting cash advance with $0.00, any so it doesn't prompt for cash advance

        nc_info = {
            "Global Information" : {
                "Page 2" :
                        {
                            "Cash Advance Limit": "000"
                        }
                    }
                }
        
        trans_amount = "$5.00" # any value that gets an approval from the host
        fuel_type = 'Tractor fuel' # is tractor fuel, because is the objective of this testcase
        def_type_yes = 'Yes' # this is "yes",  because is the objective of this testcase        
        amounts_to_dispense = {
            "buffer_1":{
                "grade": 1,
                "value": "2"
            },
            "buffer_2":{
                "grade": 2,
                "value": "3"
            }
        }    
        commercial_prompts = {#"Commercial_prompt" is a dictionary in which are the dinamic prompts for commercial diesel
                        "Enter Check Number": {
                            "entry": ["120170"],
                            "buttons": ["Enter"]
                        }, 
                        "Insert Last Name and First Name": {
                            "entry" : ["Juan Jose"],
                            "buttons": ["Ok"]                
                        },
                        "Enter Money Code":{
                            "entry": [self.money_code],
                            "buttons": ["Enter"]
                        }
                    }
        self.log.info("Setting the CRIND in manual mode")
        crindsim.set_mode("manual")

        self.pos.minimize_pos()

        N = network_site_config.NetworkSetup()
        
        self.log.info('Configuring the cash advance with $0.00')

        if not N.configure_network(config=nc_info):
            tc_fail("Failed to configure the Network")

         # Start execution
        self.pos.maximize_pos()

        self.pos.wait_disp_ready()

        self.log.info(f"Adding prepay for {trans_amount}")
        self.pos.add_fuel(trans_amount,fuel_type = fuel_type, def_type = def_type_yes)

        # Pay the transaction 
        self.log.info("About to Pay the transaction")
        self.pos.pay(tender_type=self.papercheck_button_name, prompts=commercial_prompts)
        
        self.pos.select_dispenser(1)

        self.log.info(f"About to handle fueling for {amounts_to_dispense}")
        self.helpers.fuel_handler(amounts_to_dispense)
        
        self.log.info("Waiting for prepay to complte so the next test case does not start ahead of time")
        
        self.pos.wait_for_fuel(timeout=120)
        self.pos.click_function_key("Back")
       
    '''
    #TODO: Complete this test case when pinpad be able to handle cash advance prompt
    @test
    def cash_advance_exceeded(self):
        """
        Verify that the POS informs if the cash advance limit is exceeded
        and prompts again for it
        """
        #Input constants

        # Setting cash advance with $1.00, any so it doesn't prompt for cash advance

        cash_advance_limit = "1.00"

        nc_info = {
            "Global Information" : {
                "Page 2" :
                        {
                            "Cash Advance Limit": cash_advance_limit
                        }
                    }
                }
        
        trans_amount = "$5.00" # any value that gets an approval from the host
        fuel_type = 'Tractor fuel' # is tractor fuel, because is the objective of this testcase
        def_type_yes = 'Yes' # this is "yes",  because is the objective of this testcase                
        cash_advance_prompt = f"Cash advance up to {cash_advance_limit} Y/N?" # setting as variable to fix easily if it changes
        
        commercial_prompts = {#"Commercial_prompt" is a dictionary in which are the dinamic prompts for commercial diesel
                        "Enter Check Number": {
                            "entry": ["120170"],
                            "buttons": ["Enter"]
                        }, 
                        "Insert Last Name and First Name": {
                            "entry" : ["Juan Jose"],
                            "buttons": ["Ok"]                
                        },
                        cash_advance_prompt : {
                            "entry": ["500", cash_advance_limit],
                            "buttons": ["Ok", "Ok"] 
                        },
                        "Enter Money Code":{
                            "entry": [self.money_code],
                            "buttons": ["Enter"]
                        }
                    }
        
        invalid_entry_prompt = "Invalid entry"
            
        N = network_site_config.NetworkSetup()
        
        self.log.debug('Configuring the cash advance with $1.00')

        if not N.configure_network(config=nc_info):
            tc_fail("Failed to configure the Network")

         # Start execution
        
        self.log.info(f"Adding prepay for {trans_amount}")

        self.pos.add_fuel(trans_amount,fuel_type = fuel_type, def_type = def_type_yes)

        # Pay the transaction
        self.log.logger.debug("Trying to click Pay")
        if not self.pos.click_function_key('Pay'):
            tc_fail("Unable to press Pay button",exit=True)

        # Find requested key
        self.log.logger.debug(f"Trying to click {self.papercheck_button_name}")
        if not self.pos.click_tender_key(self.papercheck_button_name):
            tc_fail(f"Unable to click tender {self.papercheck_button_name}",exit=True)

        #We handle just check number and Name so we can validate that cash advance is prompted
        self.pos.commercial_prompts_handler(prompts= commercial_prompts)

        # Get prompts

        msg = self.pos.read_message_box()
        
        # Check for popup about cancellation
        if msg == invalid_entry_prompt:

            # Accept prompt

            self.pos.click_message_box_key("Ok")

            # Calling again commercial prompts handler so we use the second value set
            # for cash advance

            self.pos.commercial_prompts_handler(prompts= commercial_prompts)

        else: 
            # Handels the scenario where we get the prompt for addition product
            # or any other promt
            tc_fail(f"Unexpected prompt prompt was displayed: {msg}",exit=True)
    '''
    #TODO: Uncomment when DODO-6566 gets fixed
    '''
    @test
    def paper_check_time_out(self):
        """
        Verify that if a paper check transaction time out it is declined
        """
        # Set the host sim to time out

        networksim.set_response_mode("Timeout")

        # Setting cash advance with $0.00 so it doesn't prompt for cash advance

        nc_info = {
            "Global Information" : {
                "Page 2" :
                        {
                            "Cash Advance Limit": "000"
                        }
                    }
                }
        
        trans_amount = "$5.00" # any value that gets an approval from the host
        fuel_type = 'Tractor fuel' # is tractor fuel, because is the objective of this testcase
        def_type_yes = 'Yes' # this is "yes",  because is the objective of this testcase                
        amounts_to_dispense = {
            "buffer_1":{
                "grade": 1,
                "value": "2"
            },
            "buffer_2":{
                "grade": 2,
                "value": "3"
            }
        }
        commercial_prompts = {#"Commercial_prompt" is a dictionary in which are the dinamic prompts for commercial diesel
                        "Enter Check Number": {
                            "entry": ["120170"],
                            "buttons": ["Enter"]
                        },
                        "Enter Money Code":{
                            "entry": [self.money_code],
                            "buttons": ["Enter"]
                        }
                    }
        
        #cash_advance_prompt = f"Cash advance up to {trans_amount} Y/N?" # setting as variable to fix easily if it changes
        self.pos.minimize_pos()

        crindsim.set_mode("manual")
         
        N = network_site_config.NetworkSetup()
        
        self.log.debug('Configuring the cash advance with $0.00')

        if not N.configure_network(config=nc_info):
            tc_fail("Failed to configure the Network")
        
        self.pos.maximize_pos()
		
        self.log.info(f"Adding prepay for {trans_amount}")
        self.pos.add_fuel(trans_amount,fuel_type = fuel_type, def_type = def_type_yes)

        

        # Pay the transaction
        self.log.info("Trying to click Pay")
        if not self.pos.click_function_key('Pay'):
            tc_fail("Unable to press Pay button",exit=True)
        
        # Find requested key
        self.log.info(f"Trying to click {self.papercheck_button_name}")
        if not self.pos.click_tender_key(self.papercheck_button_name):
            tc_fail(f"Unable to click tender {self.papercheck_button_name}",exit=True)

        #We handle just check number and Name so we can validate that cash advance is prompted
        if not self.pos.commercial_prompts_handler(prompts= commercial_prompts):

            tc_fail(f"Unable to handle the following commercial prompts {commercial_prompts}")

        msg = self.pos.read_message_box(timeout=60) #Network time out is around 40 seconds

        self.log.debug(f"The prompt message displayed is {msg}")
        
        # Check for popup about cancellation
        if msg != "No Response from the Host. Please Try Again":

            tc_fail("Pop up Time Out Host was not displayed",exit=True)

        self.pos.click_message_box_key("Ok")
        
        self.log.info("Select cancel to back to the idle screen")
        self.pos.click_keypad('cancel')
        
        self.log.info("Completing the transaction with cash")
        self.pos.pay()

        self.log.info(f"About to handle fueling for {amounts_to_dispense}")
        self.helpers.fuel_handler(amounts_to_dispense)

        self.pos.wait_for_fuel(timeout=60)

        self.pos.click_function_key("Back")
    '''  
    @test
    def paper_check_no_connection(self):
        """
        Verify that a paper check transaction is declined if there is
        no connection with the host
        """
        # Set the host sim to time out

        networksim.stop_simulator()

        # Setting cash advance with $0.00 so it doesn't prompt for cash advance

        nc_info = {
            "Global Information" : {
                "Page 2" :
                        {
                            "Cash Advance Limit": "000"
                        }
                    }
                }
        
        trans_amount = "$5.00" # any value that gets an approval from the host
        fuel_type = 'Tractor fuel' # is tractor fuel, because is the objective of this testcase
        def_type_yes = 'Yes' # this is "yes",  because is the objective of this testcase                
        amounts_to_dispense = {
            "buffer_1":{
                "grade": 1,
                "value": "2"
            },
            "buffer_2":{
                "grade": 2,
                "value": "3"
            }
        }
        commercial_prompts = {#"Commercial_prompt" is a dictionary in which are the dinamic prompts for commercial diesel
                        "Enter Check Number": {
                            "entry": ["120170"],
                            "buttons": ["Enter"]
                        }, 
                        "Communication Failure. Please Try Again": {
                            "entry" : [""],
                            "buttons": ["Ok"]                
                        },
                        "Enter Money Code":{
                            "entry": [self.money_code],
                            "buttons": ["Enter"]
                        }
                    }

        self.log.info("Setting the CRIND in manual mode")
        crindsim.set_mode("manual")
                
        self.pos.minimize_pos()
         
        N = network_site_config.NetworkSetup()
        
        self.log.debug('Configuring the cash advance with $0.00')

        if not N.configure_network(config=nc_info):
            tc_fail("Failed to configure the Network")
        
        self.pos.maximize_pos()
		
        self.pos.add_fuel(trans_amount,fuel_type = fuel_type, def_type = def_type_yes)

        # Pay the transaction
        self.log.debug("Trying to click Pay")
        if not self.pos.click_function_key('Pay'):
            tc_fail("Unable to press Pay button",exit=True)
        
        # Find requested key
        self.log.debug(f"Trying to click {self.papercheck_button_name}")
        if not self.pos.click_tender_key(self.papercheck_button_name):
            tc_fail(f"Unable to click tender {self.papercheck_button_name}",exit=True)

        #We handle just check number and Name so we can validate that cash advance is prompted
        self.pos.commercial_prompts_handler(prompts= commercial_prompts)

        self.log.info("Select cancel to back to the idle screen")
        self.pos.click_keypad('cancel')
        
        self.log.info("Completing the transaction with cash")
        self.pos.pay()

        self.pos.select_dispenser(1)

        self.log.info(f"About to handle fueling for {amounts_to_dispense}")
        self.helpers.fuel_handler(amounts_to_dispense)

        self.pos.wait_for_fuel(timeout=60)

        self.pos.click_function_key("Back")
        
    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        self.pos.close()

        networksim.start_simulator()

        networksim.set_response_mode("Approval")

    ### Helpers ###

    def verify_Paper_Check_Tender_Created(self):
        """
        it verifies if paper check tender is already created, if not, it creates it.
        """
        
        tender_info = {
                "Tender Code": "1234",
                "Tender Description": self.papercheck_tender_name,
                "General": {
                    "Tender group this tender belongs to": self.papercheck_tender_group,
                    "Receipt Description": self.papercheck_tender_name,
                    "Tender Button Description": self.papercheck_button_name,
                    "NACS Tender Code": "generic"
                },
                "Currency And Denominations": {
                    "Currency": "US Dollars"
                },
                "Functions": {
                    "Sale": {
                        "Show exact amount button": True,
                        "Show next highest button": True,
                    }  
                },
                "Min/Max": {
                    "Minimum Allowed": "0.00",
                    "Maximum Allowed": "100.00",
                    "Repeated Use Limit": "5",
                    "Maximum Refund": "25.00",
                    "Primary tender for change": "Cash",
                    "Maximum primary change allowed": "100000.00",
                    "Secondary tender for change": "Cash"
                },
                "Register Groups": {
                    "POSGroup1": {
                        "Sales": True
                    }
                }
            }
        
        # tender maintenance configuration for paper check
        Navi.navigate_to("tender maintenance")

        # Check to see if tender to add already exists...
        if mws.set_value("Tenders", self.papercheck_tender_name):
            mws.click_toolbar('Exit')
            return True
        else:
            self.log.debug(f"Adding {self.papercheck_tender_name}, since it was not created previously.")
            
            # tender maintenance configuration for paper check
            tm = tender.TenderMaintenance()
            tm.configure(self.papercheck_tender_name, tender_info, True)
            mws.click_toolbar('Exit')

    