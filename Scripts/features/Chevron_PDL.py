"""
    File name: Chevron_PDL.py
    Brand: Chevron
    Description: [PEACOCK-3894] [PEACOCK-3898] [PEACOCK-3941] Tests the functionality of the PDL Module for WEX and Voyager Cards
    Author: Asha
    Date created: 2020-04-16 14:45:56
    Date last modified: 
    Python Version: 3.7
"""

import logging, time
from app import Navi, mws, system
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app import pdl
from app import runas

# The logging object. 
log = logging.getLogger()

def verify_db_result(cmd, check_list):
    """
    Description: Helper function to connect with EDH and fetch SQL query result from database
    Args:
		cmd: SQL query to be executed
        check_list : List to be searched in query result
    Returns: True if query successfully executed, False if fail
    """
    output = runas.run_sqlcmd(cmd, cmdshell=False)['output']
    output = output.replace(' ','')
    output_list = output.split("\n")
    range_found = False

    for range in check_list:
        for item in output_list:
            if range in item:
                range_found = True
                break      
        if not range_found:
            log.info(f"range not found is {range}")

    return range_found

class Chevron_PDL():
    """
    Description: Test class that provides an interface for testing.
    """

    def __init__(self):
        """Initializes the Template class.
        Args: None
        Returns: None
        """
        self.WEX_BIN_range1 = "70713800000000000007071389999999999999"
        self.WEX_BIN_range2 = "69004604660000000006900460466999999999"
        self.WEX_BIN_range3 = "62212600000000000006229999999999999999"
        self.VOY_BIN_range1 = "70888500000000000007088899999999999999"
        self.new_RID = 'A000000768'
        self.existing_RID = 'A000000003'
        self.VOY_RID = "A000000004"

    @setup
    def setup(self):
        """Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        pass

    @test
    def perform_pdl(self):
        """
        Zephyr ID : This will perform a Parameter Download request.
        Args: None
        Returns: None
        """
        pd = pdl.ParameterDownload()
        if not pd.request():
            tc_fail("Failed the Parameter Download")

        #wait for PDL to download
        time.sleep(20)

    @test
    def perform_emv_aidpk_download(self):
        """ 
        Zephyr ID : This will perform EMV AIDPK Download request.
        Args: None
        Returns: None
        """
        emv = pdl.EMVAIDPKDownload()
        if not emv.request():
            tc_fail("Failed the EMV Download")

    @test
    def TC03(self):
        """ 
        Zephyr ID : This will Verify "CardDataTable" is showing WEX card with new bin range "707138"
        Args: None
        Returns: None
        """
        cmd = "select CardRecType, PANRangeLow, PANRangeHigh from CardDataTable where PANRangeLow like '%707138%'"
        check_list = ['C'+self.WEX_BIN_range1, 'E'+self.WEX_BIN_range1, 'B'+self.WEX_BIN_range1]
                  
        if not verify_db_result(cmd, check_list):
                tc_fail(f"Required BIN range with Card type not present in database for WEX new bin range")

    @test
    def TC04(self):
        """ 
        Zephyr ID : This will Verify "CardDataTable" is showing WEX card with existing bin range "690046"
        Args: None
        Returns: None
        """
        cmd = "select CardRecType, PANRangeLow, PANRangeHigh from CardDataTable where PANRangeLow like '%690046%'"      
        check_list = ['C'+self.WEX_BIN_range2, 'E'+self.WEX_BIN_range2, 'B'+self.WEX_BIN_range2]
        
        if not verify_db_result(cmd, check_list):
            tc_fail(f"Required BIN range with Card type not present in database")

    @test
    def TC05(self):
        """ 
        Zephyr ID : This will Verify WEX cards data for EMV i.e. with RID: A000000768 is present in "nw_EMVParameters" table
        Args: None
        Returns: None
        """
        cmd = "select RID, TerminalLocationIndicator from nw_EMVParameters where RID like '"+self.new_RID+"'"
        log.info(f"cmd is {cmd}")
        
        check_list = [self.new_RID+'I', self.new_RID+'O']
        
        if not verify_db_result(cmd, check_list):
            tc_fail(f"Required RID with terminal location indicator not present in database")

    @test
    def TC06(self):
        """ 
        Zephyr ID : This will Verify WEX cards data for EMV i.e. with RID: A000000768 is present in "nw_EMVCAPublicKeys" table
        Args: None
        Returns: None
        """
        cmd = "select RID, CAPublicKeyIndex from nw_EMVCAPublicKeys where RID like '"+self.new_RID+"'"
        
        check_list = [self.new_RID+'E1', self.new_RID+'EE']
        
        if not verify_db_result(cmd, check_list):
            tc_fail(f"Required RID with CA Public key index not present in database")

    @test
    def TC07(self):
        """ 
        Zephyr ID : This will Verify "CardDataTable" is showing other cards
        Args: None
        Returns: None
        """
        cmd = "select CardRecType,PANRangeLow, PANRangeHigh from CardDataTable where PANRangeLow like '%622%'"
        
        check_list = ['C'+self.WEX_BIN_range3, 'E'+self.WEX_BIN_range3, 'B'+self.WEX_BIN_range3]
        
        if not verify_db_result(cmd, check_list):
            tc_fail(f"Required BIN range with Card type not present in database")

    @test
    def TC08(self):
        """ 
        Zephyr ID : This will Verify other cards data for EMV i.e. with RID are present in "nw_EMVParameters" table
        Args: None
        Returns: None
        """
        cmd = "select RID, TerminalLocationIndicator from nw_EMVParameters where RID like '"+self.existing_RID+"'"
        
        check_list = [self.existing_RID+'I', self.existing_RID+'O']
        
        if not verify_db_result(cmd, check_list):
            tc_fail(f"Required RID with terminal location indicator not present in database for existing RID")

    @test
    def TC09(self):
        """ 
        Zephyr ID : This will Verify other cards data for EMV i.e. with RID are present in "nw_EMVCAPublicKeys" table
        Args: None
        Returns: None
        """
        cmd = "select RID, CAPublicKeyIndex from nw_EMVCAPublicKeys where RID like '"+self.existing_RID+"'"
        
        check_list = [self.existing_RID+'08', self.existing_RID+'09']
        
        if not verify_db_result(cmd, check_list):
            tc_fail(f"Required RID with CA Public key index not present in database for existing RID")

    @test
    def TC10(self):
        """ 
        Zephyr ID : This will Verify "CardDataTable" is showing VOYAGER card with existing bin range "70888"
        Args: None
        Returns: None
        """
        cmd = "select CardRecType, PANRangeLow, PANRangeHigh from CardDataTable where PANRangeLow like '%70888%'"
        check_list = ['C'+self.VOY_BIN_range1, 'E'+self.VOY_BIN_range1, 'B'+self.VOY_BIN_range1]
                  
        if not verify_db_result(cmd, check_list):
                tc_fail(f"Required BIN range with Card type not present in database for Voyager existing BIN range")
    
    @test
    def TC11(self):
        """ 
        Zephyr ID : This will Verify VOYAGER cards data for EMV i.e. with RID: A000000004 is present in "nw_EMVParameters" table
        Args: None
        Returns: None
        """
        cmd = "select RID, TerminalLocationIndicator from nw_EMVParameters where RID like '"+self.VOY_RID+"' and ApplicationName like 'Voyager Credit'"
        
        check_list = [self.VOY_RID+'I', self.VOY_RID+'O']
        
        if not verify_db_result(cmd, check_list):
            tc_fail(f"Required RID with terminal location indicator not present in database for Voyager RID")

    @test
    def TC12(self):
        """ 
        Zephyr ID : This will Verify VOYAGER cards data for EMV i.e. with RID: A000000004 is present in "nw_EMVCAPublicKeys" table
        Args: None
        Returns: None
        """
        cmd = "select RID, CAPublicKeyIndex from nw_EMVCAPublicKeys where RID like '"+self.VOY_RID+"'"
        
        check_list = [self.VOY_RID+'05', self.VOY_RID+'06']
        
        if not verify_db_result(cmd, check_list):
            tc_fail(f"Required RID with CA Public key index not present in database for Voyager RID")

    @test
    def TC13(self):
        """ 
        Zephyr ID : This will verify total 54 rows is present in "nw_PromptCodeMapping" table
        Args: None
        Returns: None
        """
        cmd = "select count(*) from nw_PromptCodeMapping"
        
        check_list = ['54']
        
        if not verify_db_result(cmd, check_list):
            tc_fail(f"Required count not present in database")

    @test
    def TC14(self):
        """ 
        Zephyr ID : This will verify value 'J' is present in total 21 rows of "cPromptConversionTable" column 
                    in the "nw_PromptCodeMapping" table
        Args: None
        Returns: None
        """
        cmd = "select count(*) from nw_PromptCodeMapping where cPromptConversionTable = 'J'"
        
        check_list = ['21']
        
        if not verify_db_result(cmd, check_list):
            tc_fail(f"Required count not present in database")
    
    
    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        pass