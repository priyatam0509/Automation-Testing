"""
    File name: SWUpgrade_VerifyExpiryDate_OnFreshInstallation.py
    Tags:
    Description: SL-1765: Hardcode expiry date at win 10 activation
    Brand: Concord
    Author: Paresh
    Date created: 2020-05-04 19:11:00
    Date last modified:
    Python Version: 3.7
"""

import logging
import pyodbc
from datetime import datetime, timedelta
from app import Navi, mws
from app.features import feature_activation
from app.framework.tc_helpers import setup, test, teardown, tc_fail

log = logging.getLogger()

SUITES_WITHOUT_WINDOWS10 = ["Core Application Suite", "Mobile Loyalty Suite", "Express Lane Suite"]

DEFAULT_SUITES = ["Core Application Suite", "Mobile Loyalty Suite", "Windows 10 License", "Express Lane Suite"]

future_date = datetime.strftime(datetime.now() - timedelta(-365), '%m-%d-%Y')

def connect_mws_db(id='19004', conServer="POSSERVER01", dbName="GlobalSTORE"):
    """
    Description: Help function to connect with database
    Args:
        id: Primary key id of query
		conServer: Connection server name
        dbName: database Name
    Returns: True if query successfully executed, False if fail
    """
    result = ""
    connstr = 'Driver={SQL Server};Server=' + conServer + ';Database='+ dbName +';Trusted_Connection=yes;'
    try:
        # connection through the connection string
        conn = pyodbc.connect(connstr)
        cursor = conn.cursor()

        queryString = "SELECT OPT_VALUE FROM OPTIONS_STR WHERE OPT_ID='"+id+"'"
        # executes the query
        cursor.execute(queryString)
        rows = cursor.fetchall()

        for row in rows:
            result = row[0]
            break

        conn.close()

    except pyodbc.Error as ex:
        sqlstate = ex.args[1]
        log.error(sqlstate)
    
    return result


class SWUpgrade_VerifyExpiryDate_OnFreshInstallation():
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
        
    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        # Activate feature activation without selecting widows 10 and validate the message.
        FA = feature_activation.FeatureActivation()
        if not FA.activate(features=SUITES_WITHOUT_WINDOWS10, mode=feature_activation.SUITES):
            log.error("Feature activation failed")
        
    @test
    def verify_null_value_in_db(self):
        """
        Testlink Id: SL-1765: Hardcode expiry date at win 10 activation
		Description: Verify if windows 10 is not activated expiry date value should be null in DB
        Args: None
        Returns: None
        """

        # Fetch date value from DB
        date_value = connect_mws_db()

        # Verify date value is null in DB
        if date_value != "":
            tc_fail("Date value is not null")
            
        return True
    
    @test
    def activate_win10_in_featureActivation(self):
        """
        Testlink Id: SL-1765: Hardcode expiry date at win 10 activation
		Description: Activate windows 10 in feature activation
        Args: None
        Returns: None
        """

        # Activate windows 10 in feature activation
        FA = feature_activation.FeatureActivation()
        if not FA.activate(features=DEFAULT_SUITES, mode=feature_activation.SUITES):
            tc_fail("Unable to complete feature activation")
            
        return True
    
    @test
    def verify_date_value_updated_in_db(self):
        """
        Testlink Id: SL-1765: Hardcode expiry date at win 10 activation
		Description: Verify after windows 10 is activated expiry date value should be entered in DB
        Args: None
        Returns: None
        """

        # Fetch date value from DB
        date_value = connect_mws_db()

        # Verify date value is current date+365 days in DB
        if date_value != future_date:
            tc_fail("Date value is not updated in DB")
            
        return True
    
    @test
    def date_notChanged_on_2ndTime_featureActivation(self):
        """
        Testlink Id: SL-1765: Hardcode expiry date at win 10 activation
		Description: Verify if we are doing feature activation 2nd time expiry date should not be changed in DB
        Args: None
        Returns: None
        """

        #  Activate feature activation without windows 10 activation
        FA = feature_activation.FeatureActivation()
        if not FA.activate(features=SUITES_WITHOUT_WINDOWS10, mode=feature_activation.SUITES):
            tc_fail("Unable to complete feature activation")
        
        # Fetch date value from DB
        date_value = connect_mws_db()

        # Verify date value is current date+365 days  in DB
        if date_value != future_date:
            tc_fail("Date value is changed in DB")
        
        # Activate windows 10 in feature activation
        FA1 = feature_activation.FeatureActivation()
        if not FA1.activate(features=DEFAULT_SUITES, mode=feature_activation.SUITES):
            tc_fail("Unable to complete feature activation")

        # Fetch date value from DB
        date_value = connect_mws_db()

        # Verify date value is current date+365 days  in DB
        if date_value != future_date:
            tc_fail("Date value is changed in DB")
        
        return True
    
    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        pass