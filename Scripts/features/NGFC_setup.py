"""
    File name: DODO_setup.py
    Tags:
    Description: 
    Author: 
    Date created: 2020-03-17 10:00:56
    Date last modified: 
    Python Version: 3.7
"""

import logging
import time
from app import Navi, mws, pos, system, forecourt_installation, networksim, network_site_config, crindsim, runas, initial_setup
from app.framework import EDH
from app.util import constants
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app.features import feature_activation
from test_harness import site_type
from Scripts.features import NGFC_Helpers

class NGFC_setup():
    """
    Description: This test case is meant to enable all the commercial stuff needed to run in mainline
    """

    def __init__(self):
        """
        Initializes the Template class.
        """
        # The logging object. 
        
        self.log = logging.getLogger()

        self.helpers = NGFC_Helpers.NGFC_Helpers(self.log, mws, pos)


    @setup
    def setup(self):
        """
        Performs any initialization that is not default
        This script assumes that the site is already configured and 
        it just need to enable commercial stuff
        """
        
        self.enable_commercial_on_daily()

        self.log.info("Disable commercal prompts")
        networksim.disable_commercial_fuel_limits()
        networksim.disable_product_limits()
        networksim.disable_prompts()

        self.log.info("Set network sim to approve all")
        networksim.set_response_mode("Approval")
        
        self.log.info("Activate commercial on Forecourt config screen")
        self.set_commercial_on_forecourt()

        self.log.info("Perform a PDL to update the DB with commercial info")
        self.IS = initial_setup.Initial_setup(site_type)
        
        if not self.IS.pdl():
            
            tc_fail("There was an issue with the PDL")
    
    def set_commercial_on_forecourt(self):
        """
        Set the dispenser as commercial Diesel
        """
        fc_config = {
            "Dispensers" : {
                "Commercial Diesel": True,
                "Reefer": True
            }
        }
        
        fc = forecourt_installation.ForecourtInstallation()
        
        mws.click("Set Up")

        list_view_name = {
            "Dispensers" : "Dispensers",
            "Kiosks" : "Kiosks",
            "Payment Terminals" : "Terminals",
            "Product" : "Products",
            "Tanks" : "Tanks",
            "Tank - Product to Dispensers" : "Dispensers",
            "Grades to Dispensers" : "Dispensers",
            "Grade" : "Grades",
            "Tank Monitor" : "Monitors",
            "Tank Probe" : "Tank Monitors"
        }
        time.sleep(2)
        #Selecting the item and then clicking change.
        if mws.set_value(list_view_name["Dispensers"], "BLN_3+1", "Dispensers"):
            self.log.debug(f"Blended dispenser found, it will be deleted in order to have only one.")
            fc.delete_last("Dispensers")

        # Set Commercial Diesel feature to the crind Configured as "Gilbarco"
        # Setting Retry just in case it fail
        attempt = 1
        result = False
        while attempt < 3 and result is not True:

            
            self.log.info(f"Setting commercial Dispenser, attempt number {attempt}")
            result = fc.change("Gilbarco", "Dispensers", fc_config.get("Dispensers"))

            if result:

                # Checking if it was correctly set
                
                mws.select_tab("Dispensers")
                                
                #Selecting the item and then clicking change.
                if not mws.set_value("Dispensers", "Gilbarco", "Dispensers"):
                    self.log.error(f"Could not select Gilbarco on the Dispensers tab.")
                    return False
                mws.click("Change", "Dispensers")

                for key, intended_value in fc_config["Dispensers"].items():
                    current_value = mws.get_value(key,"Dispensers")
                
                    if current_value != intended_value:
                        self.log.error(f"'{key}' control was not set correctly.")
                        result = False


        if result is False:
            self.log.error("Unable to set commercial Dispenser")
            return False            

        for x in range (3):
            self.log.info(f"About to delete grade {x+3}")
            mws.select_tab("Tank - Product to")
            fc.delete_last("Grade")

        # We need to back to other tab so we can select the correct one
        mws.select_tab("Tank - Product to")

        fc.change("Regular",
                "Grade", 
                config={"Name": self.helpers.grade_1_Name,
                        "Reefer": self.helpers.grade_1_Name_reefer,
                        "Blended Grade": False,
                        "Low Product": "Product 1"
                })

        # We need to back to other tab so we can select the correct one
        mws.select_tab("Tank - Product to")
        
        fc.change("Plus",
                "Grade", 
                config={"Name": self.helpers.grade_2_Name,
                        "Reefer": self.helpers.grade_2_Name_reefer,
                        "Blended Grade": False,
                        "Low Product": "Product 2"
                })

        # We need to back to other tab so we can select the correct one
        mws.select_tab("Tank - Product to")

        fc.change("Supreme",
                "Grade", 
                config={"Name": self.helpers.grade_3_Name,
                        "Blended Grade": False,
                        "Low Product": "Product 3"
                })

        mws.select_tab("Grades To")
        
        mws.click("Change", "Grades To Dispensers")

        mws.set_value("Grade 1", f"{self.helpers.grade_1_Name}(Product 1)", "Grades To Dispensers")
        mws.set_value("Grade 2", f"{self.helpers.grade_2_Name}(Product 2)", "Grades To Dispensers")
        mws.set_value("Grade 3", f"{self.helpers.grade_3_Name}(Product 3)", "Grades To Dispensers")

        mws.click("Update List", "Grades To Dispensers")
        
        if not mws.click_toolbar("Save"):
            self.log.error("Unable to save Dispenser Options")
            return False
        
        if not mws.click_toolbar("Save"):
            self.log.error("Unable to save Dispenser Options")
            return False
        
    def enable_commercial_on_daily(self):
        """
        Enable the commercial stuff needed for runnning the scripts        
        """

        # Making visible commercial segments

        sql = "update singletons set MaskTypeId = 1 where FieldId = 351 and PSPId  = 23"

        self.log.info(f"About to run the following query {sql} in the EDH")

        result = runas.run_sqlcmd(sql, database="Network", cmdshell=False, 
                                       user="PassportTech", password="911Tech")['output']

        self.log.info(f"The query {sql} got the result {result}")
        
        self.log.info("Restarting the system to make changes take place")
        
        # Restart EDH to make changes take place
        edh = EDH.EDH()
        edh.restart()

        system.save_snapshot()
    
    @test
    def restart_passport(self):
        """
        Take a snapshot of the system after it is configured so all scripts start
        from the same place
        """
        
        #restart passport
        if not system.restartpp():
            tc_fail("Failed to restart passport")
            
        

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        pass
