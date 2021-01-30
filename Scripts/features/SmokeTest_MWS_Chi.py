"""
    File name: SmokeTest_MWS_Chi.py
    Tags:
    Description: Basic MWS Configuration tests. Written as a basic smoke test against Passport
    Author: Conor McWain
    Date created: 2019-09-10
    Date last modified: 
    Python Version: 3.7
"""

import logging, json, time

from app import carwash, crindsim, employee, forecourt_installation
from app import network_site_config, item, tax_maint
from app import initial_setup, mws, Navi, pinpad, server, system, tender
from app.framework import EDH
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app.util import constants
from test_harness import site_type

class SmokeTest_MWS_Chi():
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
        self.IS = initial_setup.Initial_setup(site_type)
        self.config_info = {
            "Car Wash":{
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
                        "Total Price":"5.00"
                    }
                }
            },
            "Item":{
                "General":{
                    "PLU/UPC":"57355",
                    "Description": "Smoke Test",
                    "Department": "Dept 1",
                    "This item sells for": True,
                    "per unit": "5.00"
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
                "Tender Code": "6",
                "Tender Description": "EBT Food",
                "General":{
                    "Receipt Description": "EBT Food",
                    "Tender Button Description": "EBT Food"
                },
                "Register Groups": {
                    "POSGroup1": {
                        "Loans": True
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
        self.IS.feature_activate(site_type)
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
    def configure_carwash(self):
        """
        Configure Car Wash Maintenance
        """
        cw_info = self.config_info["Car Wash"]

        self.log.debug('Navigating to: CarWash Maintenance')
        Navi.navigate_to('Car Wash Maintenance')
        cw = carwash.CarWashMaintenance()

        self.log.debug('Configuring Car Wash Maintenance')
        if not cw.add(cw_info):
            tc_fail("Failed to configure the car wash")

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
        mws.click_toolbar("Exit", 10, True)

    @test
    def network_config(self):
        """
        Edit Network Configuration
        """
        self.IS.setup_network()
        if "HPS-DALLAS" not in system.get_brand().upper():
            if not self.IS.pdl():
                self.log.error("There was an issue with the PDL")
                tc_fail("Failed to get a PDL")

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
        mws.click_toolbar("Save", True)
        
    @test
    def tax_maintenance(self):
        """
        Edit Tax Maintenance
        """
        tax_info = self.config_info["Tax"]

        self.log.debug('Navigating to: Tax Maintenance')
        TM = tax_maint.TaxMaintenance()
        
        self.log.debug('Configuring the taxes')
        # configure(self, config)
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
        # configure(self, tender_name, config, active = None)
        if not TM.configure("EBT Food", tender_info, True):
            tc_fail("Failed to configure the tenders")
        mws.click_toolbar("Exit", 10, True)

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        pass