"""
    File name: TaxMng_IS360_RestartSvc.py
    Tags:
    StoryID: STARFINCH-3584
    Description: Tax Management from IS360, tax rate .json object
                 generate from RemoteManager service
    Author: Pavan Kumar Kantheti
    Date created: 2020-04-07 11:12:13
    Date last modified:
    Python Version: 3.7
"""
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from Scripts.features import FromInsite360
import logging
from datetime import datetime


class TaxMng_IS360_RestartSvc():
    """
        Description: Test class that provides an interface for testing.
    """

    def __init__(self):
        """
        Initializes the Template class.
        Args: None
        Returns: None
        """
        # The logging object.
        self.log = logging.getLogger()

    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        pass

    @test
    def restart_RemoteManager_Service(self):
        """
        Zephyr Id : Restart the "RemoteManagerSVC" service to check tax rate event .json is generated or not
        Args: None
        Returns: None
        """
        index = FromInsite360.TaxMainRegisterCheck()
        self.log.info(f"Registry key index value [{index}]")
        # Setting "TaxConfigI360" register key value as one ("1")
        FromInsite360.SetRegisterValue("TaxConfigI360", "1")
        self.log.info("Check wether the insite 360 is enabled or not at Restart Service")
        insite360_enabled = FromInsite360.Check_I360_Connected()
        self.log.info(f"Insite 360 is enabled [{insite360_enabled}]")

        proceed_test = FromInsite360.insite360_configure()

        if (proceed_test):
            proceed_test = FromInsite360.Register_UnRegister_Insite360(insite360_enabled)
            insite360_enabled_status = FromInsite360.Check_I360_Connected()
            self.log.info(f"After Register_UnRegister_Insite360, latest Insite 360 is enabled [{insite360_enabled_status}]")
            if (insite360_enabled_status == insite360_enabled):
                proceed_test = False
            else:
                proceed_test = True
                insite360_enabled = insite360_enabled_status

        if (proceed_test):
            # Restart the service
            start_time_script = datetime.now()
            service_status = FromInsite360.RestartService()
            if (service_status):
                tax_status = FromInsite360.JSONGenerateTimeOutStatus("taxRates", start_time_script, 2, 60, False, False, True)
                self.log.info(f"Tax rate event send status [{ not tax_status}] Time out[{tax_status}]")
                if (insite360_enabled):
                    if (tax_status):
                        tc_fail("Failed, .json file is not generated after restart service")
                else:
                    if not(tax_status):
                        tc_fail("Failed, .json file is generated after restart service")

            else:
                tc_fail("Failed, Unable to restart the Service")
        else:
            tc_fail("Failed, Unable to proceed due to register/un-register issue.")

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        # delete pass after you implement.
        pass

