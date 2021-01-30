"""
    File name: SmokeTest_MWS_Edge_Con.py
    Tags:
    Description: Basic MWS Configuration tests. Written as a basic smoke test against Edge
    Author: Conor McWain
    Date created: 2019-09-26
    Date last modified: 
    Python Version: 3.7
"""

import logging, json

from app import crindsim, employee, forecourt_installation, network_site_config
from app import item, tax_maint
from app import initial_setup, mws, Navi, pinpad, server, system, tender
from app.framework import EDH
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app.util import constants

class SmokeTest_MWS_Edge_Con():
    """
    Description: Test class that provides an interface for testing.
    """

    def __init__(self):
        """
        Initializes the Template class.
        """
        # The logging object. 
        # Example: self.log.info(f"Current value of var: {my_var}")
        self.log = logging.getLogger()
        self.brand = system.get_brand().upper()
        self.IS = initial_setup.Initial_setup("edge")
        self.config_info = {
            "Item":{
                "General":{
                    "PLU/UPC":"57355",
                    "Description": "Smoke Test",
                    "Department": "Dept 1",
                    "This item sells for": True,
                    "per unit": "5.00"
                },
                "Scan Codes": {
                    "Add": ["893594002075"],
                    "Expand UPCE": True
                },
                "Options":{
                    "Return Price": "5.00",
                    "Food Stampable": True
                }
            },
            "Forecourt":{
                "Pump Protocol": "Gilbarco CRIND",
                "IP Address check box": True,
                "IP Address": "1.2.3.4"
            },
            "Tax":{
                "Rates":{
                    "NC Sales":{
                        "Name": "NC Sales",
                        "Receipt Description": "NC Tax",
                        "Percent": "10"
                    }
                }
            },
            "Tender":{
                "Tender Code": "4",
                "Tender Description": "Debit",
                "Register Groups": {
                    "POSGroup1": {
                        "Refunds": True
                    }
                }
            }
        }

    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        """
        edh = EDH.EDH()
        self.IS.feature_activate("Edge")
        edh.enable_security()
        edh.setup()
        crindsim.setup_edh(4, server.server.get_site_info()['ip'])
 
    @test
    def register_setup(self):
        """
        Add a Register
        """
        self.IS.configure_register()

    @test
    def add_employee(self):
        """
        Add an Employee
        """
        self.IS.add_employee()

    @test
    def add_item(self):
        """
        Add an Item
        """
        item_info = self.config_info["Item"]

        self.log.debug('Navigating to: Item')
        Item = item.Item()
        
        self.log.debug('Adding the Item')
        #TODO This doesn't check for errors after you save
        if not Item.add(item_info):
            tc_fail(f"Failed to add the item")
        mws.click_toolbar("Exit", 10)

    @test
    def network_config(self):
        """
        Edit Network Configuration
        """
        with open(constants.STANDARD_NETWORK, 'r') as fp:
            network_json = json.load(fp)

        ntwrk = network_json[self.brand]

        #list(ntwrk.keys())[0] = "Network Site Configuration" or "Global Info Editor"
        self.log.debug('Navigating to: '+list(ntwrk.keys())[0])
        N = network_site_config.NetworkSetup()

        self.log.debug('Configuring the Network')
        if not N.configure_network(config=ntwrk[list(ntwrk.keys())[0]]):
            tc_fail("Failed to configure the Network")
        if "HPS-DALLAS" not in self.brand:
            if not self.IS.pdl():
                tc_fail("There was an issue with the PDL")

    @test
    def forecourt_maint(self):
        """
        Edit Forecourt Installation
        """
        forecourt_info = self.config_info["Forecourt"]

        self.log.debug('Navigating to: Forecourt Installation')
        Navi.navigate_to('Forecourt Installation')
        FC = forecourt_installation.ForecourtInstallation()
        mws.click("Set Up")
        
        self.log.debug('Configuring the dispenser')
        if not FC.change("1", "Dispensers", forecourt_info):
            tc_fail("Failed to configure the dispenser")
        mws.click_toolbar("Save")
        mws.click_toolbar("Save")
        
    @test
    def tax_maint(self):
        """
        Edit Tax Maintenance
        """
        tax_info = self.config_info["Tax"]

        self.log.debug('Navigating to: Tax Maintenance')
        TM = tax_maint.TaxMaintenance()
        
        self.log.debug('Configuring the taxes')
        if not TM.configure(tax_info):
            tc_fail("Failed to configure the taxes")

    @test
    def tender_maint(self):
        """
        Edit Tender Maintenance
        """
        tender_info = self.config_info["Tender"]

        self.log.debug('Navigating to: Tender Maintenance')
        TM = tender.TenderMaintenance()
        
        self.log.debug('Configuring the tenders')
        if not TM.configure("Debit", tender_info, True):
            tc_fail("Failed to configure the tenders")
        mws.click_toolbar("Exit", 10)

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        pass