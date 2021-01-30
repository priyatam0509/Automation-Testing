from app import mws, Navi
import logging

class ForecourtInstallation:

    def __init__(self, blended_site = False):
        self.log = logging.getLogger()
        self.blended_site = blended_site
        ForecourtInstallation.navigate_to()
        self.black_list = [
            "payment terminals",
            "tank-product to dispensers",
            "grades to dispensers"
        ]
        return

    @staticmethod
    def navigate_to():
        return Navi.navigate_to("Forecourt Installation")

    def add(self, tab, config):
        """
        Adds whatever settings (dispenser, tank, etc.) to forecourt installation.

        Args:
            tab: The tab in which the user wants to add something.
            config: A dictionary of control:value pairs.

        Returns:
            True: If the item could be successfully added.
            False: If something went wrong while adding the item control-wise.
        """
        if tab.lower() in self.black_list:
            self.log.error(f"The {tab} tab does not have an Add function.")
            return False
        mws.select_tab(tab)
        mws.click("Add", tab)
        for key, value in config.items():
            if not mws.set_value(key, value, tab):
                self.log.error(f"Could not set {key} with {value}")
                return False
        mws.click("Update List", tab)
        return True

    def change(self, item, tab, config):
        """
        Changes whatever settings (dispenser, tank, etc.) to forecourt installation.

        Args:
            tab: The tab in which the user wants to change something.
            config: A dictionary of control:value pairs.

        Returns:
            True: If the item could be successfully changed.
            False: If something went wrong while changing the item control-wise.
        """
        mws.select_tab(tab)
        list_view_name = {
            "Dispensers" : "Dispensers",
            "Kiosks" : "Kiosks",
            "Payment Terminals" : "Terminals",
            "Product" : "Products",
            "Tanks" : "Tanks",
            "Tank - Product to Dispensers" : "Dispensers",
            "Grades to Dispensers" : "Dispensers",
            "Grade" : "Grades",
            "Tank Monitor" : "Monitors",
            "Tank Probe" : "Tank Monitors"
        }
        #Selecting the item and then clicking change.
        if not mws.set_value(list_view_name[tab], item, tab):
            self.log.error(f"Could not select {item} on the {tab} tab.")
            return False
        mws.click("Change", tab)
        for key, value in config.items():
            if not mws.set_value(key, value, tab):
                self.log.error(f"Could not set {key} with {value}")
                return False
        mws.click("Update List", tab)
        return True

    def delete_last(self, tab):
        """
        Deletes the last created item on the user defined tab.

        Args:
            tab: The tab in which the last item will be deleted.
        Returns:
            True: If the item was successfully deleted.
            False: If the item could not be deleted for some reason. (Will be logged)
        """
        if tab.lower() in self.black_list:
            self.log.error(f"The {tab} tab does not have a 'Delete Last' function.")
        mws.select_tab(tab)
        if not mws.click("Delete Last", tab):
            self.log.error(f"Could not click the Delete Last button on the {tab} tab.")
            return False
        mws.click_toolbar("Yes")
        return True