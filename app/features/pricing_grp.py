from app import mws
from app import Navi, system
import logging, time

class PricingGroup:
    def __init__(self):
        PricingGroup.navigate_to()
        self.log = logging.getLogger()
        pass

    @staticmethod
    def navigate_to():
        """
        Navigates to the Pricing Group feature module.
        """
        return Navi.navigate_to("pricing group")

    def add(self, pricing_group):
        """
        Description: Adds a new pricing group.
        Args:
            pricing_group: A string containing the name of the new pricing group.
        Returns:
            bool: Success/Failure
        """
        #Clicking the Add button
        mws.click_toolbar("Add")
        #Setting the configuration according to config:
        time.sleep(1) #Waits for control box to load, 
                      #change this line if you know a better way to do this.
        if not mws.set_value("Pricing Group",pricing_group):
            self.log.debug("Could not set pricing group name.")
            system.takescreenshot()
            return False
        mws.click_toolbar("Save")
        # Verifiying the group was added by checking if it's in the list
        self.log.debug("Checking to see if the group was added...")
        if not mws.set_value("Pricing Groups", pricing_group):
            self.log.error(f"{pricing_group} is not in list, addition unsuccessful.")
            system.takescreenshot()
            return False
        return True

    def apply(self, pricing_group, config):
        """
        Description: Applies specified pricing changes to a pricing group.
        Args:
            config: A dictionary of controls so the user can add the information that
            they need to. This is according to the schema in controls.json.
        Returns:
            bool: Success/Failure
        Example: 
            /code
            pg_info = {
                "Pricing Group":"Pricing Group 1", # ONLY include if changing p.g. name
                "Pricing":{
                    "Increase Price": True,
                    "amount per unit": "1.00",
                    "Change tax group to": "No Tax"
                }
            }
            pg = pricing_grp.PricingGroup()
            pg.add("pg_info")
            /endcode
        """
        #Selecting the Pricing Group that needs to be changed:
        if not mws.set_value("Pricing Groups", pricing_group):
            self.log.error(f"Could not find {pricing_group} in list.")
            system.takescreenshot()
            return False
        #Click the change button:
        mws.click_toolbar("Change")
        #Setting the configuration according to config:
        for tab in config:
            # If tab isn't a dictionary (its a string), 
            # use its value to rename the pricing group
            if type(config[tab]) != dict:
                self.log.debug(f"Trying to set the {tab} control to value {config[tab]}")
                time.sleep(1) # Gives time for "Pricing Group" control to load,
                              # If there is a better way to do this, please edit
                if not mws.set_value(tab,config[tab]):
                    self.log.error(f"Could not set {tab} control to {config[tab]}")
            # If tab is a dictionary, use its values to fill in the tab
            else:
                self.log.debug(f"Configuring the {tab} tab.")
                if not mws.select_tab(tab):
                    self.log.error(f"Could not find the {tab} tab.")
                    return False
                #Set values within the selected tab
                for key, value in config[tab].items():
                    if not mws.set_value(key, value, tab):
                        self.log.error(f"Could not set {key} with {value} on the {tab} tab.")
                        return False
        mws.click_toolbar("Save")
        msg = mws.get_top_bar_text()
        start_time = time.time()
        while msg:
            if msg != "Saving Pricing Group":
                self.log.error(f"Got an unexpected message when trying to save pricing group: {msg}")
                mws.click_toolbar("Cancel")
                return False
            elif time.time() - start_time > 30: # Just in case, to avoid infinite loop
                self.log.error("Took more than 30 seconds to save pricing group. Passport is probably stuck!")
                mws.recover()
                return False
            msg = mws.get_top_bar_text()
        return True
        
    def delete(self, pricing_group):
        #Selecting the Pricing Group to delete
        if not mws.set_value("Pricing Groups",pricing_group):
            self.log.error(f"Could not find {pricing_group} in list.")
            system.takescreenshot()
            return False
        #Clicking the Delete button
        mws.click_toolbar("Delete")
        #Clicking Yes to Verify deletion
        mws.click_toolbar("Yes")
        #Verifying that deletion is successful
        if mws.set_value("Pricing Groups", pricing_group):
            self.log.error(f"{pricing_group} is still in list, deletion unsuccessful.")
            system.takescreenshot()
            return False
        else:
            self.log.debug(f"{pricing_group} not found, deletion successful.")
            return True