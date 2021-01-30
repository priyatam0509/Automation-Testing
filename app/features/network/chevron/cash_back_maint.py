from app import system, mws, Navi

class CashBackMaintenance():
    """
    This is a plug class for the non-functional Cash Back Maintenance feature module for Chevron.
    """
    @staticmethod
    def navigate_to(self):
        """
        Navigates to the Cash Back Maintenance module.
        """
        return Navi.navigate_to("cash back maintenance")