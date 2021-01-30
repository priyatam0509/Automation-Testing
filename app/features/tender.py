from app import mws
from app import Navi, system
import logging, time

class TenderMaintenance:
    def __init__(self):
        self.log = logging.getLogger()
        TenderMaintenance.navigate_to()
        # Tab load order affects control IDs, so configure() must visit tabs in this specific order
        self.tab_order = ["Tender Code","Tender Description","General","Currency And Denominations","Functions","Min/Max","Register Groups"]
    
    @staticmethod
    def navigate_to():
        """
        Navigates to the Tender Maintenance feature module.
        Args: None
        Returns: Returns the result of execution of Navi.navigate_to()
        """
        return Navi.navigate_to("tender maintenance")

    def configure(self, tender_name, config, active = None):
        """
        Description: Configures an existing tender type or adds a new one if tender_name does not
                     match an existing tender.
        Args:
            tender_name: A string specifying the name of your tender type. This is what
                         the program searches for in the list of tenders. Should match the
                         "Tender Description" control.
            config: A dictionary of controls so the user can add the information that
                    they need to. This is according to the schema in controls.json.
            active: A boolean value specifying whether to activate or deactivate the currency
            following configuration.
        Returns:
            bool: Success/Failure
        Example: 
            /code
            tender_info = {
                "Tender Code": "1234",
                "Tender Description": "USD",
                "General": {
                    "Tender group this tender belongs to": "Cash",
                    "Safe drops allowed for this tender": True,
                    "Print tax invoice text on Receipt": True,
                    "Receipt Description": "Test Desc",
                    "Tender Button Description": "Test Desc",
                    "NACS Tender Code": "generic"
                },
                "Currency And Denominations": {
                    "Currency": "US Dollars",
                    "Round this tender": True,
                    "Hundred Dollar Bill": { 
                        "Description": "Hundred Dollar Bill",
                        "Amount": "100.00",
                        "Bill": True
                    },
                    "Twenty Dollar Bill": { 
                        "Description": "Twenty Dollar Bill",
                        "Amount": "20.00",
                        "Bill": True
                    }
                },
                "Functions": {
                    "Sale": {
                        "Show exact amount button": True,
                        "Show next highest button": True,
                        "Select a denomination then select one of the preset buttons": {
                            "Hundred Dollar Bill": ["Preset button top left", "Preset button bottom left"],
                            "Twenty Dollar Bill": ["Preset button top right", "Preset button bottom right"]
                        }
                    },
                    "Refund": {
                        "Show exact amount button": True,
                        "Select a denomination then select one of the preset buttons": {
                            "Hundred Dollar Bill": ["Preset button top left", "Preset button bottom left"],
                            "Twenty Dollar Bill": ["Preset button top right", "Preset button bottom right"]
                        }
                    },   
                    "Loan": False
                },
                "Min/Max": {
                    "Minimum Allowed": "0.00",
                    "Maximum Allowed": "100.00",
                    "Repeated Use Limit": "5",
                    "Maximum Refund": "25.00",
                    "Primary tender for change": "USD",
                    "Maximum primary change allowed": "100.00",
                    "Secondary tender for change": "Cash"
                },
                "Register Groups": {
                    "POSGroup1": {
                        "Sales": True,
                        "Refunds": False,
                        "Loans": True,
                        "Paid In": False,
                        "Paid Out": True,
                        "Open cash drawer when this tender is received": True
                    }
                }
            }
            tm = tender.TenderMaintenance()
            tm.configure("USD", tender_info, False)
            True
            /endcode
        """
        # Create a new dictionary config_ordered so configure() goes through tabs in order
        config_ordered = {}
        for tab in self.tab_order:
            try:
                config_ordered[tab] = config[tab]
            except: # if there is no config[tab]
                config_ordered[tab] = {} # create an empty dict so configure() visits the tab anyway

        # Check to see if tender to add already exists...
        if mws.set_value("Tenders", tender_name):
            self.log.debug(f"{tender_name} already exists, clicking Change...")
            mws.click_toolbar("Change")
        else:
            self.log.debug(f"Adding {tender_name}...")
            mws.click_toolbar("Add")

        # Begin setting controls
        for tab in config_ordered:
            # Set top two tab-independent fields
            if tab == "Tender Code" or tab == "Tender Description":
                if not mws.set_value(tab, config_ordered[tab]):
                    self.log.error(f"Could not set '{tab}' control to '{config_ordered[tab]}'")
                    system.takescreenshot()
                    return False
                continue

            # Set tab-specific controls...
            elif tab == "General":
                mws.select_tab(tab)
                for key, value in config_ordered[tab].items():
                    if not mws.set_value(key,value):
                            self.log.error(f"Could not set '{key}' control to '{value}' in '{tab}' tab.")
                            system.takescreenshot()
                            return False
                    # Certain tender groups trigger a message bar popup...
                    if mws.get_top_bar_text():
                        mws.click_toolbar("OK")
                    if not self.confirm_control_value(key,value):
                        return False
                        
            elif tab == "Currency And Denominations" or tab == "Currency and Denominations":
                self.log.debug("Navigating to Currency and Denominations")
                mws.select_tab("Denominations")
                for key, value in config_ordered[tab].items():
                    # Check if a denomination is being configured
                    if type(value) == dict:
                        ctrl_wrapper = mws.process_conn["ListView2"]
                        # Check if the denomination is already in the list
                        if mws.set_value("Denominations",key):
                            self.log.debug(f"{key} denomination exists, editing...")
                            for key2, value2 in config_ordered[tab][key].items():
                                if key2 == "Bill":
                                    # If the "Bill" control is not False or an empty string, enable the "X"
                                    if value2:
                                        mws.set_value(key2,"X")
                                    else:
                                        mws.set_value(key2,"")
                                elif not mws.set_value(key2,value2):
                                    self.log.error(f"Could not set '{key2}' control to '{value2}'.")
                                    return False
                            mws.click("Change")
                            # Deselect the current denomination for next one to work
                            ctrl_wrapper.deselect(key)
                        else:
                            for key2, value2 in config_ordered[tab][key].items():
                                # If the "Bill" control is not False or an empty string, enable the "X"
                                if key2 == "Bill" and value2:
                                    mws.set_value(key2,"X")
                                # Set other controls
                                elif not mws.set_value(key2,value2):
                                    self.log.error(f"Could not set '{key2}' control to '{value2}'.")
                                    return False
                            mws.click("Add")
                            # Deselect the current denomination for next one to work
                            ctrl_wrapper.deselect(key)
                    else: 
                        if not mws.set_value(key,value):
                            self.log.debug(f"Could not set '{key}' control to '{value}'")
                            system.takescreenshot()
                            return False
                        if not self.confirm_control_value(key,value):
                            return False 

            elif tab == "Functions":
                mws.select_tab(tab)
                # Begin configuring each individual Application Function
                for applicationfunc in config_ordered[tab]:
                    # Just enable/disable
                    if type(config_ordered[tab][applicationfunc]) == bool:
                        check = config_ordered[tab][applicationfunc]
                        if not mws.select_checkbox(applicationfunc, check=check, tab=tab, list="Application Functions"):
                            self.log.error(f"Could not {'enable' if check else 'disable'} {applicationfunc}.")
                            return False
                        continue

                    # Enable + configure options
                    if not mws.select_checkbox(applicationfunc, check=True, tab=tab, list="Application Functions"):
                        self.log.error(f"Could not set '{applicationfunc}' checkbox in '{tab}' tab.")
                        return False
                    for key, value in config_ordered[tab][applicationfunc].items():
                        # Check to see if the preset buttons are being set
                        if type(value) == dict:
                            # Iterate through each denomination and set all preset buttons
                            for denomination, buttonlist in config_ordered[tab][applicationfunc][key].items():
                                mws.set_value(key, denomination)
                                for button in buttonlist:
                                    mws.click(button)
                        # Configure other controls
                        else:
                            if not mws.set_value(key,value):
                                self.log.debug(f"Could not set '{key}' control to '{value}' in '{tab}' tab.")
                                system.takescreenshot()
                                return False

            elif tab == "Min/Max":
                mws.select_tab("Max") #OCR does not recognize the '/' character
                for key, value in config_ordered[tab].items():
                    if not mws.set_value(key,value):
                        self.log.error(f"Could not set '{key}' control to '{value}' in '{tab}' tab.")
                        system.takescreenshot()
                        return False
                    if not self.confirm_control_value(key,value):
                        return False
            elif tab == "Register Groups":
                mws.select_tab(tab)
                for registergroup in config_ordered[tab]:
                    mws.select_checkbox(registergroup, tab= tab, list= "Register Groups")
                    for key, value in config_ordered[tab][registergroup].items(): 
                        if not mws.set_value(key,value):
                            self.log.error(f"Could not set '{key}' control to '{value}' in '{tab}' tab.")
                            system.takescreenshot()
                            return False
            else:
                self.log.error(f"Tab name '{tab}' not recognized.")
                return False
        
        mws.click_toolbar("Save", submenu=True)
        msg = mws.get_top_bar_text()
        if msg and "error" in msg:
            self.log.error(f"Got an unexpected message while trying to save {tender_name}: {msg}")
            mws.click_toolbar("Cancel", submenu=True)
            return False

        # Configure active/inactive status if specified:
        if active != None and type(active) == bool:
            # Convert from bool to string
            if active == True:
                intended = "Active"
            else:
                intended = "Inactive"     
            # Allows control box to appear before continuing
            start_time = time.time()
            timeout = 10
            while time.time() - start_time < timeout and mws.get_top_bar_text():
                continue
            for tender in mws.get_value("Tenders"):
                # Find the tender being configured
                if tender[0] == tender_name:
                    # Check if the current setting is different from the desired setting
                    if tender[2] != intended:
                        if not mws.set_value("Tenders",tender_name):
                            self.log.debug(f"Failed while setting {tender_name} to Activity status: {active}. Make sure tender_name and Tender Description are identical.")
                            return False
                        mws.click_toolbar("Activate/Deactivate")

        return True

    def configure_denomination(self, action, select= None, desc= None, amount= None, bill= False):
        """
        Description: Adds, configures, or deletes a denomination on the Currency and Denominations tab.
                     Must be called while within Tender configuration menus (not Tender Maintenance homepage).
        Args:
            action: A string (Either "Add", "Change", or "Delete") that specifies the operation to perform.
            select: A string that specifies which tender to select out of the "Denominations" list.
                    Not necessary to include if adding a new denomination.
            desc: A string to fill into the "Description" field if adding/changing.
            amount: A string to fill into the "Amount" field if adding/changing.
            bill: A boolean to specify whether the "Bill" field is checked or not. 
        Returns:
            bool: Success/Failure
        Example: 
            tender.configure_denomination("Add", desc= "new_tender", amount= "1.00", bill= True)
            True
            tender.configure_denomination("Delete", "tender_to_be_deleted")
            True
        """
        mws.select_tab("Denominations")
        # If there are existing denominations, one will be selected upon loading the tab.
        # It needs to be deselected before proceeding ("Add" is a good way to do this if nothing has been changed).
        mws.click("Add")

        if action == "Delete":
            # Select denomination
            if not mws.set_value("Denominations", select):
                self.log.error(f"Could not find '{select}' in Denominations.")
                return False
            # Click delete
            mws.click(action, tab= "Currency And Denominations")
            # Navigate back to tab in case faulty controls caused mws.click() to click another tab
            mws.select_tab("Denominations")
            # Check for successful deletion
            if mws.set_value("Denominations", select):
                self.log.error(f"Could not delete {select} successfully.")
                system.takescreenshot()
                return False
        
        else: # if action is "Add" or "Change"
            if action == "Change":
                mws.set_value("Denominations", select)
            # Set all fields
            mws.set_value("Description", desc)
            mws.set_value("Amount", amount)
            if bill != bool(mws.get_value("Bill")):
                mws.click("Bill", "Currency And Denominations")
            # Click add/change (and check for typos)
            if not mws.click(action, tab= "Currency And Denominations"):
                self.log.error(f"'{action}' is not a supported action.")
                return False
            # Navigate back to tab in case faulty controls caused mws.click() to click another tab
            mws.select_tab("Denominations")
            # Check the new desc is in the list
            if not mws.set_value("Denominations", desc):
                self.log.error(f"Could not add {desc} successfully.")
                system.takescreenshot()
                return False
            
        return True

    def change_status(self, tender_name, status):
        """
        Description: Changes the Active/Inactive status of an existing tender.
        Args:
            tender_name: A string specifying the name of your tender type. This is what
                         the program searches for in the list of tenders.
            status: A boolean value: True for "Active" and False for "Inactive". 
        Returns:
            bool: Success/Failure
        Example: tender.change_status("Credit", False)
                 True
        """

        if type(status) == bool:
            # Convert from bool to string
            if status == True:
                intended = "Active"
            else:
                intended = "Inactive"
            for tender in mws.get_value("Tenders"):
                # Find the tender being configured
                if tender[0] == tender_name:
                    # Check if the current setting is different from the desired setting
                    if tender[2] != intended:
                        if not mws.set_value("Tenders",tender_name):
                            self.log.debug(f"Failed while setting {tender_name} to Activity status: {status}. Make sure tender_name and Tender Description are identical.")
                            return False
                        mws.click_toolbar("Activate/Deactivate")
                        return True
        else: 
            self.log.error("Status parameter must be a boolean value.")
            return False

    def confirm_control_value(self, control, intended=True):
        """
        Decription: Checks if a control was successfully set and, if not, re-attempts to set the control.
                    Will often be needed immediately after using mws.select_tab()
        Args:
            control: A string specifying the name of the control to check.
            intended: The intended value of the control upon calling the function. 
        Returns:
            bool: Success/Failure
        """
        if type(mws.get_value(control)) == list:
            if mws.get_value(control)[0] != intended:
                self.log.debug(f"Setting '{control}' to '{intended}' didn't work, retrying...")
                if not mws.set_value(control,intended):
                    self.log.debug(f"After repeated attempts, '{control}' could not be set to '{intended}. Failing...'")
                    system.takescreenshot()
                    return False
        else:
            if mws.get_value(control) != intended:
                self.log.debug(f"Setting '{control}' to '{intended}' didn't work, retrying...")
                if not mws.set_value(control,intended):
                    self.log.debug(f"After repeated attempts, '{control}' could not be set to '{intended}. Failing...'")
                    system.takescreenshot()
                    return False
        return True


