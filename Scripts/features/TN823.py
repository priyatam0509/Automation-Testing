"""
    File name: TN-823.py
    Tags:
    Description: Commercial Diesel sales
    Author: Kevin Walker
    Date created: 2020-05-26 11:22:57
    Date last modified:
    Python Version: 3.7
"""

import logging, time
from app import Navi, mws, pos, system, crindsim, forecourt_installation
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class TN823():
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
        fc.delete_last("Tanks")
        fc.delete_last("Tanks")
        fc.delete_last("Tanks")
        fc.add(tab = "Tanks", config = {"Capacity" : "8000", "Product Top" : "Diesel 1"})
        fc.add(tab = "Tanks", config = {"Capacity" : "8000", "Product Top" : "Diesel 2"})
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


    @test
    def tractor_diesel_1(self):
        """
        Verify Diesel 1 can be fueled
        """
        
        if self.commercial_sale():
            receipt = crindsim.get_receipt()
            self.log.info(receipt)
            #Verify Diesel 1 printed on receipt
            if "Diesel 1" in receipt:
                pass
            else:
                tc_fail("Diesel 1 was not printed on the receipt")
        else:
            tc_fail("Transaction did not complete successfully")

    @test
    def tractor_diesel_2(self):
        """
        Verify Diesel 2 can be fueled
        """
        
        if self.commercial_sale(tractor_grade = 2):
            receipt = crindsim.get_receipt()
            self.log.info(receipt)
            #Verify Diesel 2 printed on receipt
            if "Diesel 2" in receipt:
                pass
            else:
                tc_fail("Diesel 2 was not printed on the receipt")
        else:
            tc_fail("Transaction did not complete successfully")


    @test
    def diesel_1_with_def(self):
        """
        Verify tractor and def can be fueled
        """
        if self.commercial_sale(need_def = True):
            receipt = crindsim.get_receipt()
            self.log.info(receipt)
            #Verify Diesel 1 printed on receipt
            if "Diesel 1" in receipt:
                #Verify Def is printed on receipt
                if "DEF" in receipt in receipt:
                    pass
                else:
                    tc_fail("DEF was not printed on the receipt")
            else:
                tc_fail("Diesel 1 was not printed on the receipt")
        else:
            tc_fail("Transaction did not complete successfully")

    @test
    def diesel_2_with_def(self):
        """
        Verify Diesel 2 with DEF can be fueled
        """
        if self.commercial_sale(need_def = True, tractor_grade = 2):
            receipt = crindsim.get_receipt()
            self.log.info(receipt)
            #Verify Diesel 2 printed on receipt
            if "Diesel 2" in receipt:
                #Verify DEF printed on receipt
                if "DEF" in receipt in receipt:
                    pass
                else:
                    tc_fail("DEF was not printed on the receipt")
            else:
                tc_fail("Diesel 2 was not printed on the receipt")
        else:
            tc_fail("Transaction did not complete successfully")

    @test
    def reefer(self):
        """
        Verify reefer can be fueled
        """
        
        if self.commercial_sale(selection = "Reefer"):
            receipt = crindsim.get_receipt()
            self.log.info(receipt)
            #Verify RD Dsl 1 is printed on the receipt
            if "RD Dsl 1" in receipt:
                pass
            else:
                tc_fail("RD Dsl 1 was not printed on the receipt")
        else:
            tc_fail("Transaction did not complete successfully")

    
    @test
    def reefer_with_def(self):
        """
        Verify reefer and def can be fueled
        """
        if self.commercial_sale(selection = "Reefer", need_def = True):
            receipt = crindsim.get_receipt()
            self.log.info(receipt)
            #Verify RD Dsl 1 can be printed on the receipt
            if "RD Dsl 1" in receipt:
                #Verify DEF printed on the receipt
                if "DEF" in receipt in receipt:
                    pass
                else:
                    tc_fail("DEF was not printed on the receipt")
            else:
                tc_fail("RD Dsl 1 was not printed on the receipt")
        else:
            tc_fail("Transaction did not complete successfully")

    @test
    def diesel_1_with_reefer(self):
        """
        Verify diesel 1 and reefer can be fueled
        """
        if self.commercial_sale(selection = "Both"):
            receipt = crindsim.get_receipt()
            self.log.info(receipt)
            #Verify Diesel 1 is printed on the receipt
            if "Diesel 1" in receipt:
                #Verify RD Dsl 1 is printed on the receipt
                if "RD Dsl 1" in receipt:
                    pass
                else:
                    tc_fail("RD Dsl 1 was not printed on the receipt")
            else:
                tc_fail("Diesel 1 was not printed on the receipt")
        else:
            tc_fail("Transaction did not complete successfully")

    @test
    def diesel_2_with_reefer(self):
        """
        Verify diesel 2 and reefer can be fueled
        """
        if self.commercial_sale(selection = "Both", tractor_grade = 2):
            receipt = crindsim.get_receipt()
            self.log.info(receipt)
            #Verify Diesel 2 is printed on the receipt
            if "Diesel 2" in receipt:
                #Verify RD Dsl 1 is printed on the receipt
                if "RD Dsl 1" in receipt:
                    pass
                else:
                    tc_fail("RD Dsl 1 was not printed on the receipt")
            else:
                tc_fail("Diesel 2 was not printed on the receipt")
        else:
            tc_fail("Transaction did not complete successfully")

    @test
    def tractor_reefer_and_def(self):
        """
        Verify tractor, reefer, and def can be fueled
        """
        if self.commercial_sale(selection = "Both", need_def = True):
            receipt = crindsim.get_receipt()
            self.log.info(receipt)
            #Verify Diesel 1 is printed on the receipt
            if "Diesel 1" in receipt:
                #Verify RD Dsl 1 is printed on the receipt
                if "RD Dsl 1" in receipt:
                    #Verify DEF is printed on the receipt
                    if "DEF" in receipt in receipt:
                        pass
                    else:
                        tc_fail("DEF was not printed on the receipt")
                else:
                    tc_fail("RD Dsl 1 was not printed on the receipt")
            else:
                tc_fail("Diesel 1 was not printed on the receipt")
        else:
            tc_fail("Transaction did not complete successfully")
    
    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        pass

    # Handler Functions
    def commercial_sale(self, tractor_grade = 1, reefer_grade = 1, selection = "Tractor", need_def = False):
        #Put crind sim in manual mode
        crindsim.set_mode("Manual")
        #Set sales target to $15.00 since dispensing multiple grades can reach preauth limit
        crindsim.set_sales_target("money", "15.00")
        start_time = time.time()
        timeout = 60
        prompt_timeout = 10
        # Loop verifies that crindsim is in idle state before starting transaction
        while time.time() - start_time < timeout:
            if "insert" in crindsim.get_display_text().lower():
                self.log.info("Swiping card")
                crindsim.swipe_card(brand = "Exxon", card_name = "NGFC")
                break
        else:
            self.log.info("CRIND did not return to idle, transaction could not be started")
            return False
        #Make selection (Tractor, Reefer, Both)
        system.wait_for(lambda: "selection" in crindsim.get_display_text().lower(), timeout = prompt_timeout)
        self.log.info("Pressing " + selection)
        crindsim.press_softkey(selection)
        system.wait_for(lambda: "def?" in crindsim.get_display_text().lower(), timeout = prompt_timeout)
        #Answer def prompt
        if need_def:
            self.log.info("Pressing Yes for Need DEF?")
            crindsim.press_softkey("Yes")
        else:
            self.log.info("Pressing No for Need DEF?")
            crindsim.press_softkey("No")
        #Prompt if Additional Products enabled on host sim
        if system.wait_for(lambda: "additional" in crindsim.get_display_text().lower(), timeout = prompt_timeout, verify = False):
            self.log.info("Pressing no for additional products")
            crindsim.press_softkey("No")
        #Answer car wash prompt with No
        system.wait_for(lambda: "carwash" in crindsim.get_display_text().lower(), timeout = prompt_timeout)
        self.log.info("Pressing No for Carwash")
        crindsim.press_softkey("No")
        system.wait_for(lambda: "lift" in crindsim.get_display_text().lower(), timeout = prompt_timeout)
        #Fuel tractor if tractor selected
        if selection == "Tractor":
            self.log.info("Fueling Tractor")
            self.log.info(f"Selecting grade: {tractor_grade}")
            fuel(tractor_grade)
            #Fuel def if def was selected
            if need_def:
                system.wait_for(lambda: "lift" in crindsim.get_display_text().lower(), timeout = prompt_timeout)
                self.log.info("Fueling DEF")
                fuel(3)
        #Fuel reefer if reefer is selected        
        elif selection == "Reefer":
            #Fuel def if def is selected
            if need_def:
                self.log.info("Fueling DEF")
                fuel(3)
            system.wait_for(lambda: "lift" in crindsim.get_display_text().lower(), timeout = prompt_timeout)
            self.log.info("Fueling Reefer")
            self.log.info(f"Selecting grade: {reefer_grade}")
            fuel(reefer_grade)
        #Fuel tractor and reefer if both is selected
        else:
            self.log.info("Fueling Tractor")
            self.log.info(f"Selecting grade: {reefer_grade}")
            fuel(tractor_grade)
            #Fuel def if def is selected
            if need_def:
                system.wait_for(lambda: "lift" in crindsim.get_display_text().lower(), timeout = prompt_timeout)
                self.log.info("Fueling DEF")
                fuel(3)
            system.wait_for(lambda: "lift" in crindsim.get_display_text().lower(), timeout = prompt_timeout)
            self.log.info("Fueling Reefer")
            self.log.info(f"Selecting grade: {reefer_grade}")
            fuel(reefer_grade)

        system.wait_for(lambda: "receipt" in crindsim.get_display_text().lower(), timeout = 30)
        self.log.info("Pressing Yes for Receipt")
        crindsim.press_softkey("Yes")
        system.wait_for(lambda: "thank" in crindsim.get_display_text().lower(), timeout = prompt_timeout)
        return True

def fuel(grade):
    if grade is None:
        grade = 1
    crindsim.select_grade(grade)
    crindsim.lift_handle()
    crindsim.open_nozzle()
    time.sleep(5)
    crindsim.lower_handle()