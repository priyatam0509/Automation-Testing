"""
    File name: Identify_Voyager.py
    Brand: Chevron
    Story ID : PEACOCK-3939
    Description: Identify Voyager EMV Cards by POS
    Author: Asha
    Date created: 2020-05-11 13:00
    Python Version: 3.7
"""

import logging, time
from app import Navi, pos, system, crindsim, pinpad
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class Identify_Voyager():
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
        if not system.restore_snapshot():
            self.log.debug("No snapshot to restore, if this is not expected please contact automation team")
        
        # sign-on to POS
        Navi.navigate_to("POS")
        pos.sign_on()
                
    @test
    def TC01(self):     
        """
        Zephyr Id: This will verify if EMV Voyager card is swiped on pin pad magstripe reader with Bin Range "708885-708889" then 
                POS used the chip card reader to process the card when performed prepay & dry stock transactions 
        Args: None
        Returns: None
        """           
        #Add Fuel in prepay mode
        pos.add_fuel(self.fuel_amount, grade=self.fuel_grade)

        #add item with plu 1
        pos.add_item("1", method="PLU")
        
        # paying using Voyager Card
        if not pos.click_function_key('Pay', timeout=3):
            return False
        if not pos.click_tender_key("Card"):
            return False
        
        # swipe Voyager emv card of bin range 690046 - TC1
        try:            
            pinpad.swipe_card(brand=system.get_brand(), card_name="Voyager1_EMV")
            time.sleep(5)
        except Exception as e:
            self.log.warning(f"Swipe Card in pinpad failed. Exception: {e}")
            pos.click_keypad("CANCEL")
            return False

        # verify pos message
        if not pos.read_status_line() == 'Chip card, Please Insert':
            tc_fail("Required chip card error not came")

        # Insert Voyager emv card of bin range 707138 - TC11
        try:            
            pinpad.use_card(brand=system.get_brand(), card_name="Voyager1_EMV")
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
    def TC5(self):         
        """
        Zephyr Id: This will verify if MSD Voyager card is swiped on pin pad magstripe reader with Bin Range "708885-708889" 
                then POS is used the magstripe reader to process the card when performed Manual Fuel sale & dry stock transactions 
        Args: None
        Returns: None
        """
        # Add fuel in manual mode
        pos.add_fuel(self.fuel_amount, mode="manual", grade=self.fuel_grade)

        # add item with plu 1
        pos.add_item("1", method="PLU")

        # paying using Voyager MSD Card
        if not pos.click_function_key('Pay', timeout=3):
            return False
        if not pos.click_tender_key("Card"):
            return False
        
        # swipe Voyager MSD card 
        try:            
            pinpad.swipe_card(brand=system.get_brand(), card_name="Voyager1_MSD")
        except Exception as e:
            self.log.warning(f"Swipe Card in pinpad failed. Exception: {e}")
            pos.click_keypad("CANCEL")
            return False

        if not pos.verify_idle(timeout=60):
            tc_fail("POS not idle after card transaction")

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
    def TC7(self):    
        """
        Zephyr Id: This will verify when MSD Mastercard is swiped on pin pad magstripe reader then 
                POS used the magstripe reader to process the card when performed prepay & dry stock transactions
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
        
        # swipe Voyager MSD card 
        try:            
            pinpad.swipe_card(card_name="MasterCard")
        except Exception as e:
            self.log.warning(f"Swipe Card in pinpad failed. Exception: {e}")
            pos.click_keypad("CANCEL")
            return False

        # Check if fueling is completed
        if not pos.wait_for_disp_status("IDLE",timeout=60):
            return False

        if not pos.verify_idle(timeout=60):
            tc_fail("POS not idle after card transaction")
        
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
    def TC8(self):     
        """
        Zephyr Id: This will verify when EMV Mastercard is swiped on pin pad magstripe reader then 
                POS is used the chip card reader to process the card when performed postpay & dry stock transactions
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
        if not pos.check_receipt_for(sale_amount):
           tc_fail("Sale amount not matched with receipt")

        return True

    @test
    def TC10(self):       
        """
        Zephyr Id: This will verify when MSD Visa card is swiped on crind magstripe reader then 
                crind is used the magstripe reader to process the card when performed outside crind sale & crind merchandising item transactions 
        Args: None
        Returns: None
        """
        
        # pay using Visa msd card 
        if not crindsim.crind_sale():
            tc_fail("Outside crind sale failed")

        return True

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        pass