import re, os, datetime, calendar, logging,time

from app import Navi, mws, system

log = logging.getLogger()

TODAY = "today"

class ReportMenu():
    """
    A class for connecting to and interacting with report menus.
    """
    
    def __init__(self, menu):
        self.menu = menu
        Navi.navigate_to(menu)

    def get_report(self, report,networkselection = None, *args, **kwargs):
        """
        Search for a report and print preview it.
        Args:
            report: (str) The name of the report to retrieve.
            *args/**kwargs: These vary depending on the report's search criteria. 
                            See the submenu class for the desired report for full documentation.
        Returns:
            bool: Whether the process completed successfully
        Example:
            >>> ReportMenu("Accounting").get_report("Till Report", period="Current")
            True
            >>> ReportMenu("Network").get_report("EMV Configuration")
            True
        """
        log.info("Checking if menu is network")
        if self.menu == "Network":
            start_time = time.time()
            while time.time()-start_time <= 20:
                get_report_message =  mws.get_text("Network Reports")
                if (get_report_message != None):
                    mws.process_conn["ListView1"].select(networkselection)
            mws.click_toolbar("Select")
            while time.time()-start_time <= 20:
                report_list = mws.get_text(networkselection +" Reports")
                if (report_list != None):
                    mws.process_conn["ListView1"].select(report)
            mws.click_toolbar("Select")
        else:
            mws.process_conn["ListView1"].select(report)
            mws.click_toolbar("Select")


        submenu_obj = _get_submenu_obj()
        log.info(f"Using submenu class {submenu_obj.__class__.__name__}")
        #Validate if selection criteria is present on function
        if (args or kwargs):
            try:
                if not submenu_obj.set_criteria(*args, **kwargs):
                    log.warning(f"Failed setting criteria for {report} report.")
                    return False
            except TypeError:
                log.warning(f"See reports.{submenu_obj.__class__.__name__} for arg documentation.")
                raise
        mws.click_toolbar("Print Preview")
        return True

###################
# Submenu classes #
###################

"""
These classes are used to handle selection criteria for reports. 
"""

class ReportSubmenu():
    """
    A class for interacting with report submenus which do not have
    any report selection criteria, such as Forecourt Configuration and Network Current Day reports.
    This is the base class for submenus; all other submenu classes should extend it.
    """
    def __init__(self):
        return

    def set_criteria(self):
        """
        Set report selection criteria.
        Since these menus have none, this function is empty.
        To be overridden by classes for menus that do have selection criteria.
        Args: None
        Returns: True
        """
        return True

class CalendarReportSubmenu(ReportSubmenu):
    """
    A class for interacting with report submenus containing a calendar and period selection, such as
    Till Report and Fuel Sales Details.
    All classes for reports that use calendar selection should extend this class.
    """
    def __init__(self):
        super().__init__()

    def set_criteria(self, period=None, date=TODAY, period_type=None):
        """
        Set selection criteria for the report.
        Args:
            period: (str/list) The element to select from the list of periods. Defaults to the first list item.
            date: (str) The date to select on the calendar in MM/DD/YYYY format. Defaults to today's date.
            period_type: (str) The entry to select from the "Choose a period type" drop-down.
        """
        if period_type:
            if not mws.set_value("Choose a period type", period_type):
                return False
        if not self._pick_calendar_date(date):
            return False

        try:
            if period:
                mws.set_value("Business Day", period)
        except AttributeError:
            log.warning(f"Couldn't find period selection window. This likely means there were no reports available for date {date}.")
            mws.click_toolbar("Exit")
            return False

        return True

    def _pick_calendar_date(self, date, color='0000A0', bbox=(396, 281, 695, 497) if mws.is_high_resolution() else (300, 183, 602, 401)):
        """
        Selects the date in the calendar popup based on the provided parameters.
        Args:
            date: (str) the date string. It accepts following formats and the combinations of them: '01/01/1981', '1/1/1981'
            color: (str) the color of the text of the date in the calendar. Defaults to blueish
            bbox: (tuple) the tuple of coordinates bounding the calendar box (lef top right bottom)
        Returns:
            True: if the operation is a success
            False: if there were errors in the proccess
        Example:
            >>> date = "06/24/2019"
            >>> pick_calendar_date(date)
            True
            >>> date = "7/24/2019"
            >>> pick_calendar_date(date)
            True
        """
        if date == TODAY:
            return mws.click("Calendar Today")

        # Check if the date is supplied in correct format
        # mm/dd/yyyy
        if not re.match(r'^\d{1,2}\/\d{1,2}\/\d{4}$', date):
            self.log.error(f"The provided date '{date}' is invalid. It should follow mm/dd/yyyy format")
            return False
        
        # Get calendar control
        calendar_ctrl = mws.get_control("Calendar Day")
        
        # Apply changes of the currently selected date
        calendar_ctrl.click()
        
        # Introduce the signum function
        sign = lambda x: (-1, 1)[ x > 0]

        # Start date
        month, day, year = date.split('/')

        # Get rid of padding 0's if they are present
        month = int(month)
        day = int(day)

        # Check which day is currently selected
        current_day = int(datetime.datetime.today().day)

        # Set day

        # Determine how far apart the target andcurrent days are
        shift = day - current_day

        # Finc if the target is before or after the current day
        direction = sign(shift)

        # Shift the selection to the target day 
        while shift != 0:
            # Shift left if the target is before
            # Shift right if the target is after
            calendar_ctrl.type_keys('{VK_LEFT}') if direction == -1 else calendar_ctrl.type_keys('{VK_RIGHT}')
            shift = shift + 1 if direction == -1 else shift - 1
            
        # Set month
        if not mws.set_value("Calendar Month", calendar.month_name[int(month)]):
            self.log.error(f"Could not set calendar month to '{calendar.month_name[int(month)]}'.")
            return False

        # Set year
        if not mws.set_value("Calendar Year", year):
            self.log.error(f"Could not set calendar year to '{year}'.")
            return False
            
        # Apply changes
        calendar_ctrl.click()
       
        # Done
        return True

class CalendarGroupingReportSubmenu(CalendarReportSubmenu):
    """
    A class for interacting with report submenus containing calendar period selection
    as well as a grouping option, such as POS Day Report.
    """
    def __init__(self):
        super().__init__()

    def set_criteria(self, parameters=None, *args, **kwargs):
        if parameters:
            if not mws.set_value("Parameters", parameters):
                return False
        return super().set_criteria(*args, **kwargs)

def get_network_report_path(timeout=30):
    """
    Get the file path for a network report
    """
    reports_path = "C:\\Passport\\Reports\\"
    # Looks like only the currently viewed report ever lives in here, so just grab the first file
    if not system.wait_for(lambda: len(os.listdir(reports_path)) > 0, timeout=timeout, verify=False):
        log.warning(f"Report file not found within {timeout} seconds.")
        return None
    files = os.listdir(reports_path)
    if len(files) > 1: # Just in case my assumption is wrong
        log.warning(f"Unexpectedly found more than one file in {reports_path}. Returning the first one...")
    return reports_path + files[0]

####################
# Helper functions #
####################

def _get_submenu_obj():
    """
    Instantiate a submenu object, deciding which one to use via reading screen text.
    Args: None
    Returns:
        ReportSubmenu: a suitable submenu object for the report submenu we are currently viewing
    Example:
        >>> _get_submenu_obj()
        <app.features.reports.CalendarReportSubmenu object at 0x039D8A30>
    """
    if mws.find_text_ocr("Choose A Date", timeout=5):
        if mws.find_text_ocr("Select a Group"):
            return CalendarGroupingReportSubmenu()
        return CalendarReportSubmenu()

    return ReportSubmenu() # default

def _get_report_contents(report_name, menu):
    """
    Get the contents of a report. PDF reports are not supported.
    Args:
        report_name: The name of the report to get.
        menu: The menu that the report lives in.
    Returns:
        str: The raw contents of the report.
    """
    if menu.lower() == "network":
        log.warning("Getting contents of PDF reports is unsupported.")
        return None

    return _get_html_report_contents(report_name)

def _get_html_report_contents(report_name, timeout=30):
    """
    Get the contents of an HTML report (most reports)
    """
    reports_path = "C:\\Passport\\advpos\\Reports\\eng\\html\\"
    report_filename = report_name.replace(' ', '') + '.htm' # Does this work for all non-network reports?
    log.info(f"Opening report {report_filename}")
    if not system.wait_for(lambda: report_filename in os.listdir(reports_path), timeout=timeout, verify=False):
        log.warning(f"Report file not found within {timeout} seconds.")
        return None
    with open(reports_path + report_filename, 'r') as report_file:
        return report_file.read()