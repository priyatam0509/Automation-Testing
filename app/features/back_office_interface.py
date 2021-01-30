import logging
from app import mws, Navi, system

class BackOfficeInterface():
    FG_STORE_OFFSET = 425
    FG_SHIFT_OFFSET = 525
    FG_INSTANCES = { "Fuel Grade Movement": 5,
                     "Item Sales Movement": 2,
                     "Merchandise Code Movement": 2,
                     "Miscellaneous Summary Movement": 2,
                     "Tax Level Movement": 2 }

    def __init__(self):
        self.log = logging.getLogger()
        BackOfficeInterface.navigate_to()

    @staticmethod
    def navigate_to():
        return Navi.navigate_to("Back Office Interface")

    def configure(self, format, config={}):
        """
        Configure Back Office Interface settings.
        Args:
            format: (str) The Interface format to select.
            config: (dict) A map of controls to set and the values to set them to. See controls.json for mappings.
                    Documents tab must be formatted differently, see the example.
        Returns:
            bool: Success/failure
        Example:
            >>> cfg = { 
                "Generation Options": { "Generate Transaction Level Detail": True, "Generate Acknowledgement Files": True,
                    "Combine Transaction Level Detail Files": True },
                "Import Options": { "Alert cashier at POS when pricebook import is complete": True,"milliseconds": "200" },
                "Documents": {
                    "Document list": {
                            "Fuel Grade Movement by Till": [True, False] # Check Store Close, uncheck Shift Close for this row
                            "Fuel Grade Movement": [True, True],
                            "Item Sales Movement": [True, False],
                            "Tax Level Movement": [False, True],
                            "Fuel Product Movement": [False, False]
                        }
                    }
                }
            >>> BackOfficeInterface().configure("NACS XML v3.4", cfg)
            True
        """
        config = config.copy() # Make a copy of the dict so we don't alter the original
        if not mws.set_value("Interface format", format):
            self.log.warning(f"Failed to set Back Office Interface format to {format}. Aborting configuration.")
            return False

        # Configure Documents tab
        if "Documents" in config and "Document list" in config["Documents"]:
            mws.select_tab("Documents")
            if not mws.config_flexgrid("Document list", config["Documents"]["Document list"], [BackOfficeInterface.FG_STORE_OFFSET, BackOfficeInterface.FG_SHIFT_OFFSET], BackOfficeInterface.FG_INSTANCES):
                return False
        del config["Documents"]["Document list"]

        # Configure remaining tabs
        for tab in config:
            mws.select_tab(tab)
            for key, value in config[tab].items():
                if not mws.set_value(key, value, tab):
                    self.log.error(f"Could not set {key} with {value} on the {tab} tab.")
                    return False

        mws.click_toolbar("Save")
        msg = mws.get_top_bar_text()
        if msg and "Combine will take effect" in mws.get_top_bar_text():
            mws.click_toolbar("OK")
        elif msg:
            self.log.error(f"Got an unexpected message when saving Back Office Interface: {msg}")
            mws.recover()
            return False
        return True