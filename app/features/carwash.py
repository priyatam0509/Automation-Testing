from app import mws, system, Navi
import logging, time

class CarWashMaintenance:

    def __init__(self):
        self.log = logging.getLogger()
        CarWashMaintenance.navigate_to()

    @staticmethod
    def navigate_to():
        """
        Navigates to the Car Wash Maintenance feature module.
        Args: None
        Returns: Returns the result of execution of Navi.navigate_to()
        """
        return Navi.navigate_to("car wash maintenance")


    def add(self, config):
        """
        Adds a Car Wash for the user.
        Args:
            config: A dictionary of controls so the user can add the information that
                      they need to. This is according to the schema in controls.json.
        Returns:
            True: If the site was successfully configured.
            False: If something went wrong with configuring the site (will be logged).
        Examples:
            \code
            cw_info = {
                "Site":{
                    "Type of Car Wash":"Unitec Ryko Emulation",
                    "Disable Car Wash": False,
                    "Car Wash PLU":"1234",
                    "Rewash PLU":"5678",
                    "Receipt Footer 1":"Footer #1",
                    "Receipt Footer 2":"Footer #2",
                    "Print expiration date on customer receipt": True,
                    "Default Expiration": "30"
                },
                "Packages":{
                    "Carwash 1":{ 
                        "Package Name":"New Carwash Name",
                        "Total Price":"5.00",
                        "Tax amount included in package price": True,
                        "Tax amount included in package price edit": "0.50",
                    }
                },
                "Discount":{
                    "Discount Available": True,
                    "Apply Discounts On Prepays": False,
                    "Supreme Discount": {
                        "Service Levels":"Service Levels Select All",
                        "Grades":"Grades Select All",
                        "Packages":"Packages Select All",
                        "When the fuel purchase amount reaches": True,
                        "When the fuel purchase amount reaches edit": "50.00",
                        "Car wash will be discounted by": "5.00"
                    }
                }
            }
            cw = carwash.CarWashMaintenance()
            cw.add(cw_info) 
            True
            \endcode
        """
        # Note: Check controls.json file for updated control names
        
        # Configure the Site Tab first
        try:
            siteConfig = config['Site']
            self.log.debug("Configuring the Site tab")
            # Set the Type of Car Wash field so the rest can be populated
            try:
                typeOfCarWash = siteConfig['Type of Car Wash']
                if not mws.set_value('Type of Car Wash', typeOfCarWash, 'Site'):
                    self.log.error(f"Could not set the Type of Car Wash on the Site tab.")
                    system.takescreenshot()
                    return False
                # If changing to "No Wash", end the configuration process immediately afterwards
                if typeOfCarWash == "No Wash":
                    self.log.debug("Cannot configure other fields when 'No Wash' is selected. Ending configuration...")
                    mws.click_toolbar("Save")
                    return True
            except KeyError:
                pass
            for key, value in siteConfig.items():
                if key == 'Type of Car Wash':
                    continue
                if not mws.set_value(key, value, 'Site'):
                    self.log.error(f"Could not set {key} with {value} on the Site tab.")
                    system.takescreenshot()
                    return False
        except KeyError:
            pass

        # Load every tab before starting so all controls are correct (necessary for add/change/delete buttons)
        mws.select_tab("Packages")
        mws.select_tab("Discount")
        mws.select_tab("CRIND")
        mws.select_tab("Display Order")

        for tab in config:
            mws.select_tab(tab)
            #If on the packages tab handle the sub menu to add/change
            if tab == "Packages":
                self.log.debug(f"Adding CarWash Package")
                for key, value in config[tab].items():
                    self.log.debug(f"Checking if the package exist")
                    if mws.set_value("Packages", key, "Packages"):
                        self.log.debug("Package exists, selecting Change")
                        mws.click("Change","Packages")
                    else:
                        self.log.debug("Package doesn't exist, selecting Add")
                        mws.click("Add", "Packages")
                    #The value in Total Price takes a second to appear
                    start_time = time.time()
                    while time.time() - start_time < 10:
                        if mws.get_text("Total Price") != "":
                            break
                    if mws.get_text("Total Price") == "":
                        self.log.error(f"Total Price failed to load.")
                        system.takescreenshot()
                        return False
                    for key2, value2 in value.items():
                        self.log.info(f"Attempting to set up {key2} with {value2} on {tab} tab.")
                        if not mws.set_value(key2, value2, "Packages Add"):
                            self.log.error(f"Could not set {key2} with {value2} on the {key} tab.")
                            system.takescreenshot()
                            return False
                    mws.click_toolbar("Save")
                    if mws.get_top_bar_text() == "The errors in red must be corrected before you can continue.":
                        self.log.warning("Some part of your configuration is not valid")
                        system.takescreenshot()
                        mws.click_toolbar("Cancel")
                        system.takescreenshot()
                        return False
            elif "Discount" in tab:
                # Configure Checkboxes
                for key, value in config[tab].items():
                    if type(value) != dict:
                        if not mws.set_value(key, value, tab):
                            self.log.error(f"Could not set {key} with {value} on the {tab} tab.")
                            system.takescreenshot()
                            return False
                self.log.debug(f"Adding Car Wash Discounts")
                for key, value in config[tab].items():
                    if type(value) == dict:
                        self.log.debug(f"Checking if {key} exists")
                        if mws.set_value("Discounts", key, "Discount"):
                            self.log.debug(f"Discount exists, selecting Change")
                            mws.click("Change", "Discount")
                        else:
                            self.log.debug("Discount doesn't exist, selecting Add")
                            mws.click("Add", "Discount")
                        for key2, value2 in value.items():
                            #TODO: Add support for the lists within Discounts Add page
                            if key2 == "Service Levels" or key2 == "Grades" or key2 == "Packages":
                                if "Select All" not in value2:
                                    self.log.warning(f"We can only Select All for {key2} at this time")
                                    continue
                                else:
                                    if not mws.click(value2):
                                        self.log.error(f"Could not click the {value2} button.")
                                        return False
                            else:
                                self.log.info(f"Attempting to set up {key2} with {value2} on {tab} tab.")
                                if not mws.set_value(key2, value2, "Discount Add"):
                                    self.log.error(f"Could not set {key2} with {value2} on the {key} tab.")
                                    system.takescreenshot()
                                    return False
                        mws.click_toolbar("Save")

            # TODO: Add support for Display Order tab (up/down buttons)
            elif "Display Order" in tab:
                self.log.warning("Display Order tab is not currently supported. Skipping...")
                continue
            elif tab != "Site":
                self.log.debug(f"Configuring Tab: {tab}")
                for key, value in config[tab].items():
                    if not mws.set_value(key, value, tab):
                        self.log.error(f"Could not set {key} with {value} on the {tab} tab.")
                        system.takescreenshot()
                        return False
        try:
            mws.click_toolbar("Save", main=True)
        except mws.ConnException:
            self.log.error(f"Unable to save Car Wash Maintenance. Top bar message: {mws.get_top_bar_text()}")
            mws.recover()
            return False
        return True

    def change(self, config):
        """
        Configures already-created car wash settings. Will edit pre-existing packages
        and discounts, and add ones that are not already made. 
        Args:
            config: A dictionary of controls so the user can add the information that
                        they need to. This is according to the schema in controls.json.
        Returns:
            True: If the site was successfully configured.
            False: If something went wrong with configuring the site (will be logged).
        Examples:
            See "Add" example.
        
        """

        # Configure the Site Tab first
        try:
            siteConfig = config['Site']
            self.log.debug("Configuring the Site Tab")
            # Change the Type of Car Wash field to what was specified
            try: 
                typeOfCarWash = siteConfig['Type of Car Wash']
                if not mws.set_value('Type of Car Wash', typeOfCarWash, 'Site'):
                    self.log.error(f"Could not set the Type of Car Wash on the Site tab.")
                    system.takescreenshot()
                    return False
                # If changing to "No Wash", end the configuration process immediately afterwards
                if typeOfCarWash == "No Wash":
                    mws.click_toolbar("Save")
                    return True
            except KeyError:
                pass
            # Configure all other fields in Site tab
            for key, value in siteConfig.items():
                if key == 'Type of Car Wash':
                    continue
                if not mws.set_value(key, value, 'Site'):
                    self.log.error(f"Could not set {key} with {value} on the Site tab.")
                    system.takescreenshot()
                    return False
        # If no 'Site' tab within given dictionary, do not change existing 'Site' tab
        except KeyError:
            self.log.debug("Skipping Site tab configuration")
            pass

        # Load every tab before starting so all controls are correct (necessary for add/change/delete buttons)
        mws.select_tab("Packages")
        mws.select_tab("Discount")
        mws.select_tab("CRIND")
        mws.select_tab("Display Order")

        for tab in config:
            mws.select_tab(tab)
            # Configure Packages Tab
            if tab == "Packages":
                self.log.debug(f"Adding/changing Car Wash packages")
                for key, value in config[tab].items():
                    self.log.debug(f"Checking if the {key} package exists...")
                    if mws.set_value("Packages", key, "Packages"):
                        self.log.debug(f"{key} exists, selecting Change.")
                        # Search coordinates encompass "Add","Change",and "Delete" buttons
                        mws.click("Change","Packages")
                    else:
                        self.log.debug(f"{key} doesn't exist, selecting Add.")
                        mws.click("Add", "Packages")
                    #The value in Total Price takes a second to appear
                    start_time = time.time()
                    while time.time() - start_time < 10:
                        if mws.get_text("Total Price") != "":
                            break
                    if mws.get_text("Total Price") == "":
                        self.log.error(f"Total Price failed to load.")
                        system.takescreenshot()
                        return False
                    for key2, value2 in value.items():
                        self.log.info(f"Attempting to set up {key2} with {value2} on {tab} tab.")
                        if not mws.set_value(key2, value2, "Packages Add"):
                            self.log.error(f"Could not set {key2} with {value2} on the {key} tab.")
                            system.takescreenshot()
                            return False
                    mws.click_toolbar("Save")
                    if mws.get_top_bar_text() == "The errors in red must be corrected before you can continue.":
                        self.log.warning("Some part of your configuration is not valid")
                        system.takescreenshot()
                        mws.click_toolbar("Cancel")
                        system.takescreenshot()
                        return False
            elif "Discount" in tab:
                for key, value in config[tab].items():
                    if type(value) != dict:
                        self.log.debug("Configuring checkboxes...")
                        if not mws.set_value(key, value, tab):
                            self.log.error(f"Could not set {key} with {value} on the {tab} tab.")
                            system.takescreenshot()
                            return False
                self.log.debug(f"Adding/changing CarWash discounts")
                for key, value in config[tab].items():
                    if type(value) == dict:
                        self.log.debug(f"Checking if the {key} discount exists")
                        if mws.set_value("Discounts", key, "Discount"):
                            self.log.debug(f"{key} discount exists, selecting Change")
                            # Search coordinates encompass "Add","Change",and "Delete" buttons
                            mws.click("Change","Discount")
                        else:
                            self.log.debug(f"{key} discount doesn't exist, selecting Add")
                            mws.click("Add","Discount")
                        for key2, value2 in value.items():
                            #TODO: Add support for the lists within Discounts Add page
                            if key2 == "Service Levels" or key2 == "Grades" or key2 == "Packages":
                                if "Select All" not in value2:
                                    self.log.warning(f"We can only Select All for {key2} at this time")
                                    continue
                                else:
                                    if not mws.click(value2):
                                        self.log.error(f"Could not click the {value2} button.")
                                        return False
                            else:
                                self.log.info(f"Attempting to set up {key2} with {value2} on {tab} tab.")
                                if not mws.set_value(key2, value2, "Discount Add"):
                                    self.log.error(f"Could not set {key2} with {value2} on the {key} tab.")
                                    system.takescreenshot()
                                    return False

                        mws.click_toolbar("Save")
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
            self.log.error(f"Unable to save Car Wash Maintenance. Top bar message: {mws.get_top_bar_text()}")
            mws.recover()
            return False
        return True

    def delete(self, packages, discounts):
        """
        Deletes specified car wash packages and discounts.
        Args:
            packages: A string or list of strings that specifies packages to delete
            discounts: A string or list of strings that specifies discounts to delete
        Returns:
            True: If the site was successfully configured.
            False: If something went wrong with configuring the site (will be logged).
        Examples:
            cw = carwash.CarWashMaintenance()
            cw.delete(packages= ["Carwash 1","Carwash 2"], discounts= ["Discount 1","Discount 2"]) 
            True
        """
        # Check to make sure "No Wash" is not selected
        self.log.debug("Checking Car Wash type...")
        if not mws.select_tab("Site"):
            self.log.error("Could not find Site tab")
            system.takescreenshot()
            return False
        if mws.get_value("Type of Car Wash")[0] == "No Wash":
            self.log.error("Type set to 'No Wash', could not configure Packages or Discounts")
            return False
        
        # Load every tab before starting so all controls are correct (necessary for add/change/delete buttons)
        mws.select_tab("Packages")
        mws.select_tab("Discount")
        mws.select_tab("CRIND")
        mws.select_tab("Display Order")

        # Start with Discount tab to avoid listbox ID assignment issues
        mws.select_tab("Discount")
        # Remember checkbox value and reinstate after discounts have been deleted
        discountenabled = mws.status_checkbox("Discount Available")
        if discountenabled == False:
            if not mws.select_checkbox("Discount Available",check=True):
                self.log.debug("Could not enable Discount Available checkbox, cannot configure discounts")
                system.takescreenshot()
                return False

        # Force discounts to be in list
        if type(discounts) != list:
            discounts = [discounts]

        for discount in discounts:
            # Iterate through discounts and check to see if they're in the list
            self.log.debug(f"Attempting to delete {discount}...")
            if mws.set_value("Discounts", discount, "Discount"):
                self.log.debug(f"{discount} discount exists, selecting Delete")
                # Search coordinates encompass "Add","Change",and "Delete" buttons
                if not mws.click("Delete","Discount"):
                    self.log.error(f"Could not click Delete button to delete {discount} discount.")
                    return False
                if not mws.click_toolbar("Yes"):
                    self.log.error(f"Could not click Yes to delete {discount} discount.")
                    return False
            else:
                self.log.debug(f"{discount} discount doesn't exist. Skipping...")
        #Revert checkbox to previous state
        mws.select_checkbox("Discount Available", check=discountenabled)
              
        # Configure Packages Tab
        mws.select_tab("Packages")

        # Force packages to be in list
        if type(packages) != list:
            packages = [packages]

        for package in packages:
            self.log.debug(f"Attempting to delete {package}...")
            if mws.set_value("Packages", package, "Packages"):
                self.log.debug(f"{package} exists, selecting Delete")
                # Search coordinates encompass "Add","Change",and "Delete" buttons
                if not mws.click("Delete","Packages"):
                    self.log.error(f"Could not click Delete button to delete {package} package.")
                    return False
                if not mws.click_toolbar("Yes"):
                    self.log.error(f"Could not click Yes to delete {package} package.")
                    return False
            else:
                self.log.debug(f"{package} doesn't exist. Skipping...")

        try:
            mws.click_toolbar("Save", main=True)
        except mws.ConnException:
            self.log.error(f"Unable to save Car Wash Maintenance. Top bar message: {mws.get_top_bar_text()}")
            mws.recover()
            return False
        return True