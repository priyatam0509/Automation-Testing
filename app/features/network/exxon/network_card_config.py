import logging

from app.features.network.core.network_card_config import NetworkCardConfiguration as CoreNCC

class NetworkCardConfiguration(CoreNCC):
    """
    The class extends core INetworkCardConfiguration class.
    This class is specific to Exxon brand.
    
    The Network Card Configuration menu is unsupported on Exxon,
    so the the class overwrites them to return warning message
    and return False.
    """
    def __init__(self):
        self.log = logging.getLogger()
        self.log.error("Network Card Configuration is not available on Exxon")

    @staticmethod
    def navigate_to():
        pass

    def change(self, config):
        self.log.warning("Exxon does not support Network Card Configuration. Configuration is not available.")
        return False