"""
    File name: Identify_WEX_1.py
    Brand: Chevron
    Story ID : PEACOCK-3924
    Description: Verify that POS shall not use the service indicator
                 on the magnetic stripe to identify a chip card for WEX card products.
    Author: Asha
    Date created: 2020-05-11 13:00
    Python Version: 3.7
"""

import logging, time
from app import Navi, pos, system, pinpad
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class Identify_WEX_1():
    """
    Description: Test class that provides an interface for testing.
    """

    def __init__(self):
        """
        Initializes the Template class.
        Args: None
        Returns: None
        """
        # The logging object. 
        self.log = logging.getLogger()

        # initialising Variables
        self.fuel_amount = "$1.00"
        self.item_amount = "$0.01"
        self.fuel_grade = "UNL SUP CAN"    
        
    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        Args: None
        Returns: None
        """        
        # sign-on to POS
        Navi.navigate_to("POS")
        pos.sign_on()
                
    @test
    def postpay_wex_1(self):         
        """
        Zephyr Id: [TC3]This will Verify that postpay transaction completed successfully when
                    wex card of bin range 690046 with technology indicator not equals to 2 is swiped
        Args: None
        Returns: None
        """
        # wait for dispemser to be Ready
        if not pos.wait_disp_ready(idle_timeout=90):
            return False
        
        # Add fuel in preset mode
        pos.add_fuel(self.fuel_amount, mode="preset", grade=self.fuel_grade)
        
        # Check if fueling is completed
        if not pos.wait_for_disp_status("IDLE",timeout=40):
            return False

        # Take fuel inside POS
        pos.click_suspended_transaction()

        # add item with plu 1
        pos.add_item("1", method="PLU")

        # paying using WEX Card
        if not pos.click_function_key('Pay', timeout=3):
            return False
        if not pos.click_tender_key("Card"):
            return False

        # pay using wex ms card of bin range 690046
        try:            
            pinpad.use_card(brand=system.get_brand(), card_name="WEX1_MSD")
            time.sleep(10)
        except Exception as e:
            self.log.warning(f"Swipe Card in pinpad failed. Exception: {e}")
            pos.click_keypad("CANCEL")
            return False

        if not pos.verify_idle(timeout=60):
            tc_fail("Transaction Failed pos was not idle")
           
        fuel_amount = self.fuel_amount.replace("$","")

        item_amount = self.item_amount.replace("$","")

        # calculating total amount of sale
        sale_amount = float(fuel_amount) + float(item_amount)
        sale_amount = "Total=$" + str(sale_amount) 
        
        # Verifying Receipt
        if not pos.check_receipt_for(sale_amount):
           tc_fail("Sale amount not matched with receipt")

        return True
    
    @test
    def prepay_wex(self):     
        """
        Zephyr Id: [TC1 TC11] This will Verify that POS should display the message
                   to insert the card when wex card with technology indicator equals to 2 is swiped
        Args: None
        Returns: None
        """            
        # Add Fuel in prepay mode
        pos.add_fuel(self.fuel_amount, grade=self.fuel_grade)

        # add item with plu 1
        pos.add_item("1", method="PLU")
        
        # paying using WEX Card
        if not pos.click_function_key('Pay', timeout=3):
            return False
        if not pos.click_tender_key("Card"):
            return False
        
        # swipe wex emv card of bin range 690046 - TC1
        try:            
            pinpad.swipe_card(brand=system.get_brand(), card_name="WEX1_EMV")
            time.sleep(10)
        except Exception as e:
            self.log.warning(f"Swipe Card in pinpad failed. Exception: {e}")
            pos.click_keypad("CANCEL")
            return False

        # verify pos message
        if not pos.read_status_line() == 'Chip card, Please Insert':
            tc_fail("Required chip card error not came")

        # swipe wex emv card of bin range 707138 - TC11
        try:        
            pinpad.swipe_card(brand=system.get_brand(),card_name="WEX2_EMV")
            time.sleep(10)
        except Exception as e:
            self.log.warning(f"Swipe Card in pinpad failed. Exception: {e}")
            pos.click_keypad("CANCEL")
            return False

        # verify pos message
        if not pos.read_status_line() == 'Chip card, Please Insert':  
            tc_fail("emv chip not detected")

        # make the payment
        try:            
            pinpad.swipe_card()
        except Exception as e:
            self.log.warning(f"Swipe Card in pinpad failed. Exception: {e}")
            pos.click_keypad("CANCEL")
            return False

        # Check if fueling is completed
        if not pos.wait_for_disp_status("IDLE",timeout=60):
            return False

        if not pos.verify_idle(timeout=60):
            tc_fail("Transaction Failed pos was not idle")

        return True

    @test
    def postpay_wex_2(self):         
        """
        Zephyr Id: (tc13)This will Verify that postpay transaction completed successfully when
                    wex card of bin range 707138 with technology indicator not equals to 2 is swiped
        Args: None
        Returns: None
        """
        
        # Add fuel in preset mode
        pos.add_fuel(self.fuel_amount, mode="preset", grade=self.fuel_grade)
        
        # Check if fueling is completed
        if not pos.wait_for_disp_status("IDLE",timeout=90):
            return False

        # Take fuel inside POS
        pos.click_suspended_transaction()

        # add item with plu 1
        pos.add_item("1", method="PLU")

        # paying using WEX Card
        if not pos.click_function_key('Pay', timeout=3):
            return False
        if not pos.click_tender_key("Card"):
            return False

        # pay using wex msd card of bin range 707138
        try:            
            pinpad.use_card(brand=system.get_brand(), card_name="WEX2_MSD")
            time.sleep(10)
        except Exception as e:
            self.log.warning(f"Swipe Card in pinpad failed. Exception: {e}")
            pos.click_keypad("CANCEL")
            return False

        if not pos.verify_idle(timeout=60):
            tc_fail("Transaction Failed pos was not idle")

        fuel_amount = self.fuel_amount.replace("$","")

        item_amount = self.item_amount.replace("$","")

        # calculating total amount of sale
        sale_amount = float(fuel_amount) + float(item_amount)
        sale_amount = "Total=$" + str(sale_amount) 
        
        # verifying Receipt
        if not pos.check_receipt_for(sale_amount):
           tc_fail("Sale amount not matched with receipt")

        return True

    @test
    def prepay_MC(self):    
        """
        Zephyr Id: [TC21]To verify when MSD Mastercard is swiped on pinpad then POS uses the magstripe reader to process the card
                    when performed prepay & dry stock transactions
        Args: None
        Returns: None
        """
        # Add Fuel in prepay mode
        pos.add_fuel(self.fuel_amount,grade=self.fuel_grade)

        # add item with plu 1
        pos.add_item("1", method="PLU")
        
        # paying using mastercard MSD card
        if not pos.click_function_key('Pay', timeout=3):
            return False
        if not pos.click_tender_key("Card"):
            return False
        
        # swipe mastercard emv card 
        try:
            pinpad.swipe_card(card_name="MasterCard")
            time.sleep(10)
        except Exception as e:
            self.log.warning(f"Swipe Card in pinpad failed. Exception: {e}")
            pos.click_keypad("CANCEL")
            return False

        # Check if fueling is completed
        if not pos.wait_for_disp_status("IDLE",timeout=60):
            return False

        if not pos.verify_idle(timeout=60):
            tc_fail("Transaction Failed pos was not idle")

        fuel_amount = self.fuel_amount.replace("$","")

        item_amount = self.item_amount.replace("$","")

        # calculating total amount of sale
        sale_amount = float(fuel_amount) + float(item_amount)
        sale_amount = "Total=$" + str(sale_amount) 
        
        # Verifying receipt for sale amount
        if not pos.check_receipt_for([sale_amount]):
           tc_fail("Sale amount not matched with receipt")

        return True

    @test
    def preset_MC(self):     
        """
        Zephyr Id: (tc22)To verify when EMV Mastercard is swiped on pinpad then 
        POS uses the chip card reader to process the card when performed postpay & dry stock transactions
        Args: None
        Returns: None
        """
        # Add fuel in preset mode
        pos.add_fuel(self.fuel_amount, mode="preset", grade=self.fuel_grade)
        
        # Check if fueling is completed
        if not pos.wait_for_disp_status("IDLE",timeout=90):
            return False

        # Take fuel inside POS
        pos.click_suspended_transaction()

        # add item with plu 1
        pos.add_item("1", method="PLU")

        # paying using mastercard EMV Card
        if not pos.click_function_key('Pay', timeout=3):
            return False
        if not pos.click_tender_key("Card"):
            return False
        
        # swipe mastercard emv card 
        try:
            pinpad.swipe_card(card_name="EMVMCCredit")
            time.sleep(10)
        except Exception as e:
            self.log.warning(f"Swipe Card in pinpad failed. Exception: {e}")
            pos.click_keypad("CANCEL")
            return False

        # verify pos message
        if not pos.read_status_line()=='Chip card, Please Insert':     
            tc_fail("emv chip not detected")

        # insert mastercard emv card 
        try:
            pinpad.insert_card(card_name="EMVMCCredit")
        except Exception as e:
            self.log.warning(f"Insert Card in pinpad failed. Exception: {e}")
            pos.click_keypad("CANCEL")
            return False

        if not pos.verify_idle(timeout=60):
            tc_fail("Transaction Failed pos was not idle")

        fuel_amount = self.fuel_amount.replace("$","")

        item_amount = self.item_amount.replace("$","")

        # calculating total amount of sale
        sale_amount = float(fuel_amount) + float(item_amount)
        sale_amount = "Total=$" + str(sale_amount) 
        
        # Verifying Receipt
        if not pos.check_receipt_for([sale_amount]):
           tc_fail("Sale amount not matched with receipt")

        return True

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        pass