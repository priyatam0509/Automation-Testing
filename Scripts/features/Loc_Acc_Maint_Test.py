"""
    File name: Loc_Acc_Maint_Test.py
    Tags:
    Description: Tests AccountsMaintenance module
    Author: Alex Rudkov
    Date created: 2019-06-14 14:16:09
    Date last modified: 
    Python Version: 3.7
"""

import logging, time, math
from app import Navi, mws, pos, system
from app.framework.tc_helpers import setup, test, teardown, tc_fail

from app.features import accounts_maint

class Loc_Acc_Maint_Test():
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
        self.account_ids = []
        self.change_old_id_1 = None
        self.change_old_id_2 = None

    @setup
    def setup(self):
        """Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        # if not system.restore_snapshot():
        #     raise Exception
        pass

    @test
    def test_case_1(self):
        """Tests search functionality. Normal flow
        Args: None
        Returns: None
        """
        accounts_maint.AccountsMaintenance.navigate_to()
        am = accounts_maint.AccountsMaintenance()

        am_info = {
            "Local Accounts Option - Store Copy of receipt": True,
            "Local Accounts Option - Customer copy of receipt": False,
            "Account ID": "1",
            "Account Name": "DG, Inc.",
            "Taxation Number": "1234",
        }

        if am.search(am_info):
            tc_fail("Searching for accounts with unsupported parameters should have failed but it did not.")

        # Recovered. Navigate back
        accounts_maint.AccountsMaintenance.navigate_to()
        am = accounts_maint.AccountsMaintenance()

        am_info = {
            "Account ID": "1",
            "Account Name": "DG, Inc.",
            "Taxation Number": "1234",
        }

        if not am.search(am_info):
            tc_fail("Failed to search for accounts with valid parameters.")

        am_info = {}
        if not am.search(am_info):
            tc_fail("Failed to search for all acounts with empty dictionary of parameters.")

        am_info = {
            "Account ID" : "4"
        }

        if am.search(am_info):
            tc_fail("Searching for account with non-existant id should have failed but it did not.")
        
        mws.recover()
        
    @test
    def test_case_2(self):
        """Tests add functionality. Normal flow
        Args: None
        Returns: None
        """
        accounts_maint.AccountsMaintenance.navigate_to()
        am = accounts_maint.AccountsMaintenance()
        acc_id = str(math.floor(time.time() % 10000000000)) # 10 digit unique id
        self.account_ids.append(acc_id)
        self.change_old_id_1 = acc_id

        am_info = {
            "General": {
                "Account ID":acc_id,
                "Account Name":"Test Account",
                "A warning message should display if the customer's account balance reaches":"120.00",
                "Account Credit Limit":"700.00",
                "Account Type":"Card Based",
                "Enable All Cards":True,
                "Disable All Cards":False
            },
            "Address": {
                "Street":"Friendly St.",
                "City":"Wrong",
                "State":"Different",
                "Country":"This",
            },
            "Card Accounts": {
                "Card Data is On":"Track 1",
                "Issuer Number Start Position":"1",
                "Account Number Start Position":"2",
                "Account Number Range Start":"1",
                "Account Number Range End":"2",
                "Issuer Number":"1231231231231231231231231",
                "CRIND Authorization Amount":"5.00"
            },
            "Prompt Options": {
                "Prompt 1 Start Position": "1",
                "Prompt 1 Value": "45",
                "Prompt 1" : {
                    "ID" : True,
                    "Odometer" : False,
                    "Driver ID" : True,
                    "Custom" : True
                }
            },
            "Customize Prompt": {
                "Customer Prompt Text ID": "Text ID",
                "Customer Prompt Text Odometer": "Text Odo",
                "Customer Prompt Text Vehicle #": "Text Vehicle #",
                "Customer Prompt Text Driver ID": "Text Driver ID",
                "Customer Prompt Text Custom": "Text Custom",
                "Receipt Description ID": "Text ID",
                "Receipt Description Odometer": "Text Odo",
                "Receipt Description Vehicle #": "Text Vehicle #",
                "Receipt Description Driver ID": "Text Driver ID",
                "Receipt Description Custom": "Text Custom",
                "Print on Receipt ID": True,
                "Print on Receipt Odometer": True,
                "Print on Receipt Vehicle #": True,
                "Print on Receipt Driver ID": True,
                "Print on Receipt Custom": True
            }
        }

        if not am.add(am_info):
            tc_fail("Failed to add account 1 with valid parameters.")
        
        acc_id = str(math.floor(time.time() % 10000000000)) # 10 digit unique id
        self.account_ids.append(acc_id)
        am_info = {
            "General": {
                "Account ID":acc_id,
                "Account Name":acc_id,
                "A warning message should display if the customer's account balance reaches":"120.00",
                "Account Credit Limit":"700.00",
                "Enable All Cards":True,
                "Disable All Cards":False
            },
            "Address": {
                "Street":"Friendly St.",
                "City":"Wrong",
                "State":"Different",
                "Country":"This",
            },
            "Card Accounts": {
                "Card Data is On":"Track 1",
                "Issuer Number Start Position":"2",
                "Account Number Start Position":"3",
                "Account Number Range Start":"1",
                "Account Number Range End":"99",
                "Issuer Number":"46456456546",
                "CRIND Authorization Amount":"5.00"
            },
           "Negative Card": {
               "Update" : [
                   ("3", "22"),
                   ("3", "3"),
                   ("22", "99")
               ]
           }
        }

        if not am.add(am_info):
            tc_fail("Failed to add account 2 with valid parameters.")
        
        am_info = {
            "General": {
                "Account ID":acc_id,
                "Account Name":"New name that is not occupied",
                "A warning message should display if the customer's account balance reaches":"120.00",
                "Account Credit Limit":"700.00",
            },
            "Card Accounts": {
                "Card Data is On":"Track 1",
                "Issuer Number Start Position":"2",
                "Account Number Start Position":"3",
                "Account Number Range Start":"1",
                "Account Number Range End":"99",
                "Issuer Number":"46456456546",
                "CRIND Authorization Amount":"5.00"
            }
        }
        if am.add(am_info):
            tc_fail("The id was already in use, but the test did not fail while adding account 3.")

        # Recovered to MWS
        # Go back in
        accounts_maint.AccountsMaintenance.navigate_to()
        am = accounts_maint.AccountsMaintenance()

        acc_id = str(math.floor(time.time() % 10000000000)) # 10 digit unique id
        self.change_old_id_2 = acc_id
        self.account_ids.append(acc_id)
        am_info = {
            "General": {
                "Account ID":acc_id,
                "Account Name":acc_id,
                "A warning message should display if the customer's account balance reaches":"120.00",
                "Account Credit Limit":"700.00",
                "Account Type" : "Face Based",
                "Disable all sub-accts": True,
                "When the POS is offline, the maximum transaction amount is":"500"
            },
            "Address": {
                "Street":"Friendly St.",
                "City":"Wrong",
                "State":"Different",
                "Country":"This",
            },
            "Sub-Accounts": [
                {
                    "Old Sub-Account ID": "00000000000", # Overwrite the default sub-account to desired ID
                    "Sub-Account ID": "49",
                    "Description": "Something",
                    "Vehicle Reg. No": "228",
                    "Sub-Account Disabled": False
                },
                {
                    "Sub-Account ID": "51",
                    "Description": "Something",
                    "Vehicle Reg. No": "228",
                    "Sub-Account Disabled": False
                },
                {
                    "Description": "Something",
                    "Vehicle Reg. No": "228",
                    "Sub-Account Disabled": False
                }
            ]
        }

        if not am.add(am_info):
            tc_fail("Failed to add account 4 with valid parameters.")

        mws.recover()

    @test
    def test_case_3(self):
        """Tests change functionality. Normal flow
        Args: None
        Returns: None
        """
        accounts_maint.AccountsMaintenance.navigate_to()
        am = accounts_maint.AccountsMaintenance()

        am_info = {
            "General": {
                "Account Name":"Test Account Changed",
                "A warning message should display if the customer's account balance reaches":"120.00",
                "Account Credit Limit":"1400.00",
                "Account Type":"Card Based",
                "Enable All Cards":False,
                "Disable All Cards":True
            },
            "Address": {
                "Street":"Cold St.",
                "City":"Right",
                "State":"Closest",
                "Country":"Another",
            },
            "Card Accounts": {
                "Card Data is On":"Track 2",
                "Issuer Number Start Position":"4",
                "Account Number Start Position":"5",
                "Account Number Range Start":"1",
                "Account Number Range End":"123123",
                "Issuer Number":"12312345645231231231231",
                "CRIND Authorization Amount":"15.00"
            },
            "Prompt Options": {
                "Prompt 1 Start Position": "12",
                "Prompt 1 Value": "22",
                "Prompt 1" : {
                    "ID" : True,
                    "Odometer" : False,
                    "Driver ID" : False,
                    "Custom" : False
                }
            }
        }

        if not am.change(self.change_old_id_1, am_info):
            tc_fail("Failed to change account 1 with valid parameters.")

        am_info = {
            "General": {
                "A warning message should display if the customer's account balance reaches":"130.00",
                "Account Credit Limit":"45457.00",
                "Account Type" : "Face Based",
                "Disable all sub-accts": True,
                "When the POS is offline, the maximum transaction amount is":"50"
            },
            "Sub-Accounts": [
                {
                    "Old Sub-Account ID": "51",
                    "Description": "Something else",
                    "Vehicle Reg. No": "22348",
                    "Sub-Account Disabled": False
                },
                {
                    "Old Sub-Account ID": "00000000049",
                    "Description": "Totally new",
                    "Vehicle Reg. No": "2234348",
                    "Sub-Account Disabled": True
                }
            ]
        }

        if not am.change(self.change_old_id_2, am_info):
            tc_fail("Failed to change account 2 with valid parameters.")
        
        mws.recover()

    @test
    def test_case_4(self):
        """Tests adjust balance functionality. Normal flow
        Args: None
        Returns: None
        """
        accounts_maint.AccountsMaintenance.navigate_to()
        am = accounts_maint.AccountsMaintenance()

        for acc_id in self.account_ids:
            if not am.adjust_balance(acc_id, "6.00", "Testing purpose"):
                tc_fail("Failed to adjust balance")
            
        mws.recover()

    @test
    def test_case_5(self):
        """Tests delete functionality. Normal flow
        Args: None
        Returns: None
        """

        accounts_maint.AccountsMaintenance.navigate_to()
        am = accounts_maint.AccountsMaintenance()
        
        if not am.delete(self.account_ids):
            tc_fail("Failed to delete accounts")
        
        mws.recover()


    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        # delete pass after you implement.
        pass