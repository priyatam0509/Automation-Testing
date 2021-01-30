import json
import logging
import os
import shutil
import time
import xml.etree.ElementTree as ET
from pywinauto.keyboard import send_keys

#Import constants module
from app.util import constants
#Import feature modules
from app import employee, network_site_config, register_setup
from app import feature_activation, register_grp_maint, store_close
from app import express_lane_maint
#Import util modules
from app import system, server, runas
#Import framework modules
from app import mws, Navi, pos
#Import simulator modules
from app import pinpadsim, pinpad, crindsim
#Import EDH
from app.framework import EDH
#Import Host_Function Module
from app import host_function, pdl


__author__ = 'Conor McWain'

script_path = os.path.dirname(os.path.realpath(__file__))
test_script_name = os.path.basename(__file__)

log = logging.getLogger()

skip_list = {
    'Classic': ['Express Lane', 'Tablet POS'],
    'Edge': ['Express Lane'],
    'Express': ['Tablet POS']
}

class SetupException(Exception):
    def __init__(self, msg):
        self.message = msg

class Initial_setup:


    def __init__(self, site_type):
        self.site_type = site_type

        self.brand = system.get_brand().upper()
        self.version = system.get_version()
        self.core_template = constants.CORE_TEMPLATE
        self.core_export = constants.CORE_EXPORT
        self.std_json = constants.STANDARD_CONFIG
        self.fc_json = constants.STANDARD_FORECOURT
        self.ntwrk_json = constants.STANDARD_NETWORK
        
        with open(self.std_json, 'r') as fp:
            self.standard_json = json.load(fp)

    def basic_setup(self):
        """
        Basic Setup
        
        This will use the initial_setup module to configure the site with the Standard Config file. 
        This configuration includes:
            - Feature Activation
            - Fake Hardening the EDH
            - Enabling the Carwash Controller
            - Register Configuration
            - Employee Configuration
            - Network Setup
            - Editing and Importing default configuration XML
        """
        errors = ""
        self.feature_activate(self.site_type)
        
        self.configure_register()
        self.add_employee()
        self.setup_network()
        if not self.pdl():
            errors += "\nFailed to complete PDL download."
        
        if "HPS-DALLAS" in self.brand:
            if not self.comm_test():
                log.error("There was an issue with comm test")
                raise SetupException("There was an issue with the Communications Test")

        if "CITGO" in self.brand:
            log.info("Navigating to POS")
            Navi.navigate_to("POS")
            pos.sign_on()
            pos.close()
            store_close.StoreClose.navigate_to()
            sc = store_close.StoreClose()
            if not sc.begin_store_close():
                log.error("Failed to perform store close after pdl")

        self.edit_xml()
        if not self.import_xml():
            errors += "\nFailed to import configuration via Extraction Tool."
        self.reapply_forecourt_config()
        errors += self.setup_edh()
        # if not crindsim.setup_edh(4, server.server.get_site_info()['ip']): TODO: Once setup_edh has verification, add this back
        #     errors += "\nFailed to add reg keys for CRIND Sim on EDH."
        system.save_snapshot()

        if errors:
            log.error(f"Initial setup completed with errors: {errors}\n Consult the above logs for more detail.")
            raise SetupException(errors)

    def comm_test(self):
        #This will perform COMM test
        hf = host_function.HostFunction()
        if not hf.communications_test():
            log.warning("Failed the Communications Test")
            return False
        return True

    def setup_edh(self):
        errors = ""
        edh = EDH.EDH()
        if not edh.enable_security():
            errors += "\nFailed to enable EDH security."
        if not edh.setup():
            errors += "\nFailed to set receipt printer port and enable car wash controller."
        crindsim.setup_edh(4, server.server.get_site_info()['ip'])

        return errors

    def configure_register(self):

        #If "Register Groups" is found in the StandardConfig else set it to None
        groups = self.standard_json[self.site_type]["Register Groups"] \
            if ("Register Groups" in self.standard_json[self.site_type]) else None
        manager = self.standard_json[self.site_type]["Manager"]
        #If "Clients" is found in the StandardConfig else set it to None
        clients = self.standard_json[self.site_type]['Clients'] \
            if ("Clients" in self.standard_json[self.site_type]) else None

        # Setup Register Groups. If 'groups = None' will return True
        self.create_reg_groups(groups)

        # Setup the Register
        Navi.navigate_to('Register Set Up')
        RS = register_setup.RegisterSetup()
        reg_exist = mws.get_value("Registers")
        
        #Configure the MWS Register
        if manager["Register Number"]+"\t"+ manager["Machine Name"]+"\tCashier Workstation" in reg_exist:
            log.warning(f"Register number for server already found in list of registers.")
        else:
            if not RS.add(manager):
                log.error("There was an issue configuring the Register for the MWS")
                raise SetupException("There was an issue configuring the Register for the MWS")

            #Configure the ports for the scanner sim.
            if not RS.add_scanner_port(manager["Register Number"], num_clients=len(clients) if clients else 0):
                log.error("There was an issue configuring the Scanner ports")
                raise SetupException("There was an issue configuring the Scanner ports")

        #Configure the CWS Registers
        if clients:
            log.debug("Attempting to configure clients.")
            for key,value in clients.items():
                if value["Register Number"] + "\t" + value["Machine Name"] in mws.get_value("Registers"):
                    log.warning(f"Register number for  client already found in list of registers.")
                else:
                    if not RS.add(value):
                        log.error(f"There was an issue configuring {value['Machine Name']}")
                        raise SetupException(f"There was an issue configuring {value['Machine Name']}")
                    else:
                        log.debug(f"Successfully added client {value['Machine Name']}")
        else:
            log.debug("No clients to configure.")

        mws.click_toolbar("Exit", 10)
        msg = mws.get_top_bar_text()
        if msg == "Replication needs to be re-initialized.  Do you want to do this now?":
            mws.click_toolbar("No")
            
        if "express" in self.site_type:
            config = {
                "General":{
                    "Express Lane 1": "POSCLIENT001"
                },
                "Fuel Configuration": {
                    "Allow fuel sales": True,
                    "1 Prepay Fuel": True,
                    "1 Postpay Fuel": True
                }
            }
            elm = express_lane_maint.ExpressLaneMaintenance()
            elm.configure(config)

            #Running replication so express can function 
            RS.navigate_to()
            if not RS.init_replication():
                log.error("Failed to initialize replication. Clients may not have correct configuration.")
                raise SetupException("Failed to initialize replication. Clients may not have correct configuration.")
            else:
                mws.click_toolbar("Exit", main=True)

        # Start the PIN Pad
        pinpad.start()

    def create_reg_groups(self, groups):
        """
        Create/edit register groups.
        """
        groups_added = []
        # Create the group
        if groups is not None:
            rgm = register_grp_maint.RegisterGroupMaintenance()
            for group in groups:
                if group in mws.get_value("Register Group"):
                    if not rgm.change(groups[group]):
                        log.warning(f"Failed to edit register group {group}")
                        raise SetupException(f"Failed to edit register group {group}")
                else:
                    if not rgm.add(groups[group]):
                        log.warning(f"Failed to add register group {group}")
                        raise SetupException(f"Failed to add register group {group}")
                    groups_added.append(groups[group]["General"]["Name"])

        # Enable tenders for the new group(s)
        if groups_added == []:
            return True

        Navi.navigate_to("Tender Maintenance")
        for group in groups_added:
            applications = ["Sales", "Refunds", "Loans", "Paid In", "Paid Out"]            
            for tender in mws.get_value("Tenders"):
                mws.set_value("Tenders", tender)
                mws.click_toolbar("Change")
                mws.select_tab("Register Groups")
                settings = [mws.get_value(application) for application in applications]
                mws.set_value(group, True, list="Register Groups", tab="Register Groups")               
                while True: # Remove disabled check boxes from the list
                    try:
                        settings.remove(None)
                    except ValueError:
                        break
                if not any([mws.set_value(application, setting) for application, setting in zip(applications, settings)]):
                    raise SetupException("set_value error")
                mws.click_toolbar("Save")
                time.sleep(2) # Wait for save to complete so we don't grab the wrong control on next iteration...

        mws.click_toolbar("Exit", main=True)
        return True
        
    def add_employee(self):
        employees = self.standard_json['Employees']
        Navi.navigate_to('Employee')
        E = employee.Employee()
        emp_exist = mws.get_value("Employees")

        for i,ids in enumerate(employees.keys()):
            if i<len(emp_exist) and ids == emp_exist[i][0]:
                log.info(f"employee id {ids} already present")               
            elif not E.add(employees[ids]):
                log.warning("Failed to add employee #"+str(ids))
                raise SetupException("Failed to add employee #"+str(ids))
        mws.click_toolbar("Exit")

    def setup_network(self):
        with open(self.ntwrk_json, 'r') as fp:
            self.network_json = json.load(fp)

        ntwrk = self.network_json[self.brand]

        log.debug('Navigating to: '+list(ntwrk.keys())[0])
        Navi.navigate_to(list(ntwrk.keys())[0])
        N = network_site_config.NetworkSetup()
        if not N.configure_network(config=ntwrk[list(ntwrk.keys())[0]]):
            log.warning("Failed to configure Network manually")
            mws.recover()
            log.debug("Setting up {0} network through".format(self.brand))
            edh = EDH.EDH()
            if not edh.initialize_Network():
                log.warning("Failed to configure Network through the EDH")
                raise SetupException("Failed to configure Network through the EDH")

    def pdl(self):
        pd = pdl.ParameterDownload()
        if not pd.request():
            log.warning("Failed PDL Download")
            return False
        return True

    def feature_activate(self, site_type):

        FA = feature_activation.FeatureActivation()
        if not FA.activate(getattr(feature_activation, "DEFAULT_{}".format(site_type.upper()))):
            log.warning("Failed to feature activate")
            raise SetupException("Failed to feature activate")
    
    def edit_xml(self):
        path = self.core_export[0:self.core_export.rindex("\\")]

        # If Extractiontool directory does not exist, create it.
        if not os.path.exists(path):
            os.makedirs(path)

        #If CoreExport.xml doesn't exist copy from D:\Automation\app\data
        shutil.copy(self.core_template, self.core_export)
        
        tree = ET.parse(self.core_export)
        #Edit the Version number in the XML file
        tree = self.edit_ver(tree)
        #Edit the DispenserConfig in ForecourtConfig
        tree = self.edit_forecourt(tree)
            
        tree.write(self.core_export)

    def edit_ver(self, tree):
        ver = tree.find('Header/Passport/Version')
        ver.text = self.version

        return tree

    def edit_forecourt(self, tree):

        dispensers = self.standard_json['Dispensers']

        with open(self.fc_json, 'r') as fp:
            forecourt_json = json.load(fp)

        std_disp = forecourt_json['Standard Dispenser']
        std_tank = forecourt_json['Standard Tank']

        #Grade list will be the same for all dispensers
        grade_config = forecourt_json['Grades']
        try:
            grades = grade_config[self.brand]
        except:
            grades = grade_config['Default']
        
        #Determine the number of products needed based on all dispensers being 
        # configured
        products = 0
        for dispenser in dispensers:

            disp_config = forecourt_json['Dispensers'][dispenser]

            #Evaluate the depsenser and increment the product number based on its 
            # configuration
            inc_products = 0
            for key in disp_config:
                if 'Blended' in key:
                    inc_products = 2
                elif 'Pure' in key:
                    inc_products += disp_config['Pure']

            #Set 'products' to be the highest number of products across dispensers
            if inc_products > products:
                products = inc_products

        log.debug("Products: "+str(products))

        blend_grades = 0
        pure_grades = 0
        for dispenser in dispensers:

            disp_config = forecourt_json['Dispensers'][dispenser]

            #Evaluate the depsenser and increment the grade numbers based on the 
            # config
            for key in disp_config:
                if 'Blended' in key:
                    if blend_grades < disp_config[key]:
                        blend_grades = disp_config[key]
                elif 'Pure' in key:
                    if pure_grades < disp_config[key]:
                        pure_grades = disp_config[key]

            log.debug("Dispenser: "+dispenser)
            log.debug("Blended Grands: "+str(blend_grades))
            log.debug("Pure Grands: "+str(pure_grades))

        blend_grade_ids = range(1, blend_grades+1)
        pure_grade_ids = range(blend_grades+1, pure_grades+blend_grades+1)
        
        log.debug("Blended Grade IDs: "+str(blend_grade_ids))
        log.debug("Pure Grade IDs: "+str(pure_grade_ids))

        FC = tree.find('FCInstallationMaintenance/ForecourtConfig')
        DC = FC.find('DispenserConfig')
        #Used to keep count of the dispensers we configure
        i = 1
        #Set the values unique to each dispenser
        for dispenser in dispensers:
            #dispenser = 'BLN_3+1'
            Disp = ET.SubElement(DC, 'Dispenser')
            Disp.set("ID", str(i))

            #Set all the standard elements under Standard Dispsner in the 
            # ForecourtStandard.json
            for key in std_disp:
                childElement = ET.SubElement(Disp, key)
                if std_disp[key] != "":
                    childElement.text = std_disp[key]

            if dispenser == 'CNG/LNG':
                UoM = Disp.find('UnitOfMeasure')
                UoM.text = "GGE"

            #Set the DeviceID to the incrementing variable i
            childElement = ET.SubElement(Disp, 'DeviceID')
            childElement.text = str(i)

            #Set the DispenserTypeId to the value under Dispensers in the 
            # ForecourtStandard.json
            DTID = ET.SubElement(Disp, 'DispenserTypeId')
            DTID.text = dispenser

            disp_config = forecourt_json['Dispensers'][dispenser]
            # disp_config = {"Pure": 3}
            # disp_config = {"Blended": 3, "Pure": 1}
            GM = ET.SubElement(Disp, 'GradeMap')

            log.debug("Dispenser: "+dispenser)
            log.debug("Blended Grade IDs: "+str(blend_grade_ids))
            log.debug("Pure Grade IDs: "+str(pure_grade_ids))

            #Set the GradeMap based on the Blended and Pure grades each dispenser 
            # needs
            for key in disp_config:
                if 'Blended' in key:
                    for g in range(disp_config[key]):
                        childElement = ET.SubElement(GM, 'Grade')
                        childElement.text = str(blend_grade_ids[g])
                elif 'Pure' in key:
                    for g in range(disp_config[key]):
                        childElement = ET.SubElement(GM, 'Grade')
                        childElement.text = str(pure_grade_ids[g])

            LTGM = ET.SubElement(Disp, 'LoTankGradeMap')
            for _ in range(1, 7):
                LTID = ET.SubElement(LTGM, 'LoTankID')
                LTID.text = '0'

            HTGM = ET.SubElement(Disp, 'HiTankGradeMap')
            for _ in range(1, 7):
                HTID = ET.SubElement(HTGM, 'HiTankID')
                HTID.text = '0'

            IP = ET.SubElement(Disp, 'IPAddress')
            IP.text = '0.0.0.'+str(i)

            childElement = ET.SubElement(Disp, 'SerialNumber')
            childElement.text = str(i)

            # disp_config = {"Pure": 3}
            # disp_config = {"Blended": 3, "Pure": 1}
            TM = ET.SubElement(Disp, 'TankMap')
            for key in disp_config:
                if 'Blended' in key:
                    for t in range(1, 3):
                        childElement = ET.SubElement(TM, 'Tank')
                        childElement.text = str(t)
                elif 'Pure' in key:
                    for t in range(1, disp_config[key]+1):
                        childElement = ET.SubElement(TM, 'Tank')
                        childElement.text = str(t)

            i += 1

        PC = FC.find('ProductConfig')
        for pc in range(1, products+1):
            Prod = ET.SubElement(PC, 'Product')
            Prod.set("ID", str(pc))
            Prod_Name = ET.SubElement(Prod, 'Name')
            Prod_Name.text = 'Product '+str(pc)

        #These are currently set to ensure BLN_3_FIXED work
        blend_percents = [0,20,100,60,80,40]
        GC = FC.find('GradeConfig')
        #Add the Blended Grades
        for bg in range(blend_grades):
            Grade = ET.SubElement(GC, "Grade")
            Grade.set("ID", str(bg+1))

            Abbrev = ET.SubElement(Grade, 'Abbreviation')
            Abbrev.text = grades[bg][1]
            AltAbbrev = ET.SubElement(Grade, 'AlternateAbbreviation')
            AltName = ET.SubElement(Grade, 'AlternateName')
            Blend = ET.SubElement(Grade, 'Blended')
            Blend.text = 'true'
            HPID = ET.SubElement(Grade, 'HighProductID')
            HPID.text = '2'
            LPID = ET.SubElement(Grade, 'LowProductID')
            LPID.text = '1'
            LPP = ET.SubElement(Grade, 'LowProductPercent')
            log.debug("Blend Percents: "+str(blend_percents[bg]))
            LPP.text = str(blend_percents[bg])
            Name = ET.SubElement(Grade, 'Name')
            Name.text = grades[bg][0]

        #Add the Pure Grades
        i = 1
        for pg in range(blend_grades, pure_grades+blend_grades):
            Grade = ET.SubElement(GC, "Grade")
            Grade.set("ID", str(pg+1))

            Abbrev = ET.SubElement(Grade, 'Abbreviation')
            Abbrev.text = grades[pg][1]
            AltAbbrev = ET.SubElement(Grade, 'AlternateAbbreviation')
            AltName = ET.SubElement(Grade, 'AlternateName')
            Blend = ET.SubElement(Grade, 'Blended')
            Blend.text = 'false'
            HPID = ET.SubElement(Grade, 'HighProductID')
            HPID.text = str(i)
            LPID = ET.SubElement(Grade, 'LowProductID')
            LPID.text = str(i)
            LPP = ET.SubElement(Grade, 'LowProductPercent')
            LPP.text = '0'
            Name = ET.SubElement(Grade, 'Name')
            Name.text = grades[pg][0]
            i+=1

        #Configure a Tank for every Product
        TC = FC.find('TankConfig')
        for i in range(1, products+1):
            Tank = ET.SubElement(TC, 'Tank')
            Tank.set("ID", str(i))
            #Set the Standard values
            for key in std_tank:
                childElement = ET.SubElement(Tank, key)
                childElement.text = std_tank[key]
            #Set the ProductID and SerialNumber
            Prod_ID = ET.SubElement(Tank, 'ProductID')
            Prod_ID.text = str(i)
            Serial = ET.SubElement(Tank, 'SerialNumber')
            Serial.text = str(i)

        # Configure remote sim IP for Unitec Kiosk
        KC = FC.find('KioskConfig')
        Kiosk = KC.find('Kiosk')
        Kiosk_IP = Kiosk.find('IPAddress')
        Kiosk_IP.text = server.server.get_site_info()['ip']

        return tree

    def import_xml(self):
        
        #Importing the Data File
        log.info("Import XML File")
        Navi.navigate_to('Extraction Tool')
        mws.set_value("Import Data", True)
        mws.click_toolbar('Next')

        # Ensure that folders are up to date and selector is not highlighting C:
        mws.click_toolbar('Refresh Folders')

        mws.search_click_ocr('D:', (241,253,634,592), '6D6D6D') # TODO Fix bounding box for high resolution
        send_keys("{ENTER}")
        mws.search_click_ocr('Extraction Tool')
        send_keys("{ENTER}")
        mws.search_click_ocr('CoreExport')
        
        mws.click_toolbar('Next')
        #@TODO: Add verification for errors at top of screen
        mws.click_toolbar('Start', 10)
        
        mws.click_toolbar('YES')

        result = None
        #Timer looking for Error Message
        start_time = time.time()
        while time.time() - start_time <= 120:
            results = mws.get_text("Results")
            if results[-1][0] != result:
                log.debug(result)
                result = results[-1][0]
            if results[-1][0] == "Import process finished with errors. Contact supervisor.":
                log.error("Had an issue with the import")
                mws.click_toolbar('Exit', main=True)
                return False
            if results[-1][0] == "Import process finished successfully":
                log.info('Finished Import')
                mws.click_toolbar('Exit', main=True)
                return True
        else:
            log.error("Timed out with the import")
            mws.click_toolbar('Exit', 120, True)
            return False


    def reapply_forecourt_config(self):

        #This will prevent we get the invalid forecourt grades message
        log.info("Going to Forecourt installation to reapply configuration")
        Navi.navigate_to("Forecourt Installation")
        mws.click_toolbar('Save')

if __name__ == "__main__":
    
    IS = Initial_setup('passport')
    # IS.edit_xml()
    IS.add_employee()