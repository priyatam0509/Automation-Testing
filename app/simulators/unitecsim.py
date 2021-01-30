__author__ = "Cassidy Garner"

"""
Module for interacting with the TCP/IP based Unitec Wash Entry Simulator. It provides the functionality needed to 
simulate all Unitec Kiosk functions that interact with Passport. Some functions that do not interact with Passport,
such as cash purchases, are not supported at this time. You can edit the sim's accounting data to have it report
such purchases to Passport.
"""

import logging, ast, time
import json
from app.util.runas import run_sqlcmd
from app.framework import EDH
from app.util import server, constants
from app.simulators.basesim import Simulator
from app.framework.tc_helpers import test_func

# Global Variables:
log = logging.getLogger(__name__)

def init_unitecsim():
    """
    Creates an instance of the Unitec sim using the IP given from the
    Docker Manager application running on the Server.
    """
    # TODO : We need to write the IP to some JSON file.
    ip_addr = server.server.get_site_info()['ip']
    return UnitecSim(endpoint=f"http://{ip_addr}/")

class UnitecSim(Simulator):
    def __init__(self, endpoint):
        super().__init__(endpoint, "unitec") 

    ### Authorization/purchasing ###

    def get_display_text(self):
        """
        Get the message currently being displayed by the authorization service.
        Args: None
        Returns: (str) The currently displayed message.
        """
        return self._send_get("/getdisplaytext/")

    def get_packages(self):
        """
        Get the currently configured wash packages.
        Args: None
        Returns: (list) The currently configured packages. Includes IDs, names, prices, and discounts.
        """
        return json.loads(self._send_get("/getpackages/"))

    def select_package(self, package_id):
        """
        Select a package for purchase.
        Args:
            package_id: (int) The ID of the package to select, 1-4.
        Returns: (bool) True if success, False if the sim raises an exception.
        """
        return self._send_get_void(f"/selectpackage/{package_id}")

    def select_upgrade_package(self, package_id):
        """
        Select a package to upgrade the selected package to.
        Args:
            package_id: (int) The number of the package to select, 1-4. The package must be more expensive than
                              the selected base package.
        Returns: (bool) True if success, False if the sim raises an exception.
        """
        return self._send_get_void(f"/selectupgradepackage/{package_id}")

    def swipe_card(self, card_name="Visa", brand="Core"):
        """
        Use a card to purchase the currently selected car wash package.
        Args:
            brand: (str) The brand of the store. NOTE: Different stores have different bin ranges.
            card_name: (str) The name of the card being used. NOTE: Please refer to app/data/CardData.json for card names and bins.
        Returns: (bool) True if success, False if the sim raises an exception.
        """
        card_data = self._get_card_data(brand, card_name)
        return self._send_post_void("/purchase/card/", card_data) 

    def swipe_fob(self, track_data, rfid_data=""):
        """
        Use a fob to purchase the currently selected car wash package.
        Args:
            track_data: (str) The fob's track data.
            rfid_data: (str) The fob's RFID data, if applicable.
        Returns: (bool) True if success, False if the sim raises an exception.
        """
        fob_data = { 'trackData': track_data,
                     'rfidData': rfid_data }
        return self._send_post_void("/purchase/fob/", fob_data)

    def answer_query(self, answer):
        """
        Answer a query displayed by the kiosk, i.e. ZIP code prompt.
        Args:
            answer: (str) The entry to respond with. Can be a numeric string, or yes/no/credit/debit, or Cancel.
        Returns: (bool) True if success, False if the sim raises an exception.
        """
        return self._send_get_void(f"/answerquery/{answer}")

    def get_receipt(self, receipt=1):
        """
        Get a printed receipt.
        Args:
            receipt: (int) The index of the receipt to retrieve, in reverse chronological order. Default is the most recent receipt.
        Returns: (str) The text of the receipt.
        """
        return self._send_get(f"/getreceipt/{receipt}/")

    ### Configuration ###

    def get_pos_ip(self):
        """
        Get the currently configured POS IP from the sim.
        Args: None
        Returns: (str) The currently configured POS IP.
        """
        return self._send_get("/config/ip/")

    def set_pos_ip(self, ip):
        """
        Set the IP of the POS for the sim to connect to. The EDH will be restarted to establish the connection.
        Args:
            ip: (str) The IP address of the Passport site that the sim should connect to.
        Returns: (bool) True if success, False if the sim raises an exception.
        """
        result = self._send_get_void(f"/config/ip/{ip}")
        if result:
            EDH.EDH().restart()
        return result

    def get_terminal_id(self):
        """
        Get the configured terminal ID from the sim.
        Args: None
        Returns: (int) The terminal ID of the simulated kiosk.
        """
        return int(self._send_get(f"/config/terminalid/"))

    def set_terminal_id(self, id):
        """
        Set the terminal ID on the sim.
        Args: 
            id: (int) The ID to set for the simulated kiosk.
        Returns: (bool) True if success, False if the sim raises an exception.
        """
        return self._send_get_void(f"/config/terminalid/{id}/")

    def get_connected_clients(self):
        """
        Get a list of clients that are connected to the sim's entry server.
        Args: None
        Returns: (list) IP:Port for each connected client.
        """
        return self._send_get("/getconnectedclients/").split(',')

    ### Data ###

    def get_wash_sales_data(self, id):
        """
        Get the wash sales data for a given package.
        Args:
            id: (int) The package ID to get sales data for.
        Returns: (dict) Sales data for the specified package ID.
        """
        return json.loads(self._send_get(f"/accountingdata/washsale/{id}/"))

    def set_wash_sales_data(self, id, field, value):
        """
        Edit the wash sales data for a given package.
        Args:
            id: (int) The package ID to edit sales data for.
            field: (str) The sales data field to edit. Valid fields include: id, activations, salescount, cashcount,
                   cashtotal, creditcount, credittotal, othercount, othertotal, upgradecount, upgradetotal, poscount,
                   postotal, unitecposcount, unitecpostotal.
            value: (float) The value to set for the field.
        Returns: (bool) True if success, False if the sim raises an exception.
        """
        return self._send_get_void(f"/accountingdata/washsale/{id}/{field.lower()}/{value}/")

    def get_payments_in(self):
        """
        Get the payments received data from the Unitec sim.
        Args: None
        Returns: (dict) Payments received data.
        """
        return json.loads(self._send_get("/accountingdata/payments/in"))

    def set_payments_in(self, field, value):
        """
        Edit the sim's payments received data.
        Args:
            field: (str) The data field to edit. Valid fields include: bills, coins, coupons, tokens.
            value: (float) The value to set for the field.
        Returns: (bool) True if success, False if the sim raises an exception.
        """
        return self._send_get_void(f"/accountingdata/payments/in/{field.lower()}/{value}/")

    def get_payments_out(self):
        """
        Get the payments dispensed data from the Unitec sim.
        Args: None
        Returns: (dict) Payments dispensed data.
        """
        return json.loads(self._send_get("/accountingdata/payments/out"))

    def set_payments_out(self, field, value):
        """
        Edit the sim's payments dispensed data.
        Args:
            field: (str) The data field to edit. Valid fields include: bills, coins, tokens.
            value: (float) The value to set for the field.
        Returns: (bool) True if success, False if the sim raises an exception.
        """
        return self._send_get_void(f"/accountingdata/payments/out/{field.lower()}/{value}/")

    ### Miscellaneous ###

    def alert(self, severity, description, name, errorcode):
        """
        Have the sim send an alert.
        Args:
            severity: (str) The severity of the alert to send. Valid severities include: Information, Warning, Fault.
            description: (str) The text of the alert to send.
            name: (str) The equipment name field to send with the alert.
            errorcode: (int) The error code to include with the alert.
        Returns: (bool) True if success, False if the sim raises an exception.
        """
        return self._send_get_void(f"/alert/{severity.capitalize()}/{description}/{name}/{errorcode}/")

    def cash_reconcile(self):
        """
        Have the sim perform a cash reconciliation event.
        Args: None
        Returns: (bool) True if success, False if the sim raises an exception.
        """
        return self._send_get_void("/cashreconciliation/")

    def reject_config(self):
        """
        Have the sim reject the next configuration event that it receives.
        Args: None
        Returns: (bool) True if success, False if the sim raises an exception.
        """
        return self._send_get_void("/rejectconfig/")

    def _send_get_void(self, request):
        """
        Send an HTTP GET request that does not return information.
        """
        result = self.get(request)
        if result['success'] and result['payload']['code'] == 200:
            return True
        log.warning(f"Received the following error: {result['payload']}")
        return False

    def _send_get(self, request):
        """
        Send an HTTP GET request that returns information.
        """
        result = self.get(request)
        if result['success'] and result['payload']['code'] == 200:
            return result['payload']['message']
        else:
            log.warning(f"Received the following error: {result['payload']}")
            return None

    def _send_post_void(self, request, data):
        """
        Send an HTTP POST request that does not return information.
        """
        result = self.post(request, data)
        if result['success'] and result['payload']['code'] == 200:
            return result['payload']['message']
        else:
            log.warning(f"Received the following error: {result['payload']}")
            return None