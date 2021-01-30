from app.framework import Navi, mws
from app.util import system
import logging, pywinauto, copy

class SecurityGroupMaintenance:
    SELECT_ALL_BTN = "Select All"
    CLEAR_BTN = "Clear"
    BTNS = [SELECT_ALL_BTN, CLEAR_BTN]
    DUPLICATE_ERROR_MSG = "The security group description cannot be the same as one that already exists."

    def __init__(self):
        self.log = logging.getLogger()
        SecurityGroupMaintenance.navigate_to()

    @staticmethod
    def navigate_to():
        return Navi.navigate_to("Security Group Maintenance")

    def add(self, config):
        """
        Add a new security group and configure its settings.
        Args:
            config: A dictionary describing the configuration of the new group. See example.
        Returns: (bool) True on success, False on failure
        Example:
            >>> cfg = { "Security Group Description": "Shift Lead", "Security Level": "50",
                "Point Of Sale": "Select All", "Reboot POS": True, "Safe Drop": { "Operator Till Only": True } }
            >>> SecurityGroupMaintenance().add(cfg)
            True
        """
        try:
            descr = config["Security Group Description"]
        except KeyError:
            self.log.warning("Security Group Description must be included in configuration.")
            return False
        mws.click_toolbar("Add")

        if not self._configure_group(config):
            return False

        return self._save_group(descr)

    def copy(self, descr, config):
        """
        Copy an existing security group and configure the copy.
        Args:
            descr: The name of the existing group to copy.
            config: A dictionary describing changes to make to the copy. See example.
        Example:
            >>> cfg = { 
                "Security Group Description": "Shift Manager",
                "Security Level": "55",
                "Store Close": {
                    "Print": True 
                    },
                "Store Options": {
                    "Select All": True,
                    "Enable Store Logging Options": False
                    }
                }
            >>> SecurityGroupMaintenance().copy("Shift Lead", cfg)
            True
        """
        try:
            new_descr = config["Security Group Description"]
        except KeyError:
            self.log.warning("Security Group Description must be included in configuration.")
            return False
        
        if not mws.set_value("Security Groups", descr):
            self.log.warning(f"Security group {descr} not found.")
            return False
        mws.click_toolbar("Copy")

        if not self._configure_group(config):
            return False

        return self._save_group(new_descr)

    def change(self, descr, config):
        """
        Change the settings of an existing security group.
        Args:
            descr: The name of the group to change.
            config: A dictionary describing the changes to be made. See example.
        Returns: (bool) True on success, False on failure
        Example:
            >>> cfg = { "Security Level": "55", "Safe Drop": { "All Tills": True, "Operator Till Only": False },
                "Store Close": { "Print": True }, "Store Options": { "Select All": True, "Enable Store Logging Options": False } }
            >>> SecurityGroupMaintenance().change("Shift Lead", cfg)
            True
        """
        if not mws.set_value("Security Groups", descr):
            self.log.warning(f"Security group {descr} not found.")
            return False
        mws.click_toolbar("Change")

        if not self._configure_group(config):
            return False
        #If we've changed the description we'll need to pass that into `_save_group()`
        try:
            descr = config["Security Group Description"]
        except KeyError:
            log.debug("We didn't change the description. Checking for the old one.")
            
        return self._save_group(descr)

    def delete(self, descr):
        """
        Delete an existing security group.
        Args:
            descr: The name of the group to delete.
        Returns: (bool) True on success, False on failure
        Example:
            >>> SecurityGroupMaintenance().delete("Shift Lead")
            True
        """
        if not mws.set_value("Security Groups", descr):
            self.log.warning(f"Security group {descr} not found.")
            return False
        mws.click_toolbar("Delete")

        if mws.get_top_bar_text() != f"Are you sure you want to delete {descr}?":
            self.log.warning("Didn't get confirmation prompt to delete {descr}.")
            return False
        mws.click_toolbar("YES")

        if mws.set_value("Security Groups", descr):
            self.log.warning(f"Security group {descr} was found after deletion.")
            return False

        return True

    def _configure_group(self, config):
        """
        Helper function to configure settings of a security group.
        """
        config = copy.deepcopy(config) # Make a copy so we don't alter the original
        app_func_control = mws.get_control("Application Functions")
        app_rect = app_func_control.rectangle()
        app_top_left = (app_rect.left, app_rect.top)
        for key, value in config.items():
            if key == "Security Level" or key == "Security Group Description":
                if not mws.set_value(key, value):
                    return False
            # TODO: Add support for Clear here
            elif value == SecurityGroupMaintenance.SELECT_ALL_BTN or value == SecurityGroupMaintenance.CLEAR_BTN:
                # Enable an application and enable or disable all of its functions
                if not mws.set_value(key, True, list="System Applications"):
                    return False
                if not mws.click(value):
                    return False
            elif type(value) is dict:
                # Enable an application and selected functions
                if not mws.set_value(key, True, list="System Applications"):
                    return False
                # Select All/Clear come first
                for btn in SecurityGroupMaintenance.BTNS:
                    try:
                        value[btn]
                        if not mws.click(btn):
                            return False
                        del value[btn]
                    except KeyError:
                        pass
                for func, setting in value.items():
                # We have to click these items manually or else they may not save correctly.
                # Don't ask why. It's a great mystery of the universe.
                    try:
                        func_status = app_func_control.item_texts().index(func) in app_func_control.selected_indices()
                    except ValueError:
                        self.log.warning(f"{func} not found in Application Functions.")
                        return False
                    if func_status != setting:
                        func_mid = app_func_control.item_rect(func).mid_point()
                        click_point = (app_top_left[0] + func_mid.x, app_top_left[1] + func_mid.y)
                        pywinauto.mouse.double_click(coords=click_point)
                    # This is how we would do it if Passport didn't hate us.
                    # if not mws.set_value(func, setting, list="Application Functions"):
                    #     return False
            elif type(value) is bool:
                # Enable or disable an application, don't touch its functions
                if not mws.set_value(key, value, list="System Applications"):
                    return False
            else:
                self.log.warning(f"Unknown value type {type(value)} found in config dictionary.")
                return False
        return True

    def _save_group(self, descr):
        if not mws.click_toolbar("Save"):
            return False
        msg = mws.get_top_bar_text()
        if msg == SecurityGroupMaintenance.DUPLICATE_ERROR_MSG:
            self.log.warning(f"Security group {descr} already exists.")
            mws.click_toolbar("OK")
            mws.click_toolbar("Cancel")
            return False
        elif msg and "Saving" not in msg:
            self.log.warning(f"Got an unexpected message trying to save security group: {msg}")
            return False
        if not mws.set_value("Security Groups", descr):
            self.log.warning(f"{descr} not found in the list of Security Groups after saving.")
        return True
