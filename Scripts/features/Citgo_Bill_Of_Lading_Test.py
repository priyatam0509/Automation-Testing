"""
    File name: Citgo_Bill_Of_Lading_Test.py
    Tags: Citgo
    Description: 
    Author: Wil Elias
    Date created: 2019-07-18 16:58:29
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import Navi, mws, pos, system
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app import bill_of_lading

class Citgo_Bill_Of_Lading_Test():
    """
    Description: Test class that performs tests on the 
    """

    CHNG_PROD_INFO = {
        "Product 1" : {
			"Deliver Date" : "102317",
			"Bill Of Lading Number" : "345697",
			"Product Code #1" : "11111111",
			"Gross Volume for Product #1" : "222222",
			"Net Volume for Product #1" : "33333"
		}
    }

    CHNG_PRODS_INFO = {
        "Product 1" : {
			"Deliver Date" : "102317",
			"Bill Of Lading Number" : "345697",
			"Product Code #1" : "11111111",
			"Gross Volume for Product #1" : "222222",
			"Net Volume for Product #1" : "33333"
		},
        "Product 2" : {
            "Product Code #2" : "44444444",
            "Gross Volume for Product #2" : "555555",
            "Net Volume for Product #2" : "666666"
        },
        "Product 3" : {
            "Product Code #3" : "77777777",
            "Gross Volume for Product #3" : "888888",
            "Net Volume for Product #3" : "999999"
		},
        "Product 4" : {
            "Product Code #4" : "00000000",
            "Gross Volume for Product #4" : "111111",
            "Net Volume for Product #4" : "222222"
        },
        "Product 5" : {
            "Product Code #5" : "33333333",
            "Gross Volume for Product #5" : "444444",
            "Net Volume for Product #5" : "555555"
        }
    }
    

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
        """Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        #if not system.restore_snapshot():
        #    raise Exception

    @test
    def change_product(self):
        """Changes the Bill of Lading for a single product
        Args: None
        Returns: None
        """
        bol = bill_of_lading.BillOfLading()
        if not bol.change(self.CHNG_PROD_INFO):
            mws.recover()
            tc_fail("Failed to change the Bill Of Lading")

    @test
    def change_products(self):
        """Changes the Bill of Lading for multiple products
        Args: None
        Returns: None
        """
        bol_obj = bill_of_lading.BillOfLading()
        if not bol_obj.change(self.CHNG_PRODS_INFO):
            mws.recover()
            tc_fail("Failed to change the Bill of Lading")
        
    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        # delete pass after you implement.
        pass