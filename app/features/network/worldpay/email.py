import logging

from app.features.network.core.email import Email as CoreEmail

class Email(CoreEmail):
    """
    The class extends core Email class.
    This class is specific to Worldpay brand.

    The Email menu is unsupported on Worldpay,
    so the the class overwrites them to return warning message
    and return False.
    """
    def __init__(self):
        self.log = logging.getLogger()
        self.log.error("Email is not available on Worldpay")

    @staticmethod
    def navigate_to():
        pass

    def request(self, today = True, prnt = False):
        self.log.warning("Worldpay does not support Email. Configuration is not available.")
        return False