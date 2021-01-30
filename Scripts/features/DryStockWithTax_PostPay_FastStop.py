"""
    File name: DryStockWithTax_PostPay_FastStop.py
    Brand : FastStop
    Description: [PEACOCK-3186] This will perform Dry stock with tax for faststop postpay
    Author: Deepak Verma
    Date created: 2020-4-28 14:53:24
    Date last modified: 
    Python Version: 3.7
"""

import logging, time
from app import item, Navi, mws, pos, system, tax_maint
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from Scripts.features import faststop_network_message_interpreter

class DryStockWithTax_PostPay_FastStop():
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

    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        Navi.navigate_to("MWS")
        mws.sign_on()
        
        tax_cfg = {
                    "Rates":
                        {
                          "GST Tax":
                            {
                              "Name": "GST Tax",
                              "Receipt Description": "GST",
                              "GST": True,
                              "Percent": "3.0",
                              "Activate": True
                            }
                        },
                    "Groups":
                        {
                          "GST Tax":
                            {
                              "Name": "GST",
                              "POS Description": "GST",
                              "Identify taxed items with": True,
                              "Identify taxed items with text box": "GST",
                              "and print receipt key": "GST",
                              "Rates": { "GST Tax": True },
                              "Activate": True
                            }
                        },
                    "Options":
                        {
                          "Print all assigned fuel tax amounts on receipt": True
                        }
                  }

        # Create object for Tax
        tax_obj = tax_maint.TaxMaintenance()

        #Adding tax in tax maintenance
        tax_obj.configure(tax_cfg)

        #Create object for Item
        item_obj = item.Item()

        #Adding the item with tax
        item_data = {
            "General": {
                "PLU/UPC": "8983",
                "Description": "Test_Item",
                "Department": "Dept 1",
                "This item sells for": True,
                "per unit": "6.0"
            },
            "Options": {
                "Return Price": "6.0",
                "Network Product Code": "400",
                "Tax Group": "GST"
            }
        }
        mws.set_value("PLU/UPC", "8983")

        mws.click_toolbar("Search")

        stringResult = mws.get_top_bar_text()

        # Check if item already present. If not then add item
        if ("No" in stringResult):
            item_obj.add(item_data)
            self.log.info("Item added with GST Tax")
        else:
            self.log.info("Item already exists so exit from item screen")
            
        mws.click_toolbar("Exit")
    
    @test
    def item_sale(self):
        """
        Testlink Id : This will add dry stock item and Perform sale with Fast Stop card.
                      After sale this will verify network message for Standard map, Z01-05 P7 map and Z01-11 P7 map 
        Args: None
        Returns: None
        """        
        #Navigate to POS screen
        Navi.navigate_to("POS")
        
        # Sign on to POS screen if not already sign-on
        pos.sign_on()

        # Add item on which tax is present
        pos.add_item("8983", method="plu")

        # Perform card Payment with FastStop card
        pos.pay_card(brand='FASTSTOP', card_name='Fast Stop Commercial')

        balance = pos.read_balance()
        total = balance['Total']
        self.log.debug(f"total is {total}")

        # Create list to have product data used in sale
        prod1_list = ['400','$6.00']
        
        req_cmd = "Select NetworkMessage from networkmessages where NetworkPSPId=20 and NetworkMessage like '%TESOZ01%' and NetworkMessage like '%TESOP1%' and NetworkMessage like '%Request%' order by NetworkMessageId desc"
        strNetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(req_cmd)
        self.log.info(f"Request Network Message is {strNetworkMessage}")

        #Verify Client dictionary data in network message
        if not faststop_network_message_interpreter.verify_faststop_clientDisctionaryData(strNetworkMessage,'F00'):
            tc_fail("Client Dictionary Data in network message is not correct")

        # Verify Standard Map in network message
        if not faststop_network_message_interpreter.verify_faststop_standardMap(strNetworkMessage):
            tc_fail("Standard Map in network Message is not correct")
        
        #verify Z01 13 P7 map
        if not faststop_network_message_interpreter.verify_faststop_Z01_13_p7Map(strNetworkMessage,total,prod1_list,tax='00018'):
            tc_fail("Z01 13 P7 map in network Message is not correct")
        
        # Fetch Network message for 1st response
        res_cmd = "Select NetworkMessage from networkmessages where NetworkPSPId=20 and NetworkMessage like '%M0014%'order by NetworkMessageId desc"
        res_NetworkMessage = faststop_network_message_interpreter.fetch_networkmessage(res_cmd)
        self.log.info(f"Z01 14 Network Message is {res_NetworkMessage}")
        
        #verify Z01-14 map
        if not faststop_network_message_interpreter.verify_faststop_Z01_14_Map(res_NetworkMessage):
            tc_fail("Z01 14 P7 map in network Message is not correct")
        
        return True

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        pass