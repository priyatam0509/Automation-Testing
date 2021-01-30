from app import mws
from app import Navi, system
import logging, time

class Item:
    def __init__(self):
        Item.navigate_to()
        self.log = logging.getLogger()

    @staticmethod
    def navigate_to():
        return Navi.navigate_to("Item")
        
    def add(self, config, overwrite=False):
        """
        Adds an item for the user.
        Args:
            config: A dictionary of controls so the user can add the information that
                      they need to. This is according to the schema in controls.json.
            overwrite: If an item exists and overwrite is True, the item will be overwritten.
                       If overwrite is False and the item exists, return False.
                       If the item doesn't exist (whether overwrite is True or False), Add 
                       the item.
        Returns:
            True: If the item was successfully added.
            False: If something went wrong with adding the item (will be logged).
        Example:
            >>> cfg = {
                    "General": {
                        "PLU/UPC": "123",
                        "Description": "Thingy",
                        "Department": "Dept 1",
                        "per unit": "500"
                        },
                    "Scan Codes": {
                        "Add": ["201234005001", "201234002505"],
                        "Expand UPCE": True
                        },
                    "Linked Items": {
                        "Add": ["1"]
                        },
                    "Options": {
                        "Food Stampable": True,
                        "Quantity Allowed": False,
                        "Return Price": "500",
                        "Tax Group": "Sales Tax"
                        },
                    "Qualifiers": {
                        "Qualifier Group": "Test Group",
                        "6-Pack": {
                            "General": {
                                "Description": "6 Thingies",
                                "per unit": "2000"
                                },
                            "Options": {
                                "Return Price": "2000"
                                }
                            }
                        },
                    "Tender Restrictions": {
                        "giftCertificates": True,
                        "driveOff": True
                        }
                    }
            >>> Item().add(cfg)
            True
        """
        #Clicking the "Search" button
        mws.click_toolbar("Search")
        #Searching the List View for the item:
        item = config["General"]["PLU/UPC"]
        item_found = mws.set_value("Items", [item])
        #If overwrite is True and we find the item click Change:
        if overwrite and item_found:
            mws.click_toolbar("Change")
        #Else if we did not find the item, click Add
        elif not item_found:
            mws.click_toolbar("Add")
        #Else We found the item and overwrite is False, return False
        else:
            self.log.warning(f"Item PLU: {config['General']['PLU/UPC']} was found.")
            self.log.warning("Could not add item.")
            return False

        if not self._configure_tabs(config, overwrite):
            return False

        mws.click_toolbar("Save")
        msg = mws.get_top_bar_text()
        if msg:
            self.log.error(f"Got an error message when saving item {config['General']['PLU/UPC']}: {msg}")
            return False

        return True

    def change(self, item_plu, config):
        """
        Changes an item's information for the user.
        Args:
            item_plu: The PLU/UPC of the item that needs to be changed.
            config: A dictionary of controls so the user can add the information that
                      they need to. This is according to the schema in controls.json.
        Returns:
            True: If the item's information was succesfully changed.
            False: If something went wrong while changing the item's information (will be logged).
        Example:
            >>> cfg = { "General": {
                            "Description": "Mabob",
                            "Department": "Dept 2",
                            "per unit": "555" },
                        "Scan Codes": {
                            "Add": ["201234005551", "201234010005"],
                            "Remove": ["201234002505"],
                            "Expand UPCE": False },
                        "Linked Items": {
                            "Add": ["321"],
                            "Remove": ["1"] },
                        "Options": {
                            "Food Stampable": False,
                            "Quantity Allowed": True,
                            "Quantity Required": True,
                            "Return Price": "555" },
                        "Qualifiers": {
                            "6-Pack": {
                                "General": {
                                    "Description": "6 Mabobs",
                                    "per unit": "2100" },
                                "Options": {
                                    "Return Price": "2100" } } },
                        "Tender Restrictions": {
                            "giftCertificates": False,
                            "radioFrequency": True }
                        }
        """
        mws.set_value("PLU/UPC", item_plu)
        mws.click_toolbar("Search")
        mws.click_toolbar("Change")

        if not self._configure_tabs(config):
            return False

        mws.click_toolbar("Save")
        msg = mws.get_top_bar_text()
        if msg:
            self.log.error(f"Got an error message when saving item {config['General']['PLU/UPC']}: {msg}")
            return False

        return True

    def _configure_tabs(self, config, overwrite=False):
        """
        Helper function to configure fields in the item configuration menu.
        Args:
            config: A dictionary of controls so the user can add the information that
                      they need to. This is according to the schema in controls.json.
            overwrite: If True, skip setting the PLU/UPC field.
        Returns:
            True: If the item's information was succesfully changed.
            False: If something went wrong while changing the item's information (will be logged).
        """
        for tab in config:
            mws.select_tab(tab)

            if tab == "Qualifiers":
                for key, value in config[tab].items():
                    if type(value) != dict: # For setting the qualifier group
                        if not mws.set_value(key, value, tab):
                            self.log.error(f"Could not set {key} with {value} on the {tab} tab.")
                            return False
                        if key == "Qualifier Group" and "remove all currently assigned qualifiers" in mws.get_top_bar_text():
                            mws.click_toolbar("Yes")
                    else: # Configure a qualifier
                        mws.set_value("Qualifiers", key, tab="Qualifiers")
                        mws.search_click_ocr("Change")
                        for key2, value2 in value.items():
                                mws.select_tab(key2, tolerance="000000") # 0 tolerance is needed for this to work
                                for key3, value3 in value2.items():
                                    self.log.info(f"Attempting to set up {key2} with {value2} on {tab} tab.")
                                    if not mws.set_value(key3, value3, tab):
                                        self.log.error(f"Could not set {key3} with {value3} on the {key2} tab within Qualifiers.")
                                        return False
                        mws.click_toolbar("Back")

            elif tab == "Scan Codes":
                for key, value in config[tab].items():
                    if key == "Add":
                        for code in config[tab][key]:
                            mws.set_value("Enter Scan Code", code)
                            if mws.is_high_resolution():
                                mws.search_click_ocr("Add", bbox=(294,388,370,408), tolerance='808080')
                            else:
                                mws.search_click_ocr("Add", bbox=(215,287,260,305), tolerance='808080')
                            msg = mws.get_top_bar_text()
                            if msg:
                                self.log.error(f"Error adding scan code {code}: {msg}")
                                return False
                    elif key == "Remove":
                        for code in config[tab][key]:
                            if not mws.set_value("Codes", code):
                                self.log.error(f"Item does not have scan code {code}. Could not remove.")
                                return False
                            mws.search_click_ocr("Remove")
                    elif not mws.set_value(key, value, tab): # This is just for Expand UPCE at the moment
                        self.log.error(f"Could not set {key} with {value} on the {tab} tab.")

            elif tab == "Linked Items":
                if "Add" in config[tab]:
                    for plu in config[tab]["Add"]:
                        mws.set_value("Enter PLU", plu)
                        mws.search_click_ocr("Add")
                        msg = mws.get_top_bar_text()
                        if msg:
                                self.log.error(f"Error adding linked item {PLU}: {msg}")
                                return False
                if "Remove" in config[tab]:
                    for code in config[tab]["Remove"]:
                        if not mws.set_value("PLUs", plu):
                            self.log.error(f"Item does not have linked item {plu}. Could not remove.")
                            return False
                        mws.search_click_ocr("Remove")

            elif tab == "Tender Restrictions":
                if not mws.config_flexgrid("Tender List", config[tab], 238):
                    self.log.error("Error configuring Tender Restrictions list.")
                    return False

            else: # General and Options tabs
                for key, value in config[tab].items():
                    if not mws.set_value(key, value, tab):
                        if key == "PLU/UPC" and overwrite: continue
                        self.log.error(f"Could not set {key} with {value} on the {tab} tab.")
                        return False

        return True


    def delete(self, item_plu):
        #TODO: Something with Database dumping...
        return