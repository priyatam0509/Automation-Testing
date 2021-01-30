__author__ = 'Joe Paxton'

import requests
import json
import logging

from app.util import constants, server, runas, system
from app.simulators import basesim

log = logging.getLogger()

class PinPad(basesim.Simulator):
    EMV = "EMV"
    MAGSTRIPE = "Magstripe"

    def __init__(self, endpoint):
        """
        Initializes the PinPad class.
        Args:
            endpoint : (str) The web-endpoint for the API.
            sim_obj : (str) The simulator's name.
        """
        basesim.Simulator.__init__(self, endpoint, 'pinpad')

    def use_card(self, brand='Core', card_name='Visa', debit_fee=False, cashback_amount=None, zip_code=None, cvn=None, custom=None, force_swipe=False):
        """
        Sends a POST request to the PIN Pad Simulator that will simulate swiping or inserting a card with the
        card name you passed in. Swipe or insert is determined based on the card's "Type" property.
        Args:
            brand   : (str) String representation of the Brand (found in CardData.json)
            card_name : (str) The key/name of the card you wish to use located in the CardData.json file.
            debit_fee : (bool) If Debit Fee is prompted and set to True, we click OK; otherwise, we click No.
            cashback_amount: (str) The cashback amount you wish to enter
            zip_code : (str) The ZIP code value you wish to enter
            cvn      : (str) The CVN value you wish to enter
            custom : (str) The Custom prompt value you wish to enter
            force_swipe : (bool) Force an EMV card to be swiped instead of inserted.
        Returns:
            dict: Dictionary containing a success message and a payload of the data you sent.
        Examples:
        >>> insert_card(
            card_name='EMVVisaUSDebit',
            debit_fee=True,
            cashback_amount='10.00'
        )
        True
        >>> insert_card(
            card_name='EMVVisaCredit'
        )
        True
        """
        card_data = self._get_card_data(brand, card_name)
        if 'Type' not in card_data:
            log.warning(f"Card {card_name} is missing a Type property. Please specify a Type property as either {PinPad.MAGSTRIPE} or {PinPad.EMV}.")
            return None
        card_type = card_data['Type']
        if card_type == PinPad.MAGSTRIPE or force_swipe:
            action = '/swipe'
        elif card_type == PinPad.EMV:
            action = '/insert'
        else:
            log.warning(f"Card {card_name} has invalid Type {card_data['Type']}. Please specify either {PinPad.MAGSTRIPE} or {PinPad.EMV}.")
            return None

        # Arguments given by scripter that will be sent in POST request.
        if debit_fee is not None:
            card_data['DebitFee'] = debit_fee
        if cashback_amount is not None:
            card_data['CashBackAmount'] = cashback_amount
        if zip_code is not None:
            card_data['ZipCode'] = zip_code
        if custom is not None:
            card_data['Custom'] = custom
        if cvn is not None:
            card_data['CVN'] = cvn

        # Keys in JSON file that will be sent in the POST request.
        if 'VehicleID' not in card_data:
            card_data['VehicleID'] = None
        if 'Odometer' not in card_data:
            card_data['Odometer'] = None
        if 'DriverID' not in card_data:
            card_data['DriverID'] = None
        if 'Fuel' not in card_data:
            card_data['Fuel'] = None
        if 'EmployeeID' not in card_data:
            card_data['EmployeeID'] = None
        if 'AID' not in card_data and card_type == PinPad.EMV:
            log.warning(f"EMV card {card_name} requires an AID property. Please add one.")
            return None
        if 'CVM' not in card_data and card_type == PinPad.EMV:
            card_data['CVM'] = None

        return self.post(action, card_data)

    def insert_card(self, brand='Core', card_name='EMVVisaCredit', debit_fee=False, cashback_amount=None, zip_code=None, cvn=None, custom=None):
        """
        Sends a POST request to the PIN Pad Simulator that will simulate inserting an EMV card with the
        card name you passed in.
        Args:
            brand   : (str) String representation of the Brand (found in CardData.json)
            card_name : (str) The key/name of the card you wish to use located in the CardData.json file.
            debit_fee : (bool) If Debit Fee is prompted and set to True, we click OK; otherwise, we click No.
            cashback_amount: (str) The cashback amount you wish to enter
            zip_code : (str) The ZIP code value you wish to enter
            cvn      : (str) The CVN value you wish to enter
            custom : (str) The Custom prompt value you wish to enter
        Returns:
            dict: Dictionary containing a success message and a payload of the data you sent.
        Examples:
        >>> insert_card(
            card_name='EMVVisaUSDebit',
            debit_fee=True,
            cashback_amount='10.00'
        )
        True
        >>> insert_card(
            card_name='EMVVisaCredit'
        )
        True
        """
        action = '/insert'
        card_data = self._get_card_data(brand, card_name)
        try:
            # Arguments given by scripter that will be sent in POST request.
            if debit_fee is not None:
                card_data['DebitFee'] = debit_fee
            if cashback_amount is not None:
                card_data['CashBackAmount'] = cashback_amount
            if zip_code is not None:
                card_data['ZipCode'] = zip_code
            if custom is not None:
                card_data['Custom'] = custom
            if cvn is not None:
                card_data['CVN'] = cvn

            # Keys in JSON file that will be sent in the POST request.
            if 'VehicleID' not in card_data:
                card_data['VehicleID'] = None
            if 'Odometer' not in card_data:
                card_data['Odometer'] = None
            if 'DriverID' not in card_data:
                card_data['DriverID'] = None
            if 'Fuel' not in card_data:
                card_data['Fuel'] = None
            if 'EmployeeID' not in card_data:
                card_data['EmployeeID'] = None
            if 'AID' not in card_data: # This should always be in the card - should have error.
                card_data['AID'] = None
            if 'CVM' not in card_data:
                card_data['CVM'] = None
            return self.post(action, card_data)

        except Exception as e:
            log.warning(e)

    #TODO Remove brand and read it from any of the numerous places we keep it
    def swipe_card(self, brand='Core', card_name='Visa', debit_fee=False, cashback_amount=None, zip_code=None, cvn=None, custom=None):
        """
        Sends a POST request to the PIN Pad Simulator that will simulate swiping a card with the
        card name you passed in.
        Args:
            brand   : (str) String representation of the Brand (found in CardData.json)
            card_name : (str) The key/name of the card you wish to use located in the CardData.json file.
            debit_fee : (bool) If Debit Fee is prompted and set to True, we click OK; otherwise, we click No.
            cashback_amount: (str) The cashback amount you wish to enter
            zip_code : (str) The ZIP code value you wish to enter
            cvn      : (str) The CVN value you wish to enter
            custom : (str) The Custom prompt value you wish to enter
        Returns:
            dict: Dictionary containing a success message and a payload of the data you sent.
        Examples:
        >>> swipe_card(
            brand='Citgo',
            card_name='GiftCard'
        )
        >>> swipe_card(
            card_name='Debit',
            debit_fee=True,
            cashback_amount='10.00'
        )
        >>> swipe_card(
            card_name='VisaFleet1_NoRestrictions',
            cvn='123',
            zip_code='27587'
        )
        """
        action = '/swipe'
        card_data = self._get_card_data(brand, card_name)
        try:
            # Arguments given by scripter that will be sent in POST request.
            if debit_fee is not None:
                card_data['DebitFee'] = debit_fee
            if cashback_amount is not None:
                card_data['CashBackAmount'] = cashback_amount
            if zip_code is not None:
                card_data['ZipCode'] = zip_code
            if custom is not None:
                card_data['Custom'] = custom
            if cvn is not None:
                card_data['CVN'] = cvn

            # Keys in JSON file that will be sent in the POST request.
            if 'VehicleID' not in card_data:
                card_data['VehicleID'] = None
            if 'Odometer' not in card_data:
                card_data['Odometer'] = None
            if 'DriverID' not in card_data:
                card_data['DriverID'] = None
            if 'Fuel' not in card_data:
                card_data['Fuel'] = None
            if 'EmployeeID' not in card_data:
                card_data['EmployeeID'] = None
            return self.post(action, card_data)

        except Exception as e:
            log.warning(e)

    def manual_entry(self, brand='Core', card_name='Visa', zip_code=None, custom=None):
        """
        Sends a POST request to the PIN Pad Simulator that will simulate manual entering the
        card name you passed in.
        Args:
            brand   : (str) String representation of the Brand (found in CardData.json)
            card_name : (str) The key/name of the card you wish to use located in the CardData.json file.
            zip_code : (str) The ZIP code value you wish to enter
            custom : (str) The Custom prompt value you wish to enter
        Returns:
            dict: Dictionary containing a success message and a payload of the data you sent.
        Examples:
            >>> manual_entry(
                brand='Generic',
                card_name='GiftCard'
            )
            >>> manual_entry(
                brand='Core',
                card_name='Discover'
            )
        """
        action = '/manual_entry'
        log.debug(f"Checking {constants.CARD_DATA_MANUAL} for {card_name}")
        card_data ={}
        with open(constants.CARD_DATA_MANUAL, 'r') as fp:
            card_data_file = json.load(fp)
            try:
                card_data = card_data_file[system.get_brand().upper()][card_name]
            except:
                log.warning(f"Unable to find {card_name} within {constants.CARD_DATA_MANUAL}.")
        if not card_data:
            log.debug(f"Checking {constants.CARD_DATA} for {card_name}")
            brand = brand.upper()
            card_data = self._get_card_data(brand, card_name)

        try:
            # Arguments given by scripter that will be sent in POST request.
            card_data['ZipCode'] = zip_code
            card_data['Custom'] = custom

            # Keys in JSON file that will be sent in the POST request.
            if 'VehicleID' not in card_data:
                card_data['VehicleID'] = None
            if 'Odometer' not in card_data:
                card_data['Odometer'] = None
            if 'DriverID' not in card_data:
                card_data['DriverID'] = None
            if 'Fuel' not in card_data:
                card_data['Fuel'] = None
            if 'EmployeeID' not in card_data:
                card_data['EmployeeID'] = None

            return self.post(action, card_data)
        
        except Exception as e:
            log.warning(e)
    
    def swipe_loyalty(self, brand='Core', card_name='Loyalty'):
        """
        Sends a POST request to the PIN Pad Simulator that will simulate swiping a loyalty card with the
        card name you passed in.
        Args:
            brand   : (str) String representation of the Brand (found in CardData.json)
            card_name : (str) The key/name of the card you wish to use located in the CardData.json file.
        Examples:
        >>> swipe_loyalty(
            brand='Core',
            card_name="Loyalty"
        )
        """
        action = '/swipe_loyalty'
        card_data = self._get_card_data(brand, card_name)
        return self.post(action, card_data)

    def start(self):
        log.debug(f"Starting pinpad simulator")
        return server.server.start()

    def stop(self):
        log.debug(f"Stopping pinpad simulator")
        return server.server.stop()
    
    def reset(self):
        log.debug(f"Resetting pinpad simulator and clearing queued up contents")
        reset = server.server.reset('pinpad')
        import time
        time.sleep(1)
        return reset


def init_pinpadsim():
    """
    Creates an instance of the pinpadsim using the IP given from the
    Docker Manager application running on the Server.
    """
    ip_addr = server.server.get_site_info()['ip']

    with open(constants.STANDARD_CONFIG, 'r') as fp:
        json_data = json.load(fp)
        json_data["express"]["Clients"]["1"]["IP Address"] = ip_addr
        json_data["passport"]["Manager"]["IP Address"] = ip_addr
        json_data["edge"]["Manager"]["IP Address"] = ip_addr
    with open(constants.STANDARD_CONFIG, 'w') as fp:
        fp.write(json.dumps(json_data, indent=4, separators=(',', ':')))
    pinpad = PinPad(endpoint=f"http://{ip_addr}/")
    return pinpad
