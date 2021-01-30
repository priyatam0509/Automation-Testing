from app.framework import mws, Navi
import logging

DEPT_FG_OFFSET = 280

class DepartmentMaintenance:

    def __init__(self):
        self.log = logging.getLogger()
        DepartmentMaintenance.navigate_to()
        return

    @staticmethod
    def navigate_to():
        return Navi.navigate_to("Department Maintenance")

    def add(self, config, tender_restr={}, overwrite=False):
        """
        Add a new department.
        Args:
            config: (dict) All of the controls to set in the General Information tab.
                    This will need to be setup according to the schema in controls.json.
            tender_restr: (dict) Tender types to enable or disable restriction for.
            overwrite: (bool) Set True to enable overwriting an existing department (this includes deleted departments).
        Returns:
            bool: True if successful, False if not.
        Example:
            >>> cfg = {"Department Number": "17", "Department Name": "Dept 17", "Discountable": True,
                "Food Stampable": True, "May appear as POS Department key.": False, "Tax Group": "NC Sales Tax"}
            >>> restr = {"driveOff": True, "houseCharges": True, "outsideAuxiliaryDebit": True}
            >>> department.DepartmentMaintenance().add(cfg, restr)
            True
        """
        try:
            config['Department Number']
            config['Department Name']
        except KeyError:
            self.log.error("Config dict must include Department Number and Department Name.")
            return False

        mws.click_toolbar("Add")
        for key, value in config.items():
            if not mws.set_value(key, value):
                self.log.error(f"Could not set {key} with {value} in General Information.")
                return False

        mws.select_tab("Tender Restrictions")
        if not mws.config_flexgrid("Tender Restrictions List", tender_restr, DEPT_FG_OFFSET):
            return False

        mws.click_toolbar("Save")
        if mws.get_top_bar_text() == f"Department {config['Department Number']} already exists, overwrite?":
            if overwrite:
                mws.click_toolbar("Yes")
            else:
                self.log.error(f"Department {config['Department Number']} already exists. Set overwrite to True to overwrite it.")
                mws.click_toolbar("No")
                return False
        if not mws.set_value("Departments", [config['Department Number'], config['Department Name']]):
            self.log.error(f"Department {config['Department Number']} {config['Department Name']} wasn't found in the list after saving.")
            return False
        return True

    def change(self, num, config, tender_restr={}):
        """
        Change an existing department.
        Args:
            num: (int/str) The number of the department to change.
            config: (dict) All of the controls to set in the General Information tab.
                    This will need to be setup according to the schema in controls.json.
            tender_restr: (dict) Tender types to enable or disable restriction for.
        Returns:
            bool: True if successful, False if not.
        Example:
            >>> cfg = {"Food Stampable": False, "Network Product Code": "500"}
            >>> restr = {"houseCharges": False, "foodStamps": True}
            >>> department.DepartmentMaintenance().change(17, cfg, restr)
            True
        """
        if not mws.set_value("Departments", str(num).rjust(10)):
            self.log.error(f"Department {num} wasn't found in the list.")
            return False
        mws.click_toolbar("Change")

        for key, value in config.items():
            if not mws.set_value(key, value):
                self.log.error(f"Could not set {key} with {value} in General Information.")
                return False

        mws.select_tab("Tender Restrictions")
        if not mws.config_flexgrid("Tender Restrictions List", tender_restr, DEPT_FG_OFFSET):
            return False

        mws.click_toolbar("Save")
        msg = mws.get_top_bar_text()
        if msg:
            self.log.error(f"Got an unexpected message when saving department {num}: {msg}")
            return False
        return True

    def delete(self, num, reassign_num=None):
        """
        Delete an existing department. Note that it will still remain in the database, just deactivated.
        Args:
            num: (int/str) The number of the department to delete.
            reassign_num: (int/str) The number of the department to reassign the deleted department's PLUs to, if any.
                          Leave default to delete them.
        Returns:
            bool: True if successful, False if not.
        Example:
            >>> department.DepartmentMaintenance().delete(17, 16)
            True
        """
        # Delete department
        if not mws.set_value("Departments", str(num).rjust(10)):
            self.log.error(f"Department {num} {name} wasn't found in the list.")
            return False
        mws.click_toolbar("Delete")
        if "Department will be deleted" not in mws.get_top_bar_text():
            self.log.error(f"Didn't get confirmation prompt when deleting Department {num}.")
            return False
        mws.click_toolbar("Yes")

        # Handle PLU reassignment
        if mws.get_control("Assign PLUs to Department.") is not None:
            if reassign_num is not None:
                for dept in mws.get_value("Assign PLUs to Department."):
                    if dept.startswith(f" {reassign_num}"):
                        mws.set_value("Assign PLUs to Department.", dept)
                        break
                else:
                    self.log.error(f"Couldn't find department {reassign_num} to reassign PLUs to.")
                    return False
                mws.click_toolbar("Reassign PLUs")
                mws.click_toolbar("Yes")
            else:
                self.log.debug("No reassignment dept specified. Deleting PLUs instead.")
                mws.click_toolbar("Delete")
                mws.click_toolbar("Yes")

        # Verify department deleted
        if mws.set_value("Departments", str(num).rjust(10)):
            self.log.error(f"Department {num} {name} was found in the list after deletion.")
            return False
        return True