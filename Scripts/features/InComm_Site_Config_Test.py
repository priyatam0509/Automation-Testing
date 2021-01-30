"""
    File name: InComm_Site_Config_Test.py
    Tags:
    Description: Tests incomm_site.SiteConfiguration module
    Author: Alex Rudkov
    Date created: 2019-07-02 13:37:19
    Date last modified: 
    Python Version: 3.7
"""

import logging, random, time
from app import Navi, mws, pos, system, incomm_site
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class InComm_Site_Config_Test():
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
    def test_case_1(self):
        """Configures the Site Configuration with invalid dictionary
        Args: None
        Returns: None
        """
        sc = incomm_site.SiteConfiguration()

        # Invalid params
        params = {
            "Primary Host IP Address": "1", # Invalid ip
            "Primary Host IP Port": "5001",
            "Site ID": "00000",
            "Merchant/Retailer ID": "123456789",
            "Print store copy of the receipt inside": "Yes", # Or 'No'
            "Print customer copy of the receipt inside": "Yes", # Or 'No'
        }

        # Shuffle params keys
        keys = list(params.keys())
        temp = {}
        random.shuffle(keys)
        for key in keys:
            temp[key] = params[key]
        params = temp

        self.log.info("Configuring the SC with invalid ip config that causes an error message")
        if sc.setup(params):
            tc_fail("The Site Configuration was configured successfully when failure was expected.")
        mws.recover()

        time.sleep(2)
        sc.navigate_to()

        # Invalid params
        params = {
            "Primary Host IP Address": "127.0.0.1", # Invalid ip
            "Primary Host IP Port": "0",
            "Site ID": "00000",
            "Merchant/Retailer ID": "123456789",
            "Print store copy of the receipt inside": "Yes", # Or 'No'
            "Print customer copy of the receipt inside": "Yes", # Or 'No'
        }

        # Shuffle params keys
        keys = list(params.keys())
        temp = {}
        random.shuffle(keys)
        for key in keys:
            temp[key] = params[key]
        params = temp

        self.log.info("Configuring the SC with invalid port config that causes an error message")
        if sc.setup(params):
            tc_fail("The Site Configuration was configured successfully when failure was expected.")
        mws.recover()

        time.sleep(2)
        sc.navigate_to()

        # Invalid params
        params = {
            "Primary Host IP Address": "127.0.0.1", # Invalid ip
            "Primary Host IP Port": "5001",
            "Site ID": "",
            "Merchant/Retailer ID": "123456789",
            "Print store copy of the receipt inside": "Yes", # Or 'No'
            "Print customer copy of the receipt inside": "Yes", # Or 'No'
        }

        # Shuffle params keys
        keys = list(params.keys())
        temp = {}
        random.shuffle(keys)
        for key in keys:
            temp[key] = params[key]
        params = temp

        self.log.info("Configuring the SC with empty Site ID that causes an error message")
        if sc.setup(params):
            tc_fail("The Site Configuration was configured successfully when failure was expected.")
        mws.recover()

        time.sleep(2)
        sc.navigate_to()

        # Invalid params
        params = {
            "Primary Host IP Address": "127.0.0.1", # Invalid ip
            "Primary Host IP Port": "5001",
            "Site ID": "00000",
            "Merchant/Retailer ID": "",
            "Print store copy of the receipt inside": "Yes", # Or 'No'
            "Print customer copy of the receipt inside": "Yes", # Or 'No'
        }

        # Shuffle params keys
        keys = list(params.keys())
        temp = {}
        random.shuffle(keys)
        for key in keys:
            temp[key] = params[key]
        params = temp

        self.log.info("Configuring the SC with empty Retailer ID that causes an error message")
        if sc.setup(params):
            tc_fail("The Site Configuration was configured successfully when failure was expected.")
        mws.recover()
    
    @test
    def test_case_2(self):
        """Configures the Site Configuration with valid dictionary
        Args: None
        Returns: None
        """
        sc = incomm_site.SiteConfiguration()

        # Valid params
        params = {
            "Primary Host IP Address": "127.0.0.1", # Invalid ip
            "Primary Host IP Port": "5001",
            "Site ID": "00000",
            "Merchant/Retailer ID": "123456789",
            "Print store copy of the receipt inside": "No", # Or 'No'
            "Print customer copy of the receipt inside": "No", # Or 'No'
        }

        # Shuffle params keys
        keys = list(params.keys())
        temp = {}
        random.shuffle(keys)
        for key in keys:
            temp[key] = params[key]
        params = temp

        self.log.info("Configuring the SC with valid config")
        if not sc.setup(params):
            tc_fail("Failed to configure the Site Configuration.")

        # Check
        time.sleep(2)
        sc.navigate_to()

        error = False
        for field, value in params.items():
            set_value = mws.get_value(field)
            if field == "Print store copy of the receipt inside" or field == "Print customer copy of the receipt inside":
                set_value = set_value[0]

            if set_value != value:
                self.log.error(f"The field '{field}' was set successfully, but upon check had value '{set_value}' when '{value}' was expected")
                error = True
        if error:
            tc_fail("The test failed a check after configuration")
        mws.recover()

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        # delete pass after you implement.
        pass