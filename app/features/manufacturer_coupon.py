from app.framework import mws, Navi
from app.util import system
import logging

log = logging.getLogger()

class ManufacturerCoupon:

    def __init__(self):
        ManufacturerCoupon.navigate_to()

    @staticmethod
    def navigate_to():
        return Navi.navigate_to("Manufacturer Coupon Configuration")

    def configure(self, config):
        """
        Configure the Manufacturer Coupon Network.

        Args:
            config: The dictionary of values being added.

        Returns:
            True: If the values were successfully set.
            False: If the values could not be set.
        Examples:
            \code
            mc_info = {
                "MainPage":{
                    "Verify Purchase Requirement": 'Yes',
                    "Enabled": 'Yes',
                    "Host Name": 'Host Name',
                    "Host IP Address": '1.2.3.4'
                    "Host IP Port": '5001',
                    "Secondary Host IP Address": '4.3.2.1',
                    "Secondary Host IP Port": '5002',
                    "Retailer ID": '200',
                    "Connection Interval (mins)": '5'
                }
            }
            mc = manufacturer_coupon.ManufacturerCoupon()
            if not mc.configure(mc_info):
                tc_fail("Could not generate report")
            True
            \endcode
        """
        # Set the Enabled field first
        try:
            if not mws.set_value('Enabled', config['Enabled']):
                log.error(f"Could not set {key} with {value}")
                system.takescreenshot()
                return False
        except KeyError:
            pass
                
        # Set all fields other than Enabled
        for key, value in config.items():
            if key == 'Enabled':
                continue
            if not mws.set_value(key, value):
                log.error(f"Could not set {key} with {value}")
                system.takescreenshot()
                mws.recover()
                return False

        try:
            mws.click_toolbar("Save", main = True)
            return True
        except ConnException:
            log.error("Failed to navigate back to Splash Screen")
            error_msg = mws.get_top_bar_text()
            if error_msg is not None:
                log.error(f"Error message: {error_msg}")
                system.takescreenshot()
            return False