import winreg
import importlib
import app
import os
import json
import logging

from app.util import constants

from app.framework import results
from app.util import overlay
from app.util import runas
from app.util import system

from app.framework import pytesseract
from app.framework import OCR
from app.framework import mws
from app.util import feature_activate
from app.util import server

from app.simulators import pinpadsim
from app.simulators import networksim
from app.simulators import crindsim
from app.simulators import unitecsim

# Create pinpad simulator.
simulator_ips = server.server.get_site_info()
pinpad = pinpadsim.init_pinpadsim()
crindsim = crindsim.CrindSim(endpoint=f"http://{simulator_ips['ip']}/")
unitecsim = unitecsim.init_unitecsim()
# Create/Start network simulators.
networksim = networksim.init_networksim()

#Importing pos based on the system config
pp_subkey = constants.NT_SUBKEY
reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, pp_subkey, 0, winreg.KEY_ALL_ACCESS)
html_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, constants.CSOFT_PP_SUBKEY, 0, winreg.KEY_ALL_ACCESS)

Site_Type = "Classic"
if (winreg.QueryValueEx(reg_key, 'Machine')[0] == "PS65"):
    Site_Type = "Edge"
elif ('htmlpos' in winreg.QueryValueEx(html_key, 'POSPathName')[0]):
    Site_Type = "HTMLPos"

if Site_Type == "Edge":
    from app.framework import edge as pos
elif Site_Type == "HTMLPos":
    from app.framework import pos_html as pos
else:
    from app.framework import pos

# TODO: Work checkout import into pos logic above
from app.framework import checkout, console

from app.framework import Navi

def get_feature_modules():
    """
    Sets up app.__init__.py to have all brand modules imported and the main brand module returned.
    This is meant for inside use only.
    Args:
        None
    Returns:
        None
    """
    # Initialize logging
    log = logging.getLogger()

    #Getting the path of the current module -> App\__init__.py
    module_path = os.path.dirname(os.path.realpath(__file__))
    #Getting the list of modules in the feature path.
    feature_path = f"{module_path}\\features"
    path_list = os.listdir(feature_path)
    #Looping through each file within the features directory.
    #If the item is a python file, append to the import list and remove the .py extension.
    import_list = []
    for item in path_list:
        if item == "__init__.py":
            continue
        if item.endswith(".py"):
            import_list.append(item[:len(item)-3])
    #Creating the import string and testing out the import itself.
    import_string = f"app.features"
    #Looping through the import list and setting it as an attr
    for item in import_list:
        try:
            setattr(app, item, importlib.import_module(f"{import_string}.{item}"))
        except Exception as e:
            log.warning(e)
            log.debug(f"Could not properly import the {item} module.")
            continue

def get_network_modules():
    """
    Fetches brand specific network modules.
    If the module is missing for the specific brand, the module from core is imported
    instead.
    """
    # A map of the brands that behave exactly like other brands
    # If the brand behaves like core, skip it since the core will be loaded
    # by deafult if the brand submodule is not found
    NETWORK_BRAND_ASSOCIATION_MAP = {
        "cenex" : "nbs",
        "hps-dallas" : "hps_dallas",
        "hps-chicago": "hps_chicago",
        "faststop": "hps_chicago"
    }

    # Initialize logging
    log = logging.getLogger()

    # Get brand
    brand = system.get_brand().lower()

    # Check if the brand is behaving like the other brand
    if brand in NETWORK_BRAND_ASSOCIATION_MAP:
        # Use sibling brand instead
        brand = NETWORK_BRAND_ASSOCIATION_MAP[brand]

    #Getting the path of the current module -> App\__init__.py
    module_path = os.path.dirname(os.path.realpath(__file__))

    #Getting the list of modules in the brand specific network path.
    brand_path = f"{module_path}\\features\\network\\{brand}"
    core_path = f"{module_path}\\features\\network\\core"

    # List of modules imported for the specific brand and core
    brand_modules_list = []
    core_modules_list = []

    # Check that the brand submodule exists
    # If not, load everything from core
    if os.path.isdir(brand_path):
        #Looping through each file within the features network directory.
        #If the item is a python file, append to the import list and remove the .py extension.
        path_list = os.listdir(brand_path)
        for item in path_list:
            if item == "__init__.py":
                continue
            if item.endswith(".py"):
                brand_modules_list.append(item[:len(item)-3])
        
        #Looping through the import list and setting it as an attr
        import_string = f"app.features.network.{brand}"
        for item in brand_modules_list:
            try:
                setattr(app, item, importlib.import_module(f"{import_string}.{item}"))
                # print(f"Done. {import_string}.{item}")
            except Exception as e:
                log.warning(e)
                log.debug(f"Could not properly import the {item} module for {brand.title()}")
                continue
    
    # Loop through the files from core path and import everything that is missing
    path_list = os.listdir(core_path)
    import_string = "app.features.network.core"
    for item in path_list:
        if item == "__init__.py":
            continue
        if not (item[:len(item)-3] in brand_modules_list) and item.endswith(".py"):
            core_modules_list.append(item[:len(item)-3])

    #Creating the import string and testing out the import itself.
    import_string = "app.features.network.core"
    #Looping through the import list and setting it as an attr
    for item in core_modules_list:
        try:
            setattr(app, item, importlib.import_module(f"{import_string}.{item}"))
            # print(f"Done. {import_string}.{item}")
        except Exception as e:
            log.warning(e)
            log.debug(f"Could not properly import the {item} module for Concord")
            continue
            
get_feature_modules()
get_network_modules()

from app.framework import initial_setup

Overlay = overlay.Overlay
Results = results.Results 