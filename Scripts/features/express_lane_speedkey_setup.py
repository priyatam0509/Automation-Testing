"""
    File name: express_lane_speedkey_setup.py
    Tags:
    Description: This script tests the ability to set up speedkeys for Express Lane.
    Author: Christopher Haynes
    Date created: 2019-10-21 
    Date last modified: 
    Python Version: 3.7
"""

import logging, time
from app import mws, checkout, item, register_grp_maint, key_maint
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class express_lane_speedkey_setup():
    """
    Description: Testing the ability to configure speedkeys for Express Lane.
    """

    def __init__(self):
        """
        Description:
                Initializes the express_lane_speedkey_setup class.
        Args:
                None
        Returns:
                None
        """
        # The logging object.
        # Example: self.log.info(f"Current value of var: {my_var}")
        self.log = logging.getLogger()
        self.max_items = 9 # The maximum number of items to display on Express lane
        self.plu_starting_point = 1000 # The PLU to start after when making new items

    @setup
    def setup(self):
        """
        Description:
                Performs any initialization that is not default.
        Args:
                None
        Returns:
                None
        """

        self.log.info("Establishing a common speedkey menu starting point.")
        keys = key_maint.SpeedKeyMaintenance()
        speedkeymenus = mws.get_value("Results")
        for menu in speedkeymenus:
            if menu == "Test":
                keys.delete_menu("Test")
        keys.add_menu("Test")
        mws.click_toolbar("Exit", main = True)

        self.log.info("Setting the speedkey menu for the register group.")
        reg = register_grp_maint.RegisterGroupMaintenance()
        config = {
                    "General": {"Primary Speed Key Menu": "Test"}
                 }
        reg.change("POSGroup2", config)
        mws.click_toolbar("Exit", main = True)

    @test
    def check_speedkey_setup_1(self):
        """
        Description:
                Checks for the presence of the correct Speedkeys in Express Lane.  This automates M-90838.
        Args: 
                None
        Returns: 
                None
        """
        self.log.info("Beginning speedkey test.")
        num = 0
        while num < self.max_items:
            num = num + 1
            # Creates an item for the speedkey
            self.log.info("Adding Item PLU {} for use in a speedkey.".format(num + self.plu_starting_point))
            items = item.Item()
            new_item = {
                            "General": {
                                "PLU/UPC": "{}".format(num + self.plu_starting_point),
                                "Description": "Item {}".format(num),
                                "Department": "Dept 1",
                                "Item Type": "Regular Item",
                                "Receipt Desc": "Item {}".format(num),
                                "per unit": "100"
                            },
                            "Options": {
                                "Return Price": "100"
                            }
                        
                        }
            items.add(new_item, overwrite = True)
        mws.click_toolbar("Exit", main = True)

        num = 0
        while num < self.max_items:
            num = num + 1
            # Creates a speedkey
            self.log.info("Creating a speedkey for Item {}.".format(num))
            keys = key_maint.SpeedKeyMaintenance()
            keys.change_menu("Test")
            keys = key_maint.SpeedKeyMaintenance() #This is a workaround to refresh SpeedKeyMaintenance.keys with the correct content.
            keys.add(
                        num, # position
                        "{}".format(num + self.plu_starting_point), # department code
                        "Item {}".format(num), # button text (caption)
                        "banana.bmp" # button icon 
                    )
            mws.click_toolbar("Save")
        mws.click_toolbar("Exit")

        self.log.info("Checking that all {} speedkeys are present.".format(self.max_items))
        if not checkout.connect():
            tc_fail("Couldn't connect to Express Lane.")

        #waiting for express lane to come up
        while checkout._is_element_present("//div[@id='disabled_screen']"):
            time.sleep(1)

        #ensuring the welcome screen is not in the way
        if checkout._is_element_present("//div[@id = 'welcomescreen']"):
            checkout.click_welcome_key("Start")

        num = 0
        while num < self.max_items:
            num = num + 1
            if not checkout._is_element_present("//div[@id = \"speed_key_{}\"]".format(num)):
                tc_fail("The speedkey for Item {} was not found.".format(num))

        #checks that the images on the speedkeys are drawn from the correct location.
        if not checkout._is_element_present("//div[@style= \"background-image: url('images/speedkeys/banana.png');\"]"):
            tc_fail("The correct image was not displayed for any speedkey.")

        checkout.close()

    @teardown
    def teardown(self):
        """
        Description:
                Performs cleanup after this script ends.
        Args:
                None
        Returns:
                None
        """
        self.log.info("Reverting the speedkey menu for the register group.")
        reg = register_grp_maint.RegisterGroupMaintenance()
        config = {
                   "General": {"Primary Speed Key Menu": "Default"}
                }
        reg.change("POSGroup2", config)
        mws.click_toolbar("Exit", main = True)
        

