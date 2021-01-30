import logging

from app.features.network.core.pdl import ParameterDownload as CoreParameterDownload

class ParameterDownload(CoreParameterDownload):
    """
    The class extends the core PDL class.
    This class is specific to Worldpay brand.

    We do not support PDL for WorldPay.
    """
    def __init__(self):
        self.log = logging.getLogger()
        self.log.error("PDL is not available on Worldpay")

    @staticmethod
    def navigate_to():
        pass

    def request(self, top_bar_msg_sequence = None, timeout = 120):
        self.log.warning("Worldpay does not support PDL. Configuration is not available.")
        return False