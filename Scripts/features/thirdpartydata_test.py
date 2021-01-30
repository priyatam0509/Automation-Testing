"""
    File name: thirdpartydata_test.py
    Tags:
    Description: 
    Author: 
    Date created: 2019-06-13 11:56:00
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import mws, system, thirdpartydata
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class thirdpartydata_test():
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
        self.tpd = thirdpartydata.ThirdPartyDataInterface()
        self.tpd_info = {
            "Options":{
                "Generate Transaction Level Detail": True,
                "ZIP Individual PJR files at store close": True,
                "Combine Transaction Level Detail Files": True,
                "ZIP Combined Transaction Level Detail Files": True,
                "Export price book when price book is imported from an external source": True,
                "Export price book on a nightly basis": True,
                "Copy inbound Item List, Combo And Match files": True,
                "Wetstock Export Enabled": True,
                "Export meters by grade": True,
                "Export meters by dispenser": True,
                "Export Fuel Prices Every 30 Minutes": True,
                "Copy end of period XML summary files": True
            },
            "FTP Options":{
                "Host Desc Test": {
                    "Host Description": "Host Desc Test",
                    "Host Address": "Address Test",
                    "Host Port": "7777",
                    "User Name": "User Name Test",
                    "Password": "password",
                    "FTP Folder": "Folder Test",
                    "Use Secure FTP": True,
                    "Send PJR Data": True,
                    "Send Price Book Data": True,
                    "Send Wetstock Data": True,
                    "Send EOP XML Data": True,
                    "Send Fuel Price Data": True
                },
                "Host Desc Test 2": {
                    "Host Description": "Host Desc Test 2",
                    "Host Address": "Address Test",
                    "Host Port": "7777",
                    "User Name": "User Name Test",
                    "Password": "password",
                    "FTP Folder": "Folder Test",
                    "Use Secure FTP": True,
                    "Send PJR Data": True,
                    "Send Price Book Data": True,
                    "Send Wetstock Data": True,
                    "Send EOP XML Data": True,
                    "Send Fuel Price Data": True
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
        
        self.tpd.navigate_to()
        mws.connect("third party data interface")


    @test
    def thirdpartydata_configure(self):
        """ Tests whether the Third Party Data Interface can be set up.
        Args: None
        Returns: None
        """
        if not self.tpd.configure(self.tpd_info):
            tc_fail("Could not configure Third Party Data Interface correctly...")

    @test
    def hostdesc_delete(self):
        """ Tests whether a specified Host Description can be deleted.
        Args: None
        Returns: None
        """
        self.tpd.navigate_to()
        if not self.tpd.delete("Host Desc Test"):
            tc_fail(f"Could not delete specified Host Description.")


    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        # delete pass after you implement.
        pass