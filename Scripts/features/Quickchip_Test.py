"""
    File name: Quickchip_Test.py
    Tags:
    Story ID : PEACOCK-3834
    Description: Verify that Enable quickchip field is not present 
                 for all brands of Hps-Chicago and HPS-Dallas network
    Author: Asha
    Date created: 2020-01-29 18:00
    Python Version: 3.7
"""

import logging, time
from app import Navi, mws, system, pos, pinpad, store_close, networksim, register_setup
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app.framework import EDH
from app import runas
from app import OCR

class Quickchip_Test():
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
        self.fuel_amount = "$3.00"
        self.fuel_grade = "Diesel 1"
        self.item_amount = "$1.00"

        self.brand = system.get_brand()

    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        # Perform store close for below brand for card transactions
        if self.brand.upper() == "CITGO" or self.brand.upper() == "MARATHON":
            # navigating to pos and open till
            Navi.navigate_to("POS")
            pos.sign_on()
            SC = store_close.StoreClose()
            if not SC.begin_store_close():
                self.log.error("There was an issue with the Store Close")

        if self.brand.upper() == "HPS-DALLAS":
            # navigating to pos and wait for dispenser to finish EMV download 
            Navi.navigate_to("POS")
            pos.sign_on()
            if not pos.wait_disp_ready(idle_timeout=60, dl_timeout=900):
                return False

        self.log.info("Set the host sim in automated mode, EMV PDL is failing in approval mode")
        networksim.set_response_mode('Automated')

        # checking if EMV information was downloaded 


        if not self.is_emv_data_present():  

            self.log.warning("EMV information wasn't donwload yet, strating retry process")          
            
            if not 'Online' in networksim.get_network_status()['payload']['status']:
            
                self.log.warning("Host sim isn't online, restarting it")          
                networksim.stop_simulator()

                self.log.info("Waiting 15 seconds before starting the simulator")
                time.sleep(15) # Giving time to the host sim to stop

                networksim.start_simulator()

                self.log.info("Waiting 5 minutes to allow the EDH re-connect")
                time.sleep(300) # giving 5 minutes to allow the EDH to connect
            
                if not 'Online' in networksim.get_network_status()['payload']['status']:
                    
                    self.log.error("Unable to connect to the host sim, please check it is working")
                    return False

            
            cmd = 'update Global set ForceEMVPDL = 1'
            self.log.info(f"About to force EMV download with the followign query: {cmd} ")

            output = runas.run_sqlcmd(cmd, cmdshell=False)['output']
            self.log.info(f"Force EMV donwload result: {output}")

            edh = EDH.EDH()

            edh.restart()

            self.log.info("waiting 5 minutes to let the EDH connect")

            time.sleep(1) # giving 5 minutes to allow the EDH to connect and download EMV data

            self.enable_EMV(enable=False)

            self.log.info("Giving 1 minutes to let pinpad restart")
            
            time.sleep(60)

            self.log.info("Attempting to log in in the POS before going to the mws")
            pos.sign_on()

            self.enable_EMV()

            self.log.info("Giving 2 minutes to download information")
            
            time.sleep(120)

            mws.click_toolbar("Exit")

            if not self.is_emv_data_present():

                self.log.error("Unable to download EMV information from the host")
                return False
                

    @test
    def verify_quickchip_field(self):
        """
        Zephyr Id: This will check Enable quickchip field on EMV parameters tab as well as 
                   it's value in Network database
        Args: None
        Returns: None
        """
                      
        if self.brand.upper() == "HPS-CHICAGO" or self.brand.upper() == "FASTSTOP":

            # Navigating to network site configuration 
            Navi.navigate_to("Network Site Configuration")

            # Navigating to EMV parameters tab (Indoor)   
            if not mws.select_tab("EMV Parameters (Indoor)"):
                tc_fail("not able to Select tab EMV Parameters (Indoor)")

            # Sql query to fetch EnableQuickchip column value from Network Database for each Card for indoor    
            cmd = "select EnableQuickChip from HPSC_EMVParameters where Outdoor = 0 and ApplicationName=" 

            card_list = mws.get_value("Card List", "EMV Parameters (Indoor)")

            for item in card_list:
                new_query = cmd    
                mws.select("Card List", item, "EMV Parameters (Indoor)")

                # check Enable Quick chip field on screen of EMV Parameters tab   
                if OCR.findText("Enable QuickChip"):   
                    tc_fail(f"Enable Quickchip field is present for card {item} on screen")

                # check field value in database    
                if "as Credit" in item:
                    # to remove (as Credit) from cards
                    new_query = cmd+f"'{item[0:-12]}'" 
                else:
                    new_query = cmd+f"'{item}'"

                #Fetching the output of query
                output = runas.run_sqlcmd(new_query, cmdshell=False)['output']
                    
                # Turning string into list of strings that have '\n' delimitation
                output_list = output.split("\n")
                    
                # Remove all spaces from string
                str1 = output_list[2].replace(' ','')

                if not str1 == '1':   
                    tc_fail(f"Enable Quickchip column value is not 1 for card {item} in Network Database")

            
        elif (self.brand.upper() == "CITGO" or 
              self.brand.upper() == "MARATHON" or 
              self.brand.upper() == "HPS-DALLAS"):

            # Navigating to Global info editor 
            Navi.navigate_to("Global Info Editor")

            # Navigating to EMV parameters tab    
            if not mws.select_tab("EMV Parameters"):
                tc_fail("not able to select tab EMV Parameters")

            # Sql query to fetch EnableQuickchip column value from Network Database for each Card for indoor    
            cmd = "select EnableQuickChip from ADSD_EMVParameters where ApplicationName=" 

            card_list = mws.get_value("Card List","EMV Parameters")

            for item in card_list:

                mws.select("Card List", item, "EMV Parameters")

                # check field on screen
                if OCR.findText("Enable QuickChip"):   
                    tc_fail(f"Enable Quickchip field is present for card {item} on screen")

                # check field value in database
                # Fetching the output of query
                output = runas.run_sqlcmd(cmd+f"'{item}'", cmdshell=False)['output']
                    
                # Turning string into list of strings that have '\n' delimitation
                output_list = output.split("\n")
                    
                # Remove all spaces from string
                str1 = output_list[2].replace(' ','')

                if not str1 == '1':   
                    tc_fail(f"Enable Quickchip column value is not 1 for card {item} in Network Database")
        
        mws.click_toolbar("Save")
        return True

    @test
    def prepay_EMV(self):
        """
        Zephyr Id: This will make a prepay sale of fuel & item and 
                   verify transaction done by EMV Card
        Args: None
        Returns: None
        """

        self.log.info("Set the host sim in Approval mode for transactions")
        networksim.set_response_mode('Approval')
        
        # navigating to pos
        Navi.navigate_to("POS")
        pos.sign_on()

        #wait for dispenser to be Ready
        if not pos.wait_disp_ready(idle_timeout=60):
            return False

        # adding fuel
        if not pos.add_fuel(self.fuel_amount, grade = self.fuel_grade):
            return False  

        # adding item1
        if not pos.add_item(item="Item 1", price = self.item_amount):
            return False  

        # paying using EMV Card
        if not pos.click_function_key('Pay', timeout=3):
            return False
        if not pos.click_tender_key("Card"):
            return False
        try:
            result = pinpad.use_card(card_name="EMVAmEx")
        except Exception as e:
            self.log.warning(f"Insert Card in pinpad failed. Exception: {e}")
            pos.click_keypad("CANCEL")
            return False
        if not result['success']:
            self.log.warning(f"Insert Card in pinpad failed. POST payload: {result}")
            return False

        if not pos.verify_idle(timeout=40):
            tc_fail("Transaction Failed pos was not idle")

        # Wait until dispenser 1 is idle
        if not pos.wait_for_disp_status('IDLE'):
            return False
        
        self.fuel_amount = self.fuel_amount.replace("$","")

        self.item_amount = self.item_amount.replace("$","")

        # calculating total amount of sale
        sale_amount = float(self.fuel_amount) + float(self.item_amount)
        sale_amount = "$" + str(sale_amount) + "0"
        
        # fetching Total from journal
        balance = pos.read_balance()
        total_amount = balance['Total']
    
        # verifying total amount of sale
        if not sale_amount == total_amount:
            tc_fail("sale amount is not correct")

        return True    

    def is_emv_data_present(self):

        cmd = "select * from ADSD_EMVParameters" 

        output = runas.run_sqlcmd(cmd, cmdshell=False)['output']

        if '0 rows affected' in output:
            
            self.log.error("EMV Download not performed!!!")

            return False
        
        return True

    def enable_EMV(self, enable=True):

        config = {
                    "EMV Capable": enable               
            }             

        RS = register_setup.RegisterSetup()

        RS.change(reg_num="1", machine_name="POSSERVER01", config=config)

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        pass