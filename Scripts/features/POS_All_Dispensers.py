"""
    File name: POS_All_Dispensers.py
    Tags:
    Description: HTML POS script for testing the "Show All Dispensers" button.
    Author: David Mayes
    Date created: 2020-08-03
    Date last modified: 
    Python Version: 3.7
"""

import logging, time
from app import Navi, mws, pos, system
from app.framework.tc_helpers import setup, test, teardown, tc_fail

default_timeout = 5

class POS_All_Dispensers():
    """
    Holds test cases
    """


    def __init__(self):
        """
        Initializes the POS_All_Dispensers class
        """
        # The logging object. 
        # Example: self.log.info(f"Current value of var: {my_var}")
        self.log = logging.getLogger()
        self.show_all_dispensers = pos.controls['function keys']['show all dispensers']
        self.back = pos.controls['show all dispensers']['back']
        self.all_stop = pos.controls['show all dispensers']['all stop']


    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        """
        # if not system.restore_snapshot():
        #     self.log.debug("No snapshot to restore, if this is not expected please contact automation team")
        pos.connect()


    @test
    def test_buttons_present(self):
        """
        Make sure the button is present on the screens where it's supposed to appear
        """        
        # Make sure the buttons exist where they're supposed to
        self.log.info("Checking signed off screen...")
        if not self._return_to_signon_screen():
            tc_fail("Failed to return to the sign on screen.")
        pos.click("dispenser menu")
        if not pos.is_element_present(self.show_all_dispensers):
            tc_fail("Show all dispensers button didn't appear on the sign on screen.")

        self.log.info("Checking dispenser menu screen...")
        if not self._return_to_main_screen():
            tc_fail("Failed to return to the main screen.")
        pos.click("dispenser menu")
        if not pos.is_element_present(self.show_all_dispensers):
            tc_fail("Show all dispensers button didn't appear on the dispenser menu.")

        self.log.info("Checking dispenser screen...")
        if not self._return_to_main_screen():
            tc_fail("Failed to return to the main screen.")
        pos.select_dispenser(1)
        if not pos.is_element_present(self.show_all_dispensers):
            tc_fail("Show all dispensers button didn't appear after selecting a dispenser.")
        

    @test
    def test_back(self):
        """
        Make sure the back button in show all dispensers works
        """
        self.log.info("Executing path: dispenser menu while signed on...")
        if not self._return_to_main_screen():
            tc_fail("Failed to return to the main screen.")
        pos.click("dispenser menu")
        pos.click("show all dispensers")
        pos.click_key(self.back)
        if not pos.is_element_present(self.show_all_dispensers):
            tc_fail("Back button did not return HTML POS to the dispenser menu from show all dispensers while signed on.")

        self.log.info("Executing path: individual dispenser while signed on...")
        pos.select_dispenser(1)
        pos.click("show all dispensers")
        pos.click_key(self.back)
        if not pos.is_element_present(self.show_all_dispensers):
            tc_fail("Back button did not return HTML POS to dispenser 1 from show all dispensers while signed on.")

        self.log.info("Executing path: dispenser menu while signed off...")
        if not self._return_to_signon_screen():
            tc_fail("Failed to return to the sign on screen.")
        pos.click("dispenser menu")
        pos.click("show all dispensers")
        pos.click_key(self.back)
        if not pos.is_element_present(self.show_all_dispensers):
            tc_fail("Back button did not return HTML POS to the dispenser menu from show all dispensers while signed off.")
        
        self.log.info("Executing path: individual dispenser while signed off...")
        pos.select_dispenser(1)
        pos.click("show all dispensers")
        pos.click_key(self.back)
        if not pos.is_element_present(self.show_all_dispensers):
            tc_fail("Back button did not return HTML POS to dispenser 1 from show all dispensers while sgined off.")


    @test
    def test_click_dispenser(self):
        """
        Try clicking a dispenser on the show all dispensers screen
        """
        self.log.info("Navigating to the show all dispensers screen...")
        if not self._return_to_main_screen():
            tc_fail("Failed to return to the main screen.")
        pos.click("dispenser menu")
        pos.click("show all dispensers")

        self.log.info("Clicking a dispenser...")
        pos.select_dispenser(1)

        self.log.info("Returning from selecting dispenser...")
        if not self._return_to_main_screen():
            tc_fail("Failed to return to the main screen.")


    @test
    def test_all_stop(self):
        """
        Make sure all stop works on the show all dispensers screen
        """
        # Returning to happy place
        self.log.info("Navigating to show all dispensers screen...")
        self._return_to_main_screen()
        pos.click("dispenser menu")
        pos.click("show all dispensers")

        # Cancel all stop
        self.log.info("Canceling an all stop...")
        pos.click_key(self.all_stop)
        
        msg = pos.read_message_box(default_timeout)
        if msg == None:
            tc_fail("Message did not appear after clicking the all stop button.")
        if not "stop" in msg.lower():
            tc_fail("Incorrect message appeared in the message box after clicking show all dispensers.  The message displayed was '" + msg + "' when it should have included the word stop.")

        pos.click("no")
        self.log.info("Successfully canceled all stop!")

        # Do an all stop
        self.log.info("Starting an all stop...")
        pos.click_key(self.all_stop)

        msg = pos.read_message_box(default_timeout)
        if msg == None:
            tc_fail("Message did not appear after clicking the all stop button.")
        if not "stop" in msg.lower():
            tc_fail("Incorrect message appeared in the message box after clicking show all dispensers.  The message displayed was '" + msg + "' when it should have included the word stop.")

        pos.click("yes")

        pos.select_dispenser(1)

        temp = pos.read_dispenser_diag()
        if temp != None:
            try:
                dialog = temp["Status"]
            except IndexError:
                dialog = None
        else:
            tc_fail("Unable to read dispenser message.")

        if dialog == None or not "stop" in dialog.lower():
            tc_fail("The message displayed on the dispenser is incorrect.")
        
        self.log.info("Clicking clear all stop...")
        pos.click("all stop")

        msg = pos.read_message_box(default_timeout)
        if msg == None:
            tc_fai("No message box appeared when attempting clear the all stop.")
        elif not "clear" in msg.lower():
            tc_fail("Incorrect message appeared in the message box after clicking clear all stop.  The message displayed was '" + msg + "' when it should have included the word clear.")
        pos.click("yes")

        start_time = time.time()
        while time.time() - start_time <= default_timeout:
            msg = pos.read_message_box(default_timeout/20.0)
            if msg == None:
                time.sleep(default_timeout/20.0)
            elif "authorize" in msg.lower():
                break
        else:
            tc_fail("Proper message did not appear after verifying that you would like to clear the all stop.")
        pos.click("yes")

        if pos.is_element_present(self.show_all_dispensers):
            pos.click("back")
            self.log.info("Successfully completed an all stop!")
        else:
            tc_fail("Did not return to the correct screen after clearing the all stop.")


    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        self._return_to_main_screen()
        pos.close()


    def _on_main_screen(self, timeout=default_timeout):
        """
        Helper function the returns true if HTML POS
        is on its main idle screen
        """
        return pos.is_element_present(pos.controls['function keys']['paid in'], timeout=timeout)

    
    def _return_to_main_screen(self, timeout=default_timeout):
        """
        Helper function for returning to the main idle screen
        of HTML POS
        """
        # Buttons
        sign_on = pos.controls['function keys']['sign on']
        unlock = pos.controls['function keys']['unlock']
        show_all_dispensers_back = pos.controls['show all dispensers']['back']
        stop = pos.controls['function keys']['stop']
        back = pos.controls['function keys']['back']
        
        # Return from various screens
        if self._on_main_screen():
            self.log.info("Currently on the main screen...")
            return True
        if pos.is_element_present(back):
            pos.click('back')
        if pos.is_element_present(sign_on, timeout) or pos.is_element_present(unlock):
            pos.sign_on()
            if self._on_main_screen():
                self.log.info("Succesfully returned to the main screen...")
                return True
        elif pos.is_element_present(show_all_dispensers_back, timeout):
            pos.click_key(show_all_dispensers_back)
            if self._on_main_screen():
                self.log.info("Successfully returned to the main screen...")
                return True
        if pos.is_element_present(stop, timeout):
            pos.click_key(show_all_dispensers_back)
            if self._on_main_screen():
                self.log.info("Successfully returned to the main screen...")
                return True

        if self._on_main_screen():
            self.log.info("Successfully returned to the main screen...")
            return True
        self.log.warning("Was unable to return to the main screen.")
        return False


    def _return_to_signon_screen(self, timeout=default_timeout):
        """
        Helper function for signing off if HTML POS
        is signed on
        """
        # Buttons
        sign_on = pos.controls['function keys']['sign on']
        unlock = pos.controls['function keys']['unlock']
        show_all_dispensers_back = pos.controls['show all dispensers']['back']
        stop = pos.controls['function keys']['stop']
        back = pos.controls['function keys']['back']

        # Sign off from various screens
        if pos.is_element_present(sign_on):
            return True
        elif pos.is_element_present(unlock):
            pos.click('unlock')
            pos.enter_keypad('91', after='enter')
            pos.enter_keypad('91', after='ok')
        if pos.is_element_present(stop):
            pos.click_key(show_all_dispensers_back)
        if pos.is_element_present(back):
            pos.click('back')
        pos.sign_off()

        if pos.is_element_present(sign_on):
            return True
    
        self.log.warning("Failed to return to the sign on screen!")
        return False


    def _on_dispenser_screen(self, timeout=default_timeout):
        """
        Helper function to determine if HTML POS is on a
        dispenser screen
        """
        return pos.is_element_present(pos.controls['function keys']['prepay'], timeout=default_timeout)

            
