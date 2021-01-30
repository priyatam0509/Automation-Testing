from app import mws, system, Navi
import logging, time, os

class StoreClose:
    """
    The class that represents the "Store Close" window in the
    Period Close tab in MWS.
    It provides the functionality for initiating the Shift Close process and
    verifies that the process completes successfully.
    """

    # Shift Close process name
    STORECLOSE_PROC = "STOREC~1.exe"

    # Valid popup messages upon start of the store close
    POPUP_MSG = [
        "Are you sure you want to start Store Close?",
        "It is not time to close the store! Do you wish to close anyway?"
    ]

    # Successful store close report
    REPORT_SUCCESS = [
        ['Ok', 'Restart XMLGateway'],
        ['Ok', 'Store Closing Procedures'],
        ['Ok', 'Report: Store Close Reports'],
        ['Ok', 'Report: Shift Close Reports'],
        ['Ok', 'Report: Network Shift Reports'],
        ['Ok', 'Report: Network Batch Reports'],
        ['Ok', 'Package Store Close Reports'],
        ['', ''],
        ['', '** Store Close Batch Completed **']
    ]
    
    def __init__(self):
        self.log = logging.getLogger()
        StoreClose.navigate_to()
        return

    @staticmethod
    def navigate_to():
        """
        Navigates to the Store Close menu.
        Args:
            None
        Returns:
            Returns the result of execution of Navi.navigate_to()
        """
        return Navi.navigate_to("Store Close")

    def begin_store_close(self, timeout=15*60):
        """
        Initiates the Store Close process.
        The function verifies that all steps have completion status "Completed" and
        Store Close is performed without errors.
        In the end, it navigates out to "MWS."
        Args:
            timeout: (int) the timeout of execution in seconds
        Returns:
            The list with the rows of the report upon success or None otherwise.
        Examples:
            The successful report looks like this:
            [
                ['Ok', 'Restart XMLGateway'],
                ['Ok', 'Store Closing Procedures'],
                ['Ok', 'Report: Store Close Reports'],
                ['Ok', 'Report: Shift Close Reports'],
                ['Ok', 'Report: Network Shift Reports'],
                ['Ok', 'Report: Network Batch Reports'],
                ['Ok', 'Package Store Close Reports'],
                ['', ''],
                ['', '** Store Close Batch Completed **']
            ]

            >>> begin_store_close()
                Store Close was performed successfully
                [ ... ]
        """
        if not mws.click_toolbar("Start"):
            self.log.error(f"Unable to initiate Store Close")
            mws.recover()
            return None

        # Respond to popup
        if mws.get_top_bar_text() in self.POPUP_MSG:
            mws.click_toolbar("YES")
        else:
            self.log.error(f"Unexpected message encountered in the top bar: \'{mws.get_top_bar_text()}\'")
            system.takescreenshot()
            mws.recover()
            return None

        # Check for the process that connects to registers and closes networks
        # Create timeout
        start_time = time.time()
        while time.time() - start_time <= timeout:
            if system.process_wait("STOREC~1.exe", timeout=1):
                break
        else:
            # Terminate process and recover
            self.log.warning(f"Terminating process \'{self.STORECLOSE_PROC}\' after a timeout and performing recovery")
            os.system(f"taskkill /f /im {self.STORECLOSE_PROC}")
            mws.recover()
            system.restartpp()
            return None
        
        # Wait for register and network communication to finish
        # Create timeout
        while time.time() - start_time <= timeout:
            if not system.process_wait("STOREC~1.exe", timeout=1):
                break
        else:
            # Terminate process and recover
            self.log.warning(f"Terminating process \'{self.STORECLOSE_PROC}\' after a timeout and performing recovery")
            os.system(f"taskkill /f /im {self.STORECLOSE_PROC}")
            mws.recover()
            system.restartpp()
            return None

        # Wait for report engine
        while time.time() - start_time <= timeout:
            if not system.process_wait("reportengine.exe", timeout=1):
                break
        else:
            self.log.error(f"Exceeded timout for waiting for Store Close process (reportengine.exe) to start")
            # Terminate process and recover
            self.log.warning(f"Terminating process \'{self.STORECLOSE_PROC}\' after a timeout and performing recovery")
            os.system(f"taskkill /f /im {self.STORECLOSE_PROC}")
            mws.recover()
            system.restartpp()
            return None
        
        # Connect to the Store Close window with actual report
        mws.connect("Store Close")

        report = None

        # Wait for report to be done
        # Create timeout timer
        while time.time() - start_time <= timeout:
            # Get current report status
            # Go over each field and verify that it's completed
            report = mws.get_text("list")

            # Check number of rows. If less, report must be in progress
            if len(report) >= len(self.REPORT_SUCCESS): # Using >= just in case
                break
        else:        
            self.log.error(f"The wait time for report to finish exceeded {timeout} minutes")

        # Check number of rows
        if len(report) != len(self.REPORT_SUCCESS):
            self.log.error("The Store Close report has different number of rows than expected")

        # Flag indicating that error was found
        error_report = False

        # Check every field
        for i in range(0, len(report)):
            # ['Status', 'Field Name']
            row = report[i]

            # Check name of the field
            if self.REPORT_SUCCESS[i][1] == row[1]:
                # Check status
                if row[0] != self.REPORT_SUCCESS[i][0]:
                    # The status differs from "successful" status
                    self.log.error(f"The status of the field \'{row[1]}\' is \'{row[0]}\' but \'{self.REPORT_SUCCESS[i][0]}\' was expected")
                    error_report = True
            else:
                self.log.error(f"Encountered a field \'{row[1]}\' in Store Close Report when \'{self.REPORT_SUCCESS[i][1]}\' was expected")
                error_report = True
                continue

        if error_report:
            self.log.error("Store Close terminated with errors")
            system.takescreenshot()
            mws.recover()
            return None

        self.log.info("Store Close report performed successfully")
        mws.click_toolbar("EXIT")
        return report