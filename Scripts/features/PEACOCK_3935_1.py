"""
    File name: PEACOCK_3935_1.py
    Brand: FastStop
    Description: [PEACOCK-3935] Z0 34 - Refund Transaction at Growmark Site - Message map and 
                 Discretionary data layout changes for Amex, VI, MC, Discover card
    Author: Deepak Verma
    Date created: 2020-6-5 12:00
    Date last modified: 
    Python Version: 3.7
"""

import logging,time
from app import Navi, pos, system, pinpad, mws
from app.framework import EDH
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from Scripts.features import faststop_network_message_interpreter 

class PEACOCK_3935_1():
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
        self.card_list1 = ["Visa","MasterCard","Discover","American Express"]
        self.card_list2 = ["Visa Purchase","MasterCard Purchase"]

    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        if not system.restore_snapshot():
            self.log.warning("Not able to restore snapshot")

        # set manaul entry and allow for return flag for cards
        self.allow_for_returns_manualentry(self.card_list1,self.card_list2)
        
        # Navigate to POS screen
        pos.connect()

        pos.sign_on()
    
    def allow_for_returns_manualentry(self,card_list1,card_list2):
        """
        This is helper method to Set Allow for Returns and Manual entry True for given Cards.
        Args:
            card_list(list) : list of card names(strings)
        Returns: True/Fail
        """
        Navi.navigate_to("mws")
        mws.sign_on()

        #Navigating to Network Card Configuration Menu
        Navi.navigate_to("Network Card Configuration")

        for card in card_list1:
                
            mws.select("Card List",card)
            
            mws.set_value("Allowed for Returns","Yes")

            mws.set_value("Allowed for Manual Entry","Yes")

        for card in card_list2:
                
            mws.select("Card List",card)

            mws.set_value("Allowed for Manual Entry","Yes")

            mws.set_value("Prompt for ZIP Code Outside","Yes")

        mws.click_toolbar("Save")
    
    @test
    def TC1(self):
        """
        Testlink Id : To verify refund/return for 1 dry stock item transactions is completed successfully 
                      when enter correct required data after shift close for MSD Visa card having Track2/Track1 & Track2 with N0 
                      map & N0 response map having Client Discretionary Data Layout B fields
        Args: None
        Returns: None
        """

        # Create a list of product data
        prod1_list = ["000", "$0.00", "00000", "0000", "00"]
    
        prod2_list = ["400", "1000", self.item_amount]

        # fetch last networkmessage id
        last_ID = self.edh.get_last_msg_id(pspid="20")

        #refund
        pos.click("REFUND")

        pos.add_item("1",method="PLU")

        pos.pay_card(card_name="Visa", invoice_number="1234")

        #Verifying details from receipt
        if not pos.check_receipt_for(["8021","Visa"]):
           tc_fail("details not matched with receipt")

        # wait for network message
        if not faststop_network_message_interpreter.wait_for_network_message(last_id=last_ID, request_map="34"):
            tc_fail("Required Network message did not come")

        # Fetch network message for Z01 34 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________34%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 34 Network Message is {strNetworkMessage}")
        
        #verify Z01 34 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'34','N0','N0'):    
            tc_fail("Z01 34 Standardmap map in network Mesage is not correct")

        #verify Z01 34 DDLD map
        if not faststop_network_message_interpreter.verify_ClientDictionaryData_Z01_DDL(strNetworkMessage,'B',prod1_list,prod2_list):
            tc_fail("Z01_34 DDLB map in network Mesage is not correct")
      
        return True
    
    @test
    def TC2(self):
        """
        Testlink Id : To verify refund/return for manual fuel sale & 1 dry stock item transactions is 
                      completed successfully when enter correct required data after shift close for MSD Mastercard having 
                      Track2/Track1 & Track2 with N0 request map & N0 response map having Client Discretionary Data Layout B fields
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

        # paying using MSD MasterCard Card
        pos.pay_card(card_name="MasterCard", invoice_number="1234")

        #Verifying details from receipt
        if not pos.check_receipt_for(["0008","MasterCard"]):
           tc_fail("details not matched with receipt")

        # wait for network message
        if not faststop_network_message_interpreter.wait_for_network_message(last_id=last_ID, request_map="34"):
            tc_fail("Required Network message did not come")

        # Fetch network message for Z01 34 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________34%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 34 Network Message is {strNetworkMessage}")
        
        #verify Z01 34 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'34','N0','N0'):    
            tc_fail("Z01 34 Standardmap map in network Mesage is not correct")

        #verify Z01_34 DDLD map
        if not faststop_network_message_interpreter.verify_ClientDictionaryData_Z01_DDL(strNetworkMessage,'B',prod1_list,prod2_list):
            tc_fail("Z01_34 DDLB map in network Mesage is not correct")
      
        return True

    @test
    def TC3(self):
        """
        Testlink Id : To verify refund/return for 1 dry stock item transactions is completed successfully when enter correct 
                      required data after store close for MSD Discover card having Track1 with M0 request map & N0 response
                      map having Client Discretionary Data Layout B fields
        Args: None
        Returns: None
        """
       
        # Create a list of product data
        prod1_list = ["000", "$0.00", "00000", "0000", "00"]
    
        prod2_list = ["400", "1000", self.item_amount]

        # fetch last networkmessage id
        last_ID = self.edh.get_last_msg_id(pspid="20")

        #refund
        pos.click("REFUND")

        pos.add_item("1",method="PLU")

        # paying using MSD Discover Card having Track1 only
        pos.pay_card(card_name="Discover", invoice_number="1234")

        #Verifying details from receipt
        if not pos.check_receipt_for(["0007","Discover"]):
           tc_fail("details not matched with receipt")

        # wait for network message
        if not faststop_network_message_interpreter.wait_for_network_message(last_id=last_ID, request_map="34"):
            tc_fail("Required Network message did not come")

        # Fetch network message for Z01 34 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________34%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 34 Network Message is {strNetworkMessage}")
        
        #verify Z01 34 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'34','N0','N0'):    
            tc_fail("Z01 34 Standardmap map in network Mesage is not correct")

        #verify Z01_34 DDLD map
        if not faststop_network_message_interpreter.verify_ClientDictionaryData_Z01_DDL(strNetworkMessage,'B',prod1_list,prod2_list):
            tc_fail("Z01_34 DDLB map in network Mesage is not correct")
      
        return True
    
    @test
    def TC4(self):
        """
        Testlink Id : To verify refund/return for manual fuel sale & 1 dry stock item transactions is completed 
                      successfully when enter correct required data after store close for MSD Amex card having Track1/Track1 & 
                      Track2 with M0 request map & N0 response map having Client Discretionary Data Layout B fields
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

        # paying using MSD Amex Card having Track1 and Track2
        pos.pay_card(card_name="AmExTrack1Track2", invoice_number="1234")

        #Verifying details from receipt
        if not pos.check_receipt_for(["9509","American Express"]):
           tc_fail("details not matched with receipt")

        # wait for network message
        if not faststop_network_message_interpreter.wait_for_network_message(last_id=last_ID, request_map="34"):
            tc_fail("Required Network message did not come")

        # Fetch network message for Z01 34 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________34%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 34 Network Message is {strNetworkMessage}")
        
        #verify Z01 34 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'34','N0','M0'):    
            tc_fail("Z01 34 Standardmap map in network Mesage is not correct")

        #verify Z01_34 DDLD map
        if not faststop_network_message_interpreter.verify_ClientDictionaryData_Z01_DDL(strNetworkMessage,'B',prod1_list,prod2_list):
            tc_fail("Z01_34 DDLB map in network Mesage is not correct")
      
        return True

    @test
    def TC5(self):
        """
        Testlink Id : To verify refund/return for 1 dry stock item transactions is completed successfully 
                      when enter correct required data after shift close for MSD Visa card having Track2/Track1 & Track2 by
                      manual card entry with N0 request map & N0 response map having Client Discretionary Data Layout B fields
        Args: None
        Returns: None
        """
       
        # Create a list of product data
        prod1_list = ["000", "$0.00", "00000", "0000", "00"]
    
        prod2_list = ["400", "1000", self.item_amount]

        # fetch last networkmessage id
        last_ID = self.edh.get_last_msg_id(pspid="20")

        #refund
        pos.click("REFUND")

        pos.add_item("1",method="PLU")

        pos.manual_entry(brand="FASTSTOP",card_name="Visa", invoice_number="1234")

        #Verifying details from receipt
        if not pos.check_receipt_for(["8021","Visa"]):
           tc_fail("details not matched with receipt")

        # wait for network message
        if not faststop_network_message_interpreter.wait_for_network_message(last_id=last_ID, request_map="34"):
            tc_fail("Required Network message did not come")

        # Fetch network message for Z01 34 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________34%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 34 Network Message is {strNetworkMessage}")
        
        #verify Z01 34 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'34','N0','N0'):    
            tc_fail("Z01 34 Standardmap map in network Mesage is not correct")

        #verify Z01_34 DDLD map
        if not faststop_network_message_interpreter.verify_ClientDictionaryData_Z01_DDL(strNetworkMessage,'B',prod1_list,prod2_list):
            tc_fail("Z01_34 DDLB map in network Mesage is not correct")
      
        return True
    
    @test
    def TC6(self):
        """
        Testlink Id : To verify refund/return for manual fuel sale & 1 dry stock item transactions is completed 
                      successfully when enter correct required data after shift close for MSD Mastercard having Track2/Track1 & Track2 by 
                      manual card entry with N0 request map & N0 response map having Client Discretionary Data Layout B fields
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

        pos.manual_entry(brand="FASTSTOP",card_name="MasterCard", invoice_number="1234")

        #Verifying details from receipt
        if not pos.check_receipt_for(["0008","MasterCard"]):
           tc_fail("details not matched with receipt")

        # wait for network message
        if not faststop_network_message_interpreter.wait_for_network_message(last_id=last_ID, request_map="34"):
            tc_fail("Required Network message did not come")

        # Fetch network message for Z01 34 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________34%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Z01 34 Network Message is {strNetworkMessage}")
        
        #verify Z01 34 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'34','N0','N0'):    
            tc_fail("Z01 34 Standardmap map in network Mesage is not correct")

        #verify Z01_34 DDLD map
        if not faststop_network_message_interpreter.verify_ClientDictionaryData_Z01_DDL(strNetworkMessage,'B',prod1_list,prod2_list):
            tc_fail("Z01_34 DDLB map in network Mesage is not correct")
      
        return True
    
    @test
    def TC7(self):  
        """
        Testlink Id : To verify refund/return for 1 dry stock item transactions is completed successfully when 
                      enter correct required data after store close for EMV Discover card having Track2 with B2 request map & 
                      N0 response map having Client Discretionary Data Layout E fields
        Args: None
        Returns: None
        """

        # fetch last networkmessage id
        last_ID = self.edh.get_last_msg_id(pspid="20")
       
        # Create a list of product data
        prod1_list = ["000", "$0.00", "00000", "0000", "00"]
    
        prod2_list = ["400", "1000", self.item_amount]

        #refund
        pos.click("REFUND")

        pos.add_item("1",method="PLU")

        # paying using EMV Discover
        pos.pay_card(brand="FASTSTOP",card_name="EMVDiscoverUSDebit", invoice_number="1234")

        #Verifying details from receipt
        if not pos.check_receipt_for(["0216","Discover","A0000001523010"]):
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

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        # Close pos instance
        pos.close()