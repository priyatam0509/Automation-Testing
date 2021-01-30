"""
    File name: ASU_FileCleanup_EDH.py
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

from app import runas, system
from app.framework.tc_helpers import setup, test, teardown, tc_fail

from test_harness import RUN_DATA_FILE

class ASU_FileCleanup_EDH():
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
        self.swupgrade = r"D:\Gilbarco\SWUpgrade"
        self.images = r"D:\Gilbarco\Images"
        self.images_f = r"F:\Gilbarco\Images"
        self.packages = r"C:\Gilbarco\PACKAGES"

        #Read the patch variable passed in at the test_harness call
        try:
            with open(RUN_DATA_FILE) as rdf:
                run_info = json.load(rdf)
                patch_file = run_info["Patch"]
        except KeyError as e:
            self.log.error(e)
            self.log.error("Failed to find the Patch variable. "\
            "Please use -var to pass in the Patch parameter")
            raise

        #Get the EDH Patch number using the patch # provided by the tester
        patch_dir = f"{self.swupgrade}\Packages\{patch_file}"
        EPS_zip = []
        for f in listdir(f"{patch_dir}"):
            if "EPS_" in f and ".zip" in f:
                EPS_zip.append(f)

        if len(EPS_zip) > 1:
            self.log.error("There were more than one EPS zip in the Patch zip.")
        else:
            self.edh_patch = EPS_zip[0][:-4]
            self.log.info(f"EDH Patch: {self.edh_patch}")

        #Convert brand into the Customer Number
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
        """M-40265 : FilesCleanupEDH_F24
        
        Only packages.xml, Pending.xml, StoreCloseAction.xml files are 
        available in D:\Gilbarco\SWUpgrade
        """
        expected = ["Packages.xml", "Pending.xml", "UpgradeStatus.xml"]
        
        result = runas.run_sqlcmd(f'dir {self.swupgrade}')
        output = runas.parse_output(result)
        if not runas.error_check(output):
            tc_fail("There was an issue with the SQLCMD")

        if not self.flie_verif(expected, output):
            self.log.debug(f"SQLCMD Output: {output}")
            tc_fail("See log above for missing/extra file")

    @test
    def packages_xml(self):
        """M-40266 : FilesCleanupEDH_F25
        
        Open the packages.xml and verify the listed packages match what 
        you have installed on your site
        """
        found = False

        result = runas.run_sqlcmd(f'type {self.swupgrade}\Packages.xml')
        output = runas.parse_output(result)
        if not runas.error_check(output):
            tc_fail("There was an issue with the SQLCMD")

        for _line in output:
            if "<VERSION>" in _line:
                #_line = <VERSION>09.XX.02.01</VERSION>
                #self.edh_patch = EPS_09.XX.02.01
                if self.edh_patch[4:] != _line[9:-10]:
                    self.log.debug(f"Patch Provided: {self.edh_patch[4:]}  XML Version: {_line[9:-10]}")
                    continue
                else:
                    self.log.debug(f"Found the correct Version")
                    found = True

        if not found:
            tc_fail("Failed to find the Patch version in the file")

    @test
    def pending_xml(self):
        """M-40267 : FilesCleanupEDH_F26
        
        Open the pending.xml and verify there are no packages listed
        """
        result = runas.run_sqlcmd(f'type {self.swupgrade}\Pending.xml')
        output = runas.parse_output(result)
        if not runas.error_check(output):
            tc_fail("There was an issue with the SQLCMD")

        for _line in output:
            if "<PACKAGE>" in _line:
                tc_fail("Found a <PACKAGE> tag")

    @test
    def pending_folder(self):
        """M-40268 : FilesCleanupEDH_F27
        
        No files/Folders should be present in Pending Folder
        """
        failure = False
        result = runas.run_sqlcmd(f'dir {self.swupgrade}\Pending')
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
    def invalid_folder(self):
        """M-40269 : FilesCleanupEDH_F28
        
        No files/Folders should be present in Invalid Folder
        """
        failure = False
        result = runas.run_sqlcmd(f'dir {self.swupgrade}\Invalid')
        output = runas.parse_output(result)
        if not runas.error_check(output):
            tc_fail("There was an issue with the SQLCMD")

        for _line in output:
            if "File(s)" in _line:
                if _line[0] != "0":
                    self.log.error("There are files in the Invalid folder")
                    failure = True
            if "Dir(s)" in _line:
                #This is two since we pick up the "." and ".." directory aliases
                if _line[0] != "2":
                    self.log.error("There are folders in the Invalid folder")
                    failure = True

        if failure:
            tc_fail("See log above for missing/extra file")

    @test
    def asu_image(self):
        """M-40270 : FilesCleanupEDH_F29
        
        ASU Image captured automatically in D:\Gilbarco\Images
        """
        #self.edh_patch = EPS_09.XX.02.01D
        expected = [f'asu-p-PASSPORTEPS-{self.edh_patch[4:7]}{self.brand_id}{self.edh_patch[9:15]}.tbi']

        result = runas.run_sqlcmd(f'dir {self.images}')
        output = runas.parse_output(result)
        if not runas.error_check(output):
            tc_fail("There was an issue with the SQLCMD")

        if not self.flie_verif(expected, output):
            self.log.debug(f"SQLCMD Output: {output}")
            tc_fail("See log above for missing/extra file")

    @test
    def new_primary(self):
        """M-40271 : FilesCleanupEDH_F30
        
        New Primary and Recovery Image automatically captured at the top 
        of the hour on EDH after patch has been installed. 
        F:\Gilbarco\Images
        """
        expected = [
            f'ver-r-PASSPORTEPS-{self.edh_patch[4:7]}{self.brand_id}{self.edh_patch[9:]}.tbi',
            f'ver-p-PASSPORTEPS-{self.edh_patch[4:7]}{self.brand_id}{self.edh_patch[9:]}.tbi'
            ]

        result = runas.run_sqlcmd(f'dir {self.images_f}')
        output = runas.parse_output(result)
        if not runas.error_check(output):
            tc_fail("There was an issue with the SQLCMD")

        if not self.flie_verif(expected, output):
            self.log.debug(f"SQLCMD Output: {output}")
            tc_fail("See log above for missing/extra file")

    @test
    def package_archive(self):
        """M-40272 : FilesCleanupEDH_F31
        
        Verify Package was properly archived to C:\gilbarco\packages
        """
        expected = [f"{self.edh_patch[4:]}.zip"]

        result = runas.run_sqlcmd(f'dir {self.packages}')
        output = runas.parse_output(result)
        if not runas.error_check(output):
            tc_fail("There was an issue with the SQLCMD")

        if not self.flie_verif(expected, output):
            self.log.debug(f"SQLCMD Output: {output}")
            tc_fail("See log above for missing/extra file")

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        # delete pass after you implement.
        pass

    def flie_verif(self, files, output):
        """
        Check the parsed result of an SQLCMD for specific files/folders

        Args:
            files (list): The list of files being looked for in the output
            output (list): The parsed output from SQLCMD

        Returns:
            True/False (bool): True if all files are found, False if any are not found
        """
        result = True
        for _file in files:
            found = False
            self.log.debug(f"Looking for: {_file}")
            for _line in output:
                if _file in _line:
                    self.log.debug(f"Found: {_file}")
                    found = True
            if not found:
                result = False
                self.log.error(f"Failed to find a file we expected: {_file}")

        return result
