from app import mws, system, Navi
import logging, time

class ThirdPartyDataInterface:
    def __init__(self):
        mws.connect("third party data interface")
        self.log = logging.getLogger()
        self.order = ['Generate Transaction Level Detail','Combine Transaction Level Detail Files','Wetstock Export Enabled']

    @staticmethod
    def navigate_to():
        """
        Navigates to the Third Party Data Interface.
        """
        Navi.navigate_to("third party data interface")

    def configure(self, config):
        """
        Configures the Third Party Data Interface. Adds new Hosts and changes existing Hosts.
        Args:
            config: A dictionary of controls so the user can add the information that
                      they need to. This is according to the schema in controls.json.
        Returns:
            bool: True/False successful configuration
        Examples:
            \code
            tpd_info = {
                "Options":{
                    "Generate Transaction Level Detail": True,
                    "ZIP Individual PJR files at store close": True,
                    "Combine Transaction Level Detail Files": True,
                    "ZIP Combined Transaction Level Detail Files": True,
                    "Export price book when price book is imported from an external source": True,
                    "Export price book on a nightly basis": True,
                    "Copy inbound Item List, Combo And Match files": True,
                    "Wetstock Export Enabled": True,
                    "Export meters by grade": True,
                    "Export meters by dispenser": True,
                    "Export Fuel Prices Every 30 Minutes": True,
                    "Copy end of period XML summary files": True
                },
                "FTP Options":{
                    "Host Desc Test": {
                        "Host Description": "Host Desc Test",
                        "Host Address": "Address Test",
                        "Host Port": "Port Test",
                        "User Name": "User Name Test",
                        "Password": "password",
                        "FTP Folder": "Folder Test",
                        "Use Secure FTP": True,
                        "Send PJR Data": True,
                        "Send Price Book Data": True,
                        "Send Wetstock Data": True,
                        "Send EOP XML Data": True,
                        "Send Fuel Price Data": True
                    }
                }
            }
            tpd.configure(tpd_info)
            True
            \endcode
        """  

        # Takes care of order-sensitive controls on the Options tab
        for field in self.order:
            try:
                value = config["Options"][field]
            except KeyError:
                continue
            if not mws.set_value(field,value):
                return False
            del config["Options"][field]  
        
        # Cycle through tabs
        for tab in config:
            # Configure the rest of the Options tab
            if tab == "Options":
                # OCR sometimes selects the "Options" text found in "FTP Options", so include bbox over "Options" tab
                bbox = (129, 258, 204, 279) if mws.is_high_resolution() else (20, 170, 120, 200) 
                mws.search_click_ocr(tab, bbox)
                for key, value in config[tab].items():
                    if not mws.set_value(key,value,tab):
                        self.log.error(f"Could not set {key} control to {value} in {tab} tab.")
                        return False
            if tab == "FTP Options":
                mws.select_tab(tab)
                for host_desc in config[tab]:
                    # If the specified host was found, select it and change
                    if mws.set_value("FTP Hosts", host_desc):
                        self.log.debug(f"Found '{host_desc}', editing...")
                        mws.click("Change")
                    # If the specified host doesn't exist, add it
                    else: 
                        self.log.debug(f"Could not find '{host_desc}' in host list, adding...")
                        mws.click("Add")
                    # Set fields in the Host Add/Change subtab
                    for key, value in config[tab][host_desc].items():
                        if not mws.set_value(key, value, "FTP Options Add"):
                            self.log.error(f"Could not set {key} control to {value}.")
                            system.takescreenshot()
                            return False
                    mws.click_toolbar("Save")

                msg = mws.get_top_bar_text()
                if msg:
                    self.log.error(f"Got an error when trying to save FTP Options: {msg}")
                    system.takescreenshot()
                    mws.click_toolbar("OK")
                    mws.click_toolbar("Cancel")
                    mws.click_toolbar("NO")
                    return False
            else:
                self.log.debug(f"Configuring Tab: {tab}")
                for key, value in config[tab].items():
                    if not mws.set_value(key, value, tab):
                        self.log.error(f"Could not set {key} with {value} on the {tab} tab.")
                        system.takescreenshot()
                        return False
        try:
            mws.click_toolbar("Save", main=True)
        except mws.ConnException:
            self.log.warning(f"Didn't return to main menu after saving Third Party Data Interface. Top bar message: {mws.get_top_bar_text()}")
            mws.click_toolbar("Exit")
            mws.click_toolbar("No", main=True)
            return False
        return True

    def delete(self, host_desc):
        """
        Deletes the specified host from the FTP Host list.
        Args:
            host_desc: A string matching the Host Description to delete.
        Returns:
            bool: True/False successful deletion
        """
        
        mws.select_tab("FTP Options")
        if not mws.set_value("FTP Hosts",host_desc):
            self.log.error(f"Could not find {host_desc} in list.")
            system.takescreenshot()
            return False
        mws.click("Delete")
        mws.click_toolbar("Yes")
        if mws.set_value("FTP Hosts", host_desc):
            self.log.error(f"{host_desc} still in list, deletion unsuccessful.")
            system.takescreenshot()
            return False
        try:
            mws.click_toolbar("Save", main=True)
        except mws.ConnException:
            self.log.warning(f"Didn't return to main menu after saving Third Party Data Interface. Top bar message: {mws.get_top_bar_text()}")
            mws.click_toolbar("Exit")
            mws.click_toolbar("No", main=True)
            return False
        return True
