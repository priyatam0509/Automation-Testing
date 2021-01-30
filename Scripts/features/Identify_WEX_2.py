"""
    File name: Identify_WEX_2.py
    Brand: Chevron
    Story ID : PEACOCK-3924
    Description: Verify that POS shall not use the service indicator
                 on the magnetic stripe to identify a chip card for WEX card products.
    Author: Asha
    Date created: 2020-05-11 13:00
    Python Version: 3.7
"""

import logging, time
from app import Navi, mws, pos, system, pinpad, runas, pdl
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class Identify_WEX_2():
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
    def manual_wex_noTImask_1(self):     
        """
        Zephyr Id: (tc5)To verify when technology indicator token is not present in the Track 2 Mask field of the parameter table (PDL) and 
        WEX card of bin range 690046 with TI 2 is swiped on pinpad then POS uses the magstripe reader to process the card when performed Manual Fuel sale
        & dry stock transactions
        Args: None
        Returns: None
        """
        # Removing technology indicator token from Track 2 mask of the parameter table (PDL)
        cmd = "update CardDataTable set Track2MaskLen = 28, Track2Mask='c;p19c=e04q01r02v05x04q01c?l' where PANRangeLow like '%690046%' and CardRecName like '%WEX%' and CardRecType like '%C%' or PANRangeLow like '%707138%' and CardRecName like '%WEX%' and CardRecType like '%C%';"
        output = runas.run_sqlcmd(cmd, cmdshell=False)['output']
        output_list = output.split("\n")
        
        if output_list[1] != '(2 rows affected)':
            tc_fail("Not able to remove TI Token t01 from track2mask")

        # Add Fuel in manual mode
        pos.add_fuel(self.fuel_amount, mode="Manual", grade=self.fuel_grade)

        # Add item with plu 1
        pos.add_item("1", method="PLU")
        
        # paying using WEX Card
        if not pos.click_function_key('Pay', timeout=3):
            return False
        if not pos.click_tender_key("Card"):
            return False
        
        # swipe wex emv card of bin range 690046
        try:
            pinpad.swipe_card(brand=system.get_brand(), card_name="WEX1_EMV")
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
        
        # Verifying sale amount on receipt
        if not pos.check_receipt_for(sale_amount):
           tc_fail("Sale amount not matched with receipt")

        return True

    @test
    def manual_wex_noTImask_2(self):     
        """
        Zephyr Id: (tc15)To verify when technology indicator token is not present in the Track 2 Mask field of the parameter table (PDL) and 
        WEX card of bin range 707138 with TI 2 is swiped on pinpad then POS uses the magstripe reader to process the card when performed Manual Fuel sale
        & dry stock transactions
        Args: None
        Returns: None
        """
        # Add Fuel in manual mode
        pos.add_fuel(self.fuel_amount,mode="Manual",grade=self.fuel_grade)

        # Add item with plu 1
        pos.add_item("1", method="PLU")
        
        # paying using WEX Card
        if not pos.click_function_key('Pay', timeout=3):
            return False
        if not pos.click_tender_key("Card"):
            return False
        
        # swipe wex emv card of bin range 707138
        try:
            pinpad.swipe_card(brand=system.get_brand(),card_name="WEX2_EMV")
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
    def prepay_wex_noTImask_noTI2_1(self):  
        """
        Zephyr Id: (tc7)To verify when technology indicator token is not present in the Track 2 Mask field of the parameter table (PDL) and 
        WEX card of bin range 690046 with TI not equal to 2 is swiped on pinpad then pos uses the magstripe reader to process the card when performed prepay & drystock  
        Args: None
        Returns: None
        """
        # Add Fuel in prepay mode
        pos.add_fuel(self.fuel_amount,grade=self.fuel_grade)

        # Add item with plu 1
        pos.add_item("1", method="PLU")
        
        # paying using WEX Card
        if not pos.click_function_key('Pay', timeout=3):
            return False
        if not pos.click_tender_key("Card"):
            return False
        
        # swipe wex MSD card of bin range 707138
        try:
            pinpad.swipe_card(brand=system.get_brand(), card_name="WEX1_MSD")
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
        
        # Verifying Receipt
        if not pos.check_receipt_for(sale_amount):
           tc_fail("Sale amount not matched with receipt")

        return True

    @test
    def prepay_wex_noTImask_noTI2_2(self):  
        """
        Zephyr Id: (tc17)To verify when technology indicator token is not present in the Track 2 Mask field of the parameter table (PDL) and 
        WEX card of bin range 707138 with TI not equal to 2 is swiped on pinpad then pos uses the magstripe reader to process the card when performed prepay & drystock  
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
        
        # swipe wex MSD card of bin range 707138
        try:
            pinpad.swipe_card(brand=system.get_brand(),card_name="WEX2_MSD")
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
        
        # Verifying receipt
        if not pos.check_receipt_for(sale_amount):
           tc_fail("Sale amount not matched with receipt")

        return True

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        Navi.navigate_to("mws")
        pd = pdl.ParameterDownload()
        if not pd.request():
            return False