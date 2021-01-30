from enum import Enum
import requests
from requests.auth import HTTPBasicAuth
import json
import logging
from app import constants

log = logging.getLogger(__name__)

# Status Codes
class Success(Enum):
    OK              = 200
    CREATED         = 201
    NO_CONTENT      = 204

class Redirection(Enum):
    NOT_MODIFIED    = 304

class ClientError(Enum):
    BAD_REQUEST     = 400
    UNAUTHORIZED    = 401
    FORBIDDEN       = 403
    NOT_FOUND       = 404
    CONFLICT        = 409

class ServerError(Enum):
    SERVER_ERROR    = 500

# Simulator Parent Class
class Simulator(object):

    def __init__(self, endpoint, sim_obj):
        self.endpoint = endpoint
        self.sim_obj = sim_obj.lower()
        self.full_url = self.endpoint + self.sim_obj
        self.session = requests.Session()
    
    def get(self, resource, timeout=30):
        full_url = self.full_url + resource
        try:
            log.debug(f"Sending GET request: {full_url}")
            get_request = self.session.get(full_url, timeout=timeout)
            if get_request.status_code == Success.OK.value:
                payload = {
                    "success" : True,
                    "payload" : json.loads(get_request.text)
                }
                return payload
            else:
                payload = {
                    "success" : False,
                    "payload" : "Error. Recieved status code of %s" %(get_request.status_code)
                }
                return payload
        except Exception as e:
            log.warning("Failed attempting to do a get request to: " + full_url)
            log.warning(e)
            payload = {
                "success" : False,
                "payload" : "Error" # TODO : Need to be more specefic.
            }
            return payload
    
    def post(self, resource, data, dotnet_server=True, timeout=30):
        full_url = self.full_url + resource
        log.debug(f"Sending POST request: {full_url} with data {data}")
        try:
            if dotnet_server:
                data = json.dumps(data) # DOTNET is expecting JSON str object
                post_request = self.session.post(
                    full_url,
                    data=json.dumps(data), # If I leave this as just `data`, it returns 500 status code.
                    headers={'content-type' : 'application/json'}, # If left out, this will throw a 415 status code.
                    timeout=timeout
                )
            else:
                post_request = self.session.post(
                    full_url,
                    data=data,
                    timeout=timeout
                )

            if post_request.status_code == Success.CREATED.value or\
                post_request.status_code == Success.OK.value:
                payload = {
                    "success" : True,
                    "payload" : json.loads(post_request.text)
                }
                log.debug(f"{payload} was returned from {self.full_url}")
                return payload
            else:
                payload = {
                    "success" : False,
                    "payload" : "Error. Recieved status code of %s" %(post_request.status_code)
                }
                log.debug(f"{payload} was returned from {self.full_url}")
                return payload

        except Exception as e:
            log.warning("Failed attempting to do a get request to: " + full_url)
            log.warning(e)
            payload = {
                "success" : False,
                "payload" : "Error" # TODO : Need to be more specefic.
            }
            return payload

    def _get_card_data(self, brand='Core', card_name='Visa'):
        """
        Returns a dictionary of the card data you passed in.
        Args:
            card_name : (str) The key/name of the card you wish to use.
        Returns:
            dict : Dictionary representing all of the key/value pairs of the card
        Example:
            >>> _get_card_data(
                brand='Core',
                card_name='Visa'
            )
            {
                'Track1': 'B4012002000028021^VISA^30121011909779700000',
                'Track2': '4012002000028021=30121011909779700000',
                'PaymentType': 'Credit'
            }
            >>> _get_card_data(
                brand='Concord',
                card_name='SomeCardThatIsInvalid'
            )
            {}
        """
        brand = brand.upper()
        try:
            with open(constants.CARD_DATA, 'r') as fp:
                card_data_file = json.load(fp)
                try:
                    ret_val = card_data_file[brand][card_name]
                    return ret_val
                except:
                    log.warning(f"Unable to find {card_name} within {brand} brand.")
                    return {}
        except Exception as e:
            log.warning(e)
            return {}