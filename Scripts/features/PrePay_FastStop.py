"""
    File name: Prepay_FastStop.py
    Brand: FastStop
    Description: [PEACOCK-3184] This will perform PrePay sale with FastStop card
                 After sale this will verify network message for Standard map, Z01-05 P7 map and Z01-11 P7 map
    Author: Asha
    Date created: 2020-4-28 14:53:24
    Date last modified: 
    Python Version: 3.7
"""

import logging,time
from app import Navi, pos, system, networksim
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from Scripts.features import faststop_network_message_interpreter

class PrePay_FastStop():
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
        self.fuel_amount = "$2.00"
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

        networksim.set_response_mode("Approval")

    @test
    def fuel_prepay_sale(self):
        """
        Testlink Id : This will add fuel and Perform a prepay fuel sale with Fast Stop card.
                      After sale this will verify network message for Standard map, Z01-05 P7 map and Z01-11 P7 map 
        Args: None
        Returns: None
        """
        #wait for dispemser to be Ready
        if not pos.wait_disp_ready(idle_timeout=90):
            return False

        pos.add_fuel(self.fuel_amount, grade=self.fuel_grade)
        
        # Perform card Payment with FastStop card
        pos.pay_card(brand='FASTSTOP', card_name='Fast Stop Commercial')

        # Wait until dispenser 1 is idle
        if not pos.wait_for_disp_status('IDLE', timeout=90):
            return False

        balance = pos.read_balance()        
        total = balance['Total']
        self.log.debug(f"total is {total}")
        
        # Create list to have product data used in sale
        prod1_list = ["004", self.fuel_amount]

        # Fetch network message for 1st request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkPSPId=20 and NetworkMessage like '%TESOZ01%' and NetworkMessage like '%P705%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 05 Network Message is {strNetworkMessage}")

        # Verify Client dictionary data in network message
        if not faststop_network_message_interpreter.verify_faststop_clientDisctionaryData(strNetworkMessage,"F01"):
            tc_fail("Client Dictionary Data in network message is not correct")

        # Verify Standard Map in network message
        if not faststop_network_message_interpreter.verify_faststop_standardMap(strNetworkMessage):
            tc_fail("Standard Map in network Mesage is not correct")
        
        # verify Z01-05 P7 map
        if not faststop_network_message_interpreter.verify_faststop_Z01_05_p7Map(strNetworkMessage,total,prod1_list):
            tc_fail("Z01 05 P7 map in network Mesage is not correct")
        
        # Fetch Network message for 1st response
        res_cmd = "Select NetworkMessage from networkmessages where NetworkPSPId=20 and NetworkMessage like '%M0006%'order by NetworkMessageId desc"
        res_NetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(res_cmd)
        self.log.info(f"Z01 06 Network Message is {res_NetworkMessage}")
        
        # verify Z01-06 map
        if not faststop_network_message_interpreter.verify_faststop_Z01_06_Map(res_NetworkMessage):
            tc_fail("Z01 06 P7 map in network Message is not correct")

        # Fetch network message for 2nd request
        req_cmd1 = "Select NetworkMessage from networkmessages where NetworkPSPId=20 and NetworkMessage like '%TESOZ01%' and NetworkMessage like '%P711%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage1 = faststop_network_message_interpreter.fetch_networkmessage(req_cmd1)
        self.log.info(f"Z01 11 Network Message is {strNetworkMessage1}")
        
        # verify Z01-11 P7 map
        if not faststop_network_message_interpreter.verify_faststop_Z01_11_p7Map(strNetworkMessage1,total):
            tc_fail("Z01 11 P7 map in network Message is not correct")
        
        return True  

    @test
    def fuelDrystock_prepay_sale(self):
        """
        Testlink Id : This will add fuel with Dry stock and Perform a prepay fuel sale with Fast Stop card.
                      After sale this will verify network message for Standard map, Z01-05 P7 map and Z01-11 P7 map 
        Args: None
        Returns: None
        """
        pos.add_item(item='Generic Item')

        pos.add_fuel(self.fuel_amount, grade=self.fuel_grade)
        
        # Perform card Payment with FastStop card
        pos.pay_card(brand='FASTSTOP', card_name='Fast Stop Commercial')

        # Wait until dispenser 1 is idle
        if not pos.wait_for_disp_status('IDLE', timeout=90):
            return False
        
        balance = pos.read_balance()
        total = balance['Total']
        self.log.debug(f"total is {total}")

        # Create list to have product data used in sale
        prod1_list = ["004",self.fuel_amount]
        prod2_list = ["400","$0.01"]
        
        # Fetch network message for 1st request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkPSPId=20 and NetworkMessage like '%TESOZ01%' and NetworkMessage like '%P705%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 05 Network Message is {strNetworkMessage}")

        #Verify Client dictionary data in network message
        if not faststop_network_message_interpreter.verify_faststop_clientDisctionaryData(strNetworkMessage,"F01"):
            tc_fail("Client Dictionary Data in network message is not correct")

        # Verify Standard Map in network message
        if not faststop_network_message_interpreter.verify_faststop_standardMap(strNetworkMessage):
            tc_fail("Standard Map in network message is not correct")
        
        #verify Z01-05 P7 map
        if not faststop_network_message_interpreter.verify_faststop_Z01_05_p7Map(strNetworkMessage,total,prod1_list,prod2_list):
            tc_fail("Z01 05 P7 map in network message is not correct")
        
        # Fetch Network message for 1st response
        res_cmd = "Select NetworkMessage from networkmessages where NetworkPSPId=20 and NetworkMessage like '%M0006%'order by NetworkMessageId desc"
        res_NetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(res_cmd)
        self.log.info(f"Z01 06 Network Message is {res_NetworkMessage}")
        
        #verify Z01-06 map
        if not faststop_network_message_interpreter.verify_faststop_Z01_06_Map(res_NetworkMessage):
            tc_fail("Z01 06 P7 map in network message is not correct")

        # Fetch network message for 2nd request
        req_cmd1 = "Select NetworkMessage from networkmessages where NetworkPSPId=20 and NetworkMessage like '%TESOZ01%' and NetworkMessage like '%P711%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage1 = faststop_network_message_interpreter.fetch_networkmessage(req_cmd1)
        self.log.info(f"Z01 11 Network Message is {strNetworkMessage1}")
        
        #verify Z01-11 P7 map
        if not faststop_network_message_interpreter.verify_faststop_Z01_11_p7Map(strNetworkMessage1,total):
            tc_fail("Z01 11 P7 map in network message is not correct")
        
        return True   

    @test
    def fuelDrystockCarwash_prepay_sale(self):
        """
        Testlink Id : This will add fuel,Dry stock and car wash and Perform a prepay fuel sale with Fast Stop card.
                      After sale this will verify network message for Standard map, Z01-05 P7 map and Z01-11 P7 map 
        Args: None
        Returns: None
        """
        # Add Dry Stock item
        pos.add_item(item='Generic Item')

        # Add Car Wash Item
        pos.add_item("1234",method="plu",qualifier="CARWASH 1")

        # Add Fuel
        pos.add_fuel(self.fuel_amount, grade=self.fuel_grade)
        
        # Perform card Payment with FastStop card
        pos.pay_card(brand='FASTSTOP', card_name='Fast Stop Commercial')

        # Wait until dispenser 1 is idle
        if not pos.wait_for_disp_status('IDLE',timeout=90):
            return False
        
        balance = pos.read_balance()
        total = balance['Total']
        self.log.debug(f"total is {total}")
        
        # Create list to have product data
        prod1_list = ["004",self.fuel_amount]
        prod2_list = ["102","$2.50"]
        prod3_list = ["400","$0.01"]

        # Fetch network message for 1st request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkPSPId=20 and NetworkMessage like '%TESOZ01%' and NetworkMessage like '%P705%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 05 Network Message is {strNetworkMessage}")

        #Verify client dictionary data in network message
        if not faststop_network_message_interpreter.verify_faststop_clientDisctionaryData(strNetworkMessage,"F01"):
            tc_fail("Client Dictionary Data in network message is not correct")

        # Verify Standard Map in network message
        if not faststop_network_message_interpreter.verify_faststop_standardMap(strNetworkMessage):
            tc_fail("Standard Map in network message is not correct")
        
        #verify Z01-05 P7 map
        if not faststop_network_message_interpreter.verify_faststop_Z01_05_p7Map(strNetworkMessage,total,prod1_list,prod2_list,prod3_list):
            tc_fail("Z01 05 P7 map in network message is not correct")
        
        # Fetch Network message for 1st response
        res_cmd = "Select NetworkMessage from networkmessages where NetworkPSPId=20 and NetworkMessage like '%M0006%'order by NetworkMessageId desc"
        res_NetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(res_cmd)
        self.log.info(f"Z01 06 Network Message is {res_NetworkMessage}")
        
        #verify Z01-06 map
        if not faststop_network_message_interpreter.verify_faststop_Z01_06_Map(res_NetworkMessage):
            tc_fail("Z01 06 P7 map in network message is not correct")

        # Fetch network message for 2nd request
        req_cmd1 = "Select NetworkMessage from networkmessages where NetworkPSPId=20 and NetworkMessage like '%TESOZ01%' and NetworkMessage like '%P711%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage1 = faststop_network_message_interpreter.fetch_networkmessage(req_cmd1)
        self.log.info(f"Z01 11 Network Message is {strNetworkMessage1}")
        
        #verify Z01-11 P7 map
        if not faststop_network_message_interpreter.verify_faststop_Z01_11_p7Map(strNetworkMessage1,total):
            tc_fail("Z01 11 P7 map in network message is not correct")
        
        return True       
                
    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        pass   