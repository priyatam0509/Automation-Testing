"""
    File name: LoyaltyReport_Hierarchy_Check.py
    Tags:
    Story ID : PEACOCK-3804 (EXXON)
    Description: This will verify that loyalty Report have one more filter screen
                 where user can choose loyalty partners for which report need to generated.
    Author: Asha
    Date created: 2020-02-17 13:25
    Date last modified: 
    Python Version: 3.7
"""

import logging, time
from app import mws, Navi
from app.framework.tc_helpers import setup, test, teardown, tc_fail


class LoyaltyReport_Hierarchy_Check():

    def __init__(self):
        """
        Initializes the Template class.
        Args: None
        Returns: None
        """
        self.log = logging.getLogger()

        # Store loyalty list from loyalty interface screen
        Navi.navigate_to("Loyalty Interface")

        self.loyalty_list = mws.get_value("Loyalty Providers")

        if len(self.loyalty_list) == 0:
            self.log.error("No loyalty is configured in loyalty interface")
            return False

        mws.click_toolbar("Exit")
        
    @setup
    def setup(self):
        """
        Initializes the Template class.
        Args: None
        Returns: None
        """
        # Navigate to Loyalty Reports
        Navi.navigate_to("Loyalty Reports")

    @test  
    def hierarchy_check(self):
        """
        Zephyr Id: This will verify that loyalty reports are coming in hierarchy format.
        Args: None
        Returns: None
        """
        self.log.info(f"Loyalty configured are {self.loyalty_list}")

        for item in self.loyalty_list:
            self.log.info(f"Loyalty selected is {item[0]}")

            mws.select("reports1", item[0])
            mws.click_toolbar("Select")
            
            # Fetch all reports
            reports_list = mws.get_value("reports2")

            if (not item[0]+" Loyalty Discount Report" == reports_list[0][0] or 
                not item[0]+" Loyalty Interface Configuration Report" == reports_list[1][0] or 
                not item[0]+" Loyalty Store And Forward Report" == reports_list[2][0] or 
                not item[0]+" Loyalty Transaction Detail Report" == reports_list[3][0]):
                tc_fail("Generic loyalty reports are not present on Screen")

            # one extra report for ExxonMobil
            if item[1] == "ExxonMobil":
                if not item[0]+" Loyalty Usage Report" == reports_list[4][0]:
                    tc_fail("ExxonMobil reports are not present on Screen") 
            
            mws.click_toolbar("Cancel")

            #providing a time delay of 2 sec to sync the events
            time.sleep(2)
                   
        mws.click_toolbar("Cancel")
        return True

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        pass