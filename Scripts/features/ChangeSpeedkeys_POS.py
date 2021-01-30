"""
    File name: ChangeSpeedkeys_POS.py
    Tags:
    Description: 
    Author: 
    Date created: 2020-03-11 11:20:03
    Date last modified: 
    Python Version: 3.7
"""

import logging, time
from app import Navi, mws, pos, system, key_maint
from app.framework.tc_helpers import setup, test, teardown, tc_fail 

# Speed key menu names
skm_default = "default"
skm_primary = "PrimarySpeedKeys"
skm_secondary = "SecondarySpeedKeys"
skm_sub = "SubSpeedKeys"


class ChangeSpeedkeys_POS():
    """
    Description: Test class that provides an interface for testing.
    """

    def __init__(self):
        self.log = logging.getLogger()
        
    @setup
    def setup(self):
        # if not system.restore_snapshot():
            # self.log.debug("No snapshot to restore, if this is not expected please contact automation team")
        # Setup an alternative speedkey menus
        skm = key_maint.SpeedKeyMaintenance()
        _add_speedkey_menu(skm, skm_primary, "Primary", [
            { "position": 1, "caption": skm_primary },
            { "position": 6, "caption": "Test Page" }
        ])
        _add_speedkey_menu(skm, skm_secondary, "Secondary", [
            { "position": 1, "caption": skm_secondary },
            { "position": 6, "caption": "Test Page" }
        ])
        _add_speedkey_menu(skm, skm_sub, "Sub Menu", [
            { "position": 1, "caption": skm_sub },
            { "position": 6, "caption": "Test Page" }
        ])
        # Setup POS connection
        pos.connect()
        pos.sign_on()
        pos.click_function_key("Tools")
        
    @test
    def test_basicSKChange(self):
        """
        Confirms we can do a basic speedkey change
        """
        # Change the menu
        self.log.info("Changing speedkey menu")
        pos.click("Change Speedkeys")
        pos.select_list_item(skm_primary)
        pos.click("Enter")
        
        # Check if the new menu appears
        self.log.info(f"Looking for speedkey [{skm_primary}]")
        ret = _check_for_speedkey(skm_primary)
        
        # Change speedkeys back for next test
        self.log.info("Changing speedkey menu to default")
        pos.click("Change Speedkeys")
        pos.select_list_item(skm_default)
        pos.click("Enter")
        
        # Pass/fail based on return
        if not ret:
            tc_fail("Improper speedkey menu found")
            
    @test
    def test_cancelSKChange(self):
        """
        Confirms canceling speedkey change does not change menu
        """
        # Start and cancel the menu change
        self.log.info("Starting and canceling speedkey menu change")
        pos.click("Change Speedkeys")
        pos.select_list_item(skm_primary)
        pos.click("Cancel")
        
        # Check if the Menu changed
        self.log.info(f"Looking for speedkey [{skm_default}]")
        if not _check_for_speedkey("Generic Item"):
            tc_fail("Menu changed after cancel")
        
    @test
    def test_OnlyPrimaryMenus(self):
        """
        Tests that secondary and submenu speedkeys do not appear in the change speedkey list
        """
        # Open speedkey change menu
        self.log.info("Starting change speedkeys")
        pos.click("Change Speedkeys")
        
        # Look for secondary/sub menus
        sel_list = pos.get_text(pos.controls['selection list']['list'])
        if skm_secondary in sel_list:
            tc_fail("Secondary speedkey menu found in change speedkeys list")
        if skm_sub in sel_list:
            tc_fail("Sub menu speedkeys found in change speedkeys list")
            
        pos.click("Cancel")

    @teardown
    def teardown(self):
        pos.close()
        
def _check_for_speedkey(text):
    """
    Helper function that checks if a desired speedkey is visible
    Returns true if present, false otherwise
    """
    skeys = pos.get_text("//div[@id='speedkeys_container']").split('\n')
    if text in skeys:
        return True
    return False

def _add_speedkey_menu(skm, menu_name, menu_type, buttons):
    """
    Helper function for setting up speedkey menus of different types
    """
    logger = logging.getLogger()
    
    # Choose add/change depending on whether a menu by given name exist
    if mws.set_value("Speedkeys", menu_name):
        logger.warning(f"Speedkey menu with name [{menu_name}] already exists. Modifying.")
        mws.click_toolbar("Change")
    else:
        logger.info(f"Adding Speedkey menu [{menu_name}]")
        mws.click_toolbar("Add")
        mws.set_value("Key Menu Description", menu_name)
        
    time.sleep(1) # Wait or other functions don't wait for the page to load
        
    # Choose menu type - have to do it as we make it. Can't change after
    logging.info(f"Setting menu type to [{menu_type}]")
    mws.set_value(menu_type, True)
    
    # Handle all the buttons
    # Only handles position, and caption, because that's all I really need.
    for b in buttons:
        skm.add(position=b['position'], code="1", caption=b['caption'])
        
    # Save
    mws.click_toolbar("Save")
    
