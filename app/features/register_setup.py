from app.framework import mws, Navi, OCR
import logging, time, copy
from app.util import system

log = logging.getLogger()

class RegisterSetup:
    def __init__(self):
        RegisterSetup.navigate_to()
        self.order = ['Machine Name', 'PIN Pad Type', 'Connection', 'IP Address', 'COM Port', 'Personality', 'Scanner Type', 'Scanner IP', 'Scanner COM Port']

    @staticmethod
    def navigate_to():
        return Navi.navigate_to("Register Set Up")

    def add(self, config):
        """
        Description: Add a new register.
        Args:
            config: A dictionary of controls so the user can add the information that
                      they need to. This is according to the schema in controls.json.
        Returns:
            bool: Success/failure
        """
        config = copy.deepcopy(config) # Replace config dict with a deep copy so we don't alter the original

        mws.click_toolbar("Add", 5, submenu=True)
        # Take care of order-sensitive stuff first
        for field in self.order:
            try:
                value = config[field]
            except KeyError:
                continue
            if not mws.set_value(field, value):
                mws.click_toolbar("Cancel")
                mws.click_toolbar("No")
                return False
            time.sleep(.1) # Prevent timing issues with controls reloading
            del config[field]

        for key, value in config.items():
            if not mws.set_value(key, value):
                mws.click_toolbar("Cancel")
                mws.click_toolbar("No")
                return False
        mws.click_toolbar("Save", submenu=True)

        start_time = time.time()
        msg = mws.get_top_bar_text()
        while msg:
            if time.time() - start_time > 60: # Just in case Passport gets stuck
                log.error("Waited more than 60 seconds for register to save. Seems like Passport is stuck.")
                mws.recover()
                return False
            elif "Saving" in msg:
                continue
            else:
                log.error(f"Got unexpected message when saving register: {msg}")
                return False
            msg = mws.get_top_bar_text()

        return True



    def change(self, reg_num, machine_name, config):
        """
        Description: Change the configuration for an existing register.
        Args:
            reg_num: The number of the register to change.
            machine_name: The machine name for the register to change.
            config: A dictionary of controls so the user can add the information that
                      they need to. This is according to the schema in controls.json.
        Returns:
            bool: Success/failure
        """
        config = copy.deepcopy(config) # Replace config dict with a deep copy so we don't alter the original

        # Dumb special case because register selection looks like a list view but is actually a list box
        for value in mws.get_value("Registers"):
            if reg_num in value and machine_name in value:
                mws.get_control("Registers").select(value)
                break
        else:
            log.warning(f"Register {reg_num} {machine_name} not found in list of registers.")
            return False

        mws.click_toolbar("Change", submenu=True)
        # Take care of order-sensitive stuff first
        for field in self.order:
            try:
                value = config[field]
            except KeyError:
                continue
            if not mws.set_value(field, value):
                mws.click_toolbar("Cancel")
                mws.click_toolbar("No", submenu=True)
                return False
            time.sleep(.1) # Prevent timing issues with controls reloading
            del config[field]

        for key, value in config.items():
            if not mws.set_value(key, value):
                mws.click_toolbar("Cancel")
                mws.click_toolbar("No", submenu=True)
                return False
        mws.click_toolbar("Save", submenu=True)

        start_time = time.time()
        msg = mws.get_top_bar_text()
        while msg:
            if time.time() - start_time > 60: # Just in case Passport gets stuck
                log.error("Waited more than 60 seconds for register to save. Seems like Passport is stuck.")
                mws.recover()
                return False
            elif "Saving" in msg:
                continue
            else:
                log.error(f"Got unexpected message when saving register: {msg}")
                return False

    def delete(self, reg_num, machine_name):
        """
        Description: Delete an existing register.
        Args:
            reg_num: The number of the register to delete.
            machine_name: The machine name for the register to delete.
        Returns:
            bool: Success/failure
        """
        # Dumb special case because register selection looks like a list view but is actually a list box
        for value in mws.get_value("Registers"):
            if reg_num in value and machine_name in value:
                mws.get_control("Registers").select(value)
                break
        else:
            log.warning(f"Register {reg_num} {machine_name} not found in list of registers.")
            return False
        mws.click_toolbar("Delete")
        msg = mws.get_top_bar_text()
        if msg == f"Are you sure you want to delete Register {reg_num}?":
            mws.click_toolbar("Yes")
        else:
            log.warn(f"Didn't get the right confirmation message for deleting Register {reg_num} {machine_name}. "
                     f"Actual message: {msg}")
            return False

        if any(machine_name in value for value in mws.get_value("Registers")):
            log.error(f"{machine_name} was still in the list of registers after deletion.")
            return False

        return True

    def init_replication(self, timeout=600):
        """
        Re-initialize register replication.
        Args:
            timeout: (int) How many seconds to allow for the initialization process to complete.
        Returns:
            bool: Success/failure
        Example:
            >>> RegisterSetup().init_replication()
            True
        """
        # Start initialization
        log.debug("Re-initializing replication.")
        if not mws.click_toolbar("Replication"):
            return False
        if not mws.click_toolbar("Initialize Replication"):
            return False
        if not system.wait_for(mws.get_top_bar_text, "Are you sure you want to reinitialize replication?", verify=False):
            log.warning("Did not get confirmation prompt to reinitialize replication.")
            mws.recover()
            return False
        if not mws.click_toolbar("Yes"):
            return False

        # Wait for completion
        log.debug("Replication initialization started. Waiting for completion.")
        status = ""
        last_status = ""
        start_time = time.time()
        while time.time() - start_time <= timeout:
            if "Replication was initialized successfully" in mws.get_top_bar_text():
                log.info("Replication was initialized successfully.")
                return True
            status = OCR.OCRRead(bbox=(12, 475, 632, 507))
            if status != last_status: # So we don't spam the log
                last_status = status
                log.debug(f"Initialization status: {status}")
        else:
            log.warning(f"Replication did not complete initialization within {timeout} seconds.")
            mws.recover()
            return False

    @staticmethod
    def add_scanner_port(register=1, port_num=4, num_clients=5):
        """
        Set a serial port number for the serial barcode scanner simulator to use.
        Args:
            register: (int) The register number to set the port for.
            port_num: (int) The port number to use. This should be a number that is not already occupied by a physical serial port.
                      If non-default, you will need to change the configuration of com0com in C:\Program Files (x86) to match.
            num_clients: (int) The number of clients on the site. Replication errors may occur if this is set too low.
        Returns: True if success, False if failure
        Examples:
            >>> add_scanner_port()
            True
            >>> add_scanner_port(2, 5)
            True
        """
        from app import runas

        log.info("Creating CS_SCANNER_PORTS column on server.")
        result = runas.run_as('sqlcmd -E -S localhost -d GlobalSTORE -Q \"ALTER TABLE REGISTER ADD CS_SCANNER_PORTS VARCHAR(20) NULL;\"')['output']
        if 'specified more than once' in result:
            log.info("REGISTER table already has column CS_SCANNER_PORTS. Ignoring error.")
        elif result:
            log.warning(f"Failed to add CS_SCANNER_PORTS column to REGISTER table. Error: {result}")
            return False
     
        # Create column on clients to prevent replication errors
        for client_num in range(num_clients):
            client_name = f"POSCLIENT00{client_num+1}"
            log.info(f"Creating CS_SCANNER_PORTS column on {client_name}.")
            result = runas.run_sqlcmd("ALTER TABLE REGISTER ADD CS_SCANNER_PORTS VARCHAR(20) NULL;", database="GlobalSTORE", cmdshell=False, 
                                      destination=client_name, user="PassportTech", password="911Tech")['output']
            if 'specified more than once' in result:
                log.info(f"REGISTER table on {client_name} already has column CS_SCANNER_PORTS. Ignoring error.")
            elif result:
                log.warning(f"Failed to add CS_SCANNER_PORTS column to REGISTER table on {client_name}. Error: {result}")
                return False

        log.info(f"Configuring COM port {port_num} for serial barcode scanner sim on register {register}.")
        result = runas.run_as(f'sqlcmd -E -S localhost -d GlobalSTORE -Q \"UPDATE REGISTER SET CS_SCANNER_PORTS = \'COM{port_num}\' where RGST_ID = \'{register}\'\"')['output']
        if "1 rows affected" not in result:
            log.warning(f"Failed to set scanner port to {port_num} for register {register}. Error: {result}")
            return False

        return True