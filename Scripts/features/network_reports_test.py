"""
    File name: network_reports_test.py
    Tags:
    Description: 
    Author: 
    Date created: 2020-01-27 14:59:46
    Date last modified: 
    Python Version: 3.7
"""

import logging, time, datetime
from app import Navi, mws, pos, system
from app.features import reports, period_maint, store_close
from app.framework.tc_helpers import setup, test, teardown, tc_fail



log = logging.getLogger()

class network_reports_test():
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
        self.timenow = datetime.datetime.now() 
        self.date = self.timenow.strftime("%m/%d/%Y")
    
    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        """
        
        mws.sign_on()
        st = store_close.StoreClose()
        st
        st.begin_store_close(timeout=15*60)

 
    @test   
    def Connexusreports(self):
        """Tests whether the  Mobile payment reports can be opened
        Args: None
        Returns: None
        """
        
        if not  reports.ReportMenu("Network").get_report("Configuration Report","Stuzo"):
            log.warning(f"Failed oppening Configuration Report.")
        mws.click_toolbar("exit",timeout=15)   
        mws.click_toolbar("cancel",timeout=15)
        mws.click_toolbar("cancel")

    @test
    def Auxiliaryreports(self):
        """Tests whether the Auxiliary Networks reports can be opened
        Args: None
        Returns: None
        """
            
        if not  reports.ReportMenu("Network").get_report("Sales reports by shift","Auxiliary Network",date = self.date):
            log.warning(f"Failed oppening Site Configuration.")
        mws.click_toolbar("exit",timeout=15)
        mws.click_toolbar("cancel",timeout=15)
        mws.click_toolbar("cancel")    
    @test
    def GS1Couponreports(self):
        """Tests whether the GS1 Coupon Network Networks reports can be opened
        Args: None
        Returns: None
        """
            
        if not  reports.ReportMenu("Network").get_report("Manufacturer Coupon Transaction Detail Report","GS1 Coupon Network",date = self.date):
            log.warning(f"Failed oppening Manufacturer Coupon Transaction Detail Report.")
        mws.click_toolbar("exit",timeout=15)
        mws.click_toolbar("cancel",timeout=15)
        mws.click_toolbar("cancel")
    
    @test
    def Incommreports(self):
        """Tests whether the Incomm Networks reports can be opened
        Args: None
        Returns: None
        """
            
        if not  reports.ReportMenu("Network").get_report("Account Transaction By Day","InComm",date = self.date):
            log.warning(f"Failed oppening Account Transaction By Day.")
        mws.click_toolbar("exit",timeout=15)
        mws.click_toolbar("cancel",timeout=15)
        mws.click_toolbar("cancel")
    
    @test
    def MobilepayFDCreports(self):
        """Tests whether the Mobile Pay FDC Networks reports can be opened
        Args: None
        Returns: None
        """
            
        if not  reports.ReportMenu("Network").get_report("Configuration Report","Mobile Pay FDC"):
            log.warning(f"Failed oppening Configuration Report.")
        mws.click_toolbar("exit",timeout=15)
        mws.click_toolbar("cancel",timeout=15)
        mws.click_toolbar("cancel")
    
    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        pass
