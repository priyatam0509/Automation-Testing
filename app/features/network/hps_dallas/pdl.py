import logging

from app.features.network.core.pdl import ParameterDownload as CoreParameterDownload

class ParameterDownload(CoreParameterDownload):
    """
    The class extends core PDL class.
    This class is specific to HPS Dallas brand.

    The  PDL menu is unsupported on HPS Dallas,
    so the the class overwrites them to return warning message
    and return False.
    """

    def __init__(self):
        self.log = logging.getLogger()
        self.log.warning("PDL is not available on HPS Dallas")

    @staticmethod
    def navigate_to():
        pass
        
    def request(self, top_bar_msg_sequence = None, timeout = 60):
        return True
	

    