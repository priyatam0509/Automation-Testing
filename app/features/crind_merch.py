from app import mws
from app import Navi, system
import logging, time

class CRINDMerchandising:

    def __init__(self):
        self.log = logging.getLogger()
        CRINDMerchandising.navigate_to()

    @staticmethod
    def navigate_to():
        """
        Navigates to the CRIND Merchandising Feature Module.
        """
        return Navi.navigate_to("crind merchandising")

    def configure(self, config):
        """
        Changes the fields in the CRIND Merchandising interface and saves. Can also be used to add 
        categories or items without configuring the rest of the module.
        Args:
            config: A dictionary of controls so the user can add the information that
                    they need to. This is according to the schema in controls.json.
                    Categories are passed in as a list of string(s). Items are passed in
                    as a dictionary, with keys specifying category, and values as lists of
                    strings specifying what items to add to each category.
        Returns:
            bool: True/False success condition
        Example:
            # /// code below configures entire module
            crind_merch_info = {
                "General": {
                    "CRIND Merchandising is Enabled": True,
                    "Vendor Name": "Test Name",
                    "Prompt Location": "Before Fueling"
                },
                "Categories": ["Test Category 1", "Test Category 2"],
                "Items": {
                    "Test Category 1": ["1","Item 7","004"],
                    "Test Category 2": ["Item 7", "Item 12"]
                }
            }

            # /// code below just adds a category + items
            crind_merch_info = {
                "Categories": ["Test Category 1"],
                "Items": {
                    "Test Category 1": ["1","Item 7","004"]
                }
            }

            cm = crind_merch.CRINDMerchandising()
            cm.configure(crind_merch_info)
            True
        """
        # Code block below deals with the case in which False is passed for the enable checkbox
        try: 
            # In the case that this control is not specified in config...
            # ...this try/except ensures the program does not fail out
            enable_status = config["General"]["CRIND Merchandising is Enabled"]
            mws.set_value("CRIND Merchandising is Enabled", enable_status)
            if enable_status == False:
                self.log.warning("CRIND Merchandising disabled. Exiting config early...")
                return True
        except:
            pass
        
        self.preload_tabs(["Categories", "Items", "General"])
        
        for tab in config:
            mws.select_tab(tab)
            if tab == "General": 
                for key, value in config[tab].items():
                    if "CRIND Merchandising is Enabled" in key:
                        pass
                    elif not mws.set_value(key, value):
                        self.log.error(f"Could not set {key} to {value} in {tab} tab.")
                        return False

            elif tab == "Categories":
                # Convert categories to a list of strings
                if type(config[tab]) != list:
                    config[tab] = [config[tab]]
                for category in config[tab]:
                    # Check existence
                    if not mws.set_value("Categories list", category):
                        # Add category
                        mws.set_value("Categories edit", category)
                        mws.click("Save",tab)        
                    else:
                        self.log.warning(f"{category} already exists in list. Skipping...")
                        mws.click("Save", tab) # Clicking save deselects any selection

            elif tab == "Items":
                for category, valuelist in config[tab].items():
                    # Select category
                    if not mws.set_value("Select Category", category):
                        self.log.error(f"Could not find {category} in list of categories on {tab} tab. Make sure the category is added in the Categories tab beforehand.")
                        return False
                    for value in valuelist:
                        # Open search list
                        mws.click("Search", tab)
                        #NOTE: set_value() does not correctly identify that a new subtab has been opened, and thus
                        #      does not correctly set controls for the search subtab unless connect() is called agian
                        mws.connect("crind merchandising")
                        # Search for and select item in search list
                        if not mws.set_value("Search List", value):
                            self.log.error(f"Could not find '{value}' in search list.")
                            mws.click_toolbar("Cancel")
                            return False
                        # Check if item is eligible for CRIND sale
                        elif "not eligible" in mws.get_top_bar_text():
                            self.log.warning(f"The item with PLU/Desc: '{value}' is not eligible for CRIND sale and cannot be selected. Skipping...")
                            mws.click_toolbar("OK")
                            mws.click_toolbar("Cancel")
                            time.sleep(1)
                            continue
                        # Add item
                        mws.click("Select")
                        # Check for "item already exists in list" error message
                        if "already exists" in mws.get_top_bar_text():
                            self.log.warning(f"The item with PLU/Desc: '{value}' is already in the PLU list. Skipping...")
                            mws.click_toolbar("OK")
                            # Search button needs some time to load after exiting
                            time.sleep(1)
            else:
                mws.select_tab(tab)
                self.log.warning(f"{tab} tab is unrecognized. Skipping...")
        mws.click_toolbar("Save")
        if "want to save" in mws.get_top_bar_text():
            mws.click_toolbar("Yes")
        return True

    def change_category(self, name, changed_name):
        """
        Changes the name of a category in the CRIND Merchandising interface.
        Must be called from within the CRIND Merchandising module.
        Args:
            name: A string specifying what to look for in the list of categories.
            changed_name: A string specifying what to rename the category to.
        Returns:
            bool: True/False success condition
        Example:
            cm = crind_merch.CRINDMerchandising()
            cm.change_category("Test Category","Edited Category")
            True
        """
        self.preload_tabs(["Items", "Categories"])

        # Check to make sure changed_name is not already in list
        if mws.set_value("Categories list", changed_name):
            self.log.error(f"{changed_name} already in list. Aborting change...")
            return False
        # Select category in list
        if not mws.set_value("Categories list", name):
            self.log.error(f"Could not find {name} in list of categories.")
            return False
        # Change and save
        mws.set_value("Categories edit", changed_name)
        mws.click("Save", tab= "Categories")

        return True

    def delete_category(self, name):
        """
        Deletes a category in the CRIND Merchandising interface and saves.
        Must be called from within the CRIND Merchandising module.
        Args:
            name: A string specifying what to look for in the list of categories.
        Returns:
            bool: True/False success condition
        Example:
            cm = crind_merch.CRINDMerchandising()
            cm.delete_category("Test Category")
            True
        """
        self.preload_tabs(["Items", "Categories"])

        # Find category and remove
        if not mws.set_value("Categories list", name):
            self.log.error(f"Could not find {name} in list of categories.")
            return False
        mws.click("Remove","Categories")
        mws.click_toolbar("Yes")
        time.sleep(1) # necessary to allow program time to delete category
        # Ensure successful removal
        if mws.set_value("Categories list", name):
            self.log.error(f"Could not successfully delete {name}.")
            return False

        return True

    def change_item(self, category, item, description = None, available = True):
        """
        Changes the properties of an item in the Items tab.
        Must be called from within the CRIND Merchandising module.
        Args:
            category: A string specifying the name of the category the item is in.
            item: A string specifying what to look for in the Item List. Can be a PLU or description.
            description: A string specifying what to change the description of the item to.
            available: A boolean value specifying the intended state of the "Available" checkbox.
                       If left blank, this will default to the item parameter.
        Returns:
            bool: True/False success condition
        Example:
            cm = crind_merch.CRINDMerchandising()
            cm.change_item("Generic Item", "New Generic Item", True)
            True
        """
        # Leave description unchanged if not specified
        if description == None:
            description = item

        self.preload_tabs(["Categories", "Items"])

        # Select category
        if not mws.set_value("Select Category", category):
            self.log.error(f"Could not find {category} in list of categories.")
            return False
        # Select Item
        if not mws.set_value("Item List", item):
            self.log.error(f"Could not find {item} in list of items.")
            return False
        # Set values
        if not mws.set_value("Item Description", description):
            self.log.error("Failed setting description.")
            return False
        if not mws.set_value("Available", available):
            self.log.error("Failed setting available checkbox")
            return False
        mws.click("Save","Items")
        # Handle notification that item name has been changed
        if mws.get_top_bar_text():
            mws.click_toolbar("OK")

        return True

    def delete_item(self, category, item_list):
        """
        Deletes an item from the specified category in the Items tab.
        Must be called from within the CRIND Merchandising module.
        Args:
            category: A string specifying the name of the category to delete the item from.
            item_list: A string or list of strings specifying either the PLUs or the names of the items to delete.
        Returns:
            bool: True/False success condition
        Example:
            cm = crind_merch.CRINDMerchandising()
            cm.delete_item("Test Category",["Item 2","4"])
            True
        """
        # force item to be a list
        if type(item_list) != list:
            item_list = [item_list]

        self.preload_tabs(["Categories", "Items"])
        
        # Select category
        if not mws.set_value("Select Category", category):
            self.log.error(f"Could not find {category} in list of categories.")
            return False
        # Iterate through each item, selecting and clicking remove
        for item in item_list:
            if not mws.set_value("Item List", item):
                self.log.error(f"Could not find {item} in list of items.")
                return False
            mws.click("Remove", tab= "Items")
            mws.click_toolbar("Yes")
        # Check each item for successful deletion
        for item in item_list:
            if mws.set_value("Item List", item):
                self.log.error(f"{item} still in list, deletion unsuccessful.")
                return False
        return True

    def preload_tabs(self, tablist):
        """
        Preloads specified tabs so controls are correct for rest of module.
        """
        self.log.debug("Preloading tabs...")
        for tab in tablist:
            mws.select_tab(tab)