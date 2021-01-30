"""
    File name: dept_test.py
    Tags:
    Description: 
    Author: 
    Date created: 2019-05-28 13:15:45
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import Navi, mws, pos, system
from app.features import department, item
from app.framework.tc_helpers import setup, test, teardown, tc_fail

dept_cfg = { "Department Number": "77",
             "Department Name": "SQA Automation",
             "Discountable": True,
             "Food Stampable": True,
             "Network Product Code": "404" }
new_name = "SQA Automation2"
dept_restr = { "moneyOrder": True,
               "driveOff": True,
               "pumpForTest": True,
               "cashAcceptorChange": True }
item_cfg = { "General": {
               "PLU/UPC": "18726",
               "Description": "DeptReassignTestItem",
               "Department": new_name,
               "Price Required": True }
           }
reassign_num = 16
reassign_name = "Dept 16"

class dept_test():
    """
    Description: Test class that provides an interface for testing.
    """

    def __init__(self):
        """Initializes the Template class.
        Args: None
        Returns: None
        """
        # The logging object. 
        # Example: self.log.info(f"Current value of var: {my_var}")
        self.log = logging.getLogger()

    @setup
    def setup(self):
        """Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        if not system.restore_snapshot():
            raise Exception       
        pass

    @test
    def add(self):
        """Verify we can add a new department using the DepartmentMaintenance class.
        Args: None
        Returns: None
        """
        # Configure
        Navi.navigate_to("Department Maintenance")
        if not department.DepartmentMaintenance().add(dept_cfg, dept_restr, overwrite=True):
            tc_fail("Adding department failed.")

        # Verify general information
        mws.click_toolbar("Change")
        for field, value in dept_cfg.items():
            actual = mws.get_value(field)
            if actual != value:
                mws.click_toolbar("Cancel")
                tc_fail(f"{actual} in {field} field did not match expected value of {value}.")

        # Verify tender restrictions
        mws.select_tab("Tender Restrictions")
        if not self.verify_restrs(dept_restr):
            mws.click_toolbar("Cancel")
            tc_fail("Failed to verify restrictions saved properly.")

        mws.click_toolbar("Cancel")

    @test
    def change(self):
        """Verify we can change an existing department using the DepartmentMaintenance class."""
        # Fields to be changed
        dept_change = dept_cfg.copy()
        del dept_change["Department Number"] # Can't change dept number
        dept_change["Department Name"] = new_name
        dept_change["Discountable"] = False
        dept_change.update({"May appear as POS Coupon key": True})
        dept_restr["cashAcceptorChange"] = False
        dept_restr.update({"ebt": True})

        # Configure
        Navi.navigate_to("Department Maintenance")
        if not department.DepartmentMaintenance().change(dept_cfg["Department Number"], dept_change, dept_restr):
            tc_fail("Changing department failed.")

        # Verify general information
        mws.click_toolbar("Change")
        for field, value in dept_change.items():
            actual = mws.get_value(field)
            if actual != value:
                tc_fail(f"{actual} in {field} field did not match expected value of {value}.")

        # Verify tender restrictions
        mws.select_tab("Tender Restrictions")
        if not self.verify_restrs(dept_restr):
            tc_fail("Failed to verify department contents.")

    @test
    def delete(self):
        """Verify we can delete an existing department and reassign its PLUs using the Department Maintenance class."""
        # Add an item to the department so we can reassign PLU
        Navi.navigate_to("Item")
        if not item.Item().add(item_cfg):
            tc_fail("Failed to add test item.")

        # Delete
        Navi.navigate_to("Department Maintenance")
        if not department.DepartmentMaintenance().delete(dept_cfg["Department Number"], reassign_num):
            tc_fail("Deleting department failed.")

        # Verify PLU reassignment
        Navi.navigate_to("Item")
        mws.set_value("PLU/UPC", item_cfg["General"]["PLU/UPC"])
        mws.click_toolbar("Search")
        mws.click_toolbar("Change")
        if mws.get_value("Department", tab="General")[0] != reassign_name:
            tc_fail(f"Test item was not reassigned to {reassign_name}.")

        mws.click_toolbar("Cancel")
        mws.click_toolbar("No")
        mws.click_toolbar("Exit")

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        # delete pass after you implement.
        pass

    def verify_restrs(self, restr):
        # We don't have means to interact directly with FlexGrid. Use OCR instead.
        log_level = self.log.getEffectiveLevel()
        self.log.setLevel(999)
        for tender, setting in restr.items():
            x_coords = mws.search_click_ocr(tender, offset=(270, 0), click_loc=mws.OCR.LEFT, clicks=0,
                                            max_dist=2 if tender == 'lotteryWinningTicket' else 1) # Special case for OCR not reading this correctly
            if x_coords is None: # Scroll down and try again
                mws.get_control("Tender Restrictions List").scroll("down", "end")
                x_coords = mws.search_click_ocr(tender, offset=(270, 0), click_loc=mws.OCR.LEFT, clicks=0,
                                            max_dist=2 if tender == 'lotteryWinningTicket' else 1) # Special case for OCR not reading this correctly
                if x_coords is None:
                    self.log.setLevel(log_level)
                    self.log.warning(f"Couldn't find {tender} in the list of tenders.")
                    return False
            x_bbox = (x_coords[0], x_coords[1]-10, x_coords[0]+20, x_coords[1]+7)
            if mws.find_text_ocr('X', bbox=x_bbox):
                if not setting:
                    self.log.setLevel(log_level)
                    self.log.warning(f"{tender} restriction was enabled when it should have been disabled.")
                    return False
            elif setting:
                self.log.setLevel(log_level)
                self.log.warning(f"{tender} restriction was disabled when it should have been enabled.")
                return False
            mws.get_control("Tender Restrictions List").scroll("up", "end")
        self.log.setLevel(log_level)
        return True