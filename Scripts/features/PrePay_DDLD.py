"""
    File name: PrePay_DDLD.py
    Brand: FastStop
    Description: [PEACOCK-3242] This will perform PrePay sale with debit card and verify DDLD map
    Author: Deepak Verma
    Date created: 2020-04-28 14:53:24
    Date last modified: 
    Python Version: 3.7
"""

import logging,time
from app import Navi, pos, system
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from Scripts.features import faststop_network_message_interpreter

class PrePay_DDLD():
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

        # Parameters to be used in sale
        self.fuel_amount = "$5.00"
        self.fuel_grade = "Diesel 1"

    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        # Navigate to POS screen
        Navi.navigate_to("POS")
        
        # Sign on to POS screen if not already sign-on
        pos.sign_on()

    @test
    def fuel_prepay_sale(self):
        """
        Testlink Id : This will add fuel and Perform a prepay fuel sale with debit card.
                      After sale this will verify network message for Standard map, D003 map 
        Args: None
        Returns: None
        """
        #Create a list of product data
        prod1_list = ["004", self.fuel_amount, "01000", "5000", "01"]

        #Add Fuel
        pos.add_fuel(self.fuel_amount,grade=self.fuel_grade)
        
        #Perform card Payment with FastStop debit card
        pos.pay_card(brand='FASTSTOP', card_name='Debit')

        # Wait until dispenser 1 is idle
        if not pos.wait_for_disp_status('IDLE',timeout=90):
            return False
        
        balance = pos.read_balance()
        total = balance['Total']
        self.log.debug(f"total is {total}")
        
        # Fetch network message for 1st request
        req_cmd = "Select networkMessage from networkmessages where NetworkMessage like '%TESOZ01MN%' and NetworkMessage like '%D003%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"D003 Network Message is {strNetworkMessage}")
        
        #verify D003 map
        if not faststop_network_message_interpreter.verify_D0_ClientDictionaryData_DDLD(strNetworkMessage, "D", prod1_list):
            tc_fail("D003 map in network Mesage is not correct")

        return True  

    @test
    def fuelWithDryStock_prepay_sale(self):
        """
        Testlink Id : This will add fuel and item and Perform a prepay fuel sale with debit card.
                      After sale this will verify network message for Standard map, D003 map 
        Args: None
        Returns: None
        """
        #Create a list of product data
        prod1_list = ["004", self.fuel_amount, "01000", "5000", "01"]
        prod2_list = ["400", "01000", "$0.01"]

        # Add Dry Stock item
        pos.add_item(item='Generic Item')

        #Add Fuel
        pos.add_fuel(self.fuel_amount,grade=self.fuel_grade,verify=False)
        
        # Perform card Payment with FastStop debit card
        pos.pay_card(brand='FASTSTOP',card_name='Debit')

        # Wait until dispenser 1 is idle
        if not pos.wait_for_disp_status('IDLE',timeout=90):
            return False
    
        balance = pos.read_balance()
        total = balance['Total']
        self.log.debug(f"total is {total}")
        
        # Fetch network message for 1st request
        req_cmd = "Select networkMessage from networkmessages where NetworkMessage like '%TESOZ01MN%' and NetworkMessage like '%D003%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"D003 Network Message is {strNetworkMessage}")

        #verify D003 map
        if not faststop_network_message_interpreter.verify_D0_ClientDictionaryData_DDLD(strNetworkMessage, "D", prod1_list, prod2_list):
             tc_fail("D003 map in network Mesage is not correct")

        return True  

    @test
    def fuelDryStockCarWash_prepay_sale(self):
        """
        Testlink Id : This will add fuel,Dry stock and car wash and Perform a prepay sale with debit card.
                      After sale this will verify network message for Standard map, D003 map
        Args: None
        Returns: None
        """
        #Create a list of product data
        prod1_list = ["004", self.fuel_amount, "01000", "5000", "01"]
        prod2_list = ["102", "01000", "$2.50"]
        prod3_list = ["400", "01000", "$0.01"]

        # Add Dry Stock item
        pos.add_item(item='Generic Item')

        # Add Car Wash Item
        pos.add_item("1234",method="plu",qualifier="CARWASH 1")

        # Add Fuel
        pos.add_fuel(self.fuel_amount, grade=self.fuel_grade)
        
        # Perform card Payment with FastStop debit card
        pos.pay_card(brand='FASTSTOP',card_name='Debit')

        # Wait until dispenser 1 is idle
        if not pos.wait_for_disp_status('IDLE',timeout=90):
            return False
        
        balance = pos.read_balance()
        total = balance['Total']
        self.log.debug(f"total is {total}")
        
        # Fetch network message for 1st request
        req_cmd = "Select networkMessage from networkmessages where NetworkMessage like '%TESOZ01MN%' and NetworkMessage like '%D003%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"D003 Network Message is {strNetworkMessage}")

        #verify D003 map
        if not faststop_network_message_interpreter.verify_D0_ClientDictionaryData_DDLD(strNetworkMessage, "D", prod1_list, prod2_list, prod3_list):
            tc_fail("D003 map in network Mesage is not correct")

        return True      

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        pass