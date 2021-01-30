"""
    File name: HTML_Button_Changes.py
    Tags:
    Description: Verify various button changes for HTML POS
    Author: Kevin Walker
    Date created: 2020-06-25 16:03:04
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import Navi, mws, pos, system
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class HTML_Button_Changes():
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
        """
        Performs any initialization that is not default.
        """
        # if not system.restore_snapshot():
        #     self.log.debug("No snapshot to restore, if this is not expected please contact automation team")
        pos.connect()

    @test
    def change_speedkeys_not_in_main_menu(self):
        """
        Merlin-1409, Verify Change Speedkeys is not in the Main Menu
        """
        pos.sign_on()
        if pos.is_element_present(pos.controls['function keys']['change speedkeys']):
            tc_fail("Change Speedkeys button found in Main Menu, should not be there")

    @test
    def clean_not_in_in_main_menu(self):
        """
        Merlin-1409, Verify Clean is not in Main Menu
        """
        pos.sign_on()
        if pos.is_element_present(pos.controls['function keys']['clean']):
            tc_fail("Clean button found in Main Menu, should not be there")

    @test
    def change_speedkeys_in_tools(self):
        """
        Merlin-1409, Verify Change Speedkeys is found in the tools menu when signed on
        """
        pos.sign_on()
        pos.click("tools")
        if not pos.is_element_present(pos.controls['function keys']['change speedkeys']):
            pos.click("back")
            tc_fail("Change Speedkeys button was not found in the Tools Menu")
        pos.click("back")

    @test
    def clean_in_tools(self):
        """
        Merlin-1409, Verify Clean is in tools menu when signed on
        """
        if pos.is_element_present(pos.controls['function keys']['back']):
            pos.click("back")
        pos.sign_on()
        pos.click("tools")
        if not pos.is_element_present(pos.controls['function keys']['clean']):
            pos.click("back")
            tc_fail("Clean button was not found in the Tools Menu")
        pos.click("back")

    @test
    def change_speedkeys_not_in_tools_signed_off(self):
        """
        Merlin-1409, Verify Change Speedkeys not in Tools Menu when not signed on
        """
        if pos.is_element_present(pos.controls['function keys']['back']):
            pos.click("back")
        if pos._is_signed_on():
            pos.sign_off()
        pos.click("tools")
        pos.enter_keypad("91", after = "Enter")
        pos.enter_keyboard("91", after = "Ok")
        if pos.is_element_present(pos.controls['function keys']['change speedkeys']):
            pos.click("back")
            tc_fail("Change Speedkeys button should not be found in the Tools Menu when not signed onto POS")
        pos.click("back")

    @test
    def clean_in_tools_signed_off(self):
        """
        Merlin-1409, Verify Clean is found in the Tools Menu when signed off
        """
        if pos.is_element_present(pos.controls['function keys']['back']):
            pos.click("back")
        if pos._is_signed_on():
            pos.sign_off()
        pos.click("tools")
        pos.enter_keypad("91", after = "Enter")
        pos.enter_keyboard("91", after = "Ok")
        if not pos.is_element_present(pos.controls['function keys']['clean']):
            pos.click("back")
            tc_fail("Clean button was not found in the Tools Menu")
        pos.click("back")

    @test
    def show_all_dispensers_not_in_main_menu(self):
        """
        Merlin-1411, Verify Show All Dispensers not found in main menu
        """
        if pos.is_element_present(pos.controls['function keys']['back']):
            pos.click("back")
        pos.sign_on()
        if pos.is_element_present(pos.controls['function keys']['show all dispensers']):
            tc_fail("Show All Dispensers should not be present in main menu")

    @test
    def show_all_dispensers_not_in_item_menu(self):
        """
        Merlin-1411, Verify Show All Dispensers not found in item menu
        """
        pos.sign_on()
        pos.add_item()
        if pos.is_element_present(pos.controls['function keys']['show all dispensers']):
            tc_fail("Show All Dispensers should not be present in item menu")
        pos.pay()

    @test
    def show_all_dispensers_in_dispenser_menu(self):
        """
        Merlin-1411, Verify Show All Dispensers is found in dispenser menu
        """
        pos.sign_on()
        pos.click("dispenser menu")
        if not pos.is_element_present(pos.controls['function keys']['show all dispensers']):
            pos.click("back")
            tc_fail("Show All Dispensers was not found in dispenser menu")
        pos.click("back")

    @test
    def show_all_dispensers_in_dispenser_menu_signed_off(self):
        """
        Merlin-1411, Verify Show All Dispensers is found in dispenser menu when signed off
        """
        if pos.is_element_present(pos.controls['function keys']['back']):
            pos.click("back")
        if pos._is_signed_on():
            pos.sign_off()
        pos.click("dispenser menu")
        if not pos.is_element_present(pos.controls['function keys']['show all dispensers']):
            pos.click("back")
            tc_fail("Show All Dispensers was not found in dispenser menu")
        pos.click("back")

    @test
    def no_reboot_in_tools(self):
        """
        Merlin-1412, Verify Reboot is not found in tools menu
        """
        if pos.is_element_present(pos.controls['function keys']['back']):
            pos.click("back")
        pos.sign_on()
        pos.click("tools")
        if pos.is_element_present(pos.controls['function keys']['tools keys']['reboot']):
            pos.click("back")
            tc_fail("Reboot was found in tools menu")
        pos.click("back")

    @test
    def no_reboot_in_tools_signed_off(self):
        """
        Merlin-1412, Verify Reboot is not found in tools menu when signed off
        """
        if pos.is_element_present(pos.controls['function keys']['back']):
            pos.click("back")
        if pos._is_signed_on():
            pos.sign_off()
        pos.click("tools")
        pos.enter_keypad("91", after = "Enter")
        pos.enter_keyboard("91", after = "Ok")
        if pos.is_element_present(pos.controls['function keys']['tools keys']['reboot']):
            pos.click("back")
            tc_fail("Reboot was found in tools menu")
        pos.click("back")
        
    @test
    def network_in_main_menu(self):
        """
        Merlin-1413, Verify Network button is found in the main menu when signed on
        """
        if pos.is_element_present(pos.controls['function keys']['back']):
            pos.click("back")
        pos.sign_on()
        if not pos.is_element_present(pos.controls['function keys']['network']):
            tc_fail("Network button was not found in the main menu")

    @test
    def buttons_in_network_menu(self):
        """
        Merlin-1413, Verify buttons are present in Network Menu when signed on
        """
        pos.sign_on()
        pos.click("network")
        if not pos.is_element_present(pos.controls['function keys']['network keys']['host function']):
            pos.click("back")
            tc_fail("Host Function button was not found in the Network menu")
        if not pos.is_element_present(pos.controls['function keys']['network keys']['balance inquiry']):
            pos.click("back")
            tc_fail("Balance Inquiry button was not found in the Network menu")
        if not pos.is_element_present(pos.controls['function keys']['network keys']['e-mail']):
            pos.click("back")
            tc_fail("E-mail button was not found in the Network menu")
        if not pos.is_element_present(pos.controls['function keys']['network keys']['de-activate card']):
            pos.click("back")
            tc_fail("De-activate Card button was not found in the Network menu")
        pos.click("back")

    @test
    def network_in_main_menu_locked(self):
        """
        Merlin-1413, Verify Network button is found in the main menu when register is locked
        """
        if pos.is_element_present(pos.controls['function keys']['back']):
            pos.click("back")
        pos.sign_on()
        pos.click("lock")
        if not pos.is_element_present(pos.controls['function keys']['network']):
            tc_fail("Network button was not found in the main menu")

    @test
    def buttons_in_network_menu_locked(self):
        """
        Merlin-1413, Verify buttons are noy present in Network Menu when registered is locked
        """
        pos.sign_on()
        pos.click("lock")
        pos.click("network")
        if pos.is_element_present(pos.controls['function keys']['network keys']['host function']):
            pos.click("back")
            tc_fail("Host Function button was found in the Network menu")
        if pos.is_element_present(pos.controls['function keys']['network keys']['balance inquiry']):
            pos.click("back")
            tc_fail("Balance Inquiry button was found in the Network menu")
        if pos.is_element_present(pos.controls['function keys']['network keys']['e-mail']):
            pos.click("back")
            tc_fail("E-mail button was found in the Network menu")
        if pos.is_element_present(pos.controls['function keys']['network keys']['de-activate card']):
            pos.click("back")
            tc_fail("De-activate Card button was found in the Network menu")
        pos.click("back")

    @test
    def network_in_main_menu_signed_off(self):
        """
        Merlin-1413, Verify Network button is found in the main menu when signed off
        """
        if pos.is_element_present(pos.controls['function keys']['back']):
            pos.click("back")
        pos.sign_on()
        if pos._is_signed_on():
            pos.sign_off()
        if not pos.is_element_present(pos.controls['function keys']['network']):
            tc_fail("Network button was not found in the main menu")
    
    @test
    def buttons_in_network_signed_off(self):
        """
        Merlin-1413, Verify buttons are not present in Network Menu when signed off
        """
        if pos._is_signed_on():
            pos.sign_off()
        pos.click("network")
        if pos.is_element_present(pos.controls['function keys']['network keys']['host function']):
            pos.click("back")
            tc_fail("Host Function button was found in the Network menu")
        if pos.is_element_present(pos.controls['function keys']['network keys']['balance inquiry']):
            pos.click("back")
            tc_fail("Balance Inquiry button not found in the Network menu")
        if pos.is_element_present(pos.controls['function keys']['network keys']['e-mail']):
            pos.click("back")
            tc_fail("E-mail button was found in the Network menu")
        if pos.is_element_present(pos.controls['function keys']['network keys']['de-activate card']):
            pos.click("back")
            tc_fail("De-activate Card button was found in the Network menu")
        pos.click("back")


    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        if pos.is_element_present(pos.controls['function keys']['back']):
            pos.click("back")
        if pos._is_signed_on():
            pos.sign_off()
        pos.close()
