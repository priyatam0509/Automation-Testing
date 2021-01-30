"""
    File name: TaxMng_IS360_Toggle.py
    Tags: TaxMaintenance_IS360
    StoryID: STARFINCH-3707
    Description: Tax Maintenance feature toggle from registery key value
    and validate the test cases
    Author: Pavan Kumar Kantheti
    Date created: 2020-05-17 12:10:08
    Date last modified:
    Python Version: 3.7
"""
from app.features import tax_maint
from app import mws
from Scripts.features import FromInsite360
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from datetime import datetime
import logging
import sys


class TaxMng_IS360_Toggle():
    """
    Description: Test class that provides an interface for testing.
    """
    index = -1
    update_count = 0
    key_name = "TaxConfigI360"

    def __init__(self):
        """
        Initialize reg values
        """
        # The logging object.
        # Example: self.log.info(f"Current value of var: {my_var}")
        self.log = logging.getLogger()

    @setup
    def setup(self):
        """
        Setup
        """
        pass

    @test
    def check_regKey_exist_TC1(self):
        """
        Zephyr Id : Check either the registry key string exists or not
        Args: None
        Returns: None
        """
        self.log.info(f"Insite360 registration check")
        insite360_enabled = FromInsite360.Check_I360_Connected()
        if not(insite360_enabled):
            FromInsite360.insite360_configure()
            FromInsite360.Register_UnRegister_Insite360(insite360_enabled)
        self.index = FromInsite360.TaxMainRegisterCheck()
        self.log.info(f"Registry key index value [{self.index}]")
        if (self.index < 0):
            tc_fail("Failed, Registery key is not exists in MWS system")

    @test
    def check_regKey_value_TC2(self):
        """
        Zephyr Id : Check the key value from the registry key
        Args: None
        Returns: None
        """
        value = FromInsite360.GetRegisterValue(self.index)
        self.log.info(f"Registry key value [{value}]")
        if not(value == "0"):
            tc_fail("Failed, default Registery key value is not zero")

    @test
    def add_edit_taxRate_3(self):
        """
        Zephyr Id : Add a new tax Rate or update the exist tax Rate Name and
                    check either the taxRate details send to insite360 or not.
        Args: None
        Returns: None
        """
        FromInsite360.SetRegisterValue(self.key_name, "0")
        status = self.add_edit_tax_rate(False)
        if not(status):
            tc_fail("Failed")

    @test
    def add_edit_taxRate_4(self):
        """
        Zephyr Id : Add a new tax Rate or update the exist tax Rate Name and
                    check either the taxRate details send to insite360 or not.
        Args: None
        Returns: None
        """
        FromInsite360.SetRegisterValue(self.key_name, "7rspk")
        status = self.add_edit_tax_rate(False)
        if not(status):
            tc_fail("Failed")

    @test
    def add_edit_taxRate_5(self):
        """
        Zephyr Id : Add a new tax Rate or update the exist tax Rate Name and
                    check either the taxRate details send to insite360 or not.
        Args: None
        Returns: None
        """
        FromInsite360.SetRegisterValue(self.key_name, "1")
        status = self.add_edit_tax_rate(True)
        if not(status):
            tc_fail("Failed")

    @test
    def add_edit_taxRate_6(self):
        """
        Zephyr Id : Add a new tax Rate or update the exist tax Rate Name and
                    check either the taxRate details send to insite360 or not.
        Args: None
        Returns: None
        """
        FromInsite360.DeleteRegisterKey(self.key_name)
        status = self.add_edit_tax_rate(False)
        if not(status):
            tc_fail("Failed")

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        # Setting back to "TaxConfigI360" register key value as zero ("0")
        FromInsite360.SetRegisterValue(self.key_name, "0")

    def add_edit_tax_rate(self, validate):
        """
        Add or update the tax rate details
        Args:   validate (bool)
        Returns:True/ False
        """
        return_status = True
        tax = tax_maint.TaxMaintenance()
        tax_name = "NC Sales Tax Reg"
        tab_name = "Rates"
        # check wether the tax rate is already exists or not
        # if yes, change the tax rate details
        mws.select_tab(tab_name)
        is_tax_exist = mws.set_value(tab_name, tax_name, tab_name)
        start_time_from_script = datetime.now()
        if (is_tax_exist):
            if (self.update_count == 0):
                cfg = {
                    "Receipt Description": "SalesTax",
                    "Minimum Amount": "12"
                }
            elif (self.update_count == 1):
                cfg = {
                    "Receipt Description": "NC Tax",
                    "Minimum Amount": "11"
                }
            elif (self.update_count == 2):
                cfg = {
                    "Receipt Description": "SalesTax",
                    "Minimum Amount": "20"
                }
            elif (self.update_count == 3):
                cfg = {
                    "Receipt Description": "SalesTax",
                    "Minimum Amount": "37"
                }
            self.log.info(f"is_tax_exist [{tax_name}] : [{is_tax_exist}]")
            self.log.info(f"[{self.update_count}] changing with cfg = [{cfg}]")
            self.update_count = self.update_count + 1
        else:
            cfg = {
                "Name": "NC Sales Tax Reg", "Receipt Description": "NC Tax",
                "Percent": "10", "Minimum Amount": "10"
            }
            self.log.info(f"Adding new tax with [{tax_name}]")

        try:
            add_status = tax.configure_rate(tax_name, cfg)
        except:
            self.log.error(f"An exception occured while add/update tax rate - [{sys.exc_info()[0]}]. [{sys.exc_info()[1]}], line: [{sys.exc_info()[2].tb_lineno}]")
            add_status = False

        if (not add_status):
            mws.click_toolbar("cancel")
            mws.click_toolbar("no")
            self.log.error("Failed, unable to add/modify the tax rate details")
            return_status = False
        else:
            mws.click_toolbar("save")
            # Restart the Service and check the JSON Data generated or NOT
            time_out_min = FromInsite360.RestartServiceAndValidate()
            tax_rate_time_out = FromInsite360.JSONGenerateTimeOutStatus("taxRates", start_time_from_script, time_out_min, 60, False, False, True)
            if (validate):
                if (tax_rate_time_out):
                    self.log.error("Failed, .json data is not sent to I360")
                    return_status = False
            else:
                if (not tax_rate_time_out):
                    self.log.error("Failed, .json data is sent to I360")
                    return_status = False
        return return_status
