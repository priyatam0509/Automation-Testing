"""
    File name: PEACOCK_3930.py
    Brand: FastStop
    Description: [PEACOCK-3930] Z01 05/11 Outdoor Transaction at Growmark Site - Message map and Discretionary data layout 
                changes for Amex, VI, MC, Discover card
    Author: Asha
    Date created: 2020-6-9 17:00
    Date last modified: 
    Python Version: 3.7
"""

import logging, time
from app import Navi, mws, pos, system, crindsim
from app.features import crind_merch
from app.framework import EDH
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from Scripts.features import faststop_network_message_interpreter 

log = logging.getLogger()

def crind_sale(card_name="Visa", brand="core", debit="no", selection="DONE", receipt="yes", dispenser=1, timeout=120):
    """
    Run a crind sale and answers all prompts.
    Args:
        card_name: (str) The name of the card being used.
        debit: (str) prompt to chevk if card is debit or not
        selection: (str) Answer to crindmerchandise package selection prompt 
        receipt: (str) Answer to receipt prompt
        dispenser: (int) The number of the dispenser that the card will be swiping at.
        timeout: (int) The time given for the transaction to complete.
    Returns:
        True/False: (bool) True if CRIND sale was successful. False if there was any error.
    """
    start_time = time.time()

    # Loop verifies that crindsim is in idle state before starting transaction
    while time.time() - start_time < timeout:
        if "insert card" in crindsim.get_display_text().lower():
            break
    else:
        log.warning("Unable to run transaction because CRIND is not at IDLE")
        return False

    start_time2 = time.time()
    while time.time() - start_time2 < timeout:
        display = crindsim.get_display_text().lower()
        softkey_text = crindsim.get_softkey_text()

        if "insert card" in display:
            crindsim.swipe_card(card_name, brand, dispenser)
            log.info("swiped " + card_name)
            time.sleep(3)
        elif "debit card" in display:
            crindsim.press_softkey(debit, dispenser)
            log.info("Pressed " + debit + " for debit prompt")
            time.sleep(1)
        elif " Item 7|$5.00" in softkey_text:
            crindsim.press_softkey("Item 7|$5.00", dispenser)
            log.info(f"Item 7|$5.00 selected")
            time.sleep(1)
            crindsim.press_softkey("Done", dispenser)
            log.info(f"Done selected")
            time.sleep(1)
        elif " Cancel order" in softkey_text:
            crindsim.press_softkey("Done", dispenser)
            log.info(f"Done selected")
            time.sleep(1)
        elif " Cancel/Add Items" in softkey_text:
            crindsim.press_softkey("Done", dispenser)
            log.info(f"Done selected")
        elif "please see cashier" in display:
            log.warning("Customer instructed to see cashier")
            return False
        elif "make selection carwash crindmerchandise" in display:
            crindsim.press_softkey(selection, dispenser)
            log.info(f"{selection} selected")
            time.sleep(1)
        elif "do you want a receipt" in display:
            crindsim.press_softkey(receipt, dispenser)
            log.info("pressed " + receipt + " for receipt")
        elif "thank you" in display:
            log.debug("sale complete")
            return True
        time.sleep(2)
    log.warning("Transaction did not complete before timeout")
    
    return False

class PEACOCK_3930():
    """
    Description: Test class that provides an interface for testing.
    """

    def __init__(self):
        """Initializes the Template class.
        Args: None
        Returns: None
        """
        self.fuel_amount = "$15.00"
        self.item_amount = "$5.00"

        # Create object of EDH
        self.edh = EDH.EDH()

        self.crind_merch_info = {
                    "General": {
                        "CRIND Merchandising is Enabled": True,
                        "Vendor Name": "CrindMerchandise",
                    },
                    "Categories": "TestCategory1",
                    "Items": {
                        "TestCategory1": ["1","Item 7"]
                    }
                }

    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        if not system.restore_snapshot():
            log.warning("Not able to restore snapshot")

        # Sign on to POS screen if not already sign-on
        mws.sign_on()

        # create object of crind merchandise
        cm = crind_merch.CRINDMerchandising()

        if not cm.configure(self.crind_merch_info):
            tc_fail("Configure crind merchandise in MWS")
        
        # configure sales target
        crindsim.set_sales_target(sales_type ="money", target="15.00", dispenser=1)

        # set mode for dispenser
        crindsim.set_mode("auto")

        # Navigate to POS screen
        Navi.navigate_to("POS")
        
        # Sign on to POS screen if not already sign-on
        pos.sign_on()

    @test
    def TC1(self):
        """
        Zephyr Id : To verify Outside Crind sale transactions is completed successfully 
                    for MSD Visa card having B2 request map & B0 response map for Z01 05 and
                    N0 response map for Z01 11 having Client Discretionary Data Layout E fields
        Args: None
        Returns: None
        """   
        # Create a list of product data
        prod1_list = ["004", self.fuel_amount, "01000", "15000", "01"]

        # fetch last networkmessage id
        last_ID = self.edh.get_last_msg_id(pspid="20")
            
        # perform sale with fuel
        if not crind_sale(card_name="Visa", selection="Done"):
            tc_fail("outside transaction not successfull")

        receipt = crindsim.get_receipt()

        # Verifying details from receipt
        if "Visa" not in receipt:
            tc_fail("Card name not matched with receipt")

        # wait for network message
        if not faststop_network_message_interpreter.wait_for_network_message(last_id=last_ID, request_map="11"):
            tc_fail("Required Network message did not come")

        # Fetch network message for Z01 05 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________5%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        log.info(f"Z01 05 Network Message is {strNetworkMessage}")
        
        #verify Z01 05 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'05','B0','B2'):
            tc_fail("Z01 05 Standardmap map in network Mesage is not correct")

        # Fetch network message for Z01 11 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________11%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        log.info(f"Z01 11 Network Message is {strNetworkMessage}")
        
        #verify Z01 11 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'11','N0','B2'):
            tc_fail("Z01 11 Standardmap map in network Mesage is not correct")

        #verify Z01_11 DDLE map
        if not faststop_network_message_interpreter.verify_ClientDictionaryData_Z01_DDL(strNetworkMessage,'E',prod1_list):
            tc_fail("Z01_11 DDLE map in network Mesage is not correct")

        return True

    @test
    def TC3(self):
        """
        Zephyr Id : To verify Outside Crind sale transactions is completed successfully 
                    for MSD Discover card having B2 request map and B0 response map for Z01 05 
                    and N0 response map for Z01 11 having Client Discretionary Data Layout E fields
        Args: None
        Returns: None
        """   
        # Create a list of product data
        prod1_list = ["004", self.fuel_amount, "01000", "15000", "01"]

        # fetch last networkmessage id
        last_ID = self.edh.get_last_msg_id(pspid="20")
            
        # perform sale with fuel
        if not crind_sale(card_name="Discover", selection="Done"):
            tc_fail("outside transaction not successfull")

        receipt = crindsim.get_receipt()

        #Verifying details from receipt
        if "Discover" not in receipt:
           tc_fail("Card name not matched with receipt")

        # wait for network message
        if not faststop_network_message_interpreter.wait_for_network_message(last_id=last_ID, request_map="11"):
            tc_fail("Required Network message did not come")

        # Fetch network message for Z01 05 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________5%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        log.info(f"Z01 05 Network Message is {strNetworkMessage}")
        
        #verify Z01 05 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'05','B0','B2'):
            tc_fail("Z01 05 Standardmap map in network Mesage is not correct")

        # Fetch network message for Z01 11 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________11%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        log.info(f"Z01 11 Network Message is {strNetworkMessage}")
        
        #verify Z01 11 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'11','N0','B2'):
            tc_fail("Z01 11 Standardmap map in network Mesage is not correct")

        #verify Z01_11 DDLE map
        if not faststop_network_message_interpreter.verify_ClientDictionaryData_Z01_DDL(strNetworkMessage,'E',prod1_list):
            tc_fail("Z01_11 DDLE map in network Mesage is not correct")

        return True
    
    @test
    def TC5(self):
        """
        Zephyr Id : To verify Outside Crind sale transactions is completed successfully 
                    for Master card having B2 request map and B0 response map for Z01 05 
                    and N0 response map for Z01 11 having Client Discretionary Data Layout E fields
        Args: None
        Returns: None
        """   
        # Create a list of product data
        prod1_list = ["004", self.fuel_amount, "01000", "15000", "01"]

        # fetch last networkmessage id
        last_ID = self.edh.get_last_msg_id(pspid="20")
            
        # perform sale with fuel
        if not crind_sale(card_name="MasterCard", selection="Done"):
            tc_fail("outside transaction not successfull")

        receipt = crindsim.get_receipt()

        #Verifying details from receipt
        if "MasterCard" not in receipt:
           tc_fail("Card name not matched with receipt")

        time.sleep(5)

        # wait for network message
        if not faststop_network_message_interpreter.wait_for_network_message(last_id=last_ID, request_map="11"):
            tc_fail("Required Network message did not come")

        # Fetch network message for Z01 05 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________5%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        log.info(f"Z01 05 Network Message is {strNetworkMessage}")
        
        #verify Z01 05 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'05','B0','B2'):
            tc_fail("Z01 05 Standardmap map in network Mesage is not correct")

        # Fetch network message for Z01 11 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________11%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        log.info(f"Z01 11 Network Message is {strNetworkMessage}")
        
        #verify Z01 11 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'11','N0','B2'):
            tc_fail("Z01 11 Standardmap map in network Mesage is not correct")

        #verify Z01_11 DDLE map
        if not faststop_network_message_interpreter.verify_ClientDictionaryData_Z01_DDL(strNetworkMessage,'E',prod1_list):
            tc_fail("Z01_11 DDLE map in network Mesage is not correct")

        return True
    
    @test
    def TC2(self):
        """
        Zephyr Id : To verify Outside Crind sale & 1 Crind Merchandising item transactions is completed successfully 
                    for MSD Mastercard having B2 request map & B0 response map for Z01 05 and 
                    N0 response map for Z01 11 having Client Discretionary Data Layout E fields
        Args: None
        Returns: None
        """   
        # Create a list of product data
        prod1_list = ["004", self.fuel_amount, "01000", "15000", "01"]

        # fetch last networkmessage id
        last_ID = self.edh.get_last_msg_id(pspid="20")
            
        # Perform crind sale
        if not crind_sale(card_name="MasterCard", selection="CrindMerChandise"):
            tc_fail("outside transaction not successfull")

        receipt = crindsim.get_receipt()

        #Verifying details from receipt
        if "MasterCard" not in receipt:
           tc_fail("Card name not matched with receipt")

        # wait for network message
        if not faststop_network_message_interpreter.wait_for_network_message(last_id=last_ID, request_map="11"):
            tc_fail("Required Network message did not come")

        # Fetch network message for Z01 05 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________5%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        log.info(f"Z01 05 Network Message is {strNetworkMessage}")
        
        #verify Z01 05 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'05','B0','B2'):
            tc_fail("Z01 05 Standardmap map in network Mesage is not correct")

        # Fetch network message for Z01 11 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________11%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        log.info(f"Z01 11 Network Message is {strNetworkMessage}")
        
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
        Zephyr Id : To verify Outside Crind sale & 1 Crind Merchandising item transactions is completed successfully 
                    for MSD Amex card having B2 request map & B0 response map for Z01 05 and 
                    N0 response map for Z01 11 having Client Discretionary Data Layout E fields
        Args: None
        Returns: None
        """   
        # Create a list of product data
        prod1_list = ["004", self.fuel_amount, "01000", "15000", "01"]

        # fetch last networkmessage id
        last_ID = self.edh.get_last_msg_id(pspid="20")
            
        # Perform crind sale
        if not crind_sale(card_name="AmExTrack1Track2", selection="CrindMerChandise"):
            tc_fail("outside transaction not successfull")

        receipt = crindsim.get_receipt()

        #Verifying details from receipt
        if "American Express" not in receipt:
           tc_fail("Card name not matched with receipt")

        # wait for network message
        if not faststop_network_message_interpreter.wait_for_network_message(last_id=last_ID, request_map="11"):
            tc_fail("Required Network message did not come")

        # Fetch network message for Z01 05 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________5%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        log.info(f"Z01 05 Network Message is {strNetworkMessage}")
        
        #verify Z01 05 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'05','B0','B2'):
            tc_fail("Z01 05 Standardmap map in network Mesage is not correct")

        # Fetch network message for Z01 11 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________11%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        log.info(f"Z01 11 Network Message is {strNetworkMessage}")
        
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
        Zephyr Id : To verify Outside Crind sale & 1 Crind Merchandising item transactions is completed successfully 
                    for Visa card, having B2 request map & B0 response map for Z01 05 and 
                    N0 response map for Z01 11 having Client Discretionary Data Layout E fields
        Args: None
        Returns: None
        """   
        # Create a list of product data
        prod1_list = ["004", self.fuel_amount, "01000", "15000", "01"]

        # fetch last networkmessage id
        last_ID = self.edh.get_last_msg_id(pspid="20")
            
        # Perform crind sale with crind merchandise
        if not crind_sale(card_name="Visa", selection="CrindMerChandise"):
            tc_fail("outside transaction not successfull")

        receipt = crindsim.get_receipt()

        #Verifying details from receipt
        if "Visa" not in receipt:
           tc_fail("Card name not matched with receipt")

        # wait for network message
        if not faststop_network_message_interpreter.wait_for_network_message(last_id=last_ID, request_map="11"):
            tc_fail("Required Network message did not come")

        # Fetch network message for Z01 05 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________5%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        log.info(f"Z01 05 Network Message is {strNetworkMessage}")
        
        #verify Z01 05 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'05','B0','B2'):
            tc_fail("Z01 05 Standardmap map in network Mesage is not correct")

        # Fetch network message for Z01 11 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________11%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        log.info(f"Z01 11 Network Message is {strNetworkMessage}")
        
        #verify Z01 11 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'11','N0','B2'):
            tc_fail("Z01 11 Standardmap map in network Mesage is not correct")

        #verify Z01_11 DDLE map
        if not faststop_network_message_interpreter.verify_ClientDictionaryData_Z01_DDL(strNetworkMessage,'E',prod1_list):
            tc_fail("Z01_11 DDLE map in network Mesage is not correct")

        return True
    
    @test
    def TC9(self):
        """
        Zephyr Id : To verify reversal for outside crind sale transactions is completed successfully 
                    for MSD Visa card having Track1 with M0 request map & N0 response map
        Args: None
        Returns: None
        """
        # fetch last networkmessage id
        last_ID = self.edh.get_last_msg_id(pspid="20")

        # set crind mode to manual
        crindsim.set_mode("manual", "1")

        crindsim.swipe_card(card_name="Visa")

        time.sleep(2)

        start_time2 = time.time()
        while time.time() - start_time2 < 60:
            display = crindsim.get_display_text().lower()
            if "insert card" in display:
                break
            elif "debit card" in display:
                crindsim.press_softkey("no", "1")
                time.sleep(2)
            elif "make selection" in display:
                crindsim.press_keypad("Cancel", "1")
                time.sleep(2)
            elif "lift handle" in display:
                crindsim.press_keypad("Cancel", "1")
                time.sleep(2)

        # wait for network message
        if not faststop_network_message_interpreter.wait_for_network_message(last_id=last_ID, request_map="30"):
            tc_fail("Required Network message did not come")

        # Fetch network message for Z01 30 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________30%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        log.info(f"Z01 30 Network Message is {strNetworkMessage}")
        
        #verify Z01 30 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'30','N0','B2'):
            tc_fail("Z01 30 Standardmap map in network Mesage is not correct")
      
        return True

    @test
    def TC10(self):
        """
        Zephyr Id : To verify reversal for outside crind sale transactions is completed successfully 
                    for Mastercard having Track1 with M0 request map & N0 response map
        Args: None
        Returns: None
        """
        # fetch last networkmessage id
        last_ID = self.edh.get_last_msg_id(pspid="20")

        crindsim.swipe_card(card_name="MasterCard")

        time.sleep(2)

        start_time2 = time.time()
        while time.time() - start_time2 < 60:
            display = crindsim.get_display_text().lower()
            if "insert card" in display:
                break
            elif "debit card" in display:
                crindsim.press_softkey("no", "1")
                time.sleep(2)
            elif "make selection" in display:
                crindsim.press_keypad("Cancel", "1")
                time.sleep(2)
            elif "lift handle" in display:
                crindsim.press_keypad("Cancel", "1")
                time.sleep(2)

        # wait for network message
        if not faststop_network_message_interpreter.wait_for_network_message(last_id=last_ID, request_map="30"):
            tc_fail("Required Network message did not come")

        # Fetch network message for Z01 30 request
        req_cmd = "Select NetworkMessage from networkmessages where NetworkMessage like '%TESOZ01%' and NetworkMessage like '_________30%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        log.info(f"Z01 30 Network Message is {strNetworkMessage}")
        
        #verify Z01 30 Standardmap
        if not faststop_network_message_interpreter.verify_faststop_Z01_StandardMap(strNetworkMessage,'30','N0','B2'):
            tc_fail("Z01 30 Standardmap map in network Mesage is not correct")
      
        return True
    
    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        # set mode for dispenser
        crindsim.set_mode("auto")

        # Close pos instance
        pos.close()