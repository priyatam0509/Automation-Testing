"""
    File name: pricinggroup_test.py
    Tags:
    Description: 
    Author: 
    Date created: 2019-06-05 15:19:22
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import mws, pos, system, pricing_grp
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class pricinggroup_test():
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

        self.pg_info = {
            "Pricing Group":"Test Pricing Group (EDITED)", #Changes name of group
            "Pricing":{
                "Increase Price": True,
                # "Decrease Price": True,
                "amount per unit": "1.00",
                "Change tax group to": "No Tax"
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
        
        self.pg = pricing_grp.PricingGroup()
        self.pg.navigate_to()

    @test
    def add_pricinggroup(self):
        """Tests whether a pricing group can be created
        Args: None
        Returns: True or False
        """

        self.pg.add("Test Pricing Group")

    @test
    def apply_pricinggroup(self):
        """Tests whether a pricing group can be applied to an item group
        Args: None
        Returns: True or False
        """

        self.pg.apply("Test Pricing Group",self.pg_info)

    @test
    def delete_pricinggroup(self):
        """Tests whether a pricing group can be deleted
        Args: None
        Returns: True or False
        """

        self.pg.delete("Test Pricing Group (EDITED)")

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        # delete pass after you implement.
        pass