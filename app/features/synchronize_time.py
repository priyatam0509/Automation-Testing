from app.framework import mws, Navi
import logging
import pywinauto
import time, datetime
import copy
from app.framework import OCR
from app.util import constants

log = logging.getLogger()

class SynchronizeTime:
    def __init__(self):
        SynchronizeTime.navigate_to()

    @staticmethod
    def navigate_to():
        return Navi.navigate_to("Synchronize Time")

    def sync_time(self, date, time, user, password):
        """
        Set the date and time on the Passport system.
        Note that the object will have to be reinitialized if you wish to use it again following
        a successful use of this function. It may also result in the EDH rebooting if moving date/time backwards.
        Args:
            date: (str) The date to set in mm/dd/yyyy format.
            time: (str) The time to set in hh/mm/ss AM/PM format
            user: (str) SMI username
            password: (str) SMI password
        Returns:
            bool: Success/failure
        """
        def verify_edh_reboot(timeout=300):
            smi_path = constants.SECURITY_MANAGER
            smi_app = pywinauto.application.Application().start(smi_path)
            smi = smi_app['PASSPORTEPS']
            try:
                smi['Disconnected from EDH'].wait('exists visible', 180)
            except:
                log.warning(f"EDH didn't reboot.")
                return False
            try:
                smi['Please Enter Username and Password'].wait('exists visible', 450)
                smi['Edit2'].set_text(user)
                smi['Edit1'].set_text(password)
                smi['Loginbutton'].wait('enabled').click()
                smi['System Managementbutton'].wait('exists enabled', 60)
                smi['Exitbutton'].click()
            except Exception as e:
                log.warning(f"EDH didn't finish rebooting.")
                raise e
                # return False
            smi_app.kill()
            log.info("Giving the EDH another minute to finish rebooting.")
            from time import sleep # avoid collision with time param
            sleep(60)
            return True

        # Verify date and time match the correct format
        if len(date.split(':')[0]) == 1:
            date = f"0{date}" # Add a leading zero to satisfy strptime (%m assumes zero-padded month)
        if len(time.split(':')[0]) == 1:
            time = f"0{time}" # %I assumes zero-padded hour
        try:
            datetime.datetime.strptime(date, "%m/%d/%Y")
        except ValueError:
            log.warning(f"{date} is not a correctly formatted date. Please use mm/dd/yyyy format.")
            return False
        try:
            datetime.datetime.strptime(time, "%I:%M:%S %p")
        except ValueError:
            log.warning(f"{time} is not a correctly formatted time. Please use hh/mm/ss AM/PM format.")
            return False

        # Set fields
        mws.set_text("Date", date)
        # Pretty janky solution for Time field. Can't figure out how to directly set DTPicker20WndClass.
        time.replace(' ', '{RIGHT}') # Need a right keystroke to get to AM/PM
        mws.get_control("Time").click(coords=(10,0)) # Click on the hour segment first
        mws.get_control("Time").send_keystrokes(time) 
        mws.set_text("Username", user)
        mws.set_text("Password", password)

        # Save changes
        mws.click_toolbar("Save")
        msg = mws.get_top_bar_text()
        if msg != "Update Date/Time and broadcast to all registers?":
            log.warning("Got an error attempting to save time sync: {msg}")
            return False
        mws.click_toolbar("Yes")
        # Sometimes we have to reboot EDH - seems to happen when we are moving the date/time backwards
        if mws.verify_top_bar_text("This update will require a reboot of the EDH. Continue?", timeout=5):
            reboot_edh = True
            mws.click_toolbar("Yes")
        if mws.verify_top_bar_text("Updated Date/Time and notified all registers", timeout=30):
            mws.click_toolbar("OK", main=True)
        else:
            log.warning(f"Got an error attempting to save time sync: {mws.get_top_bar_text()}")
            mws.click_toolbar("OK", main=True)
            return False
        if reboot_edh:
            return verify_edh_reboot()
        return True