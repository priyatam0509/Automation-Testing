from app import mws, system, Navi
import time

from app.features.network.core.pdl import ParameterDownload as CoreParameterDownload

class ParameterDownload(CoreParameterDownload):
    def __init__(self):
        super().__init__()
        self.TOP_BAR_MSG_SEQUENCE = {
            "Do you want to continue with Parameter Download?" : "Yes",
            "Processing Parameter Download" : None,
            "Request Timeout Failure" : ["Exit", False],
            "Parameter Table Request Successful" : ["Exit", True],
            "Cannot get Parameter Table Download now." : ["Exit", False],
            "Parameter Table Request already in progress" : ["Exit", False]
        }

    @staticmethod
    def navigate_to():
        """
        Navigates to the Parameter Download module.
        """
        return Navi.navigate_to("parameter download")


class EMVAIDPKDownload(CoreParameterDownload):
    def __init__(self):
        super().__init__()
        self.TOP_BAR_MSG_SEQUENCE = {
            "Loading EMV AIDPK Download" : None,
            "Request EMV AIDPK Download?" : "Yes",
            "Processing Host Function" : None,
            "Download failed" : ["Exit", False],
            "EMV AIDPK Download Request successful" : ["Exit", True],
            "Cannot get EMV AIDPK download now" : ["Exit", False]
        }

    @staticmethod
    def navigate_to():
        """
        Navigates to the EMV AIDPK Download module.
        """
        return Navi.navigate_to("emv aidpk download")
