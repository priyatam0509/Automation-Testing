"""
    File name: InComm_Card_Config_Test.py
    Tags:
    Description: Tests incomm.CardConfiguration module
    Author: Alex Rudkov
    Date created: 2019-07-03 09:05:17
    Date last modified: 
    Python Version: 3.7
"""

import logging, time
from app import Navi, mws, pos, system, incomm_card
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class InComm_Card_Config_Test():
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
        """Adds valid cards
        Args: None
        Returns: None
        """
        cc = incomm_card.CardConfiguration()

        # Valid parameters
        params = [
            {
                "Card Name": "Test Card 1",
                "IIN": "123456789",
                "CRIND Auth Request Amount": "5.00",
                "Fuel Discount Group": "NONE"
            },
            {
                "Card Name": "Test Card 2",
                "IIN": "321654897"
            },
            {
                "Card Name": "Test Card 3",
                "IIN": "321654987"
            },
            {
                "Card Name": "Test Card 4",
                "IIN": "465321789"
            }
        ]

        self.log.info("Configuring the CC with valid parameters list")
        if not cc.add(params):
            tc_fail("Failed to configure the Card Configuration with the valid parameters list.")
        self.log.info("Successfully configured the Card Configuration with valid parameters list.")
        
        # Check
        time.sleep(2)
        cc.navigate_to()

        error = False
        for entry in params:
            if not mws.select("Card List", entry["Card Name"]):
                self.log.error(f"The card with the name '{entry['Card Name']}' was successfully added, but cannot be found in the list.")
                error = True
                continue

            for field, value in entry.items():
                set_value = mws.get_value(field)
                if type(set_value) is list:
                    set_value = set_value[0]
                if set_value != value:
                    self.log.error(f"The field '{field}' was set successfully, but upon check had value '{set_value}' when '{value}' was expected")
                    error = True
        if error:
            tc_fail("The test failed a check after configuration 1")
        mws.recover()

        time.sleep(2)
        cc.navigate_to()

        # Add an entry that should overwrite existing entry
        params = {
            "Card Name": "Test Card 1",
            "IIN": "159753215",
            "CRIND Auth Request Amount": "10.00",
            "Fuel Discount Group": "NONE"
        }

        self.log.info("Configuring the CC with valid parameter dictionary that overwrites existing entry")
        if not cc.add(params):
            tc_fail("Failed to configure the Card Configuration with the valid parameters dictionary.")
        self.log.info("Successfully configured the Card Configuration with valid parameters dictionary.")

        time.sleep(2)
        cc.navigate_to()

        # Check
        error = False
        params = [params]
        for entry in params:
            if not mws.select("Card List", entry["Card Name"]):
                self.log.error(f"The card with the name '{entry['Card Name']}' was successfully added, but cannot be found in the list.")
                error = True
                continue

            for field, value in entry.items():
                set_value = mws.get_value(field)
                if type(set_value) is list:
                    set_value = set_value[0]
                if set_value != value:
                    self.log.error(f"The field '{field}' was set successfully, but upon check had value '{set_value}' when '{value}' was expected")
                    error = True
        if error:
            tc_fail("The test failed a check after configuration")
        mws.recover()

    @test
    def test_case_2(self):
        """Adds invalid card
        Args: None
        Returns: None
        """
        cc = incomm_card.CardConfiguration()

        # Invalid IIN
        params = {
            "Card Name": "Test Card 1",
            "IIN": "",
            "CRIND Auth Request Amount": "10.00",
            "Fuel Discount Group": "NONE"
        }

        self.log.info("Configuring the CC with invalid parameters dictionary")
        if cc.add(params):
            tc_fail("The Card Configuration was configured successfully when failure was expected.")
        self.log.info("Card Configuration was not configured with invalid parameters dictionary.")
        mws.recover()
    
    @test
    def test_case_3(self):
        """Deletes valid cards
        Args: None
        Returns: None
        """
        cc = incomm_card.CardConfiguration()

        # Valid list
        params = [
            "Test Card 1",
            "Test Card 2",
            "Test Card 3"
        ]

        self.log.info("Removing the cards from CC with valid parameters list")
        if not cc.delete(params):
            tc_fail("Failed to remove the cards from Card Configuration with the valid parameters list.")
        self.log.info("Successfully removed the cards from the Card Configuration with valid parameters list.")

        # Check
        time.sleep(2)
        cc.navigate_to()

        # Check
        error = False
        for name in params:
            if mws.select("Card List", name):
                self.log.error(f"The card with the name '{name}' was successfully removed, but was found in the list.")
                error = True
                continue

        if error:
            tc_fail("The test failed a check after configuration")
        mws.recover()

        time.sleep(2)
        cc.navigate_to()

        # Valid string
        params = "Test Card 4"

        self.log.info("Removing the card from CC with valid parameter string")
        if not cc.delete(params):
            tc_fail("Failed to remove the card from Card Configuration with the valid parameter string.")
        self.log.info("Successfully removed the card from the Card Configuration with valid parameter string.")

        time.sleep(2)
        cc.navigate_to()

        # Check
        if mws.select("Card List", params):
            self.log.error(f"The card with the name '{params}' was successfully removed, but was found in the list.")
            error = True

        if error:
            tc_fail("The test failed a check after configuration")
        mws.recover()
        
        time.sleep(2)
        cc.navigate_to()

        # invalid string
        params = "Test Card 89898989898"

        self.log.info("Removing the card from CC with invalid parameter string")
        if cc.delete(params):
            tc_fail("The card with invalid name was removed from Card Configuration when failure was expected.")
        self.log.info("The card with invalid name was not removed from Card Configuration.")
        mws.recover()

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        # delete pass after you implement.
        pass