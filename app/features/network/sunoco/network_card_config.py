import logging

from app.features.network.core.network_card_config import NetworkCardConfiguration as CoreNCC

class NetworkCardConfiguration(CoreNCC):
    """
    The class extends core NetworkCardConfiguration class.
    This class is specific to Sunoco brand.

    The Network Card Configuration menu is unsupported on Sunoco,
    so the the class overwrites them to return warning message
    and return False.
    """
    def __init__(self):
        self.log = logging.getLogger()
        self.log.error("Network Card Configuration is not available on Sunoco")

    @staticmethod
    def navigate_to():
        pass

    def change(self, config):
        self.log.warning("Sunoco does not support Network Card Configuration. Configuration is not available.")
        return False