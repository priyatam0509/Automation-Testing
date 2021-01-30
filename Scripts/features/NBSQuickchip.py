"""
    File name: NBSQuickchip.py
    Tags:
    Description: 
    Author: 
    Date created: 2020-07-22 09:56:47
    Date last modified: 
    Python Version: 3.7
"""

import logging, time
from app import Navi, mws, system, pos, pinpad,crindsim
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app.framework import EDH
from app.features import register_setup
from app.features.network.nbs import pdl
from app import runas
from app import OCR


class NBSQuickchip():
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
            
        pdl.EMVPDLDownload()
        mws.click_toolbar("YES",timeout=10)
        mws.click_toolbar("exit",timeout=10)        
    
    @test
    def EMVconfigurationtab(self):
        """
        Validate that EMV Configuration tab is present

        """
          # Navigating to network site configuration 
        Navi.navigate_to("Site Configuration")
        # Navigating to EMV parameters tab (Indoor)   
        if not mws.select_tab("EMV Configuration"):
            tc_fail("not able to Select tab EMV Parameters")
        mws.click_toolbar("save",timeout=10)   


    @test
    def is_emv_quickchip_enabled(self):

        "Validate that Quickchip is enabled"

        cmd = "select QuickchipEnabled from NBS_EMVParameters where Outdoor = 0" 
        output = runas.run_sqlcmd(cmd, cmdshell=False)['output']
        output_list = output.split("\n")
        output_list = output_list[2:-3]
        self.log.info(f"query result {output_list}")
        if '0' in output_list:
            self.log.error(output)
            tc_fail("Quickchip Disabled")
        if '0 rows affected' in output:

            tc_fail("No EMV Download")

            
    @test
    def EMVtrx(self):
        """
        EMV transaction
        Args: None
        Returns: None
        """
        Navi.navigate_to("POS")        
        pos.sign_on()        
        pos.wait_disp_ready()
        pos.add_item("Generic Item", method="Speedkey", price="500")
        pos.pay_card(card_name="EMVVisaCredit")

    @test
    def magstripetrx(self):
        """
        magstripe approval transaction
        Args: None
        Returns: None
        """
        Navi.navigate_to("POS")        
        pos.sign_on()        
        pos.wait_disp_ready()
        pos.add_item("Generic Item", method="Speedkey", price="500")
        pos.pay_card(card_name="Visa")
    
    @test
    def Outsidetransaction(self):
        """
        outside transaction
        Args: None
        Returns: None
        """
        iddle_status='Pay here Insert card or Pay inside Lift handle'
        crind_status=crindsim.get_display_text(dispenser=1)
        if crind_status not in  iddle_status:
            tc_fail("Failed while checking Crind status.")

        crindsim.set_mode("auto")
        crindsim.set_sales_target("random")
        #Iniciate outside trnsaction
        if not crindsim.crind_sale(card_name="Visa",debit="no",dispenser=1,receipt="yes"):
            tc_fail("Failed while configuring Mobile Payment Config menu a second time.")
        
        self.log.debug("Waiting for fueling")
        if not pos.wait_for_fuel(timeout=120):
            tc_fail(f"Failed while checking Crind ending trx.")


    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        pass
