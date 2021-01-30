"""
    File name: Loyalty_Configuration.py
    Tags:
    Description: [PEACOCK-3735] This will verify loyalty configuration on loyalty interface 
                 in MWS by adding 6 loyalty
    Author: Asha
    Date created: 2019-12-12 11:40:00
    Python Version: 3.7
"""

import logging
from app import Navi, mws
from app.features import loyalty
from app.simulators import loyaltysim
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class Loyalty_Configuration():
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

        self.loyalty_name = "Kickback"

        self.card_mask = ['6008']

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
        
        # Create object for loyalty
        self.objLoyalty = loyalty.LoyaltyInterface()
        
    @setup
    def setup(self):
        """
		Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        # Delete existing loyalty
        # Fetch existing addded loyalty provider
        # Let's first set up the sims the way we need them
        loyaltysim.StartLoyaltySim()

        # Create new reward
        loyaltysim.AddTransactionReward(RewardName="1 dollar trans rwd", TypeRewardDescription="$1 Off",
                                        Discount="1.00", ReceiptTextShort="1 Dollar transaction Reward",
                                        ReceiptTextLong="1 Dollar transaction reward receipt text")
        rewardId = loyaltysim.AddNonFuelReward(RewardName="InstDryStock", TypeReward="Optional",
                                    TypeRewardDescription="15 Cent Instant Discount", DiscountMethod="amountOff",
                                    Discount="0.15", ItemType="itemLine", CodeFormat="plu", CodeValue="002",
                                    RewardLimit="1", ReceiptText="Dry stock 15 cents amount off")

        # Create new Loyalty IDs if they don't exist
        loyaltysim.AddLoyaltyIDs("6008*", "6008*", "6008*", "6008*")
        loyaltysim.AddLoyaltyIDs("7079*", "7079*", "7079*", "7079*")


        ids =[loyaltysim.GetLoyaltyId("6008*"), loyaltysim.GetLoyaltyId("7079*")]

        for id in ids:
            # Remove all assigned rewards
            loyaltysim.UnAssignAllFuelRewardsByLoyalty(id)
            loyaltysim.UnAssignAllNonFuelRewardsByLoyalty(id)
            loyaltysim.UnAssignAllTransRewardsByLoyalty(id)

            # Assign rewards to ids
            loyaltysim.AssignFuelReward(id, "1", "FuelReward1")
            loyaltysim.AssignNonFuelReward(id, rewardId, "DryStockDiscount")
            loyaltysim.AssignTransactionReward(id, "1", "20 cents trans.")

        loyalty_list = mws.get_value("Loyalty Providers")

        if len(loyalty_list) != 0:
            for loyalty in loyalty_list:
                if not self.objLoyalty.delete_provider(loyalty[0]):
                    self.log.error("Failled to delete existing loyalty")
                    return False

    @test
    def add_loyalty_provider(self):
        """
        Zephyr Id: This will configure loyalty1 with Generic loyalty provider on loyalty interface. 
        Args: None
        Returns: None
        """
        if not self.objLoyalty.add_provider(self.loyalty_cfg, self.loyalty_name, cards=self.card_mask):
            tc_fail("Failled to add loyalty provider")
        return True

    @test
    def multilple_loyalty_provider(self):
        """
        Zephyr Id: This will configure 6 loyalty providr in MWS. 
        Args: None
        Returns: None
        """
        loyalty_list = ['Loyalty2', 'Loyalty3', 'Loyalty4', 'Loyalty5', 'Loyalty6']
        for loyalty_name in loyalty_list:
            if not self.objLoyalty.add_provider(self.loyalty_cfg, loyalty_name, cards=['7079']):
                tc_fail("Failled to add 6 loyalty provider")
        
        mws.click_toolbar("Exit")
        return True

    @test
    def restrict_loyalty(self):
        """
        Zephyr Id: This will verify that restriction should be displayed
                   if we try to add more than 6 loyalty of provider type Generic  
        Args: None
        Returns: None
        """
        Navi.navigate_to("Loyalty Interface")

        # Fetch existing addded loyalty provider
        loyalty_list = mws.get_value("Loyalty Providers")
        
        # Try to add one more loyalty if already 6 loyalty configured
        if len(loyalty_list) == 6:
            mws.click_toolbar("Add")
        else:
            tc_fail("Less than 6 loyalty present")

        error_msg = mws.get_top_bar_text()

        if "cannot add any more loyalty providers" not in error_msg.lower():
            tc_fail("Allowing to add more than 6 loyalty")
            return False

        mws.click_toolbar("OK")
        return True

    @test
    def enabled_loyalty_deletion(self):
        """
        Zephyr Id: This will verify that error will be shown when you delete loyalty which is enabled
        Args: None
        Returns: None
        """
        if not mws.set_value("Loyalty Providers", self.loyalty_name):
            self.log.error(f"Couldn't select provider {self.loyalty_name}.")
            return False
        
        if not mws.click_toolbar("Delete"):
            return False
        
        if not mws.verify_top_bar_text(f"WARNING! Deleting {self.loyalty_name} will cause you to lose all configuration, transaction data,"\
            f" and reports for this loyalty provider. Are you sure you want to delete {self.loyalty_name}?"):
            tc_fail(f"Didn't get delete confirmation for provider {self.loyalty_name}.")
            return False
        
        mws.click_toolbar("Yes")

        if not mws.verify_top_bar_text(f"{self.loyalty_name} Enabled field is set to Yes in Configuration"):
            tc_fail("Enabled field error during deletion message not came")
            return False

        mws.click_toolbar("OK")
        return True

    @test
    def disabled_loyalty_deletion(self):
        """
        Zephyr Id: This will verify that deletion is successful if loyalty is disabled
        Args: None
        Returns: None
        """
        # Disable loyalty
        enable_cfg = {'Enabled': 'No'}
        loyalty_list = {'Loyalty5', 'Loyalty6'}

        for loyalty in loyalty_list:
            if not self.objLoyalty.change_provider(enable_cfg, loyalty):
                tc_fail("Failled to disable loyalty")
            
            self.log.info(f" {loyalty} is disabled")
            
            mws.click_toolbar("Exit")
            Navi.navigate_to("Loyalty Interface")
            
            if not self.objLoyalty.delete_provider(loyalty):
                tc_fail("Failled to delete loyalty")

    @test
    def add_EXXON_loyalty_provider(self):
        """
        Zephyr Id: This will configure EXXON loyalty providr in loyalty interface. 
        Args: None
        Returns: None
        """
        if not self.objLoyalty.add_provider(self.loyalty_cfg, "Loyalty5", provider_type="ExxonMobil"):
            tc_fail("Failled to add loyalty provider")
        
        mws.click_toolbar("Exit")
        return True

    @test
    def multiple_EXXON_loyalty_provider(self):
        """
        Zephyr Id: This will verify that we can't configure more than 1 EXXON 
                   loyalty providr in MWS.
        Args: None
        Returns: None
        """
        Navi.navigate_to("Loyalty Interface")

        mws.click_toolbar("Add")

        value = mws.get_value("Loyalty Provider Type")

        if "ExxonMobile" in value:
            tc_fail("Able to add another Exxonmobile provider type")

        mws.click_toolbar("Cancel")
        mws.click_toolbar("No")
        mws.click_toolbar("Exit")
        return True

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        pass