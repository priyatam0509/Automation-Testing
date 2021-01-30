from app import Navi, mws
import time

from app.features.network.core.host_function import HostFunction as CoreHF

class HostFunction(CoreHF):
    """
    The class extends general HostFunction class.
    This class is specific to Dallas brand.
    """
    def __init__(self):
        super().__init__()

        # This dictionary will specify brand-specific top bar messages, 
        # as well as what toolbar button to click when they are displayed. 
        # A boolean input indicates a termination point (and what value to return) for the program.
        self.TOP_BAR_MSG_SEQUENCE = {
            "Do you want to continue with Host Function?" : "Yes",
            "Processing Host Function" : None,
            "Connected to host":["Exit",True],
            "Not connected to host" : ["Exit", False]
        }


    @staticmethod
    def navigate_to():
        """
        Navigates to the Comms Test menu.
        Args:
            None
        Returns:
            Returns the result of execution of Navi.navigate_to()
        """
        return Navi.navigate_to("Comm Test")