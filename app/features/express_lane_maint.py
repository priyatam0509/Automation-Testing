from app.framework import mws, Navi
import logging
import pywinauto
import time, datetime
import copy
from app.framework import OCR
from app.util import constants

log = logging.getLogger()

class ExpressLaneMaintenance:
    def __init__(self):
        ExpressLaneMaintenance.navigate_to()
        self.order = { "Branding": ["Cashier Button Gradient", "Start Button Gradient"],
                       "Fuel Configuration": ["Allow fuel sales"] }

    @staticmethod
    def navigate_to():
        return Navi.navigate_to("Express Lane Maintenance")

    def configure(self, config):
        """
        Configure settings in Express Lane Maintenance.
        Args:
            config: (dict) A dictionary of tabs, controls and what to set their values to. See controls.json for names of controls.
        Returns:
            bool: True if success, False if failure
        Examples:
            >>> cfg = { "General": { "Express Lane 1": "POSCLIENT001", "Display thank you for": "10" }, 
                "Branding": { "Logo": "MiniMart.png", "Background Color": "Orange", "Start Button Gradient": True, "Start Button 2": "White" },
                "Advertisement": { "Available Media File(s)": ["image1.jpeg", "image2.jpeg", "image3.jpeg"], "Selected Media File(s)": ["image4.jpeg", "image5.jpeg"] }}
            >>> express_lane_maint.ExpressLaneMaintenance().configure(cfg)
            True
        """
        # Handle ordered stuff first
        for tab in self.order:
            mws.select_tab(tab)
            for item in self.order[tab]:
                try:
                    if not mws.set_value(item, config[tab][item]):
                        mws.click_toolbar("Exit")
                        mws.click_toolbar("No")
                        return False
                except KeyError:
                    continue
            
        for tab in config:
            if tab == "Advertisement":
                mws.select_tab("Advertisement")
                available = []
                selected = []
                for key, value in config[tab].items():
                    if "available" in key.lower():
                        available = value
                    elif "selected" in key.lower():
                        selected = value
                    else:
                        if not mws.set_value(key, value, tab):
                            mws.click_toolbar("Exit")
                            mws.click_toolbar("No")
                            return False
                if not self._configure_advertisement(available, selected):
                    mws.click_toolbar("Exit")
                    mws.click_toolbar("No")
                    return False
                continue
            for key, value in config[tab].items():
                mws.select_tab(tab)
                if not mws.set_value(key, value):
                    mws.click_toolbar("Exit")
                    mws.click_toolbar("No")
                    return False

        try:
            mws.click_toolbar("Save", main=True)               
        except mws.ConnException:
            self.log.error(f"Didn't return to main menu after saving Express Lane Maintenance. Top bar message: {mws.get_top_bar_text()}")
            mws.recover()
            return False

        return True

    def _configure_advertisement(self, available=[], selected=[]):
        """
        Configure media files in the advertisement tab, dragging them around as needed.
        Args:
            available: (list) The desired configuration of the Available Media File(s) list.
            selected: (list) The desired configuration of the Selected Media File(s) list.
        Returns:
            bool: True if success, False if failure
        Examples:
            >>> _configure_advertisement(selected=["image1.jpeg", "image2.jpeg", "image3.jpeg"])
            True
            >>> _configure_advertisement(["available.jpeg", "available2.jpeg"], ["selected.jpeg", "selected2.jpeg"])
            True
            >>> _configure_advertisement(["image.jpeg"], ["image.jpeg"]) # Can't have same file in both lists
            False
        """
        available_name = "Available Media File(s)"
        selected_name = "Selected Media File(s)"
        start_available = mws.get_value(available_name)
        start_selected = mws.get_value(selected_name)

        # Configure available media files
        for file in available:
            if [file] in start_selected:
                mws.click_and_drag(file, available_name, start_list=selected_name)
            elif [file] not in start_available:
                log.error(f"{file} not found in Selected or Available Media File(s). Aborting configuration.")
                return False
            else:
                log.debug(f"{file} already in Available Media File(s). Not moving it.")

        # Configure selected media files
        for file in selected:
            if [file] in start_available:
                mws.click_and_drag(file, selected_name, start_list=available_name)
            elif [file] not in start_selected:
                log.error(f"{file} not found in Selected or Available Media File(s). Aborting configuration.")
                return False
            else:
                log.debug(f"{file} already in Selected Media File(s). Not moving it.")

        # Verify the configuration was successful
        ret = True
        end_available = mws.get_value(available_name)
        end_selected = mws.get_value(selected_name)
        for file in available:
            if [file] not in end_available:
                log.error(f"{file} was not in Available Media File(s) after configuration.")
                ret = False
        for file in selected:
            if [file] not in end_selected:
                log.error(f"{file} was not in Selected Media File(s) after configuration.")
                ret = False

        return ret
