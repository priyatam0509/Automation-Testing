from app import mws
from app import Navi, system
import logging, time

class ReminderMaintenance:
    def __init__(self):
        self.log = logging.getLogger()
        ReminderMaintenance.navigate_to()

    @staticmethod
    def navigate_to():
        """
        Navigates to the Reminder Maintenance homepage.
        Args: None
        Returns: Returns the result of execution of Navi.navigate_to()
        """
        return Navi.navigate_to("reminder maintenance")
        
    def configure(self, config, select= "new_reminder"):
        """
        Description: Configures an existing reminder or adds a new one.
        Args:
            config: A dictionary of controls so the user can add the information that
                    they need to. This is according to the schema in controls.json.
                    If a control is already set, it will be replaced by its new value in config.
                    "months" and "Days" controls can be (str), (list), or "all" to select all.
            select: A string specifying the name of the reminder to select in the list of 
                    reminders. If found, it will change the existing; if not, it will add 
                    a new reminder.
        Returns:
            bool: Success/Failure
        Example:
            reminder_info = {
                "Properties": {
                    "Task": "Test Task",
                    "Message": "Test Message",
                    "Manager Work Station": True,
                    "POS": True,
                    "Enabled": True
                },
                "Schedule": {
                    "Frequency": "Monthly",
                    "Start Date": "6/18/2020"
                    "Start Time": "02:10 PM",
                    # "every": "1"
                    # "Days": "all",
                    # "Day": True,
                    "The": True,
                    # "of the months": "1",
                    "Occurence": "second",
                    "Day of the week": "Thursday",
                    "months": ["January", "March", "December"]
                }
            }
            rm = reminder_maint.ReminderMaintenance()
            rm.configure(reminder_info, "existing_reminder")
            True
        """
        # Check if the specified reminder exists
        if mws.set_value("Reminders", select):
            self.log.debug(f"{select} already exists, clicking Change...")
            mws.click_toolbar("Change")
        else:
            self.log.debug(f"Adding {select}...")
            mws.click_toolbar("Add")
        
        # Begin setting controls
        for tab in config:
            mws.select_tab(tab)
            for key, value in config[tab].items():
                if key == "months" or key == "Days":
                    # Months and Days checkbox controls can be strings, lists, or "all" to select all.
                    if type(value) == list:
                        for date in value:
                            if not mws.set_value(key, date):
                                self.log.error(f"Could not set '{key}' control to '{date}'.")
                                return False
                    # Allow settng all
                    elif value.lower() == "all":
                        for date in mws.get_value(key):
                            if not mws.set_value(key, date):
                                self.log.error(f"Could not set '{key}' control to '{date}'.")
                                return False
                    # Set individual month
                    else:
                        if not mws.set_value(key,value):
                            self.log.error(f"Could not set '{key}' control to '{date}'.")
                            return False
                # Start Time control does not allow AM/PM changing, removing failing out for now
                elif key == "Start Time" or key == "Task":
                    if not mws.set_value(key, value):
                        continue
                # Set miscellaneous controls
                elif not mws.set_value(key,value):
                    self.log.error(f"Could not set '{key}' control to '{value}' in '{tab}' tab.")
                    system.takescreenshot()
                    return False
        mws.click_toolbar("Save")
        starttime = time.time()
        while starttime - time.time() < 1:
            try:
                errormessage = mws.get_top_bar_text().lower()
                if "errors" in errormessage:
                    self.log.warning(errormessage)
                    self.log.error("Some part of your configuration is wrong. Exiting without saving...")
                    mws.click_toolbar("Cancel")
                    mws.click_toolbar("No")
                    return False
            except:
                continue
        return True

    def delete(self, select):
        """
        Description: Deletes an existing reminder.
        Args:
            select: A string specifying the name of the reminder to delete in the list of 
                    reminders.
        Returns:
            bool: Success/Failure
        Example:
            rm = reminder_maint.ReminderMaintenance()
            rm.delete("Test Reminder")
            True
        """
        # Find reminder in list
        if not mws.set_value("Reminders", select):
            self.log.error(f"Could not find {select} in list of reminders.")
            return False
        # Click delete
        mws.click_toolbar("Delete")
        mws.click_toolbar("Yes")
        # Verify successful deletion
        if mws.set_value("Reminders", select):
            self.log.error(f"{select} still in list, deletion unsuccessful...")
            return False
        else:
            self.log.debug("Deletion successful.")
            return True
