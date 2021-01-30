from app import mws, system, Navi
import logging, time, os

class ShiftClose:
    """
    The class that represents the "Shift Close" window in the
    Period Close tab in MWS.
    It provides the functionality for initiating the Shift Close process and
    verifies that the process completes successfully.
    """
    # Shift Close process name
    SHIFTCLOSE_PROC = "shiftchange.exe"

    # The dictionary of some of expected  fields
    REPORT_SUCCESS = [
        ['Site Shift Change', 'Begin Shift Change'],
        ['Site Shift Change', 'Completed.']
    ]
    
    def __init__(self):
        self.log = logging.getLogger()
        ShiftClose.navigate_to()
        return
    
    @staticmethod
    def navigate_to():
        """
        Navigates to the Shift Close menu.
        Args:
            None
        Returns:
            Returns the result of execution of Navi.navigate_to()
        """
        return Navi.navigate_to("shift close")

    def begin_shift_change(self, timeout=10*60):
        """
        Initiates the Shift Close process.
        The function verifies that report has completion status "Completed" and
        Shift Change is performed without errors.
        In the end, it navigates out to "MWS."
        Args:
            None
        Returns:
            The list of report rows if the process is a success. Otherwise, logs the 
            the report fields' statuses and returns None.
        Examples:
            The successful report looks like this:
            [
                ['Site Shift Change', 'Begin Shift Change'],
                ....
                ['Site Shift Change', 'Completed.']
            ]

            >>> begin_shift_change()
                Shift Close was performed successfully
                [
                    ['Site Shift Change', 'Begin Shift Change'],
                    ....
                    ['Site Shift Change', 'Completed.']
                ]
        """

        if not mws.click_toolbar("Begin Shift Change"):
            self.log.error(f"Unable to initiate Shift Close")
            mws.click_toolbar("Exit", timeout=10)
            return False

        # Create a flag indicating full match
        # The status changes to True if at least one field does not match
        report_error = False

        # Wait for report to be done
        # Create timeout timer
        start_time = time.time()
        while time.time() - start_time <= timeout:
            # Get current report status
            # Go over the fields of interest and verify that it's completed
            report = mws.get_text("list")

            # Check if report has anything in it
            if len(report) < 2:
                continue

            # Check first and last rows to verify success status
            row_first = report[0]
            row_last = report[-1]

            if row_first[0] != self.REPORT_SUCCESS[0][0] and row_first[1] != self.REPORT_SUCCESS[0][1]:
                self.log.error(f"Invalid field \'{row_first[0]}\' with status \'{row_first[1]}\'")
                report_error = True

            if row_last[0] != self.REPORT_SUCCESS[1][0]:
                continue
            elif row_last[1] != self.REPORT_SUCCESS[1][1]: # Check status
                self.log.error(f"The report was finished with unexpected status \'{row_last[1]}\'")
                report_error = True
                break
            else:
                break

        else:
            self.log.error(f"Exceeded timout for waiting for Shift Close report to finish")
            system.takescreenshot()

            # Terminate process and recover
            self.log.warning(f"Terminating process \'{self.SHIFTCLOSE_PROC}\' after a timeout and performing recovery")
            os.system(f"taskkill /f /im {self.SHIFTCLOSE_PROC}")
            system.restartpp()
            return None
        
        # Get report
        report = mws.get_text("list")

        # Check for error flag
        if report_error:
            # Report the fields
            self.log.info("The report fields are the following:")
            for row in report:
                # ['Field Name', 'Status']
                self.log.info(f"\t\'{row[0]}\' with status \'{row[1]}\'")

            # Abort
            self.log.error(f"Shift Close terminated with errors")
            system.takescreenshot()

            if not mws.click_toolbar("Exit"):
                self.log.error(f"Unable to exit Shift Close window")
                mws.recover()

            return None

        # No errors
        self.log.info(f"Shift Close was performed successfully")
        if not mws.click_toolbar("Exit"):
            self.log.error(f"Unable to exit Shift Close window. Initiating recovery")
            system.takescreenshot()
            mws.recover()
            return None
        
        return report