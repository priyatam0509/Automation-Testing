__author__ = 'Joe Paxton'

import logging, time, datetime, time, os, csv
#from logging.handlers import RotatingFileHandler
import inspect

"""
logger.py:
    *Logging class that logs information based on different severity levels for each Test Case
    *Places ALL of the logging information into an event log and ONLY errors into a error log
    *The ERRORs will have the testFile, lineNumber, line, and functionName it failed at in logs
    *Writes the runtime of the script into an event log and Windows Registry
    *Graphs the runtime for each Test Case into a bar chart
    *Generates a CSV file from the event log

Original Author: Joe Paxton
Created on: 12/2/2016

Modified by: 
Modified on: 
"""

class Logger:
    def __init__(self, loggerName, logPath, level=logging.DEBUG, debug = False):
        """
        Returns a Logger object that sets the format and handlers for the file and console logging

        @param: loggerName  the logger's name
        @param: logPath     the path for the loggerName
        @param: level       the severity level for the information containted in the loggerName
        """
        #Full path to pass the log file into handler
        fullPath = str(logPath) + "\\" + str(loggerName)
        
        #Returns a singelton logger
        self.loggerName = logging.getLogger(loggerName)

        #Creates the format for all of the logs
        FORMAT = '[%(asctime)s]: **[%(levelname)s]** %(message)s'
        self.formatLogger = logging.Formatter(FORMAT, datefmt='%m/%d/%Y %I:%M:%S %p')

        #Creates the file and stream handlers
        self.fileHandler = logging.FileHandler(fullPath, mode='a')
        self.streamHandler = logging.StreamHandler()

        #Sets the format for console and log files
        self.fileHandler.setFormatter(self.formatLogger)
        self.streamHandler.setFormatter(self.formatLogger)
        
        #We need this check because it will add these handlers to the instance everytime Logger is called
        if not self.loggerName.handlers:
            self.loggerName.setLevel(level)
            
            #Adds handlers to console and file logging
            self.loggerName.addHandler(self.fileHandler)
            if debug:
                self.loggerName.addHandler(self.streamHandler)

    def debug(self, message):
        """
        Returns logging information that may provide steps to future errors or warnings
        @param: message  the message you want to log when calling Logger's debug function
        """
        self.loggerName.debug(message)
        self.fileHandler.close()
        return
        
    def info(self, message):
        """
        Returns logging information that contains events under normal circumstances

        @param: message  the message you want to log when calling Logger's info function
        """
        self.loggerName.info(message)
        self.fileHandler.close()
        return

    def warning(self, message):
        """
        Returns logging information that may have the potential to cause an error

        @param: message  the message you want to log when calling Logger's warning function
        """
        self.loggerName.warn(message)
        self.fileHandler.close()
        return

    def error(self, message):
        """
        Returns logging information that contains unexpected failures during program execution

        @param: message  the message you want to log when calling Logger's error function
        """
        self.loggerName.error(message)
        self.fileHandler.close()
        return

    def critical(self, message):
        """
        Returns logging information that contains a system failure that should be investigated immediately

        @param: message  the message you want to log when calling Logger's critical function
        """
        self.loggerName.critical(message)
        self.fileHandler.close()
        return
    
    def exception(self, message):
        """
        Returns logging information that contains an exception in the program, usually logs Traceback error
        Places the funcName, lineNo, and lineError from test script into both event and error logs

        @param: message  the message you want to log when calling Logger's exception function
        """

        #gets the caller frame information from callee - get info from scripter
        (frame, fileName, lineNo, funcName, lineError, index) = inspect.getouterframes(inspect.currentframe())[2]
        
        #goes into the event log file
        output = f"{message}\n"
        output += f'Error occured at:\n'
        output += f'\tModule Name:\t{fileName}\n'
        output += f'\tFunction name:\t{funcName}()\n'
        output += f'\tLine number:\t{lineNo}\n'
        output += f'\tLine failure:\t{lineError}\n\n'
        output += f'Full traceback:'
        self.loggerName.exception(output)
        self.fileHandler.close()

        return
   
    def script_start(self, scriptName):
        """
        Returns the start time of the Test Case into the event logger with the severity level - INFO

        @param: scriptName the test case being ran
        """
        self.startTime = datetime.datetime.now().replace(microsecond=0)
        self.info("-----------------------------------------------")
        self.info(f"| STARTING {scriptName}: {self.startTime} |")
        self.info("-----------------------------------------------")
        return
    
    def script_end(self):
        """
        Returns the runtime of script to the event log in seconds
        """
        self.runTime = datetime.datetime.now().replace(microsecond=0) - self.startTime
        out_date = datetime.datetime.now().replace(microsecond=0)
        self.info("------------------------------------------")
        self.info(f'| FINISHED SCRIPT AT: {out_date}|')
        self.info("------------------------------------------")
        self.info("---------------------------")
        self.info(f'| SCRIPT RUN TIME: {self.runTime} |')
        self.info("---------------------------")
        return

    def generate_log_to_csv(self, loggerName, logPath, scriptName):
        """
        Parses through the event log and generates a CSV file out of it

        @param: loggerName  the name of the logger
        @param: logPath     the path of the logs
        @param: scriptName  the name of the test case script
        """
        fullPath = str(logPath) + "\\" + str(loggerName)
        inputFile = csv.reader(open(fullPath, 'rb'), delimiter='\t')
        outputFile = csv.writer(open("..\\Mini_Regression\\CSV\\" + str(scriptName) + "_Results.csv", 'wb'))
        outputFile.writerow( ('Time', 'Level', 'Message') )
        outputFile.writerows(inputFile)
        return