"""
    File name: LoyaltyService.py
    Tags:
    StoryID: PPAUTO-5071
    Description: Functions to perform loyalty configuration at simulator
    Author: Pavan Kumar Kantheti
    Date created: 2020-04-03 15:10:05
    Date last modified: 2020-04-16 15:47:20
    Python Version: 3.7
"""
import logging
import sys
import clr
import os
import psutil
import json

LOYALTY_SIM_PATH = "D:/Automation/Tools/LoyaltySimulator"
sys.path.append(LOYALTY_SIM_PATH)
clr.AddReference("LoyaltyClassLibrary")
from LoyaltyClassLibrary import Loyalty

log = logging.getLogger()


def StartLoyaltySim():
    """
    Stop and Start the Loyalty Simulator dektop application
    Args: None
    Return: status (0 - Success)
    """
    ProcName = "LoyaltySimulator.exe"
    for proc in psutil.process_iter():
        # check whether the process name matches
        if (proc.name() == ProcName):
            proc.kill()

    cmd = r"start /min " + LOYALTY_SIM_PATH + "/" + ProcName
    status = os.system(cmd)
    return (status)


def StopLoyaltySim():
    """
    Stop the Loyalty Simulator dektop application
    Args: None
    Return: status (True/ False)
    """
    try:
        status = False
        ProcName = "LoyaltySimulator.exe"
        for proc in psutil.process_iter():
            # check whether the process name matches
            if (proc.name() == ProcName):
                proc.kill()
                status = True
    except:
        log.error(f"Unable to stop the 'LoyaltySimulator.exe' - [{sys.exc_info()[0]}]")
        status = False

    return status


def GetAllLoyaltyIds():
    """
    Get all the Loyalty Ids Configuratin data in JSON data format
    Args: None
    Return: result (JSON data format string)
    Example:
        >>> GetAllLoyaltyIds()
        '{"LoyaltyIDs":{
            "LoyaltyID":[
                {"Id":"0","Name":"NONLOYALTY","MCS":"","RFID":"","BARCODE":"","MANUAL":"","OTHER":"",
                "StatusMessages":{"DisplayLines":null,"ReceiptLines":null}},
                {"Id":"1","Name":"LOY1","MCS":"6008*","RFID":"","BARCODE":"6008*","MANUAL":"6008*","OTHER":""},
                {"Id":"2","Name":"LOY2","MCS":"6006*","RFID":"","BARCODE":"6006*","MANUAL":"6006*","OTHER":""},
                {"Id":"3","Name":"LOY3","MCS":"7083*","RFID":"","BARCODE":"7083*","MANUAL":"7083*","OTHER":""},
                {"Id":"4","Name":"LOY4","MCS":"603237*","RFID":"603237*","BARCODE":"603237*","MANUAL":"603237*","OTHER":"603237*"},
                {"Id":"5","Name":"LOY5","MCS":"7120*","RFID":"7120*","BARCODE":"7120*","MANUAL":"7120*","OTHER":"7120*"},
                {"Id":"6","Name":"LOY6","MCS":"20000*","RFID":"20000*","BARCODE":"20000*","MANUAL":"20000*","OTHER":"20000*"},
                {"Id":"7","Name":"LOY7","MCS":"34111*","RFID":"34111*","BARCODE":"34111*","MANUAL":"34111*","OTHER":"34111*"}]}}'
    """
    result = Loyalty().GetAllLoyaltyIds()
    return result


def GetLoyaltyIdData(LoyaltyID, MCS):
    """
    Get Loyalty ID data based on loyalty ID
    Args:   LoyaltyID (string) - Ids like ("1", "2", "3", "4",...)
            MCS (string) - magnetic card swipe like ("6008", "7377",...)
    Return: result (JSON data format string)
    Example:
        >>> GetLoyaltyIdData("1", "")
        >>> GetLoyaltyIdData("", "6008")
        >>> GetLoyaltyIdData("1", "6008")
        '{"LoyaltyID":{
              "Id":"1","Name":"LOY1","MCS":"6008*","RFID":"","BARCODE":"6008*","MANUAL":"6008*","OTHER":""}}'
    """
    result = Loyalty().GetLoyaltyIdData(LoyaltyID, MCS)
    return result


def GetLoyaltyId(MCS):
    """
    Gets a loyalty ID based off MCS
    Args:   MCS (string) - Magnetic Card Swipe data
    Return: result (string) loyaltyID if it exists, -1 if not
    Example:
        >>> Loyalty().GetLoyaltyId("6008")
        '1'
    """
    ids = json.loads(GetAllLoyaltyIds())
    for id in ids["LoyaltyIDs"]["LoyaltyID"]:
        if id['MCS'] == MCS:
            return str(id["Id"])
    return "-1";


def AddLoyaltyIDs(MCS, RFID="", Barcode="", Manual="", Others=""):
    """
    Add a new Loyalty IDs Configuration data
    Args:   MCS (string) - Magnetic Card Swipe data
            RFID (string) - RFID value
            Barcode(string)
            Manual (string)
            Others (string)
    Return: result (string) loyaltyID
    Example: 
        >>> Loyalty().AddLoyaltyIDs("6008", "6008", "6008", "6008", "6008")
        '1'
    """
    result = Loyalty().AddLoyaltyIDs(MCS, RFID, Barcode, Manual, Others)
    return result


def UpdateLoyaltyID(LoyaltyID, MCS, RFID="", Barcode="", Manual="", Others=""):
    """
    Update the loyalty configuration data based on LoyaltyID
    Args:   LoyaltyID (string)
            MCS (string) - Magnetic Card Swipe data
            RFID (string) - RFID value
            Barcode(string)
            Manual (string)
            Others (string)
    Return: result (bool) True/False
    Example:
        >>> UpdateLoyaltyID("1", "6007", "6007", "6007", "6007", "6007")
        True
            
    """
    result = False
    result = Loyalty().UpdateLoyaltyID(LoyaltyID, MCS, RFID, Barcode, Manual, Others)
    if (result == 'true'):
        result = True
    return result


def DeleteLoyaltyID(LoyaltyID):
    """
    Delete the Loyalty Configuration data based on LoyaltyID
    Also un-Assign LoyaltyID based Rewards, Status Messages and Prompts
    Args: LoyaltyID (string)
    Returns: result (bool) True/False
    Example: 
        >>> DeleteLoyaltyID("1")
        True
    """
    result = False
    result = Loyalty().DeleteLoyaltyID(LoyaltyID)
    if (result == 'true'):
        result = True
    return result


def DeleteAllLoyaltyIDs():
    """
    Delete all existing loyalty IDs with out any condition
    Args: None
    Return: result (bool) True/False
    Example: 
        >>> DeleteAllLoyaltyIDs()
        True
    """
    result = False
    result = Loyalty().DeleteAllLoyaltyIDs()
    if (result == 'true'):
        result = True
    return result


def GetAllPrompts():
    """
    Get all the Prompts Configuration data with out any check
    Args: None
    Returns: result (JSON data format string)
    Example:
        >>> GetAllPrompts()
        '{"Prompts":{"Prompt":[{"PromptID":"1","PromptName":"Prompt1","Type":"Boolean","DisplayDevice":"OPT",
                    "PromptTextShort":" Prompt1","PromptTextLong":"Prompt1","TimeOut":"30","MinLength":"",
                    "MaxLength":"","MaskUserInput":""},
                    {"PromptID":"2","PromptName":"Prompt2","Type":"Boolean","DisplayDevice":"OPT",
                    "PromptTextShort":"Prompt2","PromptTextLong":"Prompt2","TimeOut":"10","MinLength":"",
                    "MaxLength":"","MaskUserInput":""}]}}'
    """
    result = Loyalty().GetAllPrompts()
    return result


def GetPromptData(PromptID):
    """
    Get the prompts configuration data based on the PromptID
    Args:   PromptID (string)
    Returns: result (JSON data format string)
    Example:
        >>> GetPromptData("1")
        '{"Prompt":
            {"PromptID":"1","PromptName":"Prompt1","Type":"Boolean","DisplayDevice":"OPT",
            "PromptTextShort":" Prompt1","PromptTextLong":"Prompt1","TimeOut":"30","MinLength":"",
            "MaxLength":"","MaskUserInput":""}}'
    """
    result = Loyalty().GetPromptData(PromptID)
    return result


def AddPrompts(PromptName, PromptType="Boolean", DisplayDevice="OPT", PromptTextShort="", PromptTextLong="", MaskUserInput="", TimeOut="1", MinLength="", MaxLength=""):
    """
    Adding new prompts configuration
    Args:   PromptName (string)
            PromptType (strig) - should be {"Boolean", "Numeric"}
            DisplayDevice (string) - should be {"OPT", "POS-Cashier", "POS-CustTerminal", "POS-PoleDisplay", "None"}
            PromptTextShort (string)
            PromptTextLong (string)
            MaskUserInput (string) - should be {"","yes", "no"}
            TimeOut (string) - any numeric value like (1 to 100)
            MinLength (string) - empty or numeric value {1 to 100)
            MaxLength (string) - empty or numeric value {1 to 100)
    Returns: result (string) - PromptID
    Example:
        >>> AddPrompts("Prompt Name", "Numeric", "OPT", "Prompt Name", "Prompt Name", "yes", "10", "1", "10")
        '1'
        >>> AddPrompts("Prompt Name", "Boolean", "POS-Cashier", "Prompt Name", "Prompt Name", "no", "20", "", "")
        '2'
    """
    result = ''
    if not(PromptType == "Boolean" or PromptType == "Numeric"):
        log.info("PromptType should be in {'Boolean','Numeric'}")
        return result
    if not(DisplayDevice == "OPT" or DisplayDevice == "POS-Cashier" or DisplayDevice == "POS-CustTerminal" or DisplayDevice == "POS-PoleDisplay" or DisplayDevice == "None"):
        log.info("DisplayDevice should be in {'OPT', 'POS-Cashier', 'POS-CustTerminal', 'POS-PoleDisplay', 'None'}")
        return result
    if not(MaskUserInput == "" or MaskUserInput == "yes" or MaskUserInput == "no"):
        log.info("MaskUserInput should be in {'','yes', 'no'}")
        return result
    if (PromptTextShort == ""):
        PromptTextShort = PromptName
    if (PromptTextLong == ""):
        PromptTextLong = PromptName

    result = Loyalty().AddPrompts(PromptName, PromptType, DisplayDevice, PromptTextShort, PromptTextLong, MaskUserInput, TimeOut, MinLength, MaxLength)
    return result


def UpdatePrompts(PromptID, PromptName, PromptType, DisplayDevice, PromptTextShort, PromptTextLong, MaskUserInput, TimeOut, MinLength, MaxLength):
    """
    Modification/Update for existing prompt configuratin data based on PromptID
    If PromptID is "" then it works same as AddPrompts function
    Args:   PromptID (string)
            PromptName (string)
            PromptType (strig) - should be {"Boolean", "Numeric"}
            DisplayDevice (string) - should be {"OPT", "POS-Cashier", "POS-CustTerminal", "POS-PoleDisplay", "None"}
            PromptTextShort (string)
            PromptTextLong (string)
            MaskUserInput (string) - should be {"","yes", "no"}
            TimeOut (string) - any numeric value like (1 to 100)
            MinLength (string) - empty or numeric value {1 to 100)
            MaxLength (string) - empty or numeric value {1 to 100)
    Returns: result (bool) True/False
    Example:
            >>> UpdatePrompts("1", "Prompt Name", "Numeric", "OPT", "Prompt Name", "Prompt Name", "yes", "10", "1", "10")
            True
    """
    result = False
    if not(PromptType == "Boolean" or PromptType == "Numeric"):
        log.info("PromptType should be in {'Boolean','Numeric'}")
        return result
    if not(DisplayDevice == "OPT" or DisplayDevice == "POS-Cashier" or DisplayDevice == "POS-CustTerminal" or DisplayDevice == "POS-PoleDisplay" or DisplayDevice == "None"):
        log.info("DisplayDevice should be in {'OPT', 'POS-Cashier', 'POS-CustTerminal', 'POS-PoleDisplay', 'None'}")
        return result
    if not(MaskUserInput == "" or MaskUserInput == "yes" or MaskUserInput == "no"):
        log.info("MaskUserInput should be in {'','yes', 'no'}")
        return result
    if (PromptTextShort == ""):
        PromptTextShort = PromptName
    if (PromptTextLong == ""):
        PromptTextLong = PromptName

    result = Loyalty().UpdatePrompts(PromptID, PromptName, PromptType, DisplayDevice, PromptTextShort, PromptTextLong, MaskUserInput, TimeOut, MinLength, MaxLength)
    if (result == 'true'):
        result = True
    return result


def DeletePrompt(PromptID):
    """
    Delete the existing prompt based on the PromptID
    Args: PromptID (string)
    Returns: result (bool) True/False
    Example:
        >>> DeletePrompt("1")
        True
    """
    result = False
    result = Loyalty().DeletePrompt(PromptID)
    if (result == 'true'):
        result = True
    return result


def GetDisplayCommand():
    """
    Get the Display Command data with display lines
    Args: None
    Return: result (JSON data format string)
    Example:
        >>> GetDisplayCommand()
        '{"DisplayCommands":{
            "DisplayCommand":{
                "DisplayCommandID":"1","Code":"Display Command Text","GetRewards":"True",
                "GetCustomerMessaging":"False","FinalizeRewards":"False","GetRewardStatus":"False",
                "Device":"OPT","Sequence":"AfterFueling","Duration":"1",
                "DisplayLines":{
                    "DisplayLine":"new display line..."}}}}'
    """
    result = Loyalty().GetDisplayCommand()
    return result


def GetDisplayLines():
    """
    Get the only display lines from command
    Args: None
    Return: result (JSON data format string)
    Example:
        >>> GetDisplayLines()
        '{"DisplayLines":{"DisplayLine":"new display line..."}}'
    """
    result = Loyalty().GetDisplayLines()
    return result


def UpdateDisplayCommandDetails(CommandName="new display command", GetRewards="True", GetCustomerMessaging="False", FinalizeRewards="False", GetRewardStatus="False", Device="OPT", Sequence="AfterFueling", Duration="10", DisplayLines="new display line..."):
    """
    update the Display Commands Configuration based on Display Command ID = "1"
    Args:   CommandName (string) - Command Name
            GetRewards (string) - value should be in - {'True', 'False'}
            GetCustomerMessaging (string) - value should be in - {'True', 'False'}
            FinalizeRewards (string) - value should be in - {'True', 'False'}
            GetRewardStatus (string) - value should be in - {'True', 'False'}
            Device (string) - value should be in - {"OPT", "POS-Cashier", "POS-CustTerminal", "POS-PoleDisplay", "None"}
            Sequence (string) - value should be in - {"WhenReceived", "BeforeFueling", "DuringFueling", "AfterFueling", "None"}
            Duration (string) - any numeric value like (1 to 100)
            DisplayLines (string) - if need to add more lines should be seperated by "|" Example: "Display Line1|Display Line2"
    Return: result (bool) True/False
    Example:
        >>> UpdateDisplayCommandDetails("new display command", "True", "False", "False", "False", "OPT", "WhenReceived", "7", "Display Line1|Display Line2")
        True
    """
    result = False
    if not(GetRewards == "True" or GetRewards == "False"):
        log.info("GetRewards (string) - value should be in - {'True', 'False'}")
        return result
    if not(GetCustomerMessaging == "True" or GetCustomerMessaging == "False"):
        log.info("GetCustomerMessaging (string) - value should be in - {'True', 'False'}")
        return result
    if not(FinalizeRewards == "True" or FinalizeRewards == "False"):
        log.info("FinalizeRewards (string) - value should be in - {'True', 'False'}")
        return result
    if not(GetRewardStatus == "True" or GetRewardStatus == "False"):
        log.info("GetRewardStatus (string) - value should be in - {'True', 'False'}")
        return result
    if not(Device == "OPT" or Device == "POS-Cashier" or Device == "POS-CustTerminal" or Device == "POS-PoleDisplay" or Device == "None"):
        log.info("Device should be in {'OPT', 'POS-Cashier', 'POS-CustTerminal', 'POS-PoleDisplay', 'None'}")
        return result
    if not(Sequence == "WhenReceived" or Sequence == "BeforeFueling" or Sequence == "DuringFueling" or Sequence == "AfterFueling" or Sequence == "None"):
        log.info("Sequence should be in {'WhenReceived', 'BeforeFueling', 'DuringFueling', 'AfterFueling', 'None'}")
        return result

    result = Loyalty().UpdateDisplayCommandDetails(Code, GetRewards, GetCustomerMessaging, FinalizeRewards, GetRewardStatus, Device, Sequence, Duration, DisplayLines)

    if (result == 'true'):
        result = True
    return result


def AddDisplayLines(DisplayLines="Display Line1|Display Line2"):
    """
    Add new Display Lines for command
    Args: DisplayLines (string) - if need to add more lines should be seperated by "|" Example: "Display Line1|Display Line2"
    Returns: result (bool) True/False
    Example:
        >>> AddDisplayLines("Display Line1|Display Line2")
        True
    """
    result = False
    result = Loyalty().AddDisplayLines(DisplayLines)
    if (result == 'true'):
        result = True
    return result


def UpdateDisplayLines(DisplayLines="Display Line1|Display Line2"):
    """
    Clear and Add new Display Lines for command
    Args: DisplayLines (string) - if need to add more lines should be seperated by "|" Example: "Display Line1|Display Line2"
    Returns: result (bool) True/False
    Example:
        >>> UpdateDisplayLines("Display Line1|Display Line2")
        True
    """
    result = False
    result = Loyalty().UpdateDisplayLines(DisplayLines)
    if (result == 'true'):
        result = True
    return result


def DeleteDisplayLine(DisplayLine="Display Line1"):
    """
    Delete the Display Line from the command, based on the provided DisplayLine
    Args: DisplayLine (string)
    Returns: result (bool) True/False
    Example:
        >>> DeleteDisplayLine("Display Line1")
        True
    """
    result = False
    result = Loyalty().DeleteDisplayLine(DisplayLine)
    if (result == 'true'):
        result = True
    return result


def GetReceiptCommand():
    """
    Get the Receipt Command data with Receipt lines
    Args: None
    Return: result (JSON data format string)
    Example:
        >>> GetReceiptCommand()
        '{"ReceiptCommands":{
            "ReceiptCommand":{
                "ReceiptCommandID":"1","Code":"New Receipt Text","GetRewards":"False",
                "GetCustomerMessaging":"False","FinalizeRewards":"False","GetRewardStatus":"False",
                "ReceiptLines":{
                    "ReceiptLine":"new receipt line..."}}}}'
    """
    result = Loyalty().GetReceiptCommand()
    return result


def GetReceiptLines():
    """
    Get the only Receipt lines from command
    Args: None
    Return: result (JSON data format string)
    Example:
        >>> GetReceiptLines()
            '{"ReceiptLines":{
                "ReceiptLine":"new receipt line..."}}'
    """
    result = Loyalty().GetReceiptLines()
    return result


def UpdateReceiptCommandDetails(CommandName="new Receipt command", GetRewards="True", GetCustomerMessaging="False", FinalizeRewards="False", GetRewardStatus="False", ReceiptLines="new Receipt line..."):
    """
    update the Receipt Commands Configuration based on Receipt Command ID = "1"
    Args:   CommandName (string) - Command Name
            GetRewards (string) - value should be in - {'True', 'False'}
            GetCustomerMessaging (string) - value should be in - {'True', 'False'}
            FinalizeRewards (string) - value should be in - {'True', 'False'}
            GetRewardStatus (string) - value should be in - {'True', 'False'}
            ReceiptLines (string) - if need to add more lines should be seperated by "|" Example: "Receipt Line1|Receipt Line2"
    Return: result (bool) True/False
    Example:
        >>> UpdateReceiptCommandDetails("new Receipt command", "True", "False", "False", "False", "Receipt Line1|Receipt Line2")
        True
    """
    result = False
    if not(GetRewards == "True" or GetRewards == "False"):
        log.info("GetRewards (string) - value should be in - {'True', 'False'}")
        return result
    if not(GetCustomerMessaging == "True" or GetCustomerMessaging == "False"):
        log.info("GetCustomerMessaging (string) - value should be in - {'True', 'False'}")
        return result
    if not(FinalizeRewards == "True" or FinalizeRewards == "False"):
        log.info("FinalizeRewards (string) - value should be in - {'True', 'False'}")
        return result
    if not(GetRewardStatus == "True" or GetRewardStatus == "False"):
        log.info("GetRewardStatus (string) - value should be in - {'True', 'False'}")
        return result

    result = Loyalty().UpdateReceiptCommandDetails(Code, GetRewards, GetCustomerMessaging, FinalizeRewards, GetRewardStatus, ReceiptLines)

    if (result == 'true'):
        result = True
    return result


def AddReceiptLines(ReceiptLines="Receipt Line1|Receipt Line2"):
    """
    Add new Receipt Lines for command
    Args: ReceiptLines (string) - if need to add more lines should be seperated by "|" Example: "Receipt Line1|Receipt Line2"
    Returns: result (bool) True/False
    Example:
        >>> AddReceiptLines("Receipt Line1|Receipt Line2")
        True
    """
    result = False
    result = Loyalty().AddReceiptLines(ReceiptLines)
    if (result == 'true'):
        result = True
    return result


def UpdateReceiptLines(ReceiptLines="Receipt Line1|Receipt Line2"):
    """
    Clear and Add new Receipt Lines for command
    Args: ReceiptLines (string) - if need to add more lines should be seperated by "|" Example: "Receipt Line1|Receipt Line2"
    Returns: result (bool) True/False
    Example:
        >>> UpdateReceiptLines("Receipt Line1|Receipt Line2")
        True
    """
    result = False
    result = Loyalty().UpdateReceiptLines(ReceiptLines)
    if (result == 'true'):
        result = True
    return result


def DeleteReceiptLine(ReceiptLine="Receipt Line1"):
    """
    Delete the Receipt Line from the command, based on the provided ReceiptLine
    Args: ReceiptLine (string)
    Returns: result (bool) True/False
    Example:
        >>> DeleteReceiptLine("Receipt Line1")
        True
    """
    result = False
    result = Loyalty().DeleteReceiptLine(ReceiptLine)
    if (result == 'true'):
        result = True
    return result


def GetTransactionRewardsList():
    """
    Get the all available transaction level rewards in JSON data format
    Args: None
    Return: result (JSON data format string)
    Example:
        >>> GetTransactionRewardsList()
        '{"TransactionLevelRewards":{
            "TransLevelRewardDetails":[
                {"TransLevelRewardID":"1","Name":"20 cents trans. rwd","TypeReward":"Instant",
                "TypeRewardDescription":"","Discount":"0.20","DiscountMethod":"amountOff",
                "ReceiptTextShort":"20 cents transaction Reward",
                "ReceiptTextLong":"20 cents transaction reward Receipt Text"},
                {"TransLevelRewardID":"2","Name":"30 cents trans. rwd.","TypeReward":"Instant",
                "TypeRewardDescription":"","DiscountMethod":"amountOff","Discount":"0.30",
                "ReceiptTextShort":"30 cents trans. rwd.",
                "ReceiptTextLong":"30 cents transaction reward"},
                {"TransLevelRewardID":"3","Name":"40 cents trans. rwd.","TypeReward":"Instant",
                "TypeRewardDescription":"","DiscountMethod":"amountOff","Discount":"0.40",
                "ReceiptTextShort":"40 cents trans. rwd.","ReceiptTextLong":"40 cents transaction reward"},
                {"TransLevelRewardID":"4","Name":"$10 - trans lev reg","TypeReward":"Instant",
                "TypeRewardDescription":"","DiscountMethod":"amountOff","Discount":"10.00",
                "ReceiptTextShort":"$10 - trans lev reg","ReceiptTextLong":"$10 - transaction level reward"},
                {"TransLevelRewardID":"5","Name":"$20 dollars","TypeReward":"Instant",
                "TypeRewardDescription":"","DiscountMethod":"amountOff","Discount":"20.00",
                "ReceiptTextShort":"short desc","ReceiptTextLong":"long desc"}]}}'
    """
    result = Loyalty().GetTransactionRewardsList()
    return result


def GetTransactionRewardsById(TransLevelRewardID="1", RewardName="20 cents Trans.Rwd"):
    """
    Get Tranasaction Reward by TransLevelRewardID or RewardName
    Args:   TransLevelRewardID (string) - Ids like ("1", "2", "3", "4",...)
            RewardName (string) - Transaction reward name
    Return: result (JSON data format string)
    Example:
        >>> GetTransactionRewardsById("1", "20 cents Trans.Rwd")
        >>> GetTransactionRewardsById("", "20 cents Trans.Rwd")
        >>> GetTransactionRewardsById("1", "")
        '{"TransLevelRewardDetails":
            {"TransLevelRewardID":"1","Name":"20 cents trans. rwd","TypeReward":"Instant",
            "TypeRewardDescription":"","Discount":"0.20","DiscountMethod":"amountOff",
            "ReceiptTextShort":"20 cents transaction Reward",
            "ReceiptTextLong":"20 cents transaction reward Receipt Text"}}'
    """
    result = ""
    if (TransLevelRewardID == "" and RewardName == ""):
        log.info("TransLevelRewardID or RewardName must be not empty")
        return result

    result = Loyalty().GetTransactionRewardsById(TransLevelRewardID, RewardName)
    return result


def AddTransactionReward(RewardName="20 cents Trans.Rwd", TypeReward="Instant", TypeRewardDescription="", DiscountMethod="amountOff", Discount="0.20", ReceiptTextShort="20 cents transaction Reward", ReceiptTextLong="20 cents transaction reward Receipt Text"):
    """
    Add new transaction level reward details
    Args:   RewardName (string) - transaction reward name
            TypeReward (string) - Reward Type must be - {"Instant", "Optional"}
            TypeRewardDescription (string) - if reward type is "Instant" then this field is optional "" other wise description to dispaly at POS
            DiscountMethod (string) - default "amountOff"
            Discount (string) - discount amount in any numeric value
            ReceiptTextShort (string)
            ReceiptTextLong (string)
    Return: result (string) - TransactionRewardID
    Example:
        >>> AddTransactionReward("20 cents Trans.Rwd", "Optional", "R u Sure?", "amountOff", "0.20", "20 cents transaction Reward", "20 cents transaction reward Receipt Text")
        "6"
    """
    result = ""
    if not(TypeReward == "Instant" or TypeReward == "Optional"):
        log.info("TypeReward (string) must be - {'Instant', 'Optional'}")
        return result
    if not(DiscountMethod == "amountOff"):
        log.info("DiscountMethod (string) - should be 'amountOff'")
        return result

    result = Loyalty().AddTransactionReward(RewardName, TypeReward, TypeRewardDescription, DiscountMethod, Discount, ReceiptTextShort, ReceiptTextLong)
    return result


def UpdateTransactionReward(TransactionId="1", RewardName="20 cents Trans.Rwd", TypeReward="Instant", TypeRewardDescription="", DiscountMethod="amountOff", Discount="0.20", ReceiptTextShort="20 cents transaction Reward", ReceiptTextLong="20 cents transaction reward Receipt Text"):
    """
    Update the transaction level reward details based on TransactionId
    if TransactionId = "" then the it act as AddTransactionReward function
    Args:   TransactionId (string) - any numeric value
            RewardName (string) - transaction reward name
            TypeReward (string) - Reward Type must be - {"Instant", "Optional"}
            TypeRewardDescription (string) - if reward type is "Instant" then this field is optional "" other wise description to dispaly at POS
            DiscountMethod (string) - default "amountOff"
            Discount (string) - discount amount in any numeric value
            ReceiptTextShort (string)
            ReceiptTextLong (string)
    Return: result (bool) True/False
    Example:
        >>> UpdateTransactionReward("1", "20 cents Trans.Rwd", "Optional", "R u Sure?", "amountOff", "0.20", "20 cents transaction Reward", "20 cents transaction reward Receipt Text")
        True
    """
    result = False
    if not(TypeReward == "Instant" or TypeReward == "Optional"):
        log.info("TypeReward (string) must be - {'Instant', 'Optional'}")
        return result
    if not(DiscountMethod == "amountOff"):
        log.info("DiscountMethod (string) - should be 'amountOff'")
        return result

    result = Loyalty().UpdateTransactionReward(TransactionId, RewardName, TypeReward, TypeRewardDescription, DiscountMethod, Discount, ReceiptTextShort, ReceiptTextLong)
    if (result == 'true'):
        result = True
    return result


def DeleteTransactionReward(TransactionID="1"):
    """
    Delete the transaction level reward based on the TransactionID
    Args: TransactionID (string)
    Returns: result (bool) True/False
    Example:
        >>> DeleteTransactionReward("1")
        True
    """
    result = False
    result = Loyalty().DeleteTransactionReward(TransactionID)
    if (result == 'true'):
        result = True
    return result


def GetNonFuelRewardsList():
    """
    Get the all available non-fuel rewards in JSON data format
    Args: None
    Return: result (JSON data format string)
    Example:
        >>> GetNonFuelRewardsList()
        '{"NonfuelRewards":
            {"NonfuelRewardDetails":
                {"NonfuelRewardId":"1","Name":"DryStockDiscount","TypeReward":"Optional",
                 "TypeRewardDescription":"Do you want to apply the discount?","DiscountMethod":"amountOff",
                 "Discount":"0.15","ItemType":"itemLine","CodeFormat":"plu","Code":"1","RewardLimit":"1",
                 "ReceiptText":""}}}'
    """
    result = Loyalty().GetNonFuelRewardsList()
    return result


def GetNonFuelRewardsById(NonfuelRewardId="1", RewardName="15 cents DryStock"):
    """
    Get NonFuel Reward by NonfuelRewardId or RewardName
    Args:   NonfuelRewardId (string) - Ids like ("1", "2", "3", "4",...)
            RewardName (string) - Nonfuel reward name
    Return: result (JSON data format string)
    Example:
        >>> GetNonFuelRewardsById("1", "15 cents DryStock")
        >>> GetNonFuelRewardsById("", "15 cents DryStock")
        >>> GetNonFuelRewardsById("1", "")
        '{"NonfuelRewards":
            {"NonfuelRewardDetails":
                {"NonfuelRewardId":"1","Name":"DryStockDiscount","TypeReward":"Optional",
                 "TypeRewardDescription":"Do you want to apply the discount?","DiscountMethod":"amountOff",
                 "Discount":"0.15","ItemType":"itemLine","CodeFormat":"plu","Code":"1","RewardLimit":"1",
                 "ReceiptText":""}}}'
    """
    result = ""
    if (NonfuelRewardId == "" and RewardName == ""):
        log.info("NonfuelRewardId or RewardName must be not empty")
        return result

    result = Loyalty().GetNonFuelRewardsById(NonfuelRewardId, RewardName)
    return result


def AddNonFuelReward(RewardName="15 cents DryStock", TypeReward="Optional", TypeRewardDescription="R u Sure?", DiscountMethod="amountOff", Discount="0.15", ItemType="merchandiseLine", CodeFormat="plu", CodeValue="1234", RewardLimit="10.10", ReceiptText="Dry stock 10 cents amount off"):
    """
    Add the new Non-Fuel reward details and returns NonfuelRewardId as string
    Args:   RewardName (string) - nonFuel reward name
            TypeReward (string) - Reward Type must be - {"Instant", "Optional"}
            TypeRewardDescription (string) - if reward type is "Instant" then this field is optional "" other wise description to dispaly at POS
            DiscountMethod (string) - Discount method value should be - {"amountOff", "percentOff", "newPrice"}
            Discount (string) - discount amount in any numeric value
            ItemType (string) - Item type value should be - {"itemLine", "merchandiseLine"}
            CodeFormat (string) - Code format value should be - { "upcA", "upcE", "ean8", "ean13", "plu", "gtin", "rss14", "none"}
            CodeValue (string) - Code value for selected code format
            RewardLimit (string) - Reward Limit in any numeric value
            ReceiptText (string)
    Return: result (string) - NonfuelRewardId
    Example:
        >>> AddNonFuelReward("15 cents DryStock", "Optional", "R u Sure?", "amountOff", "0.15", "merchandiseLine", "plu", "1234", "10.10", "Dry stock 10 cents amount off")
        "1"
    """
    result = ""
    if not(TypeReward == "Instant" or TypeReward == "Optional"):
        log.info("TypeReward (string) must be - {'Instant', 'Optional'}")
        return result
    if not(DiscountMethod == "amountOff" or DiscountMethod == "percentOff" or DiscountMethod == "newPrice"):
        log.info("DiscountMethod (string) - should be - {'amountOff', 'percentOff', 'newPrice'}")
        return result
    if not(ItemType == "itemLine" or ItemType == "merchandiseLine"):
        log.info("ItemType (string) - should be - {'itemLine', 'merchandiseLine'}")
        return result
    if not(CodeFormat == "upcA" or CodeFormat == "upcA" or CodeFormat == "upcE" or CodeFormat == "ean8" or CodeFormat == "ean13" or CodeFormat == "plu" or CodeFormat == "gtin" or CodeFormat == "rss14" or CodeFormat == "none"):
        log.info("CodeFormat (string) - should be - {'upcA', 'upcE', 'ean8', 'ean13', 'plu', 'gtin', 'rss14', 'none'}")
        return result

    result = Loyalty().AddNonFuelReward(RewardName, TypeReward, TypeRewardDescription, DiscountMethod, Discount, ItemType, CodeFormat, CodeValue, RewardLimit, ReceiptText)
    return result


def UpdateNonFuelReward(NonfuelRewardId="1", RewardName="15 cents DryStock", TypeReward="Optional", TypeRewardDescription="R u Sure?", DiscountMethod="amountOff", Discount="0.15", ItemType="merchandiseLine", CodeFormat="plu", CodeValue="1234", RewardLimit="10.10", ReceiptText="Dry stock 10 cents amount off"):
    """
    Update nonFuel level reward details based on NonfuelRewardId
    Args:   NonfuelRewardId (string) - any numeric value
            RewardName (string) - nonFuel reward name
            TypeReward (string) - Reward Type must be - {"Instant", "Optional"}
            TypeRewardDescription (string) - if reward type is "Instant" then this field is optional "" other wise description to dispaly at POS
            DiscountMethod (string) - Discount method value should be - {"amountOff", "percentOff", "newPrice"}
            Discount (string) - discount amount in any numeric value
            ItemType (string) - Item type value should be - {"itemLine", "merchandiseLine"}
            CodeFormat (string) - Code format value should be - { "upcA", "upcE", "ean8", "ean13", "plu", "gtin", "rss14", "none"}
            CodeValue (string) - Code value for selected code format
            RewardLimit (string) - Reward Limit in any numeric value
            ReceiptText (string)
    Return: result (bool) True/False
    Example:
        >>> UpdateNonFuelReward("1", "15 cents DryStock", "Optional", "R u Sure?", "amountOff", "0.15", "merchandiseLine", "plu", "1234", "10.10", "Dry stock 10 cents amount off")
        True
    """
    result = False
    if not(TypeReward == "Instant" or TypeReward == "Optional"):
        log.info("TypeReward (string) must be - {'Instant', 'Optional'}")
        return result
    if not(DiscountMethod == "amountOff" or DiscountMethod == "percentOff" or DiscountMethod == "newPrice"):
        log.info("DiscountMethod (string) - should be - {'amountOff', 'percentOff', 'newPrice'}")
        return result
    if not(ItemType == "itemLine" or ItemType == "merchandiseLine"):
        log.info("ItemType (string) - should be - {'itemLine', 'merchandiseLine'}")
        return result
    if not(CodeFormat == "upcA" or CodeFormat == "upcA" or CodeFormat == "upcE" or CodeFormat == "ean8" or CodeFormat == "ean13" or CodeFormat == "plu" or CodeFormat == "gtin" or CodeFormat == "rss14" or CodeFormat == "none"):
        log.info("CodeFormat (string) - should be - {'upcA', 'upcE', 'ean8', 'ean13', 'plu', 'gtin', 'rss14', 'none'}")
        return result

    result = Loyalty().UpdateNonFuelReward(NonfuelRewardId, RewardName, TypeReward, TypeRewardDescription, DiscountMethod, Discount, ItemType, CodeFormat, CodeValue, RewardLimit, ReceiptText)
    if (result == 'true'):
        result = True
    return result


def DeleteNonFuelReward(NonfuelRewardId="1"):
    """
    Delete the non-fuel reward based on the NonfuelRewardId
    Args: NonfuelRewardId (string)
    Returns: result (bool) True/False
    Example:
        >>> DeleteNonFuelReward("1")
        True
    """
    result = False
    result = Loyalty().DeleteNonFuelReward(NonfuelRewardId)
    if (result == 'true'):
        result = True
    return result


def GetFuelRewardsList():
    """
    Get the all available fuel rewards in JSON data format
    Args: None
    Return: result (JSON data format string)
    Example:
        >>> GetFuelRewardsList()
        '{"FuelRewards":
            {"FuelRewardDetails":[
                {"FuelRewardId":"1","Name":"FuelReward1","TypeReward":"Instant","TypeRewardDescription":"",
                 "DiscountMethod":"amountOffPPU","RewardLimit":"30","ReceiptText":"25 cents Discount",
                 "FuelGrades":
                    {"FuelGrade":[
                        {"FuelCode":"001","RewardAmount":"0.25"},{"FuelCode":"002","RewardAmount":"0.25"},
                        {"FuelCode":"003","RewardAmount":"0.25"},{"FuelCode":"004","RewardAmount":"0.25"},
                        {"FuelCode":"005","RewardAmount":"0.25"},{"FuelCode":"019","RewardAmount":"0.25"},
                        {"FuelCode":"020","RewardAmount":"0.25"}]
                    }},
                {"FuelRewardId":"2","Name":"FuelReward2 Optional","TypeReward":"Optional",
                 "TypeRewardDescription":"Would You Like to Save today?","DiscountMethod":"amountOffPPU",
                 "RewardLimit":"30","ReceiptText":"5 cenets Discount",
                 "FuelGrades":{
                    "FuelGrade":[
                        {"FuelCode":"001","RewardAmount":"0.05"},{"FuelCode":"002","RewardAmount":"0.05"}]}}]}}'
    """
    result = Loyalty().GetFuelRewardsList()
    return result


def GetFuelRewardsById(FuelRewardId="1", RewardName="FuelReward1"):
    """
    Get Fuel Reward by FuelRewardId or RewardName
    Args:   FuelRewardId (string) - Ids like ("1", "2", "3", "4",...)
            RewardName (string) - Nonfuel reward name
    Return: result (JSON data format string)
    Example:
        >>> GetFuelRewardsById("1", "FuelReward1")
        >>> GetFuelRewardsById("", "FuelReward1")
        >>> GetFuelRewardsById("1", "")
        '{"FuelRewardDetails":
            {"FuelRewardId":"1","Name":"FuelReward1","TypeReward":"Instant","TypeRewardDescription":"",
             "DiscountMethod":"amountOffPPU","RewardLimit":"30","ReceiptText":"25 cents Discount",
             "FuelGrades":
                {"FuelGrade":[
                    {"FuelCode":"001","RewardAmount":"0.25"},{"FuelCode":"002","RewardAmount":"0.25"},
                    {"FuelCode":"003","RewardAmount":"0.25"},{"FuelCode":"004","RewardAmount":"0.25"},
                    {"FuelCode":"005","RewardAmount":"0.25"},{"FuelCode":"019","RewardAmount":"0.25"},
                    {"FuelCode":"020","RewardAmount":"0.25"}]}}}'
    """
    result = ""
    if (FuelRewardId == "" and RewardName == ""):
        log.info("FuelRewardId or RewardName must be not empty")
        return result

    result = Loyalty().GetFuelRewardsById(FuelRewardId, RewardName)
    return result


def AddFuelRewards(RewardName="FuelReward1", TypeReward="Instant", TypeRewardDescription="", DiscountMethod="amountOffPPU", RewardLimit="30", ReceiptText="25 cents Discount", FuelGrades="001:0.25, 002:0.25, 003:0.25"):
    """
    Add new Fuel level reward details
    Args:   RewardName (string) - Fuel reward name
            TypeReward (string) - Reward Type must be - {"Instant", "Optional"}
            TypeRewardDescription (string) - if reward type is "Instant" then this field is optional "" other wise description to dispaly at POS
            DiscountMethod (string) - Discount method value should be - {"amountOffPPU", "newPrice"}
            RewardLimit (string) - Reward Limit in any numeric value
            ReceiptText (string)
            FuelGrades (string) - grade and its reward amount is seperated by ":" Example: 001:0.10. More than one grade is seperated by ","  Example: "001:0.25, 002:0.25, 003:0.25"
    Return: result (bool) True/False
    Example:
        >>> AddFuelRewards("FuelReward1", "Instant", "", "amountOffPPU", "30", "25 cents Discount", "001:0.25, 002:0.25, 003:0.25")
        "1"
    """
    result = ""
    if not(TypeReward == "Instant" or TypeReward == "Optional"):
        log.info("TypeReward (string) must be - {'Instant', 'Optional'}")
        return result
    if not(DiscountMethod == "amountOffPPU" or DiscountMethod == "newPrice"):
        log.info("DiscountMethod (string) - should be - {'amountOffPPU', 'newPrice'}")
        return result

    result = Loyalty().AddFuelRewards(RewardName, TypeReward, TypeRewardDescription, DiscountMethod, RewardLimit, ReceiptText, FuelGrades)
    return result


def UpdateFuelRewards(FuelRewardId="1", RewardName="FuelReward1", TypeReward="Instant", TypeRewardDescription="", DiscountMethod="amountOffPPU", RewardLimit="30", ReceiptText="25 cents Discount", FuelGrades="001:0.25, 002:0.25, 003:0.25"):
    """
    Update Fuel reward details based on FuelRewardId
    Args:   FuelRewardId (string)
            RewardName (string) - Fuel reward name
            TypeReward (string) - Reward Type must be - {"Instant", "Optional"}
            TypeRewardDescription (string) - if reward type is "Instant" then this field is optional "" other wise description to dispaly at POS
            DiscountMethod (string) - Discount method value should be - {"amountOffPPU", "newPrice"}
            RewardLimit (string) - Reward Limit in any numeric value
            ReceiptText (string)
            FuelGrades (string) - grade and its reward amount is seperated by ":" Example: 001:0.10. More than one grade is seperated by ","  Example: "001:0.25, 002:0.25, 003:0.25"
    Return: result (bool) True/False
    Example:
        >>> UpdateFuelRewards("1", "FuelReward1", "Instant", "", "amountOffPPU", "30", "25 cents Discount", "001:0.25, 002:0.25, 003:0.25")
        True
    """
    result = False
    if not(TypeReward == "Instant" or TypeReward == "Optional"):
        log.info("TypeReward (string) must be - {'Instant', 'Optional'}")
        return result
    if not(DiscountMethod == "amountOffPPU" or DiscountMethod == "newPrice"):
        log.info("DiscountMethod (string) - should be - {'amountOffPPU', 'newPrice'}")
        return result

    result = Loyalty().UpdateFuelRewards(FuelRewardId, RewardName, TypeReward, TypeRewardDescription, DiscountMethod, RewardLimit, ReceiptText, FuelGrades)
    if (result == 'true'):
        result = True
    return result


def DeleteFuelReward(FuelRewardId="1"):
    """
    Delete the fuel reward based on the FuelRewardId
    Args: FuelRewardId (string)
    Returns: result (bool) True/False
    Example:
        >>> DeleteFuelReward("1")
        True
    """
    result = False
    result = Loyalty().DeleteFuelReward(FuelRewardId)
    if (result == 'true'):
        result = True
    return result


def AddFuelGrades(FuelRewardId, FuelGrades="001:0.25, 002:0.25, 003:0.25"):
    """
    Add new Fuel grade with code and amount for fuel reward details
    Args:   FuelRewardId (string) - Fuel Reward ID
            FuelGrades (string) - Fuel grades, grade and its reward amount is seperated by ":" Example: 001:0.10. More than one grade is seperated by ","  Example: "001:0.10, 002:0.10, 003:0.10"
    Return: result (bool) True/False
    Example:
        >>> AddFuelGrades("1", "001:0.25, 002:0.25, 003:0.25")
        True
    """
    result = False
    result = Loyalty().AddFuelGrades(FuelRewardId, FuelGrades)
    if (result == 'true'):
        result = True
    return result


def GetFuelGradesById(FuelRewardId="1", RewardName="FuelReward1"):
    """
    Get Fuel grade details by FuelRewardId or RewardName
    Args:   FuelRewardId (string) - Ids like ("1", "2", "3", "4",...)
            RewardName (string) - Fuel reward name
    Return: result (JSON data format string)
    Example:
        >>> GetFuelGradesById("1", "FuelReward1")
        >>> GetFuelGradesById("", "FuelReward1")
        >>> Loyalty().GetFuelGradesById("1", "")
        '{"FuelGrades":{
            "FuelGrade":[
                {"FuelCode":"001","RewardAmount":"0.25"},{"FuelCode":"002","RewardAmount":"0.25"},
                {"FuelCode":"003","RewardAmount":"0.25"},{"FuelCode":"004","RewardAmount":"0.25"},
                {"FuelCode":"005","RewardAmount":"0.25"},{"FuelCode":"019","RewardAmount":"0.25"},
                {"FuelCode":"020","RewardAmount":"0.25"}]}}'
    """
    result = ""
    if (FuelRewardId == "" and RewardName == ""):
        log.info("FuelRewardId or RewardName must be not empty")
        return result

    result = Loyalty().GetFuelGradesById(FuelRewardId, RewardName)
    return result


def AssignTransactionReward(LoyatyID="1", TransactionID="1", RewardName="20 cents Trans.Rwd"):
    """
    Assign transaction level rewards to loyalty ID based on TransactionID or RewardNames
    Args:   LoyatyID (string) - Ids like ("1", "2", "3", "4",...)
            TransactionID (string) - Ids like ("1", "2", "3", "4",...)
            RewardName (string) - Transaction reward name
    Return: result (bool) True/False
    Example:
        >>> AssignTransactionReward("1", "1", "20 cents Trans.Rwd")
        >>> AssignTransactionReward("1", "", "20 cents Trans.Rwd")
        >>> AssignTransactionReward("1", "1", "")
        True
    """
    result = False

    if (TransactionID == "" and RewardName == ""):
        log.info("TransactionID or RewardName must be not empty")
        return result

    result = Loyalty().AssignTransactionReward(LoyatyID, TransactionID, RewardName)
    if (result == 'true'):
        result = True
    return result


def AssignNonFuelReward(LoyatyID="1", NonFuelID="1", RewardName="15 cents DryStock"):
    """
    Assign nonFuel rewards to loyalty ID based on NonFuelID or RewardNames
    Args:   LoyatyID (string) - Ids like ("1", "2", "3", "4",...)
            NonFuelID (string) - Ids like ("1", "2", "3", "4",...)
            RewardName (string) - nonFuel reward name
    Return: result (bool) True/False
    Example:
        >>> AssignNonFuelReward("1", "1", "15 cents DryStock")
        >>> AssignNonFuelReward("1", "", "15 cents DryStock")
        >>> AssignNonFuelReward("1", "1", "")
        True
    """
    result = False

    if (NonFuelID == "" and RewardName == ""):
        log.info("NonFuelID or RewardName must be not empty")
        return result

    result = Loyalty().AssignNonFuelReward(LoyatyID, NonFuelID, RewardName)
    if (result == 'true'):
        result = True
    return result


def AssignFuelReward(LoyatyID="1", FuelID="1", RewardName="15 cents DryStock"):
    """
    Assign Fuel rewards to loyalty ID based on FuelID or RewardNames
    Args:   LoyatyID (string) - Ids like ("1", "2", "3", "4",...)
            FuelID (string) - Ids like ("1", "2", "3", "4",...)
            RewardName (string) - Fuel reward name
    Return: result (bool) True/False
    Example:
        >>> AssignFuelReward("1", "1", "15 cents DryStock")
        >>> AssignFuelReward("1", "", "15 cents DryStock")
        >>> AssignFuelReward("1", "1", "")
        True
    """
    result = False

    if (FuelID == "" and RewardName == ""):
        log.info("FuelID or RewardName must be not empty")
        return result

    result = Loyalty().AssignFuelReward(LoyatyID, FuelID, RewardName)
    if (result == 'true'):
        result = True
    return result


def UnAssignTransactionReward(LoyatyID="1", TransactionID="1", RewardName="20 cents Trans.Rwd"):
    """
    UnAssign transaction level rewards to loyalty ID based on TransactionID or RewardNames
    Args:   LoyatyID (string) - Ids like ("1", "2", "3", "4",...)
            TransactionID (string) - Ids like ("1", "2", "3", "4",...)
            RewardName (string) - Transaction reward name
    Return: result (bool) True/False
    Example:
        >>> UnAssignTransactionReward("1", "1", "20 cents Trans.Rwd")
        >>> UnAssignTransactionReward("1", "", "20 cents Trans.Rwd")
        >>> UnAssignTransactionReward("1", "1", "")
        True
    """
    result = False

    if (TransactionID == "" and RewardName == ""):
        log.info("TransactionID or RewardName must be not empty")
        return result

    result = Loyalty().UnAssignTransactionReward(LoyatyID, TransactionID, RewardName)
    if (result == 'true'):
        result = True
    return result


def UnAssignNonFuelReward(LoyatyID="1", NonFuelID="1", RewardName="15 cents DryStock"):
    """
    UnAssign nonFuel rewards to loyalty ID based on NonFuelID or RewardNames
    Args:   LoyatyID (string) - Ids like ("1", "2", "3", "4",...)
            NonFuelID (string) - Ids like ("1", "2", "3", "4",...)
            RewardName (string) - nonFuel reward name
    Return: result (bool) True/False
    Example:
        >>> UnAssignNonFuelReward("1", "1", "15 cents DryStock")
        >>> UnAssignNonFuelReward("1", "", "15 cents DryStock")
        >>> UnAssignNonFuelReward("1", "1", "")
        True
    """
    result = False

    if (NonFuelID == "" and RewardName == ""):
        log.info("NonFuelID or RewardName must be not empty")
        return result

    result = Loyalty().UnAssignNonFuelReward(LoyatyID, NonFuelID, RewardName)
    if (result == 'true'):
        result = True
    return result


def UnAssignFuelReward(LoyatyID="1", FuelID="1", RewardName="15 cents DryStock"):
    """
    UnAssign Fuel rewards to loyalty ID based on FuelID or RewardNames
    Args:   LoyatyID (string) - Ids like ("1", "2", "3", "4",...)
            FuelID (string) - Ids like ("1", "2", "3", "4",...)
            RewardName (string) - Fuel reward name
    Return: result (bool) True/False
    Example:
        >>> UnAssignFuelReward("1", "1", "15 cents DryStock")
        >>> UnAssignFuelReward("1", "", "15 cents DryStock")
        >>> UnAssignFuelReward("1", "1", "")
        True
    """
    result = False

    if (FuelID == "" and RewardName == ""):
        log.info("FuelID or RewardName must be not empty")
        return result

    result = Loyalty().UnAssignFuelReward(LoyatyID, FuelID, RewardName)
    if (result == 'true'):
        result = True
    return result


def UnAssignAllTransRewardsByLoyalty(LoyatyID="1"):
    """
    UnAssign all transaction level rewards by loyalty ID
    Args:   LoyatyID (string) - Ids like ("1", "2", "3", "4",...)
    Return: result (bool) True/False
    Example:
        >>> UnAssignAllTransRewardsByLoyalty("1")
        True
    """
    result = False
    result = Loyalty().UnAssignAllTransRewardsByLoyalty(LoyatyID)
    if (result == 'true'):
        result = True
    return result


def UnAssignAllNonFuelRewardsByLoyalty(LoyatyID="1"):
    """
    UnAssign all nonFuel rewards by loyalty ID
    Args:   LoyatyID (string) - Ids like ("1", "2", "3", "4",...)
    Return: result (bool) True/False
    Example:
        >>> UnAssignAllNonFuelRewardsByLoyalty("1")
        True
    """
    result = False
    result = Loyalty().UnAssignAllNonFuelRewardsByLoyalty(LoyatyID)
    if (result == 'true'):
        result = True
    return result


def UnAssignAllFuelRewardsByLoyalty(LoyatyID="1"):
    """
    UnAssign all Fuel rewards by loyalty ID
    Args:   LoyatyID (string) - Ids like ("1", "2", "3", "4",...)
    Return: result (bool) True/False
    Example:
        >>> UnAssignAllFuelRewardsByLoyalty("1")
        True
    """
    result = False
    result = Loyalty().UnAssignAllFuelRewardsByLoyalty(LoyatyID)
    if (result == 'true'):
        result = True
    return result


def AssignStatusMessages(LoyatyID="1", DisplayMessages="dispaly1, display2", ReceiptMessages="receipt1, receipt2"):
    """
    Assign status messages by loyalty ID
    Args:   LoyatyID (string) - Ids like ("1", "2", "3", "4",...)
            DisplayMessages (string) - any string, if we need to add multiple display messages should be seperate by ","
            ReceiptMessages (string) - any string, if we need to add multiple receipt messages should be seperate by ","
    Return: result (bool) True/False
    Example:
        >>> AssignStatusMessages("1", "dispaly1, display2", "receipt1, receipt2")
        True
    """
    result = False
    result = Loyalty().AssignStatusMessages(LoyatyID, DisplayMessages, ReceiptMessages)
    if (result == 'true'):
        result = True
    return result


def AssignLoyaltyPrompts(LoyatyID="1", PromptID="1", PromptName="Prompt1"):
    """
    Assign Prompts by loyalty ID
    Args:   LoyatyID (string) - Ids like ("1", "2", "3", "4",...)
            PromptID (string) - Ids like ("1", "2", "3", "4",...)
            PromptName (string) - any string
    Return: result (bool) True/False
    Example:
        >>> AssignLoyaltyPrompts("1", "1", "Prompt1")
        >>> AssignLoyaltyPrompts("1", "1", "")
        >>> AssignLoyaltyPrompts("1", "", "Prompt1")
        True
    """
    result = False

    if (PromptID == "" and PromptName == ""):
        log.info("PromptID or PromptName must be not empty")
        return result

    result = Loyalty().AssignLoyaltyPrompts(LoyatyID, PromptID, PromptName)
    if (result == 'true'):
        result = True
    return result


def DeleteLoyaltyPromptsById(LoyatyID="1", PromptID="1", PromptName="Prompt1"):
    """
    UnAssign Prompts by loyalty ID
    Args:   LoyatyID (string) - Ids like ("1", "2", "3", "4",...)
            PromptID (string) - Ids like ("1", "2", "3", "4",...)
            PromptName (string) - any string
    Return: result (bool) True/False
    Example:
        >>> DeleteLoyaltyPromptsById("1", "1", "Prompt1")
        >>> DeleteLoyaltyPromptsById("1", "1", "")
        >>> DeleteLoyaltyPromptsById("1", "", "Prompt1")
        True
    """
    result = False

    if (PromptID == "" and PromptName == ""):
        log.info("PromptID or PromptName must be not empty")
        return result

    result = Loyalty().DeleteLoyaltyPromptsById(LoyatyID, PromptID, PromptName)
    if (result == 'true'):
        result = True
    return result


def DeleteAllLoyaltyPrompts(LoyatyID="1"):
    """
    UnAssign all Prompts by loyalty ID
    Args:   LoyatyID (string) - Ids like ("1", "2", "3", "4",...)
    Return: result (bool) True/False
    Example:
        >>> DeleteAllLoyaltyPrompts("1")
        True
    """
    result = False
    result = Loyalty().DeleteAllLoyaltyPrompts(LoyatyID)
    if (result == 'true'):
        result = True
    return result