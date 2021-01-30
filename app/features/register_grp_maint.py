from app.framework import mws, Navi
import logging

log = logging.getLogger()

class RegisterGroupMaintenance:
    def __init__(self):
        RegisterGroupMaintenance.navigate_to()
        return

    @staticmethod
    def navigate_to():
        return Navi.navigate_to("Register Group Maintenance")

    def add(self, config):
        """
        Description: Add a new register group.
        Args:
            config: A dictionary of controls so the user can add the information that
                      they need to. This is according to the schema in controls.json.
        Returns:
            bool: Success/failure
        """
        mws.click_toolbar("Add", submenu=True)
        for tab in config:
            for key, value in config[tab].items():
                mws.select_tab(tab)
                if not mws.set_value(key, value):
                    mws.click_toolbar("Cancel")
                    mws.click_toolbar("No")
                    return False
        mws.click_toolbar("Save")

        accepted_msgs = {
            "",
            "Sending reload message to registers.",
            "Saving register group options."
        }
        msg = mws.get_top_bar_text()
        if msg not in accepted_msgs:
            log.warn(f"Got an error when saving new register group: {msg}")
            return False

        return True

    def change(self, group_name, config):
        """
        Description: Change the configuration for an existing register group.
        Args:
            group_name: The name of the group to change.
            config: A dictionary of controls so the user can add the information that
                      they need to. This is according to the schema in controls.json.
        Returns:
            bool: Success/failure
        """
        mws.set_value("Register Group", group_name)
        mws.click_toolbar("Change", submenu=True)
        for tab in config:
            for key, value in config[tab].items():
                mws.select_tab(tab)
                if not mws.set_value(key, value):
                    mws.click_toolbar("Cancel")
                    mws.click_toolbar("No")
                    return False
        if not mws.click_toolbar("Save"):
            return False
        accepted_msgs = {
            "",
            "Sending reload message to registers.",
            "Saving register group options."
        }
        msg = mws.get_top_bar_text()
        if msg not in accepted_msgs:
            log.warn(f"Got an error when saving {group_name}. Error message: {msg}")
            return False
        return True

    def delete(self, group_name):
        """
        Description: Delete an existing register group.
        Args:
            group_name: The name of the group to delete.
        Returns:
            bool: Success/failure
        """
        mws.set_value("Register Group", group_name)
        mws.click_toolbar("Delete")
        msg = mws.get_top_bar_text()
        if msg == f"Are you sure you want to delete {group_name}?":
            mws.click_toolbar("Yes")
        else:
            log.warn(f"Didn't get the right confirmation message for deleting {group_name}. "
                     f"Actual message: {msg}")
            return False

        if group_name in mws.get_value("Register Group"):
            log.warn(f"Found {group_name} in the list of register groups after deletion.")
            return False

        return True