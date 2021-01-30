"""
    File name: endurance.py
    Tags:
    Description: A script to repeatedly run a variety of transactions for a long period of time, testing the endurance of Passport.
    Author: Cassidy Garner
    Date created: 2019-09-25 14:00:48
    Date last modified: 
    Python Version: 3.7
"""

"""
TODO
- Support Watchdog reboots
- Eliminate need for manual setup
- Switch to new headless crind sim
- Write TC results
- Add indoor credit transactions
- Analyze perfmon/health check logs
"""

import logging, pywinauto, datetime, time, threading, random, os, json, sys
from app import Navi, mws, pos, system, store_close, crindsim, runas, server
from app.framework import EDH
from app.framework.tc_helpers import setup, test, teardown, tc_fail

script_path = os.path.dirname(os.path.realpath(__file__))
test_script_name = os.path.basename(__file__)

class endurance():
    """
    Description: Test class that provides an interface for testing.
    """

    def __init__(self):
        """Initializes the Template class.
        Args: None
        Returns: None
        """
        # The logging object. 
        # Example: self.log.info(f"Current value of var: {my_var}")
        self.log = logging.getLogger(__name__)
        self.close_time = datetime.time(10, 0)
        self.num_crinds = 15
        self.num_prepays = 5 # Prepays will be run on the last N dispensers. They must be set to auth amt if using fred's sim
        self.crind_threads = []
        self.stop_crinds = False
        with open("C:/Automation/run_info.json") as run_info_file:
            run_info = json.load(run_info_file)
            self.log_path = run_info['logs_dir']
            self.log_name = run_info['log_name']
            try:
                self.setup_edh = run_info['setup_edh'].lower() == 'true'
            except KeyError:
                self.setup_edh = True
        self.log_num = 1
        self.error_count = 0
        self.consecutive_errors = 0

    @setup 
    def setup(self):
        """Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        # Add reg key to bring us back after reboot
        runas.run_as(r"reg add HKLM\Software\Microsoft\Windows\CurrentVersion\Run "
                        "/v EnduranceAutomation /t REG_SZ /d %s /f \"python D:\Automation\test_harness.py -run endurance.py -var setup_edh:False\"")

        if self.setup_edh:
            crindsim.setup_edh(self.num_crinds, server.server.get_site_info()['ip'])
            edh = EDH.EDH()
            edh.setup()
            edh.enable_security()

        Navi.navigate_to("pos")
        pos.sign_on()

    @test
    def endurance(self):
        """Main endurance loop. Run repeated transactions and handle daily maintenance such as store closes.
        Args: None
        Returns: None
        """
        for i in range(self.num_crinds-self.num_prepays+1, self.num_crinds+1):
            crindsim.set_sales_target("auth", dispenser=i)
        self.dispatch_crind_threads(self.num_crinds-self.num_prepays)     
        self.loops_since_restart = 0
        while True:
            pass # remove me
            try:
                self.run_transactions()
                self.consecutive_errors = 0
            except AssertionError as e:
                self.error_count += 1
                self.consecutive_errors += 1
                self.log.error(f"!!! {e}")
                if self.consecutive_errors >= 5:
                    self.log.error("!!! Failed 5 transactions in a row. Trying to recover...")
                    system.takescreenshot()
                    pos.close()
                    system.restartpp()
                    pos.connect()
                    pos.sign_on()
                    self.consecutive_errors = 0
                    self.loops_since_restart = 0
                # TODO: Do something here to log a TC fail? Need to do it without ending the script.     
            self.message_check()
            self.serveralert_check()
            
            # Commented out for speed and because pos_recover doesn't seem to work properly
            #if not system.wait_for(pos.read_status_line, "Press the speed keys to enter items.", verify=False):
            #    self.log.warning("Didn't return to idle after running transactions. Trying to recover.")
            #    pos.pos_recover()

            now = datetime.datetime.now().time()
            if now >= self.close_time and now <= datetime.time(self.close_time.hour, self.close_time.minute+5):
                self.stop_crinds = True
                self.store_close()
                self.log.info(f"Current error count: {self.error_count}")
                self.zip_files()
                self.rotate_log()
                self.stop_crinds = False
                self.dispatch_crind_threads(self.num_crinds)

            # Restart Chrome every so often to work around a ChromeDriver memory leak
            # TODO: Remove this as soon as the leak is resolved. This workaround reduces our ability to identify long-term performance issues with the POS GUI
            if self.loops_since_restart >= 100:
                pos.close()
                pos.connect()
                self.loops_since_restart = 0

    def run_transactions(self):
        """Run a handful of indoor transactions."""
        # Speedkey sale
        assert pos.add_item("Generic Item", verify=False), "Failed to add item by speed key"
        assert pos.pay(verify=False), "Failed to pay out speed key transaction" 

        # Dept key sale
        assert pos.add_item("Dept 3", "Dept Key", price="$5.00", verify=False), "Failed to add item by dept key"
        assert pos.pay(verify=False), "Failed to pay out dept key transaction"

        # Car wash sale
        assert pos.add_item("1234", "PLU", qualifier="Carwash 1 ($5.00)", verify=False), "Failed to add car wash by PLU"
        assert pos.pay(verify=False), "Failed to pay out car wash transaction"

        try:
            for i in range(self.num_crinds-self.num_prepays+1, self.num_crinds+1):
                assert pos.add_fuel("10.00", i, verify=False), f"Failed to add prepay on dispenser {i}"
                assert pos.pay(verify=False), f"Failed to pay for prepay on dispenser {i}"
        except AssertionError as e:
            pos.click("GO BACK", verify=False)
            raise
        

    def dispatch_crind_threads(self, num_crinds):
        """Create threads to run CRIND transactions in parallel."""
        logging.getLogger("app.simulators.basesim").propagate = False # Silence logging from sim requests. Too spammy otherwise.
        logging.getLogger("app.simulators.crindsim").propagate = False
        self.stop_crinds = False
        del self.crind_threads
        self.crind_threads = []
        for i in range(num_crinds):
            # Dispatch a thread per CRIND
            self.crind_threads.append(threading.Thread(target=self.run_crind_transactions, name=f"CRIND {i+1}", args=[i+1], daemon=True))
            self.crind_threads[i].start()

    def run_crind_transactions(self, num):
        """Repeatedly run transactions against a given CRIND."""
        crindsim.open(num)
        crindsim.set_mode("auto", num)
        while not self.stop_crinds:
            time.sleep(random.randint(10, 30)) # Random interval between transactions. Adjust this?
            fuel_value = "%.2f" % (random.randint(500, 3000)/100) # Random target between $5.00 and $30.00
            crindsim.set_sales_target(sales_type="money", target=fuel_value, dispenser=num)
            if not system.wait_for(lambda: "Pay here" in crindsim.get_display_text(num), timeout=60, verify=False):
                self.log.warning(f"CRIND {num} not idle. Actual prompt: {crindsim.get_display_text(num)}")
                continue
            crindsim.swipe_card(dispenser=num)
            if not system.wait_for(lambda: "DEBIT" in crindsim.get_display_text(num), timeout=30, verify=False):
                self.log.warning(f"Didn't get debit prompt on CRIND {num}. Actual prompt: {crindsim.get_display_text(num)}")
                continue
            crindsim.press_softkey("No", dispenser=num)
            if not system.wait_for(lambda: "Carwash" in crindsim.get_display_text(num), timeout=30, verify=False):
                self.log.warning(f"Didn't get Carwash prompt on CRIND {num}. Actual prompt: {crindsim.get_display_text(num)}")
                continue
            crindsim.press_softkey("No", dispenser=num)
            if not system.wait_for(lambda: "receipt" in crindsim.get_display_text(num), timeout=60, verify=False):
                self.log.warning(f"Didn't get receipt prompt on CRIND {num}. Actual prompt: {crindsim.get_display_text(num)}")
                continue
            crindsim.press_softkey("No", dispenser=num)
            if not system.wait_for(lambda: "Thank you" in crindsim.get_display_text(num), timeout=120, verify=False):
                self.log.warning(f"Didn't get transaction complete prompt on CRIND {num}. Actual prompt: {crindsim.get_display_text(num)}")
                continue
            self.log.info(f"Sale of {fuel_value} completed on CRIND {num}.")

    def message_check(self):
        """Check for, log, and dismiss any unexpected POS popup messages."""
        msg = pos.read_message_box()
        if msg:
            self.log.error(f"!!! Got an unexpected popup message: {msg}")
            pos.click_message_box_key("OK", verify=False)

    def serveralert_check(self):
        """Check for, log, and dismiss any unexpected server alerts."""
        try:
            app = pywinauto.application.Application().connect(title_re="SERVER ALERT")
        except pywinauto.ElementNotFoundError:
            return
        win = app["SERVER ALERT"]
        msg = "%s\n%s" % (win['Static2'].texts()[0],
                          win['Static3'].texts()[0].replace('\n', ' '))
        self.log.error(f"!!! Got a server alert: {msg}")
        win["Clear Alert"].click()

    def store_close(self):
        """Perform a store close."""
        assert store_close.StoreClose().begin_store_close()
        assert Navi.navigate_to("pos")
        assert pos.sign_on()
        return True

    def clear_cw_codes(self):
        """Clear the list of car wash codes on the EDH, to prevent maxing out the file size."""
        result = runas.run_sqlcmd(r"del C:\Passport\Testers\CarwashCodeDB.csv")
        if "NULL" not in result['output']:
            self.log.error("Failed to clear car wash codes. Output: %s" % result['output'])
        else:
            self.log.info("Cleared car wash codes.")

    def zip_files(self):
        """Collect and compress logs and other information."""
        from zipfile import ZipFile
        import glob
        
        file_format = time.strftime("%Y%m%d")
        eps_hc = "C:\\EPSFiles\\HC\\"
        mws_hc = "C:\\Gilbarco\\HCReport\\"
        edh_logs = "C:\\EPSFiles\\Logs\\"
        sr_alerts = "C:\\Gilbarco\\ServerAlerts\\"
        sr_pending = "C:\\Gilbarco\\PendingAlerts\\"
        mws_logs = "D:\\Gilbarco\\logs\\"
        with ZipFile("%s\\%s.zip"%(self.log_path, self.log_name.strip(".log"))
                     , 'w') as my_zip:
            self.log.info("Finding and Zipping anything with "
                                    "ServerAlerts")
            file_list = glob.glob("%s*.xml"%sr_alerts)
            if len(file_list) > 0:
                for thing in file_list:
                    my_zip.write(thing)
            file_list = glob.glob("%s*.xml"%sr_pending)
            if len(file_list) > 0:
                for thing in file_list:
                    my_zip.write(thing)
            self.log.info("Zipping the EPS Health Check")
            file_list = glob.glob("%s*"%eps_hc)
            latest_file = max(file_list, key=os.path.getctime)
            my_zip.write(latest_file)
            self.log.info("Running MWS Health Check")
            if runas.run_as("C:\\Gilbarco\\Tools\\HealthCheck.exe") == -1:
                self.log.info("HealthCheck.exe did not work properly "
                                        "or moved directories.")
            else:
                self.log.info("Zipping the MWS Health Check.")
                file_list = glob.glob("%s*"%mws_hc)
                latest_file = max(file_list, key=os.path.getctime)
                my_zip.write(latest_file)
            self.log.info("Running CollectEPSLogs")
            epslogs_result = runas.run_as("C:\\Gilbarco\\Tools\\CollectEPSLogs.exe")
            if epslogs_result['pid'] == -1:
                self.log.info("CollectEPSLogs.exe did not work properly "
                                        "or moved directories.")
            else:
                self.log.info("Zipping the EDH logs zip file.")
                if "Timeout waiting FTP Pull of logs" in epslogs_result['output']:
                    self.log.info("CollectEPSLogs failed to transfer logs, "
                                            "probably due to pbugs57367. "
                                            "Transferring them manually. ")
                    dir_output = runas.run_sqlcmd("dir D:\\Gilbarco\\LogArchive")['output']
                    dir_list = dir_output.split("\n")
                    epslog_name = None
                    for item in dir_list:
                        if "PASSPORTEPS.zip" in item:
                            epslog_name = item.split(" ")[13]
                            break
                    if epslog_name is None:
                        self.log.error("Couldn't find log archive on EDH.")
                    else:
                        runas.run_as("C:\\Gilbarco\\Tools\\EDHUtil.exe /action="
                                       "GetFileFromEDH /edhhost=10.5.50.2 /source="
                                       "D:\\Gilbarco\\LogArchive\\%s /destination="
                                       "C:\\EPSFiles\\Logs\\%s" % (epslog_name, epslog_name))
                file_list = glob.glob("%s*"%edh_logs)
                latest_file = max(file_list, key=os.path.getctime)
                my_zip.write(latest_file)
            self.log.info("Getting the yesterday's and today's perfmon "
                                    "logs through edhutil")
            perfmon_dir = "D:\\Gilbarco\\Logs\\"
            eps_dir = "C:\\EPSFiles\\"
            yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
            today = datetime.datetime.now().strftime("%m%d")
            perfmon_list = self.get_perfmon_files()
            command = "C:\\Gilbarco\\Tools\\edhutil "\
                    "/action=GetFileFromEDH "\
                    "/edhhost=10.5.50.2 "\
                    "/source=%s%s "\
                    "/destination=%s%s"
            for item in perfmon_list:
                runas.run_as(command%(perfmon_dir, item, eps_dir,
                                        item))
                my_zip.write("%s%s"%(eps_dir, item))
            file_list = []
            for x in glob.glob("%sperfmon_%s*.blg"%(mws_logs, today)):
                file_list.append(x)
            for x in glob.glob("%sperfmon_%s*.blg"%(mws_logs,
                                                    yesterday.strftime("%m%d"))):
                file_list.append(x)
            for item in file_list:
                my_zip.write(item)
            self.log.info("Zipping the automation event logs.")
            try:
                my_zip.write("%s\\%s"%(self.log_path, self.log_name))
            except Exception as e:
                self.log.error(e.message)
        self.log.info("Zip file has been created.")
        return True

    def get_perfmon_files(self):
        #Getting a list of all of the perfmon logs on the edh.
        edh_perfmon = runas.run_sqlcmd("dir /s D:\\Gilbarco\\Logs\\*.blg")
        #Retreiving the last two days worth of perfmon logs.
        today = datetime.datetime.today().strftime("%m%d")
        yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
        yesterday = yesterday.strftime("%m%d")
        perfmon_today = "perfmon_%s" %today
        perfmon_yest = "perfmon_%s" %yesterday
        output_list = edh_perfmon['output'].split('\n')
        perfmon_list = []
        for item in output_list:
            new_item = item.split(" ")
            for file_name in new_item:
                if perfmon_today in file_name or perfmon_yest in file_name:
                    perfmon_list.append(file_name)
        return perfmon_list

    def rotate_log(self):
        """Start a fresh log for the new day."""
        self.log_num += 1
        log_verbosity = logging.getLogger().getEffectiveLevel()
        exceptionLog = logging.getLogger("exceptionLog")
        exceptionLog.setLevel(logging.CRITICAL)
        exceptionLog.propagate = False

        self.log_name = self.log_name[:-6] + self.log_name[-4:] # Remove existing number
        filename_split = self.log_name.split('.')
        self.log_name = f"{filename_split[0]}_{self.log_num}.{filename_split[1]}"
        new_filepath = f"{self.log_path}/{self.log_name}"
        #Configure the FileHandlers
        fh = logging.FileHandler(new_filepath)
        fh.setLevel(log_verbosity)

        exceptionfh = logging.FileHandler(new_filepath)
        exceptionfh.setLevel(logging.CRITICAL)
    
        #Configure and set the Formatters
        formatter = logging.Formatter('[%(asctime)s]: [%(levelname)s] %(message)s',
                                    '%m/%d/%Y %I:%M:%S %p')
        fh.setFormatter(formatter)
    
        exceptionFormatter = logging.Formatter('%(message)s')
        exceptionfh.setFormatter(exceptionFormatter)

        console_logger = logging.StreamHandler(stream=sys.stdout)
        console_logger.setFormatter(formatter)

        error_console_logger = logging.StreamHandler()
        error_console_logger.setFormatter(exceptionFormatter)
    
        #Add the configured FileHandler to the logger
        self.log.handlers = [fh, console_logger]
        exceptionLog.handlers = [exceptionfh, error_console_logger]
    
    def write_result(status="pass"):
        """Write a TC result without ending the TC. Unfinished. Add support in test harness?"""
        from test_harness import res, end_test
        delta = time.time()-start_time
        m, s = divmod(delta, 60)
        h, m = divmod(m, 60)
        test_file = f'scripts/features/{test}'
        run_time = f"{int(h):02}:{int(m):02}:{int(s):02}"

        base_file_name = os.path.basename(test_file)
        class_name = base_file_name.replace('.py', '')
        res = Results(system.get_brand(), system.get_version(), 1, class_name, 
                      
                      
                      
                      
                      
                      ["results_dir"])
        res.record(test.__name__, base_file_name, docstr[0], status, run_time)
        end_test(run_info, test.__name__, status == "pass", str(e))

    def add_item(self, item="Generic Item", method="Speed Key", price=None, qualifier=None):
        """
        Add an item to the current transaction. (from pos.py, trimmed down for speed)
        Args:
            item: (str) The name or PLU of the item.
            method: (str) The method of item entry. Can be PLU, Speed Key, or Dept Key.
        Return:
            bool: True on success, False on failure.
        Examples:
            >>> add_item()
            True
            >>> add_item("101", method="PLU")
            True
            >>> add_item("Dept 13", method="Dept Key")
            True
        """
        if method.upper() == "SPEEDKEY" or method.upper() == "SPEED KEY":
            if not pos.click_speed_key(item, verify=False):
                return False
        elif method.upper() == 'DEPT KEY':
            if price is None:
                self.log.warning("Price must be specified for Department Key entry.")
                return False
            if not pos.click_dept_key(item, verify=False):
                return False
        elif method.upper() == 'PLU':
            pos.enter_keypad(item, verify=False)
            pos.click_keypad("PLU", verify=False)
        else:
            self.log.warning(f"Invalid method for add_item: '{method}'")
            return False

        if qualifier is not None:
            pos.select_list_item(qualifier, verify=False)
            pos.click_keypad("ENTER", verify=False)

        if price is not None:
            price = price.replace("$", "").replace(".", "")
            pos.enter_keypad(price, verify=False)
            pos.click_keypad('ENTER', verify=False)

        return True

    def add_fuel(self, amount, dispenser=1, mode="Prepay", grade="REGULAR", level="CASH"):
        """
        Add fuel to the current transaction. (from pos.py, trimmed down for speed)

        Args:
            amount: (str) Dollar amount of fuel to purchase.
            dispenser: (int) Number of the dispenser to purchase fuel on.
            mode: (str) Prepay, preset, or manual.
            grade: (str) The fuel grade to select.
            level: (str) Cash/Credit pricing level.

        Return: 
            bool: True on success, False on failure.

        Examples:
            >>> add_fuel("$20.00", 3)
                True
            >>> add_fuel("$11.11", 4, "Manual", "SUPREME", "Credit")
                True
        """
        # Add fuel
        if not pos.select_dispenser(dispenser, verify=False):
            return False
        if not pos.click_forecourt_key(mode.upper(), verify=False):
            return False
        if mode.upper() != "PRESET" and not pos.click_prepay_key(grade.upper(), verify=False):
            return False
        if mode.upper() == 'MANUAL':
            if not pos.click_prepay_key(f"{level} LEVEL", verify=False):
                self.log.debug("Failed to click the CASH LEVEL button. Later verification will catch if this was an issue")
        stripped_amount = amount.replace("$", "").replace(".", "")
        if not pos.enter_keypad(stripped_amount, verify=False):
            return False
        if not pos.click_keypad('ENTER', verify=False):
            return False

        return True

    def pay(self, amount="exact change", tender_type="cash"):
        """
        Add payment for the current transaction. (from pos.py, trimmed down for speed)
        Args:
            amount: (str) How much to pay if not using card. Default is exact change.
            tender_type: (str) Type of tender to select.
        Returns:
            bool: True if success, False if fail
        Examples:
            >>> pay()
            True
            >>> pay(amount="$5.00", tender_type="Check")
            True
        """
        # Find out how much we need to pay
        refund = False
        balance = pos.read_balance()
        try:
            total = balance['Total']
        except KeyError:
            try:
                total = balance['Refund Due']
                refund = True
            except KeyError:
                self.log.warning("There is no balance to pay out.")
                return False
            
        # Get to tender screen
        self.log.debug("Attempting to click the Tender/Pay button")
        if not pos.click_function_key("pay", verify=False):
            return False
        # Handle loyalty
        msg = pos.read_message_box(timeout=5)
        if msg is not None and "ID" in msg:
            if not pos.click_message_box_key('NO', verify=False):
                pos.click_keypad("CANCEL")
                return False
        # Select tender type
        self.log.debug("Selecting the Tender Type")
        while not pos.click_tender_key(tender_type, verify=False):
            if not pos.click_tender_key('more', verify=False):
                self.log.warning("The tender type %s does not exist."
                                             %(str(tender_type)))
                return False

        # Select or enter tender amount
        if not pos.click_tender_key(amount, timeout=1, verify=False):
            amount_to_enter = amount.replace("$", "").replace(".", "")
            self.log.setLevel(temp_level)
            for num in amount_to_enter:
                pos.click_keypad(num, verify=False)
            pos.click_keypad("ENTER", verify=False)      

        return True

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        self.stop_crinds = True

        #if not system.restore_snapshot():
        #    self.log.debug("No snapshot to restore, if this is not expected please contact automation team")