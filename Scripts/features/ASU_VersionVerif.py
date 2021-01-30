"""
    File name: ASU_VersionVerif.py
    Tags:
    Description: 
    Author: 
    Date created: 2019-07-30
    Date last modified: 
    Python Version: 3.7
"""

import datetime, logging, json, time
from os import listdir

from app import Navi, OCR, pos, runas, system
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app.util.gvrhtmlparser import HtmlParser

from test_harness import RUN_DATA_FILE

class ASU_VersionVerif():
    """
    Description: Verify the state of the system before applying an ASU Update.
    """

    def __init__(self):
        """Initializes the Template class."""
        # The logging object. 
        self.log = logging.getLogger()
        self.swupgrade = r"D:\Gilbarco\SWUpgrade"

        try:
            with open(RUN_DATA_FILE) as rdf:
                run_info = json.load(rdf)
                self.patch_file = run_info["Patch"]
        except KeyError as e:
            self.log.error(e)
            self.log.error("Failed to find the Patch variable. "\
            "Please use -var to pass in the Patch parameter")
            raise     

        #Get the EDH Patch number using the patch # provided by the tester
        patch_dir = f"{self.swupgrade}\Packages\{self.patch_file}"
        EPS_zip = []
        for f in listdir(f"{patch_dir}"):
            if "EPS_" in f and ".zip" in f:
                EPS_zip.append(f)

        if len(EPS_zip) > 1:
            log.error("There were more than one EPS zip in the Patch zip.")
        else:
            self.edh_patch = EPS_zip[0][4:-4]
            self.log.info(f"EDH Patch: {self.edh_patch}")


        try:
            with open(r"D:\Automation\app\data\brandIDs.json") as bIDs:
                brand_ids = json.load(bIDs)
                self.brand_id = brand_ids[system.get_brand().upper()]
        except KeyError as e:
            self.log.error(e)
            self.log.error("Failed to find the current Brand in the brandIDs file.")
            raise

    @setup
    def setup(self):
        """Performs any initialization that is not default."""
        # delete pass after you implement.
        pass

    @test
    def registry_ver(self):
        """TC1 : VersionVerif_TC1

        Verify the version number in the Registry
        """
        #system.get_version() = 12.02.23.01
        #self.patch_file = 12.02.XX.01
        if system.get_version() != f'{self.patch_file[:6]}{self.brand_id}{self.patch_file[8:]}':
            self.log.error(f'Expected Version: {self.patch_file[:6]}{self.brand_id}{self.patch_file[8:]}')
            self.log.error(f'Registry Version: {system.get_version()}')
            tc_fail("The version number in the Registry was wrong")

    @test
    def hlthchk_rpt_ver(self):
        """TC4 : VersionVerif_TC4
        
        Verify the version number in the Health Check Report
        """
        failure = False
        now = datetime.datetime.now()
        result = runas.run_as(r"C:\Gilbarco\Tools\EPSDashboard.exe PULLHEALTHCHECK")
        output = runas.parse_output(result)
        if not runas.error_check(output):
            tc_fail("There was an issue with the run_as function")
        
        parser = HtmlParser(f'C:\EPSFiles\HC\HealthCheck_{now.strftime("%Y%m%d")}.html')
        for ele in parser.data_list:
            if "Passport Version" in ele:
                if not self.edh_patch != ele[1]:
                    self.log.debug(f"File version: {ele[1]}")
                    self.log.error("Failed to match the first Passport Version")
                    failure = True
        
        if self.edh_patch != parser.data_list[-1][0]:
            self.log.debug(f"File version: {parser.data_list[-1][0]}")
            self.log.debug(f"Expected version: {self.edh_patch}")
            self.log.error("Failed to match the second Passport Version")
            failure = True

        if failure:
            tc_fail("See log above for error")
        
    @teardown
    def teardown(self):
        """Performs cleanup after this script ends."""
        # delete pass after you implement.
        pass