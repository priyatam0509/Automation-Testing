import logging

from app.features.network.core.fuel_disc_config import FuelDiscountConfiguration as CoreDiscountConfig

class FuelDiscountConfiguration(CoreDiscountConfig):
    """
    The class extends core IFuelDiscountConfiguration class.
    This class is specific to NBS brand.

    The Fuel Discount Configuration menu is unsupported on NBS,
    so the the class overrides them to return warning message
    and return False.
    """
    def __init__(self):
        self.log = logging.getLogger()
        self.log.error("Fuel Discount Configuration module is not available on NBS.")

    @staticmethod
    def navigate_to():
        pass

    def change(self, config):
        self.log.warning("NBS does not support Fuel Discount Configuration. Configuration is not available.")
        return False