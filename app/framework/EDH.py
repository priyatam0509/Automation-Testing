"""
Name: EDH
Description: This module handles all the needs from the EDH

Date created: 04/29/2019
Modified By:
Date Modified:
"""


import json, logging

import requests

from app import runas
from app import system
from app.util import constants
from app.framework.tc_helpers import test_func
from requests.auth import HTTPBasicAuth

class EDH:

    # Log object
    log = logging.getLogger()

    # Installed Software

    brand = system.get_brand().upper()

    if brand == "CONCORD" or \
       brand == "SUNOCO" or \
       brand == "VALERO" or \
       brand == "EXXON" or \
       brand == "MOBIL":

        # At this point we do the same for all brands
        brand = "CONCORD"
        
    elif brand == "HPS-CHICAGO" or \
        brand == "FASTSTOP":
        brand = "CHICAGO"

    def __init__(self):

        """
        Reading JSON file with initialization info
        """

        try:
            
            with open(constants.BRAND_ID) as bIDs:
                brand_ids = json.load(bIDs)
                self.PSPId = brand_ids[self.brand.upper()]
        
        except KeyError as e:
        
            self.log.error(e)
            self.log.error("Failed to find the current Brand in the brandIDs file.")
        
            raise

        self.ntwrk_json = constants.STANDARD_NETWORK

        self.network_json = None

        try:
            with open(self.ntwrk_json, 'r') as f:
            
                self.network_json = json.load(f)
        
        except Exception as e:
            
            self.log.warning(e)

    @test_func
    def setup(self):
        """
        Sets up fake cash drawer and printer. Enables car wash.
        Args:
            None
        Return:
            bool: True if the result is a success. Otherwise, returns False
                    and logs the output of the command
        Example:
        """
        if not self.enable_carwash_controller():
            return False

        res = runas.run_sqlcmd(f'reg add HKEY_LOCAL_MACHINE\{constants.CRIND_SUBKEY}\Download /v SecurePromptAlternateContent /t REG_SZ /d True /f')
        if res['pid'] == -1:
            self.log.error("Registry edit failed. The response was: %s" % (res['output']))
            return False

        return True

    def enable_carwash_controller(self):
        self.log.debug("Attempting to enable the carwash controller simulator.")
        res = runas.run_sqlcmd(f'reg add HKEY_LOCAL_MACHINE\{constants.CARWASH_SUBKEY}\RykoServiceObject /v Simulator /t REG_DWORD /d 1 /f')
        if res['pid'] == -1:
            self.log.error("Registry edit failed. The response was: %s" % (res['output']))
            return False
        self.log.debug("Successfully enabled the carwash controller simulator.")
        return True

    def restart(self, timeout=120):
        """
        @Creator: Jesse Thomas / Kyle Schneiderman
        @Name: restart
        @Description: Performs EDH Restart
        @params:
            none
        @return:
            bool: False if something fails or True is the restart succeeded
        Examples:
            >>> edh.restart()
            'True'
        """
        ret = False
        if "Think it worked" in runas.run_as("C:\\Gilbarco\\Tools\\EPSDashboard.exe HIDE_GUI RESTART_EPS"):
            ret = True
        return ret

    def enable_security(self, stype="local"):
        """
        @Creator: Jesse Thomas / Kyle Schneiderman
        @Name: enable_security
        @Description: Hardens EDH for performaning credit and debit sales
        @params:
            stype: (string) Which kind of encryption method you would like. Defaults to local
        @return:
            bool: False if something fails or True is the update succeed
        Examples:
            >>> edh.enable_security()
            'True'
        """

        ret = False
        if stype.lower() == "local":
            # Do the thing
            if runas.run_sqlcmd("Update SMIStatus set OptionValue = '1' where OptionID = '0'", database="network", cmdshell=False):
                    ret = True
        else:
            # Do another thing
            if runas.run_sqlcmd("insert into EncryptionConfig (configid, value) values(6,1)", database="network", cmdshell=False):
                    ret = True

        return ret

    def get_network_messages(self, amount, pspid=None, start_in=0, order_by="desc" ):
        """
        Performs a query in the NetworkMessages table in the EDH based on the parameters provided

        Args:
            amount (str): the amount of messages that you want to get, this is a Select Top (amount) * from Networkmessages
            pspid (str): this is used to filter for the messages of the network that you are insterested in, by default it fileters by the primary network
            start_in (str): this is used to make your query more specific and get just the messages related with your transaction
            order_by (str): this is the orderby of the query

        Returns:
            List: List of messages returned by the EDH

        Examples:
            >>> edh.getNetworkmessages(10) will return a list of the last 10 messages in the table
            
        """       
        
        # Setting psp base on primary network
        if pspid is None:
            pspid = self.PSPId

        #convert the number to int just in case we get a string
        start_in = int(start_in)

        #we order by 1 desc to get the last messages and filter for PSPis to avoid Loyalty or another network logging in the middle
        query = f"select top ({amount}) * from networkmessages where NetworkPSPid = '{pspid}' and NetworkMessageId > {start_in} order by 1 {order_by}"
        output = runas.run_sqlcmd(query, database="network", cmdshell=False)['output']
        
        # Turning string into list of strings that have \n delimitation
        output_list = output.split("\n")

        if pspid == "23":

            output_list = self._clean_concord_messages(output_list)
        
        else:
            
            #TODO: Implement a clean for each network
            self.log.info("Pending to remove rows from the list that are not real messages")

        self.log.debug(f"The network messages obtined are: {output_list}")
        
        return output_list

    def _clean_concord_messages(self, messages):
        """
        Removes from the list the rows that do not contain messages

        Args:
            messages (str): list of messages obtined with getNetworkmessages 
        
        Returns:
        
            List: Rows that are real messages
        
        Examples:
            >>> edh._clean_concord_messages(ListOfMessages)
        """

        finalList = []

        for message in messages:

            # If the message does not contains "> [" there is nothing to parse there
            if "> [" in message:

                finalList.append(message.strip())
                
        return finalList
    
    def get_last_msg_id(self, pspid=None):
        """
        Get the last message for a PSP given, this is used to get only the messages involved in the transaction later
        
        Args:
            pspid (str): the id of the psp that we are interested in
        
        Returns:
            
            string: number to be used in get_network_messages function

        Examples:
            >>> edh.get_last_msg_id()
                '2354'
        """

        # Setting psp base on primary network
        if pspid is None:
            pspid = self.PSPId

        query = f"select top 1 NetworkMessageId from NetworkMessages where NetworkPSPid = '{pspid}' order by 1 desc"
        output = runas.run_sqlcmd(query, database="network", cmdshell=False)['output']
        
        # Turning string into list of strings that have \n delimitation
        output_list = output.split("\n")

        #the first 2 lines are not important
        return output_list[2].strip()

    def translate_message(self, message, timeout=30):
        """
        Sends the message to the the parser API to get it a readable way (JSON)
        
        Args:

            message (str): the message that we want to parse

        Returns:

            Dictionary: the message in a readable way

        Examples:

            >>> edh.translate_message(messages)
        """
        
        
        self.log.debug(f"{message} was sent to {constants.PARSER_API}")
            
        try:
            #Send the message to the API
            post_request = requests.post(
                    constants.PARSER_API,
                    data=message,
                    timeout=timeout
                )

            self.log.debug(f"{post_request.text} was returned from {constants.PARSER_API}")
       
        except requests.exceptions.ConnectionError as e:

            self.log.error(f"Failed attempting to do a get request to: {constants.PARSER_API}, please check it the parser is working")
            self.log.error(e)
            return False


        #Check if the API was able to parse the message
            
        if post_request.status_code == 200:

            return json.loads(post_request.text)

        else:

            self.log.error(f"Error was returned from {constants.PARSER_API} status code {post_request.status_code}")                
            return False
    
    @test_func
    def verify_field(self, message, verifications):
        """
        Verify that message obtined from the EDH contains the expected values on the specified fields
        
        Args:

            message (dictionary): The message in a JSON format
            verification (tuple): List of field: expected value

        Returns:

            Boolean: True if all the expected values match with the message provided

        Examples:

            >>> edh.verify_field(message, {NonFuel Amount': '10000'})
            >>> edh.verify_field(message, {'Prod 4 product Code': {'present': False, 'value': '032'}})
        """
        
        result = False
        
        for field_to_verify, expected_value in verifications.items():
            #Check expected_value is a dict, if so, that means that the validation is for a specific field is present or not in the network message
            if type(expected_value) is dict:
                if expected_value['present']:
                    #if should be present, expected_value take its value
                    expected_value = expected_value['value']
                else:
                    try:
                        #if should not be present, test case will fail if it is found
                        message[field_to_verify]
                        self.log.error(f'{field_to_verify} is in message and it is not expected.')
                        return False
                    except KeyError as e:
                        self.log.debug(f'{field_to_verify} is not in message and it is expected.')
                        return True

            try:
                if message[field_to_verify]['value'] == expected_value:

                    result = True

                else:
                    
                    current_value = message[field_to_verify]['value']
                    
                    self.log.error(f'{field_to_verify} is {current_value} instead of {expected_value}')   

                    return False

            except KeyError as e:

                self.log.error(f"Please check your validations, the key {field_to_verify} was not found")
                self.log.error(e) 
                # Making test fail if an expected field is not present
                return False 
    
        return result

    def initialize_Network(self):

        """
        @Creator: Ezequiel Juan
        @Name: initialize_Network
        @Description: Updates the EDH's database to configure network parameters that allow connectivity 
            with the host
        @params:
            >None            
        @return:
            >False if something fails or True is the update succeed
        """  

        if self.brand.upper() == "CONCORD" :

            self.initialize_Concord()
        
        elif self.brand.upper() == "WORLDPAY":

            self.initialize_RBS()

        # Kill network so changes take place
        
        output = self.kill_EDH_process()

        if "SUCCESS" not in output['output']:

                self.log.error("Kill Primary network process failes: %s" %(output['output']))

                return False

        else:

            self.log.debug('Primary network process correctly ended')

        return True

    def initialize_RBS(self):

        """
        @Creator: Ezequiel Juan
        @Name: initialize_RBS
        @Description: Updates the EDH's database to configure RBS connectivity
        @params:
            >None            
        @return:
            >False if something fails or True is the update succeed
        """     

        try:

            primaryIPAddress = self.network_json[self.brand]['TCP/IP Configuration']['Primary Host IP Address']
            primaryIPPort = self.network_json[self.brand]['TCP/IP Configuration']['Primary Host IP Port']
            secondaryIPAddress = self.network_json[self.brand]['TCP/IP Configuration']['Secondary Host IP Address']
            secondaryIPPort = self.network_json[self.brand]['TCP/IP Configuration']['Secondary Host IP Port']
            URLAndIPPort = self.network_json[self.brand]['TCP/IP Configuration']['URL and IP Port']
            enableSSL = self.network_json[self.brand]['TCP/IP Configuration']['Enable SSL']

        except Exception as e:
            
            self.log.error("Configuration values not found: %s" %(e))


        # Transalte enable SSL value

        if enableSSL == 'No':
            enableSSL = '2'
        elif enableSSL == 'Yes':
            enableSSL = '1'

        # Update connection parmeters
        output = runas.run_sqlcmd(  "update RBS_ConnectionInfo set "
                                    "PrimaryIPAddress = '%s', "
                                    "primaryIPPort = '%s', "
                                    "SecondaryIPAddress = '%s', "
                                    "SecondaryIPPort = '%s', "
                                    "URLAndIPPort = '%s', "
                                    "EnableSSL = %s" %(primaryIPAddress, primaryIPPort,
                                                    secondaryIPAddress, secondaryIPPort,
                                                    URLAndIPPort, enableSSL
                                    ), cmdshell=False
                                )

        if "1 rows affected" not in output['output']:
        
            self.log.error("Update connection parameters failed: %s" %(output['output']))
            
            return False
        
        else:

            self.log.debug('RBS_ConnectionInfo correctly updated')

        # Update Site Info

        TID = enableSSL = self.network_json[self.brand]['Site Configuration']['Page 1']['Terminal Id']

        output = runas.run_sqlcmd(  "update RBS_GlobalInfo set "
                                    "TID = '%s'" %(TID), cmdshell=False
                                )

        if "1 rows affected" not in output['output']:

            self.log.error("Update Site Info failed: %s" %(output['output']))

            return False

        else:

            self.log.debug('RBS_GlobalInfo correctly updated')

    def initialize_Concord(self):

        """
        @Creator: Ezequiel Juan
        @Name: initialize_Concord
        @Description: Updates the EDH's database to configure Concord connectivity
        @params:
            >None            
        @return:
            >False if something fails or True is the update succeed
        """     

        try:

            IPAddress = self.network_json[self.brand]['Network Site Configuration']['Network Connection Options']['Page 3']['Host IP Address']
            IPPort = self.network_json[self.brand]['Network Site Configuration']['Network Connection Options']['Page 3']['IP Port']

            # Site information is provided by de PDL so we do not need to initialize Site information

        except Exception as e:
            
            self.log.error("Configuration values not found: %s" %(e))
        
        # Update connection parmeters
        output = runas.run_sqlcmd(  "update ConnectionInfo set "
                                    "IPAddress = '%s', "
                                    "IPPort = '%s' " %(IPAddress, IPPort
                                    ), cmdshell=False
                                )

        if "2 rows affected" not in output['output']:
        
            self.log.error("Update connection parameters failed: %s" %(output['output']))
            
            return False
        
        else:

            self.log.debug('ConnectionInfo correctly updated')
        
    def kill_EDH_process(self, processName=brand):

        """
        @Creator: Ezequiel Juan
        @Name: kill_EDH_process
        @Description: Kill a process in the EDH, if not process is provided it 
            will kill the primary network process
        @params:
            >processName (string): The name of the process to kill
            
        @return:
            >output of taskkill
        """        
        # set the process to kill according the primary network
       
        if processName.lower() == "concord":

            processName = 'concordnetwork.exe'

        elif processName.lower() == "worldpay":
       
            processName = 'RBSNetwork.exe'

        # Will add support for other networks when initialization be included

        return runas.run_sqlcmd('taskkill /im %s /F' %(processName),domain="passporteps")
        


