"""
    File name: AgeRestriction_MWS.py
    Tags:
    Description: Tests the Manager Work Station (MWS) Application for setting age restrictions.
    Author(s): Gene Todd
    Date created: 2019-12-17 16:00:21
    Date last modified: 2020-1-8 10:29 by Gene Todd
    Python Version: 3.7
"""

import logging
from app import Navi, mws, pos, system
from app.framework.tc_helpers import setup, test, teardown, tc_fail

from app import restriction_maint
import time

class AgeRestriction_MWS():
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
        
        # Age entry limits used by tests
        self.min_age = 1
        self.max_age = 99

    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        """
        pass
    
    @test
    def test_specialCharacterName(self):
        """
        Tests using special characters in the restriction name
        """
        self.log.info("Initializing Restriction Maintenance Helper")
        rest_maint = restriction_maint.RestrictionMaintenance()
        
        # Testing special characters
        # <,>,&,", and ' are the main characters of concern
        rest_name = "!@#$%^&*()<>'\""
        self.log.info(f"Attempting to add restriction name: {rest_name}")
        res = rest_maint.add({
            "Restriction For Group": rest_name,
            "Buyer/Seller": {
                "Seller must be at least": True
            }
        })
        self._confirmAdd(res, rest_name)
        
        # Confirm that the name is correct in the list and hasn't had replacements
        if rest_name not in mws.get_text("Restriction"):
            tc_fail(f"Failed to find restriction in list: {rest_name}")
        else:
            self.log.info(f"Found {rest_name} in restriction list")
        
        return True
       
    @test
    def test_minRestrictionName(self):
        """
        Tests the lower character limit for a restriction name
        """
        self.log.info("Initializing Restriction Maintenance Helper")
        rest_maint = restriction_maint.RestrictionMaintenance()
        
        # Testing shortest possible restriction name
        rest_name = "1"
        self.log.info(f"Attempting to add restriction name: {rest_name}")
        res = rest_maint.add({
            "Restriction For Group": rest_name,
            "Buyer/Seller": {
                "Seller must be at least": True
            }
        })
        self._confirmAdd(res, rest_name)
        
        # Testing too short of a restriction name
        rest_name = ""
        self.log.info(f"Attempting to add empty restriction name: {rest_name}")
        res = rest_maint.add({
            "Restriction For Group": rest_name,
            "Buyer/Seller": {
                "Seller must be at least": True
            }
        })
        # Catching a failure we want to occur
        self._confirmAdd(res, rest_name)

        return True
        
    @test
    def test_maxRestrictionName(self):
        """
        Tests the upper character limit for a restriction name.
        Tests deleting a restriction by necessity
        """
        self.log.info("Initializing Restriction Maintenance Helper")
        rest_maint = restriction_maint.RestrictionMaintenance()
        
        rest_name = "123456789-123456789-123456789-"
        # Testing too long of a restriction name
        self.log.info(f"Attempting to add oversized restriction name: {rest_name + str(1)}")
        res = rest_maint.add({
            "Restriction For Group": rest_name + str(1),
            "Buyer/Seller": {
                "Seller must be at least": True
            }
        })
        # This will pass, because the last charcter should have been truncated on entry
        self._confirmAdd(res, rest_name)
        # The name should have been truncated to the original restriction name
        if rest_name not in mws.get_text("Restriction"):
            tc_fail(f"Failed to find restriction in list: {rest_name}")
        else:
            self.log.info(f"Found {rest_name} in restriction list")
            
        # Testing deleting restriction to clear the way for the max length test
        rest_maint.delete(rest_name)
        
        # Testing longest possible restriction name
        self.log.info(f"Attempting to add restriction name: {rest_name}")
        res = rest_maint.add({
            "Restriction For Group": rest_name,
            "Buyer/Seller": {
                "Seller must be at least": True
            }
        })
        self._confirmAdd(res, rest_name)
        
        return True

    @test
    def test_minimumSellerAge(self):
        """
        Tests whether the minimum seller age is configurable, and respects upper and lower age limits
        """
        self.log.info("Initializing Restriction Maintenance Helper")
        rest_maint = restriction_maint.RestrictionMaintenance()
        
        # Confirming the minimum seller age is configurable and testing the lowest age limit
        rest_name = "minSellerAgeRestriction"
        self.log.info(f"Adding restriction with name: {rest_name}")
        self.log.info(f"Attempting to add restriction with minimum seller age: {self.min_age}")
        res = rest_maint.add({
            "Restriction For Group": rest_name,
            "Buyer/Seller": {
                "Seller must be at least": True,
                "Minimum Seller Age": self.min_age
            }
        })
        self._confirmAdd(res, rest_name)
        
        # Testing too low of a minimum age 
        self.log.info(f"Attempting to change restriction's minimum seller age to: {self.min_age - 1}")
        rv = self._changeValue(rest_name, "Minimum Seller Age", self.min_age - 1)
        # The value min_age - 1 should have automatically changed to min_age, confirming the change
        if not int(rv) == self.min_age:
            tc_fail(f"Entered value is [{rv}]. Expected value is [{self.min_age}]")
        else:
            self.log.info(f"Confirmed entered value [{self.min_age - 1}] rounded to [{self.min_age}]")
            
        # Testing highest minimum age
        self.log.info(f"Attempting to change restriction's minimum seller age to: {self.max_age + 1}")
        rv = self._changeValue(rest_name, "Minimum Seller Age", self.max_age + 1)
        # The value max_age + 1 should have been truncated to the first 2 entered characters
        ev = str(self.max_age + 1)[:2]
        if not int(rv) == int(ev):
            tc_fail(f"Entered value is [{rv}]. Expected value is [{ev}")
        else:
            self.log.info(f"Confirmed entered value [{self.max_age + 1}] truncated to [{ev}]")
            
        return True

    @test
    def test_minimumBuyerAge(self):
        """
        Tests whether the minimum buyer age is configurable, and respects upper and lower age limits
        """
        self.log.info("Initializing Restriction Maintenance Helper")
        rest_maint = restriction_maint.RestrictionMaintenance()
        
        # Confirming the minimum buyer age is configurable and testing the lowest age limit
        rest_name = "minBuyerAgeRestriction"
        self.log.info(f"Adding restriction with name: {rest_name}")
        self.log.info(f"Attempting to add restriction with minimum buyer age: {self.min_age}")
        res = rest_maint.add({
            "Restriction For Group": rest_name,
            "Buyer/Seller": {
                "Buyer Verify Only": True,
                "Minimum Buyer Age": self.min_age
            }
        })
        self._confirmAdd(res, rest_name)
        
        # Testing too low of a minimum age 
        self.log.info(f"Attempting to change restriction's minimum buyer age to: {self.min_age - 1}")
        rv = self._changeValue(rest_name, "Minimum Buyer Age", self.min_age - 1)
        # The value min_age - 1 should have automatically changed to min_age, confirming the change
        if not int(rv) == self.min_age:
            tc_fail(f"Entered value is [{rv}]. Expected value is [{self.min_age}]")
        else:
            self.log.info(f"Confirmed entered value [{self.min_age - 1}] rounded to [{self.min_age}]")
            
        # Testing highest minimum age
        self.log.info(f"Attempting to change restriction's minimum buyer age to: {self.max_age + 1}")
        rv = self._changeValue(rest_name, "Minimum Buyer Age", self.max_age + 1)
        # The value max_age + 1 should have been truncated to the first 2 entered characters
        ev = str(self.max_age + 1)[:2]
        if not int(rv) == int(ev):
            tc_fail(f"Entered value is [{rv}]. Expected value is [{ev}]")
        else:
            self.log.info(f"Confirmed entered value [{self.max_age + 1}] truncated to [{ev}]")
            
        return True
        
    @test
    def test_ageRestrictionOptions(self):
        """
        Tests Configurable options for age restrictions
        """
        self.log.info("Initializing Restriction Maintenance Helper")
        rest_maint = restriction_maint.RestrictionMaintenance()
        
        # Setting up base item with just verify
        rest_name = "ageRestrictionOpts"
        self.log.info(f"Attempting to add restriction name: {rest_name}")
        res = rest_maint.add({
            "Restriction For Group": rest_name,
            "Buyer/Seller": {
                "Buyer Verify Only": True
            }
        })
        self._confirmAdd(res, rest_name)
        
        # Navigate back into the restriction
        mws.select("Restriction", rest_name)
        mws.click_toolbar("Change")
            
        # Confirm the age verification tab can only be edited when Entry of Birthdate required
        if mws.select_tab("Age Verification", tolerance="111111"): # Tolerance is too low to find disabled tabs
            tc_fail("Age Verification tab appears enabled")
        else:
            self.log.info("Age verification tab appears disabled")
        mws.set_value("Entry of birth date required", True)
        self.log.info("Birthdate required set")
        if not mws.select_tab("Age Verification", tolerance="111111"):
            tc_fail("Age verification tab appears disabled")
        else:
            self.log.info("Age verification tab appears Enabled")
        mws.click_toolbar("Save")
        # Change fires too fast. Have to sleep to give it a second.
        time.sleep(.5)
            
        # Toggle all the extra settings on
        self.log.info("Turning on auxilary settings")
        rest_maint.change(rest_name, {
            "Buyer/Seller": {
                "Entry of birth date required": True
            },
            "Age Verification": {
                "Customer ID scan preferred for birth date entry": True,
                "Allow Default button to be used for sale of age restricted items": True,
                "Require cashier to confirm scanned ID": True
            }
        })
        
        time.sleep(.5)
        # Confirm the settings were saved
        self.log.info("Confirming settings were saved")
        mws.select("Restriction", rest_name)
        mws.click_toolbar("Change")
        mws.select_tab("Age Verification")
        mws.get_value("Customer ID scan preferred for birth date entry")
        mws.get_value("Allow Default button to be used for sale of age restricted items")
        mws.get_value("Customer ID scan preferred for birth date entry")
        mws.click_toolbar("Cancel")
        mws.click_toolbar("Exit")
            
        return True
    
    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        if not system.restore_snapshot():
            self.log.debug("No snapshot to restore, if this is not expected please contact automation team")
        pass
    
    def _confirmAdd(self, result, rName):
        """
        Helper function to confirm that RestrictionMaintenance.add() succeded
        """
        # Check the passed result for success
        self.log.info(f"Add restriction result: {result}")
        if not result:
            msg = mws.get_top_bar_text()
            if msg:
                if not mws.click_toolbar("Cancel"):
                    self.log.error("Unable to click on cancel button")
                    return False
                self.log.error(f"Unable to add restriction: {rName}")
        
    def _changeValue(self, restriction, target, value):
        """
        Helper function to change a value of the restriction I'm in and provide a confirmation value.
        Calls tc_fail if fails due to navigation errors.
        restriction - the name of the restriction to change
        target - Target name according to controls.json
        value - Intended value to enter
        return: returns the value of my target after the attempt to change
        """
        self.log.info(f"Attempting to change [{target}] to [{value}]")
        # RestrictionMaintenance.change() does not verify values. Have to check here.
        mws.select("Restriction", restriction)
        mws.click_toolbar("Change")
        mws.set_value(target, value)
        # Return what the value actually ended up being
        ret = mws.get_value(target)
        # Restriction Maintenance changes values it won't accept, so any message on save should be a failure
        mws.click_toolbar("Save")
        msg = mws.get_top_bar_text()
        if msg:
            mws.click_toolbar("Cancel")
            tc_fail(f"Message appeared: {msg}")
        return ret
    
