"""
    File name: mobilepay_inside.py
    Tags:
    StoryID:
    Description: Conexxus Mobile Payment Inside support common functions
    to support the automation projecct
    Author: Pavan Kumar Kantheti
    Date created: 2020-06-24 10:20:30
    Date last modified:
    Python Version: 3.7
"""
from app import system
from app.simulators import serial_scanner
from pywinauto.application import Application
from app.util import constants
import logging
import time
import psutil
import sys
import xml.etree.ElementTree as ET

log = logging.getLogger()
grades_data = ["001", "002", "003", "004"]


# CONEXXUS MOBILE PAYMENT DESKTOP HOST SIM FUNCTIONS


def update_mobile_data(default_schema_version="2.0", default_merchant="0146-2380", default_port="5000", default_TLS_enabled=False, default_site="0146-2380", default_host="127.0.0.1", buffer_size="1024", default_cert="GVRHostsimCert.pfx", default_cert_pwd="GVRHostsimCert", heart_beat="45", heart_beat_timeout="60", log_file="ConexxusMobileSim.log", log_roll="10", log_to_file=True, max_log_size="25", response_timeout="30"):
    """
    Modify/Update the conexxus mobile data XML based on the parameters, all the parameter value will set to mobile data xml path
    Args:   default_schema_version (string) - ("2.0"/ "1.0")
            default_merchant (string)
            default_port (string)
            default_TLS_enabled (bool)
            default_site (string)
            default_host (string)
            buffer_size (string)- value should be numeric
            default_cert (string)
            default_cert_pwd (string)
            heart_beat (string) - value should be numeric
            heart_beat_timeout (string) - value should be numeric
            log_file (string)
            log_roll (string) - value should be numeric
            log_to_file (bool)
            max_log_size (string) - value should be numeric
            response_timeout (string) - value should be numeric
    Returns: True/ False
    """
    return_status = False
    try:
        log.info("Processing... [update_mobile_data]")
        tree = ET.parse(constants.MOBILE_DATA_PATH)
        root = tree.getroot()
        index = 0
        while (index < len(root)):
            if (root[index].tag.lower() == "defaultschemaversion"):
                root[index].text = default_schema_version
            elif (root[index].tag.lower() == "defaultmerchantid"):
                root[index].text = default_merchant
            elif (root[index].tag.lower() == "defaultport"):
                root[index].text = default_port
            elif (root[index].tag.lower() == "defaulttlsenabled"):
                root[index].text = str(default_TLS_enabled)
            elif (root[index].tag.lower() == "defaultsiteid"):
                root[index].text = default_site
            elif (root[index].tag.lower() == "defaulthostaddress"):
                root[index].text = default_host
            elif (root[index].tag.lower() == "buffersize"):
                root[index].text = buffer_size
            elif (root[index].tag.lower() == "defaultcertfilename"):
                root[index].text = default_cert
            elif (root[index].tag.lower() == "defaultcertpw"):
                root[index].text = default_cert_pwd
            elif (root[index].tag.lower() == "heartbeatinterval"):
                root[index].text = heart_beat
            elif (root[index].tag.lower() == "heartbeattimeout"):
                root[index].text = heart_beat_timeout
            elif (root[index].tag.lower() == "logfilename"):
                root[index].text = log_file
            elif (root[index].tag.lower() == "logrollinterval"):
                root[index].text = log_roll
            elif (root[index].tag.lower() == "logtofile"):
                root[index].text = str(log_to_file)
            elif (root[index].tag.lower() == "maxlogsize"):
                root[index].text = max_log_size
            elif (root[index].tag.lower() == "responsetimeout"):
                root[index].text = response_timeout
            index = index + 1
        tree.write(constants.MOBILE_DATA_PATH)
        return_status = True
    except:
        log.error(f"Error at [update_mobile_data] - [{sys.exc_info()[0]}]. [{sys.exc_info()[1]}], line: [{sys.exc_info()[2].tb_lineno}]")

    return return_status


def update_rewards(reward_name="Fuel Reward", promotion_reason="loyaltyOffer", amount="0.10", unit_price="0.10", quantity="1", maximum_quantity="999", reward_applied=False, price_adj="11111", program_id="22222", trans_reward=True, rebate_label="Above Site Fuel Reward", disable_reward=False, auth_request=True, loyalty_req=True, trans_prod_code="900", network_grades=["001", "002", "003", "004"]):
    """
    Modify/ Update the conexxus mobile rewards config xml file
    Args:   reward_name (string)
            promotion_reason (string) - value should be in any {"loyaltyOffer", "combinationOffer", "mixAndMatchOffer", "posFuelDiscount", "posPromotion", "other"}
            amount (string) - any numeric value with with 2 decimals
            unit_price (string) - any numeric value with with 2 decimals
            quantity (string) - any numeric value
            maximum_quantity (string) - any numeric value
            reward_applied (bool)
            price_adj (sring)
            program_id (string) - any numeric value
            trans_reward (bool)
            rebate_label (string)
            disable_reward (bool)
            auth_request (bool)
            loyalty_req (bool) 
            trans_prod_code (string) - any numeric value
            network_grades (list)
    Returns:True/ False
    """
    global grades_data
    return_status = False
    try:
        log.info("Processing... [update_rewards]")
        tree = ET.parse(constants.REWARDS_PATH)
        root = tree.getroot()
        index = 0
        while (index < len(root[0])):
            if (root[0][index].tag.lower() == "rewardname"):
                root[0][index].text = reward_name
            elif (root[0][index].tag.lower() == "promotionreason"):
                root[0][index].text = promotion_reason
            elif (root[0][index].tag.lower() == "amount"):
                root[0][index].text = amount
            elif (root[0][index].tag.lower() == "unitprice"):
                root[0][index].text = unit_price
            elif (root[0][index].tag.lower() == "quantity"):
                root[0][index].text = quantity
            elif (root[0][index].tag.lower() == "maximumquantity"):
                root[0][index].text = maximum_quantity
            elif (root[0][index].tag.lower() == "rewardapplied"):
                root[0][index].text = str(reward_applied).lower()
            elif (root[0][index].tag.lower() == "priceadjustmentid"):
                root[0][index].text = price_adj
            elif (root[0][index].tag.lower() == "programid"):
                root[0][index].text = program_id
            elif (root[0][index].tag.lower() == "transactionalreward"):
                root[0][index].text = str(trans_reward).lower()
            elif (root[0][index].tag.lower() == "rebatelabel"):
                root[0][index].text = rebate_label
            elif (root[0][index].tag.lower() == "disablereward"):
                root[0][index].text = str(disable_reward).lower()
            elif (root[0][index].tag.lower() == "authrequest"):
                root[0][index].text = str(auth_request).lower()
            elif (root[0][index].tag.lower() == "loyaltyrequest"):
                root[0][index].text = str(loyalty_req).lower()
            elif (root[0][index].tag.lower() == "transactionproductcode"):
                root[0][index].text = trans_prod_code
            index = index + 1

        if not(network_grades == grades_data):
            index_cnt = len(root[0])
            delete_status = True
            while(delete_status):
                if (root[0][index_cnt-1].tag.lower() == "poscode"):
                    root[0].remove(root[0][index_cnt-1])
                else:
                    delete_status = False
                index_cnt = index_cnt - 1

            grades_data = network_grades
            grade_cnt = len(network_grades)
            index = 0
            while (index < grade_cnt):
                ET.SubElement(root[0], 'POSCode')
                for elem in root.iter('POSCode'):
                    if (elem.text is None):
                        elem.text = network_grades[index]
                index = index + 1

        tree.write(constants.REWARDS_PATH)
        return_status = True
    except:
        log.error(f"Error at [update_rewards] - [{sys.exc_info()[0]}]. [{sys.exc_info()[1]}], line: [{sys.exc_info()[2].tb_lineno}]")
    return return_status


def update_settings(version="2.0", loyalty="False"):
    """
    Set/ Update the conexxus settings - version number and apply loyalty or not
    Args:   version (string)- ("2.0"/ "1.0")
            loyalty (string) - value sholuld be in any {"True", "False"}
    Returns: True/ False
    """
    return_status = False
    try:
        log.info("Processing... [update_settings]")
        tree = ET.parse(constants.SETTINGS_PATH)
        root = tree.getroot()
        index = 0
        while (index < len(root)):
            if (root[index].tag.lower() == "schemaversion"):
                root[index].text = version
            elif (root[index].tag.lower() == "loyalty"):
                root[index].text = loyalty
            index = index + 1
        tree.write(constants.SETTINGS_PATH)
        return_status = True
    except:
        log.error(f"Error at [update_settings] - [{sys.exc_info()[0]}]. [{sys.exc_info()[1]}], line: [{sys.exc_info()[2].tb_lineno}]")
    return return_status


def perform_conexxus_event_withscan():
    """
    Perform Conexxus mobile payment with QR scan event at POS
    Args: None
    Returns: True/ False
    """
    status = False
    try:
        log.info("Processing... [perform_conexxus_event_withscan]")
        app = Application(backend="uia").start(constants.CONEXXUS_EXE)
        time.sleep(10)
        mi_w = app.top_window()
        time.sleep(2)
        scanner = serial_scanner.SerialScanner(port=3)
        scanner.scan('MCX.123')
        time.sleep(2)
        simr = mi_w.child_window(title="Send Inside MobileAuth Request", auto_id=" m_sendMobileAuthRequest", control_type="Button")
        time.sleep(1)
        simr.click_input()
        time.sleep(5)
        status = stop_conexxus()
    except:
        log.error(f"Error at [perform_conexxus_event_withscan] - [{sys.exc_info()[0]}]. [{sys.exc_info()[1]}], line: [{sys.exc_info()[2].tb_lineno}]")
        system.restartpp()
        pos_load()
    return status


def stop_conexxus():
    """
    Stop the Conexxus Mobile Simulator dektop application
    Args: None
    Return: status (True/ False)
    """
    try:
        status = False
        ProcName = "ConexxusMobileSimulator.exe"
        for proc in psutil.process_iter():
            # check whether the process name matches
            if (proc.name() == ProcName):
                proc.kill()
                status = True
    except:
        log.error(f"Unable to stop the 'ConexxusMobileSimulator.exe' - [{sys.exc_info()[0]}]. [{sys.exc_info()[1]}], line: [{sys.exc_info()[2].tb_lineno}]")
        status = False
    return status
