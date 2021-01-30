from app import mws, Navi
import time, logging

class HostFunction:
    """
    Core fuel discount config feature class. Supports Concord network. To be extended and overridden for other networks
    where needed.
    """
    
    def __init__(self):
        self.log = logging.getLogger()
        self.navigate_to()
        
        # This dictionary will specify brand-specific top bar messages, 
        # as well as what toolbar button to click when they are displayed. 
        # A boolean input indicates a termination point (and what value to return) for the program.
        self.TOP_BAR_MSG_SEQUENCE = {
            "Do you want to continue with Host Function?" : "YES",
            "Processing Host Function" : None,
            "Do you want to perform a Communications Test?" : "YES",
            "Do you really want to perform a Communications Test?" : "YES",
            "COMM TEST PASSED" : ["Exit", True],
            "Test message failed - No connection" : ["Exit", False]
        }

        self.TOP_BAR_MSG_SEQUENCE_MAIL_REQUEST = {
            "Do you want to continue with Host Function?" : "NO",
            "Processing Host Function" : None,
            "Do you want to perform a Communications Test?" : "NO",
            "Do you want to perform a Mail Request?" : "YES",
            "Do you really want to perform a Mail Request?" : "YES",
            "Mail request succeeded" : ["Exit", True],
            "Mail request function failed" : ["Exit", False]
        }

        self.TOP_BAR_MSG_SEQUENCE_MAIL_RESET = {
            "Do you want to continue with Host Function?" : "NO",
            "Processing Host Function" : None,
            "Do you want to perform a Communications Test?" : "NO",
            "Do you want to perform a Mail Request?" : "NO",
            "Do you want to perform a Mail Reset?" : "YES",
            "Do you really want to perform a Mail Reset?" : "YES",
            "Mail reset sent" : ["Exit", True]
        }

    @staticmethod
    def navigate_to():
        return Navi.navigate_to("Host Function")

    def communications_test(self, top_bar_msg_sequence = None, timeout = 120):
        """
        Performs a Host Function - Communications Test

        Returns:
            True: Communications test Passed
            False: Communications test Failed
            
        Examples:
            \code
            hf = host_function.HostFunction()
            if not hf.communications_test():
                mws.recover()
                tc_fail("Failed the Comm Test")
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
    
    def mail_request(self, timeout = 120):
        """
        Performs a Host Function - Mail Request

        Delegates the execution to communications test with the special message sequence.

        Returns:
            True: Mail Request Passed
            False: Mail Request Failed
            
        Examples:
            \code
            hf = host_function.HostFunction()
            if not hf.mail_request():
                mws.recover()
                tc_fail("Failed the Mail Request")
            True
            \endcode
        """
        return self.communications_test(top_bar_msg_sequence = self.TOP_BAR_MSG_SEQUENCE_MAIL_REQUEST, timeout = timeout)

    def mail_reset(self, timeout = 120):
        """
        Performs a Host Function - Mail Reset

        Delegates the execution to communications test with the special message sequence.

        Returns:
            True: Mail Reset Passed
            False: Mail Reset Failed
            
        Examples:
            \code
            hf = host_function.HostFunction()
            if not hf.mail_reset():
                mws.recover()
                tc_fail("Failed the Mail Reset")
            True
            \endcode
        """
        return self.communications_test(top_bar_msg_sequence = self.TOP_BAR_MSG_SEQUENCE_MAIL_RESET, timeout = timeout)