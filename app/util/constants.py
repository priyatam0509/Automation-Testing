
import platform

# HTML5
CHROME_DRIVER               = r"D:\Automation\Program Files\Selenium\chromedriver.exe"

# Initial Setup files
CORE_TEMPLATE               = r"D:\Automation\app\data\CoreTemplate.xml"
CORE_EXPORT                 = r"D:\ExtractionTool\CoreExport.xml"
STANDARD_CONFIG             = r"D:\Automation\app\data\StandardConfig.json"
STANDARD_FORECOURT          = r"D:\Automation\app\data\ForecourtStandard.json"
STANDARD_NETWORK            = r"D:\Automation\app\data\NetworkStandard.json"
BRAND_ID                    = r"D:\Automation\app\data\brandIDs.json"
PARSER_API                  = r"http://10.4.38.122:3000/parser/"

# Control/Locator files
CONTROLS_WPF                = r"D:\Automation\app\data\controls.json"
CONTROLS_EDGE               = r"D:\Automation\app\data\edge_controls.json"
CONTROLS_SCO                = r"D:\Automation\app\data\checkout_controls.json"
CONTROLS_CCC                = r"D:\Automation\app\data\console_controls.json"

# Site specific
APPDATA                     = r"D:\Automation\app\data"
APPDATA_EDH                 = r"D:\AutomationTools\data"
SNAPSHOT_PATH               = r"D:\Gilbarco\snapshot"
SNAPSHOT_PATH_EDH           = r"F:\Gilbarco\snapshot"
COLLECTLOGS_DIR             = r"D:\Gilbarco\LogArchive"
USER_CREDENTIALS            = r"C:\Gilbarco\pos_creds.json"

# Tools
SECURITY_MANAGER            = r"C:\Gilbarco\Tools\SecurityManager.exe"
TESTING_TOOLS               = r"D:\Automation\Tools\TestingTools"

# Card Data
CARD_DATA                   = r"D:\Automation\app\data\CardData.json"
CARD_DATA_MANUAL            = r"D:\Automation\app\data\CardData_Manual.json"

# Conexxus Mobile Payment MWS APP
CONEXXUS_EXE                = r"D:\Automation\Tools\ConexxusMWS\ConexxusMobileSimulator.exe"
REWARDS_PATH                = r"D:\Automation\Tools\ConexxusMWS\RewardDetails.xml"
MOBILE_DATA_PATH            = r"D:\Automation\Tools\ConexxusMWS\Conexxus_MobileData.xml"
SETTINGS_PATH               = r"D:\Automation\Tools\ConexxusMWS\Conexxus_Settings.xml"
DISCOUNT_NAME               = r"Discount 1"

#Insite 360
LOGIN_URL                   = r"https://insite360.sandbox.gilbarco.com/i360"
MAIN_PAGE                   = r"https://insite360.sandbox.gilbarco.com/i360/pos/"
STORE_URL                   = r"https://insite360.sandbox.gilbarco.com/i360/store-list/#/storeList"
EMP_URL                     = r"https://insite360.sandbox.gilbarco.com/i360/employee-list/#/employee-list"
NEW_EMP_URL                 = r"https://insite360.sandbox.gilbarco.com/i360/employee-list/#/employee-edit/new"
CONTROL_PATH                = r"D:\automation\app\data\insite360_controls.json"

# Registry
if '7' in platform.release():
    PASSPORT_SUBKEY             = r"SOFTWARE\Gilbarco\Passport"
    NT_SUBKEY                   = r'SOFTWARE\Gilbarco\NT'
    CRIND_SUBKEY                = r'SOFTWARE\Gilbarco\CRIND'
    SECURE_SUBKEY               = r'SOFTWARE\Gilbarco\Secure'
    RES_SUBKEY                  = r'SOFTWARE\Gilbarco\Passport\MWS'
    CASHDRAWER_SUBKEY           = r'SOFTWARE\OleForRetail\ServiceOPOS\CashDrawer'
    POSPRINTER_SUBKEY           = r'SOFTWARE\OleForRetail\ServiceOPOS\POSPrinter'
    CARWASH_SUBKEY              = r'SOFTWARE\OLEforRetail\ServiceOPOS\CarWashController'
    CSOFT_PP_SUBKEY             = r'SOFTWARE\CSOFT\Passport'
    REMOTEMNGR_SUBKEY           = r'SOFTWARE\Gilbarco\RemoteManager'

else:
    PASSPORT_SUBKEY             = r"SOFTWARE\WOW6432Node\Gilbarco\Passport"
    NT_SUBKEY                   = r'SOFTWARE\WOW6432Node\Gilbarco\NT'
    CRIND_SUBKEY                = r'SOFTWARE\WOW6432Node\Gilbarco\CRIND'
    SECURE_SUBKEY               = r'SOFTWARE\WOW6432Node\Gilbarco\Secure'
    RES_SUBKEY                  = r'SOFTWARE\WOW6432Node\Gilbarco\Passport\MWS'
    CASHDRAWER_SUBKEY           = r'SOFTWARE\WOW6432Node\OleForRetail\ServiceOPOS\CashDrawer'
    POSPRINTER_SUBKEY           = r'SOFTWARE\WOW6432Node\OleForRetail\ServiceOPOS\POSPrinter'
    POSPRINTER_T88II_SUBKEY     = r'SOFTWARE\WOW6432Node\OleForRetail\ServiceOPOS\POSPrinter\TM-T88II'
    CARWASH_SUBKEY              = r'SOFTWARE\WOW6432Node\OLEforRetail\ServiceOPOS\CarWashController'
    CSOFT_PP_SUBKEY             = r'SOFTWARE\WOW6432Node\CSOFT\Passport'
    HTMLPOS_SUBKEY              = r'SOFTWARE\WOW6432Node\Gilbarco\HTMLPOS'
    REMOTEMNGR_SUBKEY           = r'SOFTWARE\WOW6432Node\Gilbarco\RemoteManager'


# NOTE: Who is in charge of following up on Joe's legacy TODO's?
# Host Simulator IPs
# TODO: Get rid of this after Network Sims are rewritten in C#
PRIMARY_IP                  = r"10.4.18.67"
SECONDARY_IP                = r"10.80.31.237"

