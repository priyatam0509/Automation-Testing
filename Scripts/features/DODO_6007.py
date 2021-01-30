"""
    File name: DODO_6007.py
    Tags:
    Description: Use only two buffers in retail transactions with prepays, preset and postpay.
    Author: Kayren Escobar
    Date created: 2020-04-20 07:21:07
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import Navi, mws, pos, system, forecourt_installation, networksim, crindsim, runas
from app.framework import EDH
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app.features import feature_activation
from app.util import constants
import time

class DODO_6007():
    """
    Description: Use only two buffers in retail transactions with prepays, preset and postpay.
    """

    def __init__(self):
        """
        Initializes the Template class.
        """
        # The logging object.         
        self.log = logging.getLogger()

        # The main MWS object 
        self.mws = mws
        
        # The main POS object
        self.pos = pos

        # The main EDH object
        self.edh = EDH.EDH()

        # The main crindsim object
        self.crindsim = crindsim

    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        """

        #Commercial feature activation
        #self.Commercial_feature_activation()

        #Commercial Diesel checkbox activation in forecourt installation 
        self.set_commercial_on_forecourt()

        # HostSim Response mode
        networksim.set_response_mode("Approval")
                
        # Disable all promtps

        networksim.disable_commercial_fuel_limits()
        networksim.disable_product_limits()
        networksim.disable_prompts() 

        # Set specif config for this script

        networksim.set_commercial_customer_information("ABC TRUCKING", "DENVER", "CO", "234W987")
        networksim.set_commercial_product_limit("True","CADV","Company funds cash advance",20.00)
        networksim.set_commercial_product_limit("True", "MERC", "Default category for merchandise", 30.00)        
        networksim.set_commercial_fuel_limit("True", "001", 50.00)
        networksim.set_commercial_fuel_limit("True", "002", 50.00)
        networksim.set_commercial_fuel_limit("True", "003", 50.00)
        networksim.set_commercial_fuel_limit_send_mode("fuel product configuration based",110,True)

        crindsim.set_mode("auto")
        crindsim.set_sales_target()

        #open Browser
        self.pos.connect()

        self.pos.sign_on()
    
    def Commercial_feature_activation(self):
        
        #Set the features to activate
        DEFAULT_COMMERCIAL = ["Base Passport", "Enhanced Store", "Enhanced Reporting", "Advanced Merchandising",
                    "Employee Management", "Enhanced Card Services", "Enhanced Loyalty Interface",
                    "Multiple Loyalty Interface", "Play at the Pump", "Mobile Payment",
                    "Prepaid Card Services", "Windows 10 License",  "Commercial Diesel", "Tablet POS", "Car Wash"]
        
        #Instatiate Feature Activation
        FA = feature_activation.FeatureActivation()
        
        # Activate defined Features
        if not FA.activate(DEFAULT_COMMERCIAL, mode="Passport Individual Bundles"):
            return False
    
    def set_commercial_on_forecourt(self):
        """
        Set the dispenser as commercial Diesel
        """
        fc_config = {
            "Dispensers" : {
                "Commercial Diesel": False #Transponder is now Commercial Check
            }
        }
        
        FC = forecourt_installation.ForecourtInstallation()
        mws.click("Set Up")

        # Set Commercial Diesel feature to the crind Configured as "Gilbarco"
        FC.change("Gilbarco", "Dispensers", fc_config.get("Dispensers"))

        mws.click_toolbar("Save")
        mws.click_toolbar("Save")
    
    def wait_for_new_msg(self, last_msg, psp_id, timeout=30):
        
        start = time.time()

        #check it a new message happened since the the last check
        while (last_msg == self.edh.get_last_msg_id(pspid=psp_id)) and (time.time() - start < timeout):
            
            self.log.debug("No new messages found")
            time.sleep(1) #seconds
        
        return last_msg 

    
    #TODO: fix this when we can check if the button enabled or disabled   
    @test
    def Retail_MultipleBuffers_Prepay_Prepay(self):
        
        """
        For the inside transaction with retail dispenser, it allows two buffers, 
		if a prepay transaction is made and it is not finished it is saved in 
		buffer A, another prepay transaction can be made and if it has not finished 
		it is saved in buffer B, then, it has the two transaction in its buffers and 
		it if you try to made other transaction is denied because both buffers are busy.
        """
        
        #Input constants

        trans_amount = "$5.00" # any value that gets an approval from the host
        crindsim.set_sales_target("money", "2")
        default_dispenser = '1'
		
        #first prepay, buffer A
        self.log.info(f"Adding prepay for {trans_amount}") 
        self.pos.add_fuel(trans_amount)
		
        # Pay the transaction
        self.log.info("Trying to click Pay")
        self.pos.pay(trans_amount)

        #second prepay, buffer B
        self.log.info(f"Adding prepay for {trans_amount}") 
        self.pos.add_fuel(trans_amount)
		
        # Pay the transaction
        self.log.info("Trying to click Pay")
        self.pos.pay(trans_amount)

        #postpay with two buffer are full
        self.pos.wait_for_disp_status("Fueling", timeout=10, verify=False)
        self.pos.wait_for_fuel(timeout=60)

        crindsim.lift_handle()
        self.pos.click('auth', timeout=20)

        #Check out for pop up about enable to auth if the two buffer are full
        msg = self.pos.read_message_box(timeout = 20)

        if msg!= "Unable to authorize dispenser 1 at this time. Try again later.":
            tc_fail("Must not handle up and auth fuel, if the buffers are full", exit = True)
        
        self.pos.click_message_box_key("Ok")

        #Free buffer A and buffer B
        self.pos.click_fuel_buffer('A')
        self.pos.pay()
        
        self.pos.select_dispenser(default_dispenser)
        
        self.pos.click_fuel_buffer('B')
        self.pos.pay()

        #Auth the transaction pending
        self.pos.select_dispenser(default_dispenser)
        
        crindsim.set_mode("auto")
        crindsim.set_sales_target("auth")
        self.pos.click('auth', timeout=20)

        self.pos.wait_for_disp_status("Fueling", timeout=10, verify=False)
        crindsim.lower_handle()
        self.pos.wait_for_fuel(timeout=60)

        self.pos.click_fuel_buffer('A')
        self.pos.click('Back')
        self.pos.pay()
    
    @test
    def Retail_MultipleBuffers_Prepay_PostPay(self):
        """
        For the inside and outside transactions with retail dispenser, 
        it allows two buffers, if a prepay transaction is made and it 
        is not finished it is saved in buffer A, and postpay transaction 
        can be made and if it has not finished it is saved in buffer B, 
        then, it has the two transaction in its buffers and it if you try 
        to made other transaction is denied because both buffers are busy.
        """
        #Input constants

        trans_amount = "$5.00" # any value that gets an approval from the host
        crindsim.set_sales_target("money", "2")
        default_dispenser = '1'
		
        #prepay, buffer A
        self.log.info(f"Adding prepay for {trans_amount}") 
        self.pos.add_fuel(trans_amount)

        # Pay the transaction
        self.log.info("Trying to click Pay")
        self.pos.pay(trans_amount)
        self.pos.wait_for_disp_status("Fueling", timeout=10, verify=False)
        self.pos.wait_for_fuel(timeout=60)

        #postpay, buffer B
        crindsim.set_mode("auto")
        crindsim.set_sales_target("auth")
    
        crindsim.lift_handle()
        self.pos.select_dispenser(default_dispenser)
        self.pos.click('auth', timeout=20)

        self.pos.wait_for_disp_status("Fueling")
        crindsim.lower_handle()
        self.pos.wait_for_disp_status("Fueling", timeout=10, verify=False)
        self.pos.wait_for_fuel(timeout=60)

        #Free buffer A and buffer B
        self.pos.click_fuel_buffer('A')
        self.pos.pay()
        
        self.pos.select_dispenser(default_dispenser)
        
        self.pos.click_fuel_buffer('B')
        self.pos.click('Back')
        self.pos.pay()
    
    @test
    def Retail_MultipleBuffers_PrepayPreset(self):
        
        """
        For the inside transaction with retail dispenser, 
        it allows two buffers, if a prepay transaction is 
        made and it is not finished it is saved in buffer A, 
        and another preset transaction can be made and it is 
        saved in buffer B, then, it has the two transaction 
        in its buffers and it if you try to made other transaction 
        is denied because both buffers are busy.
        """

        #Input constants
        trans_amount = "$5.00" # any value that gets an approval from the host
        crindsim.set_sales_target("money", "2")
        default_dispenser = '1'
		
        #prepay, buffer A
        self.log.info(f"Adding prepay for {trans_amount}") 
        self.pos.add_fuel(trans_amount)

        # Pay the transaction
        self.log.info("Trying to click Pay")
        self.pos.pay(trans_amount)
        self.pos.wait_for_disp_status("Fueling", timeout=10, verify=False)
        self.pos.wait_for_fuel(timeout=60)

        #preset, buffer B
        crindsim.set_mode("auto")
        crindsim.set_sales_target("auth")

        self.pos.add_fuel(trans_amount, 1, "preset")
        self.pos.wait_for_disp_status("Fueling", timeout=10, verify=False)
        self.pos.wait_for_fuel(timeout=60)

        #Free buffer A and buffer B
        self.pos.click_fuel_buffer('A')
        self.pos.pay()
        
        self.pos.select_dispenser(default_dispenser)
        
        self.pos.click_fuel_buffer('B')
        self.pos.click('Back')
        self.pos.pay()
    
    @test
    def Retail_MultipleBuffers_PresetPreset(self):
        
        """
        For the inside and outside transactions with retail dispenser, 
        it allows two buffers, if a preset transaction is made, it is 
        saved in buffer A, and another preset transaction can be made 
        it is saved in buffer B, then, it has the two transaction in 
        its buffers and it if you try to made other transaction is 
        denied because both buffers are busy.
        """

        #Input constants
        trans_amount = "$5.00" # any value that gets an approval from the host
        crindsim.set_mode("auto")
        crindsim.set_sales_target("auth")
        default_dispenser = '1'
		
        #preset inside, buffer A
        self.pos.add_fuel(trans_amount, 1, "preset")
        self.pos.wait_for_disp_status("Fueling", timeout=10, verify=False)
        self.pos.wait_for_fuel(timeout=60)

        #preset outside, buffer B
        crindsim.press_keypad("Enter")
        time.sleep(1)
        crindsim.press_keypad("3")
        time.sleep(1)
        crindsim.press_keypad("0")
        time.sleep(1)
        crindsim.press_keypad("0")
        time.sleep(1)
        crindsim.press_keypad("Enter")
        time.sleep(1)

        crindsim.lift_handle()
        self.pos.select_dispenser(default_dispenser)
        self.pos.click('auth', timeout=20)
        self.pos.wait_for_disp_status("Fueling", timeout=10, verify=False)
        self.pos.wait_for_fuel(timeout=60)

        #Free buffer A and buffer B
        self.pos.click_fuel_buffer('A')
        self.pos.click('Back')
        self.pos.pay()
        
        self.pos.select_dispenser(default_dispenser)
        
        self.pos.click_fuel_buffer('B')
        self.pos.click('Back')
        self.pos.pay()
    
    @test
    def Retail_MultipleBuffers_PresetPostpay(self):
        
        """
        For the inside and outside transactions with retail dispenser, 
        it allows two buffers, if a preset transaction is made, it is 
        saved in buffer A, and another postpay transaction can be made 
        it is saved in buffer B, then, it has the two transaction in its
         buffers and it if you try to made other transaction is denied 
         because both buffers are busy.
        """

        #Input constants
        trans_amount = "$5.00" # any value that gets an approval from the host
        crindsim.set_mode("auto")
        crindsim.set_sales_target("auth")        
        default_dispenser = '1'
		
        #preset, buffer A
        self.pos.add_fuel(trans_amount, 1, "preset")
        self.pos.wait_for_disp_status("Fueling", timeout=10, verify=False)
        self.pos.wait_for_fuel(timeout=60)

        #postpay, buffer B
        crindsim.lift_handle()
        self.pos.select_dispenser(default_dispenser)
        self.pos.click('auth', timeout=20)

        self.pos.wait_for_disp_status("Fueling")
        crindsim.lower_handle()
        self.pos.wait_for_disp_status("Fueling", timeout=10, verify=False)
        self.pos.wait_for_fuel(timeout=60)

        #Free buffer A and buffer B
        self.pos.click_fuel_buffer('A')
        self.pos.click('Back')
        self.pos.pay()
        
        self.pos.select_dispenser(default_dispenser)
        
        self.pos.click_fuel_buffer('B')
        self.pos.click('Back')
        self.pos.pay()
    
    @test
    def Retail_MultipleBuffers_PostpayPostpay(self):
        """
        For the outside transactions with retail dispenser, 
        it allows two buffers, if a postpay transaction is made, 
        it is saved in buffer A, and another postpay transaction 
        can be made it is saved in buffer B, then, it has the two 
        transaction in its buffers and it if you try to made other 
        transaction is denied because both buffers are busy.
        """
        #Input constants
        crindsim.set_mode("auto")
        crindsim.set_sales_target() 
        default_dispenser = '1'
		
        #postpay, buffer A

        crindsim.lift_handle()
        self.pos.select_dispenser(default_dispenser)
        self.pos.click('auth', timeout=20)

        self.pos.wait_for_disp_status("Fueling")
        crindsim.lower_handle()
        self.pos.wait_for_disp_status("Fueling", timeout=10, verify=False)
        self.pos.wait_for_fuel(timeout=60)

        #postpay, buffer B
        crindsim.lift_handle()
        self.pos.select_dispenser(default_dispenser)
        self.pos.click('auth', timeout=20)

        self.pos.wait_for_disp_status("Fueling")
        crindsim.lower_handle()
        self.pos.wait_for_disp_status("Fueling", timeout=10, verify=False)      
        self.pos.wait_for_fuel(timeout=60)

        #Free buffer A and buffer B
        self.pos.click_fuel_buffer('A')
        self.pos.click('Back')
        self.pos.pay()
        
        self.pos.select_dispenser(default_dispenser)
        
        self.pos.click_fuel_buffer('B')
        self.pos.click('Back')
        self.pos.pay()
    
    @test
    def Retail_MultipleBuffers_PostpayPreset(self):

        """
        For the outside transactions with retail dispenser, 
        it allows two buffers, if a postpay transaction is made, 
        it is saved in buffer A, and another preset transaction 
        can be made it is saved in buffer B, then, it has the two 
        transaction in its buffers and it if you try to made other 
        transaction is denied because both buffers are busy.
        """
        #Input constants
        crindsim.set_mode("auto")
        crindsim.set_sales_target("auth")
        default_dispenser = '1'
		
        #postpay, buffer A
        crindsim.lift_handle()
        self.pos.select_dispenser(default_dispenser)
        self.pos.click('auth', timeout=20)

        self.pos.wait_for_disp_status("Fueling")
        crindsim.lower_handle()
        self.pos.wait_for_disp_status("Fueling", timeout=10, verify=False)
        self.pos.wait_for_fuel(timeout=60)

        #preset outside, buffer B
        crindsim.press_keypad("Enter")
        time.sleep(1)
        crindsim.press_keypad("4")
        time.sleep(1)
        crindsim.press_keypad("0")
        time.sleep(1)
        crindsim.press_keypad("0")
        time.sleep(1)
        crindsim.press_keypad("Enter")
        time.sleep(1)

        crindsim.lift_handle()
        self.pos.select_dispenser(default_dispenser)
        self.pos.click('auth', timeout=20)
        self.pos.wait_for_disp_status("Fueling", timeout=10, verify=False)
        self.pos.wait_for_fuel(timeout=60)

        #Free buffer A and buffer B
        self.pos.click_fuel_buffer('A')
        self.pos.click('Back')
        self.pos.pay()
        
        self.pos.select_dispenser(default_dispenser)
        
        self.pos.click_fuel_buffer('B')
        self.pos.click('Back')
        self.pos.pay()
    
    @test
    def Retail_MultipleBuffers_OldInterface(self):

        """
        This a regresion case using the old interface in a retail 
        transaction using two buffer with a prepays transactions.
        """

        # Moving to the old fuel mode
        
        cmd = f'reg add HKEY_LOCAL_MACHINE\{constants.HTMLPOS_SUBKEY}\ /v htmlpos.fuelMode /t REG_DWORD /d 0x00000000 /f'
        
        self.log.info(f"About to update registry with {cmd}")
        result = runas.run_sqlcmd(cmd, destination="POSSERVER01", user="PassportTech", password="911Tech")
        
        self.log.info(f"The update returned {result} ")
        if result['pid'] == 1:
            self.log.error(f"Unable to update registry with  {cmd}, the result is: {result['output']} ")
            
            return False

        #Input constants

        trans_amount = "$5.00" # any value that gets an approval from the host
        crindsim.set_sales_target("money", "2")
        default_dispenser = '1'
		
        #first prepay, buffer A
        self.log.info(f"Adding prepay for {trans_amount}") 
        self.pos.add_fuel(trans_amount)
		
        # Pay the transaction
        self.log.info("Trying to click Pay")
        self.pos.pay(trans_amount)

        #second prepay, buffer B
        self.log.info(f"Adding prepay for {trans_amount}") 
        self.pos.add_fuel(trans_amount)

        # Pay the transaction
        self.log.info("Trying to click Pay")
        self.pos.pay(trans_amount)       

        #Free buffer A and buffer B
        self.pos.select_dispenser(default_dispenser)
        
        self.pos.click_fuel_buffer('A')
        self.pos.pay()
        
        self.pos.select_dispenser(default_dispenser)
        
        self.pos.click_fuel_buffer('B')
        self.pos.pay()

        cmd = f'reg add HKEY_LOCAL_MACHINE\{constants.HTMLPOS_SUBKEY}\ /v htmlpos.fuelMode /t REG_DWORD /d 0x00000001 /f'
        
        self.log.info(f"About to update registry with {cmd}")
        result = runas.run_sqlcmd(cmd, destination="POSSERVER01", user="PassportTech", password="911Tech")
        
        self.log.info(f"The update returned {result} ")
        if result['pid'] == -1:
            self.log.error(f"Unable to update registry with  {cmd}, the result is: {result['output']} ")
            
            return False
    
    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """

        self.pos.close()
