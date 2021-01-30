"""
    File name: PEACOCK_4161.py
    Brand: CITGO
    Description: [PEACOCK-4161] This will verify Remove Double DataCollect logic 
                only for Citgo
    Author: Asha Sangrame
    Date created: 2020-07-28 12:53:24
    Date last modified:
    Python Version: 3.7
"""


import logging, time
from app import Navi, pos, system
from app import networksim, crindsim
from app.framework import EDH
from app.framework.tc_helpers import setup, test, teardown, tc_fail


class PEACOCK_4161():
    """
    Description: Test class that provides an interface for testing.
    """
    def __init__(self):
        """Initializes the Template class.
        Args: None
        Returns: None
        """
        # The logging object. 
        # Example: self.log.info(f"Current value of var: {my_var}")
        self.log = logging.getLogger()

        self.fuel_amount = "$1.00"
        self.fuel_grade = "Diesel 1"  

        # Create EDH object
        self.edh = EDH.EDH()  

    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        # Navigate to POS
        Navi.navigate_to("POS")  

    def fetch_network_message(self, last_id):
        """
        This is helper method to fetch required network messages from EDH
        """
        output_list = []
        
        # only fetch 2 network messages
        counter = 0
        messages = self.edh.get_network_messages(amount="20", start_in=last_id)
        for message in messages:
            if "Outgoing queue sequence" in message:
                message_to_find = message.split()
                output_list.append(message_to_find[11])
                counter = counter + 1
                if counter == 2:
                    break

        return output_list
    
    @test
    def TC01(self):
        """
        Zephyr Id : This will Verify that Double Data Collect Message Code 39 
                    is not displayed on Host Sim  when perform credit card 
                    transaction with host sim in offline mode  
        Args: None
        Returns: None
        """        
        # Put network sim on offline mode
        networksim.stop_simulator()
        time.sleep(5)

        # fetch last networkmessage id
        last_id = self.edh.get_last_msg_id(pspid="24")
        
        # Perform first credit card transaction with offline Host sim mode
        # Add Dry Stock Item
        pos.add_item("002", method="PLU")
        
        # Perform card Payment with Visa card
        pos.pay_card()
        
        # Perform second credit card transaction with offline Host sim mode
        # Add fuel in prepay mode
        pos.add_fuel(self.fuel_amount, grade=self.fuel_grade)
        
        # Perform card Payment with Visa Card
        pos.pay_card()
        
        # Wait until dispenser 1 is idle
        if not pos.wait_for_disp_status('IDLE'):
            return False

        # put networksim on online code
        networksim.start_simulator()

        # wait some time to send response to EDH
        time.sleep(5)

        output_list = self.fetch_network_message(last_id)

        for element in output_list:
            if "P02" not in element:
                tc_fail("Required Double Data collect message code not found")

        return True

    @test
    def TC02(self):
        """
        Zephyr Id : This will Verify that Double Data Collect Message Code 
                    '02' is displayed on performing dry stock and manual fuel
                    sale transaction in offline host sim mode
        Args: None
        Returns: None
        """        
        # Put network sim on offline mode
        networksim.stop_simulator()
        time.sleep(5)

        # fetch last networkmessage id
        last_id = self.edh.get_last_msg_id(pspid="24")
        
        # First transaction in offline mode
        # Add Dry Stock Item
        pos.add_item("002", method="PLU")
        
        # Perform card Payment with Mastercard
        pos.pay_card(card_name="MasterCard")
        
        # Second transaction in offline mode
        # Add fuel in prepay mode
        pos.add_fuel(self.fuel_amount, mode="manual", grade=self.fuel_grade)
        
        # Perform card Payment with Visa Card
        pos.pay_card()
        
        # put networksim on online code
        networksim.start_simulator()

        # wait some time to send response to EDH
        time.sleep(5)

        output_list = self.fetch_network_message(last_id)

        for element in output_list:
            if "P02" not in element:
                tc_fail("Double Data collect message code not found")

        return True
    
    @test
    def TC03(self):
        """
        Zephyr Id : This will Verify that Double Data Collect Message Code 
                    02 is displayed on performing outside crind sale 
                    transaction on offline host sim
        Args: None
        Returns: None
        """        
        # Put network sim on offline mode
        networksim.stop_simulator()
        time.sleep(5)

        # fetch last networkmessage id
        last_id = self.edh.get_last_msg_id(pspid="24")
        
        # Perform crind sale with citgo reward card
        crindsim.crind_sale(brand=system.get_brand(), card_name="Citgo_Rewards", carwash="no")
        
        # Perform crind sale with citgo reward card
        crindsim.crind_sale()
                
        # put networksim on online code
        networksim.start_simulator()

        # wait some time to send response to EDH
        time.sleep(5)

        output_list = self.fetch_network_message(last_id)

        for element in output_list:
            if "P02" not in element:
                tc_fail("Required Double Data collect message code not found")

        return True

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        pass