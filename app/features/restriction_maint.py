from app import mws, system, Navi
import logging, time

class RestrictionMaintenance:
    """
    The class representing the Restriction Maintenance
    window in Set Up -> Store section of MWS.

    The class has add, change, and remove methods that allow
    to configure various groups in the window
    based on the configuration dictionary provided to it
    by user.
    """

    # The list of unsupported tabs or fields
    UNSUPPORTED = [
        "Specific Dates",
        "View PLUs"
    ]

    # The fields that should have the checkbox enabled before they can be
    # edited
    FORCE_CHECK_FIELDS = {
        "Minimum Seller Age": "Seller must be at least",
        "Minimum Buyer Age" : "Buyer Verify Only",
    }

    # A map for the tab name and the buttons with their click config
    TAB_BUTTONS = {
        "Days Of Week": [
			"Monday All Day",
			"Tuesday All Day",
			"Wednesday All Day",
			"Thursday All Day",
			"Friday All Day",
			"Saturday All Day",
			"Sunday All Day",
			"Make all days same as",
			"Clear All"
        ]
    }

    def __init__(self):
        self.log = logging.getLogger()
        RestrictionMaintenance.navigate_to()
        return
    
    @staticmethod
    def navigate_to():
        """"
        Navigates to the Restriction Maintenance menu.
        Args:
            None
        Returns:
            Returns the result of execution of Navi.navigate_to()
        """
        return Navi.navigate_to("Restriction Maintenance")

    def add(self, params):
        """
        Adds new restriction group based on the provided dictionary
        with configrations.
        Args:
            params: the dictionary with the information about
                    various tabs and fields that need to be 
                    configured.
                    This will need to be setup according to the schema in controls.json.

        Returns:
            True: If restriction group was added successfully.
            False: If something went wrong while adding new group (will be logged).

        Example:
            params = {
               "Restriction For Group": "Under 99",
               "Buyer/Seller": {
                    "Seller must be at least": True,
                    "Minimum Seller Age": "22",
                    "Buyer Verify Only": True,
                    "Entry of birth date required": True,
                    "Permit Verify Only": False,
                    "Entry of permit number required": True,
                    "Items in this group must be sold separately.": True
                },
                "Days Of Week": {
                    "Monday Start 1": "10:00 AM",
                    "Monday Stop 1": "11:00 PM",
                    "Monday All Day" : True,
                    "Make all days same as dropdown" : "Tuesday"
                },

            }
            >>> add(params)
                True
            >>> add(params)
                False
        """
        # Press Add
        if not mws.click_toolbar("Add"):
            return False

        # Delegate to _modify
        if not self._modify_entry(params):
            self.log.warning("Performing recovery after errors in the process")
            mws.recover()
            return False
        
        return True

    def change(self, group_name, params):
        """
        Chnages restriction group with the given name based on the provided dictionary
        with configrations.
        Args:
            group_name: (string) the name of the restriction group to change
            params: the dictionary with the information about
                    various tabs and fields that need to be 
                    configured.
                    This will need to be setup according to the schema in controls.json.

        Returns:
            True: If restriction group was changed successfully.
            False: If something went wrong while changing the group (will be logged).

        Example:
            params = {
               "Restriction For Group": "Under 99",
               "Buyer/Seller": {
                    "Seller must be at least": True,
                    "Minimum Seller Age": "22",
                    "Buyer Verify Only": True,
                    "Entry of birth date required": True,
                    "Permit Verify Only": False",
                    "Entry of permit number required": True,
                    "Items in this group must be sold separately": True
                },
                "Days Of Week": {
                    "Monday Start 1": "10:00 AM",
                    "Monday Stop 1": "11:00 PM",
                    "Monday All Day" : True,
                    "Make all days same as dropdown" : "Tuesday"
                },
            }
            >>> change("Must be 18", params)
                True
            >>> change("Must be must be", params)
                False
        """
        # Get the list of current restriction groups
        group_list_current = mws.get_text("Restriction")

        if not group_name in group_list_current:
            self.log.error(f"The restriction group name \'{group_name}\' was not found in the list")
            system.takescreenshot()
            return False
        
        if not mws.select("Restriction", group_name):
            return False

        if not mws.click_toolbar("CHANGE"):
            return False

        # Delegate to modify
        if not self._modify_entry(params):
            self.log.warning("Performing recovery after errors in the process")
            mws.recover()
            return False
        
        return True

    def delete(self, group_name):
        """
        Deletes restriction group with the given name.
        Args:
            group_name: (string) the name of the restriction group to change

        Returns:
            True: If restriction group was deleted successfully.
            False: If something went wrong while deleting the group (will be logged).

        Example:
            >>> delete("Must be 18")
                True
            >>> delete("What must be, must be")
                False
        """
        if not self.select(group_name):
            return False

        if not mws.click_toolbar("DELETE"):
            self.log.error(f"Unable to click \'DELETE\' to remove \'{group_name}\'")
            self.log.warning("Performing recovery after errors in the process")
            mws.recover()
            return False
        
        # Agree to popup
        return self._click_on_popup_msg(f"Are you sure you want to delete {group_name}?", "yes")

    def select(self, group_name):
        """
        Selects the restriction group with the given name in the list of groups.
        Args:
            group_name: (string) the name of the restriction group to change

        Returns:
            True: If restriction group was selected successfully.
            False: If something went wrong while selecting the group (will be logged).

        Example:
            >>> select("Must be 18")
                True
            >>> select("What must be, must be")
                False
        """
        # Get the list of current restriction groups
        group_list_current = mws.get_text("Restriction")

        if not group_name in group_list_current:
            self.log.error(f"The restriction group name \'{group_name}\' was not found in the list")
            system.takescreenshot()
            return False
        
        if not mws.select("Restriction", group_name):
            return False

        return True

    def _modify_entry(self, params):
        """
        Modifies the restriction group entry with the given name based on the params provided.
        Args:
            params: the dictionary with the information about
                    various tabs and fields that need to be 
                    configured.
                    This will need to be setup according to the schema in controls.json.
        Returns:
            True: If restriction group was changed successfully.
            False: If something went wrong while changing the group (will be logged).

        Example:
            params = {
               "Restriction For Group": "Under 99",
               "Buyer/Seller": {
                    "Seller must be at least": True,
                    "Minimum Seller Age": "22",
                    "Buyer Verify Only": True,
                    "Entry of birth date required": True,
                    "Permit Verify Only": False,
                    "Entry of permit number required": True,
                    "Items in this group must be sold separately": True
                },
                "Days Of Week": {
                    "Monday Start 1": "10:00 AM",
                    "Monday Stop 1": "11:00 PM",
                    "Monday All Day" : True,
                    "Make all days same as dropdown" : "Tuesday"
                },
            }
        """
        # Create error flag
        error = False

        for tab in params:
            # Example: "Buyer/Seller"
            self.log.debug(f"Current tab is \'{tab}\'")

            # Check if the tab is supported
            if tab in self.UNSUPPORTED:
                self.log.warning(f"The configuration contains the tab \'{tab}\' that is not supported.")
                error = True
                continue
            
            # Check if tab is actually the name of the group
            if tab == "Restriction For Group":
                key = tab
                value = params[tab]
                self.log.debug(f"Setting the name \'{value}\' for \'{tab}\''")
                if not mws.set_value(key, value):
                    self.log.error(f"Could not set {key} with {value}.")
                    error = True
                continue

            elif tab == "Age Verification" and not mws.select_tab(tab, tolerance='000000'):
                if "Buyer/Seller" in params and params["Buyer/Seller"]["Entry of birth date required"]: 
                    mws.select_tab("Buyer/Seller")
                    mws.set_value("Entry of birth date required", True)
                else:
                    self.log.error("Cannot modify the Age Verification tab without enabling Entry of birth date required on the Buyer/Seller tab."\
                                   "Please include this field in your configuration.")
                    return False

            if not mws.select_tab(tab):
                self.log.error(f"Could not select tab with the name {tab}.")
                system.takescreenshot()
                error = True
                continue
            
            for key, value in params[tab].items():
                # Example:
                #    key = "Seller must be at least"
                #    value = True

                self.log.debug(f"Current key is \'{key}\' and value is \'{value}\'")

                # Check whether the option is dependent on other option
                if key in self.FORCE_CHECK_FIELDS:
                    if not self._set_dependent_fields(key, params, tab):
                        error = True
                        continue
                # Check if the tab support buttons, and key is a button
                elif tab in list(self.TAB_BUTTONS) and key in self.TAB_BUTTONS[tab]:
                    if not mws.click(key, tab):
                        self.log.error(f"Could not click {key} on the {tab} tab.")
                        error = True

                        # Move to next one
                        continue
                else:
                    if not mws.set_value(key, value, tab):
                        self.log.error(f"Could not set {key} with {value} on the {tab} tab.")
                        error = True

                        # Move to next one
                        continue

        mws.click_toolbar("Save")
        msg = mws.get_top_bar_text()
        start_time = time.time()
        while msg and time.time() - start_time < 10:
            if msg == "Sending reload message to registers.":
                continue
            else:
                self.log.error(f"Got an error when saving restriction: {msg}")
                error = True
                break
        
        # Check for errors
        if error:
            self.log.error("There were errors in the process of configuring Restriction Maintenance")
            return False
        
        return True

    def _set_dependent_fields(self, depend_name, params, tab):
        """
        Sets the fields which availability depends on
        some master field.
        Logs errors if they occur.
        Args:
            depend_names: (string) the name of field to set
            params: (dictionary) a dictionary of the config delegated from add or change funcs that
                    should contain the dependent and master fields' values if needed
            tab: (string) the name of the tab the fields are on
        Returns:
            True: if operation is a success
            False: if there are errors in the process
        """
        master_name = self.FORCE_CHECK_FIELDS[depend_name]
        # Error flag
        error = False

        # Check if the "master" field is present
        if master_name in list(params[tab]):
            # Apply the config
            if not mws.set_value(master_name, params[tab][master_name]):
                self.log.error(f"Could not set {master_name} with {params[tab][master_name]} on the {tab} tab.")
                system.takescreenshot()
                error = True
        else:
            # Check if it is enabled
            if not mws.get_value(master_name):
                # Dependent field cannot be set
                error = True

        if error:
            self.log.error(f"Could not set {depend_name} with {params[tab][depend_name]} on the {tab} tab.")
            return False
        
        if not mws.set_value(depend_name, params[tab][depend_name]):
            self.log.error(f"Could not set {depend_name} with {params[tab][depend_name]} on the {tab} tab.")
            system.takescreenshot()
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