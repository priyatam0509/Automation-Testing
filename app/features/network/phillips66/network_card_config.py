from app import system, mws, Navi

from app.features.network.hps_dallas.network_card_config import NetworkCardConfiguration as DallasNCC

class NetworkCardConfiguration(DallasNCC):
    """
    The class extends HPS-Dallas Network Card Configuration class.
    This class is specific to Phillips66 brand.

    The execution is the same as HPS-Dallas, but the name
    of the module is different, so navigation is handled differently.
    """

    @staticmethod
    def navigate_to():
        """
        Navigates to the Card Configuration menu.
        Args:
            None
        Returns:
            Returns nothing because our existence is pointless.
        """
        Navi.navigate_to("Card Configuration")
        mws.connect("Card Info Editor")