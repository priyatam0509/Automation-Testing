from app import Navi

from app.features.network.core.network_site_config import NetworkSetup as CoreNetworkSetup

class NetworkSetup(CoreNetworkSetup):
    """
    The class extends general NetworkSiteConfiguration class.
    This class is specific to Concord brand.
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