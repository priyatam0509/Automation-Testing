from app.framework import mws, Navi
import logging

class SiteOptions:

    def __init__(self):
        SiteOptions.navigate_to()
        self.log = logging.getLogger()

    @staticmethod
    def navigate_to():
        return Navi.navigate_to("Site Options")

    def setup(self, config):
        """
        Sets up fuel site options.

        Args:
            config: A dictionary of control:value pairs.

        Returns:
            True: If fuel site options was successfully set up.
            False: If something went wrong while setting up fuel site options.
        """
        self.log.info("Setting up Fuel Site Options")
        for tab in config:
            self.log.info("Setting up the {tab} tab.")
            mws.select_tab(tab)
            for key, value in config[tab].items():
                if not mws.set_value(key, value, tab):
                    self.log.error(f"Could not set {key} to {value} on the {tab} tab.")
                    return False
        return True