"""
    File name: PEACOCK_4159.py
    Brand: CITGO
    Description: [PEACOCK-4159] This will verify that card is renamed 
                to CITGO Plus -> CITGO REWARDS (Card Type 01 - ISO 709900)
    Author: Asha Sangrame
    Date created: 2020-07-14 12:53:24
    Date last modified:
    Python Version: 3.7
"""


import logging, time
from app import Navi, mws, pos, system, store_close, crindsim, pinpad
from app import networksim, OCR
from app.framework.tc_helpers import setup, test, teardown, tc_fail


class PEACOCK_4159():
    """
    Description: Test class that provides an interface for testing.
    """
    def __init__(self):
        """Initializes the Template class.
        Args: None
        Returns: None
        """
        # The logging object. 
        # Example: self.log.info(f"Current value of var: {my_var}")
        self.log = logging.getLogger()

        self.fuel_amount = "$1.00"
        self.fuel_grade = "Diesel 1"    

    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        # set mode for networksim
        networksim.set_response_mode("Automated")

        # Navigate to MWS
        Navi.navigate_to("MWS")       
    
    def fetch_ref_no(self):
        """
        This is helper method to fetch reference number for refund sale.
        """
        pos.click_function_key("SEARCH")

        pos.select_receipt(1)

        receipt = pos.read_receipt()

        pos.click("CANCEL")

        for e in receipt:
            if e.find("REF") != -1:
                ref_no = e[e.find('REF')+4:]      
                break

        return ref_no
    
    @test
    def TC01(self):
        """
        Zephyr Id : This will Verify that CITGO PLUS card is successfully
                    renamed as CITGO REWARDS card in "Card Info Editor"
        Args: None
        Returns: None
        """        
        Navi.navigate_to("Card Info Editor")

        card_list = mws.get_value("Card List")

        # Check if Citgo Rewards is available in card list
        card_found = False
        for card in card_list:
            if card == "CITGO REWARDS":
                self.log.info(f"{card} found in list")
                card_found = True
                break

        if not card_found:
            tc_fail("Citgo Rewards card not found in list")

        # Check if Citgo Plus is not available in card list
        card_not_found = False
        for card in card_list:
            if card == "CITGO PLUS":
                self.log.error(f"{card} found in list")
                card_not_found = True
                break

        if card_not_found:
            tc_fail("Citgo plus card found in list")

        mws.select("Card List", "CITGO REWARDS")

        # Verify Response auth field is present on screen
        if not OCR.findText("Response Auth"):
            tc_fail("Response auth field is available on screen")

        item_found = False
        expected_list = ['HOST RSP', 'CARD ID', 'ON TRANS']
        response_auth_list = mws.get_value("Response Auth")

        # Verify Response auth field is having default value as HOST RSP
        if not response_auth_list[0] == "HOST RSP":
            tc_fail("Default value is not as expected for Response auth field")

        # Verify Response auth field is having all value as expected in list
        for exp_item in expected_list:
            for item in response_auth_list:
                if exp_item == item:
                    item_found = True
                    break

        if not item_found:
            tc_fail(f"Expected value not found in Response Auth field")

        if not mws.click_toolbar("Cancel"):
            self.log.error("Not able to click on cancel")
            return False

        if 'Do you want to save changes?' in mws.get_top_bar_text():
            mws.click_toolbar("NO")
        else:
            self.log.error("Not able to click on 'No'")
            return False

    @test
    def TC02(self):
        """
        Zephyr Id : This will Verify that CITGO PLUS card is successfully
                    renamed as CITGO REWARDS card in "Fuel Discount Configuration"
        Args: None
        Returns: None
        """        
        Navi.navigate_to("Fuel Discount Configuration")

        card_list = mws.get_value("Cards")

        # Check if Citgo Rewards is available in card list
        card_found = False
        for card in card_list:
            if card == "CITGO REWARDS":
                self.log.info(f"{card} found in list")
                card_found = True
                break

        if not card_found :
            tc_fail("Citgo Rewards card not found in list")

        # Check if Citgo Plus is not available in card list
        card_not_found = False
        for card in card_list:
            if card == "CITGO PLUS":
                self.log.error(f"{card} found in list")
                card_not_found = True
                break

        if card_not_found:
            tc_fail("Citgo plus card found in list")

        mws.select("Cards", "CITGO REWARDS")

        # Verify Discount Group field is present on screen
        if not OCR.findText("Discounting Group"):
            tc_fail("Discount Groupfield is available on screen")

        discount_group_list = mws.get_value("Discount Group")

        # Verify Response auth field is having default value as HOST RSP
        if not discount_group_list[0] == "NONE":
            tc_fail("Default value is not as expected for discount group field")

        if not mws.click_toolbar("Cancel"):
            self.log.error("Not able to click on cancel")
            return False

        if 'Do you want to save changes?' in mws.get_top_bar_text():
            mws.click_toolbar("NO")
        else:
            self.log.error("Not able to click on 'No'")
            return False

    @test
    def TC05(self):
        """
        Zephyr Id : This will Verify that "CITGO REWARDS" is showing in the receipt as a card name 
                    when perform inside fuel sale transaction with CITGO REWARDS card having bin range "709900"
        Args: None
        Returns: None
        """
        # Navigating to pos and open till
        Navi.navigate_to("POS")
        
        # Sign on to POS screen if not already sign-on
        pos.sign_on()

        # Perform store close for CITGO brand to accept card transaction
        SC = store_close.StoreClose()
        if not SC.begin_store_close():
            self.log.error("There was an issue with the Store Close")
        
        # Navigate to POS
        Navi.navigate_to("POS")
        
        # Sign on to POS screen if not already sign-on
        pos.sign_on()
        
        # Wait for dispenser to finish downloading
        if not pos.wait_disp_ready(idle_timeout=90):
            return False
        
        # Add fuel in prepay mode
        pos.add_fuel(self.fuel_amount, grade=self.fuel_grade)
        
        # Perform card Payment with Citgo rewards Card
        pos.pay_card(brand=system.get_brand(), card_name="Citgo_Rewards")
        
        # Wait until dispenser 1 is idle
        if not pos.wait_for_disp_status('IDLE'):
            return False

        # Verifying details from receipt
        if not pos.check_receipt_for(["025 CITGOREWARDS"]):
           tc_fail("Card details not matched with receipt")

    @test
    def TC06(self):
        """
        Zephyr Id : This will Verify that "CITGO REWARDS" is showing in the receipt as a card name 
                    when perform dry stock item sale transaction with CITGO REWARDS card having bin range "709900"
        Args: None
        Returns: None
        """
        # Add Dry Stock Item
        pos.add_item("002", method="PLU")
        
        # Perform card Payment with Citgo rewards card
        pos.pay_card(brand=system.get_brand(), card_name="Citgo_Rewards")
        
        # Verifying details from receipt
        if not pos.check_receipt_for(["025 CITGOREWARDS"]):
           tc_fail("Card details not matched with receipt")

    @test
    def TC07(self):
        """
        Zephyr Id : This will Verify that "CITGO REWARDS" is showing in the receipt as a card name 
                    when perform outside fuel sale transaction with CITGO REWARDS card having bin range "709900"
        Args: None
        Returns: None
        """
        # perform outside sale with fuel
        if not crindsim.crind_sale(brand=system.get_brand(), card_name="Citgo_Rewards", carwash="no"):
            tc_fail("outside transaction not successfull")

        receipt = crindsim.get_receipt()

        self.log.info(f"Receipt is {receipt}")

        # Verifying details from receipt
        if "CITGOREWARDS" not in receipt:
            tc_fail("Card details not matched with receipt")

    @test
    def TC08(self):
        """
        Zephyr Id : This will Verify that "CITGO REWARDS" is showing in the receipt as a card name 
                    when perform refund for dry stock item & manual fuel sale transaction with CITGO REWARDS card having bin range "709900"
        Args: None
        Returns: None
        """
        # Add fuel in manual mode
        pos.add_fuel(self.fuel_amount, mode="manual", grade=self.fuel_grade)

        # Add dry stock item
        pos.add_item("002", method="PLU")

        # Perform card Payment with Citgo rewards Card
        pos.pay_card(brand=system.get_brand(), card_name="Citgo_Rewards")

        # fetch reference number
        ref_no = self.fetch_ref_no()

        # Perform refund transaction
        pos.click("REFUND")

        pos.add_fuel(self.fuel_amount, mode="manual", grade=self.fuel_grade)

        pos.add_item("002", method="PLU")

        # paying using Citgo reward Card
        if not pos.click_function_key('Pay', timeout=3):
            return False
        if not pos.click_tender_key("Card"):
            return False
        try:
            pinpad.use_card(brand=system.get_brand(), card_name="Citgo_Rewards")
            time.sleep(5)
        except Exception as e:
            self.log.warning(f"swipe Card in pinpad failed. Exception: {e}")
            pos.click_keypad("CANCEL")
            return False

        pos.enter_keypad(ref_no)  

        pos.click_pwd_key("OK")

        if not pos.verify_idle(timeout=40):
            tc_fail("Transaction Failed pos was not idle")

        #Verifying details from receipt
        if not pos.check_receipt_for(["025 CITGOREWARDS"]):
           tc_fail("Card details not matched with receipt")

    @test
    def TC09(self):
        """
        Zephyr Id : This will Verify that "CITGO REWARDS" is showing in the receipt as a card name 
                    when perform inside fuel and dry stock item sale transaction by manual card entry 
                    with CITGO REWARDS card having bin range "709900"
        Args: None
        Returns: None
        """
        # Add fuel in prepay mode
        pos.add_fuel(self.fuel_amount, grade=self.fuel_grade)
        
        # Add Dry Stock Item
        pos.add_item("002", method="PLU")
        
        # Perform card Payment with Citgo rewards card
        pos.manual_entry(brand=system.get_brand(), card_name="Citgo_Rewards")
        
        # Verifying details from receipt
        if not pos.check_receipt_for(["025 CITGOREWARDS"]):
           tc_fail("Card details not matched with receipt")

    @test
    def TC10(self):
        """
        Zephyr Id : This will Verify that "CITGO REWARDS" is showing in the receipt as a card name 
                    when perform refund for dry stock item & manual fuel sale transaction 
                    by manual card entry with CITGO REWARDS card having bin range "709900"
        Args: None
        Returns: None
        """
        # Perform transaction to fetch reference number
        pos.add_fuel(self.fuel_amount, mode="manual", grade=self.fuel_grade)

        pos.add_item("002", method="PLU")

        # Perform card Payment with Citgo rewards Card
        pos.pay_card(brand=system.get_brand(), card_name="Citgo_Rewards")

        # fetch reference number
        ref_no = self.fetch_ref_no()

        # perform refund sale
        pos.click("REFUND")

        pos.add_fuel(self.fuel_amount, mode="manual", grade=self.fuel_grade)

        pos.add_item("002", method="PLU")

        # paying using MSD MasterCard Card
        if not pos.click_function_key('Pay', timeout=3):
            return False
        if not pos.click_tender_key("Card"):
            return False
        if not pos.click_keypad("Manual", verify=False):
            return False
        try:
            pinpad.manual_entry(brand=system.get_brand(), card_name="Citgo_Rewards")
            time.sleep(5)
        except Exception as e:
            self.log.warning(f"swipe Card in pinpad failed. Exception: {e}")
            pos.click_keypad("CANCEL")
            return False

        if not pos.click_message_box_key(key='Yes', verify=False):
            return False

        if pos.read_message_box() == "Is this an Auxiliary Network Card?":
            pos.click_message_box_key(key='No')

        if not pos.read_status_line() == "Enter Expiration Date":
            pos.enter_keypad("1230")
            pos.click_keypad("Enter")
            time.sleep(5)

        pos.enter_keypad(ref_no)

        pos.click_pwd_key("OK")

        if not pos.verify_idle(timeout=40):
            tc_fail("Transaction Failed pos was not idle")

        #Verifying details from receipt
        if not pos.check_receipt_for(["025 CITGOREWARDS"]):
           tc_fail("Card details not matched with receipt")

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        pass