"""
    File name: PEACOCK_3935_2.py
    Brand: FastStop
    Description: [PEACOCK-3935] Z0 34 - Refund Transaction at Growmark Site - Message map and 
                 Discretionary data layout changes for Amex, VI, MC, Discover card
    Author: Deepak Verma
    Date created: 2020-6-5 12:00
    Date last modified: 
    Python Version: 3.7
"""

import logging,time
from app import pos, system, pinpad, mws, networksim
from app.framework import EDH
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from Scripts.features import faststop_network_message_interpreter 

class PEACOCK_3935_2():
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
        
    def fetch_invoice_no_msd(self):
        
        pos.click_function_key("Receipt Search")

        pos.select_receipt(1)

        receipt = pos.read_receipt()

        pos.click("CANCEL")

        for e in receipt:
            if e.find("INVOICE") != -1:
                inv_no_index = receipt.index(e)
                inv_no=receipt[inv_no_index+1]    
                break

        return inv_no
    
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
    def TC13_1(self):
        """
        Testlink Id : [PEACOCK_3994] To verify refund void for carwash transaction is completed successfully 
                      when enter correct required data in current batch for MSD Visa Purchase card having Track1 
                      with M0 request map & N0 response map
        Args: None
        Returns: None
        """
        
        #add itm with plu 1234
        pos.add_item("1234",method="PLU",qualifier="Carwash 1 ($2.50)")

        # Perform card Payment with MSD Visa Purchase Card having track1 only
        pos.pay_card(card_name="VisaPurchaseTrack1")

        # fetch invoice not 1234
        invoice = self.fetch_invoice_no_msd()

        # fetch last networkmessage id
        last_ID = self.edh.get_last_msg_id(pspid="20")

        #refund
        pos.click("REFUND")

        pos.add_item("1234",method="PLU",qualifier="Carwash 1 ($2.50)")

        # paying using MSD Visa Card
        pos.pay_card(card_name="VisaPurchaseTrack1", invoice_number=invoice)

        #Verifying details from receipt
        if not pos.check_receipt_for(["8889","Visa"]):
           tc_fail("details not matched with receipt")

        time.sleep(240)

        # wait for network message
        if not faststop_network_message_interpreter.wait_for_network_message(last_id=last_ID, request_map="32"):
            tc_fail("Required Network message did not come")

        # Fetch network message for Z01 32 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________32%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 32 Network Message is {strNetworkMessage}")
        
        #verify Z01 13 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'32','N0','M0'):    
            tc_fail("Z01 32 Standardmap map in network Mesage is not correct")
      
        return True
    
    @test
    def TC13_2(self):
        """
        Testlink Id : To verify refund void for 1 dry stock item transaction is completed successfully when 
                      enter correct required data in current batch for MSD Visa card having Track2/Track1 & Track2 with B2
                      request map & N0 response map
        Args: None
        Returns: None
        """
        
        #add item with plu 1
        pos.add_item("1", method="PLU")

        # Perform card Payment with MSD Visa Card
        pos.pay_card(card_name="Visa")

        # fetch invoice not 1234
        invoice = self.fetch_invoice_no_msd()

        # fetch last networkmessage id
        last_ID = self.edh.get_last_msg_id(pspid="20")

        #refund
        pos.click("REFUND")

        pos.add_item("1",method="PLU")

        # paying using MSD Visa Card
        pos.pay_card(card_name="Visa", invoice_number=invoice)

        #Verifying details from receipt
        if not pos.check_receipt_for(["8021","Visa"]):
           tc_fail("details not matched with receipt")

        # It has been observed that after 4 mins network message comes in EDH
        time.sleep(240)

        # wait for network message
        if not faststop_network_message_interpreter.wait_for_network_message(last_id=last_ID, request_map="32"):
            tc_fail("Required Network message did not come")

        # Fetch network message for Z01 32 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________32%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 32 Network Message is {strNetworkMessage}")
        
        #verify Z01 32 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'32','N0','B2'):    
            tc_fail("Z01 32 Standardmap map in network Mesage is not correct")
      
        return True

    @test
    def TC8(self):       
        """
        Testlink Id : To verify refund/return for manual fuel sale, 1 dry stock item & carwash transactions is 
                      completed successfully when enter correct required data after store close for EMV Amex card having Track2 
                      with B2 request map & N0 response map having Client Discretionary Data Layout E fields
        Args: None
        Returns: None
        """
       
        # Create a list of product data
        prod1_list = ["004", self.fuel_amount, "01000", "1000", "01"]
    
        prod2_list = ["400", "1000", self.item_amount]

        # fetch last networkmessage id
        last_ID = self.edh.get_last_msg_id(pspid="20")

        #refund
        pos.click("REFUND")

        pos.add_fuel(self.fuel_amount, mode="manual", grade=self.fuel_grade)

        pos.add_item("1",method="PLU")

        # paying using EMV Discover
        pos.pay_card(card_name="EMVAmEx", invoice_number="1234")

        #Verifying details from receipt
        if not pos.check_receipt_for(["9509","American Express","A00000002501"]):
           tc_fail("details not matched with receipt")

        # wait for network message
        if not faststop_network_message_interpreter.wait_for_network_message(last_id=last_ID, request_map="34"):
            tc_fail("Required Network message did not come")

        # Fetch network message for Z01 34 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________34%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 34 Network Message is {strNetworkMessage}")
        
        #verify Z01 34 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'34','N0','B2'):    
            tc_fail("Z01 34 Standardmap map in network Mesage is not correct")

        #verify Z01_34 DDLD map
        if not faststop_network_message_interpreter.verify_ClientDictionaryData_Z01_DDL(strNetworkMessage,'E',prod1_list,prod2_list):
            tc_fail("Z01_34 DDLE map in network Mesage is not correct")
      
        return True
        
    @test
    def TC14(self):
        """
        Testlink Id : To verify refund void for carwash transaction is completed successfully when enter correct 
                      required data in current batch for MSD Discover card having Track1 with M0 request map & N0 response map
        Args: None
        Returns: None
        """
        
        #add item with plu 1234
        pos.add_item("1234",method="PLU",qualifier="Carwash 1 ($2.50)")

        # Perform card Payment with MSD Discover with Track1 only
        pos.pay_card(card_name="Discover")

        # fetch invoice not 1234
        invoice=self.fetch_invoice_no_msd()

        # fetch last networkmessage id
        last_ID = self.edh.get_last_msg_id(pspid="20")

        #refund
        pos.click("REFUND")

        pos.add_item("1234",method="PLU",qualifier="Carwash 1 ($2.50)")

        # paying using MSD Discover Card having track1 only
        pos.pay_card(card_name="Discover", invoice_number=invoice)

        #Verifying details from receipt
        if not pos.check_receipt_for(["0007","Discover"]):
           tc_fail("details not matched with receipt")

        # It has been observed that after 4 mins network message comes in EDH
        time.sleep(240)

        # wait for network message
        if not faststop_network_message_interpreter.wait_for_network_message(last_id=last_ID, request_map="32"):
            tc_fail("Required Network message did not come")

        # Fetch network message for Z01 32 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________32%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 32 Network Message is {strNetworkMessage}")
        
        #verify Z01 32 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'32','N0','B2'):    
            tc_fail("Z01 32 Standardmap map in network Mesage is not correct")
      
        return True
    
    @test
    def TC11(self):
        """
        Testlink Id : To verify reversal for refund for dry stock transaction is completed successfully for card
                      having Track1 with M0 request map & N0 response map
        Args: None
        Returns: None
        """
        #Change response mode of networksim
        networksim.set_response_mode("Timeout")

        # fetch last networkmessage id
        last_ID = self.edh.get_last_msg_id(pspid="20")

        #refund
        pos.click("REFUND")

        pos.add_item("1",method="PLU")

        # paying using Card having track1
        if not pos.click_function_key('Pay', timeout=3):
            return False
        if not pos.click_tender_key("Card"):
            return False
        try:
            pinpad.use_card(card_name="AmExTrack1Track2")
        except Exception as e:
            self.log.warning(f"swipe Card in pinpad failed. Exception: {e}")
            pos.click_keypad("CANCEL")
            return False

        time.sleep(5)

        pos.enter_keypad("1234")   

        pos.click_keypad("ENTER")
        
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

        #Change response mode of networksim
        networksim.set_response_mode("Approval")

        # wait for network message
        if not faststop_network_message_interpreter.wait_for_network_message(last_id=last_ID, request_map="30"):
            tc_fail("Required Network message did not come")

        # Fetch network message for Z01 30 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________30%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 30 Network Message is {strNetworkMessage}")
        
        #verify Z01 30 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'30','N0','M0'):    
            tc_fail("Z01 30 Standardmap map in network Mesage is not correct")
      
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