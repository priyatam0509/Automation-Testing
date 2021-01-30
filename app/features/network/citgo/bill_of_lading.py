from app import system, mws, Navi
import logging

class BillOfLading :
    """
    The class is a core Bill Of Lading class.
    This class is specific to Citgo brand.
    """

    def __init__(self):
        self.log = logging.getLogger()
        self.navigate_to()
        return

    @staticmethod
    def navigate_to():
        """
        Navigates to the Bill Of Lading menu.
        Args:
            None
        Returns:
            Returns the result of execution of Navi.navigate_to()
        """
        return Navi.navigate_to("Bill Of Lading")

    def change(self, config):
        """
        Changes the configuration of the Bill Of Lading.

        Args:
            config: The dictionary of values being added.

        Returns:
            True: If the values were successfully set.
            False: If the values could not be changed.
            
        Examples:
            /code
            nc_info = {
		        "Product 1" : {
			        "Deliver Date" : "102317",
			        "Bill Of Lading Number" : "345697",
			        "Product Code #1" : "11111111",
			        "Gross Volume for Product #1" : "222222",
			        "Net Volume for Product #1" : "33333"
		        },
		        "Product 2" : {
			        "Product Code #2" : "44444444",
			        "Gross Volume for Product #2" : "555555",
			        "Net Volume for Product #2" : "666666"
		        }
            }
            nc = bill_of_lading.BillOfLading()
            if not nc.add(nc_info):
                tc_fail("Could not add the configuration")
            True
            /endcode
        """
        #Select the card we're configuring
        #Tab ==> {"Product 1", "Product 2"}
        for tab in config:
            if not mws.select_tab(tab=tab):
                self.log.error(f"Could not select tab with the name {tab}.")
                system.takescreenshot()
                return False
            #Key ==> "Deliver Date"
            #Value ==> "102317"
            for key, value in config[tab].items():
                if not mws.set_value(key, value):
                    self.log.error(f"Could not set {key} with {value}")
                    system.takescreenshot()
                    return False
        mws.click_toolbar("Save")
        return True