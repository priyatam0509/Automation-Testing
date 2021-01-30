"""
    File name: Email_Test.py
    Tags: HPS-Dallas, Concord, Valero, Sunoco, Exxon
    Description: Tests the Email printing functionality
    Author: Conor McWain
    Date created: 2019-06-28 14:45:56
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import Navi, mws, pos, system
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app import email

class Email_Test():
    """
    Description: Test class that provides an interface for testing.
    """

    def __init__(self):
        """Initializes the Template class.
        Args: None
        Returns: None
        """
        # The logging object. 
        # Example: self.log.info(f"Current value of var: {my_var}")
        self.log = logging.getLogger()

    @setup
    def setup(self):
        """Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        # if not system.restore_snapshot():
        #     raise Exception

    @test
    def todays_mail(self):
        """Request Today's Mail, but don't print
        Args: None
        Returns: None
        """
        em = email.Email()
        emails = em.request(today = True, prnt = False)
        if emails:
            for lines in emails:
                self.log.info(lines)
        else:
            mws.recover()
            tc_fail("Failed requesting Today's Mail")

    @test
    def unread_mail(self):
        """Print all Unread Mail
        Args: None
        Returns: None
        """
        em = email.Email()
        emails = em.request(today = False,  prnt = True)
        if emails:
            for lines in emails:
                self.log.info(lines)
        else:
            mws.recover()
            tc_fail("Failed requesting Unread Mail")

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        # delete pass after you implement.
        pass