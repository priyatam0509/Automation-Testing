"""
    File name: Concord_Network_Card_Test.py
    Tags: Concord, Valero
    Description: Tests the Network Card Configuration
    Author: Conor McWain
    Date created: 2019-06-28 14:45:56
    Date last modified: 2019-07-17 (Alex Rudkov)
    Python Version: 3.7
"""

import logging
from app import Navi, mws, pos, system
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app import network_card_config

class Concord_Network_Card_Test():
    """
    Description: Test class that provides an interface for testing.\
        Test class is specific to Concord  and Valero brands
    """
    # Config dictionaries used in the test cases
    CHNG_CARD_INFO = {
        "Debit":{
            "Page 1":{
                "CRIND Authorization Amount": '20'
            },
            "Page 2":{
                "Track Configuration": 'Preferred Track 1'
            }
        }
    }

    CHNG_CARDS_INFO = {
        "Gulf":{
            "Page 1":{
                "CRIND Authorization Amount": '20'
            }
        },
        "JCB":{
            "Page 2":{
                "Track Configuration": 'Preferred Track 1'
            }
        }
    }

    DIS_FIELD_INFO = {
        "Debit":{
            "Page 1":{
                "Inside Floor Limit": 'Kittens'
            }
        }
    }

    SHIFT_CTRLS_INFO = {
        "Discover":{
            "Page 1":{
                "Inside Floor Limit": '5',
                "CRIND Floor Limit": '10',
                "CRIND Authorization Amount": '15'
            }
        },
        "Fleet 1":{
            "Page 1":{
                "Inside Floor Limit": '5',
                "CRIND Floor Limit": '10',
                "CRIND Authorization Amount": '15'
            }
        },
        "Fuelman":{
            "Page 1":{
                "Inside Floor Limit": '5',
                "CRIND Floor Limit": '10',
                "CRIND Authorization Amount": '15'
            }
        }
    }

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
        pass

    @test
    def change_card(self):
        """Change a Network Card Configuration
        Args: None
        Returns: None
        """
        nc = network_card_config.NetworkCardConfiguration()
        if not nc.change(self.CHNG_CARD_INFO):
            mws.recover()
            tc_fail("Failed to change the Network Card Configuration")

    @test
    def change_cards(self):
        """Change multiple Network Card Configurations
        Args: None
        Returns: None
        """
        nc = network_card_config.NetworkCardConfiguration()
        if not nc.change(self.CHNG_CARDS_INFO):
            mws.recover()
            tc_fail("Failed to change the Network Card Configurations")

    @test
    def disabled_field(self):
        """Attempt to change a field that is disabled
        Args: None
        Returns: None
        """
        nc = network_card_config.NetworkCardConfiguration()
        if nc.change(self.DIS_FIELD_INFO):
            tc_fail("Was able to change the Network Card Configuration")
        else:
            pass
            mws.recover()

    @test
    def shifting_controls(self):
        """Change crads, shifting the controls of the text boxes. Verify functionality
        Args: None
        Returns: None
        """
        nc = network_card_config.NetworkCardConfiguration()
        if not nc.change(self.SHIFT_CTRLS_INFO):
            mws.recover()
            tc_fail("Failed to change the Network Card Configurations")

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        # delete pass after you implement.
        pass