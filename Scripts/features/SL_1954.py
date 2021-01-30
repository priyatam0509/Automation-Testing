"""
    File name: SL_1954.py
    Tags:
    Description: Option to enable/disable voyager workaround on HPSD
    Author: V.Yaswanth
    Date created: 2020-10-24 14:37:13
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import Navi, mws
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class SL_1954():
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
        """Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        #Navigating to Global Info Editor
        if not Navi.navigate_to("Global Info Editor"):
            return False

        #Selecting Site Configuration Tab
        if not mws.select_tab("Site Configuration"):
            return False

    @test
    def TC01(self):
        """ 
        Description : To verify a new option is present in Site Configuration tab> Global Info Editor
        Args: None
        Returns: None
        """

        #Checking wether new field Allow Unsupported Chip Card As Magstripe Outside is present or not
        if not mws.find_text_ocr("Allow Unsupported Chip Card As Magstripe Outside"):
            tc_fail(f"New field Allow Unsupported Chip Card As Magstripe Outside is not present")
        
        return True
    
    @test
    def TC02(self):
        """ 
        Description : To verify the default value for new option when Site Configuration tab is opened for the first time
        Args: None
        Returns: None
        """
        
        #Checking wether default value of the field is Yes
        if mws.get_value("Allow Unsupported Chip Card")[0] != "Yes":
            tc_fail(f"The default value is not Yes")
        
        return True

    @test
    def TC03(self):
        """ 
        Description : To verify the message when clicked on dropdown icon for new option
        Args: None
        Returns: None
        """
       
        #Clicking dropdown
        if not mws.click("Allow Unsupported Chip Card"):
            tc_fail("Unable to click on Drop down button")

        #Checking top bar text
        if mws.get_top_bar_text() != "Allow unsupported chip card to be processed as swipe entry method on outside terminal":
            tc_fail(f"The top bar text is mismatched")
        
        return True
        
    @test
    def TC04(self):
        """ 
        Description : To verify the dropdown values for new option which is present in Site Configuration tab
        Args: None
        Returns: None
        """

        values = mws.get_value("Allow Unsupported Chip Card")
        if values[1]!="Yes" and values[2]!="No":
            tc_fail(f"There were values other than Yes and No")
        
        return True

    @test
    def TC05(self):
        """ 
        Description : To verify the changed value is not saved when clicked on Cancel button>No
        Args: None
        Returns: None
        """
        
        #Changing value of field to No
        if not mws.set_value("Allow Unsupported Chip Card","No"):
            tc_fail("Unable to set value")

        #clicking cancel button
        if not mws.click_toolbar("Cancel"):
            tc_fail("Unable to click on cancel button")

        #checking confirmation message
        if mws.get_top_bar_text()!="Do you want to save changes?":
            tc_fail(f"The confirmation message is different from Do you want to save changes?")

        #Clicking No button
        if not mws.click_toolbar("No"):
            tc_fail("Unable to click on No button")

        #Navigating to Global Info Editor
        if not Navi.navigate_to("Global Info Editor"):
            tc_fail("Unable to naviagte to page")

        #Selecting Site Configuration Tab
        if not mws.select_tab("Site Configuration"):
            tc_fail("Unable to select tab")

        #Checking wether the value changed is saved or not
        if mws.get_value("Allow Unsupported Chip Card")[0] != "Yes":
            tc_fail("The value in database is not Yes")

        return True

    @test
    def TC06(self):
        """ 
        Description : To verify the user is able to change value from YES to NO and save it 
        Args: None
        Returns: None
        """
        
        #Changing value of field to No
        if not mws.set_value("Allow Unsupported Chip Card","No"):
            tc_fail("Unable to set value")

        #clicking Save button
        if not mws.click_toolbar("Save"):
            tc_fail("Unable to click on Save button")
   
        #Navigating to Global Info Editor
        if not Navi.navigate_to("Global Info Editor"):
            tc_fail("Unable to naviagte to page")

        #Selecting Site Configuration Tab
        if not mws.select_tab("Site Configuration"):
            tc_fail("Unable to select tab")

        #Checking wether the value changed is saved or not
        if mws.get_value("Allow Unsupported Chip Card")[0]!="No":
            tc_fail("The value in database is not No")
        
        return True

    @test
    def TC07(self):
        """ 
        Description : To verify the user is able to change value from NO to YES and save it 
        Args: None
        Returns: None
        """

        #Changing value of field to Yes
        if not mws.set_value("Allow Unsupported Chip Card","Yes"):
            tc_fail("Unable to set value")

        #clicking cancel button
        if not mws.click_toolbar("Cancel"):
            tc_fail("Unable to click on cancel button")

        #checking confirmation message
        if mws.get_top_bar_text()!="Do you want to save changes?":
            tc_fail(f"The confirmation message is different from Do you want to save changes?")

        #Clicking Yes button
        if not mws.click_toolbar("Yes"):
            tc_fail("Unable to click on yes button")

        #Navigating to Global Info Editor
        if not Navi.navigate_to("Global Info Editor"):
            tc_fail("Unable to naviagte to page")

        #Selecting Site Configuration Tab
        if not mws.select_tab("Site Configuration"):
            tc_fail("Unable to select tab")

        #Checking wether the value changed is saved or not
        if mws.get_value("Allow Unsupported Chip Card")[0]!="Yes":
            tc_fail("The value is not Yes")
        
        return True

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """

        #clicking cancel button
        if not mws.click_toolbar("Cancel"):
            return False

        #Clicking Yes button
        if not mws.click_toolbar("Yes"):
            return False
