"""
    File name: multi_mobile_payment_test.py
    Tags:
    Description: Test Multiple Mobile Payment Feature
    Author: 
    Date created: 2020-20-01 15:38:21
    Date last modified: 2020-30-01 15:38:21
    Python Version: 3.7
"""

import logging, time
from app import Navi, mws, pos, system
from app.features import mobile_payment,fuel_discount_maint,feature_activation
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class multi_mobile_payment_test():
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
    @setup
    def setup(self):
        """Instantiates the Fuel Discount Maintenance class and adds a new "testdiscount"
        so the rest of mobile_payment_test.py can run correctly.
        Args: None
        Returns: None
        """
        # if not system.restore_snapshot():
        #     raise Exception
        #Set the features to activate
        DEFAULT_MOBILE = ["Base Passport", "Enhanced Store", "Enhanced Reporting", "Advanced Merchandising",
                    "Employee Management", "Enhanced Card Services", "Enhanced Loyalty Interface",
                    "Multiple Loyalty Interface", "Mobile Payment",
                    "Prepaid Card Services", "Windows 10 License", "Car Wash"]
        
        
        #Instatiate Feature Activation
        FA = feature_activation.FeatureActivation()
        
        # Activate defined Features
        if not FA.activate(DEFAULT_MOBILE, mode="Passport Individual Bundles"):
            return False
        

        self.fdm = fuel_discount_maint.FuelDiscountMaintenance()
        fdm_info = {
            "Discount Group Name" : "Discount 1",
            "Grades" : {
                "Regular" : "0.100"
            }
        }

        self.fdm.add("Fuel Discount Groups", fdm_info)
    
    @test
    def config_mmpcexxon(self):
        """
        whether the fields in the Multiple mobile Payment Configuration menu can be added.
        Args: None
        Returns: None
        """

        mpc_info = {
            "Mobile Provider Name":'SpeedPass+',
            "General": {
                "Page 1": {
                    "Provider Name": "SpeedPass+",
                    "Site ID": "EXXONMOBIL_GVR_US",
				    "Host Address": "204.194.139.242",
				    "Port Number": "9060",
				    "Schema Version": "1.0",
                    "Enabled": "No"
                }
            }
	    }
        brand = system.get_brand
        self.mpc = mobile_payment.MobilePaymentConfiguration()
        if (brand == 'EXXON' or 'EXXONMobil'):
            mws.sign_on
            if not self.mpc.check_values(mpc_info):
                mws.recover
                tc_fail("Failed while checking Mobile Payment Config.")
        mws.click_toolbar("exit",timeout=10)

    @test
    def config_mmpc(self):
        """
        Tests whether the fields in the Multiple mobile Payment Configuration menu can be added. 
        Args: None
        Returns: None
        """
        mws.sign_on
        Navi.navigate_to("mws")
        self.mpc = mobile_payment.MobilePaymentConfiguration()
        QR_list = ["testQR7"]
		    
        mpc_info = {
            "Mobile Provider Name":'Stuzo',
            "General": {
                "Page 1": {
                    "Provider Name": "Stuzo",
				    "Enabled": "Yes",
				    "Merchant ID": "0146-2380",
				    "Site ID": "01462380",
				    "Host Address": "10.28.120.62",
				    "Port Number": "9052",
				    "Settlement Software Version": "1",
				    "Settlement Passcode": "Passcode",
				    "Settlement Employee": "Employee",
				    "Schema Version": "2.0"
                },
                "Page 2": {
                    "Use TLS": "Yes",
                    "OCSP Mode": "Strict",
                    "TLS Certificate Name": "TLSCertificateName"
                 }
		    },
		    "Local Fuel Discounts": {
			    "Mobile Local Discount Code": "Provider Automated",
			    "Mobile Local Discount Description": "test Automated",
			    "Fuel Discount Group": "Discount 1"
		    }
	    }

        if not self.mpc.configure(mpc_info,"Discount 1",QR_list, EMVCo_QR= "Yes"):
            mws.recover
            tc_fail("Failed while configuring Mobile Payment Config menu.")
        mws.click_toolbar("exit",timeout=10)

    @test
    def config_mmpcsamename(self):
        """
        Tests whether can't be configure a two mobile providers with same name 
        Args: None
        Returns: None
        """
        Navi.navigate_to("mws")
        mws.sign_on
        self.mpc = mobile_payment.MobilePaymentConfiguration()
		    
        mpc_info = {
            "Mobile Provider Name":'Stuzo',
            "General": {
                "Page 1": {
                    "Provider Name": "Stuzo",
				    "Enabled": "Yes",
				    "Merchant ID": "0146-2380",
				    "Site ID": "01462380",
				    "Host Address": "10.28.120.62",
				    "Port Number": "9052",
				    "Settlement Software Version": "1",
				    "Settlement Passcode": "Passcode",
				    "Settlement Employee": "Employee",
				    "Schema Version": "2.0"
                },
                "Page 2": {
                    "Use TLS": "Yes",
                    "OCSP Mode": "Strict",
                    "TLS Certificate Name": "TLSCertificateName"
                 }
		    }
	    }

        if not self.mpc.configure(mpc_info, EMVCo_QR= "Yes"):
            mws.recover
        mws.click_toolbar("exit",timeout=10)

    @test
    def config_mmpc2(self):
        """
        Tests whether a Second Mobile Provider Can be configured
        Args: None
        Returns: None
        """
        self.mpc = mobile_payment.MobilePaymentConfiguration()      
        mpc_info= {
            "Mobile Provider Name":'ZipLine',
            "General": {
                "Page 1": {
                    "Provider Name": "Paypal",
                    "Enabled": "Yes",
                    "Merchant ID": "0146-2380",
				    "Site ID": "01462380",
				    "Host Address": "10.28.120.62",
				    "Port Number": "9052",
				    "Settlement Software Version": "1",
				    "Settlement Passcode": "Passcode",
				    "Settlement Employee": "Employee",
				    "Schema Version": "2.0"
                },
                "Page 2": {
                    "Use TLS": "Yes",
                    "OCSP Mode": "Strict",
                    "TLS Certificate Name": "TLSCertificateName"
                 }
		    }
	    }
        if not  self.mpc.configure(mpc_info, EMVCo_QR= "Yes"):
            mws.recover()
            tc_fail("Failed while configuring Mobile Payment Config menu a second time.")
        mws.click_toolbar("exit",timeout=2)   
    @test
    def change_mmpc(self):
        """
        Tests whether the fields in the Mobile Payment Configuration menu can be changed. In this case, the functionality that forces "Enabled" to be set first is tested, as well as the logic that changes the EMVCo_QR variable from True to "Yes" within the code.
        Args: None
        Returns: None
        """

        self.mpc = mobile_payment.MobilePaymentConfiguration()

        Navi.navigate_to("mws")
        mws.sign_on
        
        mpc_info= {
            "General": {
                "Page 1": {
                    "Provider Name": "Zipline",
				    "Enabled": "No"
                }
            }
		}
        if not  self.mpc.change_provider(mpc_info,"Paypal", EMVCo_QR= "No"):
            mws.recover()
            tc_fail("Failed while changing Mobile Payment Config menu.")
        mws.click_toolbar("exit",timeout=10)

    @test
    def config_mmpforreports(self):
        """
        Tests
        Args: None
        Returns: None
        """
        self.mpc = mobile_payment.MobilePaymentConfiguration()      
        mpc_info= {
            "Mobile Provider Name":'Paypal',
            "General": {
                "Page 1": {
                    "Provider Name": "Paypal",
                    "Enabled": "Yes",
                    "Merchant ID": "0146-2380",
				    "Site ID": "01462380",
				    "Host Address": "10.28.120.24",
				    "Port Number": "9053",
				    "Settlement Software Version": "1",
				    "Settlement Passcode": "Passcode",
				    "Settlement Employee": "Employee",
				    "Schema Version": "2.0"
                },
                "Page 2": {
                    "Use TLS": "Yes",
                    "OCSP Mode": "Strict",
                    "TLS Certificate Name": "TLSCertificateName"
                 }
		    }
        }
        if not  self.mpc.configure(mpc_info, EMVCo_QR= "Yes"):
            mws.recover()
            tc_fail("Failed while configuring Multiple Mobile Payment")
        mws.click_toolbar("exit",timeout=10)

    @test
    def Delete_mmpc(self):
        """
        Tests whether the Mobile Provider can be Deleted.
        Args: None
        Returns: None
        """
        self.mpc = mobile_payment.MobilePaymentConfiguration()

        if not  self.mpc.delete_provider("Zipline"):
            mws.recover()
            tc_fail("Failed while deleteing Mobile Payment Config .")
        mws.click_toolbar("exit")
    @test
    def Delete_mmpc2(self):
        """
        Tests whether the Mobile Provider can't be deleted when field enabled on yes.
        Args: None
        Returns: None
        """
        self.log.debug("Allowing 10 seconds to load MWS...")
        self.mpc = mobile_payment.MobilePaymentConfiguration()

        self.mpc.delete_provider("Stuzo")
        mws.click_toolbar("exit",timeout=5)
    
    @test
    def Delete_QR(self):
        """
        Tests whether the QR codes in the Mobile Payment Configuration menu can be deleted.
        Args: None
        Returns: None
        """

        self.mpc = mobile_payment.MobilePaymentConfiguration()
        QR_list = ["testQR7"]
        
        if not  self.mpc.deleteQr(QR_list,"Stuzo"):
            mws.recover()
            tc_fail("Failed while deleteing Mobile Payment QR code .")
        mws.click_toolbar("exit",timeout=10)
    
    @test
    def Delete_discount(self):
        """
        Tests whether the Local fuel discounts in the Mobile Payment Configuration menu can be deleted.
        Args: None
        Returns: None
        """
 
        self.mpc = mobile_payment.MobilePaymentConfiguration()
        delete_list = ["Provider Automated"]
        
        if not  self.mpc.deleteDiscount(delete_list,"Stuzo"):
            mws.recover()
            tc_fail("Failed while deleteing Mobile Payment Discount .")
        mws.click_toolbar("exit",timeout=10)

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        "s""

        if not system.restore_snapshot():
            self.log.debug("No snapshot to restore, if this is not expected please contact automation team")

        """