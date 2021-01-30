"""
Description: This is a module that allows us the ability to run commands as another user.

Do not modify this file unless you are familiar with the windows subsystem.

This file is based off of a script for salt, which was based off of a solution from
    http://stackoverflow.com/questions/29566330

Created on: 8/31/17
Created by: Cory Henderlite

Last modified by: Conor McWain
Last modified on: 09/19/19
"""
__author__ = 'Cory Henderlite'

import ctypes
from ctypes import wintypes
import win32api
import win32con
import msvcrt
import os
import signal
import time
import logging

NULL = 0
TRUE = 1
FALSE = 0
k32 = ctypes.windll.kernel32
ad32 = ctypes.windll.advapi32

WORD   = ctypes.c_ushort
DWORD  = ctypes.c_uint
LPSTR  = ctypes.c_char_p
LPBYTE = LPSTR
HANDLE = DWORD

log = logging.getLogger()

def run_as(cmd, user="passporttech", domain="passport", password="911Tech", ignore_stdout=False):
    """
    @Creator: Cory Henderlite
    @Name: run_as
    @Description: run cmd as a user. Defaulted to passporttech
    @params:
        >cmd (string): The command to run
        >user (string:passporttech": The user to run as
        >domain (string:passport): The domain to run in
        >password (string:911Tech): The password to use
        >ignore_stdout (bool:False): Ignores stdout which closes 
            the cmd window
    @return:
        >dictionary: The 'pid' of the comand ran and the 
            'output' of the command. 'pid' is -1 on
            failure
    """
    r, w = create_pipe(inherit_read=False, inherit_write=True)
    startup_info              = STARTUP_INFO()
    startup_info.cb           = ctypes.sizeof(STARTUP_INFO)
    startup_info.lpReserved   = 0
    startup_info.lpDesktop    = 0
    startup_info.lpTitle      = 0
    startup_info.dwFlags      = win32con.STARTF_USESTDHANDLES
    startup_info.cbReserved2  = 0
    startup_info.lpReserved2  = 0
    startup_info.hStdOutput   = w

    cmd = "cmd.exe /C %s"%(cmd)
    ret = {'pid': -1}
    ret['output'] = ""
    proc = None
    try:
        proc = create_process_with_logon(user,
                                         domain, 
                                         password, 
                                         lpCommandLine=cmd, 
                                         lpStartupInfo=startup_info)
    except Exception as e:
        k32.CloseHandle(w)
        k32.CloseHandle(r)
        if proc != None:
            k32.CloseHandle(proc.hThread)
        else:
            pass
        ret['output'] = e
        return ret
     
    k32.CloseHandle(w)
    k32.CloseHandle(proc.hThread)
    ret['pid'] = proc.dwProcessId

    if ignore_stdout:
        k32.CloseHandle(r)
        ret['output'] = "Ignored"        
        run_as("tskill " + str(ret['pid']))
    else:
        fd_out = msvcrt.open_osfhandle(r, os.O_RDONLY | os.O_TEXT)
        with os.fdopen(fd_out, 'r') as out:
            ret['output'] = out.read()


    return ret

def run_sqlcmd(cmd, 
               database=None, 
               cmdshell=True, 
               destination="passporteps",
               user="EDH", 
               password="EDH", 
               domain="passport",
               ignore_stdout=False):
    """
    @Creator: Cory Henderlite
    @Name: run_sqlcmd
    @Description: run sqlcmd queries. Defaults to user EDH
    @params:
        >cmd (string): The command to run
        >database (string:None): The database to use
        >cmdshell (bool:True): Whether to use xp_cmdshell or not
        >user (string:EDH): The user to run as
        >password (string:EDH): The password to use
        >domain (string:passport): The domain to run in
        >ignore_stdout (bool:False): Ignores stdout which closes the cmd window
    @return:
        >dictionary: The 'pid' of the comand ran and the 
            'output' of the command. 'pid' is -1 on
            failure
    """
    if cmdshell:
        return run_as("sqlcmd.exe -S %s -l 50 -E -Q \"xp_cmdshell \'%s\'\""%(destination, cmd),
                      user=user, 
                      password=password,
                      domain=domain,
                      ignore_stdout=ignore_stdout)
    else:
        if database is None:
            database="network"
        return run_as("sqlcmd.exe -S %s -l 50 -d %s -E -Q \"%s\""%(destination, database, cmd),
                      user=user, 
                      password=password,
                      domain=domain,
                      ignore_stdout=ignore_stdout)

def parse_output(result):
    """
    Parse the result of the SQLCMD

    Args:
        result (dict): The dictionary value that gets returned by the run_sqlcmd function

    Returns:
        output (list): A list comprised of the output returned by the run_sqlcmd()
    """
    output = result['output']
    parsed = output.split('\n')
    output = []
    for _line in parsed:
        output.append(_line.strip())
        log.debug(_line)
    return output

def error_check(output_list):
    """
    Check the result of the SQLCMD for errors

    Args:
        output_list (list): The list value returned by the parse_output function
        
    Returns:
        True/False (bool): Returns False if an error message is found
    """
    #NOTE: Add error messages as you come across them
    #keys = error messages we are looking for
    #values = what we log if the key is found
    known_errors = {
        "File Not Found":"File was not found",
        "No such host is known":"Failed to connect to Client"
    }
    #Verify the command ran without errors
    for _line in output_list:
        for key, value in known_errors.items():
            if key in _line:
                log.error(value)
                return False
    return True

"""#########################################################################
SUPPORT FUNCTIONS AND CLASSES:
They are not meant to be used outside of this file.
########################################################################"""

class PROCESS_INFO(ctypes.Structure):
    """
    Creator: Cory Henderlite
    Name: PROCESS_INFO
    Description: A class that wraps around the structure for 
        processinformation in windows
    """
    _pack_   = 1
    _fields_ = [
            ('hProcess',    HANDLE),
            ('hThread',     HANDLE),
            ('dwProcessId', DWORD),
            ('dwThreadId',  DWORD),
    ]

class STARTUP_INFO(ctypes.Structure):
    """
    Creator: Cory Henderlite
    Name: STARTUP_INFO 
    Description: A class that wraps around the structure for 
       startupinfo in windows
    """
    _pack_   = 1
    _fields_ = [
            ('cb',              DWORD),
            ('lpReserved',      DWORD),     # LPSTR
            ('lpDesktop',       LPSTR),
            ('lpTitle',         LPSTR),
            ('dwX',             DWORD),
            ('dwY',             DWORD),
            ('dwXSize',         DWORD),
            ('dwYSize',         DWORD),
            ('dwXCountChars',   DWORD),
            ('dwYCountChars',   DWORD),
            ('dwFillAttribute', DWORD),
            ('dwFlags',         DWORD),
            ('wShowWindow',     WORD),
            ('cbReserved2',     WORD),
            ('lpReserved2',     DWORD),     # LPBYTE
            ('hStdInput',       DWORD),
            ('hStdOutput',      DWORD),
            ('hStdError',       DWORD),
    ]

def create_pipe(inherit_read=False, inherit_write=False):
    """
    @Creator: Cory Henderlite
    @Name: create_pipe
    @Description: creates a pipe between processes to allow 
                  interprocess communication to happen.
    @params:
        >inherit_read (bool:False): make the 'read' pipe be inheritable
        >inherit_write (bool:False): make the 'write' pipe be inheritable
    @return:
        >touple: the read and write pipes created (r,w)
    """
    r = wintypes.HANDLE()
    w = wintypes.HANDLE()
    k32.CreatePipe(ctypes.byref(r), 
                   ctypes.byref(w),
                   None, 
                   0)
    if inherit_read:
        k32.SetHandleInformation(r, 
                                 win32con.HANDLE_FLAG_INHERIT, 
                                 win32con.HANDLE_FLAG_INHERIT)
    if inherit_write:
        k32.SetHandleInformation(w, 
                                 win32con.HANDLE_FLAG_INHERIT, 
                                 win32con.HANDLE_FLAG_INHERIT)
    return r.value, w.value    

def create_process_with_logon(lpUsername = None,
                              lpDomain = None, 
                              lpPassword = None, 
                              lpCommandLine = None,
                              lpStartupInfo = None,
                              dwLogonFlags = 0, 
                              lpApplicationName = None,
                              dwCreationFlags = 0, 
                              lpEnvironment = None,
                              lpCurrentDirectory = None):
    """
    @Creator: Cory Henderlite
    @Name: create_process_with_logon
    @Description: Creates a new process with the supplied
                  login information.
    @params:
        >lpUsername (string:None): The username to login as
        >lpDomain (string:None): The domain to login with
        >lpPassword (string:None): The password to login with
        >lpCommandLine (string:None): The command to run
        >lpStartupInfo (STARTUP_INFO:None): A STARTUP_INFO instance to use
        >dwLogonFlags (int:None): Logon flags
        >lpApplicationName (string:None): The application Name
        >dwCreationFlags (int:None) : Creation flags to use
        >lpEnvironment (string:None): The environment settings desired
        >lpCurrentDirrectory (string:None): The working directory
    @return:
        >PROCESS_INFO object: Object containing process info
    """
    if not lpUsername:
        lpUsername          = NULL
    else:
        lpUsername          = ctypes.c_wchar_p(lpUsername)
    if not lpDomain:
        lpDomain            = NULL
    else:
        lpDomain            = ctypes.c_wchar_p(lpDomain)
    if not lpPassword:
        lpPassword          = NULL
    else:
        lpPassword          = ctypes.c_wchar_p(lpPassword)
    if not lpApplicationName:
        lpApplicationName   = NULL
    else:
        lpApplicationName   = ctypes.c_wchar_p(lpApplicationName)
    if not lpCommandLine:
        lpCommandLine       = NULL
    else:
        lpCommandLine       = ctypes.create_unicode_buffer(lpCommandLine)
    if not lpEnvironment:
        lpEnvironment       = NULL
    else:
        lpEnvironment       = ctypes.c_wchar_p(lpEnvironment)
    if not lpCurrentDirectory:
        lpCurrentDirectory  = ctypes.c_wchar_p("C:\\Windows\\system32")
    else:
        lpCurrentDirectory  = ctypes.c_wchar_p(lpCurrentDirectory)
    if not lpStartupInfo:
        lpStartupInfo              = STARTUP_INFO()
        lpStartupInfo.cb           = ctypes.sizeof(STARTUP_INFO)

    dwCreationFlags |= win32con.CREATE_UNICODE_ENVIRONMENT

    lpProcessInformation              = PROCESS_INFO()
    lpProcessInformation.hProcess     = -1 
    lpProcessInformation.hThread      = -1
    lpProcessInformation.dwProcessId  = 0
    lpProcessInformation.dwThreadId   = 0
    success = ad32.CreateProcessWithLogonW(lpUsername,
                                           lpDomain,
                                           lpPassword,
                                           dwLogonFlags,
                                           lpApplicationName,
                                           ctypes.byref(lpCommandLine),
                                           dwCreationFlags,
                                           lpEnvironment,
                                           lpCurrentDirectory,
                                           ctypes.byref(lpStartupInfo),
                                           ctypes.byref(lpProcessInformation))
    if success == FALSE:
        raise ctypes.WinError()
    return lpProcessInformation

if __name__ == '__main__':
    print(run_as("notepad"))
