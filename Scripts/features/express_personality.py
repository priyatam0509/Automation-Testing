"""
    File name: express_personality.py
    Tags:
    Description: This script tests the ability to change register personalities with Express Lane enabled.
                    This test automates M-90693 and M-90694
    Author: Christopher Haynes
    Date created: 2019-09-18 08:46:30
    Date last modified: 
    Python Version: 3.7
"""

import logging, time
from app import Navi, mws, server, system, checkout, console, register_setup
from app.framework.tc_helpers import setup, test, teardown, tc_fail

class express_personality():
    """
    Description: Test class that provides an interface for testing.
    """

    def __init__(self):
        """Initializes the Template class.
        Args: None
        Returns: None
        """
        # The logging object. 
        self.log = logging.getLogger()
        self.sc = server.server()
        self.pinpad_ip = self.sc.get_site_info()
        self.pinpad_test_ip = self.pinpad_ip['ip']

    @setup
    def setup(self):
        """Performs any initialization that is not default.
        Args: None
        Returns: None
        """

        self.log.info("Ensuring the clients have a consistent starting point.")
        self.free_pinpads()
            
        mws.click_toolbar("Exit", main = True)

    @test
    def switch_clients_1(self):
        """Switches the Express Lane and the CCC.
        Args: None
        Returns: None
        """

        self.log.info("Switching POSCLIENT002 to Express Lane")
        self.set_express_lane("3", "POSCLIENT002")
        
        self.log.info("Switching POSCLIENT001 to CCC")
        self.set_ccc("2", "POSCLIENT001")
            
        mws.click_toolbar("Exit", main = True)

        self.log.info("Setting the Express Lane Client to lane 1.")
        self.set_lane("POSCLIENT002")

        # Restart Passport
        system.restartpp()
        time.sleep(3)

        self.log.info("Checking to see if POSCLIENT002 is in the correct personality.")
        if not checkout.connect():
            tc_fail("Unable to connect with express lane")
        checkout.close()
        
        self.log.info("Checking to see if POSCLIENT001 is in the correct personality.")
        if not console.connect():
            tc_fail("Unable to connect with cashier control")
        console.close()
        
    @test
    def both_cws_2(self):
        """Switches the Express Lane and CCC to normal CWS.
        Args: None
        Returns: None
        """

        self.log.info("Switching POSCLIENT001 to Cashier Workstation")
        reg = register_setup.RegisterSetup()
        reg.change("2", "POSCLIENT001", {"Personality": "Cashier Workstation"})

        
        self.log.info("Switching POSCLIENT002 to Cashier Workstation")
        reg.change("3", "POSCLIENT002", {"Personality": "Cashier Workstation"})
        
        self.log.info("Checking to see if the clients are in the correct personality.")
        Navi.navigate_to("register set up")

        client001, client002 = self.find_clients()
        if "Cashier Workstation" not in client001 or "Cashier Workstation" not in client002:
            tc_fail("Cashier Workstation personality not successfully saved.")
        mws.click_toolbar("Exit", main = True)

    @test
    def unswitch_clients_3(self):
        """Switches both Clients back to their original personality.
        Args: None
        Returns: None
        """

        self.log.info("Freeing pinpad for reuse.")
        self.free_pinpads()
        
        self.log.info("Switching POSCLIENT001 to Express Lane")
        self.set_express_lane("2", "POSCLIENT001")
        
        self.log.info("Switching POSCLIENT002 to CCC")
        self.set_ccc("3", "POSCLIENT002")
        
        mws.click_toolbar("Exit", main = True)
        
        self.log.info("Setting the Express Lane Client to lane 1.")
        self.set_lane("POSCLIENT001")
        
        self.log.info("Rebooting clients to apply personalities.")
        
        # Restart Passport
        system.restartpp()
        time.sleep(3)

        self.log.info("Checking to see if POSCLIENT002 is in the correct personality.")
        if not checkout.connect():
            tc_fail("Unable to connect with express lane")
        checkout.close()
        
        self.log.info("Checking to see if POSCLIENT001 is in the correct personality.")
        if not console.connect():
            tc_fail("Unable to connect with cashier control")
        console.close()

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        pass

# #####################################################
# ###############   HELPER FUNCTIONS    ###############
# #####################################################

    def set_lane(self, client):
        """Assigns the given client to a lane in express lane maintenance
        Args: client: the client to assign to a lane. (Example: "POSCLIENT001")
        Returns: None
        """
        Navi.navigate_to("Express Lane Maintenance")
        mws.set_value("Express Lane 1", client)
        mws.click_toolbar("Save", main=True)

    def find_clients(self):
        """Finds clients 1 and 2 in the register set up menu.
        This function assumes the site is already in the register set up menu.
        Args: None
        Returns: The strings for POSCLIENT001 and POSCLIENT002 in the register list.
        """
        registers = mws.get_value("Registers")
        client001 = ""
        client002 = ""
        for register in registers:
            if "POSCLIENT001" in register:
                client001 = register
            if "POSCLIENT002" in register:
                client002 = register
        if client001 == "":
            tc_fail("Couldn't find the POSCLIENT001.")
        if client002 == "":
            tc_fail("Couldn't find the POSCLIENT002.")
        return client001, client002
        
    def free_pinpads(self):
        """Sets the pinpads to None.
        Args: None
        Returns: None
        """
        reg = register_setup.RegisterSetup()
        
        client001, client002 = self.find_clients()
        if "Cashier Control Console" not in client001:
            change = {"PIN Pad Type": "None"}
            reg.change("2", "POSCLIENT001", change)
        
        if "Cashier Control Console" not in client002:
            change = {"PIN Pad Type": "None"}
            reg.change("3", "POSCLIENT002", change)

    def set_ccc(self, number, name):
        """Changes a given client to a ccc personality.
        Args: number: the number of the register to change
              name: the client to change the personality of.
        Returns: None
        """
        reg = register_setup.RegisterSetup()
        changes = {"Personality": "Cashier Control Console",
                   "Scanner Type": "TCP/IP Connection",
                   "Scanner IP": "10.5.48.2"}
        reg.change(number, name, changes)
           
    def set_express_lane(self, number, name):
        """Changes a given client to an express lane personality.
        Args: number: the number of the register to change
              name: the client to change the personality of.
        Returns: None
        """
        reg = register_setup.RegisterSetup()
        changes = {"Personality": "Express Lane",
                   "Scanner Type": "TCP/IP Connection",
                   "Scanner IP": "10.5.48.2"}
        reg.change(number, name, changes)
        changes = {
                    "PIN Pad Type": "Verifone MX 915",
                   "Connection": "TCP/IP",
                   "IP Address": self.pinpad_test_ip,
                   "Contactless": True,
                    "EMV Capable": True
        }
        reg.change(number, name, changes)