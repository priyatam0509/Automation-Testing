from app import mws, system, Navi
import logging, re, time, copy
import pywinauto.keyboard as pkb

class AccountsMaintenance:
    """
    The class representing the Local Accounts Maintenance
    window in Set Up -> Store section of MWS.

    The class has search, add, change, remove, and balance
    methods that allow to configure various groups in the window
    based on the configuration dictionary provided to it
    by user.
    """

    # The dictionary of lists of unsupported tabs or fields
    UNSUPPORTED = {
        "Search" : [
            "Local Accounts Option - Store Copy of receipt",
            "Local Accounts Option - Customer copy of receipt"
        ],
        "Add" : {
            "Card Based" : [
                "Sub-Accounts",
                "When the POS is offline, the maximum transaction amount is",
                "Enable all sub-accts",
                "Disable all sub-accts"
            ],
            "Face Based" : [
                "Card Accounts",
                "Prompt Options",
                "Customize Prompt",
                "Negative Card",
                "Enable All Cards",
                "Disable All Cards"
            ]
        },
        "Change" : {
            "Card Based" : [
                "Sub-Accounts",
                "When the POS is offline, the maximum transaction amount is",
                "Account ID",
                "Enable all sub-accts",
                "Disable all sub-accts"
            ],
            "Face Based" : [
                "Card Accounts",
                "Account ID",
                "Prompt Options",
                "Customize Prompt",
                "Negative Card",
                "Enable All Cards",
                "Disable All Cards"
            ]
        }
    }

    # A map for the tab name and the buttons with their click config
    TAB_BUTTONS = {
        "General": [
            "Enable All Cards",
            "Disable All Cards",
            "Enable all sub-accts",
            "Disable all sub-accts"
        ]
    }

    def __init__(self):
        self.log = logging.getLogger()
        AccountsMaintenance.navigate_to()
        return
    
    @staticmethod
    def navigate_to():
        """
        Navigates to the Local Acocunts Maintenance menu.
        Args:
            None
        Returns:
            Returns the result of execution of Navi.navigate_to()
        """
        return Navi.navigate_to("Local Accounts Maintenance")

    def search(self, params):
        """
        Performs a search for the accounts that match the search criteria provided in params.
        Providing empty params dictionary means matching everything.
        Args:
            params: (dictionary) a dictionary of search parameters. May be empty to match everything
        Returns:
            If accounts were found returns True, otherwise returns False
        Example:
            params = {
                "Account ID": "1",
                "Account Name": "DG, Inc.",
                "Taxation Number": "1234",
            }

            >>> search(params)
                True

            >>> search({})
                True
        """
        # Error flag
        error = False

        for key, value in params.items():
            # Check if the field is supported
            if key in self.UNSUPPORTED["Search"]:
                self.log.warning(f"The configuration contains the field \'{key}\' that is not supported.")
                error = True
                break

            # Example:
            # key = "Account ID", value = "1"
            if not mws.set_value(key, value):
                # Try one more time
                if not mws.set_value(key, value):
                    self.log.error(f"Unable to set \'{key}\' to \'{value}\'")
                    error = True
                    continue

        if error:
            self.log.error("There were errors in the process. Unable to perform search since not all search parameters were set")
            return False
        
        # Search
        if not mws.click_toolbar("Search"):
            self.log.error(f"Unable to click \'Search\'")
            self.log.error("There were errors in the process. Unable to perform search since not all search parameters were set")
            return False

        # Check for messages
        if self._check_top_bar_msg("No accounts were found matching these criteria.", wait=3):
            self._click_on_popup_msg("No accounts were found matching these criteria.", "OK")
        
        accounts_list = mws.get_text("Accounts")
        return len(accounts_list) != 0

    def add(self, params):
        """
        Adds new account based on the provided dictionary
        with configrations.
        Args:
            params: the dictionary with the information about
                    various tabs and fields that need to be 
                    configured.
                    This will need to be setup according to the schema in controls.json.

        Returns:
            True: If account was added successfully.
            False: If something went wrong while adding new account (will be logged).

        Example:
            params = {
               "General": {
                    "Account ID":"5", # Unique id
                    "Account Name":"Test Account",
                    "Account Credit Limit":"700.00",
                    "Account Type":"Card Based",
                    "Enable All Cards":True,
                    "Disable All Cards":False,
                    "A warning message should display if the customer's account balance reaches":"120.00"
                    "Enable all sub-accts":True, # Only for Face type
                    "Disable all sub-accts":True, # Only for Face Type
                    "When the POS is offline, the maximum transaction amount is":"500" # Only for Face Type
                },
                "Address": {
                    "Street":"Friendly St.",
                    "City":"Wrong",
                    "State":"Different",
                    "Country":"This",
                },
                "Card Accounts": {
                    "Card Data is On":"Track 1",
                    "Issuer Number Start Position":"1",
                    "Account Number Start Position":"2",
                    "Account Number Range Start":"1",
                    "Account Number Range End":"99",
                    "Issuer Number":"123123123123123123",
                    "CRIND Authorization Amount":"20.00"
                },
                "Prompt Options": {
                    "Prompt 1 Start Position": "21",
                    "Prompt 1 Value": "22",
                    "Prompt 1" : {
                        "ID" : True,
                        "Odometer" : False
                    }
                },
                "Customize Prompt": {
                    "Customer Prompt Text ID": "Text ID",
                    "Customer Prompt Text Odometer": "Text Odo",
                    "Customer Prompt Text Vehicle #": "Text Vehicle #",
                    "Customer Prompt Text Driver ID": "Text Driver ID",
                    "Customer Prompt Text Custom": "Text Custom",
                    "Receipt Description ID": "Text ID",
                    "Receipt Description Odometer": "Text Odo",
                    "Receipt Description Vehicle #": "Text Vehicle #",
                    "Receipt Description Driver ID": "Text Driver ID",
                    "Receipt Description Custom": "Text Custom",
                    "Print on Receipt ID": True,
                    "Print on Receipt Odometer": True,
                    "Print on Receipt Vehicle #": True,
                    "Print on Receipt Driver ID": True,
                    "Print on Receipt Custom": True
                },
                "Negative Card": {
                    "Update" : [
                        ["1", "22"],
                        ["1", "1"],
                        ["22", "99"]
                    ]
                },
                "Sub-Accounts": [ # For Face Based only
                    {
                        "Sub-Account ID": "49",
                        "Description": "Something",
                        "Vehicle Reg. No": "228",
                        "Sub-Account Disabled": False
                    },
                    {
                        "Sub-Account ID": "51",
                        "Description": "Something",
                        "Vehicle Reg. No": "228",
                        "Sub-Account Disabled": False
                    },
                    {
                        "Description": "Something",
                        "Vehicle Reg. No": "228",
                        "Sub-Account Disabled": False
                    }
                ]
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
        if not self._modify_entry("Add", params):
            self.log.warning("Performing recovery after errors in the process")
            mws.recover()
            return False
        
        return True

    def change(self, account_id, params):
        """
        Changes the existing account with the given id based on the provided dictionary
        with configrations.
        Args:
            account_id: (str) the id of the existring account to change 
            params: the dictionary with the information about
                    various tabs and fields that need to be 
                    configured.
                    This will need to be setup according to the schema in controls.json.

        Returns:
            True: If account was changed successfully.
            False: If something went wrong while changing the account (will be logged).

        Example:
            params = {
               "General": {
                    "Account ID":"5",
                    "Account Name":"Test Account",
                    "Account Credit Limit":"700.00",
                    "Account Type":"Card Based"
                    "Enable All Cards":True,
                    "Disable All Cards":False,
                    "A warning message should display if the customer's account balance reaches":"120.00"
                    "Enable all sub-accts":True, # Only for Face type
                    "Disable all sub-accts":True, # Only for Face Type
                    "When the POS is offline, the maximum transaction amount is":"500", # Only for Face Type
                },
                "Address": {
                    "Street":"Friendly St.",
                    "City":"Wrong",
                    "State":"Different",
                    "Country":"This",
                },
                "Card Accounts": {
                    "Card Data is On":"Track 1",
                    "Issuer Number Start Position":"1",
                    "Account Number Start Position":"2",
                    "Account Number Range Start":"1",
                    "Account Number Range End":"2",
                    "Issuer Number":"1231231231231231231231231",
                    "CRIND Authorization Amount":"20"
                },
                "Prompt Options": {
                    "Prompt 1 Start Position": 21,
                    "Prompt 1 Value": 22,
                    "Prompt 1" : {
                        "ID" : True,
                        "Odometer" : False
                    }
                },
                "Customize Prompt": {
                    "Customer Prompt Text ID": "Text ID",
                    "Customer Prompt Text Odometer": "Text Odo",
                    "Customer Prompt Text Vehicle #": "Text Vehicle #",
                    "Customer Prompt Text Driver ID": "Text Driver ID",
                    "Customer Prompt Text Custom": "Text Custom",
                    "Receipt Description ID": "Text ID",
                    "Receipt Description Odometer": "Text Odo",
                    "Receipt Description Vehicle #": "Text Vehicle #",
                    "Receipt Description Driver ID": "Text Driver ID",
                    "Receipt Description Custom": "Text Custom",
                    "Print on Receipt ID": True,
                    "Print on Receipt Odometer": True,
                    "Print on Receipt Vehicle #": True,
                    "Print on Receipt Driver ID": True,
                    "Print on Receipt Custom": True
                },
                "Negative Card": {
                    "Update" : [
                        ["1", "22"],
                        ["1", "1"],
                        ["22", "99"]
                    ]
                },
                "Sub-Accounts": [ # For Face Based only
                    {
                        "Sub-Account ID": "49",
                        "Description": "Something",
                        "Vehicle Reg. No": "228",
                        "Sub-Account Disabled": False
                    },
                    {
                        "Sub-Account ID": "51",
                        "Description": "Something",
                        "Vehicle Reg. No": "228",
                        "Sub-Account Disabled": False
                    },
                    {
                        "Description": "Something",
                        "Vehicle Reg. No": "228",
                        "Sub-Account Disabled": False
                    }
                ]
            }
            >>> change("1", params)
                True
            >>> change("7863781263", params)
                False
        """
        if not self.search({"Account ID":account_id}):
            self.log.error(f"The account with the id \'{account_id}\' was not found")
            return False
        
        # By this point the correct account should already be selected
        mws.click_toolbar("CHANGE")

        # Delegate to _modify
        if not self._modify_entry("Change", params):
            self.log.warning("Performing recovery after errors in the process")
            mws.recover()
            return False
        
        return True
    
    def delete(self, account_ids=[]):
        """
        Deletes the accounts with the given account ids from the list of accounts.
        It accepts the list of ids in case multiple accounts should be removed.
        Args:
            account_ids: (list) the list of account ids to be removed
        Returns:
            True: if the operation is a success
            False: if there were errors in the process (will be logged).
        Example:
            account_ids = ["1", "2", "3"]
            >>> delete(params)
                True
        """
        error = False

        # Process each id
        for id in account_ids:
            if not self.search({"Account ID":id}):
                self.log.error(f"The account with the id \'{id}\' was not found")
                error = True
                continue

            # By this point the correct account should already be selected
            mws.click_toolbar("DELETE")
            if not self._check_top_bar_msg("Delete Account", wait=1):
                self.log.error(f"The top bar text was \'{mws.get_top_bar_text()}\' when \'Delete Account\' was expected")
                system.takescreenshot()
                error = True
                break
            
            mws.click_toolbar("YES")
            self.log.info(f"Account with id \'{id}\' was successfully removed")

            # Wait and check
            # It takes a while to actually remove the account
            start_time = time.time()
            while time.time() - start_time <= 5:
                match = False
                for row in mws.get_text("Accounts"):
                    match = row[0] == id
                
                if not match:
                    break
            else:
                self.log.error("Exceeded timeout waiting for the delted entry to be removed.")
                error = True
                break

        # Check for errors
        if error:
            self.log.error("There were errors in the process of configuring Local Accounts Maintenance")
            return False
        
        return True

    def adjust_balance(self, account_id, balance, reason, wait=5):
        """
        Adjusts the balance of the existing account based on the parameters provided.
        Args:
            account_id: (str) the id of the account to change
            balance: (str) the balance to apply
            reason: (str) the reason message for the change
            wait: (int) the number of seconds to wait until the Adjsut Balance window opens
        Returns:
             True: if the operation is a success
            False: if there were errors in the process (will be logged).
        Example:
            >>> adjust_balance("1", "0.13", "Just Cause")
                True
        """
        self.log.debug("Entered adjust method")
        if not self.search({"Account ID":account_id}):
            self.log.error(f"The account with the id \'{account_id}\' was not found")
            return False

        self.log.debug("Search completed")
        
        mws.click_toolbar("Adjust Balance")

        self.log.debug("Adjusting window")

        # Wait for the new window to appear
        ocr_bbox = (166, 156, 467, 174) if mws.is_high_resolution() else (166, 120, 467, 139)
        system.wait_for(lambda: mws.find_text_ocr("Local Accounts Balance Adjustment", bbox=ocr_bbox), timeout=wait, verify=False)

        self.log.debug("Setting fields")
        
        if not mws.set_value("Adjust Account Balance By", balance):
            self.log.error(f"Unable to adjust balance for account \'{account_id}\'")

        if not mws.set_value("Reason", reason):
            self.log.error(f"Unable to adjust balance for account \'{account_id}\'")

        if not mws.click_toolbar("Save"):
            self.log.error("Unable to save Local Accounts Maintenance")

        # Agree to popup
        msg = mws.get_top_bar_text()
        if not re.match(r"This will change the account balance by \$\d+\.\d+. The new balance will be: \$\d+\.\d+. Proceed\?", msg):
            self.log.error("Unexpected message is encountered when trying to adjust the balance")
            self.log.error(f"The message is:\'{msg}\'")
            self.log.error("Recovering...")
            mws.recover()
            return False
        
        mws.click_toolbar("YES")
        return True
    
    def _modify_entry(self, operation, params):
        """
        Modifies the account based on the params provided.
        Args:
            operation: (str) the name of the operation performed
            params: the dictionary with the information about
                    various tabs and fields that need to be 
                    configured.
                    This will need to be setup according to the schema in controls.json.
        Returns:
            True: If account was changed successfully.
            False: If something went wrong while changing the account (will be logged).

        Example:
            params as in add()
            >>> _modify_entry(params)
                True
        """
        # Create error flag
        error = False

        # Create a copy of parameters
        params = copy.deepcopy(params)

        # Extract the account type for it is essential for configuration parameters
        if not "General" in list(params.keys()):
            self.log.error("The provided dictionary is missing parameters for \'General\' tab which is essential for configuration")
            return False

        account_type = None
        if "Account Type" in list(params["General"].keys()):
            account_type = params["General"]["Account Type"]
        else:
            # It returns a list of 3 items, first is the current value
            account_type = mws.get_value("Account Type", tab="General")[0]

        for tab in params:
            # Example: "General
            self.log.debug(f"Current tab is \'{tab}\'")

            # Check if the tab is supported
            if tab in self.UNSUPPORTED[operation][account_type]:
                self.log.error(f"The configuration contains the tab \'{tab}\' that is not available for current card type \'{account_type}\'.")
                error = True
                continue
            
            if not mws.select_tab(tab):
                if tab == "Sub-Accounts":
                    # Switch to this tab since OCR most likely failed to find it
                    if not mws.select_tab("SubAccounts"):
                        self.log.error(f"Could not select tab with the name {tab}.")
                        system.takescreenshot()
                        error = True
                        continue
                else:
                    self.log.error(f"Could not select tab with the name {tab}.")
                    system.takescreenshot()
                    error = True
                    continue
            
            if tab == "Prompt Options":
                # "Prompt 1 Start Position": 21,
                # "Prompt 1 Value": 22,
                # "Prompt 1" : {
                #     "ID" : True,
                #     "Odometer" : False
                # }
                for key, value in params[tab].items():
                    if re.match(r'^Prompt \d+$', key):
                        # Prompt box with checkboxes
                        PROMPT_LEFT = ["ID", "Odometer", "Vehicle #"]
                        PROMPT_RIGHT = ["Driver ID", "Custom"]
                        for field, check in value.items():
                            if field in PROMPT_LEFT:
                                mws.select_checkbox(field, list="%s Left"%key, check=check)
                            elif field in PROMPT_RIGHT:
                                mws.select_checkbox(field, list="%s Right"%key, check=check)
                            else:
                                self.log.error(f"Invalid checkbox \'{field}\'")
                                error = True
                                continue
                    else:
                        if not mws.set_value(key, value):
                            self.log.error(f"Unable to set the field \'{key}\'")
                            error = True
                            continue
            
            elif tab == "Negative Card":
                # "Negative Card": {
                #    "Update" : [
                #        ("1", "22"),
                #        ("1", "1"),
                #        ("22", "99")
                #    ]
                # }
                for key, value in params[tab].items():
                    if key == "Update":
                        for entry in value:
                            # ("1", "2")
                            try:
                                mws.set_value("Begin Account Number Range", entry[0])
                                mws.set_value("End Account Number Range", entry[1])
                                # Floating control
                                mws.search_click_ocr("Update List")
                            except IndexError:
                                self.log.error("Failed to set the range in Negative Cards. Invalid configuration was provided")
                                error = True
                                continue

                            # TODO Revise
                            # Check for the popup message
                            msg = mws.get_top_bar_text()
                            if msg:
                                self.log.error("Unexpected message is encountered when trying to update the Negative Cards list")
                                self.log.error(f"The message is:\'{msg}\'")
                                system.takescreenshot()
                                mws.click_toolbar("OK")
                                # Check
                                if mws.get_top_bar_text():
                                    self.log.error("Failed to dismiss the message. Recovering...")
                                    mws.recover()
                                    return False
                    elif key == "Remove":
                        # TODO
                        # The removal operation is not supported since, in some cases,
                        # it causes the process of adding/changing an account to fail
                        # upon normal conditions
                        # The support may be added in the future 
                        self.log.error(f"The requested operation \'{key}\' is not currently supported")
                        return False
                    else:
                        self.log.error(f"Encountered unknown operation type \'{key}\'")
                        return False
          
            elif tab == "Sub-Accounts":
                # "Sub-Accounts" : [
                #     {
                #         "Old Sub-Account ID" : "51",
                #         "Sub-Account ID": "49",
                #         "Description": "Something",
                #         "Vehicle Reg. No": "228",
                #         "Sub-Account Disabled": False
                #     }
                # ]
                
                sub_acc_list = params[tab]
                for i in range(0, len(sub_acc_list)):
                    acc = sub_acc_list[i]
                    if "Old Sub-Account ID" in list(acc.keys()):
                        # Change of information is requested
                        old_id = acc["Old Sub-Account ID"]
                        del acc["Old Sub-Account ID"]

                        if len(old_id) < 11:
                            self.log.warning(f"The provided sub-account id \'{old_id}\' follows incorrect format. It should be prepended with 0's")

                        # Figure out how many 0's to add
                        # The id is 11 digits
                        correct_id = '0' * (11 - len(old_id)) + old_id

                        try:
                            mws.select("Sub-Account list", correct_id, tab=tab)
                        except:
                            self.log.error(f"The provided sub-account with id \'{old_id}\' was not found.")
                            error = True
                    else:
                        # Create new sub-account
                        mws.click("Create Sub-Acct")

                    for key, value in acc.items():
                        mws.set_value(key, value)
                    
                    # Select id field and send "Enter" to confirm changes to sub account information
                    mws.get_control("Sub-Account ID").set_focus()
                    pkb.send_keys('{ENTER}')
                    
            else:
                for key, value in params[tab].items():
                    # Example:
                    #    key = "Seller must be at least"
                    #    value = True

                    self.log.debug(f"Current key is \'{key}\' and value is \'{value}\'")

                    # Check whether the option is available for current card type
                    if key in self.UNSUPPORTED[operation][account_type]:
                        self.log.warning(f"The configuration contains the parameter \'{key}\' that is not available for current card type \'{account_type}\'.")
                        error = True

                    # Check if the tab support buttons, and key is a button
                    elif tab in list(self.TAB_BUTTONS) and key in self.TAB_BUTTONS[tab]:
                        if value and not mws.search_click_ocr(key):
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

        if not mws.click_toolbar("Save"):
            self.log.error("Unable to save Local Accounts Maintenance")
            error = True
        
         # Check for top bar message
        if not self._check_top_bar_msg(wait=3):
            system.takescreenshot()
            error = True
            top_bar_message = mws.get_top_bar_text()
            self.log.error(f"The top bar message is \'{top_bar_message}\'")
            self.log.error("Unable to save the account")
            try:
                mws.click_toolbar("OK")
                mws.click_toolbar("CANCEL")
                mws.click_toolbar("YES")
            except:
                self.log.error("Failed to dismiss the message. Recovering...")
                mws.recover()
                return False

        # Check for errors
        if error:
            self.log.error("There were errors in the process of configuring Local Accounts Maintenance")
            return False
        
        return True

    def _click_on_popup_msg(self, text, btn):
        """
        Private function that clicks the button with the provided text 
        if the popup message text is equal to expected text.
        The function logs errors and takes screenshots.
        Args:
            text: (str) the expected text of the popup message
            btn: (str) the text on the button. Make sure that the text is what OCR will actually see
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
    
    def _check_top_bar_msg(self, msg="", wait=10):
        """
        Private method that makes sure that the top bar contains
        the text that mathces the given msg after the time defined by wait param.
        Args:
            msg: (str) the message the top bar should match
            wait: (int) a time in seconds after which the the top bar will be checked
        
        Returns:
            True: if the top bar message matched the given msg
            False: if the top bar message did not match the given msg
        """
        time.sleep(wait)

        self.log.debug(f"The top bar message is \'{mws.get_top_bar_text()}\'")
        self.log.debug(f"The return from check_msg is \'{mws.get_top_bar_text() == msg}\'")
        return mws.get_top_bar_text() == msg