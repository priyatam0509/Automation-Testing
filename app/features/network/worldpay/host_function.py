from app import Navi
from app.features.network.core.host_function import HostFunction as CoreHostFunction

class HostFunction(CoreHostFunction):
    """
    The class extends general Hostfunction class.
    This class is specific to Worldpay brand.
    """

    def __init__(self):
        super().__init__(self)

        self.TOP_BAR_MSG_SEQUENCE = {
            "Loading Comm Test" : None,
            "Do you want to continue with Host Function?" : "YES",
            "Processing Host Function" : None,
            "SUCCESFULL X-MIT" : ["Exit", True], # this is not a typo
            "Test message failed - No connection" : ["Exit", False]
        }

    @staticmethod
    def navigate_to():
        return Navi.navigate_to("Comm Test")