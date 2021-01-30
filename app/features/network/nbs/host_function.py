import logging

from app.features.network.core.host_function import HostFunction as CoreHostFunction

class HostFunction(CoreHostFunction):
    """
    The class extends general HostFunction class.
    This class is specific to NBS brand.

    The Host Function (Comm Test) menu is unsupported on NBS,
    so the the class overwrites them to return warning message
    and return False.
    """
    def __init__(self):
        self.log = logging.getLogger()
        self.log.error("Host Function (Comm Test) module is not available on NBS.")

    @staticmethod
    def navigate_to():
        pass

    def communications_test(self, top_bar_msg_sequence = None, timeout = 60):
        self.log.warning("NBS does not support Host Function (Comm Test). Configuration is not available.")
        return False