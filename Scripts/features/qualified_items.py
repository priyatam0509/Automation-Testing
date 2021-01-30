"""
    File name: qualified_items.py
    Tags:
    Description: This script tests the ability to use qualified items in Express Lane.
    Author: Christopher Haynes
    Date created: 2019-11-26
    Date last modified: 
    Python Version: 3.7
"""

import logging, time
from app import Navi, mws, pos, system, checkout, qualifier_maint, item
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from Scripts.features import EL_PaymentTest

class qualified_items():
    """
    Description: Testing the ability to configure qualified_items items for Express Lane.
    """

    def __init__(self):
        """
        Description:
                Initializes the qualified_items class.
        Args:
                None
        Returns:
                None
        """
        # The logging object.
        # Example: self.log.info(f"Current value of var: {my_var}")
        self.log = logging.getLogger()
        self.item_num = 2053

    @setup
    def setup(self):
        """
        Description:
                Performs any initialization that is not default.
        Args:
                None
        Returns:
                None
        """
        self.log.info("Setting up a qualifier group")
        qualifiers = qualifier_maint.QualifierMaintenance()
        params = {
            "Groups": ["Soda"]
        }
        qualifiers.add(params)
        params = {
            "Types": ["6-Pack", "6"]
        }
        qualifiers.add(params)
        params = {
            "Types": ["12-Pack", "12"]
        }
        qualifiers.add(params)
        params = {
            "Types": ["24-Pack", "24"]
        }
        qualifiers.add(params)
        params = {"Groups": {"Soda": ["6-Pack", "12-Pack", "24-Pack"]}}
        time.sleep(1)
        qualifiers.check(params)
        mws.click_toolbar("Exit", main = True)
        
        
        self.log.info("Setting up a qualified item.")
        items = item.Item()
        new_item = {
            "General": {
                "PLU/UPC": "{}".format(self.item_num),
                "Description": "Dr. Soda",
                "Department": "Dept 1",
                "Item Type": "Regular Item",
                "Receipt Desc": "What U Need",
                "per unit": "500"
            },
            "Options": {
                        "Food Stampable": True,
                        "Quantity Allowed": False,
                        "Return Price": "500"
                        },
            "Qualifiers": {
                "Qualifier Group": "Soda",
                "6-Pack": {
                    "General": {
                        "Description": "6 Cans of Dr. Soda",
                        "per unit": "550"
                    },
                    "Options": {
                        "Return Price": "550"
                    }
                },
                "12-Pack": {
                    "General": {
                        "Description": "12 Cans of Dr. Soda",
                        "per unit": "1000"
                    },
                    "Options": {
                        "Return Price": "1000"
                    }
                },
                "24-Pack": {
                    "General": {
                        "Description": "24 Cans of Dr. Soda",
                        "per unit": "1800"
                    },
                    "Options": {
                        "Return Price": "1800"
                    }
                }
            }
        }
        items.add(new_item, overwrite = True)
        mws.click_toolbar("Exit", main = True)

    @test
    def check_qualified_item_1(self):
        """
        Description:
                Checks for the function of qualified items in the Express Lane.  This automates M-90734.
        Args: 
                None
        Returns: 
                None
        """
        self.log.info("Connecting to the Express Lane.")
        checkout.connect()
        #waiting for express lane to come up
        while checkout._is_element_present("//div[@id='disabled_screen']"):
            time.sleep(1)
        #ensuring the welcome screen is not in the way
        if checkout._is_element_present("//div[@id = 'welcomescreen']"):
            checkout.click_welcome_key("Start")

        self.log.info("Adding qualified items to the transaction.")
        checkout.enter_plu("{}".format(self.item_num))
        checkout.click_key("//button[contains(text(), \"Dr. Soda\")]") #TODO: Replace with whatever function HAWK adds to support qualifiers
        checkout.enter_plu("{}".format(self.item_num))
        checkout.click_key("//button[contains(text(), \"6-Pack\")]") #TODO: Replace with whatever function HAWK adds to support qualifiers
        checkout.enter_plu("{}".format(self.item_num))
        checkout.click_key("//button[contains(text(), \"12-Pack\")]") #TODO: Replace with whatever function HAWK adds to support qualifiers
        checkout.enter_plu("{}".format(self.item_num))
        checkout.click_key("//button[contains(text(), \"24-Pack\")]") #TODO: Replace with whatever function HAWK adds to support qualifiers
        
        self.log.info("Verifying the item was added correctly.")
        time.sleep(1) #gives the journal time to populate
        journal = checkout.read_transaction_journal()
        self.log.info(journal)
        checkout.close()
        if len(journal) > 5:
            tc_fail("There are too few items in the journal.")
        if len(journal[0]) < 2 or journal[0][0] != 'What U Need' or journal[0][1] != '$5.00':
            tc_fail("The first journal item \"{}\" is wrong.".format(journal[0]))
        if len(journal[1]) < 2 or journal[1][0] != '6 Cans of Dr. Soda' or journal[1][1] != '$5.50':
            tc_fail("The second journal item \"{}\" is wrong.".format(journal[1]))
        if len(journal[2]) < 2 or journal[2][0] != '12 Cans of Dr. Soda' or journal[2][1] != '$10.00':
            tc_fail("The third journal item \"{}\" is wrong.".format(journal[2]))
        if len(journal[3]) < 2 or journal[3][0] != '24 Cans of Dr. Soda' or journal[3][1] != '$18.00':
            tc_fail("The fourth journal item \"{}\" is wrong.".format(journal[3]))

    @teardown
    def teardown(self):
        """
        Description:
                Performs cleanup after this script ends.
        Args:
                None
        Returns:
                None
        """
        checkout.pay_card()
        # Suspend Transaction if any test case is fail due to payment issue
        EL_PaymentTest.suspend_transaction()



