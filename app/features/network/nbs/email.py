import logging

from app.features.network.core.email import Email as CoreEmail

class Email(CoreEmail):
    """
    The class extends core Email class.
    This class is specific to NBS brand.

    The Email menu is unsupported on NBS,
    so the the class overwrites them to return warning message
    and return False.
    """
    def __init__(self):
        self.log = logging.getLogger()
        self.log.error("Email module is not available on NBS.")

    @staticmethod
    def navigate_to():
        pass

    def print(self, Today = True):
        self.log.error("Email module is not available on NBS. Configuration is not available.")
        return False