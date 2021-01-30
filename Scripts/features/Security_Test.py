"""
    File name: Security_Test.py
    Tags:
    Description: Tests the security camera simulator.
    Author: Nikole Nguyen
    Date created: 2020-05-22 15:08:55
    Date last modified: 
    Python Version: 3.7
"""

import logging
from app import Navi, mws, pos, system
from app.features import security_camera
from app.util import server
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app.simulators import securitysim

# Global Variables
sc = security_camera.SecurityCamera()
scs = securitysim.init_securitysim()

class Security_Test():
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
        # if not system.restore_snapshot():
        #    self.log.debug("No snapshot to restore, if this is not expected please contact automation team")

        ipaddr = server.server.get_site_info()['ip']

        self.log.info("Configuring the security camera.")
        params = { 
            "Data will be set via": "TCP",
            "Data Format":"XML",
            "Host Name": ipaddr,
            "Host Port": '4000',
            "Include forecourt transactions in security camera feed": True,
        }

        if not sc.setup(params):
            self.log.info("Failure in setting up the security camera.")
        
        # Run some transactions.
        Navi.navigate_to("POS")
        pos.sign_on()

        pos.add_item("Item 4")
        pos.add_item("Item 5")
        pos.pay()

    @test
    def get_last(self):
        """
        Retrieve last event
        """
        if "End Sale" not in scs.get_last_event()['payload']:
            tc_fail("Wrong event retrieved.")
            return False
        self.log.info("Event retrieved successfully.")
    
    @test    
    def get_all(self):
        """
        Default: get all events. 
        """
        success = scs.get_all_events()['success']
        result = scs.get_all_events()['payload']
        if not success:
            self.log.info(result)
            tc_fail("Failed retrieval.")
            return False

        if not result:
            tc_fail("List is empty.")
            return False
        self.log.info("Retrieved events successfully.")

    @test
    def get_all_string(self):
        """
        Run toggle, get events to return as string.
        """
        scs.post_toggle({'asLinkedList': False, 'Value': 50})
        if type(scs.get_all_events()['payload']) is not str:
            tc_fail("Did not retrieve a string.")
            return False
        self.log.info("Successfully retrieved a string.")

    @test
    def get_all_list(self):
        """
        Run toggle again, get events to return as list.
        """
        scs.post_toggle({'asLinkedList': True, 'Value': 50})
        if type(scs.get_all_events()['payload']) is not list:
            tc_fail("Did not retrieve a list.")
            return False
        self.log.info("Successfully retrieved a list.")

    @test
    def clear_all(self):
        """
        Clear list.
        """
        if "events cleared" not in scs.get_clear_events()['payload']:
            tc_fail("Events were not successfully cleared.")
            return False
        self.log.info("Successfully cleared list.")

    @test
    def add_after_clear(self):
        """
        Add items after clearing the feed.  
        """
        pos.add_item("Item 4")
        pos.add_item("Item 5")
        pos.add_item("Item 6")
        if "Item 6" not in scs.get_last_event()['payload']:
            tc_fail("Item was not registered in feed.")
            return False
        self.log.info("Successfully added items after clearing.")

    @test
    def clear_max(self):
        """
         Change the maximum number of items before the list is purged, and check if the list purges.
        """
        scs.post_toggle({'asLinkedList': True, 'Value': 3})
        pos.add_item("Item 4")
        pos.add_item("Item 5")
        pos.add_item("Item 6")
        pos.add_item("Item 4")
        if len(scs.get_all_events()['payload']) == 1:
            tc_fail("List was not purged correctly.")
            return False
        self.log.info("List was correctly purged.")
        pos.pay()
    
    @teardown
    def teardown(self):
        """
        Retrieve all events
        """

        pass
