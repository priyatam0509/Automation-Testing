from app.framework import mws, Navi
import logging
import pywinauto
import time, datetime
import copy
from app.framework import OCR
from app.util import constants

log = logging.getLogger()

class PINPadAdvertisement:
    def __init__(self):
        PINPadAdvertisement.navigate_to()

    @staticmethod
    def navigate_to():
        return Navi.navigate_to("PIN Pad Advertisement")

    def configure(self, available=[], selected=[], interval=None):
        """
        Configure media files in the advertisement tab, dragging them around as needed.
        Args:
            available: (list) The desired configuration of the Available Media File(s) list.
            selected: (list) The desired configuration of the Selected Media File(s) list.
        Returns:
            bool: True if success, False if failure
        Examples:
            >>> configure(selected=["image1.jpeg", "image2.jpeg", "image3.jpeg"], interval=20)
            True
            >>> configure("available.jpeg", "available2.jpeg"], ["selected.jpeg", "selected2.jpeg"])
            True
            >>> configure(["image.jpeg"], ["image.jpeg"]) # Can't have same file in both lists
            False
        """
        # Set interval
        if interval:
            if not mws.set_value("Image display interval", interval):
                return False

        available_name = "Available Image File(s)"
        selected_name = "Selected Image File(s)"
        start_available = mws.get_value(available_name)
        start_selected = mws.get_value(selected_name)

        # Configure available media files
        for file in available:
            if [file] in start_selected:
                mws.click_and_drag(file, available_name, start_list=selected_name)
            elif [file] not in start_available:
                log.error(f"{file} not found in {available_name} or {selected_name}. Aborting configuration.")
                return False
            else:
                log.debug(f"{file} already in Available Media File(s). Not moving it.")

        # Configure selected media files
        for file in selected:
            if [file] in start_available:
                mws.click_and_drag(file, selected_name, start_list=available_name)
            elif [file] not in start_selected:
                log.error(f"{file} not found in {available_name} or {selected_name}. Aborting configuration.")
                return False
            else:
                log.debug(f"{file} already in {selected_name}. Not moving it.")

        # Verify the configuration was successful
        ret = True
        end_available = mws.get_value(available_name)
        end_selected = mws.get_value(selected_name)
        for file in available:
            if [file] not in end_available:
                log.error(f"{file} was not in {available_name} after configuration.")
                ret = False
        for file in selected:
            if [file] not in end_selected:
                log.error(f"{file} was not in {selected_name} after configuration.")
                ret = False

        return ret