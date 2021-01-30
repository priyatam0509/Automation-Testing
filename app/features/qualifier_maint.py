from app import mws, system, Navi
import logging, time

class QualifierMaintenance:
    """
    The class representing the Qualifier Maintenance
    window in Set Up -> Store section of MWS.

    The class has add, change, and remove methods that allow
    to configure qualifier groups or qualifier tabs in the window
    based on the configuration dictionary provided to it
    by user.
    """
    # A map for the tab name and the list and checkbox list for check config
    TAB_LISTS = {
        "Groups" : {
            "list" : "Qualifier Groups",
            "checkbox" : "Qualifier Types"
        },
        "Types" : {
            "list" : "Qualifier Types",
            "checkbox" : "Qualifier Groups"
        }
    }

    def __init__(self):
        self.log = logging.getLogger()
        QualifierMaintenance.navigate_to()
        return

    @staticmethod
    def navigate_to():
        """
        Navigates to the Qualifier Maintenance menu.
        Args:
            None
        Returns:
            Returns the result of execution of Navi.navigate_to()
        """
        return Navi.navigate_to("Qualifier Maintenance")

    def add(self, params):
        """
        Adds new qualifier group/type with the given name on the given tab.
        Args:
            params: the dictionary with the information about
                    the fields on specific tab that need to be 
                    configured.
                    This will need to be setup according to the schema in controls.json.

        Returns:
            True: If qualifier group/type was added successfully.
            False: If something went wrong while adding new group/type (will be logged).

        Example:
            params = {
                "Groups" : [ "Totaly availanle name"]
            }

            params = {
                "Types" : ["Totaly availanle name", "2"]
            }

            >>> add({"Groups" : ["Totaly availanle name"]})
                True
            >>> add("Groups" : ["030-Qual 1"])
                Top bar message is : Errors in red must be corrected before you can continue.
                Cannot save new entry
                Performing recovery after errors in the process
                False
            >>> add({"Types" : ["Totaly availanle name", "2"]})
                True
        """
        if len(params.keys()) != 1:
            self.log.error(f"Invalid configuration. Exactly one entry is expected.")
            self.log.warning("Performing recovery after errors in the process")
            mws.recover()
            return False

        tab = list(params.keys())[0]

        if not mws.select_tab(tab):
            self.log.error(f"Could not select tab with the name {tab}.")
            system.takescreenshot()
            self.log.warning("Performing recovery after errors in the process")
            mws.recover()
            return False
        else:
            # Press Add
            if not mws.click_toolbar("Add"):
                return False
            # Delegate to _modify
            if not self._modify_entry(params):
                self.log.warning("Performing recovery after errors in the process")
                mws.recover()
                return False

        return True

    def change(self, qualif_name, params):
        """
        Chnages qualifier group/type with the given name based on the provided dictionary
        with configrations.
        Args:
            qualif_name: (string) the name of the group/type to change
            params: the dictionary with the information about
                    tab and fields that need to be configured.
                    This will need to be setup according to the schema in controls.json.

        Returns:
            True: If qualifier group/type was changed successfully.
            False: If something went wrong while changing the group (will be logged).

        Example:
            params = {
                "Types" : ["Totaly availanle name", "2"]
            }

            params = {
                "Types" : ["", "2"]
            }

            params = {
                "Types" : ["Totaly availanle name", ""]
            }
            
            >>> change("Test Type", params)
                True
            >>> change("Must be must be", params)
                False
        """
        if len(params.keys()) != 1:
            self.log.error(f"Invalid configuration. Exactly one entry is expected.")
            self.log.warning("Performing recovery after errors in the process")
            mws.recover()
            return False

        tab = list(params.keys())[0]
        list_name = self.TAB_LISTS[tab]["list"]

        if not mws.select_tab(tab):
            self.log.error(f"Could not select tab with the name {tab}.")
            system.takescreenshot()
            mws.recover()
            return False
        
        if not mws.select(list_name, qualif_name, tab):
            system.takescreenshot()
            return False
        
        if not mws.click_toolbar("CHANGE"):
            return False

        # Delegate to modify
        if not self._modify_entry(params):
            self.log.warning("Performing recovery after errors in the process")
            mws.recover()
            return False
        
        return True

    def delete(self, qualif_name, tab):
        """
        Deletes qualifier group/type with the given name.
        Args:
            qualif_name: (string) the name of the group/type to delete
            tab: (string) the tab the entry is located on

        Returns:
            True: If qualifier group was deleted successfully.
            False: If something went wrong while deleting the group (will be logged).

        Example:
            params = {
                "Types" : ["Totaly availanle name", "2"]
            }
            
            >>> delete("Test Type", params)
                True
            >>> delete("Must be must be", params)
                False
        """
        if not mws.select_tab(tab):
            return False
            
        if not mws.select(self.TAB_LISTS[tab]['list'], qualif_name, tab):
            return False

        if not mws.click_toolbar("DELETE"):
            self.log.error(f"Unable to click \'DELETE\' to remove \'{qualif_name}\'")
            self.log.warning("Performing recovery after errors in the process")
            mws.recover()
            return False
        
        # Check for top bar message
        if mws.get_top_bar_text() == "Would you like to view the PLU items for this type?":
            mws.click_toolbar("NO")
            
        # Agree to popup
        self._click_on_popup_msg(f"Are you sure you want to delete {qualif_name}?", "yes")
        
        # Verify deletion
        if qualif_name in mws.get_value(self.TAB_LISTS[tab]['list'], tab=tab):
            self.log.error(f"{qualif_name} was still present after deletion.")
            return False

        return True
    
    def check(self, params):
        """
        Checks the checkboxes for the qualifier groups/types based on the provided dictionary with configurations.
        Args:
            params: a dictionary with the information about what checkboxes with groups/types to check for which type/group

        Returns:
            True: If qualifiers were checked successfully.
            False: If something went wrong while checking the qualifier (will be logged).

        Example:
            params = {
                "Groups" : {
                    "030-Qual 1" : [
                        "Test Type",
                        "Test Test Type"
                    ],
                    "031-Qual 2" : [
                        "Test Type"
                    ]
                },
                "Types" : {
                    "Test Type" : [
                        "030-Qual 1",
                        "031-Qual 2",
                        "036-Qual 7"
                    ]
                }
            }

            >>> check(self, params)
                True
        """
        # Error flag
        error = False

        for tab in params:
            if not mws.select_tab(tab):
                self.log.error(f"Could not select tab with the name {tab}.")
                system.takescreenshot()
                error = True
                continue

            for key, value in params[tab].items():
                # Example:
                #    key = "030-Qual 1"
                #    value = ["Test Type"]

                self.log.debug(f"Current key is \'{key}\' and value is \'{value}\'")
                
                # Select the list item
                if not mws.select(self.TAB_LISTS[tab]['list'], key, tab):
                    self.log.error(f"Unable to select \'{key}\' in the list to configure it")
                    error = True
                    continue
                
                for checkbox in value:
                    # Example:
                    #   "Test Type"
                    if not mws.select_checkbox(checkbox, tab=tab, list=self.TAB_LISTS[tab]["checkbox"]):
                        self.log.error(f"Unable to check \'{checkbox}\' for \'{key}\'")
                        error = True
                        continue
        
        # Check for errors
        if error:
            self.log.error("There were errors in the process of configuring Qualifier Maintenance")
            mws.recover()
            return False
        
        return True
    
    def uncheck(self, params):
        """
        Unchecks the checkboxes for the qualifier groups/types based on the provided dictionary with configurations.
        Args:
            params: a dictionary with the information about what checkboxes with groups/types to check for which type/group

        Returns:
            True: If qualifiers were unchecked successfully.
            False: If something went wrong while unchecking the qualifier (will be logged).

        Example:
            params = {
                "Groups" : {
                    "030-Qual 1" : [
                        "Test Type",
                        "Test Test Type"
                    ],
                    "031-Qual 2" : [
                        "Test Type"
                    ]
                },
                "Types" : {
                    "Test Type" : [
                        "030-Qual 1",
                        "031-Qual 2",
                        "036-Qual 7"
                    ]
                }
            }

            >>> uncheck(self, params)
                True
        """
        # Error flag
        error = False

        for tab in params:
            if not mws.select_tab(tab):
                self.log.error(f"Could not select tab with the name {tab}.")
                system.takescreenshot()
                error = True
                continue

            for key, value in params[tab].items():
                # Example:
                #    key = "030-Qual 1"
                #    value = ["Test Type"]

                self.log.debug(f"Current key is \'{key}\' and value is \'{value}\'")
                
                # Select the list item
                if not mws.select(self.TAB_LISTS[tab]['list'], key, tab):
                    self.log.error(f"Unable to select \'{key}\' in the list to configure it")
                    error = True
                    continue
                
                for checkbox in value:
                    # Example:
                    #   "Test Type"
                    if not mws.select_checkbox(checkbox, tab=tab, check=False, list=self.TAB_LISTS[tab]["checkbox"]):
                        self.log.error(f"Unable to uncheck \'{checkbox}\' for \'{key}\'")
                        error = True
                        continue
        
        # Check for errors
        if error:
            self.log.error("There were errors in the process of configuring Qulifier Maintenance")
            mws.recover()
            return False
        
        return True

    def _modify_entry(self, params):
        """
        Modifies the qualifier group/type entry with the given name based on the params provided.
        Args:
            params: the dictionary with the information about
                    tab and fields that need to be 
                    configured.
                    This will need to be setup according to the schema in controls.json.
        Returns:
            True: If qualifier group was changed successfully.
            False: If something went wrong while modifying the group (will be logged).

        Example:
            params = {
                "Groups" : [ "Totaly availanle name"]
            }

            params = {
                "Types" : ["Totaly availanle name", "2"]
            }
        """   
        if len(params.keys()) != 1:
            self.log.error(f"Invalid configuration. Exactly one entry is expected.")
            self.log.warning("Performing recovery after errors in the process")
            mws.recover()
            return False

        # Wait for brighter future
        # Without waiting for the text field to unlock,
        # the changes cannot be applied
        time.sleep(2)

        tab = list(params.keys())[0]
        error = False

        self.log.debug(f"The tab value is \'{tab}\'")
        if tab == "Groups":
            if params[tab][0] and not mws.set_text("Qualifier Groups Textbox", params[tab][0]):
                self.log.error(f"Unable to set Qualifier Group name \'{params[tab][0]}\'.")
                error = True

            # Check it again
            if params[tab][0] and mws.get_value("Qualifier Groups Textbox", tab) != params[tab][0]:
                if not mws.set_text("Qualifier Groups Textbox", params[tab][0]):
                    self.log.error(f"Unable to set Qualifier Group name \'{params[tab][0]}\'.")
                    error = True
        
        if tab == "Types":
            # The value in "Package Quantity" takes a second to appear
            start_time = time.time()
            while time.time() - start_time < 10:
                if mws.get_text("Package Quantity") != "":
                    break
            if params[tab][0] and not mws.set_text("Qualifier Type Description", params[tab][0]):
                self.log.error(f"Unable to set Qualifier Type name \'{params[tab][0]}\'.")
                error = True
            if params[tab][1] and not mws.set_value("Package Quantity", params[tab][1]):
                self.log.error(f"Unable to set Package Quantity to \'{params[tab][1]}\'.")
                error = True

        if not mws.click_toolbar("Save"):
            self.log.error("Cannot save the entry")
            error = True

        # Check for top bar message
        top_bar_message = mws.get_top_bar_text()
        if top_bar_message:
            self.log.warning(f"The top bar message is \'{top_bar_message}\'")
            # Navigate out and take screenshot of the list
            mws.click_toolbar("CANCEL")
            system.takescreenshot()
            error = True

        if error:
            self.log.error("There were errors in the process of configuring Qualifier Maintenance")
            mws.recover()
            return False
        
        return True

    def _click_on_popup_msg(self, text, btn):
        """
        Private function that clicks the button with the provided text 
        if the popup message text is equal to expected text.
        The function logs errors and takes screenshots.
        Args:
            text: (string) the expected text of the popup message
            btn: (string) the text on the button. Make sure that the text is what OCR will actually see
        Returns:
            Returns True if the operation is a success.
            Otherwise, if the text of the message does not match or button is not clicked,
            returns False
        Example:
            >>> _click_on_popup_msg(MSG, "x") 
                True
            >> _click_on_popup_msg(MSG, "blablablabalba)
                False
        """
        if not mws.get_top_bar_text() == text:
            self.log.debug(f"The screen text should be \"{text}\", but it was \"{mws.get_top_bar_text()}\"")
            self.log.warning("Some part of your configuration is not valid")
            return False
        else:
            if not mws.click_toolbar(btn):
                self.log.error(f"Unable to click \'{btn}\' on the pop up message")
                return False
        return True