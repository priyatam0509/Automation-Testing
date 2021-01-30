"""
    File name: commercial_overrun_forgiven.py
    Tags: NGFC
    Description: Test cases for overruns with forgiven tender
    Author: Kevin Walker
    Date created: 2020-09-15 14:12:22
    Date last modified: 
    Python Version: 3.7
"""

import logging, time
from app import Navi, mws, pos, system, crindsim, forecourt_installation, networksim
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class commercial_overrun_forgiven():
    """
    Description: Test class that provides an interface for testing.
    """

    def __init__(self):
        """
        Initializes the Template class.
        """
        # The logging object. 
        # Example: self.log.info(f"Current value of var: {my_var}")
        self.log = logging.getLogger()

    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        """
        if not system.restore_snapshot():
            self.log.debug("No snapshot to restore, if this is not expected please contact automation team")
        mws.sign_on()
        # Configure forecourt for commercial diesel
        fc = forecourt_installation.ForecourtInstallation()
        mws.set_value("Blended Site", False)
        mws.click("Set Up")
        fc.delete_last("Dispensers")
        fc.change(item = "1", tab = "Dispensers", config = {"Commercial Diesel": True, "Reefer": True})
        #OCR selects the wrong tab when passing "Product" so selecting "Tank - Product" first allows the correct tab to be selected
        mws.select_tab("Tank - Product")
        fc.delete_last("Product")
        mws.select_tab("Tank - Product")
        fc.delete_last("Product")
        mws.select_tab("Tank - Product")
        fc.delete_last("Product")
        mws.select_tab("Tank - Product")
        fc.delete_last("Product")
        mws.select_tab("Tank - Product")
        fc.delete_last("Product")
        mws.select_tab("Tank - Product")
        fc.delete_last("Product")
        mws.select_tab("Tank - Product")
        #Configure fuel grades
        fc.add(tab = "Product", config = {"Name": "Diesel 1","Reefer" : "RD Dsl 1"})
        mws.select_tab("Tank - Product")
        fc.add(tab = "Product", config = {"Name": "Diesel 2", "Reefer" : ""})
        mws.select_tab("Tank - Product")
        fc.add(tab = "Product", config = {"Name": "DEF", "Reefer" : ""})
        #Delete current tanks and add new ones, there is an issue when switching from blended site to non-blended with tank mapping deleting and creating new ones solves this
        mws.select_tab("Tank - Product")
        fc.delete_last("Tanks")
        mws.select_tab("Tank - Product")
        fc.delete_last("Tanks")
        mws.select_tab("Tank - Product")
        fc.delete_last("Tanks")
        mws.select_tab("Tank - Product")
        fc.add(tab = "Tanks", config = {"Capacity" : "8000", "Product Top" : "Diesel 1"})
        mws.select_tab("Tank - Product")
        fc.add(tab = "Tanks", config = {"Capacity" : "8000", "Product Top" : "Diesel 2"})
        mws.select_tab("Tank - Product")
        fc.add(tab = "Tanks", config = {"Capacity" : "8000", "Product Top" : "DEF"})
        mws.select_tab("Tank - Product")
        #Map tanks to dispensers
        fc.change(item = "1", tab = "Tank - Product to Dispensers", config = {"Tank 1": "1 Diesel 1", "Tank 2": "2 Diesel 2", "Tank 3": "3 DEF"})
        mws.click_toolbar("Save")
        mws.click_toolbar("Save")
        #Restart passport after forecourt config changes
        system.restartpp()
        #Adding sleep to allow crinds to come back online after passport restart
        time.sleep(120)
        networksim.set_commercial_fuel_limit_send_mode("Fuel Product Configuration Based", 50, True)
        networksim.set_commercial_fuel_limit(True, '019', 10)
        networksim.set_commercial_fuel_limit(True, '032', 10)
        networksim.set_commercial_fuel_limit(True, '062', 10)

    @test
    def tractor_forgiven(self):
        """
        $4 overrun on tractor
        """
        if not crindsim.commercial(tractor_target_type = "money", tractor_target_amount = "14.00"):
            tc_fail("Transaction did not complete successfully")
        rec = crindsim.get_receipt().replace(" ", "").lower()
        if "forgiven:$4.00" not in rec:
            if "forgiven" not in rec:
                tc_fail("Forgiven tender not was listed on the receipt")
            else:
                tc_fail("Forgiven amount was not correct")
        if "diesel1" not in rec:
            tc_fail("Diesel 1 was not printed on the receipt")

    @test
    def reefer_forgiven(self):
        """
        $4 overrun on reefer
        """
        if not crindsim.commercial(selection="reefer", reefer_target_type = "money", reefer_target_amount = "14.00"):
            tc_fail("Transaction did not complete successfully")
        rec = crindsim.get_receipt().replace(" ", "").lower()
        if "forgiven:$4.00" not in rec:
            if "forgiven" not in rec:
                tc_fail("Forgiven tender was not listed on the receipt")
            else:
                tc_fail("Forgiven amount was not correct")
        if "rddsl1" not in rec:
            tc_fail("RD Dsl 1 was not printed on the receipt")

    @test
    def tractor_forgiven_with_def(self):
        """
        $4 overrun on tractor, DEF to auth
        """
        if not crindsim.commercial(tractor_target_type = "money", tractor_target_amount = "14.00", need_def="yes"):
            tc_fail("Transaction did not complete successfully")
        rec = crindsim.get_receipt().replace(" ", "").lower()
        if "forgiven:$4.00" not in rec:
            if "forgiven" not in rec:
                tc_fail("Forgiven tender was not listed on the receipt")
            else:
                tc_fail("Forgiven amount was not correct")   
        if "diesel1" not in rec:
            tc_fail("Diesel 1 was not printed on the receipt")
        if "def" not in rec:
            tc_fail("DEF was not printed on the receipt")

    @test
    def def_forgiven_with_tractor(self):
        """
        $4 overrun on DEF, tractor to auth
        """
        if not crindsim.commercial(def_target_type = "money", def_target_amount = "14.00", need_def="yes"):
            tc_fail("Transaction did not complete successfully")
        rec = crindsim.get_receipt().replace(" ", "").lower()
        if "forgiven:$4.00" not in rec:
            if "forgiven" not in rec:
                tc_fail("Forgiven tender was not listed on the receipt")
            else:
                tc_fail("Forgiven amount was not correct")   
        if "diesel1" not in rec:
            tc_fail("Diesel 1 was not printed on the receipt")
        if "def" not in rec:
            tc_fail("DEF was not printed on the receipt")   

    @test
    def tractor_and_def_forgiven(self):
        """
        $2 overrun on tractor and DEF
        """
        if not crindsim.commercial(tractor_target_type = "money", tractor_target_amount = "12.00", def_target_type = "money", def_target_amount = "12.00", need_def="yes"):
            tc_fail("Transaction did not complete successfully")
        rec = crindsim.get_receipt().replace(" ", "").lower()
        if "forgiven:$4.00" not in rec:
            if "forgiven" not in rec:
                tc_fail("Forgiven tender was not listed on the receipt")
            else:
                tc_fail("Forgiven amount was not correct")   
        if "diesel1" not in rec:
            tc_fail("Diesel 1 was not printed on the receipt")
        if "def" not in rec:
            tc_fail("DEF was not printed on the receipt") 

    @test
    def def_forgiven_with_reefer(self):
        """
        $4 overrun on DEF, reefer to auth
        """
        if not crindsim.commercial(selection = "reefer", def_target_type = "money", def_target_amount = "14.00", need_def="yes"):
            tc_fail("Transaction did not complete successfully")
        rec = crindsim.get_receipt().replace(" ", "").lower()
        if "forgiven:$4.00" not in rec:
            if "forgiven" not in rec:
                tc_fail("Forgiven tender was not listed on the receipt")
            else:
                tc_fail("Forgiven amount was not correct")   
        if "rddsl1" not in rec:
            tc_fail("RD Dsl 1 was not printed on the receipt")
        if "def" not in rec:
            tc_fail("DEF was not printed on the receipt") 

    @test
    def reefer_forgiven_with_def(self):
        """
        $4 overrun on reefer, DEF to auth
        """
        if not crindsim.commercial(selection = "reefer", reefer_target_type = "money", reefer_target_amount = "14.00", need_def="yes"):
            tc_fail("Transaction did not complete successfully")
        rec = crindsim.get_receipt().replace(" ", "").lower()
        if "forgiven:$4.00" not in rec:
            if "forgiven" not in rec:
                tc_fail("Forgiven tender was not listed on the receipt")
            else:
                tc_fail("Forgiven amount was not correct")   
        if "rddsl1" not in rec:
            tc_fail("RD Dsl 1 was not printed on the receipt")
        if "def" not in rec:
            tc_fail("DEF was not printed on the receipt")

    @test
    def def_and_reefer_forgiven(self):
        """
        $2 overrun on DEF and reefer
        """
        if not crindsim.commercial(selection = "reefer", reefer_target_type = "money", reefer_target_amount = "12.00", def_target_type = "money", def_target_amount = "12.00", need_def="yes"):
            tc_fail("Transaction did not complete successfully")
        rec = crindsim.get_receipt().replace(" ", "").lower()
        if "forgiven:$4.00" not in rec:
            if "forgiven" not in rec:
                tc_fail("Forgiven tender was not listed on the receipt")
            else:
                tc_fail("Forgiven amount was not correct")   
        if "rddsl1" not in rec:
            tc_fail("RD Dsl 1 was not printed on the receipt")
        if "def" not in rec:
            tc_fail("DEF was not printed on the receipt")                  

    @test
    def tractor_forgiven_with_reefer(self):
        """
        $4 overrun on tractor, reefer to auth
        """
        if not crindsim.commercial(selection = "both", tractor_target_type = "money", tractor_target_amount = "14.00"):
            tc_fail("Transaction did not complete successfully")
        rec = crindsim.get_receipt().replace(" ", "").lower()
        if "forgiven:$4.00" not in rec:
            if "forgiven" not in rec:
                tc_fail("Forgiven tender was not listed on the receipt")
            else:
                tc_fail("Forgiven amount was not correct")   
        if "diesel1" not in rec:
            tc_fail("Diesel 1 was not printed on the receipt")
        if "rddsl1" not in rec:
            tc_fail("RD Dsl 1 was not printed on the receipt")

    @test
    def reefer_forgiven_with_tractor(self):
        """
        $4 overrun on reefer, tractor to auth
        """
        if not crindsim.commercial(selection= "both", reefer_target_type = "money", reefer_target_amount = "14.00"):
            tc_fail("Transaction did not complete successfully")
        rec = crindsim.get_receipt().replace(" ", "").lower()
        if "forgiven:$4.00" not in rec:
            if "forgiven" not in rec:
                tc_fail("Forgiven tender was not listed on the receipt")
            else:
                tc_fail("Forgiven amount was not correct")   
        if "diesel1" not in rec:
            tc_fail("Diesel 1 was not printed on the receipt")
        if "rddsl1" not in rec:
            tc_fail("RD Dsl 1 was not printed on the receipt")   

    @test
    def tractor_and_reefer_forgiven(self):
        """
        $2 overrun on tractor and reefer
        """
        if not crindsim.commercial(selection = "both", tractor_target_type = "money", tractor_target_amount = "12.00", reefer_target_type = "money", reefer_target_amount = "12.00"):
            tc_fail("Transaction did not complete successfully")
        rec = crindsim.get_receipt().replace(" ", "").lower()
        if "forgiven:$4.00" not in rec:
            if "forgiven" not in rec:
                tc_fail("Forgiven tender was not listed on the receipt")
            else:
                tc_fail("Forgiven amount was not correct")   
        if "diesel1" not in rec:
            tc_fail("Diesel 1 was not printed on the receipt")
        if "rddsl1" not in rec:
            tc_fail("RD Dsl 1 was not printed on the receipt") 

    @test
    def tractor_forgiven_with_def_and_reefer(self):
        """
        $4 overrun on tractor, DEF and reefer to auth
        """
        if not crindsim.commercial(selection = "both", need_def = "yes", tractor_target_type = "money", tractor_target_amount = "14.00"):
            tc_fail("Transaction did not complete successfully")
        rec = crindsim.get_receipt().replace(" ", "").lower()
        if "forgiven:$4.00" not in rec:
            if "forgiven" not in rec:
                tc_fail("Forgiven tender was not listed on the receipt")
            else:
                tc_fail("Forgiven amount was not correct")   
        if "diesel1" not in rec:
            tc_fail("Diesel 1 was not printed on the receipt")
        if "def" not in rec:
            tc_fail("DEF was not printed on the receipt")
        if "rddsl1" not in rec:
            tc_fail("RD Dsl 1 was not printed on the receipt")
    
    @test
    def def_forgiven_with_tractor_and_reefer(self):
        """
        $4 overrun on DEF, tractor and reefer to auth
        """
        if not crindsim.commercial(selection = "both", need_def = "yes", def_target_type = "money", def_target_amount = "14.00"):
            tc_fail("Transaction did not complete successfully")
        rec = crindsim.get_receipt().replace(" ", "").lower()
        if "forgiven:$4.00" not in rec:
            if "forgiven" not in rec:
                tc_fail("Forgiven tender was not listed on the receipt")
            else:
                tc_fail("Forgiven amount was not correct")   
        if "diesel1" not in rec:
            tc_fail("Diesel 1 was not printed on the receipt")
        if "def" not in rec:
            tc_fail("DEF was not printed on the receipt")
        if "rddsl1" not in rec:
            tc_fail("RD Dsl 1 was not printed on the receipt")
    
    @test
    def reefer_forgiven_with_tractor_and_def(self):
        """
        $4 overrun on reefer, tractor and DEF to auth
        """
        if not crindsim.commercial(selection = "both", need_def = "yes", reefer_target_type = "money", reefer_target_amount = "14.00"):
            tc_fail("Transaction did not complete successfully")
        rec = crindsim.get_receipt().replace(" ", "").lower()
        if "forgiven:$4.00" not in rec:
            if "forgiven" not in rec:
                tc_fail("Forgiven tender was not listed on the receipt")
            else:
                tc_fail("Forgiven amount was not correct")   
        if "diesel1" not in rec:
            tc_fail("Diesel 1 was not printed on the receipt")
        if "def" not in rec:
            tc_fail("DEF was not printed on the receipt")
        if "rddsl1" not in rec:
            tc_fail("RD Dsl 1 was not printed on the receipt")

    @test
    def tractor_and_def_forgiven_with_reefer(self):
        """
        $2 overrun on tractor and DEF, reefer to auth
        """
        if not crindsim.commercial(selection = "both", need_def = "yes", tractor_target_type = "money", tractor_target_amount = "12.00", def_target_type = "money", def_target_amount = "12.00"):
            tc_fail("Transaction did not complete successfully")
        rec = crindsim.get_receipt().replace(" ", "").lower()
        if "forgiven:$4.00" not in rec:
            if "forgiven" not in rec:
                tc_fail("Forgiven tender was not listed on the receipt")
            else:
                tc_fail("Forgiven amount was not correct")   
        if "diesel1" not in rec:
            tc_fail("Diesel 1 was not printed on the receipt")
        if "def" not in rec:
            tc_fail("DEF was not printed on the receipt")
        if "rddsl1" not in rec:
            tc_fail("RD Dsl 1 was not printed on the receipt")

    @test
    def tractor_and_reefer_forgiven_with_def(self):
        """
        $2 overrun on tractor and reefer, DEF to auth
        """
        if not crindsim.commercial(selection = "both", need_def = "yes", tractor_target_type = "money", tractor_target_amount = "12.00", reefer_target_type = "money", reefer_target_amount = "12.00"):
            tc_fail("Transaction did not complete successfully")
        rec = crindsim.get_receipt().replace(" ", "").lower()
        if "forgiven:$4.00" not in rec:
            if "forgiven" not in rec:
                tc_fail("Forgiven tender was not listed on the receipt")
            else:
                tc_fail("Forgiven amount was not correct")   
        if "diesel1" not in rec:
            tc_fail("Diesel 1 was not printed on the receipt")
        if "def" not in rec:
            tc_fail("DEF was not printed on the receipt")
        if "rddsl1" not in rec:
            tc_fail("RD Dsl 1 was not printed on the receipt")

    @test
    def def_and_reefer_forgiven_with_tractor(self):
        """
        $2 overrun on DEF and reefer, tractor to auth
        """
        if not crindsim.commercial(selection = "both", need_def = "yes", def_target_type = "money", def_target_amount = "12.00", reefer_target_type = "money", reefer_target_amount = "12.00"):
            tc_fail("Transaction did not complete successfully")
        rec = crindsim.get_receipt().replace(" ", "").lower()
        if "forgiven:$4.00" not in rec:
            if "forgiven" not in rec:
                tc_fail("Forgiven tender was not listed on the receipt")
            else:
                tc_fail("Forgiven amount was not correct")   
        if "diesel1" not in rec:
            tc_fail("Diesel 1 was not printed on the receipt")
        if "def" not in rec:
            tc_fail("DEF was not printed on the receipt")
        if "rddsl1" not in rec:
            tc_fail("RD Dsl 1 was not printed on the receipt")

    @test
    def tractor_def_and_reefer_forgiven(self):
        """
        $1 overrun on tractor, DEF, and reefer
        """
        if not crindsim.commercial(selection = "both", need_def = "yes", tractor_target_type = "money", tractor_target_amount = "11.00", def_target_type = "money", def_target_amount = "11.00", reefer_target_type = "money", reefer_target_amount = "11.00"):
            tc_fail("Transaction did not complete successfully")
        rec = crindsim.get_receipt().replace(" ", "").lower()
        if "forgiven:$3.00" not in rec:
            if "forgiven" not in rec:
                tc_fail("Forgiven tender was not listed on the receipt")
            else:
                tc_fail("Forgiven amount was not correct")   
        if "diesel1" not in rec:
            tc_fail("Diesel 1 was not printed on the receipt")
        if "def" not in rec:
            tc_fail("DEF was not printed on the receipt")
        if "rddsl1" not in rec:
            tc_fail("RD Dsl 1 was not printed on the receipt")       
    
    @test
    def total_forgiven(self):
        """
        $4 overrun on total limit
        """
        networksim.set_commercial_fuel_limit(True, '019', 20)
        networksim.set_commercial_fuel_limit(True, '032', 20)
        networksim.set_commercial_fuel_limit(True, '062', 20)
        if not crindsim.commercial(selection = "both", need_def = "yes", reefer_target_type = "money", reefer_target_amount = "14.00"):
            tc_fail("Transaction did not complete successfully")
        rec = crindsim.get_receipt().replace(" ", "").lower()
        if "forgiven:$4.00" not in rec:
            if "forgiven" not in rec:
                tc_fail("Forgiven tender was not listed on the receipt")
            else:
                tc_fail("Forgiven amount was not correct")   
        if "diesel1" not in rec:
            tc_fail("Diesel 1 was not printed on the receipt")
        if "def" not in rec:
            tc_fail("DEF was not printed on the receipt")
        if "rddsl1" not in rec:
            tc_fail("RD Dsl 1 was not printed on the receipt")

    @test
    def retail_forgiven(self):
        """
        $4 overrun on retail dispenser
        """
        fc1 = forecourt_installation.ForecourtInstallation()
        mws.click("Set Up")
        fc1.change(item = "1", tab = "Dispensers", config = {"Commercial Diesel": False})
        mws.click_toolbar("Save")
        mws.click_toolbar("Save")
        #Restart passport after forecourt config changes
        system.restartpp()
        #Adding sleep to allow crinds to come back online after passport restart
        time.sleep(120)
        networksim.set_commercial_fuel_limit(True, '019', 50)
        crindsim.set_mode("manual")
        if not crindsim.crind_sale(card_name = "NGFC", brand = "Exxon", target_type = "money", target_amount = "54.00"):
            tc_fail("Transaction did not complete successfully")
        rec = crindsim.get_receipt().replace(" ", "").lower()
        if "forgiven:$4.00" not in rec:
            if "forgiven" not in rec:
                tc_fail("Forgiven tender was not listed on the receipt")
            else:
                tc_fail("Forgiven amount was not correct")   
        if "diesel1" not in rec:
            tc_fail("Diesel 1 was not printed on the receipt")


    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        pass
