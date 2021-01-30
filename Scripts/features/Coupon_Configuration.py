"""
    File name: Coupon_Configuration.py
    Tags:
    Description: Add a coupon configuration in POS and validate error message for missing field.
    Author: Paresh Rana
    Date created: 2019-08-20 11:40:00
    Python Version: 3.7
"""

import logging
import time
from app import Navi, mws, pos, system, pricing
from app.features import manufacturer_coupon
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class Coupon_Configuration():
    """
    Description: Test class that enter coupon configuration details in POS and verify missing field validation.
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
        """SL-367: Verify Coupoun Configuration can be added and verify error message for empty field.
		Performs any initialization that is not default.
        Args: None
        Returns: None
        """

    @test
    def add_coupon_configuration(self):
        """
        TestLink Id: This will add manufacturer coupon configuration details. 
        Args: None
        Returns: None
        """
        mc_info = {
             "Verify Purchase Requirement" : 'Yes',
             "Enabled" : 'Yes',
             "Host Name" : 'Host Name',
             "Host IP Address" : '1.2.3.4',
             "Host IP Port" : '5001',
             "Secondary Host IP Address" : '4.3.2.1',
             "Secondary Host IP Port" : '5002',
             "Retailer ID" : '200',
             "Store Number" : '555',
             "Connection Interval" : '5'
        }
		
        obj_mc = manufacturer_coupon.ManufacturerCoupon()
        if not obj_mc.configure(mc_info):
            tc_fail("Failled to configure Manufacturer Coupon Network", exit = True)
        
        return True
	
	@test
    def host_name_message(self):
        """
        TestLink Id: This will verify host name missing field validation. 
        Args: None
        Returns: None
        """
        mc_info = {
            "Verify Purchase Requirement" : 'Yes',
            "Enabled" : 'Yes',
            "Host Name" : '',
            "Host IP Address" : '1.2.3.4',
            "Host IP Port" : '5001',
            "Secondary Host IP Address" : '4.3.2.1',
            "Secondary Host IP Port" : '5002',
            "Retailer ID" : '200',
            "Store Number" : '555',
            "Connection Interval" : '5'
        }
        obj_mc = manufacturer_coupon.ManufacturerCoupon()
        if obj_mc.configure(mc_info):
            mws.recover()
            tc_fail("Failed to catch the Verify  error", exit = True)
        
        mws.click_toolbar("Save")
        message=mws.get_top_bar_text()
        if message == "Select Host Name \"Host Name\" cannot be blank.":
            self.log.warning("Host Name should not be blank.")
            system.takescreenshot()
        
        return True
	
	@test
	def host_ip_address_message(self):
        """
        TestLink Id: This will verify host ip address missing field validation. 
        Args: None
        Returns: None
        """
        mws.set_value("Host Name","'Host Name")
        mws.set_value("Host IP Address","")
        mws.click_toolbar("Save")
        message=mws.get_top_bar_text()
        if message == "Host IP Address(###,###,###,###) \"Host IP Address\" cannot be blank.":
            self.log.warning("Host IP Address should not be blank.")
            system.takescreenshot()

        return True
	
	@test
	def host_ip_port_message(self):
        """
        TestLink Id: This will verify host ip port missing field validation. 
        Args: None
        Returns: None
        """
        mws.set_value("Host IP Address","1.2.3.4")
        mws.set_value("Host IP Port","")
        mws.click_toolbar("Save")
        message=mws.get_top_bar_text()
        if message == "Host Port Number(####) \"Host IP  Port\" cannot be blank.":
            self.log.warning("Host IP Port should not be blank.")
            system.takescreenshot()
			
        return True
	
	@test
	def secondary_host_ip_address_message(self):
        """
        TestLink Id: This will verify secondary host ip address missing field validation. 
        Args: None
        Returns: None
        """
        mws.set_value("Host IP Port","5001")
        mws.set_value("Secondary Host IP Address","")
        mws.click_toolbar("Save")
        message=mws.get_top_bar_text()
        if message == "Secondary Host IP Address(###,###,###,###) \"Secondary Host IP Address\" cannot be blank.":
            self.log.warning("Secondary Host IP Address should not be blank.")
            system.takescreenshot()

        return True
		
	@test
	def secondary_host_ip_port_message(self):
        """
        TestLink Id: This will verify secondary host ip port missing field validation. 
        Args: None
        Returns: None
        """
         mws.set_value("Secondary Host IP Address","4.3.2.1")
        mws.set_value("Secondary Host IP Port","")
        mws.click_toolbar("Save")
        message=mws.get_top_bar_text()
        if message == "Secondary Host Port Number(####) \"Secondary Host IP  Port\" cannot be blank.":
            self.log.warning("Secondary Host IP Port should not be blank.")
            system.takescreenshot()
			
        return True
	
	@test
	def retailer_id_message(self):
        """
        TestLink Id: This will verify reatiler id missing field validation. 
        Args: None
        Returns: None
        """
        mws.set_value("Secondary Host IP Port","5002")
        mws.set_value("Retailer ID","")
        mws.click_toolbar("Save")
        message=mws.get_top_bar_text()
        if message == "Retailer ID(####) \"Retailer ID\" cannot be blank.":
            self.log.warning("Retailer Id should not be blank.")
            system.takescreenshot()
			
        return True
	
	@test
	def store_number_message(self):
        """
        TestLink Id: This will verify store number missing field validation. 
        Args: None
        Returns: None
        """
        mws.set_value("Retailer ID","200")
        mws.set_value("Store Number","")
        mws.click_toolbar("Save")
        message=mws.get_top_bar_text()
        if message == "Store Number(####) \"Store Number\" cannot be blank.":
            self.log.warning("Store Number should not be blank.")
            system.takescreenshot()
		
		mws.click_toolbar("Cancel")
        mws.click_toolbar("NO")
		
        return True
		
    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        pass
        if not system.restore_snapshot():
            raise Exception
