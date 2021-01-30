import serial, logging

log = logging.getLogger()

class SerialScanner():
    """
    A class for simulating a serial barcode scanner.
    It also provides methods to assist with creating price embedded barcodes.
    This class relies on a pair of virtual COM ports created by the com0com application.
    It also requires DB changes to work - see register_setup.RegisterSetup.add_scanner_ports().
    These requirements are built into the automation image and initial setup, respectively.
    """

    def __init__(self, port=3):
        """
        Args:
            port: (int) The port to simulate input on. This should be the half of the virtual port pair
                  that was not set in the database. Only set this if you have a non-standard com0com configuration (COM6-COM4 pair is standard).
        Raises:
            SerialException: if the serial port is already in use (probably by another instance of SerialScanner)
        """
        try:
            self.conn = serial.Serial(f"COM{port}", write_timeout=10)
        except serial.SerialException:
            log.error(f"Could not initialize serial barcode scanner sim. Ensure that COM{port} is available and not already in use.")
            raise

    def __del__(self):
        self.conn.close()

    def scan(self, code):
        """
        Simulate the scanning of a barcode by a serial scanner.
        Args:
            code: The code to scan.
        Returns: None
        Raises: 
            SerialTimeoutException: If the serial write times out
        Examples:
            >>> scan('1')
            >>> scan('00001234')
            >>> scan('227182005009')
        """
        self.conn.write(b'%s\r' % code.encode())

    def scan_pe_code(self, code, price):
        """
        Generate a barcode with an embedded price and scan it.
        Args:
            code: The scan code of the item.
            price: The desired price of the item.
        Returns: None          
        Examples:
            >>> scan_pe_code('1', '$12.34')
            >>> scan_pe_code('0000000027182, '500')
        """
        scan_code = SerialScanner.generate_pe_code(code, price)
        return self.scan(scan_code)

    @staticmethod
    def generate_pe_code(code, price):
        """
        Generate a price embedded scan code.
        Args:
            code: (str) The base scan code of the item.
            price: (str) The desired price to embed.
        Returns:
            str: A price embedded barcode with the given scan code and price.
        Examples:
            >>> SerialScanner.generate_pe_code('1', '$12.34')
            '200001012341'
            >>> SerialScanner.generate_pe_code('000000027182', '500')
            '227182005009'
        """
        price = price.replace('$', '').replace('.', '')
        barcode = '2%05.d%05.d' % (int(code), int(price))
        barcode += str(SerialScanner.checksum(barcode))
        return barcode

    @staticmethod
    def checksum(code):
        """
        Compute the checksum digit for a price embedded barcode.
        Args:
            code: (str) The code to generate a checksum digit for.
        Returns:
            int: The checksum digit for the code.
        Examples:
            >>> SerialScanner.checksum('20000101234')
            1
            >>> SerialScanner.checksum('22718200500')
            9
        """
        c = 0
        for i in range(0, len(code), 2):
            c += int(code[i])
        c *= 3
        for i in range(1, len(code), 2):
            c += int(code[i])
        c = ((c+9) // 10 * 10) - c

        return c 