import logging, datetime, re, calendar
from app import mws, Navi, system

class XMLRepollFiles:
    """
    The class representing the XML Repoll Files
    window in Set Up -> Store -> Back Office section of MWS.


    The class has a repoll method that repolls a report or reports
    from a store or a shift close from a certain period of time based
    on the parameters provided by a user.
    """

    def __init__(self):
        """
        Set up mws connection.
        """
        self.log = logging.getLogger()
        XMLRepollFiles.navigate_to()
        return

    @staticmethod
    def navigate_to():
        """
        Navigates to the XML Repoll Files menu.
        Args:
            None
        Returns:
            Returns the result of execution of Navi.navigate_to()
        """
        return Navi.navigate_to("XML Repoll Files")


    def repoll(self, date, time, files=None, event='store close'):
        """
        Configures the fields accessible in the
        XML Repoll Files window according to the provided
        dictionary.
    
        Args:
            date: (string) a string specifying the desired date for repolling
            time: (tuple) a tuple with (starting time, ending time) string specifying the desired period of time for repolling
            files: (list) a list of files to repoll. Deafults to None. If set to None, all files available are repolled.
            event: (str) a string indicating the event ('store close' or 'shift close') to use for repolling
        
        Returns:
            True: If XML Repoll Files was successfully set up.
            False: If something went wrong while setting up XML Repoll Files (will be logged).
        Example:
            # Assuming the shift close was performed on 07/03/2019
            >>> repoll('07/03/2019', ('00:00 AM', '11:59 PM'), event='shift close')
                True
            >>> repoll('07/03/2019', ('00:00 AM', '11:59 PM'), files=['Fuel Product Movement'], event='shift close')
                True
        """
        # Assuming no action were performed after the window opened
        # The calendar should be set to today's date
        self._pick_calendar_date(date)

        # Select the event
        if not mws.select_radio(event.title()):
            self.log.error(f"Unable to select the target event '{event.title()}'")
            return False

        # Select time period
        if not mws.select("Choose a Period of Time", time):
            self.log.error(f"Unable to select a target time period {time}")
            return False

        # Check the target files
        if not files:
            # All files are to be repolled
            if not mws.select_radio("Repoll All Configured Files"):
                self.log.error(f"Unable to select 'Repoll All Configured Files' option.")
                return False
        else:
            # Some files are to be repolled
            # Convert the list to the dictionary
            files_dic = {}
            for file in files:
                files_dic[file] = True

            # Reset the current status of the files in the list and select target files
            if not ( mws.select_radio("Repoll All Configured Files") and mws.select_radio("Repoll Selected Files") ):
                self.log.error(f"Unable to select 'Repoll Selected Files' option.")
                return False
            
            if not mws.config_flexgrid("XML Document List", files_dic, 500):
                self.log.error(f"Unable to set the repoll status for the provided files")
                return False
        
        # Click Ok and we are done (probably)
        try:
            mws.click_toolbar("Save", main=True, main_wait=3)
        except mws.ConnException:
            # Check for top bar message
            top_bar_message = mws.get_top_bar_text()
            if top_bar_message:
                self.log.error("Unable to save ")
                self.log.error(f"Unexpected top bar message is '{top_bar_message}'")
                system.takescreenshot()
                mws.click_toolbar("Ok")
        
        return True
    
    def _pick_calendar_date(self, date, color='0000A0'):
        """
        Selects the date in the calendar popup based on the provided parameters.
        Args:
            date: (str) the date string. It accepts following formats and the combinations of them: '01/01/1981', '1/1/1981'
            color: (str) the color of the text of the date in the calendar. Defaults to blueish
        Returns:
            True: if the operation is a success
            False: if there were errors in the proccess
        Example:
            >>> date = "06/24/2019"
            >>> pick_calendar_date(date)
                True
        """

        # Check if the date is supplied in correct format
        # mm/dd/yyyy
        if not re.match(r'^\d{1,2}\/\d{1,2}\/\d{4}$', date):
            self.log.error(f"The provided date '{date}' is invalid. It should follow mm/dd/yyyy format")
            return False
        
        # Get calendar control
        calendar_ctrl = mws.get_control("Choose a Date to Repoll")
        
        # Introduce the signum function
        sign = lambda x: (-1, 1)[ x > 0]

        current_date = datetime.date.today().strftime("%m/%d/%Y")

        # Check if the current date is the target date
        # If it is not, select correct date
        if date != current_date:
            # Start date
            month, day, year = date.split('/')

            # Get rid of padding 0's if they are present
            month = int(month)
            day = int(day)

            # Check which day is currently selected
            current_day = int(current_date.split('/')[1])

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