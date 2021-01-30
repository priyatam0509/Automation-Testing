from app import mws, system, Navi
import logging, time, calendar, re

class Clock_Adjustment:
    """
    The class representing the Clock In/Out Adjustment
    window in Accoutning section of MWS.
    The functionality should be activated in Store Options
    prior to use.
    The class allows to select a day or a range of days for the employee 
    to add, change, or delete the clock in/out entries
    based on the configuration dictionary provided to it
    by user.
    """

    def __init__(self):
        self.log = logging.getLogger()
        Clock_Adjustment.navigate_to()

    @staticmethod
    def navigate_to():
        """
        Navigates to the Clock In/Out Adjustment menu.

        Returns:
            Returns the result of execution of Navi.navigate_to()
        """
        return Navi.navigate_to("Clock In/Out Adjustment")

    def add(self, params):
        """
        Adds the clock in/out entry for the specified employee based on the provided parameters.

        Args:
            params: (dict) the dictionary containing information about the employee,
                    date (or range) and clock in/out info.
                    If only one list element for 'date' is provided, the time is not needed.
                    Date accepts following formats and the combinations of them: '01/01/1981', '1/1/1981'.
                    The 'time' dictionary works with clock in, clock out, or both entries.
                    The time should follow the 'HH:MM AM' format

        Returns:
            True: if the operation is a success
            False: if there are errors in the proccess

        Example:
            params = {
                # If time is not provided, default values are used instead.
                # One day instead of two is also accepted.
                "date" : [["06/09/2019", "02:25 AM"], ["06/26/2019", "11:59 AM"]],
                "employee" : "91-Area Manager",
                "time" : {
                    "clock in" : ["06/19/2018", "11:45 AM"],
                    "clock out" : ["06/19/2018", "12:02 PM"]
                }
            }
            >>> add(params)
                True
            >>> add(params)
                Clock Out time needs to be less than next clock in time
                False
        """
        if not self._select(params):
            return False

        # New entry
        if not mws.click_toolbar("Add"):
            self.log.error("Unable to click 'Add' for the given range")
            system.takescreenshot()
            return False

        if not self._modify_entry(params['time']):
            return False

        # Navigate out
        if not mws.click_toolbar('Back'):
            self.log.error(f"Unable to click 'Back' to return to the main menu.")
            return False

    def change(self, params):
        """

        Changes the clock in/out entry for the specified employee based
        on the provided parameters.

        Args:
            params: (dict) the dictionary containing information about the employee,
                    date (or range) and clock in/out info.
                    If only one list element for 'date' is provided, the time is not needed.
                    Date accepts following formats and the combinations of them: '01/01/1981', '1/1/1981'.
                    The 'time' dictionary works with clock in, clock out, or both entries.
                    The time should follow the 'HH:MM AM' format

        Returns:
            True: if the operation is a success
            False: if there are errors in the proccess

        Example:
            params = {
                # If time is not provided, default values are used instead.
                # One day instead of two is also accepted.
                "date" : [["06/09/2019", "00:00 AM"], ["06/26/2019", "23:59 PM"]],
                "employee" : "91-Area Manager",
                # Either clock in/out or just clock in time
                "entry" : {
                    "clock in" : ["06/19/2019", "11:45 AM"],
                    "clock out" : ["06/19/2019", "12:02 PM"]
                },
                "time" : {
                    "clock in" : ["06/19/2019", "11:00 AM"],
                    "clock out" : ["06/19/2020", "01:25 PM"]
                }
            }
            >>> change(params)
                True
        """
        if not self._select(params):
            return False

        time_entry = params['entry']
        
        clock_in = "%s    %s"%( tuple(time_entry['clock in']) ) if 'clock in' in time_entry.keys() else None
        clock_out = "%s    %s"%( tuple(time_entry['clock out']) ) if 'clock out' in time_entry.keys() else None

        # Check if the entry exists
        inquiry = []
        if clock_in:
            inquiry.append(clock_in)
        if clock_out:
            inquiry.append(clock_out)

        if inquiry:
            if mws.select("Clock list", inquiry):
                # At this point it should be selected
                # Change it
                if not mws.click_toolbar("Change"):
                    self.log.error("Unable to click 'Change' for the given range")
                    system.takescreenshot()
                    return False
                if not self._modify_entry(params['time']):
                    return False

                # Navigate out
                if not mws.click_toolbar('Back'):
                    self.log.error(f"Unable to click 'Back' to return to the main menu.")
                    return False
            else:
                self.log.error("The provided time entry was not found")
                system.takescreenshot()
                return False
        else:
            self.log.error("Invalid time entry data is provided")
            return False
    
    def delete(self, params):
        """
        Deletes the clock in/out entry for the specified employee based
        on the provided parameters.

        Args:
            params: (dict) the dictionary containing information about the employee,
                    date (or range) and clock in/out info.
                    If only one list element for 'date' is provided, the time is not needed.
                    Date accepts following formats and the combinations of them: '01/01/1981', '1/1/1981'.
                    The 'time' dictionary works with clock in, clock out, or both entries.
                    The time should follow the 'HH:MM AM' format

        Returns:
            True: if the operation is a success
            False: if there are errors in the proccess

        Example:
            params = {
                # If time is not provided, default values are used instead.
                # One day instead of two is also accepted.
                "date" : [['06/26/2019', '00:00 AM'], ['06/26/2019', '23:59 PM']],
                "employee" : "91-Area Manager",
                # Either clock in/out or just clock in time
                "entry" : {
                    "clock in" : ["06/19/2019", "11:00 AM"],
                    "clock out" : ["06/19/2020", "01:25 PM"]
                }
            }
            >>>

        """
        if not self._select(params):
            return False
        
        time_entry = params['entry']
        
        clock_in = "%s    %s"%( tuple(time_entry['clock in']) ) if 'clock in' in time_entry.keys() else None
        clock_out = "%s    %s"%( tuple(time_entry['clock out']) ) if 'clock out' in time_entry.keys() else None

        # Check if the entry exists
        inquiry = []
        if clock_in:
            inquiry.append(clock_in)
        if clock_out:
            inquiry.append(clock_out)

        if inquiry:
            if mws.select("Clock list", inquiry):
                # At this point it should be selected
                # Delete it
                if not mws.click_toolbar("Delete"):
                    self.log.error("Unable to click 'Delete' for the given range")
                    system.takescreenshot()
                    return False
                
                # Accept the pop up
                if not self._click_on_popup_msg("Are you sure you want to delete this Clock In/Out Entry?", "YES"):
                    return False

                # Navigate out
                if not mws.click_toolbar('Back'):
                    self.log.error(f"Unable to click 'Back' to return to the main menu.")
                    return False

                return True
            else:
                self.log.error("The provided time entry was not found")
                system.takescreenshot()
                return False
        else:
            self.log.error("Invalid time entry data is provided")
            return False
    
    def _modify_entry(self, params):
        """
        Modifies the clock in/out entry based on the params provided.

        Args:
            params: (dictionary) the dictionary with the information about
                    date and time.
                    The 'time' dictionary works with clock in, clock out, or both entries.

        Returns:
            True: If entry was changed successfully.
            False: If something went wrong while modifying the entry (will be logged).

        Example:
            params = {
                "clock in" : ["06/19/2019", "11:45 AM"],
                "clock out" : ["08/25/2020", "12:02 PM"]
            }
        """
        calendar_bbox = (331, 260, 630, 476) if mws.is_high_resolution() else (331, 271, 626, 434)
        mws.connect("Clock In/Out Adjustment")
        if len(params.keys()) == 0:
            self.log.error("Invalid configuration provided for new clock in/out times. Time dictionary was empty")
            return False

        if not "clock in" in params.keys() and not "clock out" in params.keys():
            # Nothing to change
            self.log.error("Clock in/out times were not provided. No changes were made.")
            return False

        if 'clock in' in params.keys():
            # ["06/19/2019", "11:45 AM"]
            date_start = params['clock in']
            # Set beginning time
            if len(date_start) == 2:
                # Set time
                # HH:MM AM
                time, period = date_start[1].split(" ")
                
                # Check time and transform it
                if not re.match(r'\d\d:\d\d', time):
                    self.log.error(f"Invalid time provided '{time}'. It should follow HH:MM format.")
                    return False
                
                # time = time.replace(':', '')

                # Workaround for defective time field
                # Erase the time in the field and send the target time as chars
                # ctrl = mws.get_control("Clock in time")
                # ctrl.send_keystrokes('{VK_END}{BS 10}') # 10 backspaces just to be safe
                # for c in time:
                #     ctrl.send_keystrokes(c)
                # ctrl.send_keystrokes('{ENTER}')
                if not mws.set_value("Clock in time", time):
                    self.log.error(f"Unable to set the Clock In time to '{time}'")
                    return False
                
                # Set AM/PM
                if period != "AM" and period != "PM":
                    self.log.error(f"Invalid time period '{period}' is provided")
                    return False

                # Get current period and decide if change is needed
                period_set = mws.find_text_ocr(period, bbox=(228, 237, 262, 285))
                if not period_set and not mws.click("Clock in am/pm"):
                    self.log.error(f"Unable to set the time starting time period to '{period}'")
                    return False
            # Pick date
            if not self._pick_calendar_date(date_start[0], "Clock in calendar", bbox=calendar_bbox):
                return False

        if 'clock out' in params.keys():
            # ["08/25/2020", "12:02 PM"]
            date_end = params['clock out']
            # Set ending time
            if len(date_end) == 2:
                # Set time
                # HH:MM AM
                time, period = date_end[1].split(" ")
                
                # Check time and transform it
                if not re.match(r'\d\d:\d\d', time):
                    self.log.error(f"Invalid time provided '{time}'. It should follow HH:MM format.")
                    return False
                
                # time = time.replace(':', '')

                # # Workaround for defective time field
                # # Erase the time in the field and send the target time as chars 
                # ctrl = mws.get_control("Clock out time")
                # ctrl.send_keystrokes('{VK_END}{BS 10}') # 10 backspaces just to be safe
                # for c in time:
                #     ctrl.send_keystrokes(c)
                # ctrl.send_keystrokes('{ENTER}')
                if not mws.set_value("Clock out time", time):
                    self.log.error(f"Unable to set the Clock In time to '{time}'")
                    return False
                
                # Set AM/PM
                if period != "AM" and period != "PM":
                    self.log.error(f"Invalid time period '{period}' is provided")
                    return False

                # Get current period and decid if change is needed
                period_set = mws.find_text_ocr(period, bbox=(229, 428, 261, 442))
                if not period_set and not mws.click("Clock out am/pm"):
                    self.log.error(f"Unable to set the time starting time period to '{period}'")
                    return False
            # Pick date
            if not self._pick_calendar_date(date_end[0], "Clock out calendar", bbox=calendar_bbox):
                return False
        
        if not mws.click_toolbar("Save"):
            self.log.error("Cannot save the entry")
            return False
        
        # Check the top bar for message
        top_bar_message = mws.get_top_bar_text()
        if top_bar_message:
            self.log.error(f"The top bar message is \'{top_bar_message}\'")
            # NOTE Is the screenshot of the message even neccessary?
            system.takescreenshot()
            mws.click_toolbar("OK")
            mws.click_toolbar("CANCEL")
            mws.click_toolbar("NO")
            system.takescreenshot()
            return False

        return True
    
    def _select(self, params):
        """
        Private method that populates the date ranges and selects the employee
        for clock in/out adjustment.

        Args:
            params: (dict) the dictionary containing information about the employee,
                    date (or range)

        Returns:
            True: if the operation is a success
            False: if there are errors in the proccess

        Example:
            params = {
                # If time is not provided, default values are used instead.
                # One day instead of two is also accepted.
                "date" : [["06/26/2019", "00:00 AM"], ["06/26/2019", "23:59 PM"]],
                "employee" : "91-Area Manager"
            }
        """
        if not mws.select_radio("Select"):
            self.log.error("Unable to select the 'Select' radiobox to enable the range.")
            return False

        # [["06/26/2019", "00:00 AM"], ["06/26/2019", "23:59 PM"]]
        date = params['date']
        if len(date) == 2:
            # ["06/26/2019", "00:00 AM"]
            date_start = date[0]
            date_end = date[1]
            
            # Set beginning time
            if len(date_start) == 2:
                # Set time
                # HH:MM AM
                time, period = date_start[1].split(" ")
                
                # Check time and transform it
                if not re.match(r'\d\d:\d\d', time):
                    self.log.error(f"Invalid time provided '{time}'. It should follow HH:MM format.")
                    return False
                
                time = time.replace(':', '')

                # Workaround for defective time field
                # Erase the time in the field and send the target time as chars 
                ctrl = mws.get_control("Select begin time")
                ctrl.send_keystrokes('{VK_END}{BS 10}') # 10 backspaces just to be safe
                for c in time:
                    ctrl.send_keystrokes(c)
                ctrl.send_keystrokes('{ENTER}')
                
                # Set AM/PM
                if period != "AM" and period != "PM":
                    self.log.error(f"Invalid time period '{period}' is provided")
                    return False

                # Get current period and decide if change is needed
                period_set = mws.find_text_ocr(period, bbox=(231, 283, 267, 296))
                if not period_set and not mws.click("Select begin am/pm"):
                    self.log.error(f"Unable to set the time starting time period to '{period}'")
                    return False
                
                # Pick date
                if not self._pick_calendar_date(date_start[0], "Select begin calendar"):
                    return False
            
            # Set ending time
            if len(date_end) == 2:
                # Set time
                # HH:MM AM
                time, period = date_end[1].split(" ")

                # Check time and transform it
                if not re.match(r'\d\d:\d\d', time):
                    self.log.error(f"Invalid time provided '{time}'. It should follow HH:MM format.")
                    return False
                
                time = time.replace(':', '')

                # Workaround for defective time field
                # Erase the time in the field and send the target time as chars 
                ctrl = mws.get_control("Select end time")
                ctrl.send_keystrokes('{VK_END}{BS 10}')
                for c in time:
                    ctrl.send_keystrokes(c)
                ctrl.send_keystrokes('{ENTER}')
                
                # Set AM/PM
                if period != "AM" and period != "PM":
                    self.log.error(f"Invalid time period '{period}' is provided")
                    return False

                # Get current period and decide if change is needed
                period_set = mws.find_text_ocr(period, bbox=(229, 346, 261, 360))
                if not period_set and not mws.click("Select end am/pm"):
                    self.log.error(f"Unable to set the time starting time period to '{period}'")
                    return False
                
                # Pick date
                if not self._pick_calendar_date(date_end[0], "Select end calendar"):
                    return False

            if not mws.set_value("Select"):
                self.log.error(f"Unable to select the range")
                return False
            
        elif len(date) == 1:
            # ["06/26/2019", "00:00 AM"]
            date_start = date[0]
            # Pick date
            if not self._pick_calendar_date(date_start[0], "Select begin calendar"):
                return False
            
            # Pick date
            if not self._pick_calendar_date(date_start[0], "Select end calendar"):
                return False

            # No time setting is needed
        else:
            self.log.error("Invalid date entry in the configuration is provided.")
            return False

        # Select emloyee
        if not mws.set_value("Employee", params['employee']):
            self.log.error(f"Unable to set the Employee to '{params['employee']}'")
            return False
        
        if not mws.click_toolbar("Select"):
            self.log.error("Unable to click 'Select' for the given range")
            system.takescreenshot()
            return False
        
        return True

    def _pick_calendar_date(self, date, btn, color='0000A0', bbox=(314, 207, 611, 420) if mws.is_high_resolution else (314, 188, 611, 387)):
        """
        Selects the date in the calendar popup based on the provided parameters.

        Args:
            date: (str) the date string. It accepts following formats and the combinations of them: '01/01/1981', '1/1/1981'
            btn: (str) the calendar button control name
            color: (str) the color of the text of the date in the calendar. Defaults to blueish
            bbox: (tuple) the tuple of coordinates bounding the calendar box (lef top right bottom)

        Returns:
            True: if the operation is a success
            False: if there were errors in the proccess

        Example:
            >>> date = "06/24/2019"
            >>> pick_calendar_date(date, 'Select begin calendar')
                True
            >>> date = "7/24/2019"
            >>> pick_calendar_date(date, 'Select end calendar')
                True
        """
        # TODO: Looks like the calendars all appear in the same place now. Pull out this logic
        CAL_FIELD_MAP = {
            "Select begin calendar" : {
                "date" : "Select begin date",
                "calendar" : (109, 274, 156, 298)
            },
            "Select end calendar" : {
                "date" : "Select end date",
                "calendar" : (107, 336, 160, 365)
            },
            "Clock in calendar" : {
                "date" : "Clock in date",
                "calendar" : (109, 228, 156, 252)
            },
            "Clock out calendar" : {
                "date" : "Clock out date",
                "calendar" : (107, 426, 160, 449)
            }
        }

        # Check if the date is supplied in correct format
        # mm/dd/yyyy
        if not re.match(r'^\d{1,2}\/\d{1,2}\/\d{4}$', date):
            self.log.error(f"The provided date '{date}' is invalid. It should follow mm/dd/yyyy format")
            return False

        if not  mws.search_click_ocr("Calendar", bbox=CAL_FIELD_MAP[btn]['calendar']):
            self.log.error(f"Unable to open the calendar")
            return False
        
        # Get calendar control
        calendar_ctrl = mws.get_control("Calendar days")
        
        # Apply changes of the currently selected date
        calendar_ctrl.click()

        if not  mws.search_click_ocr("Calendar", bbox=CAL_FIELD_MAP[btn]['calendar']):
            self.log.error(f"Unable to open the calendar")
            return False
        
        # Introduce the signum function
        sign = lambda x: (-1, 1)[ x > 0]

        current_date = mws.get_value(CAL_FIELD_MAP[btn]['date'])

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

    def _click_on_popup_msg(self, text, btn):
        """
        Private function that clicks the button with the provided text 
        if the popup message text is equal to expected text.
        The function logs errors and takes screenshots.

        Args:
            text: (string) the expected text of the popup message
            btn: (string) the text on the button. Make sure that the text is what OCR will actually see

        Returns:
            Returns True if the operation is a success.
            Otherwise, if the text of the message does not match or button is not clicked,
            returns False
            
        Example:
            >>> _click_on_popup_msg(MSG, "x") 
                True
            >> _click_on_popup_msg(MSG, "blablablabalba)
                Some part of your configuration is not valid
                False
        """
        if not mws.get_top_bar_text() == text:
            self.log.error(f"The screen text should be \"{text}\", but it was \"{mws.get_top_bar_text()}\"")
            self.log.warning("Some part of your configuration is not valid")
            return False
        else:
            if not mws.click_toolbar(btn):
                self.log.error(f"Unable to click \'{btn}\' on the pop up message")
                return False
        return True
