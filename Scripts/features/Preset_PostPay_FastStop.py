"""
    File name: Preset_PostPay_FastStop.py
    Brand: FastStop
    Description: [PEACOCK-3186] This will perform preset postpay sale with faststop card
                 After sale it verifies network message for standard map, Z01-13 P7 map and Client dictionary Data 
    Author: Asha 
    Date created: 2020-04-28 10:16:52
    Date last modified: 
    Python Version: 3.7
"""

import logging, time
from app import Navi, pos, system
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from Scripts.features import faststop_network_message_interpreter

class Preset_PostPay_FastStop():
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
        # Example: self.log.info(f"Current value of var: {my_var}")
        self.log = logging.getLogger()

        # parameters to be used in sale
        self.fuel_amount = "$2.00"

    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        #Navigate to POS screen
        Navi.navigate_to("POS")
        
        # Sign on to POS screen if not already sign-on
        pos.sign_on()

    @test
    def fuel_preset_postpay_sale(self):
        """
        TestLink Id: This will add fuel and perform postpay sale. 
                     After sale it verifies network message for standard map, Z01-13 P7 map and Client dictionary Data
        Args: None
        Returns: None
        """

        # Add fuel in preset mode
        pos.add_fuel(self.fuel_amount, mode="preset", grade="Diesel 1")
        
        # Check if fueling is completed
        if not pos.wait_for_disp_status('IDLE', timeout=90):
            return False

        # Take fuel inside POS
        pos.click_suspended_transaction()

        # Perform card Payment with FastStop card
        pos.pay_card(brand='FASTSTOP', card_name='Fast Stop Commercial')

        balance = pos.read_balance()
        total = balance['Total']
        self.log.debug(f"total is {total}")

        # Create list to have product data used in sale
        prod1_list = ["004", self.fuel_amount]   
        
        req_cmd = "Select NetworkMessage from networkmessages where NetworkPSPId=20 and NetworkMessage like '%TESOZ01%' and NetworkMessage like '%TESOP1%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Request Network Message is {strNetworkMessage}")

        #Verify Client dictionary data in network message
        if not faststop_network_message_interpreter.verify_faststop_clientDisctionaryData(strNetworkMessage,'F01'):
            tc_fail("Client Dictionary Data in network message is not correct")

        # Verify Standard Map in network message
        if not faststop_network_message_interpreter.verify_faststop_standardMap(strNetworkMessage):
            tc_fail("Standard Map in network Mesage is not correct")
        
        #verify Z01 13 P7 map
        if not faststop_network_message_interpreter.verify_faststop_Z01_13_p7Map(strNetworkMessage,total,prod1_list):
            tc_fail("Z01 13 P7 map in network Mesage is not correct")
        
        # Fetch Network message for 1st respnse
        res_cmd = "Select NetworkMessage from networkmessages where NetworkPSPId=20 and NetworkMessage like '%M0014%'order by NetworkMessageId desc"
        res_NetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(res_cmd)
        self.log.info(f"Z01 14 Network Message is {res_NetworkMessage}")
        
        #verify Z01-14 map
        if not faststop_network_message_interpreter.verify_faststop_Z01_14_Map(res_NetworkMessage):
            tc_fail("Z01 14 P7 map in network Mesage is not correct")

        return True

    @test
    def fuelDryStock_preset_postpay_sale(self):
        """
        TestLink Id: This will add fuel with Dry Stock and perform postpay sale.
                     After sale it verifies network message for standard map, Z01-13 P7 map and Client dictionary Data
        Args: None
        Returns: None
        """
        # Add generic item
        pos.add_item(item='Generic Item')

        # Add fuel in preset mode
        pos.add_fuel(self.fuel_amount, mode="preset")
        
        # Check if fueling is completed
        if not pos.wait_for_disp_status('IDLE', timeout=90):
            return False

        # Take fuel inside POS
        pos.click_suspended_transaction()

        # Perform card Payment with FastStop card
        pos.pay_card(brand='FASTSTOP',card_name='Fast Stop Commercial')

        balance = pos.read_balance()
        total = balance['Total']
        self.log.debug(f"total is {total}")
        
        # Create list to have product data used in sale
        prod1_list = ["004",self.fuel_amount]
        prod2_list = ["400","$0.01"]

        req_cmd = "Select NetworkMessage from networkmessages where NetworkPSPId=20 and NetworkMessage like '%TESOZ01%' and NetworkMessage like '%TESOP1%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Request Network Message is {strNetworkMessage}")

        #Verify Client dictionary data in network message
        if not faststop_network_message_interpreter.verify_faststop_clientDisctionaryData(strNetworkMessage,'F01'):
            tc_fail("Client Dictionary Data in network message is not correct")

        # Verify Standard Map in network message
        if not faststop_network_message_interpreter.verify_faststop_standardMap(strNetworkMessage):
            tc_fail("Standard Map in network message is not correct")
        
        #verify Z01 13 P7 map
        if not faststop_network_message_interpreter.verify_faststop_Z01_13_p7Map(strNetworkMessage,total,prod1_list,prod2_list):
            tc_fail("Z01 13 P7 map in network message is not correct")
        
        # Fetch Network message for 1st respnse
        res_cmd = "Select NetworkMessage from networkmessages where NetworkPSPId=20 and NetworkMessage like '%M0014%'order by NetworkMessageId desc"
        res_NetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(res_cmd)
        self.log.info(f"Z01 14 Network message is {res_NetworkMessage}")
    
        #verify Z01-14 map
        if not faststop_network_message_interpreter.verify_faststop_Z01_14_Map(res_NetworkMessage):
            tc_fail("Z01 14 P7 map in network message is not correct")

        return True

    @test
    def fuelDrystockCarwash_preset_postpay_sale(self):
        """
        TestLink Id: This will add fuel,Dry Stock and car Wash and perform postpay sale.
                     After sale it verifies network message for standard map, Z01-13 P7 map and Client dictionary Data
        Args: None
        Returns: None
        """
        # Add generic item
        pos.add_item(item='Generic Item')

        pos.add_item("1234",method="plu",qualifier="CARWASH 1")

        # Add fuel in preset mode
        pos.add_fuel(self.fuel_amount,mode="preset")
        
        # Check if fueling is completed
        if not pos.wait_for_disp_status('IDLE',timeout=90):
            return False

        # Take fuel inside POS
        pos.click_suspended_transaction()

        # Perform card Payment with FastStop card
        pos.pay_card(brand='FASTSTOP',card_name='Fast Stop Commercial')

        balance = pos.read_balance()
        total = balance['Total']
        self.log.debug(f"total is {total}")
        
        # Create list to have product data
        prod1_list = ["004",self.fuel_amount]
        prod2_list = ["102","$2.50"]
        prod3_list = ["400","$0.01"]

        req_cmd = "Select NetworkMessage from networkmessages where NetworkPSPId=20 and NetworkMessage like '%TESOZ01%' and NetworkMessage like '%TESOP1%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 13 Request Network Message is {strNetworkMessage}")

        #Verify client dictionary data in network message
        if not faststop_network_message_interpreter.verify_faststop_clientDisctionaryData(strNetworkMessage,'F01'):
            tc_fail("Client Dictionary Data in network message is not correct")

        # Verify Standard Map in network message
        if not faststop_network_message_interpreter.verify_faststop_standardMap(strNetworkMessage):
            tc_fail("Standard Map in network message is not correct")
        
        #verify zo1 13 P7 map
        if not faststop_network_message_interpreter.verify_faststop_Z01_13_p7Map(strNetworkMessage,total,prod1_list,prod2_list,prod3_list):
            tc_fail("Z01 13 P7 map in network message is not correct")
        
        # Fetch Network message for 1st respnse
        res_cmd = "Select NetworkMessage from networkmessages where NetworkPSPId=20 and NetworkMessage like '%M0014%'order by NetworkMessageId desc"
        res_NetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(res_cmd)
        self.log.info(f"Z01 14 Network Message is {res_NetworkMessage}")
        
        #verify Z01-14 map
        if not faststop_network_message_interpreter.verify_faststop_Z01_14_Map(res_NetworkMessage):
            tc_fail("Z01 14 P7 map in network message is not correct")

        return True
    
    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        pass
