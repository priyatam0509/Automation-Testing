"""
    File name: HPSDallas_Network_Card_Test.py
    Tags: HPS-Dallas
    Description: 
    Author: 
    Date created: 2019-07-17 14:09:38
    Date last modified: 
    Python Version: 3.7
"""

import logging, time
from app import Navi, mws, pos, system
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app import network_card_config

class HPSDallas_Network_Card_Test( ):
    """
    Description: 
    """
    # Config dictionaries used in the test cases
    CHNG_CARD_INFO = {
        "Card Information" : {
            "DEBIT" : {
                "Accept Card" : "No",
                "Shut Off Limit" : "15"
            }
        }
    }

    CHNG_CARDS_INFO = {
        "Card Information" : {
            "AMEX" : {
				"Accept Card" : "No",
				"Crind Fallback" : "Yes",
				"Floor Limit" : "10",
				"CRIND Pre-Auth Amount" : "20",
				"Shut Off Limit" : "70",
				"ZIP Code Prompt At CRIND" : "Yes",
				"ZIP Code Prompt on Manual Entry" : "Yes"
            },
            "FLEET ONE" : {
                "Accept Card" : "Yes",
				"Crind Fallback" : "No",
				"Floor Limit" : "10",
				"CRIND Pre-Auth Amount" : "20",
				"Shut Off Limit" : "70"
            }
        }
    }

    DIS_FIELD_INFO = {
        "Card Information" : {
            "AMEX" : {
				"Response Auth" : "Pickles"
            }
        }
    }

    SHIFT_CTRLS_INFO = {
        "Card Information" : {
            "AMEX" : {
				"Accept Card" : "No",
				"Crind Fallback" : "Yes",
				"Floor Limit" : "10",
				"CRIND Pre-Auth Amount" : "20",
				"Shut Off Limit" : "70",
				"ZIP Code Prompt At CRIND" : "Yes",
				"ZIP Code Prompt on Manual Entry" : "Yes"
            },
            "FLEET ONE" : {
                "Accept Card" : "Yes",
				"Crind Fallback" : "No",
				"Floor Limit" : "10",
				"CRIND Pre-Auth Amount" : "20",
				"Shut Off Limit" : "70"
            }
        },
        "WEX PL" : {
            "Receipt Name" : "Friday please",
            "Mask 690046" : "53"
        }
    }

    @test
    def change_card(self):
        """Change a Network Card Configuration
        Args: None
        Returns: None
        """
        time.sleep(2)
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
        time.sleep(2)
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
        time.sleep(2)
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
        time.sleep(2)
        nc = network_card_config.NetworkCardConfiguration()
        if not nc.change(self.SHIFT_CTRLS_INFO):
            mws.recover()
            tc_fail("Failed to change the Network Card Configurations")