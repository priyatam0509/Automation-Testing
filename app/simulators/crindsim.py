__author__ = "Jesse Thomas"

# to run this standalone.. the __name__ and __package__ things muck w/ where/how imports are handled.
# So if this import fails, meaning test_harness is the one calling us, use the fully qualified module name.

import logging, ast, time
import json
from app.util.runas import run_sqlcmd
from app.framework import EDH
from app.util import server, constants
from app.simulators.basesim import Simulator
from app.framework.tc_helpers import test_func

# Global Variables:
log = logging.getLogger(__name__)

# region TODO Notes
"""
TODO: <Place TODO notes here>
"""
# endregion

def init_crindsim():
    """
    Creates an instance of the cinrdsim using the IP given from the
    Docker Manager application running on the Server.
    """
    # TODO : We need to write the IP to some JSON file.
    ip_addr = server.server.get_site_info()['ip']
    return CrindSim(endpoint=f"http://{ip_addr}/")


class CrindSim(Simulator):

    def __init__(self, endpoint):  # -> CrindSim:
        super().__init__(endpoint, "crindsim")  # -> Looks like the name is static.

    def close(self, dispenser=1):
        """
        Closes the selected dispenser. This is a TCP/IP disconnect.
        
        Args:
            dispenser: (int) The number of the dispenser that will be closing.
        
        Returns:
            True/False: (bool) True if the dispenser successfully closed. False otherwise.
        
        Example:
            >>> crindsim.close()
                True
            >>> crindsim.close(4)
                True
            >>> crindsim.close("bananas")
                False
        """
        result = self.get(f"/closedispenser/{dispenser}")
        if result['success']:
            return True
        log.warning(f"Receieved the following Error: {result['payload']}")
        return False

    def set_pump_type(self, type, blend_ratios=[], dispenser=1):
        """
        Set the pump type and blend ratios (if applicable) for the selected dispenser.
        Restarts the EDH so it will pick up the new configuration.

        Args:
            type: (str) The pump type to set - MULTI_3, BLN_4, etc.
            blend_ratios: (list) The low product percentage for each blended grade, if there are any.
            dispenser: (int) The number of the dispenser to configure.

        Returns:
            (bool) True if sim successfully configures the pump. False if not.

        Examples:
            >>> crindsim.set_pump_type("MULTI_3")
            True
            >>> crindsim.set_pump_type("BLN_3+1", [100, 50, 0])
            True
            >>> crindsim.set_pump_type("BLN_4", [100, 50, 0])
            False
        """
        type = type.replace('+', '_').upper()
        if blend_ratios:
            ratios_str = ",".join([str(r) for r in blend_ratios])
            req = f"/setpumptype/{type}/{ratios_str}/{dispenser}"
        else:
            req = f"/setpumptype/{type}/{dispenser}"
        result = self.get(req)
        if result['success']:
            EDH.EDH().restart() # EDH may not pick up on the config change without a restart
            return True
        log.warning(f"{result['payload']}")
        return False

    def close_nozzle(self, dispenser=1):
        """
        Closes the nozzle to the selected dispenser.
        
        Args:
            dispenser: (int) The number of the dispenser that will have its nozzle closed.
        
        Returns:
            True/False: (bool) True if the dispenser's nozzle was successfully closed. False otherwise.
        
        Examples:
            >>> close_nozzle()
                True
            >>> close_nozzle(3)
                True
            >>> close_nozzle("some text")
                False
        """
        log.info(f"Close nozzel in dispenser #{dispenser}")
        result = self.get(f"/closenozzle/{dispenser}")
        if result['success']:
            return True
        log.warning(f"Receieved the following Error: {result['payload']}")
        return False

    def get_display_text(self, dispenser=1):
        """
        Gets the text that is on the dispenser.
        
        Args:
            dispenser: (int) The number of the dispenser
        
        Returns:
            lines: (list) A list of texts split down by the line. The list will be empty if there was any error.
        
        Examples:
            >>> get_display_text()
                ["Pay inside", "or insert card"]
            >>> get_display_text(3)
                ["Downloading..."]
            >>> get_display_text("bad argument")
                []
        """
        lines = ""
        result = self.get(f"/getdisplay/{dispenser}")
        if result['success']:
            display_text = result['payload']['message']
        else:
            log.warning(result['payload'])
            return lines
        lines = display_text.replace("\n", " ")
        log.info(f"The dispenser screen shows {lines}")
        return lines
    
    def get_grade_price(self, grade = 1, price_type = "credit", dispenser = 1):
        """
        Gets the prices of the selected grade at the selected dispenser.
        Note that for blended pumps, pure grades appear as the last grades, i.e. for BLN_3+1 the 1 will be grade 6.
        
        Args:
            grade: (int) The grade in which the price will be received from
            price_type: (str) The price type for the grade. Only credit and cash are supported
            dispenser: (int) The number of the dispenser that the price will be received from.
        
        Returns
            (str) The price of the selected grade. An empty string if there was an error.

        Examples:
            >>> get_grade_price()
                "1.000"
            >>> get_grade_price(1, dispenser = 2)
                "0.999"
            >>> get_grade_price(1, "invalid price type", 3)
                ""
        """        
        result = self.get(f"/getgradeprice/{grade}/{price_type}/{dispenser}")
        if result['success']:
            return result['payload']['message']
        log.warning(result['payload'])
        return ""
    
    def get_mode(self, dispenser=1):
        """
        Gets the mode of the selected dispenser (auto or manual)
        
        Args:
            dispenser: (int) The number of the dispenser that the mode will be retrieved from.
        
        Returns:
            (str) The mode that the selected dispenser is on (auto or manual). An Empty string if there was an error.

        Examples:
            >>> get_mode(2)
                "auto"
            >>> get_mode()
                "manual"
            >>> get_mode("guitar") #There's no dispenser called guitar
                ""
        """
        result = self.get(f"/getmode/{dispenser}")
        if result['success']:
            return result['payload']['message']
        log.warning(result['payload'])
        return ""

    def get_receipt(self, dispenser=1):
        """
        Gets the most recent receipt printed on the CRIND.

        Args:
            dispenser: (int) The dispenser number to get the receipt from.
        
        Returns:
            (str) The string that represents the receipt. Empty string if there was no receipt or if there was an error.

        Examples:
            >>> get_receipt()
                "\r\nAutomation Island\r\n299\r\n1234 Some Street\r\nFort Lauderdale, FL\r\n33308\r\n09/18/2019\r\n01:15:41 PM\r\n \r\nPREPAID RECEIPT\r\n \r\nPUMP# 1\r\nDiesel 1     "\
                "20.020G\r\nPRICE/GAL     $0.999\r\n \r\nFUEL TOTAL  $  20.00\r\n \r\n   FINAL PURCHASE\r\nAMOUNT RECEIPT WITH\r\n  FULL TRANSACTION\r\n  DETAIL AVAILABLE\r\n       "\
                    "INSIDE\r\n \r\n
            >>> get_receipt(1)
                "\r\nAutomation Island\r\n299\r\n1234 Some Street\r\nFort Lauderdale, FL\r\n33308\r\n09/18/2019\r\n01:15:41 PM\r\n \r\nPREPAID RECEIPT\r\n \r\nPUMP# 1\r\nDiesel 1     "\
                "20.020G\r\nPRICE/GAL     $0.999\r\n \r\nFUEL TOTAL  $  20.00\r\n \r\n   FINAL PURCHASE\r\nAMOUNT RECEIPT WITH\r\n  FULL TRANSACTION\r\n  DETAIL AVAILABLE\r\n       "\
                    "INSIDE\r\n \r\n"
            >>> get_receipt("Not a dispenser")
                ""
        """
        result = self.get(f"/getreceipt/{dispenser}")
        if result['success']:
            receipt = result['payload']['message']
            log.info(f"The receipt of dispenser #{dispenser} is {receipt}")
            return receipt
        log.warning(result['payload'])
        return ""

    def get_softkey_text(self, dispenser=1):
        """
        Gets the text of each softkey that is available.
        
        Args:
            dispenser: (int) The number of the dispenser that the softkey texts will be retrieved from.
        
        Returns:
            (list) A list of the softkeys that are currently active and the text that they contain. 
                   An Empty list if there are no softkeys active or if there was an error.
        
        Examples:
            >>> get_softkey_text()
                [] #This sometimes isn't bad if there are no softkeys with text
            >>> get_softkey_text(2)
                ["yes", "no"]
            >>> get_softkey_text("Not a dispenser")
                []
        """
        result = self.get(f"/getsoftkeytexts/{dispenser}")
        if result['success']:
            return result['payload']["message"].split(",")
        #Returning an empty list in case there are no speedkey texts or if there was a failure.
        log.warning(result['payload']["message"])
        return []

    def lift_handle(self, dispenser=1):
        """
        Lifts the handle to the selected dispenser.
        
        Args:
            dispenser: (int) The number of the dispenser in which the handle will be lifted.
        
        Returns:
            True/False: (bool) True if the handle was successfully lifted. False otherwise.

        Examples:
            >>> lift_handle()
                True
            >>> lift_handle(3)
                True
            >>> lift_handle("Not a dispenser")
                False
        """
        log.info(f"Lift the handle on dispenser #{dispenser}")
        result = self.get(f"/lifthandle/{dispenser}")
        if result['success']:
            return True
        log.warning(result['payload'])
        return False

    def lower_handle(self, dispenser=1):
        """
        Lowers the handle to the selected dispenser.
        
        Args:
            dispenser: (int) The number of the dispenser in which the handle will be lowered.
        
        Returns:
            True/False: (bool) True if the handle was successfully lowered. False otherwise.

        Examples:
            >>> lower_handle()
                True
            >>> lower_handle(2)
                True
            >>> lower_handle("Not a dispenser")
                False
        """
        log.info(f"Lower the handle on dispenser #{dispenser}")
        result = self.get(f"/lowerhandle/{dispenser}")
        if result['success']:
            return True
        log.warning(result['payload'])
        return False

    def open(self, dispenser=1):
        """
        Opens the dispenser through a TCP/IP connection.
        
        Args:
            dispenser: (int) The number of the dispenser that is being opened.
        
        Returns:
            True/False: (bool) True if the dispenser was successfully opened. False otherwise.

        Examples:
            >>> open()
                True
            >>> open(4)
                True
            >>> open("Not a dispenser")
                False
        """
        result = self.get(f"/opendispenser/{dispenser}")
        if result['success']:
            return True
        log.warning(result['payload'])
        return False

    def open_nozzle(self, dispenser=1):
        """
        Opens the nozzle of the selected dispenser.
        
        Args:
            dispenser: (int) The number of the dispenser that the nozzle will be opened.
        
        Returns:
            True/False: (bool) True if the nozzle was successfully opened. False otherwise.

        Examples:
            >>> open_nozzle()
                True
            >>> open_nozzle(7)
                True
            >>> open_nozzle("Not a dispenser")
                False
        """
        log.info(f"Open nozzle on dispenser #{dispenser}")
        result = self.get(f"/opennozzle/{dispenser}")
        if result['success']:
            return True
        log.warning(result['payload'])
        return False

    @test_func
    def press_keypad(self, key , dispenser=1):
        """
        Presses a key on the keypad of the selected dispenser.
        
        Args:
            key: (str) The key that will be pressed.
            dispenser: (int) The number of the dispenser in which the keypad will be pressed.
        
        Returns:
            True/False: (bool) True if the keypad key was successfully pressed. Falses otherwise.

        Examples:
            >>> press_keypad("4")
                True
            >>> press_keypad("Help", 2)
                True
            >>> press_keypad("Not a key")
                False
            >>> press_keypad("Cancel", "not a dispenser")
                False
        """
        log.info(f"Click on keypad {key} on dispenser #{dispenser}")
        result = self.get(f"/presskeypadkey/{key}/{dispenser}")
        if result['success']:
            return True
        log.warning(result['payload'])
        return False

    @test_func
    def press_softkey(self, key, dispenser=1):
        """
        Presses a softkey on the dispenser if it exists.
        
        Args:
            key: (str) The text for the softkey being pressed.
            dispenser: (int) The numbered dispenser to press the softkey at.
        
        Returns:
            True/False: (bool) True if the softkey was pressed successfully. False otherwise.

        Examples:
            >>> press_softkey("yes")
                True
            >>> press_softkey("no", 3)
                True
            >>> press_softkey("Not yes")
                False
            >>> press_softkey("yes", "Not a dispenser")
                False
        """
        log.info(f"Click softkey key {key} on dispenser #{dispenser}")
        result = self.get(f"/presssoftkey/{key}/{dispenser}")
        if result['success']:
            return True
        log.warning(result['payload'])
        return False

    def select_grade(self, grade = 1, dispenser = 1):
        """
        Selects the grade that will be dispensed.
        Note that for blended pumps, pure grades appear as the last grades, i.e. for BLN_3+1 the 1 will be grade 6.
        Selecting an unconfigured grade may lead to errors.
        
        Args:
            grade: (int) The grade number that will be dispensed. (Starts with 1)
            dispenser: (int) The number of the dispenser that the grade will be selected for.
        
        Returns:
            True/False: (bool) True if the grade was successfully selected. False otherwise.

        Examples:
            >>> select_grade()
                True
            >>> select_grade(2)
                True
            >>> select_grade(3, 2)
                True
            >>> select_grade(dispenser = 4)
                True
            >>> select_grade("not a grade")
                False
            >>> select_grade(2, "Not a dispenser")
                False
        """
        log.info(f"Select grade {grade} on dispenser #{dispenser}")
        response = self.get(f"/selectgrade/{grade}/{dispenser}")
        if response['success']:
            if response['payload']['message'] == 'false':
                log.warning(f"Could not select grade: {grade}")
            log.debug(f"Successfully selected the grade: {grade}")
            return True
        else:
            log.warning(f"Could not select grade: {grade}")
            return False
    
    def set_flow_rate(self, rate, dispenser=1):
        """
        Sets the flow rate to the selected dispenser. The higher the flowrate, the faster the CRIND will dispense.
        
        Args:
            rate: (int) The rate in which the fuel will be dispensed. Maximum rate: 10. Minimum rate: 1.
            dispenser: (int) The number of the dispenser that the flow rate is being set on.
        
        Returns:
            True/False: (bool) True if the rate was successfully set. False otherwise.

        Examples:
            >>> set_flow_rate(5)
                True
            >>> set_flow_rate(8, 2)
                True
            >>> set_flow_rate("not a flow rate")
                False
            >>> set_flow_rate(2, "not a dispenser")
                False
        """
        log.info(f"Set Flow rate {rate} on dispenser #{dispenser}")

        if type(rate)==str and not rate.isdigit():
            log.warning(f"The rate was {rate} instead of a digit.")
            return False
        results = self.get(f"/setflowrate/{int(rate)}/{dispenser}")
        if results['success'] and "false" not in results['payload']['message']:
            return True
        log.warning("Could not successfully set the flow rate.")
        return False

    def set_mode(self, mode, dispenser=1):
        """
        Sets the mode to the dispenser. If auto, the fuel will be dispensed automatically when authorized.
        
        Args:
            mode: (str) The mode that the dispenser will be set to. Only auto and manual are supported.
            dispenser: (int) The number of the dispenser in which the mode will be set.
        
        Returns:
            True/False: (bool) True if the mode was successfully set. False if an invalid mode was selected or if there was any other error.

        Examples:
            >>> set_mode("auto")
                True
            >>> set_mode("manual", 3)
                True
            >>> set_mode("kinda manual")
                False
            >>> set_mode("auto", "not a dispenser")
                False
        """
        log.info(f"Set mode {mode} for dispenser #{dispenser}")
        if mode.lower() == "auto" or mode.lower() == "manual":
            result = self.get(f"/setmode/{mode}/{dispenser}")
        else:
            log.warning(f"The {mode} mode does not exist. Please select manual or auto.")
            return False
        if result['success']:
            return True
        log.warning(result['payload'])
        return False
    
    def set_sales_target(self, sales_type = "auth", target="20.00", dispenser=1):
        """
        Sets the sales target of the dispenser.
        
        Args:
            sales_type: (str) The target type. Can be auth (authorized amount), money (set money amount), volume (set volume amount), or random (random money amount)
            target: (str) A string representative of how much the user wants dispensed (money or volume). Only works with money or volume types.
            dispenser: (int) The number of the dispenser in which the sales target is set.
        
        Returns:
            True/False: (bool) True if the sales target was successfully set. False if an invalid type was entered or if there was any other error.

        Examples:
            >>> set_sales_target()
                True
            >>> set_sales_target("money")
                True
            >>> set_sales_target("money", "15.00")
                True
            >>> set_sales_target("volume", "25.00", 3)
                True
            >>> set_sales_target(dispenser = 2)
                True
            >>> set_sales_target("cash")
                False
            >>> set_sales_target("money", "stuff")
                False
            >>> set_sales_target("money", "10.00", "not a dispenser")
                False
        """
        log.info(f"Set dispenser {dispenser} with sales_type: {sales_type} and target: {target}")
        if sales_type.lower() not in ["auth", "money", "volume", "random"]:
            log.warning(f"{sales_type.lower()} is an invalid sales type. Please choose auth, money, volume, or random")
            return False

        results = self.get(f"/setsalestarget/{sales_type.lower()}/{target}/{dispenser}")

        if results['success'] and "false" not in results['payload']:
            return True
        if not results['success']:
            log.warning(results['payload'])

        return False

    @test_func
    def swipe_card(self, card_name="Visa", brand="Core", dispenser=1):
        """
        Swipes a selected card at the CRIND.
        
        Args:
            brand: (str) The brand of the store. NOTE: Different stores have different bin ranges.
            card_name: (str) The name of the card being used. NOTE: Please refer to app/data/CardData.json for card names and bins.
            dispenser: (int) The number of the dispenser that the card will be swiping at.
        
        Returns:
            True/False: (bool) True if the card was successfully swiped at the CRIND. False if there was any error.

        Examples:
            >>> swipe_card()
                True
            >>> swipe_card("Mastercard")
                True
            >>> swipe_card(brand = "Chevron")
                True
            >>> swipe_card("Discover", "Citgo" 2)
                True
            >>> swipe_card("Not a Card")
                False
            >>> swipe_card("VisaFleet", "Not a brand")
                False
            >>> swipe_card("MCFleet", dispenser = "not a dispenser")
                False
        """
        log.info(f"Swipe card {card_name} of {brand} brand for dispenser #{dispenser}")
        card_data = self._get_card_data(brand, card_name)
        result = self.post(f"/swipecard/{dispenser}", card_data)
        if result['success']:
            return True
        log.warning(f"Receieved the following Error: {result['payload']}")
        return False

    @test_func
    def insert_card(self, card_name="Visa", brand="Core", dispenser=1):
        """
        Swipes a selected card at the CRIND.
        
        Args:
            brand: (str) The brand of the store. NOTE: Different stores have different bin ranges.
            card_name: (str) The name of the card being used. NOTE: Please refer to app/data/CardData.json for card names and bins.
            dispenser: (int) The number of the dispenser that the card will be swiping at.
        
        Returns:
            True/False: (bool) True if the card was successfully swiped at the CRIND. False if there was any error.

        Examples:
            >>> swipe_card()
                True
            >>> swipe_card("Mastercard")
                True
            >>> swipe_card(brand = "Chevron")
                True
            >>> swipe_card("Discover", "Citgo" 2)
                True
            >>> swipe_card("Not a Card")
                False
            >>> swipe_card("VisaFleet", "Not a brand")
                False
            >>> swipe_card("MCFleet", dispenser = "not a dispenser")
                False
        """
        card_data = self._get_card_data(brand, card_name)
        result = self.post(f"/insertCard/{dispenser}", card_data)
        if result['success']:
            return True
        log.warning(f"Receieved the following Error: {result['payload']}")
        return False


    # region Unfinished
    #NOTE Need to see if these are needed.

    def get_money(self, dispenser):
        raise NotImplementedError

    def get_volume(self, dispenser):
        raise NotImplementedError


    def get_flow_rate(self, dispenser):
        raise NotImplementedError

    # endregion

    # region statics

    def crind_sale(self, card_name="Visa", brand="Core", debit="no", pin="1234", carwash="no", selection="1",
                   receipt="yes", target_type="auth", target_amount="10.00", grade=1, dispenser=1, 
                   vehicle_number="1234", id_number="1234", customer_code="1234", odometer="1234", driver_id="1234",  timeout=60):
        """
        Run a crind sale and answers all prompts. 
        NOTE: Support for Zip, Crind Merch not currently implemented
        NOTE: Add support for amount to dispense (Currently dispenses max)

        Args:
            card_name: (str) The name of the card being used. NOTE: Please refer to app/data/CardData.json for card names and bins.
            brand: (str) The brand of the store. NOTE: Different stores have different bin ranges.
            debit: (str) Answer to debit prompt.
            pin: (str) PIN to be entered
            carwash: (str) Answer to carwash prompt
            selection: (str) Answer to carwash package selection prompt NOTE: If carwash = "no" leaving this as "1" is ok
            receipt: (str) Answer to receipt prompt
            dispenser: (int) The number of the dispenser that the card will be swiping at.
            target_type: (str) Type to set sales target to (Auth, Money, Volume)
            target_amount: (str) Amount to set sales target to
            grade: (int) Grade to dispense
            vehicle_number: (str) Fleet prompt for vehicle number
            id_number: (str) Fleet prompt for ID Number
            customer_code: (str) Fleet prompt for customer code
            driver_id: (str) Fleet prompt for driver id/ driver number
            odometer: (str) Fleet prompt for odometer
            timeout: (int) The time given for the transaction to complete.
        Returns:
            True/False: (bool) True if CRIND sale was successful. False if there was any error.

        Examples:
            >>> crind_sale()
                True
            >>> crind_sale("Mastercard")
                True
            >>> crind_sale(card_name = "Discover", carwash = "yes", selection = "2")
                True
            >>> crind_sale("Not a Card")
                False
            >>> crind_sale("VisaFleet", "Not a brand")
                False
            >>> crind_sale("MCFleet", dispenser = "not a dispenser")
                False
        """
        start_time = time.time()
        # Loop verifies that crindsim is in idle state before starting transaction
        while time.time() - start_time < timeout:
            if "insert card" in self.get_display_text().lower():
                break
        else:
            log.warning("Unable to run transaction because CRIND is not at IDLE")
            return False

        # Loop that gets current crind display and answers any prompts
        start_time2 = time.time()
        previous_display = []
        while time.time() - start_time2 < timeout:
            display = self.get_display_text().lower()
            if not display == previous_display:
                log.debug(display)
            if "insert card" in display:
                self.swipe_card(card_name, brand, dispenser)
                log.debug("swiped " + card_name)
            elif "please see cashier" in display:
                log.warning("Customer instructed to see cashier")
                return False
            elif "vehicle number" in display:
                for digit in vehicle_number:
                    self.press_keypad(digit, dispenser)
                self.press_keypad("Enter", dispenser)
                log.debug("Vehicle Number Entered")
            elif "id number" in display:
                for digit in id_number:
                    self.press_keypad(digit, dispenser)
                self.press_keypad("Enter", dispenser)
                log.debug("ID Number Entered")
            elif "customer code" in display:
                for digit in customer_code:
                    self.press_keypad(digit, dispenser)
                self.press_keypad("Enter", dispenser)
                log.debug("Customer Code Entered")
            elif "driver" in display:
                for digit in driver_id:
                    self.press_keypad(digit, dispenser)
                self.press_keypad("Enter", dispenser)
                log.debug("Driver ID Entered")
            elif "odometer reading" in display:
                for digit in odometer:
                    self.press_keypad(digit, dispenser)
                self.press_keypad("Enter", dispenser)
                log.debug("Odometer Entered")
            elif "debit" in display:
                self.press_softkey(debit, dispenser)
                log.debug("Pressed " + debit + " for debit prompt")
            elif "pin" in display:
                for digit in pin:
                    self.press_keypad(digit, dispenser)
                self.press_keypad("Enter", dispenser)
                log.debug("PIN Entered")
            elif "carwash" in display:
                self.press_softkey(carwash, dispenser)
                log.debug("pressed " + carwash + " for carwash")
            elif "make selection" in display:
                self.press_softkey(selection, dispenser)
                log.debug("wash selected")
            elif "lift handle" in display and self.get_mode().lower() == "manual":
                self.fuel_manually(grade, target_type, target_amount, dispenser)
            elif "receipt?" in display:
                self.press_softkey(receipt, dispenser)
                log.debug("pressed " + receipt + " for receipt")
            elif "thank you" in display:
                log.debug("sale complete")
                return True
            previous_display = display

            time.sleep(1)
        log.warning("Transaction did not complete before timeout")
        return False

    def commercial(self, card_name="NGFC", brand="Exxon", selection="tractor", need_def="no", 
                   tractor_grade=1, tractor_target_type="auth", tractor_target_amount="10.00", 
                   reefer_grade=1, reefer_target_type="auth", reefer_target_amount="10.00",
                   def_grade=3, def_target_type="auth", def_target_amount="10.00",
                   receipt="yes", additional_product = "no", dispenser=1, timeout=60):
        """
        Run a commercial fuel sale at the crind and answers all prompts.

        Args:
            card_name: (str) The name of the card being used. NOTE: Please refer to app/data/CardData.json for card names and bins.
            brand: (str) The brand of the store. NOTE: Different stores have different bin ranges.
            selection: (str) Type of fuel to purchase (Tractor, Reefer, Both)
            need_def: (str) Answer to the Need DEF? prompt
            tractor_grade: (int) Grade to dispense for Tractor
            tractor_taget_type: (str) Type to send to set_sale_target for Tractor (Auth, Money, Volume)
            tractor_target_amount: (str) Amount to set sales target to for Tractor
            reefer_grade: (int) Grade to dispense for Tractor
            reefer_taget_type: (str) Type to send to set_sale_target for Reefer (Auth, Money, Volume)
            reeger_target_amount: (str) Amount to set sales target to for Reefer
            def_grade: (int) Grade to dispense for Tractor
            def_taget_type: (str) Type to send to set_sale_target for DEF (Auth, Money, Volume)
            def_target_amount: (str) Amount to set sales target to for DEF
            receipt: (str) Answer to receipt prompt
            additional_product: (str) Answer to additional product prompt
            dispenser: (int) The number of the dispenser that the card will be swiping at.
            timeout: (int) The time given for the transaction to complete.
        Returns:
            True/False: (bool) True if CRIND sale was successful. False if there was any error or if the customer was told to go inside.

        Examples:
            >>> commercial_sale()
                True
            >>> commercial_sale("Mastercard")
                True
            >>> commercial_sale(selection = "Reefer", need_def = "yes")
                True
            >>> commercial_sale("Not a Card")
                False
            >>> commercial_sale("VisaFleet", "Not a brand")
                False
            >>> commecial_sale("MCFleet", dispenser = "not a dispenser")
                False
        """
        
        #set crindsim mode to manual as auto mode will not allow grades to be changed for commercial fueling
        self.set_mode("manual")
        start_time = time.time()
        # Loop verifies that crindsim is in idle state before starting transaction
        while time.time() - start_time < timeout:
            if "insert card" in self.get_display_text().lower():
                break
        else:
            log.warning("Unable to run transaction because CRIND is not at IDLE")
            return False

        # Loop that gets current crind display and answers any prompts
        start_time2 = time.time()
        previous_display = []
        while time.time() - start_time2 < timeout:
            display = self.get_display_text().lower()
            if not display == previous_display:
                log.debug(display)
            if "insert card" in display:
                self.swipe_card(card_name, brand, dispenser)
                log.debug("swiped " + card_name)
            elif "please see cashier" in display:
                log.warning("Customer instructed to see cashier")
                return False
            elif "make selection" in display:
                self.press_softkey(selection, dispenser)
                log.debug(selection + " selected")
            elif "need def?" in display:
                self.press_softkey(need_def, dispenser)
                log.debug(need_def + " entered for Need DEF?")
            elif "additional products" in display:
                self.press_softkey(additional_product)
                log.debug(additional_product + " selected for Additional Products?")
            elif "ready to fuel tractor" in display:
                self.fuel_manually(tractor_grade, tractor_target_type, tractor_target_amount, dispenser)
            elif "ready to fuel def" in display:
                self.fuel_manually(def_grade, def_target_type, def_target_amount, dispenser)
            elif "ready to fuel reefer" in display:
                self.fuel_manually(reefer_grade, reefer_target_type, reefer_target_amount, dispenser)
            elif "receipt?" in display:
                self.press_softkey(receipt, dispenser)
                log.debug("pressed " + receipt + " for receipt")
            elif "thank you" in display:
                log.debug("sale complete")
                return True
            previous_display = display

            time.sleep(1)
        log.warning("Transaction did not complete before timeout")
        return False

    def fuel_manually(self, grade= 1, target_type="auth", amount="10.00", dispenser=1, dispense_time = 5):       
        """
        Used to dispense fuel for a crindsim that is set to manual mode
        NOTE: Support for Zip, Crind Merch not currently implemented
        NOTE: Add support for amount to dispense (Currently dispenses max)

        Args:
            dispenser: (int) The number of the dispenser that the card will be swiping at.
            target_type: (str) Type to set sales target to (Auth, Money, Volume)
            target_amount: (str) Amount to set sales target to
            grade: (int) Grade to dispense
            dispense_time: (int) Amount of time you would like to allow the crindsim to dispense fuel
        Returns:
            True/False: (bool) True if fuel was dispensed. False if there was any error.

        Examples:
            >>> fuel_manually()
                True
            >>> fuel_manually(grade = 2)
                True
            >>> fuel_manually(target_type="money", target_amount="20.00")
                True
        """
        if target_type == "auth":
            self.set_sales_target("auth")     
        else:
            self.set_sales_target(target_type, amount)
        self.select_grade(grade, dispenser)
        self.lift_handle()
        self.open_nozzle()
        time.sleep(dispense_time)
        self.lower_handle()
        return True

    @staticmethod
    def setup_edh(num_dispensers, ip="10.80.31.210"):
        """
        Sets up the needed registry keys for the EDH to accept the CRIND Sim
        Args:
            num_dispensers: (int) The number of dispensers to setup
            ip: (str) The IP address where the CRIND Sim is running. Default value: 10.80.31.210
        Returns:
            None
        Example:
            >>> setup_edh(4)
        """
        crindsim_root = r'HKLM\%s\Debug\TWOIPIPTest' % (constants.CRIND_SUBKEY)
        tls_type = r'reg add HKLM\%s /v TWOIPIPConnection /t REG_SZ /d TLSNoAuth /f' \
                   % (constants.SECURE_SUBKEY)
        run_sqlcmd(tls_type)

        key_4 = r'reg add HKLM\%s\4 /f' % (crindsim_root)
        run_sqlcmd(key_4)

        key_5 = r'reg add %s\5 /f' % (crindsim_root)
        run_sqlcmd(key_5)

        for i in range(int(num_dispensers)):
            string_4 = r'reg add %s\4 /v %s /t REG_SZ /d default /f' \
                       % (crindsim_root, str(i + 1))
            run_sqlcmd(string_4)

        IP = r'reg add %s\4 /v defaultip /t REG_SZ /d %s /f' \
             % (crindsim_root, ip)
        run_sqlcmd(IP)

        Port = r'reg add %s\4 /v defaultport /t REG_DWORD /d 0x000012c0 /f' \
               % (crindsim_root)
        run_sqlcmd(Port)
        edh = EDH.EDH()
        edh.restart()

    # endregion