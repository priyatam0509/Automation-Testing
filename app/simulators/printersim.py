"""
Receipt printer simulator for Passport POS.
Converted from C# code originally written by Lucas Daniel.
It supports both serial and TCP/IP communications,
can send printer statuses, and stores the last printed receipt as plain text.
"""

from enum import IntFlag
from app import runas, system, constants
from pywinauto.keyboard import send_keys
import serial, logging, threading, sys, socket, time, winreg

class PrinterStatus(IntFlag):
    DRAWER_OPEN = 0x04
    OFFLINE = 0x08
    COVER_OPEN = 0x20
    PAPER_FEEDING = 0x40

    ONLINE_RECOVERY = 0x0100
    PAPER_FEED_PUSHED = 0x0200
    RECOVERABLE_ERROR = 0x0400
    AUTO_CUT_ERROR = 0x0800
    UNRECOVERABLE_ERROR = 0x2000
    AUTO_RECOVERABLE_ERROR = 0x4000

    PAPER_NEAR_END = 0x030000
    PAPER_OUT = 0x0C0000

class PrinterSim():
    # Public variables
    ip_mode = False
    port = None
    connected = False
    receipt_text = ""

    # Private variables
    _serial_port = None
    _tcp_conn = None

    _status = 0
    _storing_graphics = False
    _status_enabled = False
    _graphics_bytes = 0

    _graphics_data = b""
    _data = ""
    _encoding = "UTF-8"

    _cut_position = -1

    _data_processor = None
    _stop_flag = False

    """
    Printer status properties. Get/set these as booleans.
    """
    @property
    def cover_open(self):
        return (self._status & PrinterStatus.COVER_OPEN) != 0

    @cover_open.setter
    def cover_open(self, value):
        if value != self.cover_open:
            if value:
                self._status |= PrinterStatus.COVER_OPEN
            else:
                self._status &= ~PrinterStatus.COVER_OPEN

            self._send_status()

    @property
    def drawer_open(self):
        return (self._status & PrinterStatus.DRAWER_OPEN) != 0

    @drawer_open.setter
    def drawer_open(self, value):
        if value != self.drawer_open:
            if value:
                self._status |= PrinterStatus.DRAWER_OPEN
            else:
                self._status &= ~PrinterStatus.DRAWER_OPEN

            self._send_status()

    @property
    def auto_recoverable_error(self):
        return (self._status & PrinterStatus.AUTO_RECOVERABLE_ERROR) != 0

    @auto_recoverable_error.setter
    def auto_recoverable_error(self, value):
        if value != self.auto_recoverable_error:
            if value:
                self._status |= PrinterStatus.AUTO_RECOVERABLE_ERROR
            else:
                self._status &= ~PrinterStatus.AUTO_RECOVERABLE_ERROR

            self._send_status()

    @property
    def unrecoverable_error(self):
        return (self._status & PrinterStatus.UNRECOVERABLE_ERROR) != 0

    @unrecoverable_error.setter
    def unrecoverable_error(self, value):
        if value != self.unrecoverable_error:
            if value:
                self._status |= PrinterStatus.UNRECOVERABLE_ERROR
            else:
                self._status &= ~PrinterStatus.UNRECOVERABLE_ERROR

            self._send_status()

    @property
    def auto_cut_error(self):
        return (self._status & PrinterStatus.AUTO_CUT_ERROR) != 0

    @auto_cut_error.setter
    def auto_cut_error(self, value):
        if value != self.auto_cut_error:
            if value:
                self._status |= PrinterStatus.AUTO_CUT_ERROR
            else:
                self._status &= ~PrinterStatus.AUTO_CUT_ERROR

            self._send_status()

    @property
    def paper_out(self):
        return (self._status & PrinterStatus.PAPER_OUT) != 0

    @paper_out.setter
    def paper_out(self, value):
        if value != self.paper_out:
            if value:
                self._status |= PrinterStatus.PAPER_OUT
            else:
                self._status &= ~PrinterStatus.PAPER_OUT

            self.send_status()

    @property
    def paper_near_end(self):
        return (self._status & PrinterStatus.PAPER_NEAR_END) != 0

    @paper_near_end.setter
    def paper_near_end(self, value):
        if value != self.paper_near_end:
            if value:
                self._status |= PrinterStatus.PAPER_NEAR_END
            else:
                self._status &= ~PrinterStatus.PAPER_NEAR_END

            self._send_status()

    def __init__(self, port=10, ip_mode=False):
        """
        Args:
            port: (int) The port to simulate input on. This should be the half of the virtual port pair
                   that was not set in the registry. Only set this if you have a non-standard com0com configuration (COM10-COM9 pair is standard).
        Raises:
             SerialException: if the serial port is already in use (probably by another instance of PrinterSim)
        """
        self.log = logging.getLogger("PrinterSim")
        self.port = port
        self.ip_mode = ip_mode
        self.start(port, ip_mode)

    # Public functions
    def start(self, port=10, ip_mode=False):
        """
        Dispatch a thread to handle incoming serial messages from the POS.
        Args:
            port: (int) The number of the COM port to communicate on.
            ip_mode: (bool) If true, run in TCP/IP mode instead of serial. The value of port will be ignored.
        Returns: None
        """
        if ip_mode:           
            self._data_processor = threading.Thread(target=self._await_tcp_data, name="ReceiptPrinter", daemon=True)
            self._data_processor.start()

        else:  
            try:
                self._serial_port = serial.Serial(f"COM{port}",
                                          baudrate=9600,
                                          bytesize=serial.SEVENBITS,
                                          parity=serial.PARITY_NONE,
                                          stopbits=serial.STOPBITS_ONE)
            except serial.SerialException:
                self.log.error(f"Could not initialize serial printer sim. Ensure that COM{port} is available and not already in use.")
                raise

            self._serial_port.timeout = 0.1

            self._data_processor = threading.Thread(target=self._await_serial_data, name="ReceiptPrinter", daemon=True)
            self._data_processor.start()

    def get_receipt(self):
        """
        Get the most recent receipt.
        Args: None
        Returns: (str) The text of the last printed receipt.
        """
        # TODO: Store and provide access to more than just the most recent receipt, if users desire it
        # TODO: Figure out a way to represent rich text formatting
        return self.receipt_text

    def stop(self): 
        """
        Kill data processing thread and close open ports.
        """
        self._stop_flag = True
        self._data_processor.join()

        if self._serial_port != None:
            self._serial_port.close()
            self._serial_port = None
        if self._tcp_conn != None:
            self._tcp_conn.close()
            self._tcp_conn = None

    # Private functions

    def __del__(self):
        self.stop()

    def _await_serial_data(self):
        """
        Wait for serial communications from the POS and pass them to be processed.
        """
        while True:
            if self._stop_flag:
                break
            data = self._serial_port.read(4096)
            if len(data) == 0:
                continue
            if type(data) == str: # Unsure if this is needed. Pyserial doc says it returns bytes "when available".
                data = data.encode(self._encoding) 
            self._process_data(data)

    def _await_tcp_data(self):
        """
        Wait for TCP communications from the POS and pass them to be processed.
        """
        self._connect_tcp()

        while True:
            if self._stop_flag:
                break
            buffer = bytearray(4096)
            try:
                bytes_read = self._tcp_conn.recv_into(buffer)
            except ConnectionResetError:
                self.log.warning("Receipt printer connection reset. Attempting to recreate connection.")
                self._connect_tcp()
                continue

            self._process_data(buffer[:bytes_read-1])

    def _connect_tcp(self, ip='127.0.0.1', port=9100):
        """
        Create a socket and listen for a connection from the POS.
        Args:
            ip: (str) The IP address to use for the socket.
            port: (int) The port to use for the socket.
        Returns: None
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #s.settimeout(5)  # seconds

            s.bind((ip, port))
            s.listen(1)

            self.log.debug(f"[PrinterSim] Listening for connections on: {ip}:{port}")
            self._tcp_conn, addr = s.accept()
            self.log.debug("[PrinterSim] Connection from: " + str(addr))

        except socket.error as e:
            self.log.warning(f"[PrinterSim] Failed to create socket: {e}")     
            raise

    def _process_data(self, data):
        """
        Process and respond to an incoming message from the POS.
        Args:
            data: (bytes) The data to process.
        Returns: None
        """
        self.log.debug(f"Process data {data}")
        self._data += data.decode('utf-8')

        self.connected = True # Use this to know when we can continue with POS operations without error popups

        i = 0
        while (i < len(self._data)):
            if (self._storing_graphics and len(self._graphics_data) < self._graphics_bytes):
                bytes_to_take = min(len(data) - i, self._graphics_bytes - len(self._graphics_data))
                self._graphics_data += str(self._data)[i:bytes_to_take]
                i += bytes_to_take

                if self._graphics_bytes == len(self._graphics_data):
                    self._storing_graphics = False

            else:
                if ord(self._data[i]) == 0x1B: # ESC
                    i += 1
                    data_byte = self._data[i]
                    i += 1

                    if data_byte == '@': # initialize printer
                        self.log.debug("Initializing printer")
                        self._graphics_bytes = 0
                        self._graphics_data = ""
                        self._status_enabled = False
                    elif data_byte == 'p': # generate pulse
                        drawer = self._data[i]
                        i += 1
                        self.log.debug(f"Opening drawer [{drawer}]")
                        self.drawer_open = (drawer == 1)
                        i += 2 # ignore pulse duration
                    elif data_byte == 'E': # emphasized on/off
                        self.log.debug(f"Set bold [{ord(self._data[i])}] (not yet supported)")
                        i += 1
                        # TODO: How to represent bolded text without a GUI?
                    elif data_byte == '-': # underline on/off
                        self.log.debug(f"Set underline [{ord(self._data[i])}] (not yet supported)")
                        i += 1
                        # TODO: How to represent underlined text without a GUI?
                    elif data_byte == '!': # select print modes
                        mode = self._data[i]
                        i += 1
                        self.log.debug(f"Set mode [{ord(mode)}]] (not yet supported)")
                        # TODO set_bold((mode & 0x08) != 0)
                        # TODO set_large((mode & 0x10) != 0)
                        # TODO set_underline((mode & 0x80) != 0)
                        # TODO: How to represent bold/large/underline text without a GUI?
                    elif data_byte == 'd': # print and feed
                        self._write_text("\n")
                        i += 1
                    else:
                        self.log.debug(f"Ignore ESC [{self._data[i-1]}]")


                elif ord(self._data[i]) == 0x1D: # GS   
                    i += 1
                    data_byte = self._data[i]
                    i += 1

                    if data_byte == 'a': # enable/disable automatic status back (ASB)
                        # Easier to ask for forgiveness than for permission
                        try:
                            self.log.debug(f"Set ASB [{ord(self._data[i])}]")
                            self._status_enabled = self._data[i] != 0 # being lazy, all or nothing, not letting you pick what status you want
                        except IndexError:
                            self._status_enabled = False #Since the bit at that index does not exist, we assume failure here

                        # if it's enabled, send it
                        if self._status_enabled:
                            self._send_status()
                    elif data_byte == 'B': # reverse print mode on/off
                        self.log.debug(f"Set reverse [{ord(self._data[i])}]")
                        #self.set_reverse(self._data[i] == 1) # There is no method set_reverse currently implemented
                        i += 1
                    elif data_byte == 'V': # select cut mode and cut paper
                        self.log.debug("Cut paper")

                        # not processing partial vs full cut and line feeds, just read the data
                        if (ord(self._data[i]) > 49):
                            i +=1

                        i += 1
                        self._cut_paper()
                    elif data_byte == '(':
                        i += 1
                        data_byte = self._data[i]
                        i += 1

                        if data_byte == 'L': # graphics command
                            self.graphics_length = (self._data[i+1] << 8) + self._data[i]
                            m = self._data[i+2]
                            fn = self._data[i+3]
                            i += 4
                            if fn == '2':
                                # function 50, print stored data
                                self.log.debug("Print stored graphics data")
                            elif fn == 'p':
                                # store graphics
                                self.log.debug("Store graphics data")
                                self._storing_graphics = True
                                self._graphics_data = ""
                                self._graphics_bytes = self._graphics_length - 10
                                i += 10
                            else:
                                self.log.error(f"Ignore graphics function [{fn}]")
                        else:
                            self.log.error(f"Ignore unexpected command after ( [{self._data[i]}]")
                    else:
                        self.log.debug(f"Ignore GS [{self._data[i-1]}]")
                elif ord(self._data[i]) == 0x1F: # FS
                    self.log.debug("Ignore FS [{self._data[i+1]}]")
                    i += 2
                elif ord(self._data[i]) == 0x10: # transmit real-time status
                    i += 3
                elif ord(self._data[i]) == 0x7f: # del
                    i += 1 # ignore it
                else:
                    self._write_text(self._data[i])
                    i += 1

            #i += 1

        self._data = ""

    def _send_status(self):
        """
        Send the current printer status to the POS.
        """
        try:
            if self._status_enabled:
                status = self._status.to_bytes(4, sys.byteorder)

                if (self._serial_port != None):
                    self._serial_port.write(status)

                if (self._tcp_conn != None):
                    self._tcp_conn.send(status)

        except Exception as e:
            self.log.error(type(e).__name__ + ": " + str(e))

    def _write_text(self, text):
        """
        Write text to the current receipt.
        # TODO: Find a way to represent text formatting
        # TODO: Store past receipts if it's a desired feature
        Args:
            text: (str) The text to add to the receipt.
        Returns: None
        """
        self.log.log(1, f"Writing receipt: {text}") # Extremely spammy, only enable for debugging purposes
        # If paper has been cut and we are not writing whitespace, clear text up to the cut position
        if (self._cut_position > 0 and not any([c.isspace() for c in text])):
            self.receipt_text = self.receipt_text[self._cut_position-1:]
            self._cut_position = -1
        self.receipt_text += text;
        
    def _cut_paper(self):
        """
        Set cut position at the end of the current receipt, signaling to clear receipt text next time we write a receipt.
        """
        self._cut_position = len(self.receipt_text)

def setup():
    """
    Sets up the needed registry keys and com ports for the serial receipt ptiner sim
    Args:
        None
    Returns:
        True/False: (bool) True if the receipt printer is setup and ready to run.
    Example:
        >>> setup()
    """

    log = logging.getLogger("PrinterSim")
    pp_subkey = constants.POSPRINTER_T88II_SUBKEY
    reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, pp_subkey, 0, winreg.KEY_ALL_ACCESS)

    # Set up virtual COM port pair for receipt printer simulator
    list = runas.run_as("cd c:\Program Files (x86)\com0com\ && setupc.exe list")  # Check if it's already configured
    if "COM10" not in list['output']:
        runas.run_as("cd C:\Program Files (x86)\com0com && setupc.exe install PortName=COM10 PortName=COM9",
                     ignore_stdout=True)
        time.sleep(5)
        send_keys("{RIGHT}{ENTER}")  # Select "Restart Later". Is there a better way to do this?

    if (winreg.QueryValueEx(reg_key, 'Port')[0] == "COM5"): # COM5 is the default, if this is set then assume site isn't yet set up for printer sim
        res = runas.run_as(
            f'reg add HKEY_LOCAL_MACHINE\{pp_subkey} /v Port /t REG_SZ /d COM9 /f')
        if res['pid'] == -1:
            log.error("Registry edit failed. The response was: %s" % (res['output']))
            return False

        system.restartpp()

    return True