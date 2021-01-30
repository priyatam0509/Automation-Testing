'''
Created on Apr 17, 2018

@author: ejuan
'''

import socket
import sys
import logging
import os

# Log object
log = logging.getLogger()

class IPScanner():

    def __init__(self, ip="127.0.0.1"):
        """
        Initializes IP barcode scanner local to the MWS.
        """
        # On Express Lane, the IP will be 10.5.48.2
        self.TCP_IP = ip # assumes that this will be run from the MWS
        self.TCP_PORT = 10001
        
        # TODO : We will wait up to 10 seconds everytime any module is imported that needs this. Need to think of a solution for this.
        self.scanner_time_out = 10  # seconds

        # Opens a connection so the MWS can connects to it on port 10001
        # self.open_connection()

    def open_connection(self):
        """
        Attempts to connect to the MWS and waits `self.scanner_time_out` amount of seconds for success
        Args:
            None
        Return:
            True, if success; otherwise, False
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(self.scanner_time_out)  # seconds

            s.bind((self.TCP_IP, self.TCP_PORT))
            s.listen(1)

            log.debug("Listening for connections on : " +
                    str(self.TCP_IP) + ":" + str(self.TCP_PORT))
            self.conn, addr = s.accept()
            log.debug("Connection from: " + str(addr))
            return True

        except socket.error as e:
            log.warning(f"Failed to create socket: {e}")     
            return False       

        except socket.timeout:
            log.warning(f"No connections made in {self.scanner_time_out} seconds")
            return False        
   
    def scan(self, barcode):
        """
        Scans the bar
         that the connection was established and try to send the data
        """
        connected = os.system(f"netstat -ano | findstr {self.TCP_PORT}")
        if connected != 0: # Not connected
            self.open_connection()
        try:
            self.barcode = barcode + '\r'
            log.debug("Attempting to send:" + barcode)
            self.conn.send(str.encode(self.barcode))
            log.debug("scanner information sent")
            return True

        except AttributeError:
            '''In case that the connection was not established before
                re-attempt to connect'''
            if self.open_connection():
                try:
                    log.debug("Attemting to send:" + barcode)
                    self.conn.send(str.encode(self.barcode))
                    log.debug("scanner information sent")
                    return True
                except:
                    return False
            else:
                # Return False if the MWS does not connect to the Scanner
                return False

        except:
            # Return False if the scanner can not send the data
            return False
