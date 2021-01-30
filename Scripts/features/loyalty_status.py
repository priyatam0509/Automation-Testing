"""
    File name: loyalty_status.py
    Tags:
    Description: Verify Loyalty Status Button in HTML POS
    Author: Kevin Walker
    Date created: 2020-05-06 10:53:51
    Date last modified: 
    Python Version: 3.7
"""

import logging, json
from app import Navi, mws, pos, system, pinpad
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app.simulators import loyaltysim, serial_scanner
from app.features import loyalty

class loyalty_status():
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

        #Create variables to be used for loyalty provider configuration
        self.loyalty_name = "Kickback"

        self.card_mask_to_add = ['6008']

        self.loyalty_cfg = {
            "General": {
                    "Enabled": "Yes",
                    "Site Identifier": '1',
                    "Host IP Address": '10.5.48.2',
                    "Port Number": '7900'
            },
        }

        

    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        """
        if not system.restore_snapshot():
            self.log.debug("No snapshot to restore, if this is not expected please contact automation team")

        #creates class object of LoyaltyInterface to be used to configure loyalty
        self.objLoyalty = loyalty.LoyaltyInterface()
        
        # #configure loyalty provider        
        self.objLoyalty.change_provider(self.loyalty_cfg, self.loyalty_name, cards_to_add = self.card_mask_to_add)
        mws.click_toolbar("Exit")
        
        #Start loyalty sim
        loyaltysim.StartLoyaltySim()
        
        #Check to see if loyalty provider with mask 6008 is configured in the sim if not add one
        loyaltysim.DeleteAllLoyaltyIDs()
        loyalty_id = loyaltysim.AddLoyaltyIDs("6008", "6008", "6008", "6008", "6008")        
        loyaltysim.AssignStatusMessages(loyalty_id, "Loyalty Display Message", "Loyalty Receipt Message")
        
        pos.connect()
        pos.sign_on()


    @test
    def loyatly_status_swipe_summary(self):
        """
        Verify swiping valid loyalty and selecting Summary for loyalty status returns loyalty info
        """        
        if not self.get_loyalty_status(method = "swipe", info_type = "summary", valid = True):
            tc_fail("Unable to complete loyalty status")
        #TODO: add verification once receipt info can be checked

    @test
    def loyatly_status_swipe_detail(self):
        """
        Verify swiping valid loyalty and selecting Detail for loyalty status returns loyalty info
        """
        if not self.get_loyalty_status(method = "swipe", info_type = "detail", valid = True):
            tc_fail("Unable to complete loyalty status")
        #TODO: add verification once receipt info can be checked

    @test
    def loyatly_status_swipe_invalid_summary(self):
        """
        Verify swiping invalid loyalty and selecting Summary for loyalty status returns invalid loyalty
        """
        if not self.get_loyalty_status(method = "swipe", info_type = "summary", valid = False):
            tc_fail("Unable to complete loyalty status")

    @test
    def loyatly_status_swipe_invalid_detail(self):
        """
        Verify swiping invalid loyalty and selecting Detail for loyalty status returns Invalid Loyalty
        """
        if not self.get_loyalty_status(method = "swipe", info_type = "detail", valid = False):
            tc_fail("Unable to complete loyalty status")

    @test
    def loyatly_status_manual_summary(self):
        """
        Verify manually entering valid loyalty and selecting Summary for loyalty status returns loyalty info
        """
        if not self.get_loyalty_status(method = "manual", info_type = "summary", valid = True):
            tc_fail("Unable to complete loyalty status")
        #TODO: add verification once receipt info can be checked

    @test
    def loyatly_status_manual_detail(self):
        """
        Verify manually entering valid loyalty and selecting Detail for loyalty status returns loyalty info
        """
        if not self.get_loyalty_status(method = "manual", info_type = "detail", valid = True):
            tc_fail("Unable to complete loyalty status")
        #TODO: add verification once receipt info can be checked

    @test
    def loyatly_status_manual_invalid_summary(self):
        """
        Verify manually entering invalid loyalty and selecting Summary for loyalty status returns Invalid Loyalty
        """
        if not self.get_loyalty_status(method = "manual", info_type = "summary", valid = False):
            tc_fail("Unable to complete loyalty status")

    @test
    def loyatly_status_manual_invalid_detail(self):
        """
        Verify manually entering invalid loyalty and selecting Detail for loyalty status returns Invalid Loyalty
        """
        if not self.get_loyalty_status(method = "manual", info_type = "detail", valid = False):
            tc_fail("Unable to complete loyalty status")

    @test
    def loyatly_status_scan_summary(self):
        """
        Verify scanning valid loyalty and selecting Summary for loyalty status returns loyalty info
        """
        if not self.get_loyalty_status(method = "scan", info_type = "summary", valid = True):
            tc_fail("Unable to complete loyalty status")
        #TODO: add verification once receipt info can be checked

    @test
    def loyatly_status_scan_detail(self):
        """
        Verify scanning valid loyalty and selecting Detail for loyalty status returns loyalty info
        """
        if not self.get_loyalty_status(method = "scan", info_type = "detail", valid = True):
            tc_fail("Unable to complete loyalty status")
        #TODO: add verification once receipt info can be checked

    @test
    def loyatly_status_scan_invalid_summary(self):
        """
        Verify scanning invalid loyalty and selecting Summary for loyalty status returns Invalid Loyalty
        """
        if not self.get_loyalty_status(method = "scan", info_type = "summary", valid = False):
            tc_fail("Unable to complete loyalty status")

    @test
    def loyatly_status_scan_invalid_detail(self):
        """
        Verify scanning invalid loyalty and selecting Detail for loyalty status returns Invalid Loyalty
        """
        if not self.get_loyalty_status(method = "scan", info_type = "summary", valid = False):
            tc_fail("Unable to complete loyalty status")


    @test
    def loyalty_disabled(self):
        """
        Verify that Loyalty Status button is not present when loyalty is disabled
        """
        # Change config to disable loyalty provider
        objLoyalty2 = loyalty.LoyaltyInterface()
        disable_config = {'Enabled': 'No'}
        objLoyalty2.change_provider(disable_config, self.loyalty_name)
        # Check to make sure Loyalty Status button disappears when loyalty is disabled
        system.wait_for(lambda: pos.is_element_present(pos.controls['function keys']['loyalty status']) == False)


    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        pos.sign_off()
        pos.close()
        loyaltysim.StopLoyaltySim()
        mws.sign_off()


    #Helper Function
    def get_loyalty_status(self, method = "swipe", info_type = "summary", valid = True):
        #Click loyalty status
        if pos.click("loyalty status"):
            self.log.info("Clicked Loyalty Status")
        else:
            self.log.warning("Could not click Loyalty Status")
            return False
 
        #Answer yes to prompt
        if pos.click("yes"):
            self.log.info("Clicked Yes")
        else:
            self.log.warning("Could not click Yes")
            return False

        #Determine entry method and use swipe/manual/scan valid or invalid
        if (method == "swipe" and valid):
            pinpad.swipe_card(card_name = "Loyalty")
            self.log.info("Swiping Loyalty Card")
        elif (method == "swipe" and not valid):
            pinpad.swipe_card()
            self.log.info("Swiping Invalid Loyalty Card")
        elif (method == "manual" and valid):
            if pos.click("manual"):
                self.log.info("Clicked Manual")
            else:
                self.log.warning("Could not click manual")
                return False
            pinpad.manual_entry(card_name = "Loyalty")
            self.log.info("Entered Loyalty ID")
        elif (method == "manual" and not valid):
            if pos.click("manual"):
                self.log.info("Clicked Manual")
            else:
                self.log.warning("Could not click manual")
                return False
            pinpad.manual_entry()
            self.log.info("Entering Invalid Loyalty Card")
        elif (method == "scan" and valid):
            #check to make sure POS is ready to receive a scan by checking if 'Manual' button is present
            if(pos.is_element_present(pos.controls['keypad']['manual'], timeout = 10)):
                serial_scanner.SerialScanner(3).scan("600800000")
                self.log.info("Scanning Loyalty Card")
            else:
                self.log.warning("Loyalty entry was not prompted for")
                return False
        elif (method == "scan" and not valid):
            #check to make sure POS is ready to receive a scan by checking if 'Manual' button is present
            if(pos.is_element_present(pos.controls['keypad']['manual'], timeout = 10)):
                serial_scanner.SerialScanner(3).scan("123400000")
                self.log.info("Scanning Loyalty Card")
            else:
                self.log.warning("Loyalty entry was not prompted for")
        else:
            self.log.warning("Unable to complete transaction with method=" + method + " and valid=" + valid)
            return False
        
        #Click summary or detail
        if (info_type == "summary"):
            if pos.click("Summary"):
                self.log.info("Clicked Summary")
            else:
                self.log.warning("Could not click Summary")
                return False
        else:
            if pos.click("Detail"):
                self.log.info("Clicked Detail")
            else:
                self.log.warning("Could not click Detail")
        
        #If using invalid loyalty check to make sure invalid loyalty message is displayed
        if(not valid):
            msg = pos.read_message_box()
            if (msg != "Invalid Loyalty ID" ):
                self.log.warning("Did not return as Invalid Loyalty")
                return False
            if pos.click("ok"):
                self.log.info("Clicked OK")
            else:
                self.log.warning("Could not click OK")
                return False

        return True