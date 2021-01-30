"""
    File name: SL_1903_1.py
    Brand: Concord
    Description: Inside transaction with Voyager EMV cards
    Author: Paresh
    Date created: 2020-09-25 08:42:19
    Date last modified: 
    Python Version: 3.7
"""

import logging, time
from app import pos, mws, item, Navi, crindsim
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app.simulators import loyaltysim
from app.features import loyalty


#The logging object. 
log = logging.getLogger()

def fetch_invoice():
    """
    This is helper method to fetch the invoice number
    """

    pos.click_function_key("Receipt Search")

    pos.select_receipt(1)

    receipt = pos.read_receipt()

    inv_num = receipt.index("INVOICE:")+1
    inv_no = receipt[inv_num]
    pos.click("CANCEL")

    return inv_no

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
    
def configure_loyalty(item_data, loyalty_cfg, loyalty_name):
    """
    This is helper method to configure loyalty in MWS
    """
    #Navigate to POS
    Navi.navigate_to("MWS")

    #Create object for Item
    obj = item.Item()

    #Make item discountable
    if not obj.change("002", item_data):
        log.error("Not able to make item discoutable")
        return False

    mws.click_toolbar("Exit")

    #Create object for loyalty
    objLoyalty = loyalty.LoyaltyInterface()

    if not objLoyalty.add_provider(loyalty_cfg, loyalty_name, cards=['6008']):
        log.error("Failled to add loyalty provider")
        return False
    
    mws.click_toolbar("Exit")

    return True

class SL_1903_1():
    """
    Description: Test class that provides an interface for testing.
    """

    def __init__(self):
        """Initializes the Template class.
        Args: None
        Returns: None
        """
        #Parameter to be used for sale
        self.fuel_amount = "$1.00"
        self.fuel_grade = "Diesel 1"
        self.item_PLU = "002"
        self.loyalty_name = "LOYALTY_TEST"
        self.fuel_price = 1.00
        self.fuel_loyalty = 0.20
        self.nonfuel_loyalty = 0.30
        self.refund_fuel_amount = "$-1.00"

    @setup
    def setup(self):
        """Performs any initialization that is not default.
        Args: None
        Returns: None
        """

        if not pos.connect():
            log.error("Unable to connect with pos")
            return False
        
        if not pos.sign_on():
            log.error("failed to login in pos")
            return False

    @test
    def TC01(self):
        """ 
        Description : To verify prepay & dry stock item transactions is completed successfully for EMV VOYAGER card with bin range "708885-708889"
        Args: None
        Returns: None
        """

        #Add 1 dry stock item and fuel with prepay
        pos.add_item("002", method="PLU")

        #Add fuel in prepay mode
        pos.add_fuel(amount=self.fuel_amount, grade=self.fuel_grade)
        
        #Pay usign Voyager EMV card
        pos.pay_card(card_name="Voyager1_EMV")
        
        #Wait until dispenser 1 is idle
        pos.wait_for_disp_status('IDLE', timeout=90)

        #Calculate sale amount. Fuel amount(1.00) + item 2 amount(5.00)
        fuel_amount = self.fuel_amount.split('$')
        total = float(fuel_amount[1]) + 5.00
        
        strTotal = "Total=$" + str(total)

        #Verify card name and aid is printed on receipt
        if not pos.check_receipt_for([strTotal, "Voyager", "AID: A0000000041010"]):
            tc_fail("Card Name and AID is not present in receipt")
        
        return True
    
    @test
    def TC04(self):
        """ 
        Description : To verify postpay & dry stock item transactions is completed successfully for  EMV Credit card i.e. EMV Visa/Amex/Discover card
        Args: None
        Returns: None
        """
    
        #Add fuel with preset
        pos.add_fuel(amount=self.fuel_amount, mode="preset", grade=self.fuel_grade)
        
        #Check if fueling is completed
        pos.wait_for_disp_status("IDLE",timeout=90)

        #Take fuel inside POS
        pos.click_fuel_buffer("A")
        
        #Add item
        pos.add_item("002", method="PLU")
        
        #Pay with EMV Amex card
        pos.pay_card(card_name="EMVAmEx")

        #Calculate sale amount. Fuel amount(1.00) + item 2 amount(5.00)
        fuel_amount = self.fuel_amount.split('$')
        total = float(fuel_amount[1]) + 5.00
        
        strTotal = "Total=$" + str(total)

        #Verify card name and aid is present in receipt
        if not pos.check_receipt_for([strTotal, "American Express"]):
            tc_fail("Card Name and AID is not present in receipt")
        
        return True

    @test
    def TC05(self):
        """ 
        Description : To verify manual fuel sale & dry stock item transactions is completed successfully for EMV Debit card
        Args: None
        Returns: None
        """
        
        #Add fuel in manual mode
        pos.add_fuel(self.fuel_amount, mode="manual", grade=self.fuel_grade)
        
        #Add dry stock item
        pos.add_item("002", method="PLU")

        #Pay with EMV debit card
        pos.pay_card(card_name="EMVVisaUSDebit")

        #Calculate sale amount. Fuel amount(1.00) + item 2 amount(5.00)
        fuel_amount = self.fuel_amount.split('$')
        total = float(fuel_amount[1]) + 5.00
        
        strTotal = "Total=$" + str(total)

        #verify card name and aid is present in receipt
        if not pos.check_receipt_for([strTotal, "Debit"]):
            tc_fail("Card Name and AID is not present in receipt")
        
        
        return True
        
    @test
    def TC08(self):
        """ 
        Description : To verify refund/return is performed for manual fuel sale & dry stock item transactions for EMV VOYAGER card with bin range "708885-708889"
        Args: None
        Returns: None
        """

        #Set crindsim mode manual
        crindsim.set_mode("manual")

        #Add fuel in manual mode
        pos.add_fuel(self.fuel_amount, mode="manual", grade=self.fuel_grade)
        
        #Add dry stock item
        pos.add_item("002", method="PLU")

        #Pay usign Voyager EMV card
        pos.pay_card(card_name="Voyager1_EMV")

        #refund the amount of manual fuel sale
        invoice_num = fetch_invoice()

        pos.click("Refund")

        pos.add_fuel(self.fuel_amount, mode="manual", grade=self.fuel_grade)

        pos.pay_card(card_name="Voyager1_EMV", invoice_number=invoice_num)

        #Verify card name and aid is printed on receipt
        if not pos.check_receipt_for(["Refund Credit "+self.refund_fuel_amount, "Voyager"]):
            tc_fail("Card Name and AID is not present in receipt")

        return True
    
    @test
    def TC09(self):
        """ 
        Description : To verify refund/return is performed for manual fuel sale & dry stock item transactions for EMV Mastercard
        Args: None
        Returns: None
        """

        #Add fuel in manual mode
        pos.add_fuel(self.fuel_amount, mode="manual", grade=self.fuel_grade)
        
        #Add dry stock item
        pos.add_item("002", method="PLU")

        #Pay using EMV master card
        pos.pay_card(card_name="EMVMCFleet_NoRestrictions_1")

        #refund the amount of manual fuel sale
        invoice_num = fetch_invoice()

        pos.click("Refund")

        pos.add_fuel(self.fuel_amount, mode="manual", grade=self.fuel_grade)
    

        pos.pay_card(card_name="EMVMCFleet_NoRestrictions_1", invoice_number=invoice_num)

        #Verify card name and aid is printed on receipt
        if not pos.check_receipt_for(["Refund Credit "+self.refund_fuel_amount, "Mastercard Fleet"]):
            tc_fail("Card Name and AID is not present in receipt")

        return True
    
    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        Args: None
        Returns: None
        """

        #Set crindsim mode manual
        crindsim.set_mode("auto")
        
        #Close pos instance
        pos.close()
