"""
    File name: EBT_VerifyEBT_CashBack_Limit.py
    Tags:
    Description: SL-1575 - Enable the cashback limit and configuration in the network configuration
    Brand: Phillips 66
    Author: Paresh
    Date created: 2019-31-12 13:31:37
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import Navi, mws
from app import OCR
from app.features import feature_activation
from app.framework.tc_helpers import setup, test, teardown, tc_fail


class EBT_VerifyEBT_CashBack_Limit():
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
    
    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        FA = feature_activation.FeatureActivation()
        if not FA.activate(feature_activation.DEFAULT_PASSPORT):
            self.log.error("Not able to perform feature activation")
            return False
        
        # Set terminal id value to save Global info editor setup
        Navi.navigate_to("Global Info Editor")
        mws.select_tab("Dealer")
        mws.set_value("Terminal ID", "01")
        mws.click_toolbar("Save")

    @test
    def verify_maximum_EBT_cashbackAmountField_Visible(self):
        """
        Testlink Id: SL-1575 - Enable the cashback limit and configuration in the network configuration
        Description: Verify we are able to see Maximum EBT cashback limit field.
        Args: None
        Returns: None
        """
        
        Navi.navigate_to("Global Info Editor")
        mws.select_tab("Site Configuration")
        
        if not OCR.findText("Maximum EBT Cashback Amount"):
            tc_fail("Maximum EBT cashback amount field is not visible")
        
        return True

    @test
    def verify_EBT_cashBack_amount_validation(self):
        """
        Testlink Id: SL-1575 - Enable the cashback limit and configuration in the network configuration
        Description: Verify EBT cash back limit should be greater than or equal to Debit cash back maximum amount
        Args: None
        Returns: None
        """
		# Fetch maximum Debit cashback amount
        debit_cashback_amount = int(mws.get_value("Debit Cashback Maximum", tab="Site Configuration"))
        
        if not mws.set_value("Maximum EBT Cashback Amount", debit_cashback_amount-1, tab="Site Configuration"):
            tc_fail("Unable to set the value of EBT cashback amount")
        
        mws.click_toolbar("Save")

        if "Maximum cashback amount in an EBT Cash transaction" not in mws.get_top_bar_text():
            tc_fail("Error validation message is not displayed")
        
        mws.click_toolbar("Cancel")
        mws.click_toolbar("Yes")
        if "EBT Cash back amount must be equal to or greater than" not in mws.get_top_bar_text():
            tc_fail("Error validation message is not displayed")
        
        if not mws.click_toolbar("Cancel"):
            return False
        if not mws.click_toolbar("No"):
            return False  
        
        return True
    
    @test
    def verify_valueIsNotSet_afterClickOnCancel(self):
        """
        Testlink Id: SL-1575 - Enable the cashback limit and configuration in the network configuration
        Description: Verify EBT cash back limit should not changed if we are clicking on Cancel > No button
        Args: None
        Returns: None
        """
        Navi.navigate_to("Global Info Editor")
        mws.select_tab("Site Configuration")
        
        # Store the value of EBt cash back field before save
        get_EBT_cashBack_beforeSave = mws.get_value("Maximum EBT Cashback Amount", tab="Site Configuration")
        
        debit_cashback_amount = int(mws.get_value("Debit Cashback Maximum", tab="Site Configuration"))
        
        if not mws.set_value("Maximum EBT Cashback Amount", debit_cashback_amount+1, tab="Site Configuration"):
            tc_fail("Unable to set the value of EBT cashback amount")
        
        mws.click_toolbar("Cancel")
        mws.click_toolbar("No")

        if not mws.wait_for_button("INFO"):
            tc_fail("Info button is not visible")
        
        Navi.navigate_to("Global Info Editor")
        mws.select_tab("Site Configuration")
        
        # Verify value is not saved
        get_EBT_cashBack_afterSave = mws.get_value("Maximum EBT Cashback Amount", tab="Site Configuration")
        if get_EBT_cashBack_beforeSave != get_EBT_cashBack_afterSave:
            tc_fail("Value is saved after click on Cancel-->No button")

        return True

    @test
    def verify_valueIsSaved_afterClickOnYes(self):
        """
        Testlink Id: SL-1575 - Enable the cashback limit and configuration in the network configuration
        Description: Verify EBT cash back limit should be changed if we are clicking on Cancel > Yes button
        Args: None
        Returns: None
        """
        #Store the value before save
        get_EBT_cashBack_beforeSave = mws.get_value("Maximum EBT Cashback Amount", tab="Site Configuration")
        if not mws.set_value("Maximum EBT Cashback Amount", "200000", tab="Site Configuration"):
            tc_fail("Unable to set the value of EBT cashback amount")
        mws.click_toolbar("Cancel")
        mws.click_toolbar("Yes")

        if not mws.wait_for_button("INFO"):
            tc_fail("Unable to find Info button")
        
        # Verify value is saved after click on Cancel>Yes button
        Navi.navigate_to("Global Info Editor")
        mws.select_tab("Site Configuration")
        get_EBT_cashBack_afterSave = mws.get_value("Maximum EBT Cashback Amount", tab="Site Configuration")
        if get_EBT_cashBack_beforeSave == get_EBT_cashBack_afterSave:
            tc_fail("Value is not saved after click on Yes button")
                
        return True

    @test
    def verify_valueIsSaved_afterClickOnSave(self):
        """
        Testlink Id: SL-1575 - Enable the cashback limit and configuration in the network configuration
        Description: Verify EBT cash back limit should be changed if we are clicking on Save button
        Args: None
        Returns: None
        """
        # Store the value before save
        get_EBT_cashBack_beforeSave = mws.get_value("Maximum EBT Cashback Amount", tab="Site Configuration")
        
        debit_cashback_amount = int(mws.get_value("Debit Cashback Maximum", tab="Site Configuration"))
        if not mws.set_value("Maximum EBT Cashback Amount", debit_cashback_amount, tab="Site Configuration"):
            tc_fail("Unable to set the value of EBT cashback amount")
        mws.click_toolbar("Save")
        
        if not mws.wait_for_button("INFO"):
            tc_fail("Info button is not visible")
        
        # Verify value is saved after click on save
        Navi.navigate_to("Global Info Editor")
        mws.select_tab("Site Configuration")
        get_EBT_cashBack_afterSave = mws.get_value("Maximum EBT Cashback Amount", tab="Site Configuration")
        if get_EBT_cashBack_beforeSave == get_EBT_cashBack_afterSave:
            tc_fail("Value is not saved after click on Save button")
        
        mws.click_toolbar("Save")

        return True

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        pass