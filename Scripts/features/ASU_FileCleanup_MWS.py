"""
    File name: ASU_FileCleanup_MWS.py
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
from pathlib import Path
import xml.etree.ElementTree as et

from app import system
from app.framework.tc_helpers import setup, test, teardown, tc_fail

from test_harness import RUN_DATA_FILE

class ASU_FileCleanup_MWS():
    """
    Description: Test class that provides and interface for testing.
    """

    def __init__(self):
        """Initializes the Template class."""
        # The logging object. 
        # Example: self.log.info(f"Current value of var: {my_var}")
        self.log = logging.getLogger()
        self.swupgrade = r"D:\Gilbarco\SWUpgrade"
        self.pending = r"D:\Gilbarco\SWUpgrade\Pending"
        self.invalid = r"D:\Gilbarco\SWUpgrade\Invalid"
        self.images = r"D:\Gilbarco\Images"
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
        """Performs any initialization that is not default."""
        # delete pass after you implement.
        pass

    @test
    def swupgrade_contents(self):
        """M-40250 - FilesCleanupMWS_F9
        
        Only packages.xml, Pending.xml, StoreCloseAction.xml files are 
        available in D:\Gilbarco\SWUpgrade
        """
        failure = False
        expected = ["Packages.xml", "Pending.xml", "StoreCloseAction.xml", "UpgradeStatus.xml"]
        present = [f for f in listdir(self.swupgrade) if isfile(join(self.swupgrade, f))]

        for f in present:
            if f not in expected:
                self.log.error(f"Found a file we did not expect: {f}")
                failure = True

        for f in expected:
            if f not in present:
                self.log.error(f"Failed to find a file we expected: {f}")
                failure = True

        if failure:
            tc_fail("See log above for missing/extra file")
                
    @test
    def packages_xml(self):
        """M-40251 - FilesCleanupMWS_F10
        
        Open the packages.xml and verify the listed packages match what 
        you have installed on your site
        """
        packages = Path(f"{self.swupgrade}\\Packages.xml")
        #Verify the file exists
        if not packages.exists():
            tc_fail("Failed to find the Packages.xml file")

        #Read the file
        tree = et.parse(packages)
        root = tree.getroot()

        #Define the value of the namespace in the xml. We need this to find the elements
        ns = {'NS': 'http://www.gilbarco.com/schema/fcc/asu1.0'}
        versions = root.findall('NS:PACKAGE/NS:VERSION', ns)

        #Make sure there is at least one version tag in the file
        if len(versions) == 0:
            tc_fail("We found no Version tags in the file")

        for version in versions:
            if self.patch_file == version.text:
                self.log.debug(f"Found the matching version tag: {version.text}")
                found = True
                break

        if not found:
            tc_fail(f"Failed to find: {self.patch_file} in the xml file")

    @test
    def pending_xml(self):
        """M-40252 - FilesCleanupMWS_F11
        
        Open the pending.xml and verify there are no packages listed
        """
        pending = Path(f"{self.swupgrade}\\Pending.xml")
        #Verify the file exists
        if not pending.exists():
            tc_fail("Failed to find the Pending.xml file")

        #Read the file
        tree = et.parse(pending)
        root = tree.getroot()

        #Define the value of the namespace in the xml. We need this to find the elements
        ns = {'NS': 'http://www.gilbarco.com/schema/fcc/asu1.0'}
        package = root.findall('NS:PACKAGE', ns)

        #Verify there is no PACKAGE element
        if len(list(package)) > 0:
            tc_fail("There was a 'PACKAGE' Element in the xml.")

    @test
    def pending_folder(self):
        """M-40253 - FilesCleanupMWS_F12
        
        No files/Folders should be present in Pending Folder
        """
        failure = False
        expected = []
        present = [f for f in listdir(self.pending) if isfile(join(self.pending, f))]

        for f in present:
            if f not in expected:
                self.log.error(f"Found a file we did not expect: {f}")
                failure = True

        for f in expected:
            if f not in present:
                self.log.error(f"Failed to find a file we expected: {f}")
                failure = True

        if failure:
            tc_fail("See log above for missing/extra file")

    @test
    def invalid_folder(self):
        """M-40254 - FilesCleanupMWS_F13
        
        No files/Folders should be present in Invalid Folder
        """
        failure = False
        expected = []
        present = [f for f in listdir(self.invalid) if isfile(join(self.invalid, f))]

        for f in present:
            if f not in expected:
                self.log.error(f"Found a file we did not expect: {f}")
                failure = True

        for f in expected:
            if f not in present:
                self.log.error(f"Failed to find a file we expected: {f}")
                failure = True

        if failure:
            tc_fail("See log above for missing/extra file")

    @test
    def asu_image(self):
        """M-40255 - FilesCleanupMWS_F14
        
        ASU Image of previous patch captured automatically in 
        D:\Gilbarco\Images
        """
        expected = [f'ver-r-POSSERVER01-{self.patch_file[:6]}{self.brand_id}{self.patch_file[8:]}.tbi']
        present = [f for f in listdir(self.images) if isfile(join(self.images, f))]

        for f in expected:
            if f not in present:
                tc_fail(f"Failed to find a file we expected: {f}")

    @test
    def new_primary(self):
        """M-40256 - FilesCleanupMWS_F15
        
        New Primary Image automatically captured after patch has been 
        installed in D:\Gilbarco\Images
        """
        expected = [f'ver-p-POSSERVER01-{self.patch_file[:6]}{self.brand_id}{self.patch_file[8:]}.tbi']
        present = [f for f in listdir(self.images) if isfile(join(self.images, f))]

        for f in expected:
            if f not in present:
                tc_fail(f"Failed to find a file we expected: {f}")

    @test
    def package_archive(self):
        """M-40257 - FilesCleanupMWS_F16
        
        Verify Package was properly archived to C:\gilbarco\packages
        """
        expected = [f"{self.patch_file}.zip"]
        present = [f for f in listdir(self.packages) if isfile(join(self.packages, f))]

        for f in expected:
            if f not in present:
                tc_fail(f"Failed to find a file we expected: {f}")

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends."""
        # delete pass after you implement.
        pass