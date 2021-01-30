__author__ = 'Joe Paxton'

import requests
import json
import logging

from app.simulators import basesim
from app.util import system, server
from app import constants
from app import runas

log = logging.getLogger()

class NetworkSim(basesim.Simulator):
    def __init__(self, endpoint, sim_obj):
        """
        Parent class for all Simulators that inherits from BaseSim parent class.
        Args:
            endpoint : (str) The web-endpoint for the API.
            sim_obj : (str) The simulator's name.
        """
        basesim.Simulator.__init__(self, endpoint, sim_obj)
    
    def get_network_status(self):
        """
        Sends a GET request to the Network Sim and returns the network status.
        Args:
            None
        Returns:
            dict: Dictionary that represents the status and success of the GET request.
        Examples:
            >>> get_network_status()
            {'success': True, 'payload': {'ip': '10.80.31.235', 'status': 'Online'}}
            >>> get_network_status()['success']
            True
            >>> get_network_status()['payload']['status']
            'Online'
        """
        return self.get('/status')
    
    def start_simulator(self):
        """
        Sends a POST request to the Network Sim and starts the simulator.
        Args:
            None
        Returns:
            dict: Dictionary that represents the status after starting the simulator.
        Examples:
            >>> start_simulator()
            {'success': True, 'payload': {'status': 'Concord Network service has started.'}}
            >>> start_simulator()['success']
            True
            >>> start_simulator()['payload']['status']
            'Concord Network service has started.'
        """
        data = {'payload' : 'start'}
        return self.post('/status', data, dotnet_server=False)

    def stop_simulator(self):
        """
        Sends a POST request to the Network Sim and stops the simulator.
        Args:
            None
        Returns:
            dict: Dictionary that represents the status after stopping the simulator.
        Examples:
            >>> stop_simulator()
            {'success': True, 'payload': {'status': 'Concord Network service has stopped.'}}
            >>> stop_simulator()['success']
            True
            >>> stop_simulator()['payload']['status']
            'Concord Network service has stopped.'
        """
        data = {'payload' : 'stop'}
        return self.post('/status', data, dotnet_server=False)
    
    def get_response_mode(self):
        """
        Sends a GET request to the Network Sim and returns the response mode.
        Args:
            None
        Returns:
            dict: Dictionary that represents the status after getting the response code.
        Examples:
        >>> get_response_mode()
        {'success': True, 'payload': {'response_code': None, 'sim_mode': 'Automated'}}
        >>> get_response_mode()
        {'success': True, 'payload': {'response_code': 'C0', 'sim_mode': "Fixed 'C0'"}}
        >>> get_response_mode()['success']
        True
        >>> get_response_mode()['payload']['sim_mode']
        "Fixed 'C0'"
        """
        return self.get('/response_mode')
    
    def set_response_mode(self, response_code):
        """
        Sends a POST request to the Network Sim and sets the response mode to whatever you pass i
        Warning: The response code must be valid. See the UI for a list of valid response codes.
        Args:
            response_code : (str) Response code you want to change the Network Sim to.
        Returns:
            dict: Dictionary that represents the status after setting the response code.
        Examples:
        >>> set_response_mode('!2')
        {'success': True, 'payload': {'meaning': ' !2 - Invalid Driver number.', 'status': 'Successfully changed Response Mode to !2'}}
        >>> set_response_mode('Automated')
        {'success': True, 'payload': {'meaning': 'Automated - Approve whole dollar amount and Decline penny amounts', 'status': 'Successfully changed Response Mode to Automated'}}
        >>> set_response_mode('automated')['payload']['status']
        'Successfully changed Response Mode to Automated'
        """
        data = {'payload' : response_code}
        return self.post('/response_mode', data, dotnet_server=False)
    
    def get_prepaid_card(self):
        """
        Sends a GET request to the Network Sim and returns a list of lists for gift cards in the payload section of the dictionary.
        Each list within the list represents one gift card with AccountNumber, Active, PreAuthAmt, BalanceAmount, and ActivationAmount, respectively. 
        Args:
            None
        Returns:
            dict: Dictionary that represents the gift card data.
        Examples:
        >>> get_prepaid_card()
        {
            'success': True, 
            'payload': {
                'gift_card_data': [
                    ['6006491112345678916', 'False', 5.0, 50.0, 5.0], 
                    ['6006491499999908266', 'False', 5.0, 50.0, 5.0], 
                    ['6006495555555555555', 'False', 5.0, 50.0, 5.0], 
                    ['6006496666666666666', 'False', 5.0, 50.0, 5.0], 
                    ['6006497777777777777', 'False', 5.0, 50.0, 5.0], 
                    ['6006498888888888888', 'False', 5.0, 50.0, 5.0], 
                    ['6006499999999999999', 'False', 5.0, 10.0, 5.0], 
                    ['7000630219991022317', 'False', 5.0, 10.0, 5.0], 
                    ['7083310000017775248', 'False', 5.0, 10.0, 5.0]
                ]
            }
        }
        >>> get_prepaid_card()['payload']['gift_card_data'][0]
        ['6006491112345678916', 'False', 5.0, 50.0, 5.0]
        >>> account_number = get_prepaid_card()['payload']['gift_card_data'][0][0]
        '6006491112345678916'
        >>> active = get_prepaid_card()['payload']['gift_card_data'][0][1]
        'False'
        >>> balance_amount = get_prepaid_card()['payload']['gift_card_data'][0][3]
        '50.0'
        """
        return self.get('/prepaid_manager')
    
    def set_prepaid_manager(self, account_number, active, preauth_amount, balance_amount, activation_amount):
        """
        Sends a POST request to the Network Sim and returns a dictionary containing the gift card information you just set.
        Each list within the list represents one gift card with AccountNumber, Active, PreAuthAmt, BalanceAmount, and ActivationAmount, respectively. 
        Args:
            None
        Returns:
            dict: Dictionary that represents the gift card data.
        Examples:
        >>> set_prepaid_manager("600649000000000", True, "10.00", "50.00", "5.00")
        {
            'success': True,
            'payload': {
                'account_number': '600649000000000', 
                'activation_amount': '5.00', 
                'active': 'True', 
                'balance_amount': '50.00', 
                'preauth_amount': '10.00'
            }
        }
        >>> set_prepaid_manager("600649000000000", True, "10.00", "50.00", "5.00")['payload']['account_number']
        "600649000000000"
        """
        data = {
            'account_number' : account_number,
            'active' : active,
            'preauth_amount' : _strip_currency(preauth_amount),
            'balance_amount' : _strip_currency(balance_amount),
            'activation_amount' : _strip_currency(activation_amount)
        }
        return self.post('/prepaid_manager', data, dotnet_server=False)
    
    def get_partial_approval(self):
        """
        Sends a GET request to the Network Sim and returns a dictionary representing partial approval data.
        Warning: If partial approval is disabled, the partial approval amount will be None.
        Args:
            None
        Returns:
            dict: Dictionary that represents the partial approval amount and if it is enabled.
        Examples:
        >>> get_partial_approval()
        {
            'success': True, 
            'payload': {
                'amount': None,
                'enabled': False
            }
        }
        >>> get_partial_approval()['payload']['amount']
        None
        >>> get_partial_approval()
        {
            'success' : True,
            'payload' : {
                'amount' : '15.00',
                'enabled' : True,
            }
        }
        >>> get_partial_approval()['payload']['amount']
        "15.00"
        """
        return self.get('/partial_approval')
    
    def set_partial_approval(self, partial_approval_amount, enabled):
        """
        Sends a POST request to the Network Sim and updates partial approval data.
        Warning: If partial approval is disabled, the partial approval amount will be None.
        Args:
            partial_approval_amount : (str) String representation of the Partial Approval Amount.
            enabled : (bool) If True, enable partial approval; otherwise, disable partial approval.
        Returns:
            dict: Dictionary that represents the partial approval amount and if it is enabled.
        Examples:
        >>> set_partial_approval("1.00", True)
        {
            'success': True, 
            'payload': {
                'amount': '1.00', 
                'enabled': 'True'
            }
        }
        >>> set_partial_approval("1.00", True)['payload']['amount']
        "1.00"
        >>> set_partial_approval("10.00", False)
        {
            'success': True, 
            'payload': {
                'amount': None,
                'enabled': 'False'
            }
        }
        """
        if not enabled:
            partial_approval_amount = "99999.99"
        data = {
            'partial_approval_amount' : _strip_currency(partial_approval_amount),
            'status' : enabled
        }
        return self.post('/partial_approval', data, dotnet_server=False)


class Concord(NetworkSim):
    def __init__(self, endpoint, sim_obj='concord'):
        """
        Inherits from Network Sim parent class.
        Args:
            endpoint : (str) The web-endpoint for the API.
            sim_obj : (str) The simulator's name.
        Examples:
        >>> Concord(endpoint='http://10.4.18.118:5000/api/', sim_obj='concord')
        """
        NetworkSim.__init__(self, endpoint, sim_obj)
    
    def get_configuration_manager(self):
        """
        Sends a GET request to the Concord Network Sim and returns the configuration manager fields.
        Args:
            None
        Returns:
            dict: Dictionary that represents the status after getting the configuration manager fields.
        Examples:
        >>> get_configuration_manager()
        {'success': True, 'payload': {'address_line': '112 Tenbridge Ct.', 'city': 'Wake Forest', 'merchant_name': "Joe's Store", 'phone_number': '9192446403', 'state': 'NC', 'store_number': '4444', 'zip_code': '27587'}}
        >>> get_configuration_manager()['payload']['merchant_name']
        "Joe's Store"
        """
        return self.get('/config_manager')
    
    def set_configuration_manager(self, merchant_name, store_num, address_line, city, state, zip_code, phone_num):
        """
        Sends a POST request to the Concord Network Sim and returns the configuration manager fields that you set.
        Warning: The parameters must be valid. If they are not, then, they will not be updated.
            This will be fixed in the future, but for now, time is a factor.
        Args:
            merchant_name   : (str) Merchant name that will be set for configuration manager
            store_num       : (str) Store Number that will be set for configuration manager
            address_line    : (str) Address Line that will be set for configuration manager
            city            : (str) City that will be set for configuration manager
            state           : (str) State that will be set for configuration manager
            zip_code        : (str) ZIP Code that will be set for configuration manager
            phone_num       : (str) Phone Number that will be set for configuration manager
        Returns:
            dict: Dictionary that represents the status after settings the configuration manager fields.
        Examples:
        >>> set_configuration_manager(
                merchant_name="Joe's Store",
                store_num="4444",
                address_line="112 Tenbridge Ct.",
                city="Wake Forest",
                state="NC",
                zip_code="27587",
                phone_num="9192446403"
            )
        {
            'success': True, 
            'payload': {
                'address_line': '112 Tenbridge Ct.',
                'city': 'Wake Forest', 
                'merchant_name': "Joe's Store", 
                'phone_number': '9192446403', 
                'state': 'NC', 
                'store_number': '4444', 
                'zip_code': '27587'
            }
        }
        """
        data = {
            'merchant_name' : merchant_name,
            'store_number' : store_num,
            'address_line' : address_line,
            'city' : city,
            'state' : state,
            'zip_code' : zip_code,
            'phone_number' : phone_num
        }
        return self.post('/config_manager', data, dotnet_server=False)
    
    def get_card_data(self):
        """
        Sends a GET request to the Concord Network Sim and returns the card data.
        You can get the meanings of each card prompt code using the Web UI.
        Args:
            None
        Returns:
            dict: Dictionary that represents the status after getting the card data.
        Examples:
        >>> get_card_data()
        {
            'success': True, 
            'payload': {
                '001': 'Enabled', '011': 'Enabled', '012': 'Enabled', '013': 'Enabled', '020': 'Enabled', 
                '040': 'Enabled', '041': 'Enabled', '042': 'Disabled', '043': 'Enabled', '045': 'Enabled', 
                '046': 'Disabled', '050': 'Enabled', '051': 'Enabled', '054': 'Enabled', '055': 'Enabled', 
                '056': 'Enabled', '057': 'Enabled', '058': 'Enabled', '059': 'Enabled', '060': 'Enabled', 
                '064': 'Enabled', '070': 'Enabled', '071': 'Enabled', '072': 'Enabled', '073': 'Enabled', 
                '074': 'Enabled', '075': 'Enabled', '077': 'Enabled', '078': 'Enabled', '079': 'Enabled', 
                '080': 'Enabled', '081': 'Enabled', '083': 'Enabled', '084': 'Enabled', '085': 'Enabled', 
                '086': 'Enabled', '088': 'Disabled', '127': 'Enabled', '148': 'Enabled', '162': 'Enabled', 
                '163': 'Enabled', '164': 'Enabled', '165': 'Enabled', '166': 'Disabled', '167': 'Enabled', 
                '168': 'Enabled', '174': 'Enabled'
            }
        }
        >>> get_card_data()['payload']['001']
        "Enabled"
        >>> get_card_data()['payload']['088']
        "Disabled"
        """
        return self.get('/card_data')
    
    def set_card_data(self, card_prompt_code, enabled=True):
        """
        Sends a POST request that changes the card prompt code to be Enabled or Disabled.
        You can get the meanings of each card prompt code using the Web UI.
        Warning: Use the correct card_prompt_code; otherwise, it will not be updated.
        Args:
            card_prompt_code : (str) Card prompt code that you wish to enable or disable
            enabled : (bool) If True, card prompt code will be enabled; otherwise, if False, card prompt code will be disbaled.
        Returns:
            dict: Dictionary that represents the status after updating the card data.
        Examples:
        >>> set_card_data('166', True)
        {'success': True, 'payload': {'166': 'Enabled'}}
        >>> set_card_data('166', False)
        {'success': True, 'payload': {'166': 'Disabled'}}
        >>> set_card_data('166', False)['payload']['166']
        "Disabled"
        """
        data = {'card_prompt_code' : card_prompt_code, 'status' : enabled}
        return self.post('/card_data', data, dotnet_server=False)
    
    def restore_card_data(self):
        """
        Sends a POST request that restores all of the card prompt codes back to their original/default values.
        Args:
            None
        Returns:
            dict: Dictionary that tells user if simulator was able to restore card data back to its original value successfully or not.
        Examples:
        >>> restore_card_data()
        {
            'success' : True,
            'payload' : {
                'message' : 'Successfully restored the card data table to its default values'
            }
        }
        >>> restore_card_data()
        {
            'success' : False,
            'payload' : {
                'message' : 'Did NOT restore card data table. Issues with Database'
            }
        }
        """
        data = {'restore' : True}
        return self.post('/restore_card_data', data, dotnet_server=False)
    
    def get_settlement_indicator_flag(self):
        """
        Sends a GET request to the Concord Network Sim and returns the settlement indicator configured
        Args:
            None
        Returns:
            dict: Dictionary that represents settlement configuration flag set in the host sim
        Examples:
        >>> get_settlement_indicator_flag()
        {
            "description": "Empty",
            "enabled": true,
            "responseFlag": ""
        }
        
        """      
        return self.get('/commercial_settlement_indicator')
    
    def set_settlement_indicator_flag(self, flag, enabled):
        """
        Sends a POST request that changes the settlement indicator
        You can get the valid values in the Web UI.
        Warning: You need to set a flag the matches with the UI, otherwise,
            it won't be updated if both aren't correct
        Args:
            flag: (str) Flags available in the UI
            enabled : (bool) If True, other flags will be turned off and this
                will be turned on
        Returns:
            dict: Dictionary that represents the status after updating the settlement indicator.
        Examples:
        >>> set_settlement_indicator('CP - Cost Plus', True)
        {
            'success': True, 
            'payload': 
                {
                    "description": "Cost Plus",
                    "enabled": true,
                    "responseFlag": "CP"
                }
        }

        """
        data = {'flag' : flag, 'enabled' : enabled}
        return self.post('/commercial_settlement_indicator', data, dotnet_server=False)

    def get_commercial_product_limits(self):
        """
        Sends a GET request to the Concord Network Sim and returns the product limits
        Args:
            None
        Returns:
            dict: Dictionary that represents the product limits set in the host
        Examples:
        >>> get_commercial_product_limits()
        {
            'success': True, 
            'payload': {
                "productLimits": [
                    ["ADD", "Additives", 0.0, false],
                    ["ANFR", "Anti-freeze", 0.0, false ],
                    ["BRAK", "Brakes and wheels", 0.0, false],
                    ["CADV", "Company funds cash advance", 20.0, true],
                    ["CLTH", "Clothing",0.0,false],
                    ["DEF", "DEF Container", 0.0, false],
                    ["DELI", "Deli items", 0.0, false],
                    ["ELEC", "Electronics", 0.0,false],
                    ["ETAX","Exempt tax amount",0.0,false],
                    ["FAX","Fax",0.0,false],
                    ["FLAT","Flat Repair",0.0,false],
                    ["GROC","Groceries",0.0,false],
                    ["HARD","Hardware",0.0,false],
                    ["IDLE","Idleaire",0.0,false],
                    ["LMPR","Lumper Fee",0.0,false],
                    ["LUBE","Lube",0.0,false],
                    ["MERC","Default category for merchandise",30.0,true],
                    ["OIL","Oil",0.0,false]
                ]
            }
        }

        """
        return self.get('/commercial_product_limits')

    def set_commercial_product_limit(self, enabled, category, description, amount):
        """
        Sends a POST request that changes one product limit
        You can get the plausible values in the Web UI.
        Warning: Only amount and enabled can be modified but you need to set correctly
            Category and Description to get it updated
        Args:
            Category : (str) Product Category
            Description : (str) Product Description
            Amount: (float) Limit amount
            enabled : (bool) Limit enabled or disabled, if disabled, the amount is set in 0
        Returns:
            dict: Dictionary that represents the status after updating the limit.
        Examples:
        >>> set_commercial_product_limits(True, "ANFR", "Anti-freeze", 5.36)
        {
            'success': True, 
            'payload': 
                {
                    "enabled": true,
                    "productAmount": 25.65,
                    "productCategory": "TRAL",
                    "productDescription": "Trailer"
                }
        }

        """
        data = {
            'productCategory' : category,
            'productDescription' : description,
            'productAmount' : amount,
            'enabled': enabled
            }
        return self.post('/commercial_product_limits', data, dotnet_server=False)
        
    def get_commercial_prompts(self):
        """
        Sends a GET request to the Concord Network Sim and returns the commercial prompts
        Args:
            None
        Returns:
            dict: Dictionary that represents the commercial prompts set in the host
        Examples:
        >>> get_commercial_product_limits()
        {
            'success': True, 
            'payload': {
                "commercialPrompts": [
                    ["BLID","Billing ID","",false],
                    ["BDAY","Birthday information ","",true],
                    ["CNTN","Control number","",false],
                    ["NAME","Customer name","",false],
                    ["DTKT","Delivery ticket number","",false],
                    ["DRID","Driver ID","",false]
                ]
            }
        }

        """
        return self.get('/commercial_prompts')

    def set_commercial_prompt(self, enabled, token, description, prompt_Format):
        """
        Sends a POST request that changes one prompt
        You can get the plausible values in the Web UI.
        Warning: Only format and enabled can be modified but you need to set correctly
            token and Description to get it updated
        Args:
            token : (str) prompt token
            description : (str) prompt Description
            promptFormat: (str) mask format
            enabled : (bool) prompt enabled or disabled, if disabled, the mask is set in "" (empty)
        Returns:
            dict: Dictionary that represents the status after updating the prompt.
        Examples:
        >>> set_commercial_prompt(True, "DLST", "Driver Licence state", "")
        {
            'success': True, 
            'payload':
                {
                    "enabled": true,
                    "promptDescription": "Driver Licence state",
                    "promptFormat": "",
                    "promptToken": "DLST"
                } 
                
        
        }

        """
        data = {
            'promptToken' : token,
            'promptDescription' : description,
            'promptFormat' : prompt_Format,
            'enabled': enabled
            }
        return self.post('/commercial_prompts', data, dotnet_server=False)
    
    def get_commercial_fuel_limit_send_mode(self):
        """
        Sends a GET request to the Concord Network Sim and returns the commercial fuel limit
        send mode
        Args:
            None
        Returns:
            dict: Dictionary that represents commercial fuel limit send mode set in the host sim
        Examples:
        >>> get_commercial_fuel_limit_send_mode()
        {
            "fuelLimitsSendmode": "Host Simulator Based",
            "totalFuelLimit": 100,
            "enabled": "true"
        }
        
        """      
        return self.get('/commercial_fuel_limits_mode')
    
    def set_commercial_fuel_limit_send_mode(self, send_mode, fuel_limit, enabled):
        """
        Sends a POST request that changes the commercial fuel limit send mode
        You can get the plausible values in the Web UI.
        Warning: The valid values for send mode are:
             
        Args:
            send_mode : (str) fuel limit send mode:
                - fuel product configuration based
                - host simulator based 
            fuel_limit: (float) fuel limit amount
            enabled : (bool) If false, the fuel limit will be set to 0
        Returns:
            dict: Dictionary that represents the status after updating the send mode
        Examples:
        >>> set_commercial_fuel_limite_send_mode('Host Simulator Based', 100, True)
        {
            'success': True, 
            'payload': 
                {
                    "fuelLimitsSendmode": "Host Simulator Based",
                    "totalFuelLimit": 100,
                    "enabled": true
                }
        }

        """
        data = {'fuelLimitsSendMode' : send_mode, 'totalFuelLimit' : fuel_limit, 'enabled' : enabled}
        return self.post('/commercial_fuel_limits_mode', data, dotnet_server=False)
    
    def get_commercial_fuel_limits(self):
        """
        Sends a GET request to the Concord Network Sim and returns the commercial fuel limits
        Args:
            None
        Returns:
            dict: Dictionary that represents the commercial fuel limits set in the host
        Examples:
        >>> get_commercial_fuel_limits()
        {
            'success': True, 
            'payload': {
                "fuelLimits": [
                    [false,"001","Regular","REG",50.0],
                    [true, "002", "Plus", "PLS", 100.0],
                    [false, "003", "Supreme", "SUP", 50.0],
                    [false, "019", "Diesel 1", "DSL", 50.0],
                    [false, "020", "Diesel 2", "DS2", 50.0],
                    [false, "021", "Desl Blnd", "DSB", 50.0],
                    [false, "022", "CNG", "CNG", 50.0]
            }
        }

        """
        return self.get('/commercial_fuel_limits')
    
    def set_commercial_fuel_limit(self, allways_send, product_code, total_price):
        """
        Sends a POST request that changes one fuel limit
        You can get the plausible values in the Web UI.
        Warning: Only amount and enabled can be modified but you need to set correctly
            Category and Description to get it updated
        Args:
            allways_send : (bool) Always send enabled / disabled
            product code : (str) Product code used to identify the product to update
            total_price: (float) Limit amount            
        Returns:
            dict: Dictionary that represents the status after updating the limit.
        Examples:
        >>> set_commercial_fuel_limit(True, '002', 100)
        {
            'success': True, 
            'payload': 
                {
                    "TotalPrice": 100.0,
                    "abbreviation": "PLS",
                    "alwaysSend": true,
                    "productCode": "002",
                    "productDescription": "Plus"
                }
        }

        """
        data = {
            'alwaysSend' : allways_send,
            'productCode' : product_code,
            'totalPrice' : total_price            
            }
        return self.post('/commercial_fuel_limits', data, dotnet_server=False)
 
    def get_commercial_customer_information(self):
        """
        Sends a GET request to the Concord Network Sim and returns the commercial customer information
        Args:
            None
        Returns:
            dict: Dictionary that represents commercial customer information set in the host sim
        Examples:
        >>> get_commercial_customer_information()
        {
            'success': True, 
            'payload': 
                {
                    "WexCustomerAccCode": "123456",
                    "WexCustomerCity": "City1",
                    "WexCustomerName": "Name1",
                    "WexCustomerState": "NC"
                }
        }        
        """      
        return self.get('/customer_information')
    
    def set_commercial_customer_information(self, name, city, state, acc_code):
        """
        Sends a POST request that changes the commercial customer information
             
        Args:
            name : (str) Wex customer Name
            city : (str) Wex customer City
            state: (str) Wex customer state
            acc_code: (str) Wex customer acc_code
        Returns:
            dict: Dictionary that represents the status after updating the customer information
        Examples:
        >>> set_commercial_customer_information('Name1', 'City1', 'NC', '123456')
        {
            'success': True, 
            'payload': 
                {
                    "WexCustomerAccCode": "123456",
                    "WexCustomerCity": "City1",
                    "WexCustomerName": "Name1",
                    "WexCustomerState": "NC"
                }
        }

        """
        data = {'WexCustomerName' : name, 'WexCustomerCity' : city, 'WexCustomerState' : state, 'WexCustomerAccCode': acc_code}
        return self.post('/customer_information', data, dotnet_server=False)

    def disable_commercial_fuel_limits(self):
        """
        Sends a POST request disable all commercial fuel limits in the host sim
             
        Args:
            dict: Dictionary that represents all the product limits
        Examples:
        >>> disable_commercial_fuel_limits()
                {
            'success': True, 
            'payload': {
                "fuelLimits": [
                    [false,"001","Regular","REG",50.0],
                    [false, "002", "Plus", "PLS", 100.0],
                    [false, "003", "Supreme", "SUP", 50.0],
                    [false, "019", "Diesel 1", "DSL", 50.0],
                    [false, "020", "Diesel 2", "DS2", 50.0],
                    [false, "021", "Desl Blnd", "DSB", 50.0],
                    [false, "022", "CNG", "CNG", 50.0]
            }
        }

        """
        data = {}
        return self.post('/concord_commercial_Fuel_limits_disabled', data, dotnet_server=False)
    
    def disable_prompts(self):
        """
        Sends a POST request disable all commercial prompts in the host sim
             
        Args:
            dict: Dictionary that represents all the product limits
        Examples:
        >>> disable_prompts()
        {
            'success': True, 
            'payload': {
                "commercialPrompts": [
                    ["BLID","Billing ID","",false],
                    ["BDAY","Birthday information ","",false],
                    ["CNTN","Control number","",false],
                    ["NAME","Customer name","",false],
                    ["DTKT","Delivery ticket number","",false],
                    ["DRID","Driver ID","",false]
                ]
            }
        }
        """
        data = {}
        return self.post('/concord_commercial_prompts_disabled', data, dotnet_server=False)

    def disable_product_limits(self):
        """
        Sends a POST request disable all commercial product limits in the host sim
             
        Args:
            dict: Dictionary that represents all the product limits
        Examples:
        >>> disable_product_limits()
        {
            'success': True, 
            'payload': {
                "productLimits": [
                    ["ADD", "Additives", 0.0, false],
                    ["ANFR", "Anti-freeze", 0.0, false ],
                    ["BRAK", "Brakes and wheels", 0.0, false],
                    ["CADV", "Company funds cash advance", 20.0, false],
                    ["CLTH", "Clothing",0.0,false],
                    ["DEF", "DEF Container", 0.0, false],
                    ["DELI", "Deli items", 0.0, false],
                    ["ELEC", "Electronics", 0.0,false],
                    ["ETAX","Exempt tax amount",0.0,false],
                    ["FAX","Fax",0.0,false],
                    ["FLAT","Flat Repair",0.0,false],
                    ["GROC","Groceries",0.0,false],
                    ["HARD","Hardware",0.0,false],
                    ["IDLE","Idleaire",0.0,false],
                    ["LMPR","Lumper Fee",0.0,false],
                    ["LUBE","Lube",0.0,false],
                    ["MERC","Default category for merchandise",30.0,false],
                    ["OIL","Oil",0.0,false]
                ]
            }
        }

        """
        data = {}
        return self.post('/concord_commercial_prod_limits_disabled', data, dotnet_server=False)
    
    def get_commercial_fixed_approval_amount(self):
        """
        Sends a GET request to the Concord Network Sim and returns the 
        fixed approval amount set for commercial and if it is enabled
        Args:
            None
        Returns:
            dict: Dictionary that represents the approval amount and if
            it is enabled
        Examples:
        >>> get_commercial_fixed_approval_amount()
        {
            "fixedApprovalEnabled": true,
            "fixedApprovalField": 0
        }        
        """      
        return self.get('/concord_Commercial_Fixed_Approval_Amount')

    def set_commercial_fixed_approval_amount(self, amount, enabled=True):
        """
        Sends a POST request that changes the commercial fixed approval amount
             
        Args:
            enabled : (bool) enable / disable the usage if the amount
            amount : (float) The amount to approve            
        Returns:
            dict: Dictionary that represents the status after updating
            the fixed approval amount the customer information
        Examples:
        >>> set_commercial_fixed_approval_amount('10')
        {
            'success': True, 
            'payload': 
                {
                    "fixedApprovalEnabled": true,
                    "fixedApprovalField": 10.0
                }
        }

        """
        data = {'fixedApprovalField' : amount, 'fixedApprovalEnabled' : enabled}
        return self.post('/concord_Commercial_Fixed_Approval_Amount', data, dotnet_server=False)
    
class Dallas(NetworkSim):
    def __init__(self, endpoint, sim_obj='dallas'):
        """
        Inherits from Network Sim parent class.
        Args:
            endpoint : (str) The web-endpoint for the API.
            sim_obj : (str) The simulator's name.
        Examples:
        >>> Dallas(endpoint='http://10.4.18.118:5000/api/', sim_obj='dallas')
        """
        NetworkSim.__init__(self, endpoint, sim_obj)
    
    def get_download_configuration(self):
        """
        Sends a GET request to the Dallas Network Sim and returns the configuration manager fields.
        Args:
            None
        Returns:
            dict: Dictionary that represents the status after getting the configuration manager fields.
        Examples:
        >>> get_download_configuration()
        {
            'success': True, 
            'payload': {
                'unit_address': '123 Somewhere St', 
                'unit_city': 'Raleigh', 
                'unit_name': "Joe's Place", 
                'unit_state': 'NC'
            }
        }
        >>> get_download_configuration()['payload']['unit_name']
        "Joe's Place"
        """
        return self.get('/download_configuration')

    def set_download_configuration(self, unit_name, unit_address, unit_city, unit_state):
        """
        Sends a POST request to the Dallas Network Sim and updates the configuration manager fields.
        Warning: The parameters must be valid. If they are not, then, they will not be updated.
            This will be fixed in the future, but for now, time is a factor.
        Args:
            unit_name: (str) Unit Name
            unit_address: (str) Unit Address
            unit_city: (str) Unit City
            unit_state: (str) Unit State
        Examples:
        >>> set_download_configuration(
                unit_name='Dallas Site',
                unit_address='123 Somewhere St', 
                unit_city='Greensboro', 
                unit_state='NC'
            )
        {
            'success': True, 
            'payload': {
                'unit_address': '123 Somewhere St', 
                'unit_city': 'Greensboro', 
                'unit_name': 'Dallas Site', 
                'unit_state': 'NC'
            }
        }
        """
        data = {
            'unit_name' : unit_name,
            'unit_address' : unit_address,
            'unit_city' : unit_city,
            'unit_state' : unit_state,
        }
        return self.post('/download_configuration', data, dotnet_server=False)
    
    def get_mail(self):
        """
        Sends a GET request to the Dallas Network Sim and returns the mail text and if mail is enabled.
        Args:
            None
        Returns:
            dict: Dictionary containing success message and mail text and if its enabled.
        Examples:
        >>> get_mail()
        {
            'success': True, 
            'payload': {
                'mail_text' : None,
                'status' : False
            }
        }
        """
        return self.get(resource='/mail')
    
    def set_mail_text(self, mail_text):
        """
        Sends a POST request to the Dallas Network Sim and updates the mail text and enabled mail flag.
        Args:
            None
        Returns:
            dict: Dictionary containing success message and the mail text along with enabled flag that you just set.
        Examples:
        >>> set_mail_text(mail_text="You've got mail!")
        {
            'success': True, 
            'payload': {
                'mail_text' : "You've got mail!",
                'status' : True
            }
        }
        """
        payload = {
            'mail_text' : mail_text
        }
        return self.post(resource='/mail', data=payload, dotnet_server=False)

class Chicago(NetworkSim):
    def __init__(self, endpoint, sim_obj='chicago'):
        """
        Inherits from Network Sim parent class.
        Args:
            endpoint : (str) The web-endpoint for the API.
            sim_obj : (str) The simulator's name.
        Examples:
        >>> Chicago(endpoint='http://10.4.18.118:5000/api/', sim_obj='chicago')
        """
        NetworkSim.__init__(self, endpoint, sim_obj)
    
def _strip_currency(amount):
    if amount[0] == '$':
        return amount[1:]
    return amount

def init_networksim():
    """
    Creates and starts an instance of the network simulator and
    points to the brand you are currently on.
    """
    #TODO: Review these todo comments to make sure they actually say something needs  to be done. Here's a hint, they don't
    # TODO : IP is 1.2.3.4 in the JSON file
    # TODO : This will all be moved into a simulators package
    # TODO : We need to write the IP to some JSON file.

    network_file = constants.STANDARD_NETWORK
    primary_ip = server.server.get_site_info()['network']
    brand = system.get_brand().upper()
    networksim = None

    if brand == 'CONCORD' or brand == 'EXXON':
        with open(network_file, 'r') as fp:
            json_data = json.load(fp)
            json_data[brand]["Network Site Configuration"]["Network Connection Options"]["Host IP Address"] = primary_ip
        with open(network_file, 'w') as fp:
            fp.write(json.dumps(json_data, indent=4, separators=(',', ':')))
        networksim = Concord(endpoint=f"http://{primary_ip}:5000/api/")
        networksim.stop_simulator()
        networksim.start_simulator()

    elif brand == 'FASTSTOP' or brand == 'HPS-CHICAGO':
        with open(network_file, 'r') as fp:
            json_data = json.load(fp)
            json_data[brand]["Network Site Configuration"]["TCP/IP Configuration"]["Primary Host Address"] = primary_ip
            json_data[brand]["Network Site Configuration"]["TCP/IP Configuration"]["Secondary Host Address"] = primary_ip
            json_data[brand]["Network Site Configuration"]["TCP/IP Configuration"]["Tertiary Host Address"] = primary_ip
        with open(network_file, 'w') as fp:
            fp.write(json.dumps(json_data, indent=4, separators=(',', ':')))
        networksim = Chicago(endpoint=f"http://{primary_ip}:5000/api/")
        networksim.stop_simulator()
        networksim.start_simulator()

    elif brand == 'CITGO' or brand == 'HPS-DALLAS' or brand == 'MARATHON' or brand=="PHILLIPS66":
        with open(network_file, 'r') as fp:
            json_data = json.load(fp)
            json_data[brand]["Global Info Editor"]["Connection"]['Page 1']["Primary IP Address"] = primary_ip
            json_data[brand]["Global Info Editor"]["Connection"]['Page 1']["Secondary IP Address"] = primary_ip
            json_data[brand]["Global Info Editor"]["Connection"]['Page 1']["Tertiary IP Address"] = primary_ip
        with open(network_file, 'w') as fp:
            fp.write(json.dumps(json_data, indent=4, separators=(',', ':')))
        networksim = Dallas(endpoint=f"http://{primary_ip}:5000/api/")
        networksim.stop_simulator()
        networksim.start_simulator()

    elif brand == 'CHEVRON':
        cmd = f"update nw_hostconnectioninfo set vcHostIPAddress = '{primary_ip}', \
            iHostIPPrimaryPort = 18100, iHostIPSecondaryPort = 18100, iHostIPTertiaryPort = 18100, bUseSSLEncrypted = 0, \
            iHostOfflineAuthPrimaryPort = 18300, iHostOfflineAuthSecondaryPort = 18300, iHostOfflineAuthTertiaryPort = 18300"

        output = runas.run_sqlcmd(cmd, cmdshell=False)['output']
        output_list = output.split("\n")
        if output_list[1] != '(1 rows affected)':
            log.error(f"Not able to set ip : {primary_ip} in database")

    else:
        log.warning(f"{system.get_brand()} is not supported yet. Please, use the old {system.get_brand()} network simulator")
        return None

    if networksim is not None:
        try:
            if networksim.get_network_status()['payload']['status'] == 'Offline':
                start = networksim.start_simulator()
                log.info(f"Successfully, started {brand} network simulator")
        except:
            log.warning(f"Could not start {brand} network simulator")
        return networksim
    else:
        log.warning(f"Networksim not available for brand {brand}")

