"""
    File name: SL-1900.py
    Brand:  Concord
    Description: PDL changes to add Wex/Voyager cards
    Author: Yashwanth
    Date created: 2020-09-25 08:42:19
    Date last modified: 
    Python Version: 3.7
"""

import logging, time
from app import runas
from app.framework.tc_helpers import setup, test, teardown, tc_fail

# The logging object. 
log = logging.getLogger()

def verify_db_result(cmd, check_list):
    """
    Description: Helper function to connect with EDH and fetch SQL query result from database
    Args:
		cmd: SQL query to be executed
        check_list : RID/PIX number that we have to verify in query
    Returns: True if query successfully executed, False if fail
    """

    output = runas.run_sqlcmd(cmd, cmdshell=False)['output']
    output = output.replace(' ','')
    output_list = output.split("\n")

    if check_list not in output_list:
        log.error("RID/PIX not present in DB table")
        return False
    
    return True


class SL_1900():
    """
    Description: Test class that provides an interface for testing.
    """

    def __init__(self):
        """Initializes the Template class.
        Args: None
        Returns: None
        """

        self.wex_rid = "A000000768"
        self.voyager_rid = "A000000004"
        self.wex_pix = "1010"
        self.voyager_pix = "9999C00016"
        
    @setup
    def setup(self):
        """Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        pass

    @test
    def TC01(self):
        """ 
        Description : To Verify WEX cards data for EMV i.e. with RID: A000000768 is present in "FDC_EMVParameters" table
        Args: None
        Returns: None
        """

        query = "select RID from FDC_EMVParameters where ApplicationName like 'WEX'"
        if not verify_db_result(query, self.wex_rid):
            tc_fail("RID is not present for Wex card")
       
        return True
        
    @test
    def TC02(self):
        """ 
        Description : To Verify Voyager cards data for EMV i.e. with RID: A000000004  is present in "FDC_EMVParameters" table
        Args: None
        Returns: None
        """

        query = "select RID from FDC_EMVParameters where ApplicationName like 'Voyager'"
        if not verify_db_result(query, self.voyager_rid):
            tc_fail("RID is not present for Voyger card")
        
        return True

    @test
    def TC03(self):
        """ 
        Description : To Verify WEX cards data for EMV i.e. with PIX: 1010 is present in "FDC_EMVParameters" table
        Args: None
        Returns: None
        """

        query = "select PIX from FDC_EMVParameters where ApplicationName like 'Wex'"
        if not verify_db_result(query, self.wex_pix):
            tc_fail("PIX is not present for WEX card")
        
        return True

    @test
    def TC04(self):
        """ 
        Description : To Verify VOYAGER cards data for EMV i.e. with PIX: 9999C00016  is present in "FDC_EMVParameters" table
        Args: None
        Returns: None
        """

        query = "select PIX from FDC_EMVParameters where ApplicationName like 'Voyager'"
        if not verify_db_result(query, self.voyager_pix):
            tc_fail("PIX is not present for Voyager card")
        
        return True

    @test
    def TC05(self):
        """ 
        Description : To Verify other cards data for EMV i.e. with RID are present in "FDC_EMVParametersDefault" table
        Args: None
        Returns: None
        """

        query = "select RID from FDC_EMVParametersDefault"
        if "(0 rows affected)" in runas.run_sqlcmd(query, cmdshell=False)['output']:
            tc_fail("RID is not present for other cards")

        return True

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        pass