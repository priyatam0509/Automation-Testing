"""
    File name: carwash_test.py
    Tags:
    Description: 
    Author: 
    Date created: 2019-06-10 16:25:59
    Date last modified: 
    Python Version: 3.7
"""

import logging, time
from app import mws, system, carwash
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class carwash_test():
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
        self.cw_info = {
            "Site":{
                "Type of Car Wash":"Unitec Ryko Emulation",
                "Disable Car Wash": False,
                "Car Wash PLU":"1234",
                "Rewash PLU":"5678",
                "Receipt Footer 1":"Footer #1",
                "Receipt Footer 2":"Footer #2",
                "Print expiration date on customer receipt": True,
                "Default Expiration": "30"
            },
            "Packages":{
                "Carwash 1":{ 
                    "Package Name":"Carwash 1",
                    "Total Price":"5.00",
                    "Tax amount included in package price": True,
                    "Tax amount included in package price edit": "0.50",
                },
                "Carwash 2":{ 
                    "Package Name":"Carwash 2",
                    "Total Price":"5.00",
                    "Tax amount included in package price": True,
                    "Tax amount included in package price edit": "0.50",
                }
            },
            "Discount":{
                "Discount Available": True,
                "Apply Discounts On Prepays": False,
                "New Discount": {
                    "Discount Name": "Supreme Discount",
                    "Service Levels":"Service Levels Select All",
                    "Grades":"Grades Select All",
                    "Packages":"Packages Select All",
                    "When the fuel purchase amount reaches": True,
                    "When the fuel purchase amount reaches edit": "50.00",
                    "Car wash will be discounted by": "5.00",
                }
            }
        }

        self.cw_info_edited = {
            "Site":{
                "Type of Car Wash":"Kesseltronics",
                "Disable Car Wash": False,
                "Car Wash PLU":"6789",
                "Rewash PLU":"4321",
                "Receipt Footer 1":"Footer #1 Edited",
                "Receipt Footer 2":"Footer #2 Edited",
                "Print expiration date on customer receipt": True,
                "Default Expiration": "15"
            },
            "Packages":{
                "Carwash 1":{ 
                    "Package Name":"Carwash 1 (Edited)",
                    "Total Price":"25.00",
                    "Tax amount included in package price": True,
                    "Tax amount included in package price edit": "2.50",
                },
                "Carwash 2":{ 
                    "Package Name":"Carwash 2 (Edited)",
                    "Total Price":"25.00",
                    "Tax amount included in package price": True,
                    "Tax amount included in package price edit": "2.50",
                }
            },
            "Discount":{
                "Discount Available": True,
                "Apply Discounts On Prepays": False,
                "Supreme Discount": {
                    "Service Levels":"Service Levels Select All",
                    "Grades":"Grades Select All",
                    "Packages":"Packages Select All",
                    "When the fuel purchase amount reaches": True,
                    "When the fuel purchase amount reaches edit": "25.00",
                    "Car wash will be discounted by": "2.50"
                }
            }
        }

    @setup
    def setup(self):
        """Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        # if not system.restore_snapshot():
        #     raise Exception
        self.cw = carwash.CarWashMaintenance()

    @test
    def add_carwash(self):
        """Tests whether a car wash can be added with new info
        Args: None
        Returns: None
        """
        self.cw.navigate_to()
        if not self.cw.add(self.cw_info):
            tc_fail("Could not add carwash")
        time.sleep(3)
        

    @test
    def change_carwash(self):
        """Tests whether the fields of a car wash can be changed once saved
        Args: None
        Returns: None
        """
        self.cw.navigate_to()
        if not self.cw.change(self.cw_info_edited):
            tc_fail("Could not change carwash")
        time.sleep(3)

    @test
    def delete_carwash(self):
        """Tests whether packages and discounts can be deleted
        Args: None
        Returns: None
        """
        packages = ["Carwash 1 (Edited)","Carwash 2 (Edited)"]
        discounts = "Supreme Discount"
        self.cw.navigate_to()
        if not self.cw.delete(packages,discounts):
            tc_fail("Could not delete carwash packages and discounts")

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        # delete pass after you implement.
        pass