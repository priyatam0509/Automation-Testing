"""
    File name: PEACOCK_3934.py
    Brand: FastStop
    Description: [PEACOCK-3934] Z01 05/11 Indoor Transaction at Growmark Site - Message map
                 and Discretionary data layout changes for Amex, VI, MC, Discover card
    Author: Asha
    Date created: 2020-5-28 17:00
    Date last modified: 
    Python Version: 3.7
"""

import logging,time
from app import Navi, pos, system, pinpad, networksim, mws
from app.framework import EDH
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from Scripts.features import faststop_network_message_interpreter 

class PEACOCK_3934():
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
        # Make approval mode of network sim as Approval
        networksim.set_response_mode("Approval")

        # Navigate to POS screen
        Navi.navigate_to("POS")
        
        # Sign on to POS screen if not already sign-on
        pos.sign_on()

    @test
    def TC1(self):
        """
        Zephyr Id : To verify Prepay completed successfully for MSD Visa card having Track2/Track1 & 
                    Track2 with B2 request map & B0 response map for Z01 05 & N0 response map for Z01 11 having 
                    Client Discretionary Data Layout E fields
        Args: None
        Returns: None
        """
        # wait for dispemser to be Ready
        if not pos.wait_disp_ready(idle_timeout=90):
            return False

        # Create a list of product data
        prod1_list = ["004", self.fuel_amount, "01000", "1000", "01"]
    
        # fetch last networkmessage id
        last_ID = self.edh.get_last_msg_id(pspid="20")

        # Add fuel in prepay mode
        pos.add_fuel(self.fuel_amount, grade=self.fuel_grade)
        
        # Perform card Payment with Visa MSD Card
        pos.pay_card()
        
        # Wait until dispenser 1 is idle
        if not pos.wait_for_disp_status('IDLE'):
            return False

        #Verifying details from receipt
        if not pos.check_receipt_for(["8021","Visa"]):
           tc_fail("details not matched with receipt")

        # wait for network message
        if not faststop_network_message_interpreter.wait_for_network_message(last_id=last_ID, request_map="11"):
            tc_fail("Required Network message did not come")

        # Fetch network message for Z01 05 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________5%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 05 Network Message is {strNetworkMessage}")
        
        # verify Z01 05 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'05','B0','B2'):
            tc_fail("Z01 05 Standardmap map in network Mesage is not correct")

        # verify Z01_05 DDLE map
        if not faststop_network_message_interpreter.verify_ClientDictionaryData_Z01_DDL(strNetworkMessage,'E',prod1_list):
            tc_fail("Z01_05 DDLE map in network Mesage is not correct")

        # Fetch network message for Z01 11 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________11%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 11 Network Message is {strNetworkMessage}")
        
        # verify Z01 11 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'11','N0','B2'):
            tc_fail("Z01 11 Standardmap map in network Mesage is not correct")

        # verify Z01_11 DDLE map
        if not faststop_network_message_interpreter.verify_ClientDictionaryData_Z01_DDL(strNetworkMessage,'E',prod1_list):
            tc_fail("Z01_11 DDLE map in network Mesage is not correct")

        return True

    @test
    def TC2(self):
        """
        Zephyr Id : To verify Prepay & 1 dry stock item transactions is completed successfully for 
                    MSD Mastercard having Track2/Track1 & Track2 with B2 request map & B0 response map for 
                    Z01 05 & N0 response map for Z01 11 having Client Discretionary Data Layout E fields
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
        
        # add item with plu 1
        pos.add_item("1", method="PLU")

        # Perform card Payment with MSD MasterCard 
        pos.pay_card(card_name="MasterCard")
        
        # Wait until dispenser 1 is idle
        if not pos.wait_for_disp_status('IDLE'):
            return False

        # Verifying details from receipt
        if not pos.check_receipt_for(["0008","MasterCard"]):
           tc_fail("details not matched with receipt")

        # wait for network message
        if not faststop_network_message_interpreter.wait_for_network_message(last_id=last_ID, request_map="11"):
            tc_fail("Required Network message did not come")

        # Fetch network message for Z01 05 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________5%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 05 Network Message is {strNetworkMessage}")
        
        # verify Z01 05 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'05','B0','B2'):
            tc_fail("Z01 05 Standardmap map in network Mesage is not correct")

        # verify Z01_05 DDLE map
        if not faststop_network_message_interpreter.verify_ClientDictionaryData_Z01_DDL(strNetworkMessage,'E',prod1_list,prod2_list):
            tc_fail("Z01_05 DDLE map in network Mesage is not correct")

        # Fetch network message for Z01 11 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________11%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 11 Network Message is {strNetworkMessage}")
        
        # verify Z01 11 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'11','N0','B2'):
            tc_fail("Z01 11 Standardmap map in network Mesage is not correct")

        # verify Z01_11 DDLE map
        if not faststop_network_message_interpreter.verify_ClientDictionaryData_Z01_DDL(strNetworkMessage,'E',prod1_list,prod2_list):
            tc_fail("Z01_11 DDLE map in network Mesage is not correct")

        return True

    @test
    def TC3(self):
        """
        Zephyr Id : To verify Prepay completed successfully for MSD Discover card having Track1 
                    with B2 request map & B0 response map for Z01 05 & N0 response map for Z01 11 having Client
                    Discretionary Data Layout E fields
        Args: None
        Returns: None
        """

        # Create a list of product data
        prod1_list = ["004", self.fuel_amount, "01000", "1000", "01"]

        # fetch last networkmessage id
        last_ID = self.edh.get_last_msg_id(pspid="20")
    
        # Add fuel in prepay mode
        pos.add_fuel(self.fuel_amount, grade=self.fuel_grade)
        
        # Perform card Payment with Discover MSD Card
        pos.pay_card(card_name="Discover")
        
        # Wait until dispenser 1 is idle
        if not pos.wait_for_disp_status('IDLE'):
            return False

        #Verifying details from receipt
        if not pos.check_receipt_for(["0007","Discover"]):
           tc_fail("details not matched with receipt")

        # wait for network message
        if not faststop_network_message_interpreter.wait_for_network_message(last_id=last_ID, request_map="11"):
            tc_fail("Required Network message did not come")

        # Fetch network message for Z01 05 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________5%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 05 Network Message is {strNetworkMessage}")
        
        #verify Z01 05 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'05','B0','B2'):
            tc_fail("Z01 05 Standardmap map in network Mesage is not correct")

        #verify Z01_05 DDLE map
        if not faststop_network_message_interpreter.verify_ClientDictionaryData_Z01_DDL(strNetworkMessage,'E',prod1_list):
            tc_fail("Z01_05 DDLE map in network Mesage is not correct")

        # Fetch network message for Z01 11 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________11%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 11 Network Message is {strNetworkMessage}")
        
        #verify Z01 11 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'11','N0','B2'):
            tc_fail("Z01 11 Standardmap map in network Mesage is not correct")

        #verify Z01_11 DDLE map
        if not faststop_network_message_interpreter.verify_ClientDictionaryData_Z01_DDL(strNetworkMessage,'E',prod1_list):
            tc_fail("Z01_11 DDLE map in network Mesage is not correct")

        return True

    @test
    def TC4(self):
        """
        Zephyr Id : To verify Prepay & 1 dry stock item transactions is completed successfully for MSD Amex
                    card having Track1 with B2 request map & B0 response map for Z01 05 & N0 response map for Z01 11 
                    having Client Discretionary Data Layout E fields
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

        # Perform card Payment with MSD Amex card 
        pos.pay_card(card_name="AmEx")
        
        # Wait until dispenser 1 is idle
        if not pos.wait_for_disp_status('IDLE'):
            return False

        #Verifying details from receipt
        if not pos.check_receipt_for(["9509","American Express"]):
           tc_fail("details not matched with receipt")

        # wait for network message
        if not faststop_network_message_interpreter.wait_for_network_message(last_id=last_ID, request_map="11"):
            tc_fail("Required Network message did not come")

        # Fetch network message for Z01 05 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________5%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 05 Network Message is {strNetworkMessage}")
        
        #verify Z01 05 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'05','B0','B2'):
            tc_fail("Z01 05 Standardmap map in network Mesage is not correct")

        #verify Z01_05 DDLE map
        if not faststop_network_message_interpreter.verify_ClientDictionaryData_Z01_DDL(strNetworkMessage,'E',prod1_list,prod2_list):
            tc_fail("Z01_05 DDLE map in network Mesage is not correct")

        # Fetch network message for Z01 11 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________11%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 11 Network Message is {strNetworkMessage}")
        
        #verify Z01 11 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'11','N0','B2'):
            tc_fail("Z01 11 Standardmap map in network Mesage is not correct")

        #verify Z01_11 DDLE map
        if not faststop_network_message_interpreter.verify_ClientDictionaryData_Z01_DDL(strNetworkMessage,'E',prod1_list,prod2_list):
            tc_fail("Z01_11 DDLE map in network Mesage is not correct")

        return True

    @test
    def TC5(self):
        """
        Zephyr Id : To verify Prepay completed successfully for MSD Visa card by manual card entry having
                    Track2/Track1 & Track2 with B2 request map & B0 response map for Z01 05 & N0 response map for 
                    Z01 11 having Client Discretionary Data Layout E fields
        Args: None
        Returns: None
        """

        # Create a list of product data
        prod1_list = ["004", self.fuel_amount, "01000", "1000", "01"]

        # fetch last networkmessage id
        last_ID = self.edh.get_last_msg_id(pspid="20")
    
        # Add fuel in prepay mode
        pos.add_fuel(self.fuel_amount, grade=self.fuel_grade)
        
        # Perform manual card Payment with Visa MSD Card details
        pos.manual_entry(brand="Faststop", card_name="Visa", expiration_date="1230")
        
        # Wait until dispenser 1 is idle
        if not pos.wait_for_disp_status('IDLE'):
            return False

        #Verifying details from receipt
        if not pos.check_receipt_for(["8021","Visa"]):
           tc_fail("details not matched with receipt")

        # wait for network message
        if not faststop_network_message_interpreter.wait_for_network_message(last_id=last_ID, request_map="11"):
            tc_fail("Required Network message did not come")

        # Fetch network message for Z01 05 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________5%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 05 Network Message is {strNetworkMessage}")
        
        #verify Z01 05 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'05','B0','B2'):
            tc_fail("Z01 05 Standardmap map in network Mesage is not correct")

        #verify Z01_05 DDLE map
        if not faststop_network_message_interpreter.verify_ClientDictionaryData_Z01_DDL(strNetworkMessage,'E',prod1_list):
            tc_fail("Z01_05 DDLE map in network Mesage is not correct")

        # Fetch network message for Z01 11 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________11%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 11 Network Message is {strNetworkMessage}")
        
        #verify Z01 11 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'11','N0','B2'):
            tc_fail("Z01 11 Standardmap map in network Mesage is not correct")

        #verify Z01_11 DDLE map
        if not faststop_network_message_interpreter.verify_ClientDictionaryData_Z01_DDL(strNetworkMessage,'E',prod1_list):
            tc_fail("Z01_11 DDLE map in network Mesage is not correct")

        return True

    @test
    def TC7(self):
        """
        Zephyr Id : To verify Prepay completed successfully for EMV Discover card having Track2 with B2 
                    request map & B0 response map for Z01 05 & N0 response map for Z01 11 having Client Discretionary
                    Data Layout E fields
        Args: None
        Returns: None
        """

        # Create a list of product data
        prod1_list = ["004", self.fuel_amount, "01000", "1000", "01"]

        # fetch last networkmessage id
        last_ID = self.edh.get_last_msg_id(pspid="20")
        
        # Add fuel in prepay mode
        pos.add_fuel(self.fuel_amount, grade=self.fuel_grade)
        
        # Perform card Payment with EMV Discover Card
        pos.pay_card(brand="FASTSTOP",card_name="EMVDiscoverUSDebit")
                
        # Wait until dispenser 1 is idle
        if not pos.wait_for_disp_status('IDLE'):
            return False

        #Verifying details from receipt
        if not pos.check_receipt_for(["0216","Discover","A0000001523010"]):
           tc_fail("details not matched with receipt")

        # wait for network message
        if not faststop_network_message_interpreter.wait_for_network_message(last_id=last_ID, request_map="11"):
            tc_fail("Required Network message did not come")

        # Fetch network message for Z01 05 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________5%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 05 Network Message is {strNetworkMessage}")
        
        #verify Z01 05 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'05','B0','B2'):
            tc_fail("Z01 05 Standardmap map in network Mesage is not correct")

        #verify Z01_05 DDLE map
        if not faststop_network_message_interpreter.verify_ClientDictionaryData_Z01_DDL(strNetworkMessage,'E',prod1_list):
            tc_fail("Z01_05 DDLE map in network Mesage is not correct")

        # Fetch network message for Z01 11 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________11%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 11 Network Message is {strNetworkMessage}")
        
        #verify Z01 11 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'11','N0','B2'):
            tc_fail("Z01 11 Standardmap map in network Mesage is not correct")

        #verify Z01_11 DDLE map
        if not faststop_network_message_interpreter.verify_ClientDictionaryData_Z01_DDL(strNetworkMessage,'E',prod1_list):
            tc_fail("Z01_11 DDLE map in network Mesage is not correct")

        return True

    @test
    def TC6(self):
        """
        Zephyr Id : To verify Prepay & 1 dry stock item transactions is completed successfully for MSD 
                    Mastercard having Track2/Track1 & Track2 by manual card entry with B2 request map & B0 response map 
                    for Z01 05 & N0 response map for Z01 11 having Client Discretionary Data Layout E fields
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

        # Perform manual card Payment with MasterCard MSD Card details
        pos.manual_entry(brand="Faststop",card_name="MasterCard",expiration_date="1230")
        
        # Wait until dispenser 1 is idle
        if not pos.wait_for_disp_status('IDLE'):
            return False

        #Verifying details from receipt
        if not pos.check_receipt_for(["0008","MasterCard"]):
           tc_fail("details not matched with receipt")

        # wait for network message
        if not faststop_network_message_interpreter.wait_for_network_message(last_id=last_ID, request_map="11"):
            tc_fail("Required Network message did not come")

        # Fetch network message for Z01 05 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________5%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 05 Network Message is {strNetworkMessage}")
        
        #verify Z01 05 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'05','B0','B2'):
            tc_fail("Z01 05 Standardmap map in network Mesage is not correct")

        #verify Z01_05 DDLE map
        if not faststop_network_message_interpreter.verify_ClientDictionaryData_Z01_DDL(strNetworkMessage,'E',prod1_list,prod2_list):
            tc_fail("Z01_05 DDLE map in network Mesage is not correct")

        # Fetch network message for Z01 11 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________11%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 11 Network Message is {strNetworkMessage}")
        
        #verify Z01 11 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'11','N0','B2'):
            tc_fail("Z01 11 Standardmap map in network Mesage is not correct")

        #verify Z01_11 DDLE map
        if not faststop_network_message_interpreter.verify_ClientDictionaryData_Z01_DDL(strNetworkMessage,'E',prod1_list,prod2_list):
            tc_fail("Z01_11 DDLE map in network Mesage is not correct")

        return True

    @test
    def TC8(self):
        """
        Zephyr Id : To verify Prepay & 1 dry stock item transactions is completed successfully for EMV Amex 
                    card having Track2 with B2 request map & B0 response map for Z01 05 & N0 response map for
                    Z01 11 having Client Discretionary Data Layout E fields
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

        # Perform card Payment with EMV Amex
        pos.pay_card(card_name="EMVAmEx")
                
        # Wait until dispenser 1 is idle
        if not pos.wait_for_disp_status('IDLE'):
            return False

        #Verifying details from receipt
        if not pos.check_receipt_for(["9509","American Express","A00000002501"]):
           tc_fail("details not matched with receipt")

        # wait for network message
        if not faststop_network_message_interpreter.wait_for_network_message(last_id=last_ID, request_map="11"):
            tc_fail("Required Network message did not come")

        # Fetch network message for Z01 05 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________5%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 05 Network Message is {strNetworkMessage}")
        
        #verify Z01 05 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'05','B0','B2'):
            tc_fail("Z01 05 Standardmap map in network Mesage is not correct")

        #verify Z01_05 DDLE map
        if not faststop_network_message_interpreter.verify_ClientDictionaryData_Z01_DDL(strNetworkMessage,'E',prod1_list,prod2_list):
            tc_fail("Z01_05 DDLE map in network Mesage is not correct")

        # Fetch network message for Z01 11 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________11%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 11 Network Message is {strNetworkMessage}")
        
        #verify Z01 11 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'11','N0','B2'):
            tc_fail("Z01 11 Standardmap map in network Mesage is not correct")

        #verify Z01_11 DDLE map
        if not faststop_network_message_interpreter.verify_ClientDictionaryData_Z01_DDL(strNetworkMessage,'E',prod1_list,prod2_list):
            tc_fail("Z01_11 DDLE map in network Mesage is not correct")

        return True

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        # close pos instance
        pos.close()