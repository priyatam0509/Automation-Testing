"""
    File name: POS_Clock_In.py
    Tags:
    Description: Script for testing clock in/out functionality in HTML POS.
    Author: David Mayes
    Date created: 2020-07-02
    Date last modified: 
    Python Version: 3.7
"""

import logging, time
from app import Navi, mws, pos, system
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app.features import store_options

default_timeout = 5

class POS_Clock_In():
    """
    Holds test cases
    """

    def __init__(self):
        """
        Initializes the POS_Clock_In
        """
        # The logging object. 
        # Example: self.log.info(f"Current value of var: {my_var}")
        self.log = logging.getLogger()
        self.time_clock = pos.controls['function keys']['time clock']
        self.appear_wait_time = 5

    @setup
    def setup(self):
        """
        Performs initialization
        """
        # if not system.restore_snapshot():
        #     self.log.debug("No snapshot to restore, if this is not expected please contact automation team")
        mws.sign_on()

        # Add store info so the time clock setting can be changed and saved
        store_options_config = {
            "General": {
                "Store Number": "22",
                "Store Name": "Lettuce",
                "Address Line 1": "Tomato",
                "Address Line 2": "H-eye-nz Fifty Seven",
                "Address Line 3": "French Fried Potatoes",
                "City": "Big Kosher Pickle",
                "State": "CD",
                "Postal Code": "11111",
                "Store": "(111)111-1111",
                "Help Desk": "(111)111-1111"
            },
            "TimeClock": {
                "Enable Clock In/Out": True,
			    "Require Clock In Reason": True,
            }
        }

        s = store_options.StoreOptions()

        s.setup(store_options_config)
        self._settings_saved()
        Navi.navigate_to("Store Options")
        mws.select_tab("TimeClock")
        if not mws.select("Clock In Reasons", "tryna get paid yo"):
            mws.click("Add")
            mws.set_value("Clock In Reason", "tryna get paid yo")
            mws.click("Update List", tab="TimeClock")
            mws.click_toolbar("Save")
            if not self._settings_saved(timeout=3):
                mws.click_toolbar("Yes", main=True)
        else:
            mws.click_toolbar("Cancel")

        self._settings_saved()

        pos.connect()


    @test
    def buttons_appear(self):
        """
        Make sure that the HTML POS buttons appear after
        enabling clock in/clock out in the MWS
        """
        # Enable time clock
        self.log.info("Enabling time clock...")
        s = store_options.StoreOptions()
        
        config = {
            "TimeClock": {
                "Enable Clock In/Out": True,
                "Require Clock In Reason": False
            }
        }

        s.setup(config)

        if not self._settings_saved():
            tc_fail("Failed to save time clock setting.")

        # Test whether time clock appears on sign on screen
        self.log.info("Making sure time clock button appears on relevant screens...")

        if self._on_main_screen():
            if not pos.is_element_present(self.time_clock, timeout=self.appear_wait_time):
                tc_fail("Time clock button did not appear on the main idle screen.")
            self.log.info("Time clock button appeared on the main idle screen!")
            if not self._return_to_signon_screen():
                tc_fail("Failed to sign off and return to the sign on screen.")
            if not pos.is_element_present(self.time_clock, timeout=self.appear_wait_time):
                tc_fail("Time clock button did not appear on the sign on screen.")
            self.log.info("Time clock button appeared on the sign on screen!")
        elif self._on_signon_screen():
            if not pos.is_element_present(self.time_clock, timeout=self.appear_wait_time):
                tc_fail("Time clock button did not appear on signon screen.")
            self.log.info("Time clock button appeared on the main idle screen!")
            if not self._return_to_main_screen():
                tc_fail("Failed to sign on and return to the main idle screen.")
            if not pos.is_element_present(self.time_clock, timeout=self.appear_wait_time):
                tc_fail("Time clock button did not appear on the main idle screen.")
            self.log.info("Time clock button appeared on the main idle screen screen!")
        else:
            tc_fail("On an unknown screen.")


    @test
    def cancel_clock_in_signed_off(self):
        """
        Cancel a clocked in while on the sign on screen
        """
        # Setup
        if not self._return_to_signon_screen():
            tc_fail("Was unable to navigate to the sign on screen before starting the test case.")
        self.log.info("Verified HTML POS is on the sign on screen...")

        # Test stuff
        self.log.info("Attempting to start a clock in then cancel it...")

        if not self._clock_in(cancel=True):
            tc_fail("Failed to cancel clock in.")

        self.log.info("Successfully cancelled clock in while signed off!")

    
    @test
    def clock_in_signed_off(self):
        """
        Clock in while on the sign on screen
        """
        # Setup
        if not self._return_to_signon_screen():
            tc_fail("Was unable to navigate to the sign on screen before starting the test case.")
        self.log.info("Verified HTML POS is on the sign on screen...")

        # Test stuff
        self.log.info("Attempting to clock in...")
        
        if not self._clock_in():
            tc_fail("Failed to clock in.")

        self.log.info("Successfully clocked in while signed off!")


    @test
    def cancel_clock_out_signed_off(self):
        """
        Cancel clock out while on the sign on screen
        """
        # Setup
        if not self._return_to_signon_screen():
            tc_fail("Was unable to navigate to the sign on screen before starting the test case.")
        self.log.info("Verified HTML POS is on the sign on screen...")

        # Test stuff
        self.log.info("Attempting to start a clock out then cancel it...")

        if not self._clock_out(cancel=True):
            tc_fail("Failed to cancel clock out.")

        self.log.info("Successfully cancelled clock out while signed off!")

    
    @test
    def clock_out_signed_off(self):
        """
        Clock out while on the sign on screen
        """
        # Setup
        if not self._return_to_signon_screen():
            tc_fail("Was unable to navigate to the sign on screen before starting the test case.")
        self.log.info("Verified HTML POS is on the sign on screen...")

        # Test stuff
        self.log.info("Attempting to clock out...")

        if not self._clock_out():
            tc_fail("Failed to clock out.")

        self.log.info("Successfully clocked out while signed off!")


    @test
    def cancel_clock_in_signed_on(self):
        """
        Cancel clock in while signed on
        """
        # Setup
        if not self._return_to_main_screen():
            tc_fail("Was unable to navigate to the main idle screen before starting the test case.")
        self.log.info("Verified HTML POS is on the main idle screen...")

        # Test stuff
        self.log.info("Attempting to start a clock in then cancel it...")

        if not self._clock_in(cancel=True):
            tc_fail("Failed to cancel clock in.")

        self.log.info("Successfully cancelled clock in while signed on!")
    

    @test
    def clock_in_signed_on(self):
        """
        Clock in while signed on
        """
        # Setup
        if not self._return_to_main_screen():
            tc_fail("Was unable to navigate to the main idle screen before starting the test case.")
        self.log.info("Verified HTML POS is on the main idle screen...")

        # Test stuff
        self.log.info("Attempting to clock in...")

        if not self._clock_in():
            tc_fail("Failed to clock in.")

        self.log.info("Successfully clocked in while signed on!")
    

    @test
    def cancel_clock_out_signed_on(self):
        """
        Cancel clock out while signed on
        """
        # Setup
        if not self._return_to_main_screen():
            tc_fail("Was unable to navigate to the main idle screen before starting the test case.")
        self.log.info("Verified HTML POS is on the main idle screen...")

        # Test stuff
        self.log.info("Attempting to start a clock out then cancel it...")

        if not self._clock_out(cancel=True):
            tc_fail("Failed to cancel clock out.")

        self.log.info("Successfully cancelled clock out while signed on!")

    
    @test
    def clock_out_signed_on(self):
        """
        Clock out while signed on
        """
        # Setup
        if not self._return_to_main_screen():
            tc_fail("Was unable to navigate to the main idle screen before starting the test case.")
        self.log.info("Verified HTML POS is on the main idle screen...")

        # Test stuff
        self.log.info("Attempting to clock out...")

        if not self._clock_out():
            tc_fail("Failed to clock out.")

        self.log.info("Successfully clocked out while signed on!")

    
    @test
    def with_reason_code(self):
        """
        Clock in with reason codes enabled
        """
        # Enable reason codes
        self.log.info("Enabling time clock...")
        s = store_options.StoreOptions()
        
        config = {
            "TimeClock": {
                "Enable Clock In/Out": True,
                "Require Clock In Reason": True
            }
        }

        s.setup(config)

        if not self._settings_saved():
            tc_fail("Failed to save time clock setting.")

        # Setup
        if not self._return_to_main_screen():
            tc_fail("Was unable to navigate to the main idle screen before starting the test case.")
        self.log.info("Verified HTML POS is on the main idle screen...")

        # Test stuff
        self.log.info("Attempting to clock in...")

        if not self._clock_in(reason="tryna get paid yo"):
            tc_fail("Failed to clock in.")

        self.log.info("Successfully clocked in with reason code!")


    @test
    def buttons_disappear(self):
        """
        Make sure that the HTML POS buttons disappear after
        disabling clock in/clock out in the MWS
        """
        # Disable time clock
        # Enable time clock
        self.log.info("Enabling time clock...")
        s = store_options.StoreOptions()
        
        config = {
            "TimeClock": {
                "Enable Clock In/Out": False
            }
        }

        s.setup(config)

        if not self._settings_saved():
            tc_fail("Failed to save time clock setting.")

        # Test whether time clock appears on sign on screen
        self.log.info("Making sure time clock button does not appear on relevant screens...")

        if self._on_main_screen():
            if self._is_not_present(self.time_clock, timeout=self.appear_wait_time):
                self.log.info("Time clock disappeared on the main idle screen!")
            else:
                tc_fail("Time clock did not disappear on the main idle screen.")
            if not self._return_to_signon_screen():
                tc_fail("Failed to sign off and return to the sign on screen.")
            if self._is_not_present(self.time_clock, timeout=self.appear_wait_time):
                self.log.info("Time clock disappeared on the sign on screen!")
            else:
                tc_fail("Time clock did not disappear on the sign on screen.")
        elif self._on_signon_screen():
            if self._is_not_present(self.time_clock, timeout=self.appear_wait_time):
                self.log.info("Time clock disappeared on the sign on screen!")
            else:
                tc_fail("Time clock did not disappear on the sign on screen.")
            if not self._return_to_main_screen():
                tc_fail("Failed to sign on and return to the main idle screen.")
            if self._is_not_present(self.time_clock, timeout=self.appear_wait_time):
                self.log.info("Time clock disappeared on the main idle screen!")
            else:
                tc_fail("Time clock did not disappear on the main idle screen.")
        else:
            tc_fail("On an unknown screen.")


    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        # Enable time clock to clock out for teardown
        sa = store_options.StoreOptions()

        config = {
            "TimeClock": {
                "Enable Clock In/Out": True
            }
        }

        sa.setup(config)

        # Clock HTML POS out (setup for running script again)
        self._clock_out()

        # Remove reason
        Navi.navigate_to("Store Options")
        mws.select_tab("TimeClock")
        mws.set_value("Enable Clock In/Out", True)
        if mws.select("Clock In Reasons", "tryna get paid yo"):
            mws.click("Remove")
            mws.click_toolbar("Save")
            if not self._settings_saved(timeout=3):
                mws.click_toolbar("Yes", main=True)
        else:
            mws.click_toolbar("Cancel")
            if not self._settings_saved(timeout=3):
                mws.click_toolbar("No", main=True)

        self._settings_saved()

        # Disable time clock
        sb = store_options.StoreOptions()
        
        config = {
            "TimeClock": {
                "Enable Clock In/Out": False
            }
        }

        sb.setup(config)

        if not self._settings_saved():
            tc_fail("Failed to save time clock setting.")

        pos.close()


    def _on_main_screen(self, timeout=default_timeout):
        """
        Helper function to determine if HTML POS is on the
        main idle screen
        """
        return pos.is_element_present(pos.controls["function keys"]["paid in"], timeout=timeout)


    def _on_signon_screen(self, timeout=default_timeout):
        """
        Helper function to determine if HTML POS
        is on the main signed off screen
        """
        return pos.is_element_present(pos.controls["function keys"]["sign on"], timeout=timeout)
    

    def _return_to_main_screen(self, timeout=2):
        """
        Helper function for returning to the main idle screen of HTML POS
        """
        # Normal cases
        if self._on_signon_screen():
            pos.click("sign on")
            pos.enter_keypad("91", after="enter")
            pos.is_element_present(pos.controls['keyboard']['shift'], timeout=default_timeout)
            pos.enter_keyboard("91", after="ok")
            if pos.read_message_box(timeout=default_timeout):
                self._click_prompt("no")
            if pos.read_status_line(timeout=default_timeout):
                pos.enter_keypad("1000", after="enter")
        if self._on_main_screen():
            self.log.info("Successfully returned to the main idle screen...")
            return True

        # Less likely cases
        if pos.read_message_box(timeout):
            pos.click("no")
        msg = pos.read_status_line()
        if not msg == None:
            if "user" in msg.lower():
                pos.click("cancel")
        if pos.is_element_present(pos.controls['keyboard']['shift'], timeout):
            pos.click("cancel")
        if self._on_main_screen():
            self.log.info("Successfully returned to the main idle screen...")
            return True
        else:
            if self._on_signon_screen():
                pos.click("sign on")
                pos.enter_keypad("91", after="enter")
                pos.is_element_present(pos.controls['keyboard']['shift'], timeout=default_timeout)
                pos.enter_keyboard("91", after="ok")
                if pos.read_message_box(timeout=default_timeout):
                    self._click_prompt("no")
                if pos.read_status_line(timeout=default_timeout):
                    pos.enter_keypad("1000", after="enter")
            if self._on_main_screen():
                self.log.info("Successfully returned to the main idle screen...")
                return True

        self.log.warning("Failed to return to the main idle screen!")
        return False

    
    def _return_to_signon_screen(self):
        """
        Helper function for return to the sign on screen of HTML POS
        """
        if pos.read_message_box():
            pos.click("no")
        msg = pos.read_status_line()
        if not msg == None:
            if "user" in msg.lower():
                pos.click("cancel")
        if pos.is_element_present(pos.controls['keyboard']['shift']):
            pos.click("cancel")
        if self._on_main_screen():
            pos.sign_off()
        if self._on_signon_screen():
            self.log.info("Successfully returned to the sign on screen...")
            return True
        self.log.warning("Failed to return to the sign on screen!")
        return False


    def _click_prompt(self, button, timeout=default_timeout):
        """
        Helper function for clicking a button on a prompt once it appears
        """
        button = str(button)
        start_time = time.time()
        while time.time() - start_time <= timeout:
            msg = pos.read_message_box(timeout/20.0)
            if msg != None:
                pos.click(button)


    def _settings_saved(self, timeout=20):
        """
        Helper function to wait for the MWS to save a setting
        """
        start_time = time.time()
        while time.time() - start_time <= timeout:
            if mws.get_top_bar_text() == '' or mws.get_top_bar_text() == None:
                return True
        else:
            return False

    
    def _is_not_present(self, control, timeout=default_timeout):
        """
        Helper function for returning as soon as an element is not present
        """
        start_time = time.time()
        while time.time() - start_time <= timeout:
            if not pos.is_element_present(control, timeout=timeout/20.0):
                return True
        else:
            return False


    def _clock_in(self, cancel=False, reason=None):
        """
        Helper function for clocking in via the Time Clock button
        """
        # Detect what screen HTML POS is on initially
        # (important for later)
        if self._on_main_screen():
             screen = "main"
        elif self._on_signon_screen():
            screen = "signon"
        
        # Enter credentials
        if not pos.click("Time Clock"):
            self.log.warning("Failed to click the Time Clock button!")
            return False
        pos.enter_keypad("91", after="enter")
        pos.is_element_present(pos.controls['keyboard']['shift'], timeout=default_timeout)
        pos.enter_keyboard("91", after="ok")

        # Complete clock in
        if reason != None:
            if not pos.click(str(reason)):
                self.log.warning("Failed to select the reason '" + str(reason) + "' and clock in.")
                return False
        else:
            msg = pos.read_message_box()
            if msg == None:
                self.log.warning("No message box appeared asking whether you would like to clock in!")
                return False
            elif not "clock in" in msg.lower():
                self.log.warning("Message box did not contain the words 'clock in'.  Instead, it said: " + msg)
                return False
            if cancel:
                pos.click("no")
            else:
                pos.click("yes")

        # Make sure clock in was successful
        if screen == "main":
            if self._on_main_screen():
                self.log.info("Clock in was successful...")
                return True
            elif cancel:
                self.log.warning("Did not navigate to the main screen after clicking no at clock in!")
            elif not cancel:
                self.log.warning("Did not navigate to the main screen after clicking yes at clock in!")
        elif screen == "signon":
            if self._on_signon_screen():
                self.log.info("Clock in was successful...")
                return True
            elif cancel:
                self.log.warning("Did not navigate to the sign on screen after clicking no at clock in!")
            elif not cancel:
                self.log.warning("Did not navigate to the sign on screen after clicking yes at clock in!")
        return False


    def _clock_out(self, cancel=False):
        """
        Helper function for clocking out via the Time Clock button
        """
        # Detect what screen HTML POS is on initially
        # (important for later)
        if self._on_main_screen():
             screen = "main"
        elif self._on_signon_screen():
            screen = "signon"

        # Enter credentials
        if not pos.click("Time Clock"):
            self.log.warning("Failed to click the Time Clock button!")
            return False
        pos.enter_keypad("91", after="enter")
        pos.is_element_present(pos.controls['keyboard']['shift'], timeout=default_timeout)
        pos.enter_keyboard("91", after="ok")
        msg = pos.read_message_box()
        if msg == None:
            self.log.warning("No message box appeared asking whether you would like to clock out!")
            return False
        elif not "clock out" in msg.lower():
            self.log.warning("Message box did not contain the words 'clock out'.  Instead, it said: " + msg)
            return False
        
        # Complete clock out
        if cancel:
            pos.click("no")
        else:
            pos.click("yes")
        

        if screen == "main":
            if not cancel:
                msg = pos.read_message_box()
                if msg == None:
                    self.log.info("Did not ask user to sign off after clocking out while signed on.")
                    return False
                pos.click("ok")
            if self._on_main_screen():
                self.log.info("Clock out was successful...")
                return True
            elif cancel:
                self.log.warning("Did not navigate to the main screen after clicking no at clock out!")
            elif not cancel:
                self.log.warning("Did not navigate to the main screen after clicking yes at clock out!")
        elif screen == "signon":
            if self._on_signon_screen():
                self.log.info("Clock out was successful...")
                return True
            elif cancel:
                self.log.warning("Did not navigate to the sign on screen after clicking no at clock out!")
            elif not cancel:
                self.log.warning("Did not navigate to the sign on screen after clicking yes at clock out!")
        return False