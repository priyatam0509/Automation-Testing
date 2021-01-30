"""
    File name: click_test.py.py
    Tags:
    Description: 
    Author: 
    Date created: 2019-05-16 13:55:23
    Date last modified: 
    Python Version: 3.7
"""

import logging, datetime
from app import Navi, mws, pos, system, employee, site_options
from app.framework.tc_helpers import setup, test, teardown, tc_fail

empl_cfg = { "General": {
                "First Name": "John",
                "Last Name": "Titor",
                "Operator ID": "2010",
                "Birth Date": "05/01/1975" },
             "Security": {
                "Security Group": "Owner" }
            }

class click_test:
    """
    Description: Test class that provides an interface for testing.
    """

    def __init__(self):
        """Initializes the Template class.
        Args: None
        Returns: None
        """
        # The logging object. 
        # Example: self.log.info(f"Current value of var: {my_var}")
        self.log = logging.getLogger()

    @setup
    def setup(self):
        """Performs any initialization that is not default.
        Args: None
        Returns: None
        """
        if not system.restore_snapshot():
            raise Exception

        Navi.navigate_to("Site Options")
        site_options.SiteOptions().setup({"Pricing Levels": {"pricing is enabled": "Cash/Credit"}})

        # TODO: Set up crind sim on EDH, when we have support for it.

        Navi.navigate_to("Employee")
        employee.Employee().add(empl_cfg)

        # TODO: Rewrite this when we have a Reminder Maintenance class
        Navi.navigate_to("Reminder Maintenance")
        mws.click_toolbar("Add")
        mws.set_value("Task:", "stuff")
        mws.set_value("Message:", "Turn on the TV.")
        mws.set_value("POS", True)
        mws.set_value("Enabled (run at scheduled time)", True)
        mws.select_tab("Schedule")
        time = (datetime.datetime.now() + datetime.timedelta(minutes=3)).strftime("%H:%M %p")
        time.replace(' ', '{RIGHT}') # Need a right keystroke to get to AM/PM
        mws.get_control("Start Time:").click(coords=(10,0)) # Click on the hour segment first
        mws.get_control("Start Time:").send_keystrokes(time) 
        mws.click_toolbar("Save")

        Navi.navigate_to("POS")

    @test
    def pwd_keys(self):
        """Verify that we can interact with password keys (by signing on)."""
        pos.sign_off()
        pos.sign_on(['2010', 'OSHMKUFA'])

    @test
    def reminder(self):
        """Verify that we can click on reminder pop-ups."""
        pos.click("OK", timeout=300) # Click OK when the reminder appears

    @test
    def keypad(self):
        """Verify that we can interact with the POS keypad.
        Args: None
        Returns: None
        """
        # Test number key
        pos.click('1')
        keypad_entry = pos.read_keypad_entry()
        if keypad_entry != '1':
            tc_fail(f"1 was not found in the keypad entry. Found: '{keypad_entry}'")
        # Test function key
        pos.click('CANCEL')
        keypad_entry = pos.read_keypad_entry()
        if keypad_entry != '':
            tc_fail(f"Keypad entry was not empty after clicking CANCEL. Found: '{keypad_entry}'")

    @test
    def speed_dept_keys(self):
        """Verify that we can click speed keys and department keys,
        and that click correctly disambiguates the two."
        Args: None
        Returns: None
        """
        # Change to dept keys to force implicit menu switch in next call
        pos.click("DEPT KEY")
        # Test speed key, with implicit menu switch
        pos.click("GENERIC ITEM")
        if not any(["Generic Item" in line for line in pos.read_transaction_journal()]):
            tc_fail("Generic Item wasn't added to the transaction journal by click().")
        # Test dept key, with implicit menu switch
        pos.click("DEPT 5")
        status = pos.read_status_line()
        if "Dept 5 selected" not in status:
            tc_fail(f"DEPT 5 wasn't selected by click(). Status message: {status}")

    @test
    def message_box(self):
        """Verify that we can read and interact with a popup message box.
        Args: None
        Returns: None
        """
        pos.click("VOID TRANS")
        msg = pos.read_message_box()
        if msg != "Are you sure that you want to void the transaction?":
            tc_fail(f"read_message_box() didn't return void transaction confirmation prompt. Actual read: {msg}")
        pos.click_message_box_key("YES")
        msg = pos.read_message_box()
        if msg is not None:
            tc_fail(f"read_message_box() didn't return None following click_message_box_key('YES'). Actual read: {msg}")
        if [" **  Trans Voided  **"] not in pos.read_transaction_journal():
            tc_fail(f"The transaction wasn't voided following click_message_box_key('YES').")

    @test
    def func_keys(self):
        """Verify that we can interact with the POS function keys,
        and that implicit navigation works.
        Args: None
        Returns: None
        """
        # Forward nav
        pos.click('CLEAN')
        pos.click_message_box_key('NO')
        # Backward nav
        pos.click("NO SALE")
        if ["No sale transaction"] not in pos.read_transaction_journal():
            tc_fail(f"No sale wasn't found in the journal after clicking the button.")

    @test
    def tools_keys(self):
        """Verify that we can interact with the keys in the Tools menu."""
        pos.click("TOOLS")
        pos.click("BACK")
        pos.click_function_key("BACK")

    @test
    def forecourt_keys(self):
        """Verify that we can interact with the forecourt GUI and fuel-related keys."""
        pos.select_dispenser(1)
        pos.select_dispenser(3)
        pos.click("DIAG")
        diag = pos.read_dispenser_diag()
        exp_diag_elements = ["DISPENSER", "STATUS", "PRINTER", "CRIND", "DOOR/BILLS"]
        for elt in exp_diag_elements:
            if elt not in diag:
                tc_fail(f"Didn't find {elt} in dispenser diag.")
        pos.click("GO BACK")
        pos.click("AUTH")
        if pos.read_status_line() != "Authorizing dispenser # 3 For fillup.":
            tc_fail("Didn't find auth message after clicking AUTH or dispenser 3 wasn't selected.")

        pos.click("PREPAY")
        pos.click("$10.00")
        if not ["REGULAR CR ON 3", "$10.00"] in pos.read_transaction_journal():
            tc_fail("Didn't find fuel in the transaction journal after trying to do a prepay.")
        pos.click("VOID TRANS")
        pos.click("YES")
        
        pos.click("MANUAL")
        pos.click("CASH LEVEL")
        pos.click("$10.00")
        pos.click("REGULAR")
        if not any([("REGULAR CA ON 3" in line and "$10.00" in line) for line in pos.read_transaction_journal()]):
            tc_fail("Didn't find fuel in the transaction journal after trying to do a manual sale at cash level.")
        pos.click("VOID TRANS")
        pos.click("YES")


    @test
    def dispenser_keys(self):
        """Verify that we can interact with dispenser and attendant menu keys."""
        pos.click("DISPENSER")
        pos.click("FUEL PRICE CHANGE")
        if pos.read_status_line() != "Changing fuel prices ... Please wait.":
            tc_fail("Didn't get price change message after trying to click FUEL PRICE CHANGE.")
        system.wait_for(pos.read_status_line, "Changes sent, system may take up to 30 seconds to reflect changes.", timeout=60)
        pos.click("ATTENDED OPTIONS")
        pos.enter_keypad("91")
        pos.click("Enter")
        pos.enter_keypad("91")
        pos.click("OK")
        pos.click("YES")
        pos.click("ENTER")
        pos.click("Activate Token")
        if pos.read_status_line() != "Swipe token or enter token identifier":
            tc_fail("Didn't get activate token message after trying to click Activate Token.")
        pos.click("Cancel")
        pos.click("Close Till")
        system.wait_for(pos.read_status_line, "Make a selection from the above menu.", timeout=60)
        pos.click("Go Back")
        if pos.read_status_line() != "Please enter the department items.":
            tc_fail("Didn't return to idle after trying to navigate out of attendant menu.")

    @test
    def local_accounts_keys(self):
        """Verify that we can interact with keys in the local accounts interface."""
        pos.click("LOC ACCT PAID IN")
        pos.click("DETAILS")
        pos.click("OK")
        pos.click("CANCEL")
        if pos.read_status_line() != "Please enter the department items.":
            tc_fail("Didn't return to idle after trying to navigate out of local accounts menu.")

    @teardown
    def teardown(self):
        """Performs cleanup after this script ends.
        Args: None
        Returns: None
        """
        # delete pass after you implement.
        pass