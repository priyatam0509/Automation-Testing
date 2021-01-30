"""
    File name: PEACOCK_3989.py
    Brand: FastStop
    Description: [PEACOCK-3989] Z01 05/11 Indoor Transaction at Growmark Site - Message map
                 and Discretionary data layout changes for MC/VI Purchase card
    Author: Asha
    Date created: 2020-6-4 12:00
    Date last modified: 
    Python Version: 3.7
"""

import logging,time
from app import pos, system
from app.framework import EDH
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from Scripts.features import faststop_network_message_interpreter 

class PEACOCK_3989():
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

        # Create object of EDH
        self.edh = EDH.EDH()

        # Parameters to be used in sale
        self.item_amount = "$0.01"
        self.fuel_amount = "$1.00"
        self.fuel_grade = "Diesel 1"
        
    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        # Navigate to POS screen
        pos.connect()

    @test
    def TC1(self):
        """
        Zephyr Id : To verify Prepay completed successfully for MSD Visa Purchase card having Track2/Track1 
                    & Track2 with P0 request map & N0 response map having Client Discretionary Data Layout D fields
        Args: None
        Returns: None
        """

        # Create a list of product data
        prod1_list = ["004", self.fuel_amount, "01000", "1000", "01"]

        # fetch last networkmessage id
        last_ID = self.edh.get_last_msg_id(pspid="20")
    
        # Add fuel in prepay mode
        pos.add_fuel(self.fuel_amount, grade=self.fuel_grade)
        
        # Perform card Payment with Visa MSD Card
        pos.pay_card(card_name="VisaPurchase")
        
        # Wait until dispenser 1 is idle
        if not pos.wait_for_disp_status('IDLE'):
            return False

        #Verifying details from receipt
        if not pos.check_receipt_for(["8889","Visa"]):
           tc_fail("details not matched with receipt")

        # wait for network message
        if not faststop_network_message_interpreter.wait_for_network_message(last_id=last_ID, request_map="11"):
            tc_fail("Required Network message did not come")

        # Fetch network message for Z01 05 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________5%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 05 Network Message is {strNetworkMessage}")
        
        #verify Z01 05 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'05','N0','P0'):
            tc_fail("Z01 05 Standardmap map in network Mesage is not correct")

        #verify Z01_05 DDLE map
        if not faststop_network_message_interpreter.verify_ClientDictionaryData_Z01_DDL(strNetworkMessage,'D',prod1_list):
            tc_fail("Z01_05 DDLD map in network Mesage is not correct")

        # Fetch network message for Z01 11 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________11%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 11 Network Message is {strNetworkMessage}")
        
        #verify Z01 11 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'11','N0','P0'):
            tc_fail("Z01 11 Standardmap map in network Mesage is not correct")

        #verify Z01_11 DDLE map
        if not faststop_network_message_interpreter.verify_ClientDictionaryData_Z01_DDL(strNetworkMessage,'D',prod1_list):
            tc_fail("Z01_11 DDLD map in network Mesage is not correct")

        return True

    @test
    def TC2(self):
        """
        Zephyr Id : To verify Prepay & 1 dry stock item transactions is completed successfully for MSD 
                    Mastercard Purchase having Track2/Track1 & Track2 with P0 request map & N0 response map 
                    having Client Discretionary Data Layout D fields
        Args: None
        Returns: None
        """

        # Create a list of product data
        prod1_list = ["004", self.fuel_amount, "01000", "1000", "01"]
    
        prod2_list = ["400", "1000", self.item_amount]

        # fetch last networkmessage id
        last_ID = self.edh.get_last_msg_id(pspid="20")
        
        # Add fuel in prepay mode
        pos.add_fuel(self.fuel_amount, grade=self.fuel_grade)
        
        #add item with plu 1
        pos.add_item("1", method="PLU")

        # Perform card Payment with MSD MasterCard Purchase
        pos.pay_card(card_name="MCPurchase")
        
        # Wait until dispenser 1 is idle
        if not pos.wait_for_disp_status('IDLE'):
            return False

        #Verifying details from receipt
        if not pos.check_receipt_for(["0003","MasterCard"]):
           tc_fail("details not matched with receipt")

        # wait for network message
        if not faststop_network_message_interpreter.wait_for_network_message(last_id=last_ID, request_map="11"):
            tc_fail("Required Network message did not come")

        # Fetch network message for Z01 05 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________5%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 05 Network Message is {strNetworkMessage}")
        
        #verify Z01 05 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'05','N0','P0'):
            tc_fail("Z01 05 Standardmap map in network Mesage is not correct")

        #verify Z01_05 DDLE map
        if not faststop_network_message_interpreter.verify_ClientDictionaryData_Z01_DDL(strNetworkMessage,'D',prod1_list,prod2_list):
            tc_fail("Z01_05 DDLD map in network Mesage is not correct")

        # Fetch network message for Z01 11 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________11%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 11 Network Message is {strNetworkMessage}")
        
        #verify Z01 11 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'11','N0','P0'):
            tc_fail("Z01 11 Standardmap map in network Mesage is not correct")

        #verify Z01_11 DDLE map
        if not faststop_network_message_interpreter.verify_ClientDictionaryData_Z01_DDL(strNetworkMessage,'D',prod1_list,prod2_list):
            tc_fail("Z01_11 DDLD map in network Mesage is not correct")

        return True

    @test
    def TC3(self):
        """
        Zephyr Id : To verify Prepay completed successfully for MSD Visa Purchase card having Track1 with 
                    P2 request map & N0 response map having Client Discretionary Data Layout D fields
        Args: None
        Returns: None
        """

        # Create a list of product data
        prod1_list = ["004", self.fuel_amount, "01000", "1000", "01"]

        # fetch last networkmessage id
        last_ID = self.edh.get_last_msg_id(pspid="20")
    
        # Add fuel in prepay mode
        pos.add_fuel(self.fuel_amount, grade=self.fuel_grade)
        
        # Perform card Payment with MSD Visa Purchase with Track1 only
        pos.pay_card(card_name="VisaPurchaseTrack1")
        
        # Wait until dispenser 1 is idle
        if not pos.wait_for_disp_status('IDLE'):
            return False

        #Verifying details from receipt
        if not pos.check_receipt_for(["8889","Visa"]):
           tc_fail("details not matched with receipt")

        # wait for network message
        if not faststop_network_message_interpreter.wait_for_network_message(last_id=last_ID, request_map="11"):
            tc_fail("Required Network message did not come")

        # Fetch network message for Z01 05 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________5%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 05 Network Message is {strNetworkMessage}")
        
        #verify Z01 05 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'05','N0','P2'):
            tc_fail("Z01 05 Standardmap map in network Mesage is not correct")

        #verify Z01_05 DDLE map
        if not faststop_network_message_interpreter.verify_ClientDictionaryData_Z01_DDL(strNetworkMessage,'D',prod1_list):
            tc_fail("Z01_05 DDLD map in network Mesage is not correct")

        # Fetch network message for Z01 11 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________11%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 11 Network Message is {strNetworkMessage}")
        
        #verify Z01 11 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'11','N0','P2'):
            tc_fail("Z01 11 Standardmap map in network Mesage is not correct")

        #verify Z01_11 DDLE map
        if not faststop_network_message_interpreter.verify_ClientDictionaryData_Z01_DDL(strNetworkMessage,'D',prod1_list):
            tc_fail("Z01_11 DDLD map in network Mesage is not correct")

        return True

    @test
    def TC5(self):
        """
        Zephyr Id : To verify Prepay completed successfully for MSD Visa Purchase card by manual card 
                    entry having Track2/Track1 & Track2 with P0 request map & N0 response map having Client 
                    Discretionary Data Layout D fields
        Args: None
        Returns: None
        """

        # Create a list of product data
        prod1_list = ["004", self.fuel_amount, "01000", "1000", "01"]

        # fetch last networkmessage id
        last_ID = self.edh.get_last_msg_id(pspid="20")
    
        # Add fuel in prepay mode
        pos.add_fuel(self.fuel_amount, grade=self.fuel_grade)
        
        # Perform manual card Payment with Visa MSD Purchase Card details
        pos.manual_entry(brand="Faststop",card_name="VisaPurchase")
        
        # Wait until dispenser 1 is idle
        if not pos.wait_for_disp_status('IDLE'):
            return False

        #Verifying details from receipt
        if not pos.check_receipt_for(["8889","Visa"]):
           tc_fail("details not matched with receipt")

        # wait for network message
        if not faststop_network_message_interpreter.wait_for_network_message(last_id=last_ID, request_map="11"):
            tc_fail("Required Network message did not come")

        # Fetch network message for Z01 05 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________5%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 05 Network Message is {strNetworkMessage}")
        
        #verify Z01 05 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'05','N0','P0'):
            tc_fail("Z01 05 Standardmap map in network Mesage is not correct")

        #verify Z01_05 DDLE map
        if not faststop_network_message_interpreter.verify_ClientDictionaryData_Z01_DDL(strNetworkMessage,'D',prod1_list):
            tc_fail("Z01_05 DDLD map in network Mesage is not correct")

        # Fetch network message for Z01 11 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________11%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 11 Network Message is {strNetworkMessage}")
        
        #verify Z01 11 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'11','N0','P0'):
            tc_fail("Z01 11 Standardmap map in network Mesage is not correct")

        #verify Z01_11 DDLE map
        if not faststop_network_message_interpreter.verify_ClientDictionaryData_Z01_DDL(strNetworkMessage,'D',prod1_list):
            tc_fail("Z01_11 DDLD map in network Mesage is not correct")

        return True

    @test
    def TC4(self):
        """
        Zephyr Id : To verify Prepay & 1 dry stock item transactions is completed successfully for MSD 
                    Mastercard Purchase having Track1 with P2 request map & N0 response map having Client 
                    Discretionary Data Layout D fields
        Args: None
        Returns: None
        """

        # Create a list of product data
        prod1_list = ["004", self.fuel_amount, "01000", "1000", "01"]
    
        prod2_list = ["400", "1000", self.item_amount]

        # fetch last networkmessage id
        last_ID = self.edh.get_last_msg_id(pspid="20")
        
        # Add fuel in prepay mode
        pos.add_fuel(self.fuel_amount, grade=self.fuel_grade)
        
        #add item with plu 1
        pos.add_item("1", method="PLU")

        # Perform card Payment with MSD MasterCard Purchase with Track1 only
        pos.pay_card(card_name="MCPurchaseTrack1")
        
        # Wait until dispenser 1 is idle
        if not pos.wait_for_disp_status('IDLE'):
            return False

        #Verifying details from receipt
        if not pos.check_receipt_for(["0003","MasterCard"]):
           tc_fail("details not matched with receipt")

        # wait for network message
        if not faststop_network_message_interpreter.wait_for_network_message(last_id=last_ID, request_map="11"):
            tc_fail("Required Network message did not come")

        # Fetch network message for Z01 05 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________5%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 05 Network Message is {strNetworkMessage}")
        
        #verify Z01 05 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'05','N0','P2'):
            tc_fail("Z01 05 Standardmap map in network Mesage is not correct")

        #verify Z01_05 DDLE map
        if not faststop_network_message_interpreter.verify_ClientDictionaryData_Z01_DDL(strNetworkMessage,'D',prod1_list,prod2_list):
            tc_fail("Z01_05 DDLD map in network Mesage is not correct")

        # Fetch network message for Z01 11 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________11%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 11 Network Message is {strNetworkMessage}")
        
        #verify Z01 11 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'11','N0','P2'):
            tc_fail("Z01 11 Standardmap map in network Mesage is not correct")

        #verify Z01_11 DDLE map
        if not faststop_network_message_interpreter.verify_ClientDictionaryData_Z01_DDL(strNetworkMessage,'D',prod1_list,prod2_list):
            tc_fail("Z01_11 DDLD map in network Mesage is not correct")

        return True
    
    @test
    def TC6(self):
        """
        Zephyr Id : To verify Prepay & 1 dry stock item transactions is completed successfully for MSD Mastercard 
                    Purchase having Track1 by manual card entry with P0 request map & N0 response map having Client 
                    Discretionary Data Layout D fields
        Args: None
        Returns: None
        """

        # Create a list of product data
        prod1_list = ["004", self.fuel_amount, "01000", "1000", "01"]
        
        prod2_list = ["400", "1000", self.item_amount]

        # fetch last networkmessage id
        last_ID = self.edh.get_last_msg_id(pspid="20")

        # Add fuel in prepay mode
        pos.add_fuel(self.fuel_amount, grade=self.fuel_grade)
        
        #add item with plu 1
        pos.add_item("1", method="PLU")

        # Perform manual card Payment with Visa MSD Purchase Card details
        pos.manual_entry(brand="Faststop",card_name="MasterCardPurchase")
        
        # Wait until dispenser 1 is idle
        if not pos.wait_for_disp_status('IDLE'):
            return False

        #Verifying details from receipt
        if not pos.check_receipt_for(["0003","MasterCard"]):
           tc_fail("details not matched with receipt")

        # wait for network message
        if not faststop_network_message_interpreter.wait_for_network_message(last_id=last_ID, request_map="11"):
            tc_fail("Required Network message did not come")

        # Fetch network message for Z01 05 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________5%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 05 Network Message is {strNetworkMessage}")
        
        #verify Z01 05 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'05','N0','P0'):
            tc_fail("Z01 05 Standardmap map in network Mesage is not correct")

        #verify Z01_05 DDLE map
        if not faststop_network_message_interpreter.verify_ClientDictionaryData_Z01_DDL(strNetworkMessage,'D',prod1_list,prod2_list):
            tc_fail("Z01_05 DDLD map in network Mesage is not correct")

        # Fetch network message for Z01 11 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________11%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 11 Network Message is {strNetworkMessage}")
        
        #verify Z01 11 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'11','N0','P0'):
            tc_fail("Z01 11 Standardmap map in network Mesage is not correct")

        #verify Z01_11 DDLE map
        if not faststop_network_message_interpreter.verify_ClientDictionaryData_Z01_DDL(strNetworkMessage,'D',prod1_list,prod2_list):
            tc_fail("Z01_11 DDLD map in network Mesage is not correct")

        return True

    
    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        # Close pos instance
        pos.close()