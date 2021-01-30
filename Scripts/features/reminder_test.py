"""
    File name: reminder_test.py
    Tags:
    Description: 
    Author: 
    Date created: 2019-06-18 14:30:34
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import mws, system, reminder_maint
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class reminder_test():
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

        self.rm = reminder_maint.ReminderMaintenance()

    @test
    def add_reminder(self):
        """Tests whether a new reminder can be added.
        Args: None
        Returns: None
        """
        reminder_info = {
            "Properties": {
                "Task": "Test Reminder",
                "Message": "Test Message",
                "Manager Work Station": False,
                "POS": True,
                "Enabled": True
            },
            "Schedule": {
                "Frequency": "Weekly",
                "Start Date": "6/18/2020",
                "Start Time": "11:10 AM",
                "every": "1",
                "Days": ["Monday","Wednesday"],
                #"Day": True,
                # "The": True,
                #"of the months": "1",
                # "Occurence": "second",
                # "Day of the week": "Thursday",
                # "months": "All"
            }
        }
        if not self.rm.configure(reminder_info):
            tc_fail("Failed during adding.")

    @test
    def change_reminder(self):
        """Tests whether an existing reminder can be changed.
        Args: None
        Returns: None
        """
        reminder_info_edit = {
            "Properties": {
                "Task": "Test Reminder (Edit)",
                "Message": "Test Message (Edit)",
                "Manager Work Station": True,
                "POS": False,
                "Enabled": False
            },
            "Schedule": {
                "Frequency": "Monthly",
                "Start Date": "6/30/2020",
                "Start Time": "02:50 PM",
                # "every": "1",
                # "Days": ["Monday","Wednesday"],
                # "Day": True,
                "The": True,
                # "of the months": "1",
                "Occurence": "third",
                "Day of the week": "Friday",
                "months": "All"
            }
        }
        # If stuck in previous menu, navigate out.
        if mws.click_toolbar("Cancel"):
            mws.click_toolbar("No")

        if not self.rm.configure(reminder_info_edit, select= "Test Reminder"):
            tc_fail("Failed during changing.")

    @test
    def delete_reminder(self):
        """Tests whether an existing reminder can be deleted.
        Args: None
        Returns: None
        """
        # If stuck in previous menu, navigate out.
        if mws.click_toolbar("Cancel"):
            mws.click_toolbar("No")

        if not self.rm.delete("Test Reminder (Edit)"):
            tc_fail("Failed during deletion.")


    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        # delete pass after you implement.
        pass