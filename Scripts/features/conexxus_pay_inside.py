"""
    File name: conexxus_pay_inside.py
    Tags:
    StoryID:
    Description: Conexxus Mobile Payment Inside support common functions
    to support the automation projecct
    Author: Pavan Kumar Kantheti
    Date created: 2020-06-24 10:20:30
    Date last modified:
    Python Version: 3.7
"""
from app import Navi, mws, pos, system, crindsim, pinpad, pdl
from app.simulators import loyaltysim, mobilepay_inside
from app.features import fuel_discount_maint, mobile_payment, loyalty
from app.util import constants
import logging
import time
import json
import sys
import xml.etree.ElementTree as ET

log = logging.getLogger()
conexxus_version = "2.0"
apply_loyalty = False


def load_conexxus(version):
    """
    Load the conexxus mobile payment configuration with no
    (Fuel Discount + Site Loyaltlty + site above reward)
    Args: version (string)
    Returns: string
    """
    status = _configure_conexxus(version)
    if (not status):
        return (f"Failed, unable to perform [configure_conexxus] at [load_conexxus {version}]")
    status = mobilepay_inside.update_mobile_data(default_schema_version=version)
    if (not status):
        return (f"Failed, unable to perform [update_mobile_data] at [load_conexxus {version}]")
    status = mobilepay_inside.update_rewards(disable_reward="true")
    if (not status):
        return (f"Failed, unable to perform [update_rewards] at [load_conexxus {version}]")
    status = mobilepay_inside.update_settings(version, "False")
    if (not status):
        return (f"Failed, unable to perform [update_settings] at [load_conexxus {version}]")
    status = loyalty_setting(apply=False)
    if (not status):
        return (f"Failed, unable to perform [loyalty_setting] at [load_conexxus {version}]")
    return ""


def process_pdl():
    """
    Call the PDL before card transactions.
    Args: None
    Returns: True/ False
    """
    log.info("Processing... [process_pdl]")
    try:
        pd = pdl.ParameterDownload()
        if not pd.request():
            log.warning("Failed PDL Download")
            return False
        return True
    except:
        log.error(f"Error at [process_pdl] - [{sys.exc_info()[0]}]. [{sys.exc_info()[1]}], line: [{sys.exc_info()[2].tb_lineno}]")
        return False


def restart_passport():
    """
    Restart the passport system and Load POS
    """
    system.restartpp()
    time.sleep(5)
    mws.sign_on()
    pos_load()


def get_settings_data():
    """
    Get/ Fetch the conexxus settings - version number and loyalty based on the parameter
    Args: None
    Returns: None
    """
    global apply_loyalty, conexxus_version
    try:
        log.info("Processing... [get_settings_data]")
        tree = ET.parse(constants.SETTINGS_PATH)
        root = tree.getroot()
        index = 0
        while (index < len(root)):
            if (root[index].tag.lower() == "schemaversion"):
                conexxus_version = root[index].text
                log.info(f"conexxus_version [{conexxus_version}] from [get_settings_data]")
            elif (root[index].tag.lower() == "loyalty"):
                apply_loyalty = eval(root[index].text)
                log.info(f"apply_loyalty [{str(apply_loyalty)}] from [get_settings_data]")
            index = index + 1
    except:
        log.error(f"Error at [get_settings_data] - [{sys.exc_info()[0]}]. [{sys.exc_info()[1]}], line: [{sys.exc_info()[2].tb_lineno}]")

# MWS GUI FUNCTIONS


def loyalty_setting(apply=True, version="2.0", trans_level=False):
    """
    loyalty interface modification based on the parameter
    Args:   apply (bool)
            version (string)
            trans_level (bool)
    Returns: True/ False
    """
    status = False
    try:
        log.info("Processing... [loyalty_setting]")
        if not(trans_level):
            obj_loyalty = loyalty.LoyaltyInterface()
            loyalty_name = "Kickback"
            card_mask_to_add = ['6008']
            if (apply):
                cfg = {
                    'General': {
                        'Enabled': 'Yes',
                        'Host IP Address': '10.5.48.2',
                        'Port Number': '7900',
                        'Site Identifier': '1',
                        'Send all transactions to loyalty provider': 'Yes'
                    }
                }
                is_exist = mws.set_value("Loyalty Providers", loyalty_name)
                if (is_exist):
                    status = obj_loyalty.change_provider(cfg, loyalty_name, cards_to_add=card_mask_to_add)
                else:
                    status = obj_loyalty.add_provider(cfg, loyalty_name, cards=card_mask_to_add)
                _load_loyalty(version, trans_level)
            else:
                cfg = {
                    'General': {
                        'Enabled': 'No'
                    }
                }
                status = obj_loyalty.change_provider(cfg, loyalty_name)
                loyaltysim.StopLoyaltySim()
            mws.click_toolbar("Exit")
        else:
            _load_loyalty(version, trans_level)
            status = True
    except:
        log.error(f"Unable to [loyalty_setting] - [{sys.exc_info()[0]}]. [{sys.exc_info()[1]}], line: [{sys.exc_info()[2].tb_lineno}]")
    return status


def _config_conexxus_json(version, update=False):
    """
    get the json dictionary based on the parameters
    Args:   version (string)
            update (bool)
    Returns:json dictionary 
    """
    json_config = '"General": {"Page 1": {"Provider Name": "Paydiant", "Enabled": "Yes", "Site ID": "77377", "Host Address": "10.5.48.2", "Port Number": "5000", "Schema Version": "'+ version + '", "Merchant ID": "0146-2380", "Settlement Software Version": "99.99", "Settlement Passcode": "Passcode", "Settlement Employee": "Employee"}, "Page 2": {"Use TLS": "No", "OCSP Mode": "Strict", "TLS Certificate Name": "TLSCertificateName"}}'
    if not(update):
        json_config = '"Mobile Provider Name": "Paydiant",' + json_config
        json_config = json_config + ', "Local Fuel Discounts": { "Mobile Local Discount Code": "MLDC1", "Mobile Local Discount Description": "Test Automated", "Fuel Discount Group": "NONE"}'
    json_config = '{' + json_config + '}'
    json_data = json.loads(json_config)
    return json_data


def _configure_conexxus(version):
    """
    Add/ Update the Mobile Payment Configuration based on the version
    Args:   version (string)
    Returns:True/ False
    """
    status = False
    try:
        log.info("Processing... [configure_conexxus]")
        mpc = mobile_payment.MobilePaymentConfiguration()
        is_exist = mws.set_value("Mobile Providers", "Paydiant")
        QR_list = ["MCX."]
        if (is_exist):
            # Modify the provider's configuration
            mpc_info = _config_conexxus_json(version, True)
            mpc = mobile_payment.MobilePaymentConfiguration()
            log.info("'Paydiant' is already exist. So updating with default data.")
            time.sleep(10)
            status = mpc.change_provider(mpc_info, 'Paydiant', "NONE", QR_list)
        else:
            mpc_info = _config_conexxus_json(version, False)
            mpc = mobile_payment.MobilePaymentConfiguration()
            log.info("'Paydiant' is not exist. Adding the with default data.")
            status = mpc.configure(mpc_info, "NONE", QR_list, False)
        mws.click_toolbar("Exit")
    except:
        log.error(f"Error at [configure_conexxus] - [{sys.exc_info()[0]}]. [{sys.exc_info()[1]}], line: [{sys.exc_info()[2].tb_lineno}]")
    return status


def change_default_discount(apply=True):
    """
    Change the default discount for the existing mobile provider
    Args: apply (boolean)
    Return: True/ False
    """
    status = False
    try:
        log.info("Processing... [change_default_discount]")
        mpc_info = {
            "General": {
                "Page 1": {
                    "Enabled": "Yes",
                    "Settlement Software Version": "99.99"
                },
                "Page 2": {
                    "Use TLS": "No",
                    "OCSP Mode": "Strict",
                    "TLS Certificate Name": "TLSCertificateName"
                }
            }
        }
        if (apply):
            local_discount = constants.DISCOUNT_NAME
        else:
            local_discount = "NONE"
        mpc = mobile_payment.MobilePaymentConfiguration()
        log.info("'Paydiant' is already exist. So updating with default data.")
        time.sleep(2)
        mpc.change_provider(mpc_info, 'Paydiant', local_discount)
        mws.click_toolbar("Exit")
        status = True
    except:
        log.error(f"Error at [change_default_discount] - [{sys.exc_info()[0]}]. [{sys.exc_info()[1]}], line: [{sys.exc_info()[2].tb_lineno}]")
    return status


def add_fuel_discount():
    """
    Add fuel discount at MWS - Discount maintenance screen
    Args: None
    Returns: True/False
    """
    try:
        log.info("Processing... [add_fuelDiscount]")
        fdm = fuel_discount_maint.FuelDiscountMaintenance()
        mws.select_tab("Fuel Discount Groups")
        status = True
        disc_exist = mws.set_value("Discounts", constants.DISCOUNT_NAME, "Fuel Discount Groups")
        if not(disc_exist):
            fdm_info = {
                "Discount Group Name": "Discount 1",
                "Grades": {
                   "UNL SUP CAN": "0.200"
                }
            }
            fdm.add("Fuel Discount Groups", fdm_info)
            status = mws.set_value("Discounts", constants.DISCOUNT_NAME, "Fuel Discount Groups")
        mws.click_toolbar("Exit")
    except:
        log.error(f"Error at [add_fuelDiscount] - [{sys.exc_info()[0]}]. [{sys.exc_info()[1]}], line: [{sys.exc_info()[2].tb_lineno}]")
    return status

# LOYALTY SIM Calling FUNCTIONS


def _load_loyalty(version, trans_level=False):
    """
    Load the loyalty information
    Args:   version (string),
            trans_level (bool)
    Returns: None
    """
    log.info("Processing... [_load_loyalty]")
    log.info("Calling StartLoyaltySim()")
    loyaltysim.StartLoyaltySim()
    log.info("Calling DeleteAllLoyaltyIDs function")
    loyaltysim.DeleteAllLoyaltyIDs()
    log.info("Adding new loyalty with details 6008")
    loyalty_id = loyaltysim.AddLoyaltyIDs("6008", "6008", "6008", "6008", "6008")
    if (version == "2.0"):
        loyaltysim.UnAssignAllTransRewardsByLoyalty(loyalty_id)
        loyaltysim.UnAssignAllFuelRewardsByLoyalty(loyalty_id)
        _assign_loyalty_fuel_rewards(loyalty_id)
        _assign_loyalty_trans_rewards(loyalty_id)
    elif (version == "1.0"):
        loyaltysim.UnAssignAllTransRewardsByLoyalty(loyalty_id)
        loyaltysim.UnAssignAllFuelRewardsByLoyalty(loyalty_id)
        if (trans_level):
            _assign_loyalty_trans_rewards(loyalty_id)
        else:
            _assign_loyalty_fuel_rewards(loyalty_id)


def _assign_loyalty_fuel_rewards(loyalty_id):
    """
    Assign the Loyalty Fuel Rewards at Loyalty Desktop Simulator
    Args: loyalty_id (string)
    Returns: None
    """
    try:
        log.info("Processing... [assign_loyalty_fuel_rewards]")
        fuel_Reward = loyaltysim.AddFuelRewards(RewardName="FuelReward", RewardLimit="9999", ReceiptText="05 Cents Discount")
        loyaltysim.AddFuelGrades(fuel_Reward, FuelGrades="001:0.05, 002:0.05, 003:0.05, 004:0.05, 005:0.05")
        status = loyaltysim.AssignFuelReward(LoyatyID=loyalty_id, FuelID=fuel_Reward)
        log.info(f"[assign_loyalty_fuel_rewards] status =[{str(status)}]")
    except:
        log.error(f"Error at [assign_loyalty_fuel_rewards] - [{sys.exc_info()[0]}]. [{sys.exc_info()[1]}], line: [{sys.exc_info()[2].tb_lineno}]")


def _assign_loyalty_trans_rewards(loyalty_id):
    """
    Assign the Loyalty Transaction level Rewards at Loyalty Desktop Simulator
    Args: loyalty_id (string)
    Returns: None
    """
    try:
        log.info("Processing... [assign_loyalty_trans_rewards]")
        trans_reward = loyaltysim.AddTransactionReward(RewardName="20 cents trans. rwd")
        status = loyaltysim.AssignTransactionReward(LoyatyID=loyalty_id, TransactionID=trans_reward)
        log.info(f"[assign_loyalty_trans_rewards] status =[{str(status)}]")
    except:
        log.error(f"Error at [assign_loyalty_trans_rewards] - [{sys.exc_info()[0]}]. [{sys.exc_info()[1]}], line: [{sys.exc_info()[2].tb_lineno}]")

# POS COMMON FUNCTIONS


def _check_split_payment():
    """
    After card payment, check either split payment has to do? If yes, allow to do split payment
    Args:   None
    Returns:None
    """
    try:
        msg = pos.read_message_box()
        time.sleep(1)
        log.info(f"message box text. [{msg}]")
        if not(msg is None):
            if (msg.lower().find('split pay?')> 0):
                pos.click_message_box_key("YES")
                pos.pay()
    except:
        log.error(f"Error at [_check_split_payment] [{sys.exc_info()[0]}]. [{sys.exc_info()[1]}], line: [{sys.exc_info()[2].tb_lineno}]")
    time.sleep(3)


def _pay_by_card(card_type):
    """
    pay the transaction by card with card_type.
    Args:   card_type (string)
    Returns:True/ False
    """
    status = False
    try:
        log.info("Processing... [_pay_by_card]")
        pos.click("PAY")
        time.sleep(2)
        pos.click("CARD")
        time.sleep(2)
        pinpad.swipe_card(card_name=card_type)
        _check_split_payment()
        status =  True
    except:
        log.error(f"Error at [_pay_by_card] - [{sys.exc_info()[0]}]. [{sys.exc_info()[1]}], line: [{sys.exc_info()[2].tb_lineno}]")
    return status


def _payment_Conexxus_Mobile():
    """
    Perform Conexxus mobile payment as MOP
    Args: None
    Returns: True/ False
    """
    # Click on Pay 'CARD' button
    global apply_loyalty, conexxus_version
    status = False
    try:
        log.info("Processing... [_payment_Conexxus_Mobile]")
        pos.click("PAY")
        time.sleep(2)
        if (apply_loyalty and conexxus_version == "1.0"):
            # Swipe Loyalty Card and Pay transaction by CASH
            pos.click_message_box_key("YES")
            time.sleep(2)
            pinpad.swipe_card(card_name="Loyalty")
            time.sleep(5)
            status = pos.pay()
            return status
        else:
            if (apply_loyalty):
                pos.click_message_box_key("NO")
                time.sleep(2)
            pos.click("CARD")
            status = mobilepay_inside.perform_conexxus_event_withscan()
    except:
        log.error(f"Error at [_payment_Conexxus_Mobile] - [{sys.exc_info()[0]}]. [{sys.exc_info()[1]}], line: [{sys.exc_info()[2].tb_lineno}]")
    return status


def _pos_wait(on_load=False):
    """
    System wait time up to Ready to perform the transactions.
    Restart passport for any issue or struck at transaction in between
    Args: on_load (bool)
    Returns: None
    """
    time.sleep(2)
    if (on_load):
        pos.select_dispenser(1)
    status = "Check"
    max_attempts = 1
    while (status != "EMPTY" and max_attempts <= 3):
        time.sleep(2)
        status = pos.read_fuel_buffer()[0]
        max_attempts = max_attempts + 1
            
    # Restart Passport for any issue or struck at transaction in between
    status_txt = pos.read_status_line().lower()
    if (status_txt.find('swipe') > 0):
        log.warning(f"screen status text is : [{status_txt}]")
        restart_passport()
    else:
        if (on_load):
            if (status_txt.find('wait') > 0):
                    log.warning(f"screen status text is : [{status_txt}]")
                    restart_passport()


def _fuel_buffer_check(buffer):
    """
    Check the fuel buffer status before performing the pos fuel transactions
    Args: buffer (string)
    Returns: True/ False
    """
    result = True
    status = pos.read_fuel_buffer(buffer)[0]
    log.warning(f"status[{status}] for buffer [{buffer}] @ [_fuel_buffer_check]")
    if (status != "EMPTY"):
        result = False
    return result


def _fuel_buffer_trans_check(buffer, lock_check=False):
    """
    Check the fuel buffer status after pos fuel transaction
    Args:   buffer (string)
            lock_check (bool)-lock status check
    Returns: True/ False
    """
    result = True
    status = pos.read_fuel_buffer(buffer)[0]
    max_attempt = 0
    while (status != 'FUEL SALE' and status != 'LOCKED' and max_attempt < 3):
        time.sleep(3)
        max_attempt += 1
        log.warning(f"Checking the FUEL STATE at [{status}] attempt [{max_attempt}]")
    if (max_attempt >= 3):
        return False
    return result


def pos_load():
    """
    Load/ Call the POS Sub system from MWS, sign on and connect
    Args: None
    Returns: None
    """
    # Navigate to POS screen
    Navi.navigate_to("POS")

    # Sign on to POS screen if not already sign-on
    pos.sign_on()


def _set_amount_crindsim(amount, target_type=""):
    """
    Set/update the crindsim Fuel amount or Money to dispenser
    Args:   amount (string)
            target_type (string) - "money" or Empty
    Returns: None
    """
    if (target_type == ""):
        crindsim.set_sales_target(target=amount)
    else:
        crindsim.set_sales_target(sales_type=target_type, target=amount)

# SALES TRASACTION RELATED


def _postpay_fuel(dispenser, buffer):
    """
    Perform the pospay fuel sale based on the dispenser and buffer
    Args:   dispenser (integer)
            buffer (string) - "A"/ "B"
    Returns: True/ False
    """
    log.warning("Processing... [_postpay_fuel]")
    status = _fuel_buffer_check(buffer)
    if not(status):
        buffer = "B"
    log.warning(f"Buffer [{buffer}] after the status [{status}] @ [_postpay_fuel]")
    pos.select_dispenser(dispenser)
    log.warning(f"Buffer [{buffer}] select disp [{dispenser}] @ [_postpay_fuel]")
    pos.click_forecourt_key("AUTH")
    log.warning(f"Buffer [{buffer}] select AUTH @ [_postpay_fuel]")
    pos.click_fuel_buffer(buffer)
    log.warning(f"Buffer [{buffer}] selected @ [_postpay_fuel]")
    time.sleep(2)
    status = _fuel_buffer_trans_check(buffer, True)
    if (status):
        pos.click_fuel_buffer(buffer)
        time.sleep(2)
    return status

def prepay_inside_payment(dispenser, grade, amount):
    """
    Login at POS and Performing THE pre-pay fuel sale and pay inside mobile payment
    Args: dispenser, grade, amount
    Returns: True/ False
    """
    # Add prepay sale item with amount
    status = False
    try:
        log.info("Processing... [prepay_inside_payment]")
        _set_amount_crindsim(amount)
        amount = str(int(amount) * 100)
        pos.add_fuel(amount, dispenser, "Prepay", grade)
        status = _payment_Conexxus_Mobile()
    except:
        log.error(f"Error at [prepay_inside_payment] - [{sys.exc_info()[0]}]. [{sys.exc_info()[1]}], line: [{sys.exc_info()[2].tb_lineno}]")
    return status


def manualfuel_inside_payment(dispenser, grade, amount):
    """
    Login at POS and Performing THE manual fuel sale and pay inside mobile payment
    Args: dispenser, grade, amount
    Returns: True/ False
    """
    status = False
    try:
        _pos_wait()
        log.info("Processing... [manualfuel_inside_payment]")
        amount = str(int(amount) * 100)
        pos.add_fuel(amount, dispenser, "manual", grade)
        status = _payment_Conexxus_Mobile()
    except:
        log.error(f"Error at [manualfuel_inside_payment] - [{sys.exc_info()[0]}]. [{sys.exc_info()[1]}], line: [{sys.exc_info()[2].tb_lineno}]")
    return status


def drysale_inside_payment(plu):
    """
    Performing the Dry sale transaction sale and pay inside mobile payment
    Args: plu
    Returns: True/ False
    """
    status = False
    try:
        log.info("Processing... [drysale_inside_payment]")
        _pos_wait()
        # Add item 2
        pos.add_item(plu, method="Speed Key")
        status = _payment_Conexxus_Mobile()
    except:
        log.error(f"Error at [drysale_inside_payment] - [{sys.exc_info()[0]}]. [{sys.exc_info()[1]}], line: [{sys.exc_info()[2].tb_lineno}]")
    return status


def presetsale_inside_payment(dispenser, buffer, grade, amount):
    """
    Performing the Preset fuel transaction sale and pay inside mobile payment
    Args: dispenser, buffer, grade, amount
    Returns: True/ False
    """
    # Add Preset fuel sale
    status = False
    try:
        log.info("Processing... [presetsale_inside_payment]")
        time.sleep(3)
        status = _fuel_buffer_check(buffer)
        _set_amount_crindsim(amount)
        amount = str(int(amount) * 100)
        pos.add_fuel(amount, dispenser, "preset", grade)
        time.sleep(5)
        if not(status):
            log.info("Adding previous buffer fuel transaction...")
            pos.click_fuel_buffer(buffer)
            buffer = "B"
            time.sleep(2)
        pos.click_fuel_buffer(buffer)
        time.sleep(2)
        status = _payment_Conexxus_Mobile()
    except:
        log.error(f"Error at [presetsale_inside_payment] - [{sys.exc_info()[0]}]. [{sys.exc_info()[1]}], line: [{sys.exc_info()[2].tb_lineno}]")
    return status


def carwash_inside_payment():
    """
    Performing the cawash sale transaction sale and pay inside mobile payment
    Args: None
    Returns: True/ False
    """
    status = False
    try:
        log.info("Processing... [carwash_inside_payment]")
        _pos_wait()
        # Add CAR WASH item
        pos.enter_keypad("1234", after="PLU")
        pos.click("ENTER")
        status = _payment_Conexxus_Mobile()
    except:
        log.error(f"Error at [carwash_inside_payment] - [{sys.exc_info()[0]}]. [{sys.exc_info()[1]}], line: [{sys.exc_info()[2].tb_lineno}]")
    return status


def postpay_inside_payment(dispenser, buffer, amount):
    """
    Performing the POST-pay transaction sale and pay inside mobile payment
    Args: dispenser, buffer, amount
    Returns: True/ False
    """
    status = False
    try:
        log.info("Processing... [postpay_inside_payment]")
        # Add post pay sale
        time.sleep(3)
        _set_amount_crindsim(amount, "money")
        status = _postpay_fuel(dispenser, buffer)
        if (status):
            status = _payment_Conexxus_Mobile()
        else:
            log.warning("Restarting the passport @ [postpay_inside_payment]")
            restart_passport()
    except:
        log.error(f"Error at [postpay_inside_payment] - [{sys.exc_info()[0]}]. [{sys.exc_info()[1]}], line: [{sys.exc_info()[2].tb_lineno}]")
    return status


def prepay_plus_inside_payment(dispenser, grade, amount, plu, card_type):
    """
    Login at POS and Performing THE pre-pay fuel + Carwash + Dry item sale and pay inside mobile payment
    Args: dispenser, grade, amount, plu
    Returns: True/ False
    """
    status = False
    try:
        log.info("Processing... [prepay_plus_inside_payment]")
        time.sleep(5)
        _set_amount_crindsim(amount)
        amount = str(int(amount) * 100)
        # Add CAR WASH item
        pos.enter_keypad("1234", after="PLU")
        pos.click("ENTER")
        # Add item on item3
        pos.add_item(plu, method="Speed Key")
        # Add prepay fuel item with $10
        pos.add_fuel(amount, dispenser, "Prepay", grade)
        if not(card_type == ''):
            status = _pay_by_card(card_type)
        else:
            status = _payment_Conexxus_Mobile()
    except:
        log.error(f"Error at [prepay_plus_inside_payment] - [{sys.exc_info()[0]}]. [{sys.exc_info()[1]}], line: [{sys.exc_info()[2].tb_lineno}]")
    return status


def postpay_plus_inside_payment(dispenser, buffer, amount, plu, card_type=''):
    """
    Login at POS and Performing post-pay fuel + Carwash + Dry item sale and pay inside mobile payment
    Args: dispenser, buffer, amount, plu
    Returns: True/ False
    """
    status = False
    try:
        log.info("Processing... [postpay_plus_inside_payment]")
        time.sleep(5)
        _set_amount_crindsim(amount, "money")
        # Add CAR WASH item
        pos.enter_keypad("1234", after="PLU")
        pos.click("ENTER")
        # Add item on item2
        pos.add_item(plu, method="Speed Key")
        # Add postpay fuel item with $05
        _postpay_fuel(dispenser, buffer)
        time.sleep(3)
        if not(card_type == ''):
            status = _pay_by_card(card_type)
        else:
            status = _payment_Conexxus_Mobile()
    except:
        log.error(f"Error at [postpay_plus_inside_payment] - [{sys.exc_info()[0]}]")
    return status


def presetsale_plus_inside_payment(dispenser, buffer, grade, amount, plu, card_type=''):
    """
    Performing the Preset fuel transaction + Drystock + Carwash sale and pay inside mobile payment
    Args: dispenser, buffer, grade, amount, plu
    Returns: True/ False
    """
    status = False
    try:
        log.info("Processing... [presetsale_plus_inside_payment]")
        # Add Preset fuel sale with dry item and car wash item
        time.sleep(5)
        _set_amount_crindsim(amount)
        # Add CAR WASH item
        pos.enter_keypad("1234", after="PLU")
        pos.click("ENTER")
        # Add item on item3
        pos.add_item(plu, method="Speed Key")
        time.sleep(5)
        status = _fuel_buffer_check(buffer)
        amount = str(int(amount) * 100)
        pos.add_fuel(amount, dispenser, "preset", grade)
        time.sleep(5)
        if not(status):
            log.info("Adding previous buffer fuel transaction...")
            pos.click_fuel_buffer(buffer)
            buffer = "B"
            time.sleep(1)
        pos.click_fuel_buffer(buffer)
        time.sleep(2)
        if not(card_type == ''):
            status = _pay_by_card(card_type)
        else:
            status = _payment_Conexxus_Mobile()
    except:
        log.error(f"Error at [presetsale_plus_inside_payment] - [{sys.exc_info()[0]}]. [{sys.exc_info()[1]}], line: [{sys.exc_info()[2].tb_lineno}]")
    return status


def manualfuel_plus_inside_payment(dispenser, grade, amount, plu, quantity=1, card_type=''):
    """
    Login at POS and Performing THE manual fuel plus dry item and pay inside mobile payment
    Args: dispenser, grade, amount, plu, quantity
    Returns: True/ False
    """
    status = False
    try:
        log.info("Processing... [manualfuel_plus_inside_payment]")
        # Add item
        if (quantity == 1):
            time.sleep(5)
            pos.add_item(plu, method="Speed Key")
        else:
            # Fractional Quantity
            time.sleep(3)
            _pos_wait()
            pos.add_item(plu, method="Speed Key", quantity=quantity)
        time.sleep(3)
        amount = str(int(amount) * 100)
        pos.add_fuel(amount, dispenser, "manual", grade)
        if not(card_type == ''):
            status = _pay_by_card(card_type)
        else:
            status = _payment_Conexxus_Mobile()
    except:
        log.error(f"Error at [manualfuel_plus_inside_payment] - [{sys.exc_info()[0]}]. [{sys.exc_info()[1]}], line: [{sys.exc_info()[2].tb_lineno}]")
    return status
