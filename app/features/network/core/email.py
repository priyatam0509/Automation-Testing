from app import mws, Navi
import glob
import time, logging

class Email:
    """
    Core e-mail feature class. Supports Concord network. To be extended and overridden for other networks
    where needed.
    """
    def __init__(self):
        self.log = logging.getLogger()
        self.navigate_to()

    @staticmethod
    def navigate_to():
        return Navi.navigate_to("EMail")
    
    def request(self, today = True, prnt = False):
        """
        Request emails from the Host

        Args:
            today: Which emails to print. Current accepted values: True - Today, False - Unread
            prnt: Whether to print the emails

        Returns:
            emails: A variable containing the contents of the email txt file generated
            None: If the emails failed to generate
            
        Examples:
            \code
            em = email.Email()
            if not em.request(today = True, prnt = True):
                mws.recover()
                tc_fail("Could not print the emails")
            True
            \endcode
        """
        msg = ''
        start_time = time.time()
        while time.time() - start_time < 300:
            #Handling the msg viewer prompts
            if msg != mws.get_top_bar_text():
                msg = mws.get_top_bar_text()
                self.log.debug(msg)
            if "Do you want to continue with Email Request?" in msg:
                mws.click_toolbar("Yes")
            elif "Processing Email Request" in msg:
                continue
            #Decide which option based on the 'today' variable
            elif "Press Yes to see Today's Mail" in msg:
                if today:
                    mws.click_toolbar("Yes")
                else:
                    mws.click_toolbar("No")
            #If done requesting emails, wait for them to load
            elif "Service completed" in msg:
                self.log.debug("Waiting on emails to load")
                second_time = time.time()
                while time.time() - second_time < 30:
                    if msg != mws.get_top_bar_text():
                        msg = mws.get_top_bar_text()
                        self.log.debug(msg)
                    if not msg:
                        #Read the email before exiting the screen
                        emails = []
                        path = "C:\Passport\Reports\Email*.txt"
                        for filename in glob.glob(path):
                            with open(filename, 'r') as f:
                                for line in f:
                                    emails.append(line)
                        if prnt:
                            mws.click_toolbar("Print", timeout = 10, main = True)
                        else:
                            mws.click_toolbar("Exit", timeout = 10, main = True)
                        #Return the values read from the email file
                        return emails
                self.log.error("Timed out waiting for the emails to load")
                return None
        self.log.error("Timed out in the prompts")
        return None