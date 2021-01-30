from app import mws, system
import logging

from app.features.network.core.fuel_disc_config import FuelDiscountConfiguration as CoreFDC

class FuelDiscountConfiguration(CoreFDC):
    """
    This is a plug class for the non-functional Fuel Discount Configuration feature module for Chevron.
    """
    def __init__(self):
        self.log = logging.getLogger()
        self.log.error("Fuel discount configuration is not supported on Chevron brand.")
    
    @staticmethod
    def navigate_to():
        pass
    
    def change(self, config):
        """
        This function cannot be invoked; Fuel Discount Configuration is not supported.
        """
        pass