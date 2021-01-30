"""
    File name: POS_Fuel.py
    Tags:
    Description: 
    Author: 
    Date created: 2020-06-05 11:41:30
    Date last modified: 
    Python Version: 3.7
"""

import logging, time
from app import Navi, mws, pos, system, crindsim
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app.features import fuel_price_change

default_timeout = 3

class POS_Fuel():
    """
    Description: Test class that provides an interface for testing.
    """

    def __init__(self):
        """
        Initializes the Template class.
        """
        # The logging object. 
        # Example: self.log.info(f"Current value of var: {my_var}")
        self.log = logging.getLogger()
        self.long_wait_time = 10
        self.price_change_wait_time = 30


    @setup
    def setup(self):
        """
        Performs any initialization that is not default.
        """
        # if not system.restore_snapshot():
        #     self.log.debug("No snapshot to restore, if this is not expected please contact automation team")
        mws.sign_on()
        pos.connect()
        pos.sign_on()


    @test
    def send_immediately(self):
        """
        Do a fuel price change that sends to POS immediately
        """
        # Fuel before changing price
        self.log.info("Adding prepay fuel to transaction before price change...")
        pos.add_fuel('$10.00')
        self._check_fuel_price("1.00")

        self._return_to_main_screen()
        pos.wait_for_fuel()

        # Fuel after changing price
        self.log.info("Changing fuel price...")
        menu = fuel_price_change.FuelPriceChange()
        mws.set_value("Immediately", True)
        menu.increase("Diesel 1", "100")
        self._mws_save()

        self.log.info("Waiting " + str(self.price_change_wait_time) + " seconds for price to be updated in HTML POS...")
        time.sleep(self.price_change_wait_time)

        self.log.info("Adding prepay fuel to transaction after price change...")
        pos.add_fuel("$10.00")

        self._check_fuel_price("2.00")

        self._return_to_main_screen()
        pos.wait_for_fuel()

        self.log.info("Fuel price change worked with 'Immediately' toggled in MWS!")


    @test
    def do_not_send(self):
        """
        Do a fuel price change that must be toggled in HTML POS
        """
        # Reset
        self._return_to_main_screen()
        pos.wait_for_fuel()
        self._reset_fuel_price()

        # Fuel before changing price
        self.log.info("Adding prepay fuel to transaction before price change...")
        pos.add_fuel('$10.00')
        self._check_fuel_price("1.00")

        self._return_to_main_screen()
        pos.wait_for_fuel()

        # Fuel after changing price MWS with Do not send toggled
        self.log.info("Changing fuel price...")
        menu = fuel_price_change.FuelPriceChange()
        mws.set_value("Do not send", True)
        menu.increase("Diesel 1", "100")
        self._mws_save()

        self.log.info("Waiting " + str(self.price_change_wait_time) + " seconds to give time for price to change in HTML POS " +\
         "(it shouldn't change, but in case the Do not send toggle is broken)...")
        time.sleep(self.price_change_wait_time)

        self.log.info("Adding prepay fuel to transaction after price change with 'Do not send' toggled...")
        pos.add_fuel("$10.00")

        self._check_fuel_price("1.00")

        self._return_to_main_screen()
        pos.wait_for_fuel()
        self._return_to_main_screen()

        # Fuel after changing price in MWS with HTML POS button
        self.log.info("Initiating fuel price change from HTML POS...")
        pos.click('dispenser menu')
        pos.click('fuel price change')
        pos.click('ok')
        pos.click('back')
        self.log.info("Waiting " + str(self.price_change_wait_time) + " seconds for price to be updated in HTML POS...")
        time.sleep(self.price_change_wait_time)

        self.log.info("Adding prepay fuel to transaction after clicking 'Fuel Price Change' on HTML POS...")
        
        pos.add_fuel("$10.00")

        self._check_fuel_price("2.00")

        self._return_to_main_screen()
        pos.wait_for_fuel()
        self._return_to_main_screen()
        
        self.log.info("Fuel price change button worked on HTML POS!")

        
    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        self._reset_fuel_price()
        pos.close()


    def _in_transaction(self, timeout=default_timeout):
        """
        Helper function to determine if HTML POS
        is currently in a transaction
        """
        return pos.is_element_present(pos.controls['function keys']['pay'], timeout=timeout)


    def _on_dispenser_screen(self, timeout=default_timeout):
        """
        Helper function to determine if HTML POS
        is currently on a dispenser screen
        """
        return pos.is_element_present(pos.controls['function keys']['prepay'], timeout=timeout)

    
    def _on_main_screen(self, timeout=default_timeout):
        """
        Helper function to determine if HTML POS
        is on the main screen (i.e. logged in with
        no transaction active)
        """
        return pos.is_element_present(pos.controls['function keys']['refund'], timeout=timeout)

    
    def _return_to_main_screen(self, timeout=default_timeout):
        """
        Helper function for returning HTML POS
        to its main screen if it's in a transaction
        or has a dispenser selected
        """
        if self._on_main_screen():
            self.log.info("On main screen...")
            return True
        elif self._in_transaction():
            self.log.info("In transaction...")
            if pos.is_element_present(pos.controls['function keys']['pay']):
                pos.click('pay')
                pos.click_tender_key('exact change')
                if pos.read_message_box(timeout=self.long_wait_time):
                    pos.click('ok')
            elif pos.is_element_present(pos.controls['function keys']['void transaction']):
                pos.click('void transaction')
                pos.click('enter')
            else:
                self.log.warning("Could not find pay or void transaction button to return to main screen!")
                return False
            if pos.is_element_present(pos.controls['function keys']['refund'], timeout=self.long_wait_time):
                self.log.info("On main screen...")
                return True
            else:
                self.log.error("Not on main screen.")
                return False
        elif self._on_dispenser_screen():
            self.log.info("On dispenser screen...")
            if not pos.click('back', verify=False):
                self.log.error("Failed to click back to exit dispenser menu in _return_to_main_screen.")
                return False
            if pos.is_element_present(pos.controls['function keys']['pay']):
                pos.click('pay')
                pos.click_tender_key('exact change')
                if pos.read_message_box(timeout=self.long_wait_time):
                    pos.click('ok')
            elif pos.is_element_present(pos.controls['function keys']['void transaction']):
                pos.click('void transaction')
                pos.click('enter')
            elif pos.is_element_present(pos.controls['function keys']['refund'], timeout=self.long_wait_time):
                self.log.info("On main screen...")
                return True
            else:
                self.log.warning("Could not find pay or void transaction button to return to main screen!")
                return False
            
            if pos.is_element_present(pos.controls['function keys']['refund'], timeout=self.long_wait_time):
                self.log.info("On main screen...")
                return True
            else:
                self.log.error("Not on main screen.")
                return False
        else:
            self.log.error("On an unknown screen.")
            return False
            

    def _reset_fuel_price(self):
        """
        Helper function for setting the fuel
        price back to default of $1.00 for all fuel types
        """
        self.log.info("Resetting fuel prices to $1.00...")
        menu = fuel_price_change.FuelPriceChange()
        # Default fuels added by automation initial setup
        fuels = ["Regular", "Plus", "Supreme", "Diesel 1", "Diesel 2", "Desl Blnd"]
        for fuel_type in fuels:
            menu.change_prices(fuel_type, "1000")
        mws.set_value("Immediately", True)
        self._mws_save()
        time.sleep(self.price_change_wait_time)
        self.log.info("Fuel prices reset...")


    def _check_fuel_price(self, price):
        """
        Helper function to make sure the transaction journal 
        contains the right price
        """
        try:
            journal = pos.read_transaction_journal()
            if price in journal[0][2]:
                self.log.info("Fuel price per gallon is correct...")
            else:
                self._return_to_main_screen()
                tc_fail("Fuel price per gallon is not correct.")
            price = float(price)
            amount = float(journal[0][2][:5])
            total = float(journal[0][1][1:])
            if abs(round((amount * price), 2) - total) < 0.01:
                self.log.info("Fuel amount correct...")
            else:
                self._return_to_main_screen()
                tc_fail("Fuel amount is not correct.  Should be " + str(total / price) + \
                 " but was listed in HTML POS as " + str(amount))
        except IndexError:
            self._return_to_main_screen()
            tc_fail("Transaction journal did not contain the proper elements.  " +\
             "Here is the transaction journal printed: " + pos.read_transaction_journal())


    def _mws_save(self, timeout=20):
        """
        Helper function for saving on the MWS
        """
        mws.click_toolbar("Save")
        start_time = time.time()
        while time.time() - start_time <= timeout:
            if mws.get_top_bar_text() == '':
                return True
            time.sleep(timeout/20)
        else:
            return False