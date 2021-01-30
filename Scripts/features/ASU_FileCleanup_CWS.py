"""
    File name: ASU_FileCleanup_CWS.py
    Tags:
    Description: 
    Author: 
    Date created: 2019-07-30
    Date last modified: 
    Python Version: 3.7
"""

import logging
import json
from os import listdir
from os.path import isfile, join

from app import runas
from app import system
from app.framework.tc_helpers import setup, test, teardown, tc_fail

from test_harness import RUN_DATA_FILE

class ASU_FileCleanup_CWS():
    """
    Description: Test class that provides and interface for testing.
    """

    def __init__(self):
        """
        Initializes the Template class.
        """
        # The logging object. 
        # Example: self.log.info(f"Current value of var: {my_var}")
        self.log = logging.getLogger()
        self.swupgrade = r"X:\Gilbarco\SWUpgrade"
        self.images = r"X:\Gilbarco\Images"
        self.images_d = r"D:\Gilbarco\Images"
        self.packages = r"C:\Gilbarco\PACKAGES"

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
        """
        Performs any initialization that is not default.
        """
        # delete pass after you implement.
        pass

    @test
    def swupgrade_contents(self):
        """M-40258 : FilesCleanupCWS_F17
        
        Only packages.xml files are available in X:\Gilbarco\SWUpgrade
        """
        failure = False
        expected = ["Packages.xml"]
        result = runas.run_sqlcmd(destination="POSCLIENT001",
                                user="PassportTech",
                                password="911Tech",
                                cmd=(f'dir {self.swupgrade}'))
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
                self.log.debug(f"SQLCMD Output: {output}")

        if failure:
            tc_fail("See log above for missing/extra file")


    @test
    def packages_xml(self):
        """M-40259 : FilesCleanupCWS_F18
        
        Open the packages.xml and verify the listed packages match what you have installed on your site.
        """
        found = False
        result = runas.run_sqlcmd(destination="POSCLIENT001",
                                user="PassportTech",
                                password="911Tech",
                                cmd=(f'type {self.swupgrade}\Packages.xml'))
        output = runas.parse_output(result)
        if not runas.error_check(output):
            tc_fail("There was an issue with the SQLCMD")

        for _line in output:
            if "<VERSION>" in _line:
                #_line = <VERSION>12.02.XX.01D</VERSION>
                #_line[9:-10] = 12.02.XX.01D
                #self.patch_file = 12.02.XX.01D
                if not self.patch_file in _line[9:-10]:
                    self.log.debug(f"Patch Provided: {self.patch_file}  XML Version: {_line[9:-10]}")
                    continue
                else:
                    self.log.debug(f"Found the correct Version")
                    found = True

        if not found:
            self.log.debug(f"SQLCMD Output: {output}")
            tc_fail("Failed to find the Patch version in the file")


    @test
    def pending_folder(self):
        """M-40260 : FilesCleanupCWS_F19
        
        No files/Folders should be present in Pending Folder
        """
        failure = False
        
        result = runas.run_sqlcmd(destination="POSCLIENT001",
                                user="PassportTech",
                                password="911Tech",
                                cmd=(f'dir {self.swupgrade}\Pending'))
        output = runas.parse_output(result)
        if not runas.error_check(output):
            tc_fail("There was an issue with the SQLCMD")

        for _line in output:
            if "File(s)" in _line:
                if _line[0] != "0":
                    self.log.error("There are files in the Pending folder")
                    failure = True
            #This is two since we pick up the "." and ".." directory aliases
            if "Dir(s)" in _line:
                if _line[0] != "2":
                    self.log.error("There are folders in the Pending folder")
                    failure = True

        if failure:
            tc_fail("See log above for missing/extra file")
            

    @test
    def pending_invalid(self):
        """M-40261 : FilesCleanupCWS_F20
        
        Verify No Pending folder is present in X:\Gilbarco\SWUpgrade\
         and if present there are No files in Invalid Folder
        """
        tc_fail("This TC requires an answer from Rhea")

    @test
    def asu_image(self):
        """M-40262 : FilesCleanupCWS_F21
        
        ASU Image captured automatically in X:\Gilbarco\Images
        """
        #self.patch_file = "12.02.XX.01D"
        # Will need to remove the Patch letter
        expected = [f'asu-p-POSCLIENT001-{self.patch_file[:6]}{self.brand_id}{self.patch_file[8:]}.tbi']

        tc_fail("ASU Image is nowhere to be found")
        #@TODO: Where is this image supposedly captured?

    @test
    def new_primary(self):
        """M-40263 : FilesCleanupMWS_F22
        
        New Primary Image automatically captured on MWS after (may take a few hours) patch has been installed. D:\Gilbarco\Images\VER-P-POSCLIENT001-<current_patch>.IMG
        """
        #self.patch_file = "12.02.XX.01D"
        expected = [f'ver-p-POSCLIENT001-{self.patch_file[:6]}{self.brand_id}{self.patch_file[8:]}.tbi']
        present = [f for f in listdir(self.images_d) if isfile(join(self.images_d, f))]

        for f in expected:
            if f not in present:
                self.log.debug(present)
                tc_fail(f"Failed to find a file we expected: {f}")

    @test
    def package_archive(self):
        """M-40264 : FilesCleanupCWS_F23
        
        Verify Package was properly archived to C:\gilbarco\packages
        """
        failure = False
        expected = [f"{self.patch_file}.zip"]

        result = runas.run_sqlcmd(destination="POSCLIENT001",
                                user="PassportTech",
                                password="911Tech",
                                cmd=(f'dir {self.packages}'))
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
                self.log.debug(f"SQLCMD Output: {output}")

        if failure:
            tc_fail("See log above for missing/extra file")

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        # delete pass after you implement.
        pass