"""
    File name: Chevron_WEX_EMV_Indoor.py
    Brand: Chevron
    Description: [PEACOCK-3895] Indoor Transaction with WEX EMV cards
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
from app import Navi, pos, mws, system, pinpad, item, runas
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app.simulators import loyaltysim
from app.features import loyalty

log = logging.getLogger()

def update_loyalty_rewards():
    """
    This is helper method to start loyalty sim and update loyalty fuel and non-fuel rewards
    """
    loyaltysim.StartLoyaltySim()

    loyalty_ID = loyaltysim.AddLoyaltyIDs("6008*", "6008*", "6008*", "6008*", "6008*")

    if loyalty_ID == "":
        log.error("Not able to add Loyalty ID")
        return False
    else:
        log.info(f"Loyalty {loyalty_ID} is added")

    fuel_ID = loyaltysim.AddFuelRewards(RewardName="FuelReward1", TypeReward="Instant", TypeRewardDescription="", DiscountMethod="amountOffPPU", RewardLimit="300", ReceiptText="20 cents Discount", FuelGrades="004:0.20, 019:0.20, 020:0.20")
    if fuel_ID == "":
        log.error("Not able to add Fuel Reward")
        return False

    non_fuel_ID = loyaltysim.AddNonFuelReward(RewardName="30 cents DryStock", TypeReward="Instant", TypeRewardDescription="R u Sure?", DiscountMethod="amountOff", Discount="0.30", ItemType="itemLine", CodeFormat="plu", CodeValue="002", RewardLimit="10000", ReceiptText="Dry stock 30 cents amount off")
    if non_fuel_ID == "":
        log.error("Not able to add non Fuel Reward")
        return False

    if not loyaltysim.AssignFuelReward(LoyatyID=loyalty_ID, FuelID=fuel_ID, RewardName="FuelReward1"):
        log.error("Not able to assign Fuel Reward")
        return False

    if not loyaltysim.AssignNonFuelReward(LoyatyID=loyalty_ID, NonFuelID=non_fuel_ID, RewardName="30 cents DryStock"):
        log.error("Not able to assign non Fuel Reward")
        return False

    return True
    
def configure_loyalty(item_data,loyalty_cfg,loyalty_name):
    """
    This is helper method to configure loyalty in MWS
    """
    # Navigate to POS
    Navi.navigate_to("MWS")

    # Create object for Item
    obj = item.Item()

    # Make item discountable
    if not obj.change("002", item_data):
        log.error("Not able to make item discoutable")
        return False

    mws.click_toolbar("Exit")

    # Create object for loyalty
    objLoyalty = loyalty.LoyaltyInterface()

    if not objLoyalty.add_provider(loyalty_cfg, loyalty_name, cards=['6008']):
        log.error("Failled to add loyalty provider")
        return False
    
    mws.click_toolbar("Exit")

    return True

class Chevron_WEX_EMV_Indoor():
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

        self.loyalty_cfg = {
            "General": {
                    "Enabled": "Yes",
                    "Site Identifier": '1',
                    "Host IP Address": '10.5.48.2',
                    "Port Number": '7900',
                "Page 2": {
                    "Loyalty Interface Version": "Gilbarco v1.0",
                    "Loyalty Vendor": 'Kickback Points'
                }
            },
	    	"Receipts": {
                "Outside offline receipt line 1": 'a receipt line'
            }
        }

        #Make item discoutable
        self.item_data = {
            "General": {
                "This item sells for": True,
                "per unit": "5.00"
            },
            "Options": {
                "Discountable": True
            }
        }

    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        if not system.restore_snapshot():
            log.debug("No snapshot to restore, if this is not expected please contact automation team")

        # Sign on to POS screen if not already sign-on
        Navi.navigate_to("POS")
        
        pos.sign_on()

    @test
    def TC02(self):
        """
        Zephyr Id : This will verify postpay & dry stock item transactions is completed successfully 
                    for EMV WEX card with bin range "690046"
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
        pos.add_item(self.item_PLU, method="PLU")

        # Perform card Payment with WEX EMV card
        pos.click_function_key("pay", verify=False)
        pos.click_tender_key('CARD', verify=False)

        # Insert WEX EMV card of range 690064 on PINPad
        try: 
            pinpad.use_card(brand=system.get_brand(), card_name='WEX1_EMV')
            time.sleep(5)
        except Exception as e:
            log.warning(f"Card swipe in pinpad failed. Exception: {e}")
            pos.click_keypad("CANCEL")
            return False

        if not pos.verify_idle(timeout=30):
            tc_fail("POS was not idle after card transaction")

        # Calculate sale amount. Fuel amount(1.00) + item 2 amount(5.00)
        fuel_amount = self.fuel_amount.split('$')
        total = float(fuel_amount[1]) + 5.00
        
        strTotal = "Total=$" + str(total)

        # Check Receipt for AID
        if not pos.check_receipt_for([strTotal, "WEX FLEET", "AID: A0000007681010"]):
           tc_fail("WEX EMV cards data not displayed in receipt")

        return True

    @test
    def TC09(self):
        """
        Zephyr Id : This will verify manual fuel sale & dry stock item transactions is completed successfully 
                    for MSD WEX card with bin range "690046"
        Args: None
        Returns: None
        """
        # Adding fuel
        pos.add_fuel(self.fuel_amount, mode="manual", grade=self.fuel_grade)

        # Add Dry Stock Item
        pos.add_item("002", method="PLU")

        # Perform card Payment with WEX EMV card
        pos.click_function_key("pay", verify=False)
        pos.click_tender_key('CARD', verify=False)

        # Insert WEX EMV card of range 690064 on PINPad
        try: 
            pinpad.use_card(brand=system.get_brand(), card_name='WEX1_MSD')
            time.sleep(5)
        except Exception as e:
            log.warning(f"Card swipe in pinpad failed. Exception: {e}")
            pos.click_keypad("CANCEL")
            return False

        if not pos.verify_idle(timeout=30):
            tc_fail("POS was not idle after card transaction")

        # Calculate sale amount. Fuel amount(1.00) + item 2 amount(5.00)
        fuel_amount = self.fuel_amount.split('$')
        total = float(fuel_amount[1]) + 5.00
        
        strTotal = "Total=$" + str(total)

        # Check Receipt
        if not pos.check_receipt_for([strTotal,'WEX FLEET']):
           tc_fail("WEX EMV cards data not displayed in receipt")
        
        return True

    @test
    def TC04(self):
        """
        Zephyr Id : This will verify prepay & dry stock item transactions is completed successfully 
                    for EMV WEX card with bin range "707138"
        Args: None
        Returns: None
        """
        # Add fuel 
        pos.add_fuel(self.fuel_amount, grade=self.fuel_grade)

        # Add Dry Stock Item
        pos.add_item(self.item_PLU, method="PLU")

        # Perform card Payment with WEX EMV
        pos.click_function_key("pay", verify=False)
        pos.click_tender_key('CARD', verify=False)

        # Insert WEX EMV card of range 707138 on PINPad
        try: 
            pinpad.use_card(brand=system.get_brand(), card_name='WEX2_EMV')
            time.sleep(5)
        except Exception as e:
            log.warning(f"Card swipe in pinpad failed. Exception: {e}")
            pos.click_keypad("CANCEL")
            return False

        if not pos.verify_idle(timeout=30):
            tc_fail("POS was not idle after card transaction")

        # Wait until dispenser 1 is idle
        if not pos.wait_for_disp_status('IDLE', timeout=90):
            return False

        # Calculate sale amount. Fuel amount(1.00) + item2 amount(5.00)
        fuel_amount = self.fuel_amount.split('$')
        total = float(fuel_amount[1]) + 5.00 
        
        strTotal = "Total=$" + str(total)

        # Check receipt for sale amount
        if not pos.check_receipt_for([strTotal, "WEX FLEET", "AID: A0000007681010"]):
           tc_fail("WEX EMV cards data not displayed in receipt")
        
        return True

    @test
    def TC05(self):
        """
        Zephyr Id : This will verify manual fuel sale & dry stock item transactions is completed successfully 
                    for MSD WEX card with bin range "707138"
        Args: None
        Returns: None
        """
        # Adding fuel
        pos.add_fuel(self.fuel_amount, mode="manual", grade=self.fuel_grade)

        # Add Dry Stock Item
        pos.add_item("002", method="PLU")

        # Perform card Payment with WEX EMV card
        pos.click_function_key("pay", verify=False)
        pos.click_tender_key('CARD', verify=False)

        # Insert WEX MSD card of range 707138 on PINPad
        try: 
            pinpad.use_card(brand=system.get_brand(), card_name='WEX1_MSD')
            time.sleep(5)
        except Exception as e:
            log.warning(f"Card swipe in pinpad failed. Exception: {e}")
            pos.click_keypad("CANCEL")
            return False

        if not pos.verify_idle(timeout=30):
            tc_fail("POS was not idle after card transaction")

        # Calculate sale amount. Fuel amount(1.00) + item 2 amount(5.00)
        fuel_amount = self.fuel_amount.split('$')
        total = float(fuel_amount[1]) + 5.00
        
        strTotal = "Total=$" + str(total)

        # Check Receipt for AID
        if not pos.check_receipt_for([strTotal, "WEX FLEET"]):
           tc_fail("WEX EMV cards data not displayed in receipt")
  
        return True

    @test
    def TC08(self):
        """
        Zephyr Id : This will verify postpay & dry stock item transactions is completed successfully 
                    for EMV Debit card
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

        # Perform card Payment with WEX EMV
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
            tc_fail("POS was not idle after card transaction")

        # Calculate sale amount. Fuel amount(1.00) + item 2 amount(5.00)
        fuel_amount = self.fuel_amount.split('$')
        total = float(fuel_amount[1]) + 5.00
        
        strTotal = "Total=$" + str(total)

        if not pos.check_receipt_for([strTotal,"DEBIT EMV", "AID: A0000000980840"]):
           tc_fail("EMV cards data not displayed in receipt")
       
        return True
    
    @test
    def TC01(self):
        """
        Testlink Id : This will verify prepay & dry stock item transactions is completed successfully 
                      with loyalty & carwash for EMV WEX card with bin range "690046" 
        Args: None
        Returns: None
        """
        
        # Configure Loyalty in MWS and rewards in loyalty simulator
        if not update_loyalty_rewards():
            log.error("Not able to configure loyalty rewards in loyalty simulator")

        if not configure_loyalty(self.item_data, self.loyalty_cfg, self.loyalty_name):
            log.error("Not able to configure loyalty in MWS")
        
        # Sign on to POS screen if not already sign-on
        Navi.navigate_to("POS")
        
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
            log.info("LOYALTY_TEST selected")
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
        
        # Perform card Payment with WEX EMV card
        pos.click_tender_key('CARD', verify=False)

        # Insert WEX EMV card of range 690064 on PINPad
        try: 
            pinpad.use_card(brand=system.get_brand(), card_name='WEX1_EMV')
            time.sleep(5)
        except Exception as e:
            log.warning(f"Card swipe in pinpad failed. Exception: {e}")
            pos.click_keypad("CANCEL")
            return False

        # Wait until dispenser 1 is idle
        if not pos.verify_idle(timeout=30):
            return False
        
        # Wait until dispenser 1 is idle
        if not pos.wait_for_disp_status('IDLE', timeout=90):
            return False

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

        # Check Receipt for AID
        if not pos.check_receipt_for(["WEX FLEET", "AID: A0000007681010"]):
           tc_fail("WEX EMV cards data not displayed in receipt")

        return True

    @test
    def TC10(self):
        """
        Testlink Id : This will verify postpay & dry stock item transactions is completed successfully 
                      with loyalty & carwash for MSD WEX card with bin range "707138"
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
            log.info("LOYALTY_TEST selected")
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
        
        # Perform card Payment with WEX MSD
        pos.click_tender_key('CARD', verify=False)

        # Insert WEX MSD card
        try: 
            pinpad.use_card(brand=system.get_brand(), card_name='WEX1_MSD')
            time.sleep(5)
        except Exception as e:
            log.warning(f"Card swipe in pinpad failed. Exception: {e}")
            pos.click_keypad("CANCEL")
            return False

        # Wait until dispenser 1 is idle
        if not pos.verify_idle(timeout=30):
            return False
        
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
        
        # Check Receipt for AID
        if not pos.check_receipt_for(["WEX FLEET"]):
           tc_fail("WEX MSD card data not displayed in receipt")
        
        return True

    @test
    def TC07(self):
        """
        Testlink Id : This will verify prepay & dry stock item transactions is completed successfully 
                      with loyalty & carwash for EMV Credit card i.e. EMV Visa Credit card
        Args: None
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
            log.info("LOYALTY_TEST selected")
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
        
        # Perform card Payment with EMV Visa credit
        pos.click_tender_key('CARD', verify=False)

        # Insert EMV Visa credit card
        try: 
            pinpad.use_card(card_name='EMVVisaCredit')
            time.sleep(5)
        except Exception as e:
            log.warning(f"Card swipe in pinpad failed. Exception: {e}")
            pos.click_keypad("CANCEL")
            return False

        # Wait until dispenser 1 is idle
        if not pos.verify_idle(timeout=90):
            return False

        # Wait until dispenser 1 is idle
        if not pos.wait_for_disp_status('IDLE', timeout=90):
            return False
        
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
           
        if not pos.check_receipt_for(["VISA_EMV", "AID: A0000000031010"]):
           tc_fail("EMV credit card data not displayed in receipt")
        
        return True    
    
    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        loyaltysim.StopLoyaltySim()