"""
    File name: PEACOCK_3988.py
    Brand: FastStop
    Description: [PEACOCK-3988] Z01 13 - Indoor Transaction at Growmark Site - Message map 
                 and Discretionary data layout changes for MC/VI Purchase card
    Author: Asha
    Date created: 2020-5-27 15:30
    Date last modified: 
    Python Version: 3.7
"""

import logging,time
from app import pos, pinpad, system, networksim
from app.framework import EDH
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from Scripts.features import faststop_network_message_interpreter

class PEACOCK_3988():
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
    def TC5(self):
        """
        Testlink Id : To verify manual fuel sale & 1 dry stock item transactions is completed successfully 
                      for MSD Visa Purchase Card having Track1 by manual card entry with P0 request map & N0 Response Map
                      having Client Discretionary Data Layout D fields
        Args: None
        Returns: None
        """
        # Create a list of product data
        prod1_list = ["004", self.fuel_amount, "01000", "1000", "01"]
    
        prod2_list = ["400", "1000", self.item_amount]

        # fetch last networkmessage id
        last_ID = self.edh.get_last_msg_id(pspid="20")

        # Add fuel in manual mode
        pos.add_fuel(self.fuel_amount, mode="manual", grade=self.fuel_grade)
        
        #add item with plu 1
        pos.add_item("1", method="PLU")

        # Perform manual card Payment with MSD Visa Purchase
        pos.manual_entry(brand="Faststop",card_name="VisaPurchase")

        # Verifying details from receipt
        if not pos.check_receipt_for("Visa"):
           tc_fail("details not matched with receipt")

        # wait for network message
        if not faststop_network_message_interpreter.wait_for_network_message(last_id=last_ID, request_map="13"):
            tc_fail("Required Network message did not come")

        # Fetch network message for Z01 13 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________13%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 13 Network Message is {strNetworkMessage}")
        
        # verify Z01 13 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'13','N0','P0'):
            tc_fail("Z01 13 Standardmap map in network Mesage is not correct")

        # verify Z01_13 DDLD map
        if not faststop_network_message_interpreter.verify_ClientDictionaryData_Z01_DDL(strNetworkMessage,'D',prod1_list,prod2_list):
            tc_fail("Z01_13 DDLD map in network Mesage is not correct")
      
        return True

    @test
    def TC1(self):
        """
        Testlink Id : To verify 1 postpay transactions is completed successfully for MSD Visa Purchase Card having
                      Track2/Track1 & Track2 with P0 request map & N0 Response Map 
                      having Client Discretionary Data Layout D fields
        Args: None
        Returns: None
        """

        # Create a list of product data
        prod1_list = ["004", self.fuel_amount, "01000", "1000", "01"]

        # fetch last networkmessage id
        last_ID = self.edh.get_last_msg_id(pspid="20")
    
        # Add fuel in preset mode
        pos.add_fuel(self.fuel_amount, mode="preset", grade=self.fuel_grade)
        
        # Check if fueling is completed
        if not pos.wait_for_disp_status("IDLE",timeout=90):
            return False

        # Take fuel inside POS
        pos.click_fuel_buffer("A")
 
        # Perform card Payment with MSD Visa Purchase
        pos.pay_card(card_name="VisaPurchase")

        # Verifying details from receipt
        if not pos.check_receipt_for("Visa"):
           tc_fail("details not matched with receipt")

        # wait for network message
        if not faststop_network_message_interpreter.wait_for_network_message(last_id=last_ID, request_map="13"):
            tc_fail("Required Network message did not come")

        # Fetch network message for Z01 13 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________13%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 13 Network Message is {strNetworkMessage}")
        
        # verify Z01 13 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'13','N0','P0'):
            tc_fail("Z01 13 Standardmap map in network Mesage is not correct")

        # verify Z01_13 DDLD map
        if not faststop_network_message_interpreter.verify_ClientDictionaryData_Z01_DDL(strNetworkMessage,'D',prod1_list):
            tc_fail("Z01_13 DDLD map in network Mesage is not correct")
      
        return True

    @test
    def TC6(self):
        """
        Testlink Id : To verify 1 dry stock item transactions is completed successfully for MSD Mastercard 
                      Purchase having Track1 by manual card entry with P0 request map & N0 Response Map having Client 
                      Discretionary Data Layout D fields
        Args: None
        Returns: None
        """
        # Create a list of product data
        prod1_list = ["000", "$0.00", "00000", "0000", "00"]
    
        prod2_list = ["400", "1000", self.item_amount]

        # fetch last networkmessage id
        last_ID = self.edh.get_last_msg_id(pspid="20")
        
        # add item with plu 1
        pos.add_item("1", method="PLU")

        # Perform manual card Payment with MSD MasterCard Purchase
        pos.manual_entry(brand="Faststop",card_name="MasterCardPurchase")

        # Verifying details from receipt
        if not pos.check_receipt_for("MasterCard"):
           tc_fail("details not matched with receipt")

        # wait for network message
        if not faststop_network_message_interpreter.wait_for_network_message(last_id=last_ID, request_map="13"):
            tc_fail("Required Network message did not come")

        # Fetch network message for Z01 13 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________13%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 13 Network Message is {strNetworkMessage}")
        
        # verify Z01 13 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'13','N0','P0'):
            tc_fail("Z01 13 Standardmap map in network Mesage is not correct")

        # verify Z01_13 DDLD map
        if not faststop_network_message_interpreter.verify_ClientDictionaryData_Z01_DDL(strNetworkMessage,'D',prod1_list,prod2_list):
            tc_fail("Z01_13 DDLD map in network Mesage is not correct")
      
        return True

    
    @test
    def TC2(self):
        """
        Testlink Id : To verify 1 postpay & 1 dry stock item transactions is completed successfully for MSD 
                      Mastercard Purchase having Track2/Track1 & Track2 with P0 request map & N0 Response Map having Client
                      Discretionary Data Layout D fields
        Args: None
        Returns: None
        """
        # Create a list of product data
        prod1_list = ["004", self.fuel_amount, "01000", "1000", "01"]
    
        prod2_list = ["400", "1000", self.item_amount]

        # fetch last networkmessage id
        last_ID = self.edh.get_last_msg_id(pspid="20")

        # Add fuel in preset mode
        pos.add_fuel(self.fuel_amount, mode="preset", grade=self.fuel_grade)
        
        # Check if fueling is completed
        if not pos.wait_for_disp_status("IDLE",timeout=90):
            return False

        # Take fuel inside POS
        pos.click_fuel_buffer("A")
        
        # add item with plu 1
        pos.add_item("1", method="PLU")

        # Perform card Payment with MSD MasterCard Purchase
        pos.pay_card(card_name="MCPurchase")

        # Verifying details from receipt
        if not pos.check_receipt_for("MasterCard"):
           tc_fail("details not matched with receipt")

        # wait for network message
        if not faststop_network_message_interpreter.wait_for_network_message(last_id=last_ID, request_map="13"):
            tc_fail("Required Network message did not come")

        # Fetch network message for Z01 13 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________13%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 13 Network Message is {strNetworkMessage}")
        
        # verify Z01 13 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'13','N0','P0'):
            tc_fail("Z01 13 Standardmap map in network Mesage is not correct")

        # verify Z01_13 DDLD map
        if not faststop_network_message_interpreter.verify_ClientDictionaryData_Z01_DDL(strNetworkMessage,'D',prod1_list,prod2_list):
            tc_fail("Z01_13 DDLD map in network Mesage is not correct")
      
        return True

    @test
    def TC3(self):
        """
        Testlink Id : To verify manual fuel sale & 1 dry stock item transactions is completed successfully 
                      for MSD Visa Purchase Card having Track1 with P2 request map & N0 Response Map having 
                      Client Discretionary Data Layout D fields
        Args: None
        Returns: None
        """

        # Create a list of product data
        prod1_list = ["004", self.fuel_amount, "01000", "1000", "01"]
    
        prod2_list = ["400", "1000", self.item_amount]

        # fetch last networkmessage id
        last_ID = self.edh.get_last_msg_id(pspid="20")

        # Add fuel in manual mode
        pos.add_fuel(self.fuel_amount, mode="manual", grade=self.fuel_grade)
        
        # add item with plu 1
        pos.add_item("1", method="PLU")

        # Perform card Payment with MSD Visa Purchase with Track1 only
        pos.pay_card(card_name="VisaPurchaseTrack1")

        #Verifying details from receipt
        if not pos.check_receipt_for("Visa"):
           tc_fail("details not matched with receipt")

        # wait for network message
        if not faststop_network_message_interpreter.wait_for_network_message(last_id=last_ID, request_map="13"):
            tc_fail("Required Network message did not come")

        # Fetch network message for Z01 13 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________13%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 13 Network Message is {strNetworkMessage}")
        
        # verify Z01 13 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'13','N0','P2'):
            tc_fail("Z01 13 Standardmap map in network Mesage is not correct")

        # verify Z01_13 DDLD map
        if not faststop_network_message_interpreter.verify_ClientDictionaryData_Z01_DDL(strNetworkMessage,'D',prod1_list,prod2_list):
            tc_fail("Z01_13 DDLD map in network Mesage is not correct")
      
        return True

    @test
    def TC4(self):
        """
        Testlink Id : To verify 1 dry stock item transactions is completed successfully for MSD Mastercard 
                      Purchase Card having Track1 with P2 request map & N0 Response Map having Client Discretionary
                      Data Layout D fields
        Args: None
        Returns: None
        """

        # Create a list of product data
        prod1_list = ["000", "$0.00", "00000", "0000", "00"]
    
        prod2_list = ["400", "1000", self.item_amount]

        # fetch last networkmessage id
        last_ID = self.edh.get_last_msg_id(pspid="20")
        
        #add item with plu 1
        pos.add_item("1", method="PLU")

        # Perform card Payment with MSD MasterCard Purchase with Track1 only
        pos.pay_card(card_name="MCPurchaseTrack1")

        # Verifying details from receipt
        if not pos.check_receipt_for("MasterCard"):
           tc_fail("details not matched with receipt")

        # wait for network message
        if not faststop_network_message_interpreter.wait_for_network_message(last_id=last_ID, request_map="13"):
            tc_fail("Required Network message did not come")

        # Fetch network message for Z01 13 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________13%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 13 Network Message is {strNetworkMessage}")
        
        # verify Z01 13 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'13','N0','P2'):
            tc_fail("Z01 13 Standardmap map in network Mesage is not correct")

        # verify Z01_13 DDLD map
        if not faststop_network_message_interpreter.verify_ClientDictionaryData_Z01_DDL(strNetworkMessage,'D',prod1_list,prod2_list):
            tc_fail("Z01_13 DDLD map in network Mesage is not correct")
      
        return True
    
    @test
    def TC12(self):
        """
        Testlink Id : To verify reversal for 1 dry stock item transactions is completed successfully 
                      for MSD Mastercard Purchase having Track1 with N0 request map & P0 Response Map
        Args: None
        Returns: None
        """
        #Change response mode of networksim
        networksim.set_response_mode("Timeout")

        # fetch last networkmessage id
        last_ID = self.edh.get_last_msg_id(pspid="20")
        
        # add item with plu 1
        pos.add_item("1", method="PLU")

        # Perform card Payment with MSD MasterCard Purchase
        pos.click_function_key("pay", verify=False)
        pos.click_tender_key('CARD', verify=False)

        # Insert Mastercard on PINPad
        try: 
            pinpad.use_card(card_name='MCPurchase')
            time.sleep(5)
        except Exception as e:
            self.log.warning(f"Card swipe in pinpad failed. Exception: {e}")
            pos.click_keypad("CANCEL")
            return False

        start_time = time.time()
        while time.time() - start_time <= 120:
            msg = pos.read_message_box()
            if msg is not None:
                if "no response from host" in msg.lower():
                    pos.click_message_box_key("OK")
                    break
        else:
            return False

        # Void transaction
        if not pos.click_keypad("CANCEL", verify=False):
            return False
        if not pos.void_transaction():
            return False

        # Change response mode of networksim
        networksim.set_response_mode("Approval")

        # wait for network message
        if not faststop_network_message_interpreter.wait_for_network_message(last_id=last_ID, request_map="13"):
            tc_fail("Required Network message did not come")

        # Fetch network message for Z01 13 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________13%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 13 Network Message is {strNetworkMessage}")
        
        # verify Z01 13 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'13','N0','P0'):
            tc_fail("Z01 13 Standardmap map in network Mesage is not correct")
      
        return True
    
    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        # Change response mode of networksim
        networksim.set_response_mode("Approval")

        # Close pos instance
        pos.close()