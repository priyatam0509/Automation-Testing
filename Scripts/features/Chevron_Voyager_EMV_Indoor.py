"""
    File name: Chevron_Voyager_EMV_Indoor.py
    Brand: Chevron
    Description: [PEACOCK-3899] Indoor Transaction with Voyager EMV cards on Chevron sites
    Pre-requisite: Fuel price must be $1.00
                   Fuel(20 cents), non-fuel(30 cents) rewards must 
                   be configured for Loyalty_Test(card mask - 6008) in loyalty simulator. 
                   Apply non-fuel reward on Item2(Price:$5.00)
    Author: Asha
    Date created: 2020-05-11 14:53:24
    Date last modified: 
    Python Version: 3.7
"""

import logging,time
from app import Navi, pos, mws, system, pinpad, item
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app.simulators import loyaltysim

log = logging.getLogger()

class Chevron_Voyager_EMV_Indoor():
    """
    Description: Test class that provides an interface for testing.
    """
    def __init__(self):
        """Initializes the Template class.
        Args: None
        Returns: None
        """
        # Parameters to be used in sale
        self.fuel_amount = "$1.00"
        self.fuel_grade = "REG DSL #2"
        self.item_PLU = "002"
        self.loyalty_name = "LOYALTY_TEST"
        self.fuel_price = 1.00
        self.fuel_loyalty = 0.20
        self.nonfuel_loyalty = 0.30

    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        # Sign on to POS screen if not already sign-on
        Navi.navigate_to("POS")
        
        pos.sign_on()

    @test
    def TC01(self):
        """
        Zephyr Id : This will verify prepay & dry stock item transactions is completed successfully 
                    for EMV VOYAGER card with bin range "708885-708889"
        Args: None
        Returns: None
        """
        # Adding fuel 
        pos.add_fuel(self.fuel_amount, grade=self.fuel_grade)

        # Add Dry Stock Item
        pos.add_item(self.item_PLU, method="PLU")

        # Perform card Payment with Voyager EMV card
        pos.click_function_key("pay", verify=False)
        pos.click_tender_key('CARD', verify=False)

        # Insert Voyager EMV card of range 70888
        try: 
            pinpad.use_card(brand=system.get_brand(), card_name='Voyager1_EMV')
            time.sleep(5)
        except Exception as e:
            log.warning(f"Card swipe in pinpad failed. Exception: {e}")
            pos.click_keypad("CANCEL")
            return False

        if not  pos.verify_idle(timeout=30):
            tc_fail("POS not IDLE after card swipe")

        # Wait until dispenser 1 is idle
        if not pos.wait_for_disp_status('IDLE', timeout=90):
            return False

        # Calculate sale amount. Fuel amount(1.00) + item 2 amount(5.00)
        fuel_amount = self.fuel_amount.split('$')
        total = float(fuel_amount[1]) + 5.00
        
        strTotal = "Total=$" + str(total)

        # Check Receipt for AID
        if not pos.check_receipt_for([strTotal, "VOYAGER", "AID: A0000000041010"]):
           tc_fail("Voyager EMV cards data not displayed in receipt")
        
        return True

    @test
    def TC05(self):
        """
        Zephyr Id : This will verify postpay & dry stock item transactions is completed successfully 
                    for  Voyager MSD card
        Args: None
        Returns: None
        """
        # Adding fuel 
        pos.add_fuel(self.fuel_amount, mode="preset", grade=self.fuel_grade)
         
        # Wait until dispenser 1 is idle
        if not pos.wait_for_disp_status('IDLE', timeout=90):
            return False
      
        # Take fuel inside POS
        pos.click_suspended_transaction()

        # Add Dry Stock Item
        pos.add_item("002", method="PLU")

        # Perform card Payment with EMV Credit Card
        pos.click_function_key("pay", verify=False)
        pos.click_tender_key('CARD', verify=False)

        # Insert Voyager MSD card
        try: 
            pinpad.use_card(brand=system.get_brand(), card_name='Voyager1_MSD')
            time.sleep(5)
        except Exception as e:
            log.warning(f"Card swipe in pinpad failed. Exception: {e}")
            pos.click_keypad("CANCEL")
            return False

        if not pos.verify_idle(timeout=30):
            tc_fail("POS not IDLE after card swipe")

        # Calculate sale amount. Fuel amount(1.00) + item 2 amount(5.00)
        fuel_amount = self.fuel_amount.split('$')
        total = float(fuel_amount[1]) + 5.00
        
        strTotal = "Total=$" + str(total)

        # Check Receipt
        if not pos.check_receipt_for([strTotal, "VOYAGER"]):
           tc_fail("EMV Credit cards data not displayed in receipt")
        
        return True

    @test
    def TC06(self):
        """
        Zephyr Id : This will verify manual fuel sale & dry stock item transactions is completed successfully 
                    for EMV Debit card
        Args: None
        Returns: None
        """
        # Adding fuel 
        pos.add_fuel(self.fuel_amount, mode="manual", grade=self.fuel_grade)

        # Add Dry Stock Item
        pos.add_item("002", method="PLU")

        # Perform card Payment with EMV card
        pos.click_function_key("pay", verify=False)
        pos.click_tender_key('CARD', verify=False)

        # Insert EMV Debit card
        try: 
            pinpad.use_card(card_name='EMVVisaUSDebit')
            time.sleep(5)
        except Exception as e:
            log.warning(f"Card swipe in pinpad failed. Exception: {e}")
            pos.click_keypad("CANCEL")
            return False

        if not pos.verify_idle(timeout=30):
            tc_fail("POS was not IDLE after card swipe")
            
        # Calculate sale amount. Fuel amount(1.00) + item 2 amount(5.00)
        fuel_amount = self.fuel_amount.split('$')
        total = float(fuel_amount[1]) + 5.00
        
        strTotal = "Total=$" + str(total)

        # Check Receipt for AID
        if not pos.check_receipt_for([strTotal, "DEBIT EMV", "AID: A0000000980840"]):
           tc_fail("EMV debit card data not displayed in receipt")
        
        return True

    @test
    def TC02(self):
        """
        Testlink Id : This will postpay & dry stock item transactions is completed successfully 
                      with loyalty & carwash for EMV VOYAGER card with bin range "708885-708889"
        Args: None
        Returns: None
        """
        # Configure Loyalty in MWS and rewards in loyalty simulator
        loyaltysim.StartLoyaltySim()
        
        # Adding fuel
        pos.add_fuel(self.fuel_amount, mode="preset", grade=self.fuel_grade)
         
        # Wait until dispenser 1 is idle
        if not pos.wait_for_disp_status('IDLE', timeout=90):
            return False
      
        # Take fuel inside POS
        pos.click_suspended_transaction()

        # Add Dry Stock Item
        pos.add_item("002", method="PLU")

        # Add carwash item 
        pos.add_item("1234", method="plu", qualifier="CARWASH 1")

        if not pos.click_function_key("pay", verify=False):
            return False

        # Select Loyalty
        if "Enter LOYALTY_TEST ID" in pos.read_message_box():
            pos.click_message_box_key("YES", verify=False)
        elif "Select Loyalty Program" in pos.read_status_line():
            pos.select_list_item(self.loyalty_name, verify=False)
            pos.click_keypad("ENTER", verify=False)
            log.info("LOYALTY_Test selected")
        else:
            tc_fail("Loyalty selection not available")
            
        # Swipe loyalty card
        try:
            if "Enter LOYALTY_TEST ID" in pos.read_status_line():
                pinpad.swipe_card(card_name="Loyalty")
                time.sleep(5)
            else:
                tc_fail("Loyalty not selected")
        except Exception as e:
            log.warning(f"Card swipe in pinpad failed. Exception: {e}")
            pos.click_keypad("CANCEL")
            return False
        
        # Perform card Payment with Voyager EMV card
        pos.click_tender_key('CARD', verify=False)

        # Insert Voyager EMV card
        try: 
            pinpad.use_card(brand=system.get_brand(), card_name='Voyager1_EMV')
            time.sleep(5)
        except Exception as e:
            log.warning(f"Card swipe in pinpad failed. Exception: {e}")
            pos.click_keypad("CANCEL")
            return False

        if not pos.verify_idle(timeout=30):
            tc_fail("Pos was not idle")
        
        # Calculate sale amount after loyalty rewards
        fuel_price = self.fuel_amount.replace('$','')
        fuel_discount = float(fuel_price) * self.fuel_loyalty
        fuel_amount = float(fuel_price) - fuel_discount
        fuel_discount_text = "$-"+ format(self.fuel_loyalty,'0.3f') + "/GAL $-" + str(fuel_discount)
        nonfuel_loyalty_text = "$-" + str(self.nonfuel_loyalty)
        
        # Total amount is calculated as fuel sale amount + carwash1 amount + ( item2 amount - non-fuel reward)
        total_amount = fuel_amount + 2.50 + (5.00 - self.nonfuel_loyalty)

        # Check receipt for loyalty rewards
        if not pos.check_receipt_for([nonfuel_loyalty_text, fuel_discount_text, "$"+str(total_amount)]):
           tc_fail("Loyalty rewards not displayed in receipt")
           
        if not pos.check_receipt_for(["VOYAGER", "AID: A0000000041010"]):
           tc_fail("Voyager EMV cards data not displayed in receipt")
        
        return True

    @test
    def TC07(self):
        """
        Testlink Id : This will verify postpay & dry stock item transactions is completed successfully 
                      with loyalty & carwash for MSD VOYAGER card with bin range "708885-708889"
        Args: None
        Returns: None
        """
        # Adding fuel
        pos.add_fuel(self.fuel_amount, mode="preset", grade=self.fuel_grade)
         
        # Wait until dispenser 1 is idle
        if not pos.wait_for_disp_status('IDLE', timeout=90):
            return False
      
        # Take fuel inside POS
        pos.click_suspended_transaction()

        # Add Dry Stock Item
        pos.add_item("002", method="PLU")

        # Add carwash item 
        pos.add_item("1234", method="plu", qualifier="CARWASH 1")

        if not pos.click_function_key("pay", verify=False):
            return False

        # Select Loyalty
        if "Enter LOYALTY_TEST ID" in pos.read_message_box():
            pos.click_message_box_key("YES", verify=False)
        elif "Select Loyalty Program" in pos.read_status_line():
            pos.select_list_item(self.loyalty_name, verify=False)
            pos.click_keypad("ENTER", verify=False)
            log.info("LOYALTY_Test selected")
        else:
            tc_fail("Loyalty selection not available")
            
        # Swipe loyalty card
        try:
            if "Enter LOYALTY_TEST ID" in pos.read_status_line():
                pinpad.swipe_card(card_name="Loyalty")
                time.sleep(5)
            else:
                tc_fail("Loyalty not selected")
        except Exception as e:
            log.warning(f"Card swipe in pinpad failed. Exception: {e}")
            pos.click_keypad("CANCEL")
            return False
        
        # Perform card Payment with Voyager MSD card
        pos.click_function_key("pay", verify=False)
        pos.click_tender_key('CARD', verify=False)

        # Insert Voyager MSD card
        try: 
            pinpad.use_card(brand=system.get_brand(), card_name='Voyager1_MSD')
            time.sleep(5)
        except Exception as e:
            log.warning(f"Card swipe in pinpad failed. Exception: {e}")
            pos.click_keypad("CANCEL")
            return False

        if not pos.verify_idle(timeout=30):
            tc_fail("POS was not idle after transaction")
        
        # Calculate sale amount after loyalty rewards
        fuel_price = self.fuel_amount.replace('$','')
        fuel_discount = float(fuel_price) * self.fuel_loyalty
        fuel_amount = float(fuel_price) - fuel_discount
        fuel_discount_text = "$-"+ format(self.fuel_loyalty,'0.3f') + "/GAL $-" + str(fuel_discount)
        nonfuel_loyalty_text = "$-" + str(self.nonfuel_loyalty)
        
        # Total amount is calculated as fuel sale amount + carwash1 amount + ( item2 amount - non-fuel reward)
        total_amount = fuel_amount + 2.50 + (5.00 - self.nonfuel_loyalty)

        # Check receipt for loyalty rewards
        if not pos.check_receipt_for([nonfuel_loyalty_text, fuel_discount_text, "$"+str(total_amount)]):
           tc_fail("Loyalty rewards not displayed in receipt")
           
        if not pos.check_receipt_for(["VOYAGER"]):
           tc_fail("Voyager MSD cards data not displayed in receipt")
        
        return True

    @test
    def TC04(self):
        """
        Testlink Id : This will verify prepay & dry stock item transactions is completed successfully 
                      with loyalty & carwash for EMV Mastercard
        Returns: None
        """
        # Add fuel for Prepay sale
        pos.add_fuel(self.fuel_amount, grade=self.fuel_grade)

        # Add Dry Stock Item
        pos.add_item("002", method="PLU")

        # Add carwash item 
        pos.add_item("1234", method="plu", qualifier="CARWASH 1")

        if not pos.click_function_key("pay", verify=False):
            return False

        # Select Loyalty
        if "Enter LOYALTY_TEST ID" in pos.read_message_box():
            pos.click_message_box_key("YES", verify=False)
        elif "Select Loyalty Program" in pos.read_status_line():
            pos.select_list_item(self.loyalty_name, verify=False)
            pos.click_keypad("ENTER", verify=False)
            log.info("LOYALTY_Test selected")
        else:
            tc_fail("Loyalty selection not available")
            
        # Swipe loyalty card
        try:
            if "Enter LOYALTY_TEST ID" in pos.read_status_line():
                pinpad.swipe_card(card_name="Loyalty")
                time.sleep(5)
            else:
                tc_fail("Loyalty not selected")
        except Exception as e:
            log.warning(f"Card swipe in pinpad failed. Exception: {e}")
            pos.click_keypad("CANCEL")
            return False
        
        # Perform card Payment with EMV card
        pos.click_tender_key('CARD', verify=False)

        # Insert EMV Master card
        try: 
            pinpad.use_card(card_name='EMVMCCredit')
            time.sleep(5)
        except Exception as e:
            log.warning(f"Card swipe in pinpad failed. Exception: {e}")
            pos.click_keypad("CANCEL")
            return False

        if not pos.verify_idle(timeout=30):
            tc_fail("POS was not idle after transaction")
        
        # Calculate sale amount after loyalty rewards
        fuel_amount = self.fuel_amount.replace('$','')
        fuel_amount = float(fuel_amount)
        fuel_rewards = self.fuel_price - self.fuel_loyalty
        discount = fuel_amount / fuel_rewards
        fuel_discount_text = format(discount, '0.3f') + "GAL @ $"+format(fuel_rewards,'0.3f')+"/GAL"
        nonfuel_loyalty_text = "$-" + str(self.nonfuel_loyalty)
        
        # Total amount is calculated as fuel sale amount + carwash1 amount + ( item2 amount - non-fuel reward)
        total_amount = fuel_amount + 2.50 + (5.00 - self.nonfuel_loyalty)

        # Check receipt for loyalty rewards
        if not pos.check_receipt_for([nonfuel_loyalty_text, fuel_discount_text, "$"+str(total_amount)]):
           tc_fail("Loyalty rewards not displayed in receipt")
           
        if not pos.check_receipt_for(["MASTER EM","AID: A0000000041010"]):
           tc_fail("EMV Mastercard data not displayed in receipt")
        
        return True
        
    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        loyaltysim.StopLoyaltySim()