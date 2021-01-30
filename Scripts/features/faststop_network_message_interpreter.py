"""
    File name: faststop_network_message_interpreter.py
    Tags:
    Description: This will have all methods for verification of DDLF and DDLD map for FastStop
    Author: Asha
    Date created: 2019-07-31 14:53:24
    Date last modified:
    Python Version: 3.7
"""

from app import runas
import logging, time
from app import pos
from app.framework import EDH
from app.framework.tc_helpers import test_func
from datetime import datetime

log = logging.getLogger()

class DatabaseException(Exception):
    def __init__(self, arg):
        try:
            self.log.info(arg)
        except:
            print(arg)
        self.message = arg

def fetch_networkmessage(cmd):
    """
    Executes sql cmd and returns output without any spaces
    Args: 
        cmd : (str) SQL query you wish to execute
    Return: 
        strNetworkMessage : String or None
    Example :
        fetch_networkmessage(cmd)  where cmd = "Select * from networkmessages"
    """
    output = runas.run_sqlcmd(cmd, cmdshell=False)['output']
        
    # Turning string into list of strings that have \n delimitation
    output_list = output.split("\n")
        
    str1 = output_list[2]

    #Remove Request number from message like Request[1234]
    str1 = str1.split("]")

    #removing leading and trailing spaces
    strNetworkMessage = str1[1].strip()


    if len(strNetworkMessage) == 0:
        raise DatabaseException("Not able to execute query")

    return strNetworkMessage

@test_func
def verify_faststop_Z01_StandardMap(strOutput, Transaction_Type, Response_Format_Code, Request_Format_Code):     
    """
    This will verify Z01 standard of network message
    Args :
        strOutput : (str) Output of sql query
        
        verify: (bool) Returns True if the function is successful, else a TC_fail will be called. Defaults to True
    Returns :
        bool : True if success, False if fail
    Example :
        verify_faststop_Z01_StandardMap(strOutput,'13','NO','PO')
        True
    """

    # verify that message is Z01 13
    message_type = strOutput[4:7]
    transaction_type = strOutput[12:14]
    if not message_type == 'Z01' and transaction_type == Transaction_Type:
        log.error(f"Transaction Type: {transaction_type} is not correct")
        return False

    #verify Response Format Code
    response_code = strOutput[8:10]
    if not response_code == Response_Format_Code:
        log.error(f"Response Format Code: {response_code} is not correct")
        return False

    #verify Request Format Code
    request_code = strOutput[10:12]
    if not request_code == Request_Format_Code:
        log.error(f"Request Format Code: {request_code} is not correct")
        return False

    log.info(f"Z01 {transaction_type} Standard Map is correct")
    return True

@test_func
def verify_ClientDictionaryData_Z01_DDL(strOutput, Format_Code, prod1_list,  prod2_list=[], prod3_list=[]):   #new
    """
    This will verify Client Dictionary Data of network message
    Args :
        strOutput : (str) Output of sql query
        cardType : {str) cardType generated during transaction
        prod1_list : (list) first product list which includes product code,fuel amount,fuel price, fuel quantity, pump number
        prod2_list : (list) Second product list which includes product code, quantity and amount
        prod3_list : (list) third product list which includes product code, quantity and amount
        verify: (bool) Returns True if the function is successful, else a TC_fail will be called. Defaults to True
    Return: 
        bool: True on success, False on failure.
    Example :
        verify_ClientDictionaryData_Z01_DDL(strOutput, "E", prod1_list)
        where prod1_list = ["004", "$5.00", "01000", "5000", "01"]
        where "004" is first fuel product code, "$5.00" is product amount, "01000" is fuel price
        "5000" is fuel quantity and "01" is pump number
    """

    indexBeforeEMVTag = strOutput.rfind("<0x1C>")
    strOutput = strOutput[:indexBeforeEMVTag]

    indexofFormat_Code = strOutput.rfind(Format_Code)
   
    strFormatCode = strOutput[indexofFormat_Code:indexofFormat_Code+1]
    if not strFormatCode == Format_Code:
        log.error(f"Format code: {strFormatCode} is not correct")
        return False
        
    strproduct_code1 = strOutput[indexofFormat_Code+1:indexofFormat_Code+4]
    if not strproduct_code1 == prod1_list[0]:
        log.error(f"Product code1: {strproduct_code1} is not correct")
        return False

    stramount = strOutput[indexofFormat_Code+4:indexofFormat_Code+11]
    if not verify_amount(stramount,prod1_list[1]):
        log.error(f"Fuel Amount: {stramount} is not correct")
        return False

    strFuelPrice = strOutput[indexofFormat_Code+11:indexofFormat_Code+16]
    if not strFuelPrice ==  prod1_list[2]:
        log.error(f"Fuel Price: {strFuelPrice} is not correct")
        return False

    strFuelQuantity = strOutput[indexofFormat_Code+16:indexofFormat_Code+23]
    if not int(strFuelQuantity) == int(prod1_list[3]):
        log.error(f"Fuel quantity: {strFuelQuantity} is not correct")
        return False

    strPump = strOutput[indexofFormat_Code+23:indexofFormat_Code+25]
    if not strPump == prod1_list[4]:
        log.error(f"Pump: {strPump} is not correct")
        return False

    # Check if product2 list is empty
    if bool(prod2_list):
        strproduct_code2 = strOutput[indexofFormat_Code+25:indexofFormat_Code+28]
        if not strproduct_code2 == prod2_list[0]:
            log.error(f"Product code2: {strproduct_code2} is not correct")
            return False

        strquantity2 = strOutput[indexofFormat_Code+28:indexofFormat_Code+35]
        if not int(strquantity2) == int(prod2_list[1]):
            log.error(f"Quantity2: {strquantity2} is not correct")
            return False

        strproduct_amount2 = strOutput[indexofFormat_Code+35:indexofFormat_Code+42]
        if not verify_amount(strproduct_amount2,prod2_list[2]):
            log.error(f"Amount2: {strproduct_amount2} is not correct")
            return False
    
    # Check if product3 list is empty
    if bool(prod3_list) :
        strproduct_code3 = strOutput[indexofFormat_Code+42:indexofFormat_Code+45]
        if not strproduct_code3 == prod3_list[0]:
            log.error(f"Product code3: {strproduct_code3} is not correct")
            return False

        strquantity3 = strOutput[indexofFormat_Code+45:indexofFormat_Code+52]
        if not int(strquantity3) == int(prod3_list[1]):
            log.error(f"Quantity3: {strquantity3} is not correct")
            return False

        strproduct_amount3 = strOutput[indexofFormat_Code+52:indexofFormat_Code+59]
        if not verify_amount(strproduct_amount3,prod3_list[2]):
            log.error(f"Amount3: {strproduct_amount3} is not correct")
            return False

    log.info(f"Client Dictionary Data DDL{Format_Code} is correct")
    return True

@test_func
def verify_faststop_clientDisctionaryData(strOutput,DDL):
    """
    This will verify Client Dictionary Data of network message
    Args :
        strOutput : (str) Output of sql query
        DDL : (str) Data dictionary value of sale
        verify: (bool) Returns True if the function is successful, else a TC_fail will be called. Defaults to True
    Return: 
        bool: True on success, False on failure.
    Example :
        verify_faststop_clientDisctionaryData(strOutput,"F01")
    """
    strDDL = strOutput[len(strOutput)-15:len(strOutput)-12]

    if not strDDL == DDL:
        log.error(f"DDL: {DDL} is not correct")
        return False

    log.info("Client Dictionary Data is correct")
    return True

@test_func
def verify_D0_ClientDictionaryData_DDLD(strOutput, cardType, prod1_list,  prod2_list=[], prod3_list=[]):
    """
    This will verify Client Dictionary Data of network message
    Args :
        strOutput : (str) Output of sql query
        cardType : {str) cardType generated during transaction
        prod1_list : (list) first product list which includes product code,fuel amount,fuel price, fuel quantity, pump number
        prod2_list : (list) Second product list which includes product code, quantity and amount
        prod3_list : (list) third product list which includes product code, quantity and amount
        verify: (bool) Returns True if the function is successful, else a TC_fail will be called. Defaults to True
    Return: 
        bool: True on success, False on failure.
    Example :
        verify_D0_ClientDictionaryData_DDLD(strOutput, "D", prod1_list)
        where prod1_list = ["004", "$5.00", "01000", "5000", "01"]
        where "004" is first fuel product code, "$5.00" is product amount, "01000" is fuel price
        "5000" is fuel quantity and "01" is pump number
    """
    strCardType = strOutput[122:123]
    if not strCardType == cardType:
        log.error(f"Card Type: {strCardType} is not correct")
        return False
        
    strproduct_code1 = strOutput[123:126]
    if not strproduct_code1 == prod1_list[0]:
        log.error(f"Product code1: {strproduct_code1} is not correct")
        return False

    stramount = strOutput[126:133]
    if not verify_amount(stramount,prod1_list[1]):
        log.error(f"Fuel Amount: {stramount} is not correct")
        return False

    strFuelPrice = strOutput[133:138]
    if not strFuelPrice ==  prod1_list[2]:
        log.error(f"Fuel Price: {strFuelPrice} is not correct")
        return False

    strFuelQuantity = strOutput[138:145]
    if not int(strFuelQuantity) == int(prod1_list[3]):
        log.error(f"Fuel quantity: {strFuelQuantity} is not correct")
        return False

    strPump = strOutput[145:147]
    if not strPump == prod1_list[4]:
        log.error(f"Pump: {strPump} is not correct")
        return False

    # Check if product2 list is empty
    if bool(prod2_list) :
        strproduct_code2 = strOutput[147:150]
        if not strproduct_code2 == prod2_list[0]:
            log.error(f"Product code2: {strproduct_code2} is not correct")
            return False

        strquantity2 = strOutput[150:157]
        if not int(strquantity2) == int(prod2_list[1]):
            log.error(f"Quantity2: {strquantity2} is not correct")
            return False

        strproduct_amount2 = strOutput[157:164]
        if not verify_amount(strproduct_amount2,prod2_list[2]):
            log.error(f"Amount2: {strproduct_amount2} is not correct")
            return False
    
    # Check if product3 list is empty
    if bool(prod3_list) :
        strproduct_code3 = strOutput[164:167]
        if not strproduct_code3 == prod3_list[0]:
            log.error(f"Product code3: {strproduct_code3} is not correct")
            return False

        strquantity3 = strOutput[167:174]
        if not int(strquantity3) == int(prod3_list[1]):
            log.error(f"Quantity3: {strquantity3} is not correct")
            return False

        strproduct_amount3 = strOutput[174:181]
        if not verify_amount(strproduct_amount3,prod3_list[2]):
            log.error(f"Amount3: {strproduct_amount3} is not correct")
            return False

    log.info("Client Dictionary Data is correct")
    return True

@test_func
def verify_D4_ClientDictionaryData_DDLD(strOutput, cardType, prod1_list,  prod2_list=[], prod3_list=[]):
    """
    This will verify Client Dictionary Data of network message
    Args :
        strOutput : (str) Output of sql query
        cardType : {str) cardType generated during transaction
        prod1_list : (list) first product list which includes product code,fuel amount,fuel price, fuel quantity, pump number
        prod2_list : (list) Second product list which includes product code, quantity and amount
        prod3_list : (list) third product list which includes product code, quantity and amount
        verify: (bool) Returns True if the function is successful, else a TC_fail will be called. Defaults to True
    Return: 
        bool: True on success, False on failure.
    Example :
        verify_D4_ClientDictionaryData_DDLD(strOutput, "D", prod1_list)
        where prod1_list = ["004", "$5.00", "01000", "5000", "01"]
        where "004" is first fuel product code, "$5.00" is product amount, "01000" is fuel price
        "5000" is fuel quantity and "01" is pump number   
    """
    strCardType = strOutput[185:186]
    if not strCardType == cardType:
        log.error(f"Card Type: {strCardType} is not correct")
        return False
        
    strproduct_code1 = strOutput[186:189]
    if not strproduct_code1 == prod1_list[0]:
        log.error(f"Product code: {strproduct_code1} is not correct")
        return False

    stramount = strOutput[189:196]
    if not verify_amount(stramount,prod1_list[1]):
        log.error(f"Fuel Amount: {stramount} is not correct")
        return False

    strFuelPrice = strOutput[196:201]
    if not strFuelPrice == prod1_list[2]:
        log.error(f"Fuel Price: {strFuelPrice} is not correct")
        return False

    strFuelQuantity = strOutput[201:208]
    if not int(strFuelQuantity) == int(prod1_list[3]):
        log.error(f"Fuel quantity: {strFuelQuantity} is not correct")
        return False

    strPump = strOutput[208:210]
    if not strPump == prod1_list[4]:
        log.error(f"Pump: {strPump} is not correct")
        return False
    
    # Check if product2 list is empty
    if bool(prod2_list):
        strproduct_code2 = strOutput[210:213]
        if not strproduct_code2 == prod2_list[0]:
            log.error(f"Product code2: {strproduct_code2} is not correct")
            return False

        strquantity2 = strOutput[213:220]
        if not int(strquantity2) == int(prod2_list[1]):
            log.error(f"Quantity2: {strquantity2} is not correct")
            return False

        strproduct_amount2 = strOutput[220:227]
        if not verify_amount(strproduct_amount2,prod2_list[2]):
            log.error(f"Amount2: {strproduct_amount2} is not correct")
            return False
    
    # Check if product3 list is empty
    if bool(prod3_list):
        strproduct_code3 = strOutput[227:230]
        if not strproduct_code3 == prod3_list[0]:
            log.error(f"Product code3: {strproduct_code3} is not correct")
            return False

        strquantity3 = strOutput[230:237]
        if not int(strquantity3) == int(prod3_list[1]):
            log.error(f"Quantity3: {strquantity3} is not correct")
            return False

        strproduct_amount3 = strOutput[237:244]
        if not verify_amount(strproduct_amount3,prod3_list[2]):
            log.error(f"Amount3: {strproduct_amount3} is not correct")
            return False

    log.info("Client Dictionary Data is correct")
    return True

@test_func
def verify_faststop_standardMap(strOutput):
    """
    This will verify standard map of network message
    Args :
        strOutput : (str) Output of sql query
        verify: (bool) Returns True if the function is successful, else a TC_fail will be called. Defaults to True
    Return: 
        bool: True on success, False on failure.
    """
    company_id = strOutput[:4]
    if not company_id == 'TESO':
        log.error(f"Company id: {company_id} is not correct")
        return False

    terminal_class_id = strOutput[4:5]
    if not terminal_class_id == 'Z':
        log.error(f"Terminal Class id: {terminal_class_id} is not correct")
        return False

    multiple_enquiry_flag = strOutput[7:8]
    if not multiple_enquiry_flag == 'M':
        log.error(f"Multiple enquiry flag: {multiple_enquiry_flag} is not correct")
        return False

    response_format_code = strOutput[8:10]
    if not response_format_code == 'N0':
        log.error(f"Response format code: {response_format_code} is not correct")
        return False

    request_format_code = strOutput[10:12]
    if not request_format_code == 'P7':
        log.error(f"Request format code: {request_format_code} is not correct")
        return False

    network_msg_date = strOutput[20:26]
    strNow = datetime.now()
    strdate = strNow.strftime("%m%d%y")
    if not network_msg_date == strdate:
        log.error(f"Network message date: {network_msg_date} is not correct")
        return False

    log.info("Standard map in network message is correct")
    return True

@test_func
def verify_faststop_Z01_13_p7Map(strOutput,total_amount,prod1_list, prod2_list=[],prod3_list=[], tax=None, discount=None):
    """
    This will verify Z01-13 of network message
    Args :
        strOutput : (str) Output of sql query
        total_amount : (str) total sale amount
        prod1_list : (list) first product list which includes product code and amount
        prod2_list : (list) Second product list which includes product code and amount
        prod3_list : (list) third product list which includes product code and amount
        tax : (str) tax applied in transaction
        discount : (str) Discount applied during transaction
        verify: (bool) Returns True if the function is successful, else a TC_fail will be called. Defaults to True
    Returns :
        bool : True if success, False if fail
    Example :
        verify_faststop_Z01_13_p7Map(strOutput,total_amount,prod1_list)
        where prod1_list = ["004","$10.00"] where "004" is first product code and "$10.00" is amount
    """
    # verify that message is Z01 13
    message_type = strOutput[4:7]
    transaction_type = strOutput[12:14]
    if not message_type == 'Z01' and transaction_type == '13':
        log.error(f"Transaction Type: {transaction_type} is not correct")
        return False
    
    #verify card type. It is always Credit for fast stop
    card_type = strOutput[90:91]
    if not card_type == 'C':
        log.error(f"Card Type: {card_type} is not correct")
        return False

    # Verify total amount of sale
    stramount = strOutput[91:98]
    if not verify_amount(stramount,total_amount):
        return False

    strodometerID = strOutput[99:105]
    if not int(strodometerID) == int(1234):
        log.error(f"Odometer ID: {strodometerID} is not correct")
        return False

    strdriverID = strOutput[105:111]
    if not int(strdriverID) == int(1234):
        log.error(f"Driver ID: {strdriverID} is not correct")
        return False

    strinvoice_total = strOutput[132:144]
    if not verify_amount(strinvoice_total,total_amount):
        return False

    strvehicleID = strOutput[144:150]
    if not int(strvehicleID) == int(1234):
        log.error(f"Vehicle ID: {strvehicleID} is not correct")
        return False

    strfuel_measure = strOutput[150:151]
    if not strfuel_measure == 'G':
        log.error(f"Fuel measure: {strfuel_measure} is not correct")
        return False

    # Take first element from product1 list which is product code
    strproduct_code1 = strOutput[153:156]
    if not strproduct_code1 == prod1_list[0]:
        log.error(f"Product code1: {strproduct_code1} is not correct")
        return False

    # Take second element from product1 list which is product amount
    strproduct_amount1 = strOutput[163:170]
    if not verify_amount(strproduct_amount1,prod1_list[1]):
        return False
    
    # Check is product2 list is empty
    if bool(prod2_list):
        strproduct_code2 = strOutput[170:173]
        if not strproduct_code2 == prod2_list[0]:
            log.error(f"Product code2: {strproduct_code2} is not correct")
            return False

        strproduct_amount2 = strOutput[180:187]
        if not verify_amount(strproduct_amount2,prod2_list[1]):
            return False

    # Check id prod3_list is empty
    if bool(prod3_list):
        strproduct_code3 = strOutput[187:190]
        if not strproduct_code3 == prod3_list[0]:
            log.error(f"Product code3: {strproduct_code3} is not correct")
            return False

        strproduct_amount3 = strOutput[197:204]
        if not verify_amount(strproduct_amount3,prod3_list[1]):
            return False
    
    if tax is not None:
        strtax = strOutput[221:226]
        if not int(strtax) == int(tax):
            log.error(f"Tax: {strtax} is not correct")
            return False

    if discount is not None:
        strdiscount = strOutput[226:231]
        if not int(strdiscount) == int(discount):
            log.error(f"Discount: {strdiscount} is not correct")
            return False

    log.info("Z01 13 P7 map is correct")
    return True

@test_func
def verify_faststop_Z01_05_p7Map(strOutput,total_amount,prod1_list,prod2_list=[],prod3_list=[], tax=None, discount=None):
    """
    This will verify Z01-05 P7 map of network message. This will come is Prepay sale
    Args :
        strOutput : (str) Output of sql query
        total_amount : (str) total sale amount
        prod1_list : (list) first product list which includes product code and amount
        prod2_list : (list) Second product list which includes product code and amount
        prod3_list : (list) third product list which includes product code and amount
        tax : (str) tax applied in transaction
        discount : (str) Discount applied during transaction
        verify: (bool) Returns True if the function is successful, else a TC_fail will be called. Defaults to True  
    Return: 
        bool: True on success, False on failure.    
    Example :
        verify_faststop_Z01_05_p7Map(strOutput,total_amount,prod1_list)
        where prod1_list = ["004","$10.00"] where "004" is first product code and "$10.00" is amount
    """
    #verify that message is Z01 05
    transaction_type = strOutput[12:14]
    message_type = strOutput[4:7]
    if not message_type == 'Z01' and transaction_type == '05':
        log.error(f"Transaction Type : {transaction_type} is not correct")
        return False
     
    #verify card type. It is always Credit for fast stop
    card_type = strOutput[90:91]
    if not card_type == 'C':
        log.error(f"Card Type : {card_type} is not correct")
        return False

    stramount = strOutput[91:98]
    if not verify_amount(stramount,total_amount):
        return False

    strodometerID = strOutput[99:105]
    if not int(strodometerID) == int(1234):
        log.error(f"Odometer ID : {strodometerID} is not correct")
        return False

    strdriverID = strOutput[105:111]
    if not int(strdriverID) == int(1234):
        log.error(f"Driver ID : {strdriverID} is not correct")
        return False

    strvehicleID = strOutput[132:138]
    if not int(strvehicleID) == int(1234):
        log.error(f"Vehicle ID : {strvehicleID} is not correct")
        return False

    strfuel_measure = strOutput[138:139]
    if not strfuel_measure == 'G':
        log.error(f"Fuel measure : {strfuel_measure} is not correct")
        return False

    strproduct_code1 = strOutput[141:144]
    if not strproduct_code1 == prod1_list[0]:
        log.error(f"Product code : {strproduct_code1} is not correct")
        return False

    strproduct_amount1 = strOutput[151:158]
    if not verify_amount(strproduct_amount1,prod1_list[1]):
        return False

    if bool(prod2_list):
        strproduct_code2 = strOutput[158:161]
        if not strproduct_code2 == prod2_list[0]:
            log.error(f"Product code: {strproduct_code2} is not correct")
            return False

        strproduct_amount2 = strOutput[168:175]
        if not verify_amount(strproduct_amount2,prod2_list[1]):
            return False

    if bool(prod3_list):
        strproduct_code3 = strOutput[175:178]
        if not strproduct_code3 == prod3_list[0]:
            log.error(f"Product code: {strproduct_code3} is not correct")
            return False

        strproduct_amount3 = strOutput[185:192]
        if not verify_amount(strproduct_amount3,prod3_list[1]):
            return False
    
    if tax is not None:
        strtax = strOutput[209:214]
        if not int(strtax) == int(tax):
            log.error(f"Tax: {strtax} is not correct")
            return False

    if discount is not None:
        strdiscount = strOutput[214:219]
        if not int(strdiscount) == int(discount):
            log.error(f"Discount: {strdiscount} is not correct")
            return False
            
    log.info("Z01 05 P7 map is correct")
    return True

@test_func
def verify_faststop_Z01_11_p7Map(strOutput,total):
    """
    This will verify Z01-11 p7 map of network message. This will come as response of postpay sale
    Args :
        strOutput : (str) Output of sql query
        total     : (str) Total amount..output of pos.read_balance()
        verify: (bool) Returns True if the function is successful, else a TC_fail will be called. Defaults to True
    Return: 
        bool: True on success, False on failure.
     Example :
        verify_faststop_Z01_11_p7Map(strOutput,total_amount)
    """
    #verify that message is Z01 11
    transaction_type = strOutput[12:14]
    message_type = strOutput[4:7]
    if not message_type == 'Z01' and transaction_type == '11':
        log.error(f"Transaction Type: {transaction_type} is not correct")
        return False
    
    stramount = strOutput[91:98]
    if not verify_amount(stramount,total):
        return False
    
    log.info("Z01 11 P7 map is correct")
    return True

@test_func
def verify_faststop_Z01_06_Map(strOutput):
    """
    This will verify Z01-06 map of network message
    Args :
        strOutput : (str) Output of sql query
        verify: (bool) Returns True if the function is successful, else a TC_fail will be called. Defaults to True
    Return: 
        bool: True on success, False on failure.
    """
    #verify that message is Z01 06
    transaction_type = strOutput[3:5]
    message_type = strOutput[:3]
    if not message_type == 'M00' and transaction_type == '06':
        log.error(f"Transaction Type: {transaction_type} is not correct")
        return False
    
    log.info("Z01 06 P7 map is correct")
    return True

@test_func
def verify_faststop_Z01_14_Map(strOutput):
    """
    This will verify Z01-14 map of network message
    Args :
        strOutput : (str) Output of sql query
        verify: (bool) Returns True if the function is successful, else a TC_fail will be called. Defaults to True
    Return: 
        bool: True on success, False on failure.
    """
    #verify that message is Z01 06
    transaction_type = strOutput[3:5]
    message_type = strOutput[:3]
    if not message_type == 'M00' and transaction_type == '14':
        log.error(f"Transaction Type: {transaction_type} is not correct")
        return False
    
    log.info("Z01 14 P7 map is correct")
    return True

def verify_amount(net_msg_amount,sale_amount):
    """
    Check if both amount are same or not
    Args : 
        net_msg_amount : (str) Amount populated in network message
        sale_amount : (str) Amount in sale transaction
    Return: 
        bool: True on success, False on failure.
    """
    
    # Remove $ from amount
    sale_amount = sale_amount.replace('$','')
    
    # Remove decimal (.) from amount 
    sale_amount = sale_amount.replace('.','')

    if not int(net_msg_amount) == int(sale_amount):
        log.error(f"Amount: {net_msg_amount} is not correct")
        return False
    
    return True

@test_func
def wait_for_network_message(last_id, request_map):
    """
    This is helper method to wait till required message comes in EDH
    Args :
        last_id: (str) message id of last network message
        request_map: (str) request map to be searched in network message
        verify: (bool) Returns True if the function is successful, else a TC_fail will be called. Defaults to True
    Return: 
        bool: True on success, False on failure.
    """
    log.info("Search for the network message")
    if not perform_comm_test():
        log.error("Comm test failed")

    edh = EDH.EDH()
    str1 = "Request ["+request_map

    start = time.time()
    while time.time() - start < 240:
        messages = edh.get_network_messages(amount="30", start_in=last_id)
        for message in messages:
            if str1 in message:
                log.debug(f"The network message was found")
                return True
        time.sleep(5)   
    else:
        return False

def perform_comm_test():
    """
    This is helper method which will perorm comm test so that network message will come in EDH
    """
    pos.click_function_key("NETWORK", timeout=3, verify=False)
    pos.click_function_key("host function", timeout=3, verify=False)

    start = time.time()
    
    while time.time() - start < 120:
        if "comm test" in pos.read_message_box().lower():
            pos.click_message_box_key("OK", verify=False, timeout=1)
            break
    else:
        return False
    return True