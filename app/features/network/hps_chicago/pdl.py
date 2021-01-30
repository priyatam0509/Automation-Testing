from app import Navi

from app.features.network.core.pdl import ParameterDownload as CoreParameterDownload

class ParameterDownload(CoreParameterDownload):
    """
    This class extends core PDL class.
    It is specific to HPS Chicago brand.

    The class is to be extended by the actual brand specific
    class that implements its functions.
    """
    
    def __init__(self):
        super().__init__()

        # This dictionary will specify brand-specific top bar messages, 
        # as well as what toolbar button to click when they are displayed. 
        # A boolean input indicates a termination point (and what value to return) for the program.
        self.TOP_BAR_MSG_SEQUENCE = {"EMV PDL Download": "YES",
                                     "Processing Host Function": None,
                                     "Requesting EMV configuration. Please see network journal for results.": ["Exit", True]}

    @staticmethod
    def navigate_to():
        """
        Navigates to PDL.
        Args: None
        Returns: Returns the result of execution of Navi.navigate_to()
        """
        return Navi.navigate_to("EMV PDL Download")