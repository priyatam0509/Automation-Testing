"""
    File name: FromInsite360.py
    Tags:
    StoryID: Common functions for Insite from/to Passport management
    Description: Employee Management from IS360, Tax management from Insite360 & Common utilities
    Author: Pavan Kumar Kantheti
    Date created: 2020-01-24 10:20:30
    Date last modified: 2020-04-29 20:20:20
    Python Version: 3.7
"""
from datetime import datetime
from app import mws, system, runas
from app.features import insite360
from app.util import constants
import time
import logging
import os
import json
import shutil
import pyodbc
import sys
import winreg as reg


log = logging.getLogger()
fromServiceDt =  datetime.now()
logFileFromService = None
reg_key = None


def OpenRegister(subkey):
    """
    Open the register key value for HKEY_LOCAL_MACHINE based on the subkey
    Args: subkey (string)
    Returns: None
    """
    global reg_key
    reg_key = reg.OpenKey(reg.HKEY_LOCAL_MACHINE, subkey, 0, reg.KEY_ALL_ACCESS)


def SetRegisterValue(name, value):
    """
    Add or update the registry key values based on the arguments
    Args: name (string) - key string name
          value (string) - key string value
    Returns: None
    """
    global reg_key
    reg.SetValueEx(reg_key, name, 0, reg.REG_SZ, value)


def GetRegisterValue(index):
    """
    Get the register key value based on the index.
    Args: index (integer) - index  value of the reg_key
    Returns: Value of the reg_key index key (string) value
    """
    global reg_key
    return reg.EnumValue(reg_key, index)[1]


def IsRegisteryExists(keyName):
    """
    Check either the keyName exists in the register key values or not
    Args: keyName (string) - register key name to check
    Returns: result (integer) [If exists retuen value is >=0, if not returns -1]
    """
    global reg_key
    noOfStr = reg.QueryInfoKey(reg_key)[1]
    keyFound = False
    if (noOfStr > 0):
        while (noOfStr > 0):
            if (reg.EnumValue(reg_key, noOfStr - 1)[0] == keyName):
                log.info(f"Key [{keyName}] found at position [{noOfStr - 1}]")
                keyFound = True
                break
            else:
                noOfStr = noOfStr - 1
    if (keyFound):
        result = noOfStr - 1
    else:
        result = - 1

    return result


def DeleteRegisterKey(keyName):
    """
    Delete the key (string) from the register
    Args:   keyName (string)
    Returns:None
    """
    global reg_key
    reg.DeleteValue(reg_key, keyName)


def TaxMainRegisterCheck():
    """
    """
    subkey = constants.RES_SUBKEY
    name = "TaxConfigI360"
    OpenRegister(subkey)
    index = IsRegisteryExists(name)
    return index


def insite360_configure():
    """Tests whether the Insite 360 Interface can be configured correctly.
    Args: None
    Returns: status (bool) - True/False
    """
    is360 = insite360.Insite360Interface()
    fieldValue = mws.get_value("Enable Insite360", "General")
    status = True
    if (not fieldValue):
        insite_info = {
            "General": {
                "Enable Insite360": True,
                "Export price book when third party changes are made to items or departments": True,
                "Gilbarco ID": "858194",
                "Apply only to this register group": True,
                "Apply to only this register group combo box": "POSGroup1"
            }
        }
        status = is360.configure(insite_info)
    return status


def Register_UnRegister_Insite360(insite360Status):
    """
    Register/ Un-Register the "Insite360 Interface"
    Args: insite360Status (bool)
    Returns: status (bool) - True/False
    """
    is360 = insite360.Insite360Interface()
    time.sleep(2)
    status = True
    if (insite360Status):
        # un-register the insite360
        try:
            if not is360.unRegister():
                status = False
                log.error(f"Restarting the Passport to check insite360 status....")
                system.restartpp()
                time.sleep(5)
        except:
            log.error(f"An exception occured while unRegister insite360 - [{sys.exc_info()[0]}]")
            system.restartpp()
    else:
        # Before regidter the insite360 update the registry key to register for sand box
        subkey = constants.REMOTEMNGR_SUBKEY
        OpenRegister(subkey)
        SetRegisterValue('HTTPUrl', "https://registration.sandbox.gilbarco.com")
        SetRegisterValue('CertThumbprint', "31A42C96F5CDB6D680E3EF8BC5E6D947C6BDBD9C")
        try:
            # register the insite360
            if not is360.register(180):
                status = False
        except:
            log.error(f"An exception occured while register insite360 - [{sys.exc_info()[0]}]")
            system.restartpp()

    return status


def StopService(serviceName):
    """
    Kill the service from task list
    Args: serviceName (string)
    Return: None
    """
    cmd = r"taskkill /IM " + serviceName + " /f"
    pid = runas.run_as(cmd)
    log.warning(f"StopService [{serviceName}] :: [{pid}]")


def StartService(serviceName):
    """
    Start the windows service and gives the result
    Args: serviceName (string)
    Return: status (int) 0 - Success, other than 0 - Fail
    """
    cmd = r"net start " + serviceName
    log.warning(f"StartService [{serviceName}] :: [{cmd}]")
    status = os.system(cmd)
    return status


def RestartService():
    """
    Restart Start the windows service "" and gives the result
    Args: None
    Return: serviceStatus (bool) True/ False
    """
    serviceName = "RemoteManagerService.exe"
    serviceStatus = True

    try:
        StopService(serviceName)
        serviceName = "RemoteManagerSvc"
        time.sleep(5)
        status = StartService(serviceName)
        if (status != 0):
            serviceStatus = False
    except:
        log.error(f"An exception occured, unable to Restart the service [{serviceName}]")
        serviceStatus = False
    return serviceStatus


def RestartServiceAndValidate():
    """
    Restart the windows service "" and gives the maximum wait timeOutInMin
    Args: None
    Return: timeOutInMin (int) 2 or 1 (inMinutes)
    """
    timeOutInMin = 1
    serviceStatus = RestartService()
    if (serviceStatus):
        timeOutInMin = 2
    else:
        log.error("RemoteManagerSvc - is not properly restarted.")
    return timeOutInMin


def Check_I360_Connected():
    """
    Check the insite 360 interface is registered at the site or not
    Args: None
    Return: connected (bool) True/False
    """
    connected = False
    queryString = "SELECT COUNT(0) FROM CS_RM_SITE_INFO"
    fromDB = ExecuteScalarFromDB(queryString)

    if (not fromDB == 0):
        connected = True
    else:
        connected = False

    log.info(f"Check_I360_Connected Status from DB = [{connected}]")
    return connected


def FileCheck(path, fileName):
    """
    Check the fileName in the system exists or not in
    specified path and fileName.
    Args: path, fileName
    Returns: True/False based on the file exists
    """
    fileName = path + fileName
    fileStatus = os.path.exists(fileName)
    return fileStatus


def DeleteFileName(path, fileName):
    """
    Delete the fileName from specified path
    Args: path, fileName
    Returns: String value status with description
    """
    # Check whether the specified
    # path exists or not
    isExist = os.path.exists(path)
    if (isExist):
        try:
            fileName = path + fileName
            if (os.path.exists(fileName)):
                os.remove(fileName)
                return("Success")
            else:
                return("Success")
        except OSError:
            return (f"Error while deleting [{fileName}]")
    else:
        return (f"Folder [{path}] is not exist.")


def Date_Diff(start, current):
    """
    Calculate the time difference between two date time
    Args: start , current - both type is datetime
          diffIn - difference in specifies "seconds/minutes/hours/days/month/year"
    Returns: timedelta (differnce in based on the diffIn parameter)
    """
    timedelta = current - start
    return timedelta.seconds


def JSONGenerateTimeOutStatus(eventName, checkTimeAuto, timeOutInMin, timeIntervalInSec, fileCopied, onlyGenerateStatus=False, jsonDataCheck=False, noTaxCheck=False):
    """
    Check the json object generate or not at maximum interval check(timeOutInMin)
    From Remote Manager service
    Args: eventName, checkTimeAuto, timeOutInMin, timeIntervalInSec, fileCopied, onlyGenerateStatus, jsonDataCheck, noTaxCheck
    Returns: True/False (timeOut check for file generate status)
    """
    log.info(f"Waiting[Max {timeOutInMin} Min] for [{eventName}] json generated or not")
    fileFound = False
    timeOut = False
    waitMaxLimit = timeOutInMin * 60

    if (fileCopied):
        fileFound = Check_Event_Send_I360(eventName, checkTimeAuto, timeOutInMin, fileCopied, onlyGenerateStatus, jsonDataCheck, noTaxCheck)
        timeOut = not fileFound
    else:
        while not fileFound:
            fileFound = Check_Event_Send_I360(eventName, checkTimeAuto, timeOutInMin, fileCopied, onlyGenerateStatus, jsonDataCheck, noTaxCheck)
            if (not fileFound):
                log.info(f"[{eventName}].json is not generated... waiting for [{timeIntervalInSec}] Seconds...")
                time.sleep(timeIntervalInSec)
                waitTime = datetime.now()
                datediff = Date_Diff(checkTimeAuto, waitTime)
                if (datediff >= waitMaxLimit):
                    log.info(f"TIME OUT [{timeOutInMin}], .json [{eventName}] is not generated...")
                    timeOut = True
                    fileFound = True

    return (timeOut)


def Get_MessageID(lineString, isCommand=False):
    """
    Get the messageID generated from remote manager through log file
    Args:   lineString (string value)
            isCommand (boolean) - default False, for commands it is True
    Returns:MessageID (string value)
    """
    startIndex = lineString.find('"messageId":"')
    mesgIndex = len('"messageId":"')
    if (isCommand):
        endIndex = lineString.find('","deviceId":')
    else:
        endIndex = lineString.find('","operation":')
    messageID = lineString[startIndex + mesgIndex: endIndex]
    return messageID


def Get_OperatorID(lineString):
    """
    Fetch the operator ID from log ine
    Args:   lineString (string) - log line to find the operator ID
    Returns:operatorID (string)
    """
    startIndex = lineString.find('"operatorId":"')
    mesgIndex = len('"operatorId":"')
    endIndex = lineString.find('","status":')
    operatorID = lineString[startIndex + mesgIndex: endIndex]
    return operatorID


def CopyFile(source, destination, fileName):
    """
    copy the RMS_[yyyyMMdd].log file from d:/gilbarco/logs
    and place it in D:/Automation/output/RMS_[yyyyMMdd].log
    """
    filestatus = FileCheck(source, fileName)
    fcStatus = ""
    if (filestatus):
        # file is exists from source path
        filestatus = FileCheck(destination, fileName)

        # if file is exists in destination folder remove it
        if (filestatus):
            DeleteFileName(destination, fileName)

        # copy the file from the source
        fcStatus = shutil.copy(source + fileName, destination + fileName)
        fcStatus = "Success"
    else:
        fcStatus = "Source file [{ source + fileName }] is not found"

    return fcStatus


def Check_Event_Send_I360(eventName, checkTimeAuto, timeOutInMin, fileCopied, onlyGenerateStatus, jsonDataCheck, noTaxCheck):
    """
    Based on the filecopied argument the file would be copied to automation drive and start process
    Args:
        eventName (str) : employees/ securitygroups/ taxrates
        checkTimeAuto (datetime) : Start date Time from automation script
        timeOutInMin (int) : time out in minutes , maximum wait time
        fileCopied (bool) : True/False
        onlyGenerateStatus (bool) : True/False
        jsonDataCheck (bool) : True/False
        noTaxCheck (bool) : True/False
    Returns: True/ False
    """
    now = datetime.now().strftime("%Y%m%d")
    fileName = "RMS_" + now + ".log"
    source = "d:/gilbarco/logs/"
    destination = "d:/Automation/output/"

    result = False

    if (fileCopied):
        fileCopyStatus = "Success"
    else:
        fileCopyStatus = CopyFile(source, destination, fileName)

    if (fileCopyStatus == "Success"):
        fileName = destination + fileName
        # result = True
        result = CheckEvent(fileName, eventName, checkTimeAuto, timeOutInMin, onlyGenerateStatus, jsonDataCheck, noTaxCheck)
    else:
        log.info(f"File [{ source + fileName }] is not found... skip this time to process")
    return (result)


def CheckEvent(file_name, eventName, fromAutomation, timeOutInMin, onlyGenerateStatus, jsonDataCheck, noTaxCheck):
    """
    Process the RMS.log file based on the eventName and check either the event send to insite is
    successful or not
    Args:
        file_name (str) : RMS_dateformat.log
        eventName (str) : employees/ securitygroups/ taxrates
        fromAutomation (datetime) : Start date Time from automation script
        timeOutInMin (int) : time out in minutes , maximum wait time
        onlyGenerateStatus (bool) : True/False
        jsonDataCheck (bool) : True/False
        noTaxCheck (bool) : True/False
    Returns: True/ False
    """
    line_number = 0
    file_lines = 0
    recordFound = False
    returnValue = False
    list_of_results = []
    list_of_LineNumbers = []

    string_to_search = 'Sending data over websocket connection [{"payload":{"' + eventName + '":'

    # Open the file in read only mode
    with open(file_name, 'r') as read_obj:
        # Read all lines in the file one by one
        for line in read_obj:
            # For each line, check if line contains the string
            line_number += 1
            if string_to_search in line:
                # If yes, then add the line number & line as a tuple in the list
                list_of_results.append(line)
                list_of_LineNumbers.append(line_number)
                recordFound = True

    if (recordFound):
        file_lines = line_number - 1
        i = 0
        while i < len(list_of_LineNumbers):
            line_number = list_of_LineNumbers[i]
            i = i + 1

        # get the date time from line and check with date time
        # 4 - starting position of the datetime and 27 is end position of datetime in file
        resultString = list_of_results[i - 1]
        fromFiledate = resultString[4: 27]
        fromService = datetime.strptime(fromFiledate, "%m/%d/%Y %H:%M:%S.%f")
        log.info(f"Latest {eventName} send @ [{fromFiledate}] :: Check Start time [{fromAutomation}]")
        # Service time should be greater than Max 15 minutes, other wise
        # Read from the common method
        timegap = Date_Diff(fromAutomation, fromService)
        timeOutInSec = timeOutInMin * 60
        if (timegap <= timeOutInSec):
            log.info(f"Check between the lines [{ str(line_number) } : {str(file_lines)} ] in the file.")
            msgID = Get_MessageID(resultString)
            log.info(f"For [{eventName}] : Message ID =[{msgID}]")

            if (jsonDataCheck):
                dataMatch = CheckJSONdataByEvent(eventName, resultString)
                if (not dataMatch):
                    log.info(f"[{eventName}] json data from db is not match. Invalid json data")
                    return (dataMatch)
                else:
                    # For tax rates need to check "no Tax" will be part of resultString or not
                    if (noTaxCheck):
                        taxcheck = resultString.lower().find("no tax")
                        if not(taxcheck > 0):
                            log.info(f"{eventName} does not having 'No Tax' details")
                        else:
                            log.info(f"{eventName} having 'No Tax' details")
                            return (False)

            if (onlyGenerateStatus):
                returnValue = True
                log.info(f"{eventName} JSON object generated: Success")
            else:
                with open(file_name, 'r') as fp:
                    for line_no, line in enumerate(fp):
                        if line_no >= line_number and line_no <= file_lines:
                            status = line.find('Message Received over websocket') and line.find(msgID)
                            if (status > 0):
                                log.info(f"LineNo:[{line_no}] - Message Received over websocket {eventName}")
                                startStatus = line.find('"success":')
                                successLen = len('"success":')
                                endStatus = line.find(',"messageId":')
                                log.info(f"line = [{line}]")
                                if (line[startStatus + successLen: endStatus] == 'true'):
                                    returnValue = True
                                    log.info(f"{eventName} Received Status: Success")
                                else:
                                    log.info(f"{eventName} Received Status: UnSuccess. Please see the logs")
                                break
        else:
            log.info("No configuration data genereated")
    else:
        log.info('No Record Found....')

    return (returnValue)


def ExecuteScalarFromDB(queryString, conServer="POSSERVER01", dbName="GlobalSTORE"):
    """
    Executes the queryString, and returns the first column of the first row
    in the result set returned by the query. Additional columns or rows are ignored.
    Args: queryString - query to execute in the database
          conServer - connection server name
          dbName - database Name
    Returns: The first column of the first row in the result set.
    """
    connstr = 'Driver={SQL Server};Server=' + conServer + ';Database='+ dbName +';Trusted_Connection=yes;'

    result = ""
    try:
        # connection through the connection string
        conn = pyodbc.connect(connstr)
        cursor = conn.cursor()
        # executes the query
        cursor.execute(queryString)
        rows = cursor.fetchall()

        for row in rows:
            result = row[0]
            break

        conn.close()

    except pyodbc.Error as ex:
        sqlstate = ex.args[1]
        log.Error(sqlstate)

    return result


def CheckJSONdataByEvent(eventName, contentLine):
    """
    Sql command for the event name to check at the database based on the event
    Args: eventName - employees/securitygroups / taxrates
          contentLine - log line from RMS_datetimeformat.log for the event
    Return: recordMatch (True/False)
    """
    log.info(f"Check the [{eventName}] JSON object generated from service and database")
    queryString = ""
    if (eventName == "employees"):
        queryString = """SELECT 
        E.EMP_ID AS OperatorId, 
        E.LST_NM AS LastName, E.FRST_NM AS FirstName, 
        CONVERT(BIT, CASE WHEN ISNULL(E.TERM_DT, '')='' THEN 'true' ELSE 'false' END) AS Active,
        REPLACE(CONVERT(VARCHAR(32), E.TERM_DT, 20),' ','T')+'Z' AS TerminationDate,
        CONVERT(VARCHAR(10), E.LANG_CD) AS LanguageCode, 
        REPLACE(CONVERT(VARCHAR(32), E.BIRTH_DT, 20),' ','T')+'Z' AS BirthDate, 
        CONVERT(VARCHAR(10), E.HAND_PREF) AS HandPreference, 
        CONVERT(VARCHAR(10), E.KEYPAD_TYPE) AS KeypadPreference, 
        CONVERT(BIT,CS_OVERRIDE_OPT_FG) AS OverrideBlindBalanceOption, 
        CONVERT(VARCHAR(10), E.CS_BLIND_BAL_FG) AS ViewTotalOnBlindBalance, 
        E.CLOCK_IN_OUT_REQ AS ClockInOutRequired, 
        CONVERT(VARCHAR(10), E.CS_THEME) AS Theme, 
        CONVERT(VARCHAR(10), PG.SECURITY_LEVEL) AS SecurityLevelId, 
        ISNULL(EA.LN_1, '') AS AddressLine1, ISNULL(EA.LN_2, '') AS AddressLine2, 
        ISNULL(EA.LN_3, '') AS AddressLine3, 
        ISNULL(EA.CTY, '') AS City, ISNULL(EA.ST, '') AS State, 
        ISNULL(EA.PST_CD, '') AS PostalCode, 
        ISNULL(ET.AREA_CD, '') AS AreaCode, ISNULL(ET.PHN_NBR, '') AS PhoneNumber 
        FROM EMPLOYEE AS E 
        INNER JOIN 
        EMPLOYEE_GROUP AS EG ON E.EMP_ID = EG.EMP_ID 
        INNER JOIN 
        PERMISSION_GROUP AS PG ON EG.GRP_ID = PG.GRP_ID 
        LEFT JOIN 
        ADDRESS AS EA ON E.EMP_ID = EA.ADDR_ID AND EA.USAGE_CD = 1 
        LEFT JOIN 
        TELEPHONE AS ET ON E.EMP_ID = ET.PHN_ID AND ET.USAGE_CD = 1 
        WHERE PG.SECURITY_LEVEL <= 90 
        FOR JSON PATH, ROOT('employees')"""
    elif (eventName == "securitygroups"):
        queryString = """SELECT 
        CONVERT(VARCHAR(10), GRP_ID) AS GroupId, GRP_DESCR AS GroupDescription, CONVERT(VARCHAR(10), SECURITY_LEVEL) AS SecurityLevel 
        FROM PERMISSION_GROUP AS PG WHERE PG.SECURITY_LEVEL <= 90 
        FOR JSON PATH, ROOT('securitygroups')"""
    elif (eventName == "taxRates"):
        queryString = """SELECT 
        CONVERT(varchar(20), TA.TAX_CD) AS TaxLevelID, CTTD.TEXT_DESCRIPTION AS TaxDescription, 
        CTTRD.TEXT_DESCRIPTION AS TaxReceiptDescription, 
        CONVERT(DECIMAL(7,1), CASE WHEN ISNULL(TA.TAX_TBL, 0) = 0 THEN TA.TAX_RATE * 100 ELSE 0 END) AS TaxRate, 
        CONVERT(DECIMAL(10,2), ISNULL(TA.MIN_TAXABLE_AMT, 0)) AS TaxMinAmount, 
        CAST(CASE WHEN ISNULL(TA.TAX_TBL, 0) = 0 THEN 0 ELSE 1 END AS BIT) AS IsTaxTable 
        FROM TAX_AUTHORITY AS TA 
        INNER JOIN CS_TEXT AS CTTD ON TA.CS_TXT_ID = CTTD.CS_TXT_ID AND CTTD.LANG_CD = 1 
        INNER JOIN CS_TEXT AS CTTRD ON TA.CS_POS_TXT_ID = CTTRD.CS_TXT_ID AND CTTRD.LANG_CD = 1 
        WHERE TA.TAX_CD NOT IN ('99', '100') 
        FOR JSON PATH, ROOT('taxRates')"""

    fromDB = ExecuteScalarFromDB(queryString)
    log.debug(f"queryString = [{queryString}]")
    log.info(f"[{eventName}] json data from db : {fromDB.lower()}")
    
    recordMatch = ValidateStringFromDB(eventName, fromDB, contentLine)
    return (recordMatch)


def CheckTaxRateActiveState(taxName):
    """
    Check the active state of the tax rate details based on the tax rate name from database
    Args: taxName (string)
    Return: recordResult (True/False)
    """
    recordResult = False
    queryString = """SELECT CONVERT(VARCHAR(3), TA.CS_ACTIVE_FG) AS 'ACTIVE' FROM TAX_AUTHORITY AS TA 
                        INNER JOIN CS_TEXT AS CTTD ON TA.CS_TXT_ID = CTTD.CS_TXT_ID AND CTTD.LANG_CD = 1
                        WHERE TA.TAX_CD NOT IN ('99', '100')
                        AND LOWER(CTTD.TEXT_DESCRIPTION) = '""" + taxName.lower() + """'"""
    log.debug(f"queryString = [{queryString}]")
    fromDB = ExecuteScalarFromDB(queryString)
    
    if (fromDB == '1'):
        recordResult = True

    return (recordResult)


def JSONReceivedTimeOutStatus(commandName, checkTimeAuto, timeOutInMin, timeIntervalInSec, operatorID):
    """
    Check the json object received or not at maximum interval check(timeOutInMin)
    From Insite360
    Args: commandName, checkTimeAuto, timeOutInMin, timeIntervalInSec, operatorID
    Returns: True/False (timeOut check for file received status)    
    """
    global fromServiceDt, logFileFromService
    fromServiceDt = datetime.now()
    log.info(f"Waiting[Max {timeOutInMin} Min] for [{commandName}] json received or not")
    log.info(f"Before command check the datetime [{fromServiceDt}]")
    fileFound = False
    timeOut = False
    waitMaxLimit = timeOutInMin * 60
    while not fileFound:
        fileFound = Check_Command_From_I360(commandName, checkTimeAuto, timeOutInMin, operatorID)
        if (not fileFound):
            log.info(f"[{commandName}].json is not received... waiting for [{timeIntervalInSec}] Seconds...")
            time.sleep(timeIntervalInSec)
            waitTime = datetime.now()
            datediff = Date_Diff(checkTimeAuto, waitTime)
            if (datediff >= waitMaxLimit):
                log.info(f"TIME OUT [{timeOutInMin}], .json [{commandName}] is not received...")
                timeOut = True
                fileFound = True
        else:
            log.info(f"After command[{commandName}] check the datetime [{fromServiceDt}] and filename [{logFileFromService}]")
        
    if not(timeOut):
        fileFound = False
        eventstatus = ""
        operation = ""
        if (commandName == "employees"):
            eventstatus = "employeeStatuses"
            operation = "employee-configuration-status-event"
        log.info(f"eventstatus = [{eventstatus}] and operation = [{operation}]")
        while not fileFound:
            # Check the event status for each command received from Insite360
            fileFound = Check_EventStatus(operation, eventstatus, logFileFromService, fromServiceDt, timeOutInMin, operatorID)
            if (not fileFound):
                log.info(f"[{eventstatus}].json is generated... waiting for [{timeIntervalInSec}] Seconds...")
                time.sleep(timeIntervalInSec)
                waitTime = datetime.now()
                datediff = Date_Diff(fromServiceDt, waitTime)
                if (datediff >= waitMaxLimit):
                    log.info(f"TIME OUT [{timeOutInMin}], .json [{eventstatus}] is not generated...")
                    timeOut = True
                    fileFound = True

    return (timeOut)


def Check_EventStatus(operation, eventstatus, file_name, checkTimeAuto, timeOutInMin, operatorID):
    """
    Process the RMS.log file based on the operation and event status check either
    the event status is generated and sent to insite369 or not
    Args:
        operation (string) : RMS_dateformat.log
        eventstatus (string) : employees/ taxRates
        file_name (datetime) : Start date Time from automation script
        checkTimeAuto (int) : time out in minutes , maximum wait time
        timeOutInMin (string) : employee operator ID received from Insite360
    Returns: True/ False
    """
    line_number = 0
    file_lines = 0
    recordFound = False
    returnValue = False
    list_of_results = []
    list_of_LineNumbers = []

    operStr = operation
    string_to_search = 'Sending data over websocket connection [{"payload":{"' + eventstatus + '":[{"operatorId":"' + operatorID + '","status":"'
    # Open the file in read only mode
    with open(file_name, 'r') as read_obj:
        # Read all lines in the file one by one
        for line in read_obj:
            # For each line, check if line contains the string
            line_number += 1
            if string_to_search in line:
                # If yes, then add the line number & line as a tuple in the list
                if operStr in line:
                    list_of_results.append(line)
                    list_of_LineNumbers.append(line_number)
                    recordFound = True

    if (recordFound):
        file_lines = line_number - 1
        i = 0
        while i < len(list_of_LineNumbers):
            line_number = list_of_LineNumbers[i]
            i = i + 1

        # get the date time from line and check with date time
        # 4 - starting position of the datetime and 27 is end position of datetime in file
        resultString = list_of_results[i - 1]
        fromFiledate = resultString[4: 27]
        fromService = datetime.strptime(fromFiledate, "%m/%d/%Y %H:%M:%S.%f")
        log.info(f"Latest {eventstatus} generated @ [{fromFiledate}] :: Check Start time [{checkTimeAuto}]")
        # Service time should be greater than Max 15 minutes, other wise
        # Read from the common method
        timegap = Date_Diff(checkTimeAuto, fromService)
        timeOutInSec = timeOutInMin * 60
        if (timegap <= timeOutInSec):
            log.info(f"Check between the lines [{ str(line_number) } : {str(file_lines)} ] in the file.")
            msgID = Get_MessageID(resultString)

            with open(file_name, 'r') as fp:
                for line_no, line in enumerate(fp):
                    if line_no >= line_number and line_no <= file_lines:
                        status = line.find('Message Received over websocket') and line.find(msgID)
                        if (status > 0):
                            log.info(f"LineNo:[{line_no}] - Message Received over websocket {eventstatus}")
                            startStatus = line.find('"success":')
                            successLen = len('"success":')
                            log.info(f"line = [{line}]")
                            if (line[startStatus + successLen: startStatus + successLen + 4] == 'true'):
                                returnValue = True
                                log.info(f"{eventstatus} Received Status: Success")
                            else:
                                log.info(f"{eventstatus} Received Status: UnSuccess. Please see the logs")
                            break
        else:
            log.info("No configuration-status-event data generated")
    else:
        log.info('No Record Found....')

    return (returnValue)        


def Check_Command_From_I360(commandName, checkTimeAuto, timeOutInMin, operatorID):
    """
    The file would be copied to automation drive and start process
    Args:
        commandName (string) : employees/ securitygroups/ taxrates
        checkTimeAuto (datetime) : Start date Time from automation script
        timeOutInMin (int) : time out in minutes , maximum wait time
        operatorID (string) : employee operator ID received from Insite360
    Returns: True/ False
    """
    global logFileFromService
    now = datetime.now().strftime("%Y%m%d")
    fileName = "RMS_" + now + ".log"
    source = "d:/gilbarco/logs/"
    destination = "d:/Automation/output/"
    
    result = False

    fileCopyStatus = CopyFile(source, destination, fileName)
    
    if (fileCopyStatus == "Success"):
        fileName = destination + fileName
        logFileFromService = fileName
        result = CheckCommand(fileName, commandName, checkTimeAuto, timeOutInMin, operatorID)
    else:
        log.info(f"File [{ source + fileName }] is not found... skip this time to process")

    return (result)


def CheckCommand(file_name, commandName, checkTimeAuto, timeOutInMin, operatorID):
    """
    Process the RMS.log file based on the commandName and check either the event send to insite is
    successful or not
    Args:
        file_name (string) : RMS_dateformat.log
        commandName (string) : employees/ taxRates
        checkTimeAuto (datetime) : Start date Time from automation script
        timeOutInMin (int) : time out in minutes , maximum wait time
        operatorID (string) : employee operator ID received from Insite360
    Returns: True/ False
    """
    global fromServiceDt
    line_number = 0
    file_lines = 0
    recordFound = False
    returnValue = False
    list_of_results = []
    list_of_LineNumbers = []

    operStr = ''
    if (commandName == 'employees'):
        operStr = '"operation":"employee-configuration-cmd"'
    elif (commandName == 'taxRates'):
        operStr = '' #'"operation":"tax-rate-configuration-event"'

    string_to_search = 'Message received over websocket [{"payload":{"' + commandName + '":[{"operatorId":"' + operatorID
    log.info(f"string_to_search for [{commandName}] is [{string_to_search}]")
    # Open the file in read only mode
    with open(file_name, 'r') as read_obj:
        # Read all lines in the file one by one
        for line in read_obj:
            # For each line, check if line contains the string
            line_number += 1
            if string_to_search in line:
                # If yes, then add the line number & line as a tuple in the list
                if operStr in line:
                    list_of_results.append(line)
                    list_of_LineNumbers.append(line_number)
                    recordFound = True

    if (recordFound):
        file_lines = line_number - 1
        i = 0
        while i < len(list_of_LineNumbers):
            line_number = list_of_LineNumbers[i]
            i = i + 1

        # get the date time from line and check with date time
        # 4 - starting position of the datetime and 27 is end position of datetime in file
        resultString = list_of_results[i - 1]
        fromFiledate = resultString[4: 27]
        fromService = datetime.strptime(fromFiledate, "%m/%d/%Y %H:%M:%S.%f")
        log.info(f"Latest {commandName} received @ [{fromFiledate}] :: Check Start time [{checkTimeAuto}]")
        # Service time should be greater than Max 15 minutes, other wise
        # Read from the common method
        timegap = Date_Diff(checkTimeAuto, fromService)
        timeOutInSec = timeOutInMin * 60
        if (timegap <= timeOutInSec):
            log.info(f"Check between the lines [{ str(line_number) } : {str(file_lines)} ] in the file.")
            msgID = Get_MessageID(resultString, True)
            log.info(f"For [{commandName}] : Message ID =[{msgID}]")

            datafromPassport = GetJson_FromDB(commandName, operatorID)
            dataMatch = ValidateStringFromDB(commandName, datafromPassport, resultString, True)
            
            if (not dataMatch):
                log.info(f"[{commandName}] json data from db is not match. Invalid json data")
                return (dataMatch)

            with open(file_name, 'r') as fp:
                for line_no, line in enumerate(fp):
                    if line_no >= line_number and line_no <= file_lines:
                        status = line.find('Sending data over websocket connection') and line.find(msgID)
                        if (status > 0):
                            fromServiceDt = datetime.strptime(line[4: 27], "%m/%d/%Y %H:%M:%S.%f")
                            log.info(f"LineNo:[{line_no}] - Sending data over websocket connection {commandName}")
                            startStatus = line.find('"success":')
                            successLen = len('"success":')
                            log.info(f"line = [{line}]")
                            if (line[startStatus + successLen: startStatus + successLen + 4] == 'true'):
                                returnValue = True
                                log.info(f"{commandName} Received Status: Success")
                            else:
                                log.info(f"{commandName} Received Status: UnSuccess. Please see the logs")
                            break
        else:
            log.info("No configuration data received")
    else:
        log.info('No Record Found....')

    return (returnValue)


def GetJson_FromDB(commandName, uniqId, notCondition=False):
    """
    Check or validate JSON received from Insite360 or not
    Args:   commandName (string)
            uniqId (string) - employee operator ID
            notCondition (boolean) - default value is False
    Returns:fromDB (string) - json object from database
    """
    log.info(f"Check the [{commandName}] json data from DB unique ids [{uniqId}] with not condition [{notCondition}]")
    queryString = ""
    if (uniqId == ""):
        substring = "= E.EMP_ID"
    else:
        substring = "= " + uniqId
        if (notCondition):
            substring = "<> " + uniqId

    if (commandName == "employees"):
        queryString = """SELECT 
        E.EMP_ID AS OperatorId, 
        E.LST_NM AS LastName, E.FRST_NM AS FirstName, 
        REPLACE(CONVERT(VARCHAR(32), E.BIRTH_DT, 21),' ','T')+'Z' AS BirthDate, 
        CONVERT(VARCHAR(10), E.LANG_CD) AS LanguageCode, 
        CONVERT(VARCHAR(10), E.HAND_PREF) AS HandPreference, 
        CONVERT(VARCHAR(10), E.KEYPAD_TYPE) AS KeypadPreference, 
        CONVERT(BIT,CS_OVERRIDE_OPT_FG) AS OverrideBlindBalanceOption, 
        CONVERT(VARCHAR(10), E.CS_BLIND_BAL_FG) AS ViewTotalOnBlindBalance, 
        E.CLOCK_IN_OUT_REQ AS ClockInOutRequired, 
        CONVERT(VARCHAR(10), E.CS_THEME) AS Theme, 
        CONVERT(VARCHAR(10), PG.SECURITY_LEVEL) AS SecurityLevelId, 
        ISNULL(EA.LN_1, '') AS AddressLine1, ISNULL(EA.LN_2, '') AS AddressLine2, 
        ISNULL(EA.LN_3, '') AS AddressLine3, 
        ISNULL(EA.CTY, '') AS City, ISNULL(EA.ST, '') AS State, 
        ISNULL(EA.PST_CD, '') AS PostalCode, 
        ISNULL(ET.AREA_CD, '') AS AreaCode, ISNULL(ET.PHN_NBR, '') AS PhoneNumber,  
        CONVERT(BIT, CASE WHEN ISNULL(E.TERM_DT, '')='' THEN 'true' ELSE 'false' END) AS Active
        FROM EMPLOYEE AS E  
        INNER JOIN 
        EMPLOYEE_GROUP AS EG ON E.EMP_ID = EG.EMP_ID """
        queryString = queryString + " AND E.EMP_ID " + substring
        queryString = queryString + """
        INNER JOIN 
        PERMISSION_GROUP AS PG ON EG.GRP_ID = PG.GRP_ID AND PG.SECURITY_LEVEL <= 90 
        LEFT JOIN 
        ADDRESS AS EA ON E.EMP_ID = EA.ADDR_ID AND EA.USAGE_CD = 1 
        LEFT JOIN 
        TELEPHONE AS ET ON E.EMP_ID = ET.PHN_ID AND ET.USAGE_CD = 1 
        FOR JSON PATH, ROOT('employees')"""

    fromDB = ExecuteScalarFromDB(queryString)
    log.info(f"queryString = [{queryString}]")
    log.info(f"[{commandName}] json data from db : {fromDB.lower()}")
    return fromDB


def getUpdatedLogText(fromLog, fromDB):
    """
    Replacing the 'birthDate' time string from DB to Log. 
    Args:   fromLog (string) - json object string
            fromDB (string) - json object string
    Returns: restultStr(String) - returns replaced text
    """
    restultStr = fromLog
    string_to_search = '","birthdate":"'
    findstr = fromDB.find(string_to_search)
    log.info(f"string_to_search [{string_to_search}] findstr = [{findstr}]")
    searchStr = len(string_to_search) + 10
    replaceStr = fromDB[findstr + searchStr : findstr + searchStr + 14]
    updatestr = fromLog[findstr + searchStr : findstr + searchStr + 14]
    log.info(f"Replacing the 'birthDate' time [{updatestr}] with [{replaceStr}] AT LOG")
    restultStr = fromLog.replace(updatestr, replaceStr, 1)
    return restultStr


def DeleteRMSLog():
    """
    Delete all RMS.log files from specified path
    Args: None
    Returns: None
    """
    destination = "d:/Automation/output/"
    filelist = [ fileName for fileName in os.listdir(destination) if fileName.endswith(".log") ]
    for fileName in filelist:
        os.remove(os.path.join(destination, fileName))


def ValidateStringFromDB(searchFor, fromDB, contentLine, excludeBirthTime=False):
    """
    Verify/ Validate the content from the insite360 json object and from database either the values are same or not
    Args:
        searchFor (string) : command name/ event name 
        fromDB (string) : from db json object 
        contentLine (string) : from RMS.log line of conent of json obejct
        excludeBirthTime (boolean) : default value is False, if it is True then replace the birtTime with comparing value
    Returns: recordMatch(boolean) True/ False 
    """
    recordMatch = False
    if (fromDB != ""):
        payloadStr = '"payload":'
        findstr = contentLine.find(payloadStr)
        if (findstr > 0):
            findstr = findstr + len(payloadStr)
            fromLog = contentLine[findstr: findstr + len(fromDB)]
            log.info(f"[{searchFor}] json data from log: {fromLog.lower()}")
            # Excluding the birthdate time with empty time to validate both insite360 and passport data
            if (excludeBirthTime):
                log.info(f"Replacing the 'birthDate' time with 00.00.00.000")
                fromLog = getUpdatedLogText(fromLog.lower(), fromDB.lower())

            if (fromLog.lower() == fromDB.lower()):
                recordMatch = True

    return (recordMatch)


def json_generate_status(start_time, event_type, file_copied=False, no_reset=False):
    """
    Restart the RemoteManagerService and check the json file
    is generated or not
    Args: start_time (datetime)
          event_type (string) must be either "securitygroups" or "employees"
          file_copied (bool) - rms log file availble or not
          no_reset (bool)
    Returns: json_timeout (bool) - True/ False
    """
    # Restart the Service and check the JSON Data generated or NOT
    if (no_reset):
        time_out_in_min = 17
    else:
        time_out_in_min = RestartServiceAndValidate()
    json_timeout = JSONGenerateTimeOutStatus(event_type, start_time, time_out_in_min, 60, file_copied, False, True)
    return json_timeout


def restart_rmservice_max(event_type):
    """
    Restart the remote manager service maximum 5 times if any issue
    Args: event_type (string) must be either "securitygroups" or "employees"
    Returns: json_timeout (bool) - True/ False
    """
    cnt = 1
    max_times = 5
    json_timeout = True
    # check again, some issue with remote manager service
    log.warning(f"Issue at Remotemager. Check again eiter json is generated or not")
    while (cnt <= max_times and json_timeout == True):
        log.warning(f"Issue at Remotemager[{event_type}]. Restarted count: [{cnt}]")
        start_time = datetime.now()
        json_timeout = json_generate_status(start_time, event_type)
        cnt = cnt + 1
    return json_timeout

