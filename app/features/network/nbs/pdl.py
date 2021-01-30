from app import mws, system, Navi
import time

from app.features.network.core.pdl import ParameterDownload as CoreParameterDownload

class EMVPDLDownload(CoreParameterDownload):
    """
    The class extends the core Parameter Download class.
    This class is specific to NBS brand.

    The class represents the EMV PDL Download
    menu for NBS class.
    """
    def __init__(self):
        super().__init__()

        # This dictionary will specify brand-specific top bar messages, 
        # as well as what toolbar button to click when they are displayed. 
        # A boolean input indicates a termination point (and what value to return) for the program.
        self.TOP_BAR_MSG_SEQUENCE = {
            "Do you want to continue with EMV Configuration Download?" : "YES",
            "Processing Host Function" : None,
            "Requesting EMV configuration. Please see network journal for results." : ["Exit", True], # returns True upon success
        }

    @staticmethod
    def navigate_to():
        """
        Navigates to EMV PDL Download.
        Args: None
        Returns: Returns the result of execution of Navi.navigate_to()
        """
        return Navi.navigate_to("emv pdl download")
    
class ParameterDownload(CoreParameterDownload):
    """
    The class extends the core Parameter Download class.
    This class is specific to NBS brand.

    The class represents the Card Configuration Download
    menu for NBS class.
    """
    def __init__(self):
        super().__init__()

        # This dictionary will specify brand-specific top bar messages, 
        # as well as what toolbar button to click when they are displayed. 
        # A boolean input indicates a termination point (and what value to return) for the program.
        self.TOP_BAR_MSG_SEQUENCE = {
            "Do you want to continue with Parameter Download?" : "YES",
            "Processing Parameter Download" : None,
            "Requesting Card Configuration Table. Please see the network journal for results" : ["Exit", True], # returns True upon success
        }

    @staticmethod
    def navigate_to():
        """
        Navigates to EMV PDL Download.
        Args: None
        Returns: Returns the result of execution of Navi.navigate_to()
        """
        return Navi.navigate_to("Card Configuration Download")