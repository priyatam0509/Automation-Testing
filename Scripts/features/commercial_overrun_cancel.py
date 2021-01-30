"""
    File name: commercial_overrun_cancel.py
    Tags: NGFC
    Description: Overruns on NGFC that cancel at the CRIND and go inside for completition
    Author: Kevin Walker
    Date created: 2020-10-22 10:27:39
    Date last modified: 
    Python Version: 3.7
"""

import logging, time
from app import Navi, mws, pos, system, crindsim, forecourt_installation, networksim
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class commercial_overrun_cancel():
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
        #Set limits in sim for commercial products
        networksim.set_commercial_fuel_limit_send_mode("Fuel Product Configuration Based", 50, True)
        networksim.set_commercial_fuel_limit(True, '019', 10)
        networksim.set_commercial_fuel_limit(True, '032', 10)
        networksim.set_commercial_fuel_limit(True, '062', 10)
        pos.connect()
        pos.sign_on()


    @test
    def tractor_over(self):
        """
        $6 overrun on Tractor
        """
        # if crindsim.commercial returns true sale did not go inside for completion
        if crindsim.commercial(tractor_target_type = "money", tractor_target_amount = "16.00"):
            tc_fail("Transaction completed at the CRIND should have gone inside")
        if not self.inside():
            tc_fail("Overrun error message is not displayed at the POS")

    @test
    def reefer_over(self):
        """
        $6 overrun on Reefer
        """
        # if crindsim.commercial returns true sale did not go inside for completion
        if crindsim.commercial(selection = "reefer", reefer_target_type = "money", reefer_target_amount = "16.00"):
            tc_fail("Transaction completed at the CRIND should have gone inside")
        if not self.inside():
            tc_fail("Overrun error message is not displayed at the POS")

    @test
    def def_over_with_tractor(self):
        """
        Tractor to auth, $6 overrun on DEF
        """
        # if crindsim.commercial returns true sale did not go inside for completion
        if crindsim.commercial(def_target_type = "money", def_target_amount = "16.00", need_def="yes"):
            tc_fail("Transaction completed at the CRIND should have gone inside")
        if not self.inside():
            tc_fail("Overrun error message is not displayed at the POS")

    @test
    def tractor_over_with_def(self):
        """
        Select tractor with DEF, $6 overrun on Tractor
        """
        # if crindsim.commercial returns true sale did not go inside for completion
        if crindsim.commercial(tractor_target_type = "money", tractor_target_amount = "16.00", need_def="yes"):
            tc_fail("Transaction completed at the CRIND should have gone inside")
        if not self.inside():
            tc_fail("Overrun error message is not displayed at the POS")

    @test
    def tractor_and_def_over(self):
        """
        $3 overrun on Tractor, $3 Overrun on DEF
        """
        # if crindsim.commercial returns true sale did not go inside for completion
        if crindsim.commercial(tractor_target_type = "money", tractor_target_amount = "13.00", def_target_type = "money", def_target_amount = "13.00", need_def="yes"):
            tc_fail("Transaction completed at the CRIND should have gone inside")
        if not self.inside():
            tc_fail("Overrun error message is not displayed at the POS")

    @test
    def def_over_with_reefer(self):
        """
        Select Reefer with DEF, $6 overrun on DEF
        """
        # if crindsim.commercial returns true sale did not go inside for completion
        if crindsim.commercial(selection = "reefer", def_target_type = "money", def_target_amount = "16.00", need_def="yes"):
            tc_fail("Transaction completed at the CRIND should have gone inside")
        if not self.inside():
            tc_fail("Overrun error message is not displayed at the POS")

    @test
    def reefer_over_with_def(self):
        """
        DEF to auth, Reefer $6 overrun
        """
        # if crindsim.commercial returns true sale did not go inside for completion
        if crindsim.commercial(selection = "reefer", reefer_target_type = "money", reefer_target_amount = "16.00", need_def="yes"):
            tc_fail("Transaction completed at the CRIND should have gone inside")
        if not self.inside():
            tc_fail("Overrun error message is not displayed at the POS")

    @test
    def reefer_and_def_over(self):
        """
        $3 overrun on DEF, $3 overrun on Reefer
        """
        # if crindsim.commercial returns true sale did not go inside for completion
        if crindsim.commercial(selection = "reefer", reefer_target_type = "money", reefer_target_amount = "13.00", def_target_type = "money", def_target_amount = "13.00", need_def="yes"):
            tc_fail("Transaction completed at the CRIND should have gone inside")
        if not self.inside():
            tc_fail("Overrun error message is not displayed at the POS")

    @test
    def tractor_over_with_reefer(self):
        """
        Select both Tractor and Reefer, $6 overrun on Tractor
        """
        # if crindsim.commercial returns true sale did not go inside for completion
        if crindsim.commercial(selection = "both", tractor_target_type = "money", tractor_target_amount = "16.00"):
            tc_fail("Transaction completed at the CRIND should have gone inside")
        if not self.inside():
            tc_fail("Overrun error message is not displayed at the POS")

    @test
    def reefer_over_with_tractor(self):
        """
        Tractor to auth, $6 Overrun on Reefer
        """
        # if crindsim.commercial returns true sale did not go inside for completion
        if crindsim.commercial(selection = "both", reefer_target_type = "money", reefer_target_amount = "16.00"):
            tc_fail("Transaction completed at the CRIND should have gone inside")
        if not self.inside():
            tc_fail("Overrun error message is not displayed at the POS")

    @test
    def tractor_and_reefer_over(self):
        """
        $3 Overrun on Tractor, $3 Overrun on Reefer
        """
        # if crindsim.commercial returns true sale did not go inside for completion
        if crindsim.commercial(selection = "both", tractor_target_type = "money", tractor_target_amount = "13.00", reefer_target_type = "money", reefer_target_amount = "13.00", need_def="yes"):
            tc_fail("Transaction completed at the CRIND should have gone inside")
        if not self.inside():
            tc_fail("Overrun error message is not displayed at the POS")

    @test
    def tractor_over_with_def_and_reefer(self):
        """
        Select Tractor and Reefer with DEF, $6 Overrun on Tractor
        """
        # if crindsim.commercial returns true sale did not go inside for completion
        if crindsim.commercial(selection = "both", need_def = "yes", tractor_target_type = "money", tractor_target_amount = "16.00"):
            tc_fail("Transaction completed at the CRIND should have gone inside")
        if not self.inside():
            tc_fail("Overrun error message is not displayed at the POS")
    
    @test
    def def_over_with_tractor_and_reefer(self):
        """
        Select Tractor and Reefer with DEF, Tractor to auth, $6 Overrun on DEF
        """
        if crindsim.commercial(selection = "both", need_def = "yes", def_target_type = "money", def_target_amount = "16.00"):
            tc_fail("Transaction completed at the CRIND should have gone inside")
        if not self.inside():
            tc_fail("Overrun error message is not displayed at the POS")
    
    @test
    def reefer_over_with_tractor_and_def(self):
        """
        Tractor and DEF to auth, $6 overrun on Reefer
        """
        # if crindsim.commercial returns true sale did not go inside for completion
        if crindsim.commercial(selection = "both", need_def = "yes", reefer_target_type = "money", reefer_target_amount = "16.00"):
            tc_fail("Transaction completed at the CRIND should have gone inside")
        if not self.inside():
            tc_fail("Overrun error message is not displayed at the POS")

    @test
    def tractor_and_def_over_with_reefer(self):
        """
        Select Tractor and Reefer with DEF, $3 Overrun on Tractor, $3 overrun on DEF
        """
        # if crindsim.commercial returns true sale did not go inside for completion
        if crindsim.commercial(selection = "both", need_def = "yes", tractor_target_type = "money", tractor_target_amount = "13.00", def_target_type = "money", def_target_amount = "13.00"):
            tc_fail("Transaction completed at the CRIND should have gone inside")
        if not self.inside():
            tc_fail("Overrun error message is not displayed at the POS")

    @test
    def tractor_and_reefer_over_with_def(self):
        """
        Select Tractor and Reefer with DEF, $3 Overrun on Tractor, DEF to auth, $3 overrun on Reefer
        """
        # if crindsim.commercial returns true sale did not go inside for completion
        if crindsim.commercial(selection = "both", need_def = "yes", tractor_target_type = "money", tractor_target_amount = "13.00", reefer_target_type = "money", reefer_target_amount = "13.00"):
            tc_fail("Transaction completed at the CRIND should have gone inside")
        if not self.inside():
            tc_fail("Overrun error message is not displayed at the POS")

    @test
    def def_and_reefer_over_with_tractor(self):
        """
        Tractor to auth, $3 overrun on DEF, $3 Overrun on Reefer
        """
        # if crindsim.commercial returns true sale did not go inside for completion
        if crindsim.commercial(selection = "both", need_def = "yes", def_target_type = "money", def_target_amount = "13.00", reefer_target_type = "money", reefer_target_amount = "13.00"):
            tc_fail("Transaction completed at the CRIND should have gone inside")
        if not self.inside():
            tc_fail("Overrun error message is not displayed at the POS")

    @test
    def tractor_def_and_reefer_over(self):
        """
        $2 overrun on tractor, $2 overrun on DEF, and $2 overrun on reefer
        """
        # if crindsim.commercial returns true sale did not go inside for completion
        if crindsim.commercial(selection = "both", need_def = "yes", tractor_target_type = "money", tractor_target_amount = "12.00", def_target_type = "money", def_target_amount = "12.00", reefer_target_type = "money", reefer_target_amount = "12.00"):
            tc_fail("Transaction completed at the CRIND should have gone inside")
        if not self.inside():
            tc_fail("Overrun error message is not displayed at the POS")

    @test
    def total_over(self):
        """
        $6 overrun on total limit
        """
        #Sets host limits needed for this transaction
        networksim.set_commercial_fuel_limit(True, '019', 20)
        networksim.set_commercial_fuel_limit(True, '032', 20)
        networksim.set_commercial_fuel_limit(True, '062', 20)
        # if crindsim.commercial returns true sale did not go inside for completion
        if crindsim.commercial(selection = "both", need_def = "yes", reefer_target_type = "money", reefer_target_amount = "16.00"):
            tc_fail("Transaction completed at the CRIND should have gone inside")
        if not self.inside():
            tc_fail("Overrun error message is not displayed at the POS")

    @test
    def retail_over(self):
        """
        $6 overrun on retail dispenser
        """
        pos.close()
        fc1 = forecourt_installation.ForecourtInstallation()
        mws.click("Set Up")
        fc1.change(item = "1", tab = "Dispensers", config = {"Commercial Diesel": False})
        mws.click_toolbar("Save")
        mws.click_toolbar("Save")
        #Restart passport after forecourt config changes
        system.restartpp()
        #Adding sleep to allow crinds to come back online after passport restart
        time.sleep(120)
        #Sets host limit for this transaction
        networksim.set_commercial_fuel_limit(True, '019', 50)
        pos.connect()
        pos.sign_on()
        #crind_sale performs certain actions (needed for this case) when crindsim is in manual mode
        crindsim.set_mode("manual")
        # if crindsim.commercial returns true sale did not go inside for completion
        if crindsim.crind_sale(card_name = "NGFC", brand = "Exxon", target_type = "money", target_amount = "56.00"):
            tc_fail("Transaction completed at the CRIND should have gone inside")
        system.wait_for(lambda: "insert card" in crindsim.get_display_text().lower(), timeout = 30)
        pos.select_dispenser(1)
        #Verify error message is displayed on POS
        if "overran" not in pos.read_dispenser_diag()["Errors"].lower():
            #Complete sale before failing to avoid cascading failures
            pos.click_fuel_buffer("A")
            pos.pay()
            tc_fail("Overrun error message is not displayed at the POS")
        pos.click("Clear Errors")
        pos.click_fuel_buffer("A")
        pos.pay()

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        pos.close()
        networksim.set_commercial_fuel_limit_send_mode("Fuel Product Configuration Based", 50, False)
        networksim.set_commercial_fuel_limit(False, '019', 50)
        networksim.set_commercial_fuel_limit(False, '032', 50)
        networksim.set_commercial_fuel_limit(False, '062', 50)

    def inside(self):
        system.wait_for(lambda: "insert card" in crindsim.get_display_text().lower(), timeout = 30)
        pos.select_dispenser(1)
        #Verify error message is displayed on POS
        if "overran" not in pos.read_dispenser_diag()["Errors"].lower():
            #Complete sale before failing to avoid cascading failures
            pos.click_fuel_buffer("commercial")
            pos.pay()
            return False
        pos.click("Clear Errors")
        pos.click_fuel_buffer("commercial")
        pos.pay()
        return True
