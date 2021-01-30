"""
    File name: Network_Transactions_Indoor.py
    Tags:
    Description: Indoor transaction for Network_Transaction
    Author: Matthew Jehnke 
    Date created: 2020-01-22 10:03:11
    Date last modified: 1/22/2020
    Python Version: 3.7
"""
#import python modules
import logging, time, json, requests
#import script-based framework modules
from Scripts.framework import Network_Transactions_Functions
#import TC decorators
from app.framework.tc_helpers import setup, test, teardown, tc_fail
#import in-house modules
from app import pos, system, Results, tender, mws, crindsim, Navi
from app.util import constants
from app.features.network.core import network_site_config, fuel_disc_config
from app.features import fuel_discount_maint

from test_harness import RUN_DATA_FILE

class Network_Transactions():
    """
    Test class that provides an interface for testing.
    """

    def __init__(self):
        """
        Initializes the Template class.
        """
        self.script = "Network_Transactions_Indoor.py"
        self.log = logging.getLogger()

        self.res = Results()

        #See if a card list has been provided by the tester
        self.log.info("Reading cardlist var")
        try:
            with open (RUN_DATA_FILE) as rdf:
                run_info = json.load(rdf)
                self.cardlist = run_info["cardlist"]
                self.log.info(f"cardlist contains {self.cardlist}")
        except KeyError as e:
            self.cardlist = None
                
        #Parse the card list if provided.  Separate card arguments by a semicolon ;
        if not self.cardlist == None:
            self.card_list = self.cardlist.split(';')
        else:
            self.card_list = None

        #Read the CardData.json for a list of supported cards
        self.log.info("Reading card_file var to populate card_data")
        try:
            with open (constants.CARD_DATA) as f:
                self.cards = json.load(f)
                self.log.info(f"cards filled from file path {constants.CARD_DATA}")
            f.close()
        except Exception as e:
            self.log.error(e)
            self.log.error(f"Failed to open and retrieve card information from {constants.CARD_DATA}") 
            raise

    @setup
    def setup(self):
        """
        Performs any initialization that is not default, and navigates to the POS.
        """  
        #Disable cashback/cashback fee/debit fee     
        nw_cfg = {
            "Global Information" : {
				"Page 2" : {
					"Debit Cash Back Minimum" : "0.00",
					"Debit Cash Back Maximum" : "0.00",
					"EBT Cash Back Minimum" : "0.00",
					"EBT Cash Back Maximum" : "0.00",
					"Debit Cash Back Fee" : "0.00",
					"Debit Sale Fee" : "0.00"
				}
			}
        }
        nw = network_site_config.NetworkSetup()
        nw.configure_fields(config=nw_cfg)
        mws.click_toolbar("Save")

        #Configure debit tender for refunds
        tm = tender.TenderMaintenance()
        tender_info = tender_info = {
                "Tender Code": "4",
                "Tender Description": "Debit",
                "General": {
                    "Tender group this tender belongs to": "Integrated Debit",
                    "Safe drops allowed for this tender": True,
                    "Print tax invoice text on Receipt": False,
                    "Receipt Description": "Debit",
                    "Tender Button Description": "Debit",
                    "NACS Tender Code": "debitCards"
                },
                "Min/Max": {
                    "Minimum Allowed": "0.00",
                    "Maximum Allowed": "1000.00",
                    "Repeated Use Limit": "5",
                    "Maximum Refund": "100.00",
                    "Primary tender for change": "Cash",
                    "Maximum primary change allowed": "1000.00",
                    "Secondary tender for change": "<NoTender>"
                },
                "Register Groups": {
                    "POSGroup1": {
                        "Sales": True,
                        "Refunds": True
                    }
                }
            }
        tm.configure(tender_name = 'Debit', config = tender_info)

        Navi.navigate_to("Tender Maintenance")

        tm.change_status(tender_name = "EBT Food", status = True)
        tm.change_status(tender_name = "EBT Cash", status = True)

        # Loopback as workaround for device id
        pos.connect(url = 'https://127.0.0.1:7501')
        
        pos.pinpad.reset()

        # Open till
        self.log.info("Attempting to sign in with user 91 91 and opening balance of $1.00")
        pos.sign_on(("91","91"), "1.00")
        time.sleep(5)

        # Set dispensers to manual mode
        crindsim.set_mode("manual")
        crindsim.set_flow_rate("10")

        #Ensure starting state of nozzle and handle are closed/lowered
        crindsim.close_nozzle()
        crindsim.lower_handle()

    @test
    def sale(self):
        """
        Performs a basic network sale with cards from the CORE group in CardData.json.
        """
        #Set some variables needed to only run the cards we want
        execute_list = []
        exclude_list = ["FuelOnly", "Expired", "Loyalty", "EMVAmEx"]

        if self.card_list:
            self.log.info("Found a card list. Will use that when verifying which cards to execute")

        #TODO: Make the card_group dynamic
        card_group = self.cards["CORE"]
        for card_name in card_group:
            exclude = False
            include = False
            #Check the card against the list of cards we want to run, if it exists
            if self.card_list:
                for includes in self.card_list:
                    if card_name == includes:
                        include = True
                        break
                if include:
                    self.log.info(f"Adding card: {card_name}")
                    continue
            #Check the card against the list of cards we do not want to run
            for excludes in exclude_list:
                if excludes == "FuelOnly" or excludes == "Expired":
                    if excludes in card_name:
                        exclude = True
                        break
                else:
                    if excludes == card_name:
                        exclude = True
                        break
            if exclude:
                self.log.info(f"Excluding card: {card_name}") 
                continue
            self.log.info(f"Adding card: {card_name}")
            execute_list.append(card_name)
        #Set the variable we use to decide what to log for the whole method with test_harness
        #If a single card fails we want to mark a fail for the whole method
        failure = False

        for card in execute_list:
            #Set the test start time
            test_start = time.time()
            self.log.info(f"Current card in execute list: {card}")
            #Run the transaction
            #TODO: Make the card_group dynamic
            if not Network_Transactions_Functions.sale_func([card, "CORE"]):
                self.log.error(f"Receipt not displaying expected items or total for the card: {card}")
                #If the card isn't the last one let's just record the result. On the last one we can exit the TC
                run_time = self.get_runtime(test_start)
                self.res.record("sale", self.script, f"Performs a basic network sale with {card}", "fail", run_time, True)
                failure = True
            else:
                self.log.info(f"Successful performed a Sale with the card: {card}")
                run_time = self.get_runtime(test_start)
                self.res.record("sale", self.script, f"Performs a basic network sale with {card}", "pass", run_time, True)
        if failure:
            tc_fail(f"Failed to perform a Sale with at least one card")

    @test
    def sale_card_decline(self):
        """
        Performs a basic network sale, that declines, with cards from the CORE group in CardData.json.
        """
        #Set some variables needed to only run the cards we want
        execute_list = []
        exclude_list = ["Loyalty", "EMVAmEx"]

        if self.card_list:
            self.log.info("Found a card list. Will use that when verifying which cards to execute")

        #TODO: Make the card_group dynamic
        card_group = self.cards["CORE"]
        for card_name in card_group:
            exclude = False
            include = False
            #Check the card against the list of cards we want to run, if it exists
            if self.card_list:
                for includes in self.card_list:
                    if card_name == includes:
                        include = True
                        break
                if include:
                    self.log.info(f"Adding card: {card_name}")
                    continue
            #Check the card against the list of cards we do not want to run
            for excludes in exclude_list:
                if excludes == "FuelOnly" or excludes == "Expired":
                    if excludes in card_name:
                        exclude = True
                        break
                else:
                    if excludes == card_name:
                        exclude = True
                        break
            if ("FuelOnly" not in card_name) and ("Expired" not in card_name):
                exclude = True
            if exclude:
                self.log.info(f"Excluding card: {card_name}") 
                continue
            self.log.info(f"Adding card: {card_name}")
            execute_list.append(card_name)
        #Set the variable we use to decide what to log for the whole method with test_harness
        #If a single card fails we want to mark a fail for the whole method
        failure = False

        for card in execute_list:
            #Set the test start time
            test_start = time.time()
            self.log.info(f"Current card in execute list: {card}")
            if "FuelOnly" in card:
                decline_prompt = 'Fuel only card'
            elif "Expired" in card:
                decline_prompt = 'Expired Card: Try Another'
            else:
                self.log.error("Incorrect card made it into the execute_list")
                continue

            #Run the transaction
            #TODO: Make the card_group dynamic
            if not Network_Transactions_Functions.sale_decline_func([card, "CORE"], decline_prompt=decline_prompt):
                self.log.error(f"Sale with card decline failed for card: {card}")
                run_time = self.get_runtime(test_start)
                self.res.record("sale_card_decline", self.script, f"Performs a sale with card decline with {card}", "fail", run_time, True)
                failure = True
            else:
                self.log.info(f"Successful sale with card decline with the card: {card}")
                run_time = self.get_runtime(test_start)
                self.res.record("sale_card_decline", self.script, f"Performs a sale with card decline with {card}", "pass", run_time, True)
        if failure:
            tc_fail(f"Failed to perform a Sale Card Decline with at least one card")
                      
    @test
    def refund(self):
        """
        Performs a refund with various card types.
        """
        #Set some variables needed to only run the cards we want
        execute_list = []
        #NOTE Fuelman is excluded due to needing a cash refund
        exclude_list = ["FuelOnly", "Expired", "Loyalty", "EMVAmEx", "Fuelman"]

        if self.card_list:
            self.log.info("Found a card list. Will use that when verifying which cards to execute")

        #TODO: Make the card_group dynamic
        card_group = self.cards["CORE"]
        for card_name in card_group:
            exclude = False
            include = False
            #Check the card against the list of cards we want to run, if it exists
            if self.card_list:
                for includes in self.card_list:
                    if card_name == includes:
                        include = True
                        break
                if include:
                    self.log.info(f"Adding card: {card_name}")
                    continue
            #Check the card against the list of cards we do not want to run
            for excludes in exclude_list:
                if excludes == "FuelOnly" or excludes == "Expired":
                    if excludes in card_name:
                        exclude = True
                        break
                else:
                    if excludes == card_name:
                        exclude = True
                        break
            if exclude:
                self.log.info(f"Excluding card: {card_name}") 
                continue
            self.log.info(f"Adding card: {card_name}")
            execute_list.append(card_name)
        failure = False

        for card in execute_list:
            #Set the test start time
            test_start = time.time()
            self.log.info(f"Current card in execute list: {card}")
            #Run the transaction
            #TODO: Make the card_group dynamic
            if not Network_Transactions_Functions.refund_func([card, "CORE"]):
                self.log.error(f"Receipt not displaying expected items or total for the card: {card}")
                run_time = self.get_runtime(test_start)
                self.res.record("refund", self.script, f"Performs a refund with {card}", "fail", run_time, True)
                failure = True
            else:
                self.log.info(f"Successful performed a refund with the card: {card}")
                run_time = self.get_runtime(test_start)
                self.res.record("refund", self.script, f"Performs a refund with {card}", "pass", run_time, True)
        if failure:
            tc_fail(f"Failed to perform a Refund with at least one card")

    @test
    def split_tender_sale(self):
        """
        Performs a transaction with split tenders
        """
        #Set some variables needed to only run the cards we want
        execute_list = []
        exclude_list = ["FuelOnly", "Expired", "Loyalty", "EMVAmEx"]

        if self.card_list:
            self.log.info("Found a card list. Will use that when verifying which cards to execute")

        #TODO: Make the card_group dynamic
        card_group = self.cards["CORE"]
        for card_name in card_group:
            exclude = False
            include = False
            #Check the card against the list of cards we want to run, if it exists
            if self.card_list:
                for includes in self.card_list:
                    if card_name == includes:
                        include = True
                        break
                if include:
                    self.log.info(f"Adding card: {card_name}")
                    continue
            #Check the card against the list of cards we do not want to run
            for excludes in exclude_list:
                if excludes == "FuelOnly" or excludes == "Expired":
                    if excludes in card_name:
                        exclude = True
                        break
                else:
                    if excludes == card_name:
                        exclude = True
                        break
            if exclude:
                self.log.info(f"Excluding card: {card_name}") 
                continue
            self.log.info(f"Adding card: {card_name}")
            execute_list.append(card_name)
        failure = False

        for card in execute_list:
            #Set the test start time
            test_start = time.time()
            self.log.info(f"Current card in execute list: {card}")
            #Run the transaction
            #TODO: Make the card_group dynamic
            if not Network_Transactions_Functions.split_tender_func([card, "CORE"]):
                self.log.error(f"Receipt not displaying expected items or total for the card: {card}")
                run_time = self.get_runtime(test_start)
                self.res.record("split_tender_sale", self.script, f"Performs a split tender sale with {card}", "fail", run_time, True)
                failure = True
            else:
                self.log.info(f"Successful performed a split tender Sale with the card: {card}")
                run_time = self.get_runtime(test_start)
                self.res.record("split_tender_sale", self.script, f"Performs a split tender sale with {card}", "pass", run_time, True)
        if failure:
            tc_fail(f"Failed to perform a Split Tender Sale with at least one card")

    # @test
    def sale_with_loyalty(self):
        """
        Performs a transaction with a loyalty discount
        """
        #TODO configuration for loyalty once loyalty sim is in a more complete state
        #Importing pos based on the system config
        pp_subkey = constants.NT_SUBKEY
        reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, pp_subkey, 0, winreg.KEY_ALL_ACCESS)
        Site_Type = "Edge" if (winreg.QueryValueEx(reg_key, 'Machine')[0] == "PS65") else "Classic"

        #Cycle through CardData.json to find CORE Group
        for (card_group, card_name) in self.cards.items():
            if (card_group == "CORE"):
                #Cycle through CORE card group to use each card within
                for (card_name, card_data) in self.cards['CORE'].items():
                    if (not ("FuelOnly" in card_name or "Expired" in card_name or "Loyalty" in card_name or "EMVAmEx" in card_name)):
                        count = 0
                        success_flag = False
                        while (count < 3 and success_flag == False):
                            self.log.info("Adding item 008")
                            pos.add_item("008", "PLU")
                            
                            self.log.info("Clicking pay button.")
                            pos.click_function_key("Pay")

                            message_time = time.time()
                            while (time.time()-message_time < 5):
                                #Waiting for message box to show for loyalty
                                if Site_Type == "Edge":
                                    self.log.info("Looking for Loyalty popup message")
                                    if pos._is_element_present(pos.PROMPT['body']):
                                        break
                            else:
                                tc_fail("Waited 5 seconds for loyalty message box.  It never appeared.")
                            
                            self.log.info("Responding to loyalty message with 'Yes'")
                            pos.click_message_box_key("Yes")
                            self.log.info("Swiping loyalty card")
                            pos.pinpad.swipe_card(brand='CORE', card_name='Loyalty')

                            #Use current card in CardData.json CORE group to pay for sale
                            self.log.info(f"Name of card about to be swiped: {card_name}")
                            if pos.pay_card(brand=card_group, card_name=card_name, verify=False):
                                success_flag=True
                                # Check to make sure both items are on the receipt
                                self.log.info("Checking receipt for correct items, price and tender type")
                                if not pos.check_receipt_for(["Item 8 $5.00", "Total = $5.00",  "new loy trans reward $1.00","$4.00"]):
                                    self.log.info(f"Receipt not displaying expected items or total for the card: {card_name}")
                            else:
                                self.log.info(f"Entering fail loop for pay_card")
                                count += 1
                                # if pos._is_element_present(pos.PROMPT['body']):
                                #     pos.click_message_box_key("Ok", verify=False)
                                # else:
                                #     pos.click_function_key("Cancel", verify=False)
                                # if pos._is_element_present(pos.PROMPT['body']):
                                #     pos.click_message_box_key("Ok", verify=False)
                                pos.click_message_box_key("Ok", verify=False)
                                pos.click_function_key("Cancel", verify=False)
                                pos.click_message_box_key("Ok", verify=False)
                                pos.pinpad.reset()
                                pos.void_transaction()
                                self.log.info(f"Failed to tender transaction with {card_name} for the {count} attempt.")
                            time.sleep(10)

    @test
    def sale_with_discount(self):
        """
        Performs a sale with a discount and tender with various card types.
        """
        #Set some variables needed to only run the cards we want
        execute_list = []
        exclude_list = ["FuelOnly", "Expired", "Loyalty", "EMVAmEx"]

        if self.card_list:
            self.log.info("Found a card list. Will use that when verifying which cards to execute")

        #TODO: Make the card_group dynamic
        card_group = self.cards["CORE"]
        for card_name in card_group:
            exclude = False
            include = False
            #Check the card against the list of cards we want to run, if it exists
            if self.card_list:
                for includes in self.card_list:
                    if card_name == includes:
                        include = True
                        break
                if include:
                    self.log.info(f"Adding card: {card_name}")
                    continue
            #Check the card against the list of cards we do not want to run
            for excludes in exclude_list:
                if excludes == "FuelOnly" or excludes == "Expired":
                    if excludes in card_name:
                        exclude = True
                        break
                else:
                    if excludes == card_name:
                        exclude = True
                        break
            if exclude:
                self.log.info(f"Excluding card: {card_name}") 
                continue
            self.log.info(f"Adding card: {card_name}")
            execute_list.append(card_name)
        failure = False

        for card in execute_list:
            #Set the test start time
            test_start = time.time()
            self.log.info(f"Current card in execute list: {card}")
            #Run the transaction
            #TODO: Make the card_group dynamic
            if not Network_Transactions_Functions.sale_discount_func([card, "CORE"]):
                self.log.error(f"Receipt not displaying expected items or total for the card: {card}")
                run_time = self.get_runtime(test_start)
                self.res.record("sale_with_discount", self.script, f"Performs a basic network sale a discount with {card}", "fail", run_time, True)
                failure = True
            else:
                self.log.info(f"Successful performed a Sale with Discount with the card: {card}")
                run_time = self.get_runtime(test_start)
                self.res.record("sale_with_discount", self.script, f"Performs a basic network sale with discount with {card}", "pass", run_time, True)
        if failure:
            tc_fail(f"Failed to perform a Sale with Discount with at least one card")

    @test
    def debit_sale_with_cashback(self):
        """
        Performs a debit sale getting cash back
        """
        pos.close()
        nw_cfg = {
            "Global Information" : {
				"Page 2" : {
					"Debit Cash Back Minimum" : "0.00",
					"Debit Cash Back Maximum" : "50.00",
					"EBT Cash Back Minimum" : "0.00",
					"EBT Cash Back Maximum" : "0.00",
					"Debit Cash Back Fee" : "0.00",
					"Debit Sale Fee" : "0.00"
				}
			}
        }
        nw = network_site_config.NetworkSetup()
        nw.configure_fields(config=nw_cfg)
        mws.click_toolbar("Save")

        pos.connect(url = 'https://127.0.0.1:7501')
        #TODO Configure Cashback

        #Set some variables needed to only run the cards we want
        execute_list = []
        #TODO Temporarily exclude "EMVVisaUSDebit", "EMVMaestro", "EMVUSMaestro", "EMVDiscoverUSDebit" while we find out why they cant be used for cashback
        exclude_list = ["Loyalty", "EMVAmEx", "EMVVisaUSDebit", "EMVMaestro", "EMVUSMaestro", "EMVDiscoverUSDebit"]

        if self.card_list:
            self.log.info("Found a card list. Will use that when verifying which cards to execute")

        #TODO: Make the card_group dynamic
        card_group = self.cards["CORE"]
        for card_name in card_group:
            exclude = False
            include = False
            #Check the card against the list of cards we want to run, if it exists
            if self.card_list:
                for includes in self.card_list:
                    if card_name == includes:
                        include = True
                        break
                if include:
                    self.log.info(f"Adding card: {card_name}")
                    continue
            #Check the card against the list of cards we do not want to run
            for excludes in exclude_list:
                if excludes == "FuelOnly" or excludes == "Expired":
                    if excludes in card_name:
                        exclude = True
                        break
                else:
                    if excludes == card_name:
                        exclude = True
                        break
            try:
                if (not self.cards["CORE"][card_name]["PaymentType"] == "Debit"):
                    self.log.info(f"Card payment type is not Debit, excluding the card {card_name}")
                    exclude = True
            except Exception as e:
                self.log.warning(f"Found exception {e} while checking card {card_name} payment type.")
                exclude = True
            if exclude:
                self.log.info(f"Excluding card: {card_name}") 
                continue
            self.log.info(f"Adding card: {card_name}")
            execute_list.append(card_name)
        #Set the variable we use to decide what to log for the whole method with test_harness
        #If a single card fails we want to mark a fail for the whole method
        failure = False

        for card in execute_list:
            #Set the test start time
            test_start = time.time()
            self.log.info(f"Current card in execute list: {card}")

            #Run the transaction
            #TODO: Make the card_group dynamic
            if not Network_Transactions_Functions.cashback_sale_func([card, "CORE"], cashback_amount = "1.00"):
                self.log.error(f"Cashback failed for card: {card}")
                run_time = self.get_runtime(test_start)
                self.res.record("debit_sale_with_cashback", self.script, f"Performs a cashback sale with {card}", "fail", run_time, True)
                failure = True
            else:
                self.log.info(f"Successful cashback sale with: {card}")
                run_time = self.get_runtime(test_start)
                self.res.record("debit_sale_with_cashback", self.script, f"Performs a cashback sale with: {card}", "pass", run_time, True)

        #Return Network config to clean state
        pos.close()
        nw_cfg = {
            "Global Information" : {
				"Page 2" : {
					"Debit Cash Back Minimum" : "0.00",
					"Debit Cash Back Maximum" : "0.00",
					"EBT Cash Back Minimum" : "0.00",
					"EBT Cash Back Maximum" : "0.00",
					"Debit Cash Back Fee" : "0.00",
					"Debit Sale Fee" : "0.00"
				}
			}
        }
        nw = network_site_config.NetworkSetup()
        nw.configure_fields(config=nw_cfg)
        mws.click_toolbar("Save")

        pos.connect(url = 'https://127.0.0.1:7501')

        #Raise the failure after resetting the configuration above
        if failure:
            tc_fail(f"Failed to perform a Debit Sale with Cashback with at least one card")

    @test
    def debit_sale_with_sale_fee(self):
        """
        Performs a debit sale with a sale fee
        """
        pos.close()
        nw_cfg = {
            "Global Information" : {
				"Page 2" : {
					"Debit Cash Back Minimum" : "0.00",
					"Debit Cash Back Maximum" : "0.00",
					"EBT Cash Back Minimum" : "0.00",
					"EBT Cash Back Maximum" : "0.00",
					"Debit Cash Back Fee" : "0.00",
					"Debit Sale Fee" : "1.00"
				}
			}
        }
        nw = network_site_config.NetworkSetup()
        nw.configure_fields(config=nw_cfg)
        mws.click_toolbar("Save")

        pos.connect(url = 'https://127.0.0.1:7501')
        #TODO Configure Cashback

        #Set some variables needed to only run the cards we want
        execute_list = []
        #TODO Temporarily exclude "EMVVisaUSDebit", "EMVMaestro", "EMVUSMaestro", "EMVDiscoverUSDebit" while we find out why they cant be used for cashback
        exclude_list = ["Loyalty", "EMVAmEx", "EMVVisaUSDebit", "EMVMaestro", "EMVUSMaestro", "EMVDiscoverUSDebit"]

        if self.card_list:
            self.log.info("Found a card list. Will use that when verifying which cards to execute")

        #TODO: Make the card_group dynamic
        card_group = self.cards["CORE"]
        for card_name in card_group:
            exclude = False
            include = False
            #Check the card against the list of cards we want to run, if it exists
            if self.card_list:
                for includes in self.card_list:
                    if card_name == includes:
                        include = True
                        break
                if include:
                    self.log.info(f"Adding card: {card_name}")
                    continue
            #Check the card against the list of cards we do not want to run
            for excludes in exclude_list:
                if excludes == "FuelOnly" or excludes == "Expired":
                    if excludes in card_name:
                        exclude = True
                        break
                else:
                    if excludes == card_name:
                        exclude = True
                        break
            try:
                if (not self.cards["CORE"][card_name]["PaymentType"] == "Debit"):
                    self.log.info(f"Card payment type is not Debit, excluding the card {card_name}")
                    exclude = True
            except Exception as e:
                self.log.warning(f"Found exception {e} while checking card {card_name} payment type.")
                exclude = True
            if exclude:
                self.log.info(f"Excluding card: {card_name}") 
                continue
            self.log.info(f"Adding card: {card_name}")
            execute_list.append(card_name)
        #Set the variable we use to decide what to log for the whole method with test_harness
        #If a single card fails we want to mark a fail for the whole method
        failure = False

        for card in execute_list:
            #Set the test start time
            test_start = time.time()
            self.log.info(f"Current card in execute list: {card}")

            #Run the transaction
            #TODO: Make the card_group dynamic
            if not Network_Transactions_Functions.debit_sale_fee_func([card, "CORE"]):
                self.log.error(f"Debit sale fee failed for card: {card}")
                run_time = self.get_runtime(test_start)
                self.res.record("debit_sale_with_sale_fee", self.script, f"Performs a debit sale fee with {card}", "fail", run_time, True)
                failure = True
            else:
                self.log.info(f"Successful cashback sale with: {card}")
                run_time = self.get_runtime(test_start)
                self.res.record("debit_sale_with_sale_fee", self.script, f"Performs a debit sale fee with: {card}", "pass", run_time, True)

        #Return Network config to clean state
        pos.close()
        nw_cfg = {
            "Global Information" : {
				"Page 2" : {
					"Debit Cash Back Minimum" : "0.00",
					"Debit Cash Back Maximum" : "0.00",
					"EBT Cash Back Minimum" : "0.00",
					"EBT Cash Back Maximum" : "0.00",
					"Debit Cash Back Fee" : "0.00",
					"Debit Sale Fee" : "0.00"
				}
			}
        }
        nw = network_site_config.NetworkSetup()
        nw.configure_fields(config=nw_cfg)
        mws.click_toolbar("Save")

        pos.connect(url = 'https://127.0.0.1:7501')

        #Raise the failure after resetting the configuration above
        if failure:
            tc_fail(f"Failed to perform a Debit Sale with Sale Fee with at least one card")
    
    @test 
    def debit_sale_with_cashback_fee(self):
        """
        Performs a debit sale getting cash back with a fee
        """
        pos.close()
        nw_cfg = {"Global Information" : {
				"Page 2" : {
					"Debit Cash Back Minimum" : "0.00",
					"Debit Cash Back Maximum" : "50.00",
					"EBT Cash Back Minimum" : "0.00",
					"EBT Cash Back Maximum" : "0.00",
					"Debit Cash Back Fee" : "1.00",
					"Debit Sale Fee" : "0.00"
				}
			}
        }
        nw = network_site_config.NetworkSetup()
        nw.configure_fields(config=nw_cfg)
        mws.click_toolbar("Save")

        pos.connect(url = 'https://127.0.0.1:7501')
        #TODO Configure Cashback

        #Set some variables needed to only run the cards we want
        execute_list = []
        #TODO Temporarily exclude "EMVVisaUSDebit", "EMVMaestro", "EMVUSMaestro", "EMVDiscoverUSDebit" while we find out why they cant be used for cashback
        exclude_list = ["Loyalty", "EMVAmEx", "EMVVisaUSDebit", "EMVMaestro", "EMVUSMaestro", "EMVDiscoverUSDebit"]

        if self.card_list:
            self.log.info("Found a card list. Will use that when verifying which cards to execute")

        #TODO: Make the card_group dynamic
        card_group = self.cards["CORE"]
        for card_name in card_group:
            exclude = False
            include = False
            #Check the card against the list of cards we want to run, if it exists
            if self.card_list:
                for includes in self.card_list:
                    if card_name == includes:
                        include = True
                        break
                if include:
                    self.log.info(f"Adding card: {card_name}")
                    continue
            #Check the card against the list of cards we do not want to run
            for excludes in exclude_list:
                if excludes == "FuelOnly" or excludes == "Expired":
                    if excludes in card_name:
                        exclude = True
                        break
                else:
                    if excludes == card_name:
                        exclude = True
                        break
            try:
                if (not self.cards["CORE"][card_name]["PaymentType"] == "Debit"):
                    self.log.info(f"Card payment type is not Debit, excluding the card {card_name}")
                    exclude = True
            except Exception as e:
                self.log.warning(f"Found exception {e} while checking card {card_name} payment type.")
                exclude = True
            if exclude:
                self.log.info(f"Excluding card: {card_name}") 
                continue
            self.log.info(f"Adding card: {card_name}")
            execute_list.append(card_name)
        #Set the variable we use to decide what to log for the whole method with test_harness
        #If a single card fails we want to mark a fail for the whole method
        failure = False

        for card in execute_list:
            #Set the test start time
            test_start = time.time()
            self.log.info(f"Current card in execute list: {card}")

            #Run the transaction
            #TODO: Make the card_group dynamic
            if not Network_Transactions_Functions.cashback_fee_sale_func([card, "CORE"], cashback_amount = "1.00"):
                self.log.error(f"Cashback fee failed for card: {card}")
                run_time = self.get_runtime(test_start)
                self.res.record("debit_sale_with_cashback_fee", self.script, f"Performs a cashback fee sale with {card}", "fail", run_time, True)
                failure = True
            else:
                self.log.info(f"Successful cashback fee sale with: {card}")
                run_time = self.get_runtime(test_start)
                self.res.record("debit_sale_with_cashback_fee", self.script, f"Performs a cashback fee sale with: {card}", "pass", run_time, True)

        #Return Network config to clean state
        pos.close()
        nw_cfg = {
            "Global Information" : {
				"Page 2" : {
					"Debit Cash Back Minimum" : "0.00",
					"Debit Cash Back Maximum" : "0.00",
					"EBT Cash Back Minimum" : "0.00",
					"EBT Cash Back Maximum" : "0.00",
					"Debit Cash Back Fee" : "0.00",
					"Debit Sale Fee" : "0.00"
				}
			}
        }
        nw = network_site_config.NetworkSetup()
        nw.configure_fields(config=nw_cfg)
        mws.click_toolbar("Save")

        pos.connect(url = 'https://127.0.0.1:7501')

        #Raise the failure after resetting the configuration above
        if failure:
            tc_fail(f"Failed to perform a Debit Sale with Cashback Fee with at least one card")

    @test 
    def debit_sale_with_cashback_fee_sale_fee(self):
        """
        Performs a debit sale getting cash back with a fee and sale fee
        """
        pos.close()
        nw_cfg = {"Global Information" : {
				"Page 2" : {
					"Debit Cash Back Minimum" : "0.00",
					"Debit Cash Back Maximum" : "50.00",
					"EBT Cash Back Minimum" : "0.00",
					"EBT Cash Back Maximum" : "0.00",
					"Debit Cash Back Fee" : "1.00",
					"Debit Sale Fee" : "2.00"
				}
			}
        }
        nw = network_site_config.NetworkSetup()
        nw.configure_fields(config=nw_cfg)
        mws.click_toolbar("Save")

        pos.connect(url = 'https://127.0.0.1:7501')
        #TODO Configure Cashback

        #Set some variables needed to only run the cards we want
        execute_list = []
        #TODO Temporarily exclude "EMVVisaUSDebit", "EMVMaestro", "EMVUSMaestro", "EMVDiscoverUSDebit" while we find out why they cant be used for cashback
        exclude_list = ["Loyalty", "EMVAmEx", "EMVVisaUSDebit", "EMVMaestro", "EMVUSMaestro", "EMVDiscoverUSDebit"]

        if self.card_list:
            self.log.info("Found a card list. Will use that when verifying which cards to execute")

        #TODO: Make the card_group dynamic
        card_group = self.cards["CORE"]
        for card_name in card_group:
            exclude = False
            include = False
            #Check the card against the list of cards we want to run, if it exists
            if self.card_list:
                for includes in self.card_list:
                    if card_name == includes:
                        include = True
                        break
                if include:
                    self.log.info(f"Adding card: {card_name}")
                    continue
            #Check the card against the list of cards we do not want to run
            for excludes in exclude_list:
                if excludes == "FuelOnly" or excludes == "Expired":
                    if excludes in card_name:
                        exclude = True
                        break
                else:
                    if excludes == card_name:
                        exclude = True
                        break
            try:
                if (not self.cards["CORE"][card_name]["PaymentType"] == "Debit"):
                    self.log.info(f"Card payment type is not Debit, excluding the card {card_name}")
                    exclude = True
            except Exception as e:
                self.log.warning(f"Found exception {e} while checking card {card_name} payment type.")
                exclude = True
            if exclude:
                self.log.info(f"Excluding card: {card_name}") 
                continue
            self.log.info(f"Adding card: {card_name}")
            execute_list.append(card_name)
        #Set the variable we use to decide what to log for the whole method with test_harness
        #If a single card fails we want to mark a fail for the whole method
        failure = False

        for card in execute_list:
            #Set the test start time
            test_start = time.time()
            self.log.info(f"Current card in execute list: {card}")

            #Run the transaction
            #TODO: Make the card_group dynamic
            if not Network_Transactions_Functions.cashback_fee_sale_fee_func([card, "CORE"], cashback_amount = "1.00"):
                self.log.error(f"Cashback fee failed for card: {card}")
                run_time = self.get_runtime(test_start)
                self.res.record("debit_sale_with_cashback_fee_sale_fee", self.script, f"Performs a cashback fee sale fee with {card}", "fail", run_time, True)
                failure = True
            else:
                self.log.info(f"Successful cashback fee sale with: {card}")
                run_time = self.get_runtime(test_start)
                self.res.record("debit_sale_with_cashback_fee_sale_fee", self.script, f"Performs a cashback fee sale fee with: {card}", "pass", run_time, True)

        #Return Network config to clean state
        pos.close()
        nw_cfg = {
            "Global Information" : {
				"Page 2" : {
					"Debit Cash Back Minimum" : "0.00",
					"Debit Cash Back Maximum" : "0.00",
					"EBT Cash Back Minimum" : "0.00",
					"EBT Cash Back Maximum" : "0.00",
					"Debit Cash Back Fee" : "0.00",
					"Debit Sale Fee" : "0.00"
				}
			}
        }
        nw = network_site_config.NetworkSetup()
        nw.configure_fields(config=nw_cfg)
        mws.click_toolbar("Save")

        pos.connect(url = 'https://127.0.0.1:7501')

        #Raise the failure after resetting the configuration above
        if failure:
            tc_fail(f"Failed to perform a Debit Sale with Cashback Fee with at least one card")

    @test 
    def debit_sale_with_cashback_sale_fee(self):
        """
        Performs a debit sale getting cash back with a sale fee
        """
        pos.close()
        nw_cfg = {"Global Information" : {
				"Page 2" : {
					"Debit Cash Back Minimum" : "0.00",
					"Debit Cash Back Maximum" : "50.00",
					"EBT Cash Back Minimum" : "0.00",
					"EBT Cash Back Maximum" : "0.00",
					"Debit Cash Back Fee" : "0.00",
					"Debit Sale Fee" : "2.00"
				}
			}
        }
        nw = network_site_config.NetworkSetup()
        nw.configure_fields(config=nw_cfg)
        mws.click_toolbar("Save")

        pos.connect(url = 'https://127.0.0.1:7501')
        #TODO Configure Cashback

        #Set some variables needed to only run the cards we want
        execute_list = []
        #TODO Temporarily exclude "EMVVisaUSDebit", "EMVMaestro", "EMVUSMaestro", "EMVDiscoverUSDebit" while we find out why they cant be used for cashback
        exclude_list = ["Loyalty", "EMVAmEx", "EMVVisaUSDebit", "EMVMaestro", "EMVUSMaestro", "EMVDiscoverUSDebit"]

        if self.card_list:
            self.log.info("Found a card list. Will use that when verifying which cards to execute")

        #TODO: Make the card_group dynamic
        card_group = self.cards["CORE"]
        for card_name in card_group:
            exclude = False
            include = False
            #Check the card against the list of cards we want to run, if it exists
            if self.card_list:
                for includes in self.card_list:
                    if card_name == includes:
                        include = True
                        break
                if include:
                    self.log.info(f"Adding card: {card_name}")
                    continue
            #Check the card against the list of cards we do not want to run
            for excludes in exclude_list:
                if excludes == "FuelOnly" or excludes == "Expired":
                    if excludes in card_name:
                        exclude = True
                        break
                else:
                    if excludes == card_name:
                        exclude = True
                        break
            try:
                if (not self.cards["CORE"][card_name]["PaymentType"] == "Debit"):
                    self.log.info(f"Card payment type is not Debit, excluding the card {card_name}")
                    exclude = True
            except Exception as e:
                self.log.warning(f"Found exception {e} while checking card {card_name} payment type.")
                exclude = True
            if exclude:
                self.log.info(f"Excluding card: {card_name}") 
                continue
            self.log.info(f"Adding card: {card_name}")
            execute_list.append(card_name)
        #Set the variable we use to decide what to log for the whole method with test_harness
        #If a single card fails we want to mark a fail for the whole method
        failure = False

        for card in execute_list:
            #Set the test start time
            test_start = time.time()
            self.log.info(f"Current card in execute list: {card}")

            #Run the transaction
            #TODO: Make the card_group dynamic
            if not Network_Transactions_Functions.cashback_sale_fee_func([card, "CORE"], cashback_amount = "1.00"):
                self.log.error(f"Cashback fee failed for card: {card}")
                run_time = self.get_runtime(test_start)
                self.res.record("debit_sale_with_cashback_sale_fee", self.script, f"Performs a cashback sale fee with {card}", "fail", run_time, True)
                failure = True
            else:
                self.log.info(f"Successful cashback sale fee sale with: {card}")
                run_time = self.get_runtime(test_start)
                self.res.record("debit_sale_with_cashback_sale_fee", self.script, f"Performs a cashback sale fee with: {card}", "pass", run_time, True)

        #Return Network config to clean state
        pos.close()
        nw_cfg = {
            "Global Information" : {
				"Page 2" : {
					"Debit Cash Back Minimum" : "0.00",
					"Debit Cash Back Maximum" : "0.00",
					"EBT Cash Back Minimum" : "0.00",
					"EBT Cash Back Maximum" : "0.00",
					"Debit Cash Back Fee" : "0.00",
					"Debit Sale Fee" : "0.00"
				}
			}
        }
        nw = network_site_config.NetworkSetup()
        nw.configure_fields(config=nw_cfg)
        mws.click_toolbar("Save")

        pos.connect(url = 'https://127.0.0.1:7501')

        #Raise the failure after resetting the configuration above
        if failure:
            tc_fail(f"Failed to perform a Debit Sale with Cashback Fee with at least one card")
    
    @test
    def reversal_sale(self):
        """
        Performs a reversal sale
        """
        #Set some variables needed to only run the cards we want
        execute_list = []
        exclude_list = ["FuelOnly", "Expired", "Loyalty", "EMVAmEx", "Fuelman"]

        if self.card_list:
            self.log.info("Found a card list. Will use that when verifying which cards to execute")

        #TODO: Make the card_group dynamic
        card_group = self.cards["CORE"]
        for card_name in card_group:
            exclude = False
            include = False
            #Check the card against the list of cards we want to run, if it exists
            if self.card_list:
                for includes in self.card_list:
                    if card_name == includes:
                        include = True
                        break
                if include:
                    self.log.info(f"Adding card: {card_name}")
                    continue
            #Check the card against the list of cards we do not want to run
            for excludes in exclude_list:
                if excludes == "FuelOnly" or excludes == "Expired":
                    if excludes in card_name:
                        exclude = True
                        break
                else:
                    if excludes == card_name:
                        exclude = True
                        break
            if exclude:
                self.log.info(f"Excluding card: {card_name}") 
                continue
            self.log.info(f"Adding card: {card_name}")
            execute_list.append(card_name)
        failure = False

        for card in execute_list:
            #Set the test start time
            test_start = time.time()
            self.log.info(f"Current card in execute list: {card}")
            #Run the transaction
            #TODO: Make the card_group dynamic
            if not Network_Transactions_Functions.refund_func([card, "CORE"], item_info = [['002', 'Item 2', 5], ['008', 'Item 8', 5]], refund_list = [['002', 'Item 2', 5], ['008', 'Item 8', 5]]):
                self.log.error(f"Receipt not displaying expected items or total for the card: {card}")
                run_time = self.get_runtime(test_start)
                self.res.record("reversal_sale", self.script, f"Performs a reversal with {card}", "fail", run_time, True)
                failure = True
            else:
                self.log.info(f"Successful performed a reversal with the card: {card}")
                run_time = self.get_runtime(test_start)
                self.res.record("reversal_sale", self.script, f"Performs a reversal with {card}", "pass", run_time, True)
        if failure:
            tc_fail(f"Failed to perform a Reversal with at least one card")

    # @test
    def saf_sale(self):
        """Performs a saf (store and forward) sale **No Debit Cards Allowed**
        Args: None
        Returns: None
        """
        saf1_cfg = {
            "network" : True,
            "Concord/Valero" : {
                "Network Connection Options" : {
                    "Page 3" : {
                        "Host IP Address" : "1.2.3.4",
                        "IP Port" : "8085"
                    }
                },
                "Store & Forward Parameters" : {
                    "Store & Forward Warning Count Percent" : "99",
                    "Store & Forward Warning Total Percent" : "99",
                    "Maximum Store & Forward Count" : "9995",
                    "Maximum Store & Forward Total" : "9995"
                }
            }
        }

        #TODO go into network settings and change ip to a dumby ip

        #Cycle through CardData.json to find CORE Group
        for (card_group, card_name) in self.cards.items():
            if (card_group == "CORE"):
                #Cycle through CORE card group to use each card within
                for (card_name, card_data) in self.cards['CORE'].items():
                    if (not ("FuelOnly" in card_name or "Expired" in card_name or "Loyalty" in card_name or "Debit" in card_name or "EMVAmEx" in card_name)):
                        self.log.info("Adding item 002")
                        pos.add_item("002", "PLU")
                        self.log.info(f"Name of card about to be swiped: {card_name}")
                        #Use current card in CardData.json CORE group to pay for sale
                        self.log.info(f"Tendering sale of item 002 with card: {card_name}")
                        pos.pay_card(brand=card_group, card_name=card_name)

                        # Check to make sure both items are on the receipt
                        self.log.info("Checking receipt for correct items, price and tender type")
                        if not pos.check_receipt_for(["Item 2 $5.00", "Item 2 $5.00", "Total = $5.00",  "$5.00"]):
                            self.log.info(f"Receipt not displaying expected items or total for the card: {card_name}")

        #TODO should i check the store and forward report for all the cards or just make sure the payment goes through and check receipt?
        #TODO go back into network menu and change back to working network ip.  Run another pdl
        saf2_cfg = {
            "network" : True,
            "Concord/Valero" : {
                "Network Connection Options" : {
                    "Page 3" : {
                        "Host IP Address" : "10.28.39.72",
                        "IP Port" : "8085"
                    }
                },
                "Store & Forward Parameters" : {
                    "Store & Forward Warning Count Percent" : "50",
                    "Store & Forward Warning Total Percent" : "50",
                    "Maximum Store & Forward Count" : "0",
                    "Maximum Store & Forward Total" : "0"
                }
            }
        }

    @test
    def manual_entry(self):
        """
        Performs a transaction with manually entering the card information
        """
        #Set some variables needed to only run the cards we want
        execute_list = []
        #NOTE: Wex and Voyager return Unknown Card Type
        exclude_list = ["FuelOnly", "Expired", "Loyalty", "EMVAmEx", "WEX1", "WEX2", "Voyager"]
        #NOTE: Exclude Amex and Debit until we handle their prompts on screen - "Is this a Gulf card"
        exclude_list.extend(["AmEx", "Debit"])
        #Cards that prompt "Is this an American Express card"
        exclude_list.extend(['AmExTrack1Track2'])
        #Cards that prompt "Is this an Auxiluary Network Card"
        exclude_list.extend(['VisaPurchase'])
        #Cards the prompt "Unknown card type"
        exclude_list.extend(['VisaPurchaseTrack1'])

        #TODO: Make the card_group dynamic
        card_group = self.cards["CORE"]
        for card_name in card_group:
            exclude = False
            include = False
            #Check the card against the list of cards we want to run, if it exists
            if self.card_list:
                self.log.info("Found a card list.")
                for includes in self.card_list:
                    if card_name == includes:
                        include = True
                        break
                if not include:
                    self.log.info(f"Found a card in CardData not in the provided Card List: {card_name}")
                    continue
            else:
                self.log.info("No card list was found.")
            #Check the card against the list of cards we do not want to run
            for excludes in exclude_list:
                if excludes == "FuelOnly" or excludes == "Expired":
                    if excludes in card_name:
                        exclude = True
                        break
                else:
                    if excludes == card_name:
                        exclude = True
                        break
            if exclude:
                self.log.info(f"Excluding card: {card_name} from the execute list.") 
                continue
            #TODO: Add a check for if the card_number matches any others in the execute list
            self.log.info(f"Adding card: {card_name} to the execute list.")
            execute_list.append(card_name)
        #Set the variable we use to decide what to log for the whole method with test_harness
        #If a single card fails we want to mark a fail for the whole method
        failure = False

        for card in execute_list:
            #Set the test start time
            test_start = time.time()
            self.log.info(f"Current card in execute list: {card}")
            #Run the transaction
            #TODO: Make the card_group dynamic
            if not Network_Transactions_Functions.manual_entry_func([card, "CORE"]):
                self.log.error(f"Failed manual entry with {card}")
                run_time = self.get_runtime(test_start)
                self.res.record("manual_entry", self.script, f"Performs a sale with manual entry with {card}", "fail", run_time, True)
                failure = True
            else:
                self.log.info(f"Successful transaction with {card} in manual entry")
                run_time = self.get_runtime(test_start)
                self.res.record("manual_entry", self.script, f"Performs a manual entry sale with {card}", "pass", run_time, True)
        if failure:
            tc_fail(f"Failed to perform a Manual Entry Sale with at least one card")

    @test
    def manual_entry_card_decline(self):
        """
        Performs a transaction with manually entering the card information
        """
        #NOTE Cannot run FuelOnly cards because manual entry doesn't look at that part of the track.  It wil be accepted.
        #Set some variables needed to only run the cards we want
        execute_list = []
        exclude_list = ["Loyalty", "EMVAmEx"]

        if self.card_list:
            self.log.info("Found a card list. Will use that when verifying which cards to execute")

        #TODO: Make the card_group dynamic
        card_group = self.cards["CORE"]
        for card_name in card_group:
            exclude = False
            include = False
            #Check the card against the list of cards we want to run, if it exists
            if self.card_list:
                for includes in self.card_list:
                    if card_name == includes:
                        include = True
                        break
                if include:
                    self.log.info(f"Adding card: {card_name}")
                    continue
            #Check the card against the list of cards we do not want to run
            for excludes in exclude_list:
                if excludes == "FuelOnly" or excludes == "Expired":
                    if excludes in card_name:
                        exclude = True
                        break
                else:
                    if excludes == card_name:
                        exclude = True
                        break
            if ("Expired" not in card_name):
                exclude = True
            if exclude:
                self.log.info(f"Excluding card: {card_name}") 
                continue
            self.log.info(f"Adding card: {card_name}")
            execute_list.append(card_name)
        #Set the variable we use to decide what to log for the whole method with test_harness
        #If a single card fails we want to mark a fail for the whole method
        failure = False

        for card in execute_list:
            #Set the test start time
            test_start = time.time()
            self.log.info(f"Current card in execute list: {card}")
            #Run the transaction
            #TODO: Make the card_group dynamic
            if not Network_Transactions_Functions.manual_entry_decline_func(card_info = [card, "CORE"], expiration_date='1215', decline_prompt='Expired Card: Try Another'):
                self.log.error(f"Sale with manual entry decline failed for card: {card}")
                run_time = self.get_runtime(test_start)
                self.res.record("manual_entry_card_decline", self.script, f"Performs a sale with manual entry decline with {card}", "fail", run_time, True)
                failure = True
            else:
                self.log.info(f"Successful sale with manual entry decline with the card: {card}")
                run_time = self.get_runtime(test_start)
                self.res.record("manual_entry_card_decline", self.script, f"Performs a sale with manual entry decline with {card}", "pass", run_time, True)
        if failure:
            tc_fail(f"Failed to perform a Manual Entry Decline with at least one card")
    
    def get_runtime(self, test_start):

        delta = time.time()-test_start
        m, s = divmod(delta, 60)
        h, m = divmod(m, 60)
        run_time = f"{int(h):02}:{int(m):02}:{int(s):02}"
        return run_time

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        # Begin till close
        pos.click_function_key("Close Till")

        # Check for correct prompt and accept
        self.log.info("Checking for prompt to close till.")
        if pos.read_message_box(timeout = 3) != "Do you want to close your till?":
            self.log.warning(f"Message prompt: {pos.read_message_box()}")
            tc_fail("Missing/incorrect message box prompt")
        self.log.info("Selecting Yes to close the till.")
        pos.click_message_box_key("Yes", timeout = 3)
        # close current instance of Chrome (temporary)
        pos.close()