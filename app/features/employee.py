from app.framework import mws, Navi
import logging

class Employee:
    def __init__(self):
        Employee.navigate_to()
        self.log = logging.getLogger()

    @staticmethod
    def navigate_to():
        return Navi.navigate_to("Employee")

    def add(self, config):
        """
        Adds an employee for the user.
        Args:
            config: A dictionary of controls so the user can add the information that
                      they need to. This is according to the schema in controls.json.
        Returns:
            True: If the employee was successfully added.
            False: If something went wrong with adding the employee (will be logged).
        """
        mws.click_toolbar("Add")
        for tab in config:
            mws.select_tab(tab)
            for key, value in config[tab].items():
                if not mws.set_value(key, value, tab):
                    self.log.error(f"Could not set {key} with {value} on the {tab} tab.")
                    return False
        mws.click_toolbar("Save")
        msg = mws.get_top_bar_text()
        if msg and "error" in msg:
            log.warning(f"Failed to save employee. Error message: {msg}")
            mws.click_toolbar("Cancel")
            mws.click_toolbar("No")
            return False
        return True

    def change(self, employee_id, config):
        """
        Changes an employee's information for the user.

        Args:
            employee_id: The ID number of the employee that needs to have their information changed.
            config: A dictionary of controls so the user can add the information that
                      they need to. This is according to the schema in controls.json.
        Returns:
            True: When the employee's information was successfully changed.
            False: If something went wrong while changing the employee information (will be logged).
        """
        mws.set_value("Employees", employee_id)
        mws.click_toolbar("Change")
        for tab in config:
            mws.select_tab(tab)
            for key, value in config[tab].items():
                if not mws.set_value(key, value, tab):
                    self.log.error(f"Could not set {key} with {value} on the {tab} tab.")
                    return False
        mws.click_toolbar("Save")
        msg = mws.get_top_bar_text()
        if msg and "error" in msg:
            self.log.error(f"Failed to save employee. Error message: {msg}")
            mws.click_toolbar("Cancel")
            mws.click_toolbar("No")
            return False
        return True

    def delete(self, employee_id):
        #TODO: Something with Database dumping...
        pass