"""
    File name: DODO_6194.py
    Tags:
    Description: Restrict refund transactions with paper checks
    Author: 
    Date created: 2020-03-09 10:00:56
    Date last modified: 
    Python Version: 3.7
"""

import logging
import time
from app import Navi, mws, pos, system, forecourt_installation, networksim, network_site_config, crindsim
from app.framework import EDH
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app.features import feature_activation, tender

class DODO_6194():
    """
    Description: Test class that provides an interface for testing.
    """

    def __init__(self):
        """
        Initializes the Template class.
        """
        # The logging object. 
        
        self.log = logging.getLogger()

        # The main POS object
        
        self.pos = pos

        # The main EDH object
        self.edh = EDH.EDH()

        # The main MWS object
        self.mws = mws

    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        """

        #if not system.restore_snapshot(snapshot_name="Commercial_Diesel"):
        #    self.log.debug("Commercial Diesel snapshot not available, please run NGFC_setup.py")

        # HostSim Response mode
        networksim.set_response_mode("Approval")

        networksim.disable_commercial_fuel_limits()
        networksim.disable_product_limits()
        networksim.disable_prompts()

        crindsim.set_mode("auto")
        crindsim.set_sales_target()

        #open Browser

        #Commercial feature activation
        #self.Commercial_feature_activation()

        #Commercial Diesel checkbox activation in forecourt installation 
        self.set_commercial_on_forecourt()

        # Open browser
        self.pos.connect()
    
    def verify_Paper_Check_Tender_Created(self):
        """
        it verifies if paper check tender is already created, if not, it creates it.
        """
        
        #Input constants 
        self.papercheck_tender_code = "1234"
        self.papercheck_tender_description = 'Paper Check'
        self.papercheck_tender_group = 'Integrated Commercial Check'
        self.papercheck_button_name = 'PAPER CHK'

        tender_info = {
                "Tender Code": self.papercheck_tender_code,
                "Tender Description": self.papercheck_tender_description,
                "General": {
                    "Tender group this tender belongs to": self.papercheck_tender_group,
                    "Receipt Description": self.papercheck_tender_description,
                    "Tender Button Description": self.papercheck_tender_description,
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
        if mws.set_value("Tenders", self.papercheck_tender_description):
            return True
        else:
            self.log.debug(f"Adding {self.papercheck_tender_description}, since it was not created previously.")
            
            # tender maintenance configuration for paper check
            tm = tender.TenderMaintenance()
            tm.configure(self.papercheck_tender_description, tender_info, True)

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
    
    @test
    def DODO_6194_PaperCheck_DisabledRefund_TenderMaintenance_POS(self):
        """
        When in the MWS, it wants configurate a Paper Check tender in the "Register Groups" tab, the tender doesn't valid for refund, the option "Refund" must be disabled.
        """

        #Input constants 
        self.papercheck_tender_code = "1234" # any not existent value
        self.papercheck_tender_description = 'Paper Check' # something that make sense
        self.papercheck_tender_group = 'Integrated Commercial Check'
        self.papercheck_button_name = 'PAPER CHK' # someting that fits in the mws and the button
        
        tender_info = {
                "Tender Code": self.papercheck_tender_code,
                "Tender Description": self.papercheck_tender_description,
                "General": {
                    "Tender group this tender belongs to": self.papercheck_tender_group,
                    "Receipt Description": self.papercheck_tender_description,
                    "Tender Button Description": self.papercheck_button_name,
                    "NACS Tender Code": "generic"
                },
                "Register Groups": {
                    "POSGroup1": {
                        "Sales": True,
                        "Refunds": True
                    }
                }
            }

        # Instantiate the Tender Maintenance objet, it navigates to tender maintanance 
        # while it is created
        tm = tender.TenderMaintenance()
        
        self.log.info("Checking if the tender exist")
        # Check to see if tender to add already exists...
        if self.mws.set_value("Tenders", self.papercheck_tender_description):
            self.log.debug(f"{self.papercheck_tender_description} already exists, clicking Change...")
            self.mws.click_toolbar("Change")
        else:
            self.log.debug(f"Adding {self.papercheck_tender_description}...")
            self.mws.click_toolbar("Add")

        self.log.info(f"Setting tender code {self.papercheck_tender_code}")
        # Set Tender Code
        if not self.mws.set_value("Tender Code", self.papercheck_tender_code):            
            
            tc_fail(f"Could not set 'Tender Code' control with '{self.papercheck_tender_code}'")            
        
        self.log.info(f"Setting Tender Description {self.papercheck_tender_description}")
        # Set Tender Description
        if not mws.set_value("Tender Description", self.papercheck_tender_description):
            
            tc_fail(f"Could not set 'Tender Description' control with '{self.papercheck_tender_description}'")

        self.log.info("Select General tab")
        # Select tab General        
        mws.select_tab("General")


        # Setting mandatory info
        for key, value in tender_info["General"].items():
            
            self.log.info(f"Enter {value} in {key}")
            
            if not mws.set_value(key,value):
                    tc_fail(f"Could not set '{key}' control to '{value}' in 'General' tab.")
                    
            # Certain tender groups trigger a message bar popup...
            if mws.get_top_bar_text():
                mws.click_toolbar("OK")
            if not tm.confirm_control_value(key,value):
                tc_fail(f"Could not set '{key}' control to '{value}' in 'General' tab.")
        
        self.log.info(f"Select Groups Tab")
        # Select Register Group Tab
        mws.select_tab("Register Groups")
         
        for registergroup in tender_info["Register Groups"]:
            
            #Selects POSGroup1
            self.log.info(f"Select {registergroup} checkbox")
            mws.select_checkbox(registergroup, tab= "Register Groups", list= "Register Groups")
        
            for key, value in tender_info["Register Groups"][registergroup].items(): 
                
                self.log.info(f"Set {value} in {key}")
                if not mws.set_value(key,value):
                    # If we fail to set Refunds is because it is disabled (what is expected)
                    if key != "Refunds":
                        tc_fail(f"Could not set '{key}' control to '{value}' in 'Register Groups' tab.")
                   
        self.log.info("Checking if Refund checkbox was set")
        result = mws.status_checkbox("Refunds", tab="Register Groups")
        self.log.info(f"the chackbox is {result}")

        if  result is not False:

            tc_fail("Refund checkbox was set for paper check")

        # save the new tender
        self.log.info("Save changes")
        mws.click_toolbar("Save")  
    '''
    # TODO: Refunds is not implementd yet in HTML POS
    @test
    def DODO_6194_PaperCheck_Refund(self):
        """
        When it makes the refund for a transaction, the system shouldn't show the Paper Check in the tender of Refund.
        """

        # Minimize pos so mws can be configured
        self.pos.minimize_pos()

        # if the tender does not existe, it will create it
        self.verify_Paper_Check_Tender_Created()

        # Maximize the browser window so, in case of failure, 
        # the correct screenshot is taken
        
        self.pos.maximize_pos()

        # Start execution
                
        self.pos.sign_on()

        if not self.pos.click_function_key("Refund"):
            tc_fail("Unable to select Refund button")
        
        self.pos.add_item()

        if not self.pos.click_function_key("Pay"):
            tc_fail("Unable to select Pay button")
        
        if pos.click_tender_key(self.papercheck_button_name, verify=False):
            
            tc_fail(f"{self.papercheck_button_name} button is available on refund")

        self.log.info("Paying with cash to complete the transactions and prevent void issue")
        self.pos.pay()
        
        #self.pos.void_transaction()
    
    @test
    def DODO_6194_PaperCheck_Refund_Underrun(self):
        """
        When it makes the underrun, the system mustn't show Paper Check in the tender of Refund.
        """
        # Evironment configuiration 

        # Minimize pos so mws can be configured
        self.pos.minimize_pos()

        # if the tender does not existe, it will create it
        self.verify_Paper_Check_Tender_Created()

        # Maximize the browser window so, in case of failure, 
        # the correct screenshot is taken
        
        self.pos.maximize_pos()

        # HostSim Response mode
        networksim.set_response_mode("Approval")

        # Set the host sim to fuel #5.00 

        crindsim.set_sales_target("money", "5.00")

        #Input constants
        
        trans_amount = "$10.00" # this should be an amount above the fuel set in the crind sim
        generic_fuel_type = 'Tractor fuel.' # any of the fuel types, since is not the objetive of the TC ("Tractor fuel.", "Reefer fuel.", "Both fuels.")
        def_type_yes = 'Yes' #could be "yes" of "no",  because is not the objective of this TC        
        commercial_prompts = {#"Commercial_prompt" is a dictionary in which are the dinamic prompts for commercial diesel
                        "Enter Check Number": {
                            "entry": ["120170"],
                            "buttons": ["Enter"]
                        }, 
                        "Insert Last Name and First Name": {
                            "entry" : ["Pepe Pompin"],
                            "buttons": ["Ok"]                
                        }
                    }
        
        #Output verifications

        receipt_data = ["Regular CA   PUMP# 1",
                        "5.000 GAL @ $1.000/GAL         $5.00  99",
                        "Subtotal =   $5.00",
                        "Tax  =    $0.00",
                        "Total =   $5.00",
                        "Change Due  =    $-5.00",
                        f"{self.papercheck_tender_description}        $10.00"]
        
        # Start execution

        self.pos.sign_on()

        # add a prepay for $10 

        self.pos.add_fuel(trans_amount,fuel_type = generic_fuel_type, def_type = def_type_yes)

        # Pay with paper check

        self.pos.pay(amount=trans_amount, tender_type=self.papercheck_button_name, prompts=commercial_prompts)

        time.sleep(5) #The wait for fuel make the verifications before it start fueling

        self.pos.wait_for_fuel()

        self.pos.click_fuel_buffer('A')

        self.pos.click_function_key('Pay')

        if pos.click_tender_key(self.papercheck_button_name, verify=False):
            
            tc_fail(f"{self.papercheck_button_name} button is available on underrun")

        # Tryning to complete the transaction
        
        self.pos.pay()

        # Set the crind sim in the original state
        
        crindsim.set_sales_target(sales_type="Auth")

        self.pos.check_receipt_for(receipt_data, timeout=10)
    '''

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        self.pos.close()
