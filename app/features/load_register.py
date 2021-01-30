from app.framework import mws, Navi
import logging
import pywinauto
import time, datetime
import copy
from app.framework import OCR
from app.util import constants

log = logging.getLogger()

class LoadRegister:
    def __init__(self):
        LoadRegister.navigate_to()

    @staticmethod
    def navigate_to():
        return Navi.navigate_to("Load Register")

    def load_register(self):
        """
        Reload register options.
        Returns:
            bool: Success/failure
        """
        msg = mws.get_top_bar_text()
        if msg != "Are you sure you would like to reload register options?":
            log.warning(f"Didn't get register reload prompt. Found message: {msg}")
            return False
        mws.click_toolbar("Yes")
        if not mws.verify_top_bar_text("Message Sent"):
            log.warning(f"Didn't get confirmation message. Found message: {mws.get_top_bar_text()}")
            return False
        return mws.click_toolbar("OK", main=True)

    def get_register_status(self):
        """
        Read the list containing register statuses in Load Register.
        Returns:
            list: A list of lists of strings, with each list containing a row of the status list.
        """
        return mws.get_value("Register Status")
