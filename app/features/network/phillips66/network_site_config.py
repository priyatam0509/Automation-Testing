from app import Navi

from app.features.network.hps_dallas.network_site_config import NetworkSetup as DallasNetworkSetup

class NetworkSetup(DallasNetworkSetup):
    """
    The class extends general NetworkSiteConfiguration class.
    This class is specific to Phillips66 brand.

    The execution is the same as HPS-Dallas, but the name
    of the module is different, so navigation is handled differently.
    """
    @staticmethod
    def navigate_to():
        """
        Navigates to the Global Info Editor menu.
        Args:
            None
        Returns:
            Returns the result of execution of Navi.navigate_to()
        """
        return Navi.navigate_to("Global Info Editor")