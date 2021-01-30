
from app.features.network.core.pdl import ParameterDownload as CoreParameterDownload

class ParameterDownload(CoreParameterDownload):
    """
    The class extends Core PDL class.
    This class is specific to Exxon brand.
    """

    def __init__(self):
        super().__init__()

        # This dictionary will specify brand-specific top bar messages, 
        # as well as what toolbar button to click when they are displayed. 
        # A boolean input indicates a termination point (and what value to return) for the program.
        self.TOP_BAR_MSG_SEQUENCE = {
		    "Loading PDL Download. Please wait..." : None,
            "Do you want to continue with Parameter Download?" : "YES",
			"Processing Parameter Download" : None,
            "Download succeeded. Card Table Load successful" : ["Exit", True],
            "Download failed - No connection" : ["Exit", False]
        }