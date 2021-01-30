from app.framework import Navi, mws
from app.util import system
import logging, time, pywinauto, copy, re

class RecoveryConfiguration:
    """
    The class representing the Recovery Configuration
    window in Set Up -> Store section of MWS.


    The modules has a setup method that allows
    to configure various fields in the System Recovery
    Configuration based on the user dictionary.
    """

    # The fields that should have the checkbox enabled before they can be
    # edited
    FORCE_CHECK_FIELDS = {
        "Delete Archived Backup Sets older than" : "Archive Backup Sets",
        "Mirror time": "\"Mirror\" copies of the current server backup and image once each day at",
        "Machine used to mirror server backup files": "\"Mirror\" copies of the current server backup and image once each day at",
        "Machine used to mirror server image files": "\"Mirror\" copies of the current server backup and image once each day at"
    }

    def __init__(self):
        """
        Set up mws connection.
        """
        self.log = logging.getLogger()
        RecoveryConfiguration.navigate_to()
        return


    @staticmethod
    def navigate_to():
        """
        Navigates to the Recovery Configuration menu.
        Args:
            None
        Returns:
            Returns the result of execution of Navi.navigate_to()
        """
        return Navi.navigate_to("Recovery Configuration")


    def setup(self, params):
        """
        Configures the fields accessible in the
        Recovery Configuration window according to the provided
        dictionary.
    
        Args:
        params: the dictionary with the information about
            fields that need to be configured.
            This will need to be setup according to the schema in controls.json.
    
        Returns:
            True: If Recovery Configuration was successfully set up.
            False: If something went wrong while setting up Recovery Configuration (will be logged).
    
        Example:
            params = {
                "Start time": "3:00 AM",
                "Sunday": True,
                "Monday": True,
                "Tuesday": True,
                "Wednesday": True,
                "Thursday": True,
                "Friday": True,
                "Saturday": True,
                "Run Differential Backups on all other days": True,
                "Archive Backup Sets": True,
                "Delete Archived Backup Sets older than": "2",
                "Run a transaction log backup once every": "10",
                "\"Mirror\" copies of the current server backup and image once each day at": True,
                "Mirror time": "12:00 AM",
                "Machine used to mirror server backup files": "", # No machines were present in the dropdown
                "Machine used to mirror server image files": ""
            }
        """
        params = copy.deepcopy(params)
        error = False

        for key, value in params.items():
            # Example:
            #    key = "Start time"
            #    value = "3:00 AM"

            # Check whether the option is dependent on other option
            if key in self.FORCE_CHECK_FIELDS:
                if not self._set_dependent_fields(key, params):
                    error = True
                    continue
            else:
                if not mws.set_value(key, value):
                    self.log.error(f"Could not set {key} with {value}.")
                    error = True
        try:
            mws.click_toolbar("Save", main=True, main_wait=3)
        except mws.ConnException:

            # Check for top bar message
            top_bar_message = mws.get_top_bar_text()
            if top_bar_message:
                if top_bar_message == "Do you want to save changes?":
                    mws.click_toolbar("YES")
                    time.sleep(1)
                    mws.click_toolbar("OK")
                else:
                    self.log.error("Unable to save System Recovery Configuration")
                    self.log.error(f"Unexpected top bar message is '{top_bar_message}'")
                    system.takescreenshot()
                    mws.click_toolbar("OK")
                    error = True
        
        # Check for errors
        if error:
            self.log.error("There were errors in the process of configuring System Recovery Configuration")
            return False
        
        return True
    
    def _set_dependent_fields(self, depend_name, params):
        """
        Sets the fields which availability depends on some master field.
        Logs errors if they occur.
        Args:
            depend_names: (string) the name of field to set
            params: (dictionary) a dictionary of the config delegated from other setup funcs that
                    should contain the dependent and master fields' values if needed
        Returns:
            True: if operation is a success
            False: if there are errors in the process
        """
        master_name = self.FORCE_CHECK_FIELDS[depend_name]
        # Error flag
        error = False

        # Check if the "master" field is present
        if master_name in list(params.keys()):
            # Apply the config
            if not mws.set_value(master_name, params[master_name]):
                self.log.error(f"Could not set {master_name} with {params[master_name]}.")
                system.takescreenshot()
                error = True
        else:
            # Check if it is enabled
            if not mws.get_value(master_name):
                # Dependent field cannot be set
                error = True

        if error:
            self.log.error(f"Could not set {depend_name} with {params[depend_name]}.")
            return False
        
        if not mws.set_value(depend_name, params[depend_name]):
            self.log.error(f"Could not set {depend_name} with {params[depend_name]}.")
            system.takescreenshot()
            return False

        return True