import logging
from app import pos, Navi
from app.features import loyalty

logger = logging.getLogger()

# Helper method.
def rename_loyalty(oldname, loyaltyname, selectname):
    """
    This will rename the loyalty the test wants to select to Kickback.
    Args:
    oldname (str): the previous kickback's original name
    loyaltyname (str): the name of the new kickback
    selectname (str): the original name of the loyalty we wanted to select
    Returns: bool
    """
    # Navigate to Loyalty
    loyalobj = loyalty.LoyaltyInterface()

    old_name = oldname

    old_cfg = {
        "General": {
            "Loyalty Provider Name": oldname,
        }
    }

    new_cfg = {
        "General": {
            "Loyalty Provider Name": 'Kickback',
        }
    }

    loyalobj.change_provider(config=old_cfg, name=loyaltyname)

    loyalobj = loyalty.LoyaltyInterface()

    loyalobj.change_provider(config=new_cfg, name=selectname)

    Navi.navigate_to("POS")
    pos.connect()