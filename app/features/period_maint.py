from app import mws, system, Navi
import logging, time, copy

class PeriodMaintenance:
    """
    The class representing the Period Maintenance
    window in Set Up -> Store section of MWS.

    The class has a setup method that allows
    to configure various tabs and fields in the window
    based on the configuration dictionary provided to it
    by user.
    """

    # The constant with the text of the pop up message displayed after the 
    # Weekly is checked or the day is changed
    WEEKLY_MSG_POPUP_TEXT = "Once selected and saved, the starting day of the weekly period may not be changed again.  Please ensure that you have the correct day selected."

    # The constant with the text day field for Weekly section
    WEEKLY_DAY_FIELD_NAME = "Select the first day of the reporting week"

    # Constants used in this class

    # A map for the tab name and the buttons with their click config
    TAB_BUTTONS = {
        "Shift Close Options" : [
            "Shift Close Reports",
            "Auxiliary Reports"
        ],
        "Till Close" : [
            "Till Close Report"
        ],
        "Store Close Reports" : [
            "Shift Close Reports",
            "Auxiliary Reports"
        ]
    }

    # A map for the tabs and their lists' names
    TAB_LISTS = {
        "Shift Close Options" : "Shift Close Reporting",
        "Till Close" : "Till Close Reports",
        "Store Close Reports" : "Store Close Reporting"
    }

    # The list of unsupported tabs or fields
    UNSUPPORTED = [
        "Manager Periods"
    ],

    # The fields that should have the checkbox enabled before they can be
    # edited
    FORCE_CHECK_FIELDS = {
        "Allow store closes from POS Registers to start at": "Force Store Close" ,
        "Force the store closed at this time": "Force Store Close" ,
        "Start sending reminder messages to POS Registers at": "Force Store Close" ,
        "Display store close reminder every": "Force Store Close" ,
        "Store close reminder message": "Force Store Close"
    }

    def __init__(self):
        """
        Sets up the logger specific to this module.
        Set up mws connection.
        """
        # self.log = system.setup_logging(__name__, verbosity=logging.DEBUG)
        self.log = logging.getLogger() 

        PeriodMaintenance.navigate_to()

        return
    
    @staticmethod
    def navigate_to():
        """
        Navigates to the Period Maintenance menu.
        Args:
            None
        Returns:
            Returns the result of execution of Navi.navigate_to()
        """
        return Navi.navigate_to("Period Maintenance")

    def setup(self, params):
        """
        Configures the tabs and fields acessible in the 
        Period Maintenance window according to the provided
        dictionary.

        Args:
            params: the dictionary with the information about
                    various tabs and fields that need to be 
                    configured.
                    This will need to be setup according to the schema in controls.json.

        Returns:
            True: If Period Maintenance was successfully set up.
            False: If something went wrong while setting up Store Options (will be logged).

        Example:
            params = {
                    "General" : {
                        "Yearly": True,
                        "Quarterly": True,
                        "Monthly": True,
                        "Calendar Day": False,
                        "Store Close": False,
                        "Variable Shift": False,
                        "Weekly" : [ True, "Saturday"],
                        "Weekly" : [False]
                    },
                    "Shift Close Options" : {
                        "Close Network Batch": True,
                        "Close Network Shift": False,
                        "Shift Close Reporting": [
                            ["Store Sales Summary", True, False],
                            ["Price Override Report", True, False],
                        ]
                    },
                    "Store Close Options": {
                        "Force Store Close" : True,
                        "Allow store closes from POS Registers to start at": "12:00 PM",
                        "Force the store closed at this time": "12:00 PM",
                        "Start sending reminder messages to POS Registers at": "12:00 PM",
                        "Display store close reminder every": "10:00",
                        "Store close reminder message": "Some message"
                    },
                    "Till Close" : {
                        "Till Close Reports" : [
                            ["Till PLU Sales Report", False]
                        ] 
                    }
                }
            >>> setup(params)
                True
        """
        # Create a copy of parameters
        params = copy.deepcopy(params)

        # Create error flag
        error = False

        for tab in params:
            # Exmaple: "General"

            # Check if the tab is supported
            if tab in self.UNSUPPORTED:
                self.log.warning(f"The configuration contains the tab \'{tab}\' that is not supported.")
                return False

            if not mws.select_tab(tab):
                self.log.error(f"Could not select tab with the name {tab}.")
                system.takescreenshot()
                return False

            for key, value in params[tab].items():
                # Example:
                #    key = "Yearly"
                #    value = "True"
                
                # Check if the key is a valid list in the tab
                if tab in list(self.TAB_LISTS) and self.TAB_LISTS[tab] == key:
                    if not self.modify_tab_list(tab, key, value):
                        error = True
                    # Move to next one
                    continue

                # Check whether the option is dependent on other option
                if key in self.FORCE_CHECK_FIELDS:
                    if not self._set_dependent_fields(key, params, tab):
                        error = True
                        continue

                # Check if that's a weekly section in General
                elif tab == "General" and key == "Weekly":
                    # At this point value is a list of type [True, .... ]
                    if len(value) < 1:
                        self.log.error(f"Invalid options configuration for checkbox field {key} in tab {tab}")
                        error = True
                        # Move to next one
                        continue

                    # Flag of the current state of the checkbox
                    checked = mws.get_value(key, tab)
                    self.log.debug(f"Current state of Weekly is \'{checked}\'")
                    self.log.debug(f"Trying to set the Weekly to \'{value[0]}\'")
                    
                    # Check the checkbox
                    if not mws.select_checkbox(key, value[0]):
                        self.log.error(f"Failed to check the checkbox field {key} in tab {tab}")
                        error = True

                        # Move to next one
                        continue

                    # Fallback solution in case the checkbox state was not
                    # actualy changed.
                    # It is absolutely neccessary for correct functionality
                    if ( bool(value[0]) ^ bool(mws.get_value(key, tab))):
                        mws.select_checkbox(key, value[0], tab=tab)

                    # Alternative solution is finding the checkbox through OCR
                    # if not mws.search_click_ocr(key, bbox=(64, 406, 143, 429), click_loc=-1):
                    #     self.log.error(f"Failed to check the checkbox field {key} in tab {tab}")
                    #     system.takescreenshot()
                    #     return False

                    # Check the state
                    if ( bool(value[0]) ^ bool(mws.get_value(key, tab))):
                        self.log.error(f"The state of the checkbox field {key} in tab {tab} was not changed")
                        error = True

                        # Move to next one
                        continue

                    # If it's checked and we need to check it
                    # There is no pop up msg 

                    # Check if we enabled it
                    # Check the text box message
                    self.log.debug(f"The state of Weekly was \'{checked}\' and now it is \'{mws.get_value(key)}\'")
                    if not checked and value[0]:
                        # Agree with popup
                        if not self._click_on_popup_msg(self.WEEKLY_MSG_POPUP_TEXT, "OK"):
                            # Error is already logged
                            error = True

                            # Recover
                            mws.recover()
                            return False
                    
                    # Check if we need to set the day
                    if value[0]:
                        if len(value) > 1:
                            # Set the day
                            if not mws.set_value(self.WEEKLY_DAY_FIELD_NAME, value[1], tab):
                                self.log.error(f"Could not set {key} with {value} on the {tab} tab.")
                                error = True

                                # Move to next one
                                continue
                            
                            # Agree with popup
                            if not self._click_on_popup_msg(self.WEEKLY_MSG_POPUP_TEXT, "OK"):
                                # Error is already logged
                                error = True 

                                # Recover
                                mws.recover()
                                return False
                else:
                    if not mws.set_value(key, value, tab):
                        self.log.error(f"Could not set {key} with {value} on the {tab} tab.")
                        error = True

                        # Move to next one
                        continue

                    # Workaround for checkbox not being set right after the tab is selected
                    if mws.get_value(key, tab=tab) != value:
                        if not mws.set_value(key, value, tab):
                            self.log.error(f"Could not set {key} with {value} on the {tab} tab.")
                            error = True

                            # Move to next one
                            continue
        
        try:
            if not mws.click_toolbar("Save", main=True):
                self.log.error("Unable to save Period Maintenance")
                error = True
        except mws.ConnException:
            self.log.error("Did not return to main menu after saving Period Maintenance")
            error=True
        
        msg = mws.get_top_bar_text()
        if msg and msg != 'Sending reload message to registers.':
            self.log.error(f"Unexpected top bar message: \'{msg}\'")
            error = True

        # Check for errors
        if error:
            self.log.error("There were errors in the process of configuring Period Maintenance")
            mws.recover()
            return False

        return True
    
    def modify_tab_list(self, tab_name, list_name, options):
        """
        Modifies the list in the tab with the provided name.
        The options list specifies the row name and the values it should be set to.
        Args:
            name: (string) the name of the tab as indicated in controls.json
            options: (list) a list of rows to modify. The options list consists of lists of type
                    [ *row name*, *first column value flag*, ... ]
        Retrurns:
            Returns true if operation is a success. Otherwise returns False, and logs the details

        Example:
            Sample of options param:
                [
                    ["Store Sales Summary", True, False],
                    ["Price Override Report", True, False],
                ]
        """
        if not tab_name:
            self.log.error("The name of the tab is not provided!")
            return False

        if not tab_name in self.TAB_BUTTONS:
            self.log.error(f"The provided tab name {tab_name} is invalid!")
            return False

        if not options or len(options) == 0:
            self.log.error(f"The options for the list {list_name} in the tab {tab_name} are not provided!")
            return False

        # Create error flag
        error = False

        if tab_name == "Shift Close Options":
            # Check if the tab is editable
            if mws.find_text_ocr("(This tab is inactive unless \"Variable Shift (Shift Close)\" is checked on the General tab)", color='0000C0'):
                self.log.warning("The 'Shift Close Options' tab is being configured while inactive.")
                self.log.error("The error message is: This tab is inactive unless \"Variable Shift (Shift Close)\" is checked on the General tab")
                return False

        # In order to leave the columns blank or checked we need to figure out
        # if the current state is checked or blank

        # Process each option
        for row in options:
            if not row or len(row) < 2: # We expect at least one flag
                self.log.error(f"Invalid options configuration for list {list_name} in tab {tab_name}")
                error = True
                break

             # Retrieve the current state of the list
            list_state_current = mws.get_text(list_name, tab_name)

            # Go through current state list and find the row
            # Update the state change trigger in the row if needed
            for row_state_current in list_state_current:
                if row_state_current[0] == row[0]:
                    # Found match
                    # XOR state triggers
                    for i in range(1, len(row)):
                        row[i] = bool(row[i]) ^ bool(row_state_current[i])
                        
            # Select row in a list
            if not mws.select(list_name, row[0], tab_name):
                self.log.error(f"Unable to select the row {row[0]} in the list {list_name} in the tab {tab_name}.")
                error = True
                # Move to next one
                continue
            
            self.log.debug(f"Selected row '{row[0]}' successfully")

            # Process column values
            for i in range (1, len(row)):
                # Ex: row = ['Field', 'X', 'X']
                btn_value = row[i]
                btn_name = self.TAB_BUTTONS[tab_name][i - 1]
                # Click appropriate button
                self.log.debug(f"Button requested. Name\'{btn_name}\'")
                if btn_value:
                    if tab_name == "Till Close":
                        # The button is affected by floating control issue
                        bbox = (133, 616, 695, 648) if mws.is_high_resolution() else (40, 480, 190, 510)
                        if not mws.search_click_ocr(btn_name, bbox=bbox, click_loc=-1, offset=(-25,0)):
                            self.log.error(f"Unable to click button \'{btn_name}\' for the row \'{row[0]}\' in the list \'{list_name}\'")
                            error = True
                            # Move to next one
                            continue
                    elif tab_name == "Shift Close Options":
                        # The button is affected by floating control issue
                        bbox = (133, 616, 695, 648) if mws.is_high_resolution() else (40, 530, 380, 570)
                        if not mws.search_click_ocr(btn_name, bbox=bbox, click_loc=-1, offset=(-25,0)):
                            self.log.error(f"Unable to click button \'{btn_name}\' for the row \'{row[0]}\' in the list \'{list_name}\'")
                            error = True
                            # Move to next one
                            continue
                    self.log.debug(f"Button \'{btn_name}\' for \'{row[0]}\' pressed successfully")
        
        return not error

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