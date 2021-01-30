"""
    File name: Meta_Clock_Adjustment.py
    Tags:
    Description: The meta test to verify the functionality of the clock_adjustment.py module
    Author: Alex Rudkov
    Date created: 2019-06-26 17:21:58
    Date last modified: 2020-01-16 14:10:10
    Modified By: Conor McWain
    Python Version: 3.7
"""

import logging, time, random
from app import Navi, mws, pos, system
from app.framework.tc_helpers import setup, test, teardown, tc_fail

from app.features import clock_adjustment

class Meta_Clock_Adjustment():
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
        self.log = logging.getLogger()

    @setup
    def setup(self):
        """Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        # if not system.restore_snapshot():
        #     raise Exception

    @test
    def test_case_1(self):
        """Pick the date in calendar.
        Args: None
        Returns: None
        """
        # Generate random date in the range
        date = self.random_date()

        ca = clock_adjustment.ClockInOutAdjustment()

        mws.select_radio('Select')

        if not ca._pick_calendar_date(date, 'Select begin calendar'):
            tc_fail(f"Failed to select the beginning date: '{date}'")
        
        # Check
        current_date = mws.get_value("Select begin date")
        if current_date != date:
            tc_fail("Incorrect beginning date was set")

        date = self.random_date()
        if not ca._pick_calendar_date(date, 'Select end calendar'):
            tc_fail(f"Failed to select the correct date '{date}'")

        # Check
        current_date = mws.get_value("Select end date")
        if current_date != date:
            tc_fail("Incorrect ending date was set")

        mws.recover()

    @test
    def test_case_2(self):
        """Adds the clock in/out entries for the 91
        Args: None
        Returns: None
        """
        ca = clock_adjustment.ClockInOutAdjustment()

        params = {
            # If time is not provided, default values are used instead.
            # One day instead of two is also accepted.
            "date" : [["06/6/2019", "02:25 AM"], ["06/26/2019", "11:59 PM"]],
            "employee" : "91-Area Manager",
            "time" : {
                "clock in" : ["06/19/2019", "11:45 AM"],
                "clock out" : ["06/19/2019", "01:02 PM"]
            }
        }

        self.log.info("Starting the test trying to add new time entry")
        if not ca.add(params):
            tc_fail("Failed to add the clock in/out entry for the Area Manager")
        self.log.info("Added new time entry")
        
        # Check
        self.log.info("Checking if the new time entry is valid")
        ca._select(params)
        if not mws.select("Clock list", "%s    %s"%( params['time']['clock in'][0], params['time']['clock in'][1] ) ):
            tc_fail("The entry was added but was not found in the list")
        self.log.info("Checking passed successfully")

        mws.recover()
    
    @test
    def test_case_3(self):
        """Changes the clock in/out entries for the 91
        Args: None
        Returns: None
        """
        ca = clock_adjustment.ClockInOutAdjustment()

        params = {
            # If time is not provided, default values are used instead.
            # One day instead of two is also accepted.
            "date" : [["06/11/2019", "00:00 AM"], ["06/26/2019", "23:59 PM"]],
            "employee" : "91-Area Manager",
            # Either clock in/out or just clock in time
            "entry" : {
                "clock in" : ["06/19/2019", "11:45 AM"],
                "clock out" : ["06/19/2019", "01:02 PM"]
            },
            "time" : {
                "clock in" : ["06/19/2019", "11:00 AM"],
                "clock out" : ["06/19/2019", "01:25 PM"]
            }
        }

        self.log.info("Starting the test trying to change existing time entry")
        if not ca.change(params):
            tc_fail("Failed to change the clock in/out entry for the Area Manager")
        self.log.info("Changed the time entry")
        
        # Check
        self.log.info("Checking if the new time entry is valid")
        ca._select(params)
        if not mws.select("Clock list", "%s    %s"%( params['time']['clock in'][0], params['time']['clock in'][1] ) ):
            tc_fail("The entry was changed but the changed entry was not found in the list")
        self.log.info("Checking passed successfully")

        mws.recover()

    @test
    def test_case_4(self):
        """Deletes the clock in/out entries for the 91
        Args: None
        Returns: None
        """
        ca = clock_adjustment.ClockInOutAdjustment()

        params = {
            # If time is not provided, default values are used instead.
            # One day instead of two is also accepted.
            "date" : [['06/11/2019', '00:00 AM'], ['06/26/2019', '23:59 PM']],
            "employee" : "91-Area Manager",
            # Either clock in/out or just clock in time
            "entry" : {
                "clock in" : ["06/19/2019", "11:00 AM"],
                "clock out" : ["06/19/2019", "01:25 PM"]
            }
        }

        self.log.info("Starting the test trying to delete existing time entry")
        if not ca.delete(params):
            tc_fail("Failed to change the clock in/out entry for the Area Manager")
        self.log.info("Deleted the time entry")
        
        # Check
        self.log.info("Checking if the time entry is deleted")
        ca._select(params)
        if mws.select("Clock list", "%s    %s"%( params['entry']['clock in'][0], params['entry']['clock in'][1] ) ):
            tc_fail("The entry was deleted but the entry was found in the list")
        self.log.info("Checking passed successfully")

        mws.recover()

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        mws.recover()
        pass
    
    def random_date(self):
        """
        Generates random date in the range '01/01/1981' -- '01/01/2100'
        """
        stime = time.mktime(time.strptime('01/01/1981', '%m/%d/%Y'))
        etime = time.mktime(time.strptime('01/01/2100', '%m/%d/%Y'))

        ptime = stime + random.random() * (etime - stime)

        return time.strftime('%m/%d/%Y', time.localtime(ptime))