from app import mws, system, Navi
import logging

class CrindCashAcceptorOptions:
    """
    The class representing the CRIND Cash Acceptor Options
    window in Set up -> Forecourt section of MWS.

    The class allows to set various fields and checkboxes
    based on the configuration dictionary provided to it
    by user.
    """
    # The list with all bills that can be accepted in the module
    BILLS = ["$1", "$2", "$5", "$10", "$20", "$50", "$100"]

    def __init__(self):
        self.log = logging.getLogger()
        CrindCashAcceptorOptions.navigate_to()
        return

    @staticmethod
    def navigate_to():
        """
        Navigates to the CRIND Cash Acceptor Options menu.
        Args:
            None
        Returns:
            Returns the result of execution of Navi.navigate_to()
        """
        return Navi.navigate_to("CRIND Cash Acceptor Options")

    def setup(self, params):
        """
        Configures the fields and checkboxes acessible in the 
        CRIND Cash Acceptor Options window according to the provided
        dictionary.

        Args:
            params: the dictionary with the information about
                    various fields and checkboxes that need to be 
                    configured.
                    This will need to be setup according to the schema in controls.json.

        Returns:
            True: If CRIND Cash Acceptor Options was successfully set up.
            False: If something went wrong while setting up (will be logged).

        Example:
            params = {
                "Max cash accepted per transaction": "100", # Cannot exceed 990
                "Max Bill Insertion Retries": "5", # Can be in range 1:5
                "Total $ amount in vault exceeds": "500", # Cannot exceed 9999
                "Total number of bills in vault exceeds": "500", # Cannot exceed 500
                "Min $ amount reserved for fuel purchase": "1", # Cannot exceed 5
                "Bills Accepted" : ["$1", "$2", "$5", "$10", "$20", "$50", "$100"]
            }
            >>> setup(params, )
                True
        """
        # Check if the bills section will be configured
        if "Bills Accepted" in params.keys():
            # Uncheck all bills to prepare the section for new config
            for bill in self.BILLS:
                if not mws.set_value(bill, False):
                    self.log.error(f"Could not uncheck {bill} to prepare the window for configuration.")
                    system.takescreenshot()
                    return False

        # Create error flag
        error = False

        for field, value in params.items():
            # field = "Total $ amount in vault exceeds"
            # value = "500"
            if field == "Bills Accepted":
                # value = ["$1", "$2", "$5", "$10", "$20", "$50", "$100"]
                for bill in value:
                    # "$1"
                    if not mws.set_value(bill, True):
                        self.log.error(f"Could not check the '{bill}' checkbox.")
                        error = True
            elif not mws.set_value(field, value):
                self.log.error(f"Could not set {field} with {value}.")
                error = True

        if not mws.click_toolbar("Save"):
            self.log.error("Unable to save CRIND Cash Acceptor Options")
            error = True
        
        # Check for top bar message
        top_bar_message = mws.get_top_bar_text()
        if top_bar_message :
            if top_bar_message == "Warning: You have selected $50 and/or $100 bills.  Are you sure your CASH ACCEPTOR accepts these bill types?":
                mws.click_toolbar("YES")
            else:
                self.log.error(f"Unexpected top bar message is '{top_bar_message}'")
                system.takescreenshot()
                error = True
        
        # Check for errors
        if error:
            self.log.error("There were errors in the process of configuring CRIND Cash Acceptor Options")
            return False

        return True
