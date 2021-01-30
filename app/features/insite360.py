from app import mws
from app import Navi, system
import logging, time

class Insite360Interface:
    FG_STORE_OFFSET = 485
    FG_SHIFT_OFFSET = 585
    FG_INSTANCES = { "Fuel Grade Movement": 4,
                     "Item Sales Movement": 2,
                     "Merchandise Code Movement": 2,
                     "Miscellaneous Summary Movement": 2,
                     "Tax Level Movement": 2 }

    def __init__(self):
        self.log = logging.getLogger()
        self.order = ['Enable Insite360','Apply only to this register group','Apply to only this register group combo box']
        Insite360Interface.navigate_to()

    @staticmethod
    def navigate_to():
        """
        Navigates to the Insite360 Interface.
        Args: 
            None
        Returns:
            Result of Navi.navigate_to()
        """
        return Navi.navigate_to("insite360 interface")

    def configure(self,config,register=False):
        """
        Changes the fields in the insite360 interface and saves.
        Args:
            config: A dictionary of controls so the user can add the information that
                    they need to. This is according to the schema in controls.json.
            register: A boolean value that determines whether the method attempts to register
                      the site at the end of configuration. If False, it will Save without registering.
        Returns:
            bool: True/False success condition
        Example:
            insite_info = {
                "General": {
                    "Enable Insite360": True,
                    "Export price book when third party changes are made to items or departments": False,
                    "Gilbarco ID": "123456",
                    "Apply only to this register group": True,
                    "Apply to only this register group combo box": "POSGroup1"
                },
                "Summary Files": {
                    "Fuel Grade Movement": [True, True],
                    "Fuel Product Movement": [True, False],
                    "Item Sales Movement": [True, True]
                }
            }
        """
        # Takes care of order-sensitive controls (of the General tab)
        for field in self.order:
            try:
                value = config["General"][field]
            except KeyError:
                continue
            if not mws.set_value(field, value):
                return False
            del config["General"][field]

        #Cycles through tabs
        for tab in config:
            mws.select_tab(tab) #Go to tab
            if tab == "General":
                for key, value in config[tab].items():
                    if not mws.set_value(key,value,tab): 
                        self.log.error(f"Could not set '{key}' to '{value}' in '{tab}' tab.")
                        return False
                    # Sometimes set_value does not work after having just selected a tab
                    if mws.get_value(key) != value:
                        self.log.debug(f"Setting {key} to {value} did not work, retrying...")
                        if not mws.set_value(key,value,tab):
                            self.log.error(f"Could not set '{key}' to '{value}' in '{tab}' tab.")
                            return False
            if tab == "Summary Files":
                self.log.debug("Configuring Flex Grid...")
                mws.config_flexgrid(
                    "XML Documents list", config[tab],
                    [Insite360Interface.FG_STORE_OFFSET,
                    Insite360Interface.FG_SHIFT_OFFSET],
                    instances=Insite360Interface.FG_INSTANCES
                    )
        if register == True:
            # Attempt to register, with timeout of 10 secs
            mws.click_toolbar("Register Site")
            mws.click_toolbar("Yes")
            start_time = time.time()
            while time.time() - start_time < 10:
                if "Waiting on service" in mws.get_top_bar_text():
                    continue
                elif 'failed' in mws.get_top_bar_text().lower():
                    self.log.debug("Registration failed. Getting back to general tab...")
                    mws.click_toolbar("OK")
                    mws.select_tab("General")
                    system.takescreenshot()
                    return False
                else: 
                    self.log.warning("Registration has not failed or timed out. Assuming success...")
                    return True
                # TODO: Figure out what successful registration message looks like. Example below:
                # elif [registration success condition]
                #   return True
            self.log.error("Failure: Registration has timed out.")
            return False
        else:
            try:
                mws.click_toolbar("Save", main=True)
            except ConnException:
                msg = mws.get_top_bar_text()
                self.log.error(f"Didn't return to main menu after trying to save Insite360 config. Passport message: {msg}")
                return False
            return True

    def register(self, timeout=10):
        """
        Attempts to register site, with timeout of default 10 secs.
        Args:
            timeout (int) - in Seconds, default 10 sec.
        Returns:
            bool: True/False success condition
        """

        mws.click_toolbar("Register Site")
        # Check for correct top bar prompt
        if mws.get_top_bar_text() != "Do you want to Register this site?":
            self.log.error("Registration prompt did not appear correctly.")
            return False
        # Sleep for 2 seconds, some site is running very fast
        time.sleep(2)
        mws.click_toolbar("Yes")
        start_time = time.time()

        returnStatus = True
        # Check with the top bar text status, if is empty ready to go to next steps
        textStatus = True
        # "Waiting on service" stays on screen for about 7 secs
        while (time.time() - start_time < timeout and textStatus):
            if "Waiting on service" in mws.get_top_bar_text():
                continue
            elif 'failed' in mws.get_top_bar_text():
                self.log.debug("Registration failed. Getting back to general tab...")
                system.takescreenshot()
                mws.click_toolbar("OK")
                mws.select_tab("General")
                returnStatus = False
                textStatus = False
            elif 'Grades' in mws.get_top_bar_text(): 
                mws.click_toolbar("OK")
                time.sleep(2)
            elif 'Registration is complete,' in mws.get_top_bar_text(): 
                mws.click_toolbar("OK")
                time.sleep(2)
                textStatus = False
            else: 
                self.log.warning("Registration has not failed or timed out. Assuming success...")
                textStatus = False
            # TODO: Figure out what successful registration message looks like. Example below:
            # elif [registration success condition]
            #   return True
        if (returnStatus):
            mws.click_toolbar("Exit", main=True)
        else:    
            self.log.error("Failure: Registration has timed out.")
        return returnStatus

    # TODO: Clean this method up (fix error hiding, infinite loop, naming convention)
    def unRegister(self):
        """
        Attempts to un-register site.
        Args:
            None.
        Returns: returnStatus
            bool: True/False success condition
        """

        returnStatus = True
        wait_service = False
        try:
            mws.click_toolbar("unregister Site")
            # Check for correct top bar prompt
            textStatus = True
            while textStatus:
                if (mws.get_top_bar_text().lower() == "the site is no longer registered"):
                    self.log.info(f"Top bar text [{mws.get_top_bar_text()}]")
                    wait_service = True
                    mws.click_toolbar("OK")
                    time.sleep(2)
                elif (mws.get_top_bar_text().lower() == "waiting on service"):
                    wait_service = True
                    time.sleep(2)
                elif (mws.get_top_bar_text().lower() != ""):
                    self.log.info(f"Top bar text [{mws.get_top_bar_text()}]")
                    mws.click_toolbar("Yes")
                    time.sleep(2)
                else:
                    if (wait_service):
                        textStatus = False
            
            mws.click_toolbar("Exit", main=True)

        except:
            returnStatus = False
            self.log.error("Exception occured while unregister the site")

        return (returnStatus)
