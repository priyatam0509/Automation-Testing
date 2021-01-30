from app import mws
from app import Navi, system
import logging, time, copy

class ReportMaintenance:
    def __init__(self):
        self.log = logging.getLogger()
        self.order = ['Generate PDF files','Generate PDF with password','Copy reports to alternate destination']
        ReportMaintenance.navigate_to()

    @staticmethod
    def navigate_to():
        """
        Navigates to the Report Maintenance feature module.
        Args: None
        Returns: Returns the result of execution of Navi.navigate_to()
        """
        return Navi.navigate_to("report maintenance")

    def configure(self, config):
        """
        Configures the Report Maintenance tabs.
        Args:
            config: A dictionary of controls so the user can add the information that
                      they need to. This is according to the schema in controls.json.
        Returns:
            bool: True/False success condition
        Examples:
            \code
            rm_info = {
                "Configuration":{
                    "Generate PDF files": True,
                    "Generate PDF with password": True,
                    "Generate PDF with password edit": "password",
                    "Print the report": True,
                    "Copy reports to local XML Gateway Back Office share": False,
                    "Copy reports to local PPXMLData share": True,
                    "Copy reports to Insite360": False,
                    "Copy reports to alternate destination": False
                },
                "FTP Options":{
                    "Copy the Reports to FTP location": True,
                    "Host Description": "Test Description",
                    "Host Address": "Test Address",
                    "Host Port": "7777",
                    "User Name": "Test Username",
                    "Password": "password",
                    "FTP Folder": "Test Folder",
                    "Use Secure FTP": True
                }
            }
            rm.configure(rm_info)
            True
            \endcode
        """
        # Copies config so original dictionary is not edited by order handling below
        config = copy.deepcopy(config)

        # Takes care of order-sensitive controls on Configuration tab
        for field in self.order:
            try:
                value = config["Configuration"][field]
            except KeyError:
                continue
            if not mws.set_value(field, value):
                self.log.error(f"Could not set '{field}' control to '{value}'.")
                return False
            del config["Configuration"][field]

        # Sets remaining controls
        for tab in config:
            mws.select_tab(tab)
            for key, value in config[tab].items():
                if not mws.set_value(key, value, tab):
                    self.log.error(f"Could not set '{key}' control to '{value}' in {tab} tab.")
                    return False
                # Setting checkboxes after calling select_tab() sometimes doesn't work the first time
                if mws.get_value(key) != value:
                    self.log.debug(f"Setting '{key}' to '{value}' didn't work, retrying...")
                    if not mws.set_value(key, value, tab):
                        self.log.error(f"Could not set '{key}' control to '{value}' in {tab} tab.")
                        return False
        mws.click_toolbar("Save")

        # Check for error codes
        starttime = time.time()
        while time.time() - starttime < 1:
            errorcode = str(mws.get_top_bar_text()) # str() prevents 'Nonetype not iterable' errors if on MWS
            if "is not valid" in errorcode or "errors" in errorcode:
                self.log.error(errorcode)
                self.log.error("Some part of your configuration is incorrect. Failing...")
                system.takescreenshot()
                # Catch unfilled field errors
                try:
                    mws.click_toolbar("OK")
                except mws.ConnException:
                    pass
                # Navigate back to MWS
                mws.click_toolbar("Cancel")
                mws.click_toolbar("No")
                return False
        return True