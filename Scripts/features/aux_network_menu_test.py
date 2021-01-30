"""
    File name: aux_network_menu_test.py
    Tags:
    Description: 
    Author: 
    Date created: 2019-07-03 11:03:49
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import mws, system, aux_network_card, aux_network_site
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class aux_network_menu_test():
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

        self.ansc_info = {
            "Com Port": "1",
            "Baud Rate": "9600",
            "Data bits": "4", # cannot be less than 4 or exceed 8
            "Stop Bit": "2",
            "Parity Bit": "No Parity",
            "ACK Timer": "5000", #cannot be 0
            "Response Timer": "60000",
            "NAK Quantity": "5",
            "Comm Test Timer Polling": "10000",
            "Site ID": "123456789",
            "Print store copy of the receipt inside": "Yes",
            "Print customer copy of the receipt inside": "No"
        }
        self.ancc_info = {
            "Issuer_Name_1": {
                "ISO Number": "123",
                "Print Account Number On Aux Network Sales Report": "No",
                "Beginning Position of Account Number": "0",
                "Number of Characters in Account Number": "1",
                "Discount Group": "NONE"
            },
            "Issuer_Name_2": {
                "ISO Number": "456"
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

    @test
    def configure_ansc(self):
        """Verifies the fields of the Auxiliary Network Site Configuration feature module can be set correctly.
        Args: None
        Returns: None
        """
        ansc = aux_network_site.AuxiliaryNetworkSiteConfig()
        if not ansc.configure(self.ansc_info):
            tc_fail("Failed while configuring Auxiliary Network Site Config.")
            mws.recover()

    @test
    def configure_ancc(self):
        """Verifies the fields of the Auxiliary Network Card Configuration feature module can be set correctly.
        Args: None
        Returns: None
        """
        self.ancc = aux_network_card.AuxiliaryNetworkCardConfig()
        if not self.ancc.configure(self.ancc_info):
            tc_fail("Failed while configuring Auxiliary Network Card Config.")
            mws.recover()
    
    @test
    def ancc_delete_issuers(self):
        """Verifies the fields of the Auxiliary Network Card Configuration feature module can be set correctly.
        Args: None
        Returns: None
        """
        self.ancc.navigate_to()
        if not self.ancc.delete(["Issuer_Name_1","Issuer_Name_2"]):
            tc_fail("Failed while deleting issuers.")
            mws.recover()

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        # delete pass after you implement.
        pass