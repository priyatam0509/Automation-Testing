"""
    File name: ASU_Mirroring.py
    Tags:
    Description: 
    Author: 
    Date created: 2019-07-30
    Date last modified: 
    Python Version: 3.7
"""

import logging
import json

from app import runas, system
from app.framework.tc_helpers import setup, test, teardown, tc_fail

from test_harness import RUN_DATA_FILE

class ASU_Mirroring():
    """
    Description: Test class that provides and interface for testing.
    """

    def __init__(self):
        """Initializes the Template class.
        Args: None
        Returns: None
        """
        # The logging object. 
        # Example: self.log.info(f"Current value of var: {my_var}")
        self.log = logging.getLogger()
        try:
            with open(RUN_DATA_FILE) as rdf:
                run_info = json.load(rdf)
                self.patch_file = run_info["Patch"]
        except KeyError as e:
            self.log.error(e)
            self.log.error("Failed to find the Patch variable. "\
            "Please use -var to pass in the Patch parameter")
            raise     

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
    def verify_images(self):
        """M-40246 : Mirrioring_R13
        
        Based on the schedule done, verify Image and database backups of MWS 
        are stored in CWS @ X:\Gilbarco\Mirror\Images
        """
        #@TODO: Add verification of database backups
        failure = False
        full_patch = f'{self.patch_file[:6]}{self.brand_id}{self.patch_file[8:]}'
        expected = [f'ver-r-POSSERVER01-{full_patch}.tbi', f'ver-p-POSSERVER01-{full_patch}.tbi']

        result = runas.run_sqlcmd(destination="POSCLIENT001",
                                user="PassportTech",
                                password="911Tech",
                                cmd=(f'dir X:\Gilbarco\Mirror\Images'))
        output = runas.parse_output(result)
        if not runas.error_check(output):
            tc_fail("There was an issue with the SQLCMD")
        
        for _file in expected:
            found = False
            self.log.debug(f"Looking for: {_file}")
            for _line in output:
                if _file in _line:
                    self.log.debug(f"Found: {_file}")
                    found = True
            if not found:
                failure = True
                self.log.error(f"Failed to find a file we expected: {_file}")

        if failure:
            self.log.debug(f"SQLCMD Output: {output}")
            tc_fail("See log above for missing/extra file")

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends."""
        # delete pass after you implement.
        pass