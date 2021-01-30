from app import mws, system, Navi
import time, logging

class ParameterDownload:
    """
    Core Parameter Download feature class. Supports Concord network. To be extended and overridden for other networks
    where needed.
    """
    
    def __init__(self):
        self.log = logging.getLogger()
        self.navigate_to()

        # This dictionary will specify brand-specific top bar messages, 
        # as well as what toolbar button to click when they are displayed. 
        # A boolean input indicates a termination point (and what value to return) for the program.
        self.TOP_BAR_MSG_SEQUENCE = {
            "Do you want to continue with Parameter Download?" : "YES",
            "Processing Parameter Download" : None,
            "Download succeeded" : ["Exit", True], # returns True upon success
            "Download failed" : ["Exit", False]
        }

    @staticmethod
    def navigate_to():
        """
        Navigates to PDL.
        Args: None
        Returns: Returns the result of execution of Navi.navigate_to()
        """
        return Navi.navigate_to("pdl download")

    def request(self, top_bar_msg_sequence = None, timeout = 60):
        """
        Requests a PDL. 
        Args:
            top_bar_msg_sequence: A dictionary of possible messages that may appear in the top bar,
                                  with values specifying which buttons to click in response.
            timeout: The maximum time (in seconds) that the program will continuously check for
                     top bar messages. Will timeout if the current top bar message does not match any
                     keys in top_bar_msg_sequence.
        Returns:
            True: If the PDL requested successfully.
            False: If the PDL was not requested successfully.
        Examples:
            \code
            pd = pdl.PDL()
            pd.request()
            True
            \endcode
        """
        if top_bar_msg_sequence is None:
            top_bar_msg_sequence = self.TOP_BAR_MSG_SEQUENCE

        current_msg = ''
        start_time = time.time()
        while time.time() - start_time < timeout:
            # Read current top bar message
            if current_msg != mws.get_top_bar_text():
                current_msg = mws.get_top_bar_text()
                self.log.debug(current_msg)
            # Check if any messages in the passed dictionary match the current message
            for dict_msg in top_bar_msg_sequence.keys():
                if dict_msg in current_msg:
                    if top_bar_msg_sequence[dict_msg]: # if there is a button to press...
                        # If the button is not a list, wrap it in list for consistency
                        if type(top_bar_msg_sequence[dict_msg]) is not list:
                            top_bar_msg_sequence[dict_msg] = [top_bar_msg_sequence[dict_msg]]
                        # Press the button
                        for btn in top_bar_msg_sequence[dict_msg]:
                            # A boolean input for btn indicates termination point
                            if type(btn) is bool:
                                return btn # will return true upon termination
                            elif not mws.click_toolbar(btn):
                                self.log.error(f"{top_bar_msg_sequence[dict_msg]} is not a valid toolbar button.")
                                return False
                    # else continue
        self.log.error("Timeout exceeded. Failing...")
        return False # if timeout