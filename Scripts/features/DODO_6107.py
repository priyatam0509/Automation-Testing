"""
    File name: DODO_6107.py
    Tags:
    Description: Handle the new decline codes for the NGFC cards transactions
    Author: 
    Date created: 2020-05-25 21:12:17
    Date last modified: 
    Python Version: 3.7
"""

import logging
import time
from app import Navi, mws, pos, system, forecourt_installation, networksim, crindsim
from app import network_site_config
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app.features import feature_activation


class DODO_6107():
    """
    As Passport, I need to handle the new decline codes for the NGFC cards transactions.
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

    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        """
        #Commercial feature activation
        #self.Commercial_feature_activation()

        #Commercial Diesel checkbox activation in forecourt installation 
        #self.set_commercial_on_forecourt()

        # back cash advance to 0
        self.set_cash_advance_on_mws('000')

        # Disable all promtps
        networksim.disable_commercial_fuel_limits()
        networksim.disable_product_limits()
        networksim.disable_prompts()

        # Set host simulator in Approval mode
        networksim.set_response_mode("Approval")

        # Set Dispenser in auto

        crindsim.set_mode("auto")
        crindsim.set_sales_target()

        #open Browser
        self.pos.connect()

        self.pos.sign_on()

        self.pos.maximize_pos()        
    
    '''
    @test
    def DODO_6107_1_Prepay_D1(self):
        """
        In a prepay transaction with the D1 response mode, the decline messages are shown to the cashier in the yellow bar at the POS
        """
        generic_trans_amount = "$5.00" # any value that gets an approval from the host
        tractor_fuel_type = 'Both fuels' 
        def_type_yes = 'No' 
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts        
        Host_sim_mode = "D1" #the scripts is about new response code, we are testing all of them
        decline_message = ".INV MERCHANT D1." #expected message given the host sim mode
        commercial_prompts = {              
                            "Additional Products Y/N?": {                    
                                "buttons": ["No"]
                            },
                            "Do you want to print a receipt?": {
                                "buttons": ["No"]
                            }
                        }

        execute = self.prepay_declineCode_validation(Host_sim_mode, generic_trans_amount, tractor_fuel_type, def_type_yes, card_to_use_NGFC, commercial_prompts, decline_message)
        
        if not execute[0]:
            tc_fail(execute[1])
        
    @test
    def DODO_6107_2_Prepay_D2(self):
        """
        In a prepay transaction with the D2 response mode, the decline messages are shown to the cashier in the yellow bar at the POS
        """
        generic_trans_amount = "$5.00" # any value that gets an approval from the host
        tractor_fuel_type = 'Both fuels' 
        def_type_yes = 'No' 
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts        
        Host_sim_mode = "D2" #the scripts is about new response code, we are testing all of them
        decline_message = '.INVALID CARD D2.' #expected message given the host sim mode
        commercial_prompts = {              
                            "Additional Products Y/N?": {                    
                                "buttons": ["No"]
                            },
                            "Do you want to print a receipt?": {
                                "buttons": ["No"]
                            }
                        }

        execute = self.prepay_declineCode_validation(Host_sim_mode, generic_trans_amount, tractor_fuel_type, def_type_yes, card_to_use_NGFC, commercial_prompts, decline_message)
        
        if not execute[0]:
            tc_fail(execute[1])

    @test
    def DODO_6107_3_Prepay_D3(self):
        """
        In a prepay transaction with the D3 response mode, the decline messages are shown to the cashier in the yellow bar at the POS
        """
        generic_trans_amount = "$5.00" # any value that gets an approval from the host
        tractor_fuel_type = 'Both fuels' 
        def_type_yes = 'No' 
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts        
        Host_sim_mode = "D3" #the scripts is about new response code, we are testing all of them
        decline_message = '.INV EXP DATE D3.' #expected message given the host sim mode
        commercial_prompts = {              
                            "Additional Products Y/N?": {                    
                                "buttons": ["No"]
                            },
                            "Do you want to print a receipt?": {
                                "buttons": ["No"]
                            }
                        }

        execute = self.prepay_declineCode_validation(Host_sim_mode, generic_trans_amount, tractor_fuel_type, def_type_yes, card_to_use_NGFC, commercial_prompts, decline_message)
        
        if not execute[0]:
            tc_fail(execute[1])
        
    @test
    def DODO_6107_4_Prepay_D4(self):
        """
        In a prepay transaction with the D4 response mode, the decline messages are shown to the cashier in the yellow bar at the POS
        """
        generic_trans_amount = "$5.00" # any value that gets an approval from the host
        tractor_fuel_type = 'Both fuels' 
        def_type_yes = 'No' 
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts        
        Host_sim_mode = "D4" #the scripts is about new response code, we are testing all of them
        decline_message = '.DUPLICATE D4.' #expected message given the host sim mode
        commercial_prompts = {              
                            "Additional Products Y/N?": {                    
                                "buttons": ["No"]
                            },
                            "Do you want to print a receipt?": {
                                "buttons": ["No"]
                            }
                        }

        execute = self.prepay_declineCode_validation(Host_sim_mode, generic_trans_amount, tractor_fuel_type, def_type_yes, card_to_use_NGFC, commercial_prompts, decline_message)
        
        if not execute[0]:
            tc_fail(execute[1])

    @test
    def DODO_6107_5_Prepay_D5(self):
        """
        In a prepay transaction with the D5 response mode, the decline messages are shown to the cashier in the yellow bar at the POS
        """
        generic_trans_amount = "$5.00" # any value that gets an approval from the host
        tractor_fuel_type = 'Both fuels' 
        def_type_yes = 'No' 
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts        
        Host_sim_mode = "D5" #the scripts is about new response code, we are testing all of them
        decline_message = '.INV CURRENCY D5.' #expected message given the host sim mode
        commercial_prompts = {              
                            "Additional Products Y/N?": {                    
                                "buttons": ["No"]
                            },
                            "Do you want to print a receipt?": {
                                "buttons": ["No"]
                            }
                        }

        execute = self.prepay_declineCode_validation(Host_sim_mode, generic_trans_amount, tractor_fuel_type, def_type_yes, card_to_use_NGFC, commercial_prompts, decline_message)
        
        if not execute[0]:
            tc_fail(execute[1])

    @test
    def DODO_6107_6_Prepay_D6(self):
        """
        In a prepay transaction with the D6 response mode, the decline messages are shown to the cashier in the yellow bar at the POS
        """
        generic_trans_amount = "$5.00" # any value that gets an approval from the host
        tractor_fuel_type = 'Both fuels' 
        def_type_yes = 'No' 
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts        
        Host_sim_mode = "D6" #the scripts is about new response code, we are testing all of them
        decline_message = '.INV COUNTRY D6.' #expected message given the host sim mode
        commercial_prompts = {              
                            "Additional Products Y/N?": {                    
                                "buttons": ["No"]
                            },
                            "Do you want to print a receipt?": {
                                "buttons": ["No"]
                            }
                        }

        execute = self.prepay_declineCode_validation(Host_sim_mode, generic_trans_amount, tractor_fuel_type, def_type_yes, card_to_use_NGFC, commercial_prompts, decline_message)
        
        if not execute[0]:
            tc_fail(execute[1])

    @test
    def DODO_6107_7_Prepay_D8(self):
        """
        In a prepay transaction with the D8 response mode, the decline messages are shown to the cashier in the yellow bar at the POS
        """
        generic_trans_amount = "$5.00" # any value that gets an approval from the host
        tractor_fuel_type = 'Both fuels' 
        def_type_yes = 'No' 
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts        
        Host_sim_mode = "D8" #the scripts is about new response code, we are testing all of them
        decline_message = '.INV PRODUCT D8.' #expected message given the host sim mode
        commercial_prompts = {              
                            "Additional Products Y/N?": {                    
                                "buttons": ["No"]
                            },
                            "Do you want to print a receipt?": {
                                "buttons": ["No"]
                            }
                        }

        execute = self.prepay_declineCode_validation(Host_sim_mode, generic_trans_amount, tractor_fuel_type, def_type_yes, card_to_use_NGFC, commercial_prompts, decline_message)
        
        if not execute[0]:
            tc_fail(execute[1])
    
    @test
    def DODO_6107_8_Prepay_D9(self):
        """
        In a prepay transaction with the D9 response mode, the decline messages are shown to the cashier in the yellow bar at the POS
        """
        generic_trans_amount = "$5.00" # any value that gets an approval from the host
        tractor_fuel_type = 'Both fuels' 
        def_type_yes = 'No' 
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts        
        Host_sim_mode = "D9" #the scripts is about new response code, we are testing all of them
        decline_message = '.OVER PROD LIM D9.' #expected message given the host sim mode
        commercial_prompts = {              
                            "Additional Products Y/N?": {                    
                                "buttons": ["No"]
                            },
                            "Do you want to print a receipt?": {
                                "buttons": ["No"]
                            }
                        }

        execute = self.prepay_declineCode_validation(Host_sim_mode, generic_trans_amount, tractor_fuel_type, def_type_yes, card_to_use_NGFC, commercial_prompts, decline_message)
        
        if not execute[0]:
            tc_fail(execute[1])
    
    @test
    def DODO_6107_9_Prepay_DA(self):
        """
        In a prepay transaction with the DA response mode, the decline messages are shown to the cashier in the yellow bar at the POS
        """
        generic_trans_amount = "$5.00" # any value that gets an approval from the host
        tractor_fuel_type = 'Both fuels' 
        def_type_yes = 'No' 
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts        
        Host_sim_mode = "DA" #the scripts is about new response code, we are testing all of them
        decline_message = '.INV TRANS DA.' #expected message given the host sim mode
        commercial_prompts = {              
                            "Additional Products Y/N?": {                    
                                "buttons": ["No"]
                            },
                            "Do you want to print a receipt?": {
                                "buttons": ["No"]
                            }
                        }

        execute = self.prepay_declineCode_validation(Host_sim_mode, generic_trans_amount, tractor_fuel_type, def_type_yes, card_to_use_NGFC, commercial_prompts, decline_message)
        
        if not execute[0]:
            tc_fail(execute[1])

    @test
    def DODO_6107_10_Prepay_DB(self):
        """
        In a prepay transaction with the DB response mode, the decline messages are shown to the cashier in the yellow bar at the POS
        """
        generic_trans_amount = "$5.00" # any value that gets an approval from the host
        tractor_fuel_type = 'Both fuels' 
        def_type_yes = 'No' 
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts        
        Host_sim_mode = "DB" #the scripts is about new response code, we are testing all of them
        decline_message = '.INV FUEL TYP DB.' #expected message given the host sim mode
        commercial_prompts = {              
                            "Additional Products Y/N?": {                    
                                "buttons": ["No"]
                            },
                            "Do you want to print a receipt?": {
                                "buttons": ["No"]
                            }
                        }

        execute = self.prepay_declineCode_validation(Host_sim_mode, generic_trans_amount, tractor_fuel_type, def_type_yes, card_to_use_NGFC, commercial_prompts, decline_message)
        
        if not execute[0]:
            tc_fail(execute[1])

    @test
    def DODO_6107_11_Prepay_DC(self):
        """
        In a prepay transaction with the DC response mode, the decline messages are shown to the cashier in the yellow bar at the POS
        """
        generic_trans_amount = "$5.00" # any value that gets an approval from the host
        tractor_fuel_type = 'Both fuels' 
        def_type_yes = 'No' 
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts        
        Host_sim_mode = "DC" #the scripts is about new response code, we are testing all of them
        decline_message = '.INV FUEL USE DC.' #expected message given the host sim mode
        commercial_prompts = {              
                            "Additional Products Y/N?": {                    
                                "buttons": ["No"]
                            },
                            "Do you want to print a receipt?": {
                                "buttons": ["No"]
                            }
                        }

        execute = self.prepay_declineCode_validation(Host_sim_mode, generic_trans_amount, tractor_fuel_type, def_type_yes, card_to_use_NGFC, commercial_prompts, decline_message)
        
        if not execute[0]:
            tc_fail(execute[1])

    @test
    def DODO_6107_12_Prepay_DD(self):
        """
        In a prepay transaction with the DD response mode, the decline messages are shown to the cashier in the yellow bar at the POS
        """
        generic_trans_amount = "$5.00" # any value that gets an approval from the host
        tractor_fuel_type = 'Both fuels' 
        def_type_yes = 'No' 
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts        
        Host_sim_mode = "DD" #the scripts is about new response code, we are testing all of them
        decline_message = '.INV FUEL SRV DD.' #expected message given the host sim mode
        commercial_prompts = {              
                            "Additional Products Y/N?": {                    
                                "buttons": ["No"]
                            },
                            "Do you want to print a receipt?": {
                                "buttons": ["No"]
                            }
                        }

        execute = self.prepay_declineCode_validation(Host_sim_mode, generic_trans_amount, tractor_fuel_type, def_type_yes, card_to_use_NGFC, commercial_prompts, decline_message)
        
        if not execute[0]:
            tc_fail(execute[1])

    @test
    def DODO_6107_13_Prepay_DE(self):
        """
        In a prepay transaction with the DE response mode, the decline messages are shown to the cashier in the yellow bar at the POS
        """
        generic_trans_amount = "$5.00" # any value that gets an approval from the host
        tractor_fuel_type = 'Both fuels' 
        def_type_yes = 'No' 
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts        
        Host_sim_mode = "DE" #the scripts is about new response code, we are testing all of them
        decline_message = '.OVER FUEL LIM DE.' #expected message given the host sim mode
        commercial_prompts = {              
                            "Additional Products Y/N?": {                    
                                "buttons": ["No"]
                            },
                            "Do you want to print a receipt?": {
                                "buttons": ["No"]
                            }
                        }

        execute = self.prepay_declineCode_validation(Host_sim_mode, generic_trans_amount, tractor_fuel_type, def_type_yes, card_to_use_NGFC, commercial_prompts, decline_message)
        
        if not execute[0]:
            tc_fail(execute[1])

    @test
    def DODO_6107_14_Prepay_DF(self):
        """
        In a prepay transaction with the DF response mode, the decline messages are shown to the cashier in the yellow bar at the POS
        """
        generic_trans_amount = "$5.00" # any value that gets an approval from the host
        tractor_fuel_type = 'Both fuels' 
        def_type_yes = 'No' 
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts        
        Host_sim_mode = "DF" #the scripts is about new response code, we are testing all of them
        decline_message = '.OVER LIMIT DF.' #expected message given the host sim mode
        commercial_prompts = {              
                            "Additional Products Y/N?": {                    
                                "buttons": ["No"]
                            },
                            "Do you want to print a receipt?": {
                                "buttons": ["No"]
                            }
                        }

        execute = self.prepay_declineCode_validation(Host_sim_mode, generic_trans_amount, tractor_fuel_type, def_type_yes, card_to_use_NGFC, commercial_prompts, decline_message)
        
        if not execute[0]:
            tc_fail(execute[1])

    @test
    def DODO_6107_15_Prepay_DG(self):
        """
        In a prepay transaction with the DG response mode, the decline messages are shown to the cashier in the yellow bar at the POS
        """
        generic_trans_amount = "$5.00" # any value that gets an approval from the host
        tractor_fuel_type = 'Both fuels' 
        def_type_yes = 'No' 
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts        
        Host_sim_mode = "DG" #the scripts is about new response code, we are testing all of them
        decline_message = '.NO AUTH FOUND DG.' #expected message given the host sim mode
        commercial_prompts = {              
                            "Additional Products Y/N?": {                    
                                "buttons": ["No"]
                            },
                            "Do you want to print a receipt?": {
                                "buttons": ["No"]
                            }
                        }

        execute = self.prepay_declineCode_validation(Host_sim_mode, generic_trans_amount, tractor_fuel_type, def_type_yes, card_to_use_NGFC, commercial_prompts, decline_message)
        
        if not execute[0]:
            tc_fail(execute[1])

    @test
    def DODO_6107_16_Prepay_DH(self):
        """
        In a prepay transaction with the DH response mode, the decline messages are shown to the cashier in the yellow bar at the POS
        """
        generic_trans_amount = "$5.00" # any value that gets an approval from the host
        tractor_fuel_type = 'Both fuels' 
        def_type_yes = 'No' 
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts        
        Host_sim_mode = "DH" #the scripts is about new response code, we are testing all of them
        decline_message = '.LATE VOID DH.' #expected message given the host sim mode
        commercial_prompts = {              
                            "Additional Products Y/N?": {                    
                                "buttons": ["No"]
                            },
                            "Do you want to print a receipt?": {
                                "buttons": ["No"]
                            }
                        }

        execute = self.prepay_declineCode_validation(Host_sim_mode, generic_trans_amount, tractor_fuel_type, def_type_yes, card_to_use_NGFC, commercial_prompts, decline_message)
        
        if not execute[0]:
            tc_fail(execute[1])

    @test
    def DODO_6107_17_Prepay_DI(self):
        """
        In a prepay transaction with the DI response mode, the decline messages are shown to the cashier in the yellow bar at the POS
        """
        generic_trans_amount = "$5.00" # any value that gets an approval from the host
        tractor_fuel_type = 'Both fuels' 
        def_type_yes = 'No' 
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts        
        Host_sim_mode = "DI" #the scripts is about new response code, we are testing all of them
        decline_message = '.OVER LIMIT DI.' #expected message given the host sim mode
        commercial_prompts = {              
                            "Additional Products Y/N?": {                    
                                "buttons": ["No"]
                            },
                            "Do you want to print a receipt?": {
                                "buttons": ["No"]
                            }
                        }

        execute = self.prepay_declineCode_validation(Host_sim_mode, generic_trans_amount, tractor_fuel_type, def_type_yes, card_to_use_NGFC, commercial_prompts, decline_message)
        
        if not execute[0]:
            tc_fail(execute[1])

    @test
    def DODO_6107_18_Prepay_DJ(self):
        """
        In a prepay transaction with the DJ response mode, the decline messages are shown to the cashier in the yellow bar at the POS
        """
        generic_trans_amount = "$5.00" # any value that gets an approval from the host
        tractor_fuel_type = 'Both fuels' 
        def_type_yes = 'No' 
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts        
        Host_sim_mode = "DJ" #the scripts is about new response code, we are testing all of them
        decline_message = '.OVER LIMIT DJ.' #expected message given the host sim mode
        commercial_prompts = {              
                            "Additional Products Y/N?": {                    
                                "buttons": ["No"]
                            },
                            "Do you want to print a receipt?": {
                                "buttons": ["No"]
                            }
                        }

        execute = self.prepay_declineCode_validation(Host_sim_mode, generic_trans_amount, tractor_fuel_type, def_type_yes, card_to_use_NGFC, commercial_prompts, decline_message)
        
        if not execute[0]:
            tc_fail(execute[1])
    
    @test
    def DODO_6107_19_Prepay_DK(self):
        """
        In a prepay transaction with the DK response mode, the decline messages are shown to the cashier in the yellow bar at the POS
        """
        generic_trans_amount = "$5.00" # any value that gets an approval from the host
        tractor_fuel_type = 'Both fuels' 
        def_type_yes = 'No' 
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts        
        Host_sim_mode = "DK" #the scripts is about new response code, we are testing all of them
        decline_message = '.ACCT IN USE DK.' #expected message given the host sim mode
        commercial_prompts = {              
                            "Additional Products Y/N?": {                    
                                "buttons": ["No"]
                            },
                            "Do you want to print a receipt?": {
                                "buttons": ["No"]
                            }
                        }

        execute = self.prepay_declineCode_validation(Host_sim_mode, generic_trans_amount, tractor_fuel_type, def_type_yes, card_to_use_NGFC, commercial_prompts, decline_message)
        
        if not execute[0]:
            tc_fail(execute[1])
    
    @test
    def DODO_6107_20_Prepay_DL(self):
        """
        In a prepay transaction with the DK response mode, the decline messages are shown to the cashier in the yellow bar at the POS
        """
        generic_trans_amount = "$5.00" # any value that gets an approval from the host
        tractor_fuel_type = 'Both fuels' 
        def_type_yes = 'No' 
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts        
        Host_sim_mode = "DL" #the scripts is about new response code, we are testing all of them
        decline_message = '.NO DYED CERT DL.' #expected message given the host sim mode
        commercial_prompts = {              
                            "Additional Products Y/N?": {                    
                                "buttons": ["No"]
                            },
                            "Do you want to print a receipt?": {
                                "buttons": ["No"]
                            }
                        }

        execute = self.prepay_declineCode_validation(Host_sim_mode, generic_trans_amount, tractor_fuel_type, def_type_yes, card_to_use_NGFC, commercial_prompts, decline_message)
        
        if not execute[0]:
            tc_fail(execute[1])

    @test
    def DODO_6107_21_Prepay_DM(self):
        """
        In a prepay transaction with the DM response mode, the decline messages are shown to the cashier in the yellow bar at the POS
        """
        generic_trans_amount = "$5.00" # any value that gets an approval from the host
        tractor_fuel_type = 'Both fuels' 
        def_type_yes = 'No' 
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts        
        Host_sim_mode = "DM" #the scripts is about new response code, we are testing all of them
        decline_message = '.PAY INSIDE DM.' #expected message given the host sim mode
        commercial_prompts = {              
                            "Additional Products Y/N?": {                    
                                "buttons": ["No"]
                            },
                            "Do you want to print a receipt?": {
                                "buttons": ["No"]
                            }
                        }

        execute = self.prepay_declineCode_validation(Host_sim_mode, generic_trans_amount, tractor_fuel_type, def_type_yes, card_to_use_NGFC, commercial_prompts, decline_message)
        
        if not execute[0]:
            tc_fail(execute[1])
    '''
    @test
    def DODO_6107_23_Outside_D1(self):
        """
        In a outside transaction with the D1 response mode, the crind shows the message: "please see cashier" 
        """
        
        tractor_fuel_type = 'Reefer' 
        def_type_yes = 'No' 
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts        
        Host_sim_mode = "D1" #the scripts is about new response code, we are testing all of them
        decline_message = 'Payment rejected: .INV MERCHANT D1.' #expected message given the host sim mode
        # Dispenser prompts
        dispenser_prompts = {
            "Make selection":{
                "entry": [""],
                "buttons": [tractor_fuel_type]
            },
            "Need DEF?":{
                "entry": [""],
                "buttons": [def_type_yes]
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
                "buttons": ["No"]
            }
        }

        execute = self.outside_declineCode_validation(Host_sim_mode, card_to_use_NGFC, dispenser_prompts, decline_message)
    
        if not execute[0]:
            tc_fail(execute[1])

    @test
    def DODO_6107_24_Outside_D2(self):
        """
        In a outside transaction with the D2 response mode, the crind shows the message: "please see cashier" 
        """        
        tractor_fuel_type = 'Reefer' 
        def_type_yes = 'No' 
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts        
        Host_sim_mode = "D2" #the scripts is about new response code, we are testing all of them
        decline_message = 'Payment rejected: .INVALID CARD D2.' #expected message given the host sim mode
        # Dispenser prompts
        dispenser_prompts = {
            "Make selection":{
                "entry": [""],
                "buttons": [tractor_fuel_type]
            },
            "Need DEF?":{
                "entry": [""],
                "buttons": [def_type_yes]
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
                "buttons": ["No"]
            }
        }

        execute = self.outside_declineCode_validation(Host_sim_mode, card_to_use_NGFC, dispenser_prompts, decline_message)
    
        if not execute[0]:
            tc_fail(execute[1])

    @test
    def DODO_6107_25_Outside_D3(self):
        """
        In a outside transaction with the D3 response mode, the crind shows the message: "please see cashier" 
        """        
        tractor_fuel_type = 'Reefer' 
        def_type_yes = 'No' 
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts        
        Host_sim_mode = "D3" #the scripts is about new response code, we are testing all of them
        decline_message = 'Payment rejected: .INV EXP DATE D3.' #expected message given the host sim mode
        # Dispenser prompts
        dispenser_prompts = {
            "Make selection":{
                "entry": [""],
                "buttons": [tractor_fuel_type]
            },
            "Need DEF?":{
                "entry": [""],
                "buttons": [def_type_yes]
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
                "buttons": ["No"]
            }
        }

        execute = self.outside_declineCode_validation(Host_sim_mode, card_to_use_NGFC, dispenser_prompts, decline_message)
    
        if not execute[0]:
            tc_fail(execute[1])

    @test
    def DODO_6107_26_Outside_D4(self):
        """
        In a outside transaction with the D4 response mode, the crind shows the message: "please see cashier" 
        """        
        tractor_fuel_type = 'Reefer' 
        def_type_yes = 'No' 
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts        
        Host_sim_mode = "D4" #the scripts is about new response code, we are testing all of them
        decline_message = 'Payment rejected: .DUPLICATE D4.' #expected message given the host sim mode
        # Dispenser prompts
        dispenser_prompts = {
            "Make selection":{
                "entry": [""],
                "buttons": [tractor_fuel_type]
            },
            "Need DEF?":{
                "entry": [""],
                "buttons": [def_type_yes]
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
                "buttons": ["No"]
            }
        }

        execute = self.outside_declineCode_validation(Host_sim_mode, card_to_use_NGFC, dispenser_prompts, decline_message)
    
        if not execute[0]:
            tc_fail(execute[1])

    @test
    def DODO_6107_27_Outside_D5(self):
        """
        In a outside transaction with the D5 response mode, the crind shows the message: "please see cashier" 
        """        
        tractor_fuel_type = 'Reefer' 
        def_type_yes = 'No' 
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts        
        Host_sim_mode = "D5" #the scripts is about new response code, we are testing all of them
        decline_message = 'Payment rejected: .INV CURRENCY D5.' #expected message given the host sim mode
        # Dispenser prompts
        dispenser_prompts = {
            "Make selection":{
                "entry": [""],
                "buttons": [tractor_fuel_type]
            },
            "Need DEF?":{
                "entry": [""],
                "buttons": [def_type_yes]
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
                "buttons": ["No"]
            }
        }

        execute = self.outside_declineCode_validation(Host_sim_mode, card_to_use_NGFC, dispenser_prompts, decline_message)
    
        if not execute[0]:
            tc_fail(execute[1])

    @test
    def DODO_6107_28_Outside_D6(self):
        """
        In a outside transaction with the D6 response mode, the crind shows the message: "please see cashier" 
        """        
        tractor_fuel_type = 'Reefer' 
        def_type_yes = 'No' 
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts        
        Host_sim_mode = "D6" #the scripts is about new response code, we are testing all of them
        decline_message = 'Payment rejected: .INV COUNTRY D6.' #expected message given the host sim mode
        # Dispenser prompts
        dispenser_prompts = {
            "Make selection":{
                "entry": [""],
                "buttons": [tractor_fuel_type]
            },
            "Need DEF?":{
                "entry": [""],
                "buttons": [def_type_yes]
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
                "buttons": ["No"]
            }
        }

        execute = self.outside_declineCode_validation(Host_sim_mode, card_to_use_NGFC, dispenser_prompts, decline_message)
    
        if not execute[0]:
            tc_fail(execute[1])

    @test
    def DODO_6107_29_Outside_D8(self):
        """
        In a outside transaction with the D8 response mode, the crind shows the message: "please see cashier" 
        """        
        tractor_fuel_type = 'Reefer' 
        def_type_yes = 'No' 
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts        
        Host_sim_mode = "D8" #the scripts is about new response code, we are testing all of them
        decline_message = 'Payment rejected: .INV PRODUCT D8.' #expected message given the host sim mode
        # Dispenser prompts
        dispenser_prompts = {
            "Make selection":{
                "entry": [""],
                "buttons": [tractor_fuel_type]
            },
            "Need DEF?":{
                "entry": [""],
                "buttons": [def_type_yes]
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
                "buttons": ["No"]
            }
        }

        execute = self.outside_declineCode_validation(Host_sim_mode, card_to_use_NGFC, dispenser_prompts, decline_message)
    
        if not execute[0]:
            tc_fail(execute[1])

    @test
    def DODO_6107_30_Outside_D9(self):
        """
        In a outside transaction with the D9 response mode, the crind shows the message: "please see cashier" 
        """        
        tractor_fuel_type = 'Reefer' 
        def_type_yes = 'No' 
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts        
        Host_sim_mode = "D9" #the scripts is about new response code, we are testing all of them
        decline_message = 'Payment rejected: .OVER PROD LIM D9.' #expected message given the host sim mode
        # Dispenser prompts
        dispenser_prompts = {
            "Make selection":{
                "entry": [""],
                "buttons": [tractor_fuel_type]
            },
            "Need DEF?":{
                "entry": [""],
                "buttons": [def_type_yes]
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
                "buttons": ["No"]
            }
        }

        execute = self.outside_declineCode_validation(Host_sim_mode, card_to_use_NGFC, dispenser_prompts, decline_message)
    
        if not execute[0]:
            tc_fail(execute[1])

    @test
    def DODO_6107_31_Outside_DA(self):
        """
        In a outside transaction with the DA response mode, the crind shows the message: "please see cashier" 
        """        
        tractor_fuel_type = 'Reefer' 
        def_type_yes = 'No' 
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts        
        Host_sim_mode = "DA" #the scripts is about new response code, we are testing all of them
        decline_message = 'Payment rejected: .INV TRANS DA.' #expected message given the host sim mode
        # Dispenser prompts
        dispenser_prompts = {
            "Make selection":{
                "entry": [""],
                "buttons": [tractor_fuel_type]
            },
            "Need DEF?":{
                "entry": [""],
                "buttons": [def_type_yes]
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
                "buttons": ["No"]
            }
        }

        execute = self.outside_declineCode_validation(Host_sim_mode, card_to_use_NGFC, dispenser_prompts, decline_message)
    
        if not execute[0]:
            tc_fail(execute[1])
    
    @test
    def DODO_6107_32_Outside_DB(self):
        """
        In a outside transaction with the DB response mode, the crind shows the message: "please see cashier" 
        """        
        tractor_fuel_type = 'Reefer' 
        def_type_yes = 'No' 
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts        
        Host_sim_mode = "DB" #the scripts is about new response code, we are testing all of them
        decline_message = 'Payment rejected: .INV FUEL TYP DB.' #expected message given the host sim mode
        # Dispenser prompts
        dispenser_prompts = {
            "Make selection":{
                "entry": [""],
                "buttons": [tractor_fuel_type]
            },
            "Need DEF?":{
                "entry": [""],
                "buttons": [def_type_yes]
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
                "buttons": ["No"]
            }
        }

        execute = self.outside_declineCode_validation(Host_sim_mode, card_to_use_NGFC, dispenser_prompts, decline_message)
    
        if not execute[0]:
            tc_fail(execute[1])

    @test
    def DODO_6107_33_Outside_DC(self):
        """
        In a outside transaction with the DC response mode, the crind shows the message: "please see cashier" 
        """        
        tractor_fuel_type = 'Reefer' 
        def_type_yes = 'No' 
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts        
        Host_sim_mode = "DC" #the scripts is about new response code, we are testing all of them
        decline_message = 'Payment rejected: .INV FUEL USE DC.' #expected message given the host sim mode
        # Dispenser prompts
        dispenser_prompts = {
            "Make selection":{
                "entry": [""],
                "buttons": [tractor_fuel_type]
            },
            "Need DEF?":{
                "entry": [""],
                "buttons": [def_type_yes]
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
                "buttons": ["No"]
            }
        }

        execute = self.outside_declineCode_validation(Host_sim_mode, card_to_use_NGFC, dispenser_prompts, decline_message)
    
        if not execute[0]:
            tc_fail(execute[1])

    @test
    def DODO_6107_34_Outside_DD(self):
        """
        In a outside transaction with the DD response mode, the crind shows the message: "please see cashier" 
        """        
        tractor_fuel_type = 'Reefer' 
        def_type_yes = 'No' 
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts        
        Host_sim_mode = "DD" #the scripts is about new response code, we are testing all of them
        decline_message = 'Payment rejected: .INV FUEL SRV DD.' #expected message given the host sim mode
        # Dispenser prompts
        dispenser_prompts = {
            "Make selection":{
                "entry": [""],
                "buttons": [tractor_fuel_type]
            },
            "Need DEF?":{
                "entry": [""],
                "buttons": [def_type_yes]
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
                "buttons": ["No"]
            }
        }

        execute = self.outside_declineCode_validation(Host_sim_mode, card_to_use_NGFC, dispenser_prompts, decline_message)
    
        if not execute[0]:
            tc_fail(execute[1])

    @test
    def DODO_6107_35_Outside_DE(self):
        """
        In a outside transaction with the DE response mode, the crind shows the message: "please see cashier" 
        """        
        tractor_fuel_type = 'Reefer' 
        def_type_yes = 'No' 
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts        
        Host_sim_mode = "DE" #the scripts is about new response code, we are testing all of them
        decline_message = 'Payment rejected: .OVER FUEL LIM DE.' #expected message given the host sim mode
        # Dispenser prompts
        dispenser_prompts = {
            "Make selection":{
                "entry": [""],
                "buttons": [tractor_fuel_type]
            },
            "Need DEF?":{
                "entry": [""],
                "buttons": [def_type_yes]
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
                "buttons": ["No"]
            }
        }

        execute = self.outside_declineCode_validation(Host_sim_mode, card_to_use_NGFC, dispenser_prompts, decline_message)
    
        if not execute[0]:
            tc_fail(execute[1])

    @test
    def DODO_6107_36_Outside_DF(self):
        """
        In a outside transaction with the DF response mode, the crind shows the message: "please see cashier" 
        """        
        tractor_fuel_type = 'Reefer' 
        def_type_yes = 'No' 
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts        
        Host_sim_mode = "DF" #the scripts is about new response code, we are testing all of them
        decline_message = 'Payment rejected: .OVER LIMIT DF.' #expected message given the host sim mode
        # Dispenser prompts
        dispenser_prompts = {
            "Make selection":{
                "entry": [""],
                "buttons": [tractor_fuel_type]
            },
            "Need DEF?":{
                "entry": [""],
                "buttons": [def_type_yes]
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
                "buttons": ["No"]
            }
        }

        execute = self.outside_declineCode_validation(Host_sim_mode, card_to_use_NGFC, dispenser_prompts, decline_message)
    
        if not execute[0]:
            tc_fail(execute[1])

    @test
    def DODO_6107_37_Outside_DG(self):
        """
        In a outside transaction with the DG response mode, the crind shows the message: "please see cashier" 
        """        
        tractor_fuel_type = 'Reefer' 
        def_type_yes = 'No' 
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts        
        Host_sim_mode = "DG" #the scripts is about new response code, we are testing all of them
        decline_message = 'Payment rejected: .NO AUTH FOUND DG.' #expected message given the host sim mode
        # Dispenser prompts
        dispenser_prompts = {
            "Make selection":{
                "entry": [""],
                "buttons": [tractor_fuel_type]
            },
            "Need DEF?":{
                "entry": [""],
                "buttons": [def_type_yes]
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
                "buttons": ["No"]
            }
        }

        execute = self.outside_declineCode_validation(Host_sim_mode, card_to_use_NGFC, dispenser_prompts, decline_message)
    
        if not execute[0]:
            tc_fail(execute[1])

    @test
    def DODO_6107_38_Outside_DH(self):
        """
        In a outside transaction with the DH response mode, the crind shows the message: "please see cashier" 
        """        
        tractor_fuel_type = 'Reefer' 
        def_type_yes = 'No' 
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts        
        Host_sim_mode = "DH" #the scripts is about new response code, we are testing all of them
        decline_message = 'Payment rejected: .LATE VOID DH.' #expected message given the host sim mode
        # Dispenser prompts
        dispenser_prompts = {
            "Make selection":{
                "entry": [""],
                "buttons": [tractor_fuel_type]
            },
            "Need DEF?":{
                "entry": [""],
                "buttons": [def_type_yes]
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
                "buttons": ["No"]
            }
        }

        execute = self.outside_declineCode_validation(Host_sim_mode, card_to_use_NGFC, dispenser_prompts, decline_message)
    
        if not execute[0]:
            tc_fail(execute[1])

    @test
    def DODO_6107_39_Outside_DI(self):
        """
        In a outside transaction with the DI response mode, the crind shows the message: "please see cashier" 
        """        
        tractor_fuel_type = 'Reefer' 
        def_type_yes = 'No' 
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts        
        Host_sim_mode = "DI" #the scripts is about new response code, we are testing all of them
        decline_message = 'Payment rejected: .OVER LIMIT DI.' #expected message given the host sim mode
        # Dispenser prompts
        dispenser_prompts = {
            "Make selection":{
                "entry": [""],
                "buttons": [tractor_fuel_type]
            },
            "Need DEF?":{
                "entry": [""],
                "buttons": [def_type_yes]
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
                "buttons": ["No"]
            }
        }

        execute = self.outside_declineCode_validation(Host_sim_mode, card_to_use_NGFC, dispenser_prompts, decline_message)
    
        if not execute[0]:
            tc_fail(execute[1])

    @test
    def DODO_6107_40_Outside_DJ(self):
        """
        In a outside transaction with the DJ response mode, the crind shows the message: "please see cashier" 
        """        
        tractor_fuel_type = 'Reefer' 
        def_type_yes = 'No' 
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts        
        Host_sim_mode = "DJ" #the scripts is about new response code, we are testing all of them
        decline_message = 'Payment rejected: .OVER LIMIT DJ.' #expected message given the host sim mode
        # Dispenser prompts
        dispenser_prompts = {
            "Make selection":{
                "entry": [""],
                "buttons": [tractor_fuel_type]
            },
            "Need DEF?":{
                "entry": [""],
                "buttons": [def_type_yes]
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
                "buttons": ["No"]
            }
        }

        execute = self.outside_declineCode_validation(Host_sim_mode, card_to_use_NGFC, dispenser_prompts, decline_message)
    
        if not execute[0]:
            tc_fail(execute[1])

    @test
    def DODO_6107_41_Outside_DK(self):
        """
        In a outside transaction with the DK response mode, the crind shows the message: "please see cashier" 
        """        
        tractor_fuel_type = 'Reefer' 
        def_type_yes = 'No' 
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts        
        Host_sim_mode = "DK" #the scripts is about new response code, we are testing all of them
        decline_message = 'Payment rejected: .ACCT IN USE DK.' #expected message given the host sim mode
        # Dispenser prompts
        dispenser_prompts = {
            "Make selection":{
                "entry": [""],
                "buttons": [tractor_fuel_type]
            },
            "Need DEF?":{
                "entry": [""],
                "buttons": [def_type_yes]
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
                "buttons": ["No"]
            }
        }

        execute = self.outside_declineCode_validation(Host_sim_mode, card_to_use_NGFC, dispenser_prompts, decline_message)
    
        if not execute[0]:
            tc_fail(execute[1])

    @test
    def DODO_6107_42_Outside_DL(self):
        """
        In a outside transaction with the DL response mode, the crind shows the message: "please see cashier" 
        """        
        tractor_fuel_type = 'Reefer' 
        def_type_yes = 'No' 
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts        
        Host_sim_mode = "DL" #the scripts is about new response code, we are testing all of them
        decline_message = 'Payment rejected: .NO DYED CERT DL.' #expected message given the host sim mode
        # Dispenser prompts
        dispenser_prompts = {
            "Make selection":{
                "entry": [""],
                "buttons": [tractor_fuel_type]
            },
            "Need DEF?":{
                "entry": [""],
                "buttons": [def_type_yes]
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
                "buttons": ["No"]
            }
        }

        execute = self.outside_declineCode_validation(Host_sim_mode, card_to_use_NGFC, dispenser_prompts, decline_message)
    
        if not execute[0]:
            tc_fail(execute[1])

    @test
    def DODO_6107_43_Outside_DM(self):
        """
        In a outside transaction with the DM response mode, the crind shows the message: "please see cashier" 
        """        
        tractor_fuel_type = 'Reefer' 
        def_type_yes = 'No' 
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts        
        Host_sim_mode = "DM" #the scripts is about new response code, we are testing all of them
        decline_message = 'Payment rejected: .PAY INSIDE DM.' #expected message given the host sim mode
        # Dispenser prompts
        dispenser_prompts = {
            "Make selection":{
                "entry": [""],
                "buttons": [tractor_fuel_type]
            },
            "Need DEF?":{
                "entry": [""],
                "buttons": [def_type_yes]
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
                "buttons": ["No"]
            }
        }

        execute = self.outside_declineCode_validation(Host_sim_mode, card_to_use_NGFC, dispenser_prompts, decline_message)
    
        if not execute[0]:
            tc_fail(execute[1])

    @test
    def DODO_6107_44_Outside_DN(self):
        """
        In a outside transaction with the DN response mode, the crind shows the message: "please see cashier" 
        """        
        tractor_fuel_type = 'Reefer' 
        def_type_yes = 'No' 
        card_to_use_NGFC = 'NGFC' # using this card to get all commercial prompts        
        Host_sim_mode = "DN" #the scripts is about new response code, we are testing all of them
        decline_message = 'Payment rejected: .INV EXP DATE DN.' #expected message given the host sim mode
        # Dispenser prompts
        dispenser_prompts = {
            "Make selection":{
                "entry": [""],
                "buttons": [tractor_fuel_type]
            },
            "Need DEF?":{
                "entry": [""],
                "buttons": [def_type_yes]
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
                "buttons": ["No"]
            }
        }

        execute = self.outside_declineCode_validation(Host_sim_mode, card_to_use_NGFC, dispenser_prompts, decline_message)
    
        if not execute[0]:
            tc_fail(execute[1])

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        self.pos.close()

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
            return False
    
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

    def crind_prompts_handler(self, prompts, decline_scenario=False):
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
                         "Pay here Insert card or Pay inside Lift handle",
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

            while display_text == "Please wait..." or display_text == "Authorizing..." or display_text == "One moment please...":
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
                    
            except IndexError as e:
                self.log.warning(f"No entry provided for prompt {display_text}, probably the prompt does not need entries, please check")
                self.log.warning(e)
                return False
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

    def prepay_declineCode_validation(self, Host_sim_mode, generic_trans_amount, tractor_fuel_type, def_type_yes, card_to_use_NGFC, commercial_prompts, decline_message):
        
        # HostSim Response mode
        set_response_result = networksim.set_response_mode(Host_sim_mode)

        start_time = time.time()
        while not set_response_result['success'] and time.time() - start_time < 60:
            set_response_result = networksim.set_response_mode(Host_sim_mode)

        if not set_response_result['success']:
            networksim.set_response_mode("Approval")
            return [False,f"Setting decline code to '{Host_sim_mode}'' in the Host simulator failed"]

        self.pos.add_fuel(generic_trans_amount,fuel_type = tractor_fuel_type, def_type = def_type_yes)

        self.pos.pay_card(brand="Exxon", card_name = card_to_use_NGFC, prompts= commercial_prompts, verify=False, decline_transaction=True)
        ###########################

        
        prompt_messsage = self.pos.read_message_box()        

        
        self.pos.click_message_box_key('Ok')
        time.sleep(2)
        
        self.pos.click_keypad('Cancel')
        time.sleep(2)
        
        self.log.info("Trying to void transaction")
        
        result = self.pos.void_transaction()
        
        if not result:
            tc_fail("Transaction void failed")
            return False

        self.log.info(f"Result of void transaction: {result}")

        if not decline_message in prompt_messsage:
            networksim.set_response_mode("Approval")
            return [False, f"Invalid decline message, the message is '{prompt_messsage}' doesn't contain {decline_message}"]
    
        self.log.info("Set host simulator back to 'Approval'")
        networksim.set_response_mode("Approval")

        return [True, "Test case done"]

    def outside_declineCode_validation(self, Host_sim_mode, card_to_use_NGFC, dispenser_prompts, decline_message):
        
        crindsim_idle_display = "INSERT CARD To Pay Here or LIFT HANDLE To Pay Inside"
        
        # HostSim Response mode
        set_response_result = networksim.set_response_mode(Host_sim_mode)

        if not set_response_result['success']:
            networksim.set_response_mode("Approval")
            return [False,f"Setting decline code to '{Host_sim_mode}'' in the Host simulator failed"]
        
        current_display = crindsim.get_display_text()
        start_time = time.time()
        while current_display != crindsim_idle_display and time.time() - start_time < 120:
            time.sleep(2)
            current_display = crindsim.get_display_text()

        if time.time() - start_time >= 120:
            networksim.set_response_mode("Approval")
            return [False,f"Crind simulator is taking so long to get ready to start.  Last display: {current_display}"]

        # Iniciate outside trnsaction
        crindsim.swipe_card(card_name=card_to_use_NGFC, brand="EXXON")
        
        # Handle crind prompts
        self.crind_prompts_handler(dispenser_prompts, decline_scenario=True)

        self.pos.wait_disp_ready(idle_timeout=120)
        error_message = self.pos.read_dispenser_diag()['Errors']
        self.log.debug(f"Crind error message: {error_message}")

        if not decline_message in error_message:
            networksim.set_response_mode("Approval")
            return [False, f"Invalid decline message, the message {error_message} doesn't contain {decline_message}"]
        
        current_display = crindsim.get_display_text()
        start_time = time.time()
        while current_display != crindsim_idle_display and time.time() - start_time < 120:
            time.sleep(2)
            current_display = crindsim.get_display_text()

        if time.time() - start_time >= 120:
            networksim.set_response_mode("Approval")
            return [False,f"Crind simulator is taking so long to get ready to start after transaction.  Last display: {current_display}"]

        if not self.pos.click_forecourt_key("CLEAR ERRORS", timeout=10, verify=False):
            networksim.set_response_mode("Approval")
            return [False, f"Unable to clear POS forecourt display."]

        self.log.info("Set host simulator back to 'Approval'")
        networksim.set_response_mode("Approval")

        return [True, "Test case done"]