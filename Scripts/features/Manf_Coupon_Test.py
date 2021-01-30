"""
    File name: Manf_Coupon_Test.py
    Tags:
    Description: Tests the Store Close report
    Author: Conor McWain
    Date created: 2019-06-27 14:15:56
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import Navi, mws, pos, system
from app.features import manufacturer_coupon
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class Manf_Coupon_Test():
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
        """Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        # if not system.restore_snapshot():
        #     raise Exception

    @test
    def add_manf_coupon(self):
        """Add a Manufacturer Coupon Network Configuration
        Args: None
        Returns: None
        """
        mc_info = {
            "Verify Purchase Requirement": 'Yes',
            "Enabled": 'Yes',
            "Host Name": 'Host Name',
            "Host IP Address": '1.2.3.4',
            "Host IP Port": '5001',
            "Secondary Host IP Address": '4.3.2.1',
            "Secondary Host IP Port": '5002',
            "Retailer ID": '200',
            "Store Number": '555',
            "Connection Interval": '5'
        }
        mc = manufacturer_coupon.ManufacturerCoupon()
        if not mc.configure(mc_info):
            tc_fail("Failed to configure Manufacturer Coupon Network", exit = True)

    @test
    def verify_error(self):
        """Test the error message handling for bad config
        Args: None
        Returns: None
        """
        mc_info = {
            "Verify Purchase Requirement": 'No',
            "Enabled": 'Yes'
        }
        mc = manufacturer_coupon.ManufacturerCoupon()
        if mc.configure(mc_info):
            mws.recover()
            tc_fail("Failed to catch the Verify Purchase error")
        else:
            mws.recover()

    @test
    def missing_field(self):
        """Test the error message handling for missing fields
        Args: None
        Returns: None
        """
        mc_info = {
            "Verify Purchase Requirement": 'Yes',
            "Enabled": 'Yes',
            "Host Name": 'Host Name',
            "Host IP Address": '1.2.3.4',
            "Host IP Port": '',
            "Secondary Host IP Address": '4.3.2.1',
            "Secondary Host IP Port": '5002',
            "Retailer ID": '200',
            "Connection Interval": '5'
        }
        mc = manufacturer_coupon.ManufacturerCoupon()
        if mc.configure(mc_info):
            mws.recover()
            tc_fail("Failed to catch the missing field error")
        else:
            mws.recover()

    @test
    def change_manf_coupon(self):
        """Change the Manufacturer Coupon Network Configuration
        Args: None
        Returns: None
        """
        mc_info = {
            "Enabled": 'Yes',
            "Host Name": 'Edit Name',
            "Host IP Address": '2.3.4.5',
            "Host IP Port": '1005',
            "Secondary Host IP Address": '5.6.7.8',
            "Secondary Host IP Port": '2005',
            "Connection Interval": '15'
        }
        mc = manufacturer_coupon.ManufacturerCoupon()
        if not mc.configure(mc_info):
            mws.recover()
            tc_fail("Could not change configuration")

    @test
    def disable_manf_coupon(self):
        """Disable the Manufacturer Coupon Network Configuration
        Args: None
        Returns: None
        """
        mc_info = {
            "Enabled": 'No'
        }
        mc = manufacturer_coupon.ManufacturerCoupon()
        if not mc.configure(mc_info):
            mws.recover()
            tc_fail("Could not disable Manufacturer Coupon Network")

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        # delete pass after you implement.
        pass