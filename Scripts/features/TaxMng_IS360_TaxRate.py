"""
    File name: TaxMng_IS360_TaxRate.py
    Tags:
    StoryID: STARFINCH-3476
    Description: Tax rate configuration event json object sent to
                 Insite360file genaration validation
    Author: Pavan Kumar Kantheti
    Date created: 2020-04-07 13:14:15
    Date last modified:
    Python Version: 3.7
"""
from app.features import tax_maint
from app import mws
from Scripts.features import FromInsite360
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from datetime import datetime
import logging
import json
import time
import sys


class TaxMng_IS360_TaxRate():
    """
        Description: Test class that provides an interface for testing.
    """
    insite360_enabled = False
    tax_name = ""
    row_index = -1

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
    def add_new_taxRate_TC1(self):
        """
        Zephyr Id : Add a new tax rate to the list and check the
                    .json object is generated or not to send i360
        Args: None
        Returns: None
        """
        self.log.info("Check whether the insite 360 is enabled or not")
        self.insite360_enabled = FromInsite360.Check_I360_Connected()
        self.log.info(f"Insite 360 is enabled [{self.insite360_enabled}]")
        self.log.info("Start add_new_taxRate_TC1")
        tax = tax_maint.TaxMaintenance()
        tab_name = "Rates"
        # Default Adding Tax rate with 20 chars as NC Tax Rate YYYYmmdd
        self.tax_name = "NC Tax Rate " + datetime.now().strftime("%Y%m%d")
        # check wether the tax rate is already exists or not
        # if yes, change the tax rate details
        mws.select_tab(tab_name)
        tax_exist = mws.set_value(tab_name, self.tax_name, tab_name)
        start_time_from_script = datetime.now()
        if (tax_exist):
            cfg = {
                    "Normal": True,
                    "Minimum Amount": "12"
                }
            self.log.info(f"tax_exist [{self.tax_name }] : [{tax_exist}]")
        else:
            self.log.info(f"[{self.tax_name }] : [{tax_exist}]")
            current_value = mws.get_value("Rates", "Rates")
            tax_name_check = self.tax_name.replace("Tax Rate", "TaxRate", 1)
            self.log.info(f"tax_name_check [{tax_name_check}]")
            if (self.get_row_index(current_value, tax_name_check) > 0):
                self.tax_name = tax_name_check
                cfg = {
                        "Normal": True,
                        "Receipt Description": "SalesTax",
                        "Minimum Amount": "12"
                    }
                self.log.info(f"latest tax name [{self.tax_name }] : [{tax_exist}]")
            else:
                config = '{"Name": "' + self.tax_name + '", "Receipt Description": "NC Tax", "Percent": "10.000", "Minimum Amount": "10"}'
                cfg = json.loads(config)
                self.log.info(f"Adding new tax with [{self.tax_name}]")
        try:
            add_status = tax.configure_rate(self.tax_name, cfg)
        except:
            self.log.error(f"An exception occured while add/update a tax rate - [{sys.exc_info()[0]}]. [{sys.exc_info()[1]}], line: [{sys.exc_info()[2].tb_lineno}]")
            add_status = False

        if (not add_status):
            mws.click_toolbar("cancel")
            mws.click_toolbar("no")
            tc_fail("Failed, unable to add/modify the tax rate details")
        else:
            mws.click_toolbar("save")
            self.log.info(f"Insite360 Enabled = [{self.insite360_enabled}]")
            # Restart the Service and check the JSON Data generated or NOT
            time_out_min = FromInsite360.RestartServiceAndValidate()
            taxRateTimeOut = FromInsite360.JSONGenerateTimeOutStatus("taxRates", start_time_from_script, time_out_min, 60, False, False, True)
            if (self.insite360_enabled):
                if (taxRateTimeOut):
                    tc_fail("Failed, .json data is not sent to I360")
            else:
                if (not taxRateTimeOut):
                    tc_fail("Failed, .json data is sent to I360")

    @test
    def change_taxRate_Name_TC2(self):
        """
        Zephyr Id : Change tax rates for existing tax rate name toggle with 18 or 17 chars and check the
                    .json object is generated or not to send i360
        Args: None
        Returns: None
        """
        return_status = self.change_tax_rate_by("Name", "Rates")
        if not(return_status):
            tc_fail("Failed at modify the tax - Name")

    @test
    def change_taxRate_Name_TC3(self):
        """
        Zephyr Id : Change tax rates for existing tax rate name toggle with 18 or 17 chars and check the
                    .json object is generated or not to send i360
        Args: None
        Returns: None
        """
        return_status = self.change_tax_rate_by("Name", "Rates")
        if not(return_status):
            tc_fail("Failed at modify the tax - Name")

    @test
    def change_taxRate_Receipt_TC4(self):
        """
        Zephyr Id : Change tax rate details for existing tax rate Receipt description toggle with 8 or 7 or empty chars and check the
                    .json object is generated or not to send i360
        Args: None
        Returns: None
        """
        return_status = self.change_tax_rate_by("Receipt Description", "Rates")
        if not(return_status):
            tc_fail("Failed at modify the tax - Receipt Description")

    @test
    def change_taxRate_Receipt_TC5(self):
        """
        Zephyr Id : Change tax rate details for existing tax rate Receipt description toggle with 8 or 7 or empty chars and check the
                    .json object is generated or not to send i360
        Args: None
        Returns: None
        """
        return_status = self.change_tax_rate_by("Receipt Description", "Rates")
        if not(return_status):
            tc_fail("Failed at modify the tax - Receipt Description")

    @test
    def change_taxRate_MinimumAmount_TC6(self):
        """
        Zephyr Id : Change tax rate details for existing tax rate Minimum Amount value and check the
                    .json object is generated or not to send i360
        Args: None
        Returns: None
        """
        return_status = self.change_tax_rate_by("Minimum Amount", "Rates")
        if not(return_status):
            tc_fail("Failed at modify the tax - Minimum Amount")

    @test
    def change_taxRate_Percentage_TC7(self):
        """
        Zephyr Id : Change tax rate details for existing tax rate percentage value and check the
                    .json object is generated or not to send i360
        Args: None
        Returns: None
        """
        return_status = self.change_tax_rate_by("Percent", "Rates")
        if not(return_status):
            tc_fail("Failed at modify the tax - Percent")

    @test
    def change_taxRate_CheckNoTax_TC8(self):
        """
        Zephyr Id : Check either the "No Tax" details generated in json object or not
        Args: None
        Returns: None
        """
        time_out_min = FromInsite360.RestartServiceAndValidate()
        start_time_from_script = datetime.now()
        tax_time_out_status = FromInsite360.JSONGenerateTimeOutStatus("taxRates", start_time_from_script, time_out_min, 60, False, False, True, True)
        if (self.insite360_enabled):
            if (tax_time_out_status):
                tc_fail("Failed, .json object having 'No Tax' rate details.")
        else:
            if (not tax_time_out_status):
                tc_fail("Failed, .json data is sent to I360")

    @test
    def change_taxRate_Table_TC9(self):
        """
        Zephyr Id : Change tax rate details for existing tax rate table value and check the
                    .json object is generated or not to send i360
        Args: None
        Returns: None
        """
        return_status = self.change_tax_rate_by("Table", "Rates")
        if not(return_status):
            tc_fail("Failed at modify the tax - Table")

    @test
    def change_taxRate_Table_TC10(self):
        """
        Zephyr Id : Change tax rate details for existing tax rate table value and check the
                    .json object is generated or not to send i360
        Args: None
        Returns: None
        """
        return_status = self.change_tax_rate_by("Table", "Rates")
        if not(return_status):
            tc_fail("Failed at modify the tax - Table")

    @test
    def change_taxRate_RateType_TC11(self):
        """
        Zephyr Id : Change tax rate details for existing tax rate "rate type" value and check the
                    .json object is generated or not to send i360
        Args: None
        Returns: None
        """
        return_status = self.change_tax_rate_by("Tax Rate", "Rates")
        if not(return_status):
            tc_fail("Failed at modify the tax - Rate")

    @test
    def change_taxRate_RateType_TC12(self):
        """
        Zephyr Id : Change tax rate details for existing tax rate "rate type" value and check the
                    .json object is generated or not to send i360
        Args: None
        Returns: None
        """
        return_status = self.change_tax_rate_by("Tax Rate", "Rates")
        if not(return_status):
            tc_fail("Failed at modify the tax - Rate")

    @test
    def change_taxRate_ActiveInActive_TC13(self):
        """
        Zephyr Id : Change tax rate details for existing tax rate toggle Active / In-Active state value and check the
                    .json object is generated or not to send i360
        Args: None
        Returns: None
        """
        return_status = self.change_tax_rate_by("Activate", "Rates")
        if not(return_status):
            tc_fail("Failed at modify the tax - Activate")

    @test
    def change_taxRate_ActiveInActive_TC14(self):
        """
        Zephyr Id : Change tax rate details for existing tax rate toggle Active / In-Active state value and check the
                    .json object is generated or not to send i360
        Args: None
        Returns: None
        """
        return_status = self.change_tax_rate_by("Activate", "Rates")
        if not(return_status):
            tc_fail("Failed at modify the tax - Activate")

    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        index = FromInsite360.TaxMainRegisterCheck()
        self.log.info(f"Registry key index value [{index}]")
        # Setting back to "TaxConfigI360" register key value as zero ("0")
        FromInsite360.SetRegisterValue("TaxConfigI360", "0")

    def restart_tax(self):
        """
        Restart the Passport and open the tax maintenance screen
        Args: None
        Returns: tax(tax Maintenace object)
        """
        max_attempt = 1
        if_error = True
        while (max_attempt <= 3 and if_error):
            self.log.info(f"Attempt - [{max_attempt}]")
            system.restartpp()
            time.sleep(5)
            mws.sign_on()
            start = datetime.now()
            tax = tax_maint.TaxMaintenance()
            current = datetime.now()
            if (timedelta.seconds < 45):
                if_error = False
            else:
                self.log.info(f"Time Gap to load tax maintenance in seconds : [{timedelta.seconds}]")
            max_attempt = max_attempt + 1
        if (max_attempt > 3):
            tax = tax_maint.TaxMaintenance()
        return tax

    def start_tax(self):
        """
        Open the Tax Maintenance screen and check the time in seconds to open the tax maintenance screen
        Args: None
        Returns: tax(tax Maintenace object)
        """
        time.sleep(5)
        on_error = False
        try:
            start = datetime.now()
            tax = tax_maint.TaxMaintenance()
            current = datetime.now()
            timedelta = current - start
            if (timedelta.seconds >= 45):
                on_error = True
        except:
            self.log.error(f"Error at [start_tax]-[{sys.exc_info()[0]}]. [{sys.exc_info()[1]}], line: [{sys.exc_info()[2].tb_lineno}]")
            on_error = True

        if (on_error):
            tax = self.restart_tax()
        return tax

    def get_row_index(self, list_str, search_for):
        """
        Get the row index based on the tax rate name from the list
        Args:   list_str (string)
                search_for (string)
        Returns:row_id (int)
        """
        items_count = len(list_str)
        row_id = 0
        tax_found = False
        while not(tax_found):
            if (row_id < items_count - 1):
                row_id = row_id + 1
                if (list_str[row_id][0] == search_for):
                    tax_found = True
            else:
                row_id = 0
                tax_found = True
        return (row_id)

    def change_tax_rate_by(self, field_name, tab_name):
        """
        Change the tax rate data from UI based on the field_name and value
        Args: field_name (string) - Tax rate Name, Receipt Description, Percent, Minimum Amount, RateType, Active/Deactive etc
              tab_name (string) - tab_name at the screen
        Returns: True/ False
        """
        wait_for_time_out = False
        return_status = True
        try:
            self.log.info(f"Insite 360 is enabled [{self.insite360_enabled}]")
            self.log.info(f"Start change_tax_rate_by [{field_name}]")
            self.log.info(f"Tax Name : [{self.tax_name}]")

            tax = self.start_tax()

            # check wether the tax rate name is already exists or not
            # if yes, change the tax rate details, other wise add first time
            mws.select_tab(tab_name)
            tax_exist = mws.set_value(tab_name, self.tax_name, tab_name)
            self.log.info(f"tax_exist : [{tax_exist}]")
            start_time_from_script = datetime.now()

            if (tax_exist):
                current_value = mws.get_value(tab_name, tab_name)
                # self.log.info(f"current_value : [{current_value}]")
                if (self.row_index == -1):
                    self.row_index = self.get_row_index(current_value, self.tax_name)

                self.log.info(f"row_index : [{self.row_index}]")

                if (field_name == "Name"):
                    if (self.tax_name.find("Tax Rate") > 0):
                        tax_name_check = self.tax_name.replace("Tax Rate", "TaxRate", 1)
                        self.log.info(f"tax_name_check > 0  : [{tax_name_check}]")
                    else:
                        tax_name_check = self.tax_name.replace("TaxRate", "Tax Rate", 1)
                        self.log.info(f"tax_name_check <> 0  : [{tax_name_check}]")
                    config = '{"Name": "' + tax_name_check + '"}'
                    cfg = (json.loads(config))
                    self.log.info(f"self.tax_name : [{self.tax_name}] :: tax_name_check : [{tax_name_check}]")
                elif (field_name == "Receipt Description"):
                    field_value = current_value[self.row_index][1].strip()
                    self.log.info(f"field_name[{field_name}] :: field_value : [{field_value}]")
                    if (field_value.lower().find("nc tax") >= 0):
                        cfg = {"Receipt Description": "SalesTax"}
                    else:
                        cfg = {"Receipt Description": "NC Tax"}

                elif (field_name == "Percent"):
                    field_value = current_value[self.row_index][2].strip()
                    self.log.info(f"field_name[{field_name}] :: field_value : [{field_value}]")
                    if (field_value == "10.000"):
                        cfg = {"Percent": "1.000"}
                    else:
                        cfg = {"Percent": "10.000"}

                elif (field_name == "Tax Rate"):
                    field_value = current_value[self.row_index][4].strip()
                    self.log.info(f"field_name[{field_name}] :: field_value : [{field_value}]")
                    if (field_value == "Normal"):
                        cfg = {"GST": True}
                    elif (field_value == "GST"):
                        cfg = {"PST": True}
                    else:
                        cfg = {"Normal": True}
                    wait_for_time_out = True

                elif (field_name == "Minimum Amount"):
                    field_value = current_value[self.row_index][5].strip()
                    self.log.info(f"field_name[{field_name}] :: field_value : [{field_value}]")
                    if (field_value == "$1.00"):
                        cfg = {"Minimum Amount": "10"}
                    else:
                        cfg = {"Minimum Amount": "1"}

                elif (field_name == "Table"):
                    field_value = current_value[self.row_index][3].strip()
                    self.log.info(f"field_name[{field_name}] :: field_value : [{field_value}]")
                    if (field_value == ""):
                        cfg = {"Table": [".04", ".08", ".12", ".16", ".20", ".24", ".28"]}
                    else:
                        cfg = {"Table": "Remove", "Percent": "1.000"}

                elif (field_name == "Activate"):
                    activate = FromInsite360.CheckTaxRateActiveState(self.tax_name)
                    self.log.info(f"Tax rate Active state [{activate}] before change")
                    if (activate):
                        cfg = {"Activate": False}
                    else:
                        cfg = {"Activate": True}
                    wait_for_time_out = True

                self.log.info(f"Before congigure tax rate :: cfg : [{cfg}]")

                try:
                    time.sleep(3)
                    add_status = tax.configure_rate(self.tax_name, cfg)
                    time.sleep(2)
                except:
                    self.log.error(f"While updating tax issue at local.[{sys.exc_info()[0]}]. [{sys.exc_info()[1]}], line: [{sys.exc_info()[2].tb_lineno}]")

                mws.click_toolbar("save")
                if (add_status):
                    if (field_name == "Name"):
                        self.tax_name = tax_name_check

                    self.log.info(f"Insite360 Enabled = [{self.insite360_enabled}]")

                    # Restart the Service and check the JSON Data generated or NOT
                    if (self.insite360_enabled):
                        if not(wait_for_time_out):
                            time_out_min = FromInsite360.RestartServiceAndValidate()
                        else:
                            time_out_min = 16
                    else:
                        time_out_min = FromInsite360.RestartServiceAndValidate()

                    tax_time_out_status = FromInsite360.JSONGenerateTimeOutStatus("taxRates", start_time_from_script, time_out_min, 60, False, False, True)
                    if (self.insite360_enabled):
                        if (field_name == "Tax Rate" or field_name == "Activate"):
                            if not(tax_time_out_status):
                                return_status = False
                        else:
                            if (tax_time_out_status):
                                return_status = False
                    else:
                        if (not tax_time_out_status):
                            return_status = False
                else:
                    return_status = False
        except:
            self.log.error(f"An exception occured update a tax rate.[{sys.exc_info()[0]}]. [{sys.exc_info()[1]}], line: [{sys.exc_info()[2].tb_lineno}]")
            return_status = False

        return return_status

