from app.features.network.core.pdl import ParameterDownload as CoreParameterDownload

class ParameterDownload(CoreParameterDownload):
    """
    The class extends the Core PDL class.
    This class is specific to Marathon brand.
    """
    
    def __init__(self):
        super().__init__()

        # This dictionary will specify brand-specific top bar messages, 
        # as well as what toolbar button to click when they are displayed. 
        # A boolean input indicates a termination point (and what value to return) for the program.
        self.TOP_BAR_MSG_SEQUENCE = {
            "Do you want to continue with Parameter Download?" : "YES",
            "Processing Parameter Download" : None,
			"PDL REQUESTED SUCCESSFULLY - SEE NETWORK STATUS" : ["Exit", True], # returns True upon success
            "PDL Failed. Download Connection Info Has Not Been Configured on the MWS" : ["Exit", False]
        }