"""
    File name: POS_Discount.py
    Tags:
    Description: Script for testing the functionality of discounts in HTML POS.
    Author: David Mayes
    Date created: 2020-06-09
    Date last modified: 
    Python Version: 3.7
"""

import logging, time
from app import Navi, mws, pos, system
from app.framework.tc_helpers import setup, test, teardown, tc_fail
from app.features import discount

default_timeout = 10

class POS_Discount():
    """
    Class for testing discount button
    """

    def __init__(self):
        """
        Initializes the POS_Discount class
        """
        # The logging object. 
        # Example: self.log.info(f"Current value of var: {my_var}")
        self.log = logging.getLogger()
        self.short_wait_time = 1
        self.long_wait_time = 20
        self.quick_void = pos.controls['receipt journal']['quick_void']


    @setup
    def setup(self):
        """
        Performs initialization
        """
        # if not system.restore_snapshot():
        #     self.log.debug("No snapshot to restore, if this is not expected please contact automation team")
        mws.sign_on()
        
        # Make a change to one of the discounts so it can be tested
        disc_maint = {
            "Discount Name" : "Std_Item_Price",
            "General" : {
                "Standard" : True,
                "Standard Discount Options Text Box": "400"
            }
        }

        d = discount.DiscountMaintenance()
        d.change("Std_Item_Price", disc_maint)

        pos.connect()
        pos.sign_on()


    @test
    def trans_no_discount_item(self):
        """
        Do transaction discounts without any discountable items
        and make sure the discounts are $0.00
        """
        # Start transaction
        self.log.info("Starting a transaction...")
        pos.click("Item 9")
        pos.click("Item 9")

        # Make sure journal is updated
        if not self._number_of_journal_items(2):
            tc_fail("Journal did not update after adding two Item 9's.")

        # Add transaction discounts
        if not self._apply_transaction_discounts():
            self._return_to_main_screen()
            tc_fail("Failed to apply all transaction discounts correctly.")

        # Check that all of the discounts are 0 and that the total is unaffected
        if not self._on_transaction_screen():
            tc_fail("Did not return to the main transaction screen.")

        journal = pos.read_transaction_journal()
        if journal == None:
            tc_fail("Transaction journal not populated.")

        j = journal[2:]
        for item in j:
            if "." in item[1]:
                if not item[1] == "$0.00":
                    self._return_to_main_screen()
                    tc_fail(item[0] + " for " + item[1] + " appeared as a discount.  All discounts should be $0.00.")
        
        self.log.info("All discounts are correctly listed as $0.00...")

        total = pos.read_balance()["Total"]
        total_price = "$" + format(round(float(journal[0][1][1:]) + float(journal[1][1][1:])), '.2f')
        if not total_price == total:
            self._return_to_main_screen()
            tc_fail("Total was listed as " + total + ".  It should be listed at " + total_price + ".")

        self.log.info("Transaction discounts with non-discountable items worked as intended!")

        self._return_to_main_screen()


    @test
    def trans_discount_item(self):
        """
        Do transaction discounts with discountable items
        in the transaction and make sure the amounts are correct
        """
        # Make sure we're on the main screen
        self._return_to_main_screen()

        # Start transaction
        self.log.info("Starting a transaction...")
        pos.click("Item 8")
        pos.click("Item 8")

        # Make sure journal is updated
        if not self._number_of_journal_items(2):
            tc_fail("Journal did not update after adding two Item 8's.")

        # Add transaction discounts
        if not self._apply_transaction_discounts():
            self._return_to_main_screen()
            tc_fail("Failed to apply all transaction discounts correctly.")
        
        if not self._on_transaction_screen():
            tc_fail("Did not return to the main transaction screen.")

        # Check that all of the discounts are listed correctly and the total is affected
        if not self._number_of_journal_items(6):
            tc_fail("Failed to show all discounts in the transaction journal.")
        
        if not self._all_prices_present():
            tc_fail("Transaction journal failed to update fully.")

        journal = pos.read_transaction_journal()

        if not journal[2][1] == "-$1.00":
            tc_fail(journal[2][0] + " " + journal[2][1] + " should have been Std_Trans_Amt -$1.00.")
        if not journal[3][1] == "-$1.00":
            tc_fail(journal[3][0] + " " + journal[3][1] + " should have been Std_Trans_Pct -$1.00.")
        if not journal[4][1] == "-$0.10":
            tc_fail(journal[4][0] + " " + journal[4][1] + " should have been Var_Trans_Amt -$0.10.")
        if not journal[5][1] == "-$1.00":
            tc_fail(journal[5][0] + " " + journal[5][1] + " should have been Var_Trans_Pct -$1.00.")
        
        total = pos.read_balance()["Total"]
        if not total == "$6.90":
            self._return_to_main_screen()
            tc_fail("Total was " + total + ".  It should have been $6.90.")

        self.log.info("Transaction discounts with discountable items worked as intended!")

        self._return_to_main_screen()


    @test
    def trans_both_items(self):
        """
        Do transaction discounts with both a non-discountable and
        discountable item and make sure the amounts are correct
        """
        # Make sure we're on the main screen
        self._return_to_main_screen()

        # Start transaction
        self.log.info("Starting a transaction...")
        pos.click("Item 9")
        pos.click("Item 8")

        # Make sure journal is updated
        if not self._number_of_journal_items(2):
            tc_fail("Journal did not update after adding one Item 8 and one Item 9.")

        # Add transaction discounts
        if not self._apply_transaction_discounts():
            self._return_to_main_screen()
            tc_fail("Failed to apply all transaction discounts correctly.")
        
        if not self._on_transaction_screen():
            tc_fail("Did not return to the main transaction screen.")

        # Check that all of the discounts are listed correctly and the total is affected
        if not self._number_of_journal_items(6):
            tc_fail("Failed to show all discounts in the transaction journal.")
        
        if not self._all_prices_present():
            tc_fail("Transaction journal failed to update fully.")

        journal = pos.read_transaction_journal()

        if not journal[2][1] == "-$1.00":
            tc_fail(journal[2][0] + " " + journal[2][1] + " should have been Std_Trans_Amt -$1.00.")
        if not journal[3][1] == "-$0.50":
            tc_fail(journal[3][0] + " " + journal[3][1] + " should have been Std_Trans_Pct -$0.50.")
        if not journal[4][1] == "-$0.10":
            tc_fail(journal[4][0] + " " + journal[4][1] + " should have been Var_Trans_Amt -$0.10.")
        if not journal[5][1] == "-$0.50":
            tc_fail(journal[5][0] + " " + journal[5][1] + " should have been Var_Trans_Pct -$0.50.")
        
        total = pos.read_balance()["Total"]
        if not total == "$7.90":
            self._return_to_main_screen()
            tc_fail("Total was " + total + ".  It should have been $7.90.")

        self.log.info("Transaction discounts with both discountable and non-discountable items worked as intended!")

        self._return_to_main_screen()


    @test
    def item_after(self):
        """
        Add a discountable item after adding transaction discounts
        and make sure the discount amounts update
        """
        # Make sure we're on the main screen
        self._return_to_main_screen()

        # Start transaction
        self.log.info("Starting a transaction...")
        pos.click("Item 8")

        # Make sure journal is updated
        if not self._number_of_journal_items(1):
            tc_fail("Journal did not update after adding one Item 8.")

        # Add transaction discounts
        if not self._apply_transaction_discounts():
            self._return_to_main_screen()
            tc_fail("Failed to apply all transaction discounts correctly.")

        if not self._on_transaction_screen():
            tc_fail("Did not return to the main transaction screen.")

        # Check that all of the discounts are listed correctly and the total is correct        
        if not self._number_of_journal_items(5):
            tc_fail("Failed to show all discounts in the transaction journal.")

        if not self._all_prices_present():
            tc_fail("Transaction journal failed to update fully.")

        journal = pos.read_transaction_journal()

        if not journal[1][1] == "-$1.00":
            tc_fail(journal[1][0] + " " + journal[1][1] + " should have been Std_Trans_Amt -$1.00.")
        if not journal[2][1] == "-$0.50":
            tc_fail(journal[2][0] + " " + journal[2][1] + " should have been Std_Trans_Pct -$0.50.")
        if not journal[3][1] == "-$0.10":
            tc_fail(journal[3][0] + " " + journal[3][1] + " should have been Var_Trans_Amt -$0.10.")
        if not journal[4][1] == "-$0.50":
            tc_fail(journal[4][0] + " " + journal[4][1] + " should have been Var_Trans_Pct -$0.50.")
        
        total = pos.read_balance()["Total"]
        if not total == "$2.90":
            self._return_to_main_screen()
            tc_fail("Initial total with one item was " + total + ".  It should have been $7.90.")

        # Add another discountable item
        self.log.info("Adding another discountable item...")
        pos.click("Item 8")

        # Wait for transaction journal to update before checking prices
        start_time = time.time()
        while time.time() - start_time <= default_timeout:
            x = 0
            for item in pos.read_transaction_journal():
                if "Item 8" in item[0]:
                    x += 1
            if x == 2:
                break
        else:
            tc_fail("Transaction journal failed to update.")

        if not self._number_of_journal_items(6):
            tc_fail("Transaction journal not populated with 6 objects after adding 1 Item 8, 4 discounts, and another Item 8.")

        journal = pos.read_transaction_journal()
        
        # Check that all of the discounts have changed to the correct value
        # and the total has been updated
        if not journal[2][1] == "-$1.00":
            tc_fail(journal[2][0] + " " + journal[2][1] + " should have been Std_Trans_Amt -$1.00.")
        if not journal[3][1] == "-$1.00":
            tc_fail(journal[3][0] + " " + journal[3][1] + " should have been Std_Trans_Pct -$1.00.")
        if not journal[4][1] == "-$0.10":
            tc_fail(journal[4][0] + " " + journal[4][1] + " should have been Var_Trans_Amt -$0.10.")
        if not journal[5][1] == "-$1.00":
            tc_fail(journal[5][0] + " " + journal[5][1] + " should have been Var_Trans_Pct -$1.00.")
        
        total = pos.read_balance()["Total"]
        if not total == "$6.90":
            self._return_to_main_screen()
            tc_fail("Initial total with one item was " + total + ".  It should have been $6.90.")

        self.log.info("Adding a discountable item to a transaction with discounts updated the journal correctly!")

        self._return_to_main_screen()


    @test
    def non_discountable_item(self):
        """
        Make sure you can't discount a non-discountable item
        """
        # Make sure we're on the main screen
        self._return_to_main_screen()

        # Start transaction
        self.log.info("Starting a transaction...")
        pos.click("generic item")

        pos.click("discount")
        if self._is_discountable_item():
            self._return_to_main_screen()
            tc_fail("HTML POS thinks the Generic Item is discountable when it is configured to be non-discountable.")

        self.log.info("Can't discount a non-discountable item!")

        self._return_to_main_screen()


    @test
    def discountable_item(self):
        """
        Make sure you can discount a discountable item
        """
        # Make sure we're on the main screen
        self._return_to_main_screen()

        # Start transaction
        self.log.info("Starting a transaction...")
        pos.click("Item 8")

        if not self._apply_item_discounts(price=5.00):
            self._return_to_main_screen()
            tc_fail("Did not successfully apply all item discounts.")

        self.log.info("Applied item discounts to a discountable item!")

        self._return_to_main_screen()


    @test
    def void_discount(self):
        """
        Void a transaction discount
        """
        # Make sure we're on the main screen
        self._return_to_main_screen()

        # Start transaction
        self.log.info("Starting a transaction...")
        pos.click("Item 8")

        # Void discount with quick void button
        pos.click("discount")
        pos.click("transaction")
        if not self._list_loaded("Std_Trans_Amt"):
            self._return_to_main_screen()
            tc_fail("'Std_Trans_Amt' was not in the selection list.")
        pos.select_list_item("Std_Trans_Amt")
        pos.click("enter")

        if not self._on_transaction_screen():
            tc_fail("Did not return to the main transaction screen.")

        pos.click_journal_item("Std_Trans_Amt")
        if pos.is_element_present(self.quick_void):
            pos.click_key(self.quick_void)
        else:
            tc_fail("Could not click quick void.")

        if not self._number_of_journal_items(1):
            self._return_to_main_screen()
            tc_fail("Transaction journal should only have Item 8 in it.  Dump of transaction journal: " + str(pos.read_transaction_journal()))
        else:
            self.log.info("Voided discount with quick void button...")

        total = pos.read_balance()["Total"]
        if not total == "$5.00":
            self._return_to_main_screen()
            tc_fail("Voiding transaction discount via quick void did not update transaction total.  Should be $5.00, but instead was " + total)

        # Void discount with void item button
        pos.click("discount")
        pos.click("transaction")
        if not self._list_loaded("Std_Trans_Amt"):
            self._return_to_main_screen()
            tc_fail("'Std_Trans_Amt' was not in the selection list.")
        pos.select_list_item("Std_Trans_Amt")
        pos.click("enter")

        if not self._on_transaction_screen():
            tc_fail("Did not return to the main transaction screen.")

        pos.click_journal_item("Std_Trans_Amt")
        pos.click("void item")

        if not self._number_of_journal_items(1):
            self._return_to_main_screen()
            tc_fail("Transaction journal should only have Item 8 in it.  Dump of transaction journal: " + str(pos.read_transaction_journal()))
        else:
            self.log.info("Voided discount with void item button...")

        total = pos.read_balance()["Total"]
        if not total == "$5.00":
            self._return_to_main_screen()
            tc_fail("Voiding transaction discount via quick void did not update transaction total.  Should be $5.00, but instead was " + total)

        self.log.info("Successfully voided discount!")

        self._return_to_main_screen()


    @test
    def void_discounted_item(self):
        """
        Void a discounted item
        """
        # Make sure we're on the main screen
        self._return_to_main_screen()

        # Start transaction
        self.log.info("Starting a transaction...")
        pos.click("Item 8")

        # Void with quick void button
        pos.click("discount")
        pos.click("item")
        if not self._list_loaded("Std_Item_Amt"):
            self._return_to_main_screen()
            tc_fail("'Std_Item_Amt' was not in the selection list.")
        pos.select_list_item("Std_Item_Amt")
        pos.click("enter")

        if not self._on_transaction_screen():
            tc_fail("Did not return to the main transaction screen.")

        pos.click_journal_item("Item 8")
        if pos.is_element_present(self.quick_void):
            pos.click_key(self.quick_void)
        else:
            tc_fail("Could not click quick void.")

        if not self._number_of_journal_items(0):
            self._return_to_main_screen()
            tc_fail("Transaction journal should have no items in it.  Dump of transaction journal: " + str(pos.read_transaction_journal()))
        else:
            self.log.info("Voided discounted item with quick void button...")

        total = pos.read_balance()["Total"]
        if not total == "$0.00":
            self._return_to_main_screen()
            tc_fail("Voiding discounted item via quick void did not update transaction total.  Should be $0.00, but instead was " + total)

        # Add item again, since transaction is now empty
        pos.click("Item 8")

        # Void with void item button
        pos.click("discount")
        pos.click("item")
        if not self._list_loaded("Std_Item_Amt"):
            self._return_to_main_screen()
            tc_fail("'Std_Item_Amt' was not in the selection list.")
        pos.select_list_item("Std_Item_Amt")
        pos.click("enter")

        if not self._on_transaction_screen():
            tc_fail("Did not return to the main transaction screen.")

        pos.click("void item")

        if not self._number_of_journal_items(0):
            self._return_to_main_screen()
            tc_fail("Transaction journal should have no items in it.  Dump of transaction journal: " + str(pos.read_transaction_journal()))
        else:
            self.log.info("Voided discounted item with void item button...")

        total = pos.read_balance()["Total"]
        if not total == "$0.00":
            self._return_to_main_screen()
            tc_fail("Voiding discounted item via void item did not update transaction total.  Should be $0.00, but instead was " + total)

        self.log.info("Successfully voided discounted item!")

        self._return_to_main_screen()


    @test
    def clear_journal(self):
        """
        Make sure clearing the transaction journal gets rid of all transaction discounts
        """
        # Make sure we're on the main screen
        self._return_to_main_screen()

        # Start transaction
        self.log.info("Starting a transaction...")
        pos.click("Item 8")

        # Add transaction discounts
        self._apply_transaction_discounts()

        if not self._on_transaction_screen():
            tc_fail("Did not return to the main transaction screen.")

        # Void item
        pos.click_journal_item("Item 8")
        pos.click_key(self.quick_void)

        if not self._number_of_journal_items(0):
            self._return_to_main_screen()
            tc_fail("Transaction journal should have no items in it.  Dump of transaction journal: " + str(pos.read_transaction_journal()))
        else:
            self.log.info("Voided discounted item with quick void button and transaction discounts disappeared...")

        # Add item again, since transaction is now empty
        pos.click("Item 8")

        # Add transaction discounts
        self._apply_transaction_discounts()

        if not self._on_transaction_screen():
            tc_fail("Did not return to the main transaction screen.")

        # Void item
        pos.click("void item")

        if not self._number_of_journal_items(0):
            self._return_to_main_screen()
            tc_fail("Transaction journal should have no items in it.  Dump of transaction journal: " + str(pos.read_transaction_journal()))
        else:
            self.log.info("Voided discounted item with void item button and transaction discounts disappeared...")

        total = pos.read_balance()["Total"]
        if not total == "$0.00":
            self._return_to_main_screen()
            tc_fail("Voiding discounted item via void item did not update transaction total.  Should be $0.00, but instead was " + total)

        self.log.info("HTML POS correctly cleared the transation discounts when the transaction was made empty!")

        self._return_to_main_screen()


    @teardown
    def teardown(self):
        """
        Performs cleanup after this script ends.
        """
        pos.close()

        # Restore changed setting
        disc_maint = {
            "Discount Name" : "Std_Item_Price",
            "General" : {
                "Standard" : True,
                "Standard Discount Options Text Box": "500"
            }
        }

        d = discount.DiscountMaintenance()
        d.change("Std_Item_Price", disc_maint)


    def _apply_transaction_discounts(self, timeout=default_timeout):
        """
        Helper function for applying all transaction discounts
        """
        # List of transaction discount names
        discounts = ["Std_Trans_Amt", "Std_Trans_Pct", "Var_Trans_Amt",\
         "Var_Trans_Pct"]
        discount_tracker = discounts.copy()
        self._on_transaction_screen()
        journal = pos.read_transaction_journal()
        if journal == None:
            index = 0
        else:
            index = len(journal)
        
        # Apply the discounts
        self.log.info("Applying all transaction discounts...")
        for discount in discounts:
            if "st" in discount[:2].lower() or "var" in discount[:3].lower():
                pos.click("discount")
                if self._is_discountable_item():
                    if not pos.click("transaction"):
                        system.log.warning("Failed to click the transaction keypad button on " + discount + " transaction.")
                        break
                if not self._list_loaded(discount):
                    self.log.warning("Dump of selection list: " + str(pos.read_list_items()))
                    self._return_to_main_screen()
                    tc_fail("Did not find '" + discount + "' in selection list.")
                pos.select_list_item(discount)
                pos.click("enter")
                if "var" in discount[:3].lower() and not pos.read_status_line() == '':
                    pos.enter_keypad("10", after="enter")
                if self._status_line_blank():
                    self.log.info(discount + " added successfully...")
                    discount_tracker.remove(discount)
                else:
                    self.log.warning(discount + " NOT added!")            

        # Check whether all discounts were applied
        if len(discount_tracker) == 0:
            # Check that the discounts showed up in the transaction journal
            self._on_transaction_screen()
            journal = pos.read_transaction_journal()
            for discount in discounts:
                if "var" in discount.lower() and "pct" in discount.lower():
                    discount = "10% " + discount
                if not journal[index][0] == discount:
                    self.log.warning(discount + " was not displayed correctly in the transaction journal!  Instead of " + discount + " it was " + journal[index][0] + ".")
                    return False
                index += 1
            self.log.info("Transaction discounts successfully applied...")
            return True
        else:
            discount_string = "The following discounts were NOT added: "
            for discount in discount_tracker:
                discount_string += discount + ", "
            self.log.warning(discount_string[:-2])
            return False

    
    def _apply_item_discounts(self, price=5.00):
        """
        Helper function for applying all item discounts
        """
        start_time = time.time()
        while time.time() - start_time <= default_timeout:
            if float(pos.read_balance()["Total"][1:]) > 0.01:
                total_price = float(pos.read_balance()["Total"][1:])
                break
        else:
            self.log.warning("Total price did not update.  Total price was listed as " + pos.read_balance()["Total"][1:])
            return False

        selected_item = pos.read_transaction_journal(only_selected=True)
        if len(selected_item) < 1:
            self.log.warning("No item selected!")
            return False
        
        # Make sure item is discountable
        pos.click("discount")
        if not self._is_discountable_item():
            self.log.warning(selected_item[0] + " is not able to be discounted!")
            return False

        # Apply discounts
        self.log.info("Applying item discounts...")
        discount_total = 0

        # Var_Item_Pct
        if not self._list_loaded("Var_Item_Pct"):
            self._return_to_main_screen()
            tc_fail("'Var_Item_Pct' was not in the selection list.")
        pos.select_list_item("Var_Item_Pct")
        pos.click('enter')

        if not pos.read_status_line() == "":
            pos.enter_keypad("1", after="enter")
        else:
            self.log.warning("Failed to add Var_Item_Pct discount!")
            return False

        self._on_transaction_screen()

        if not self._journal_updated(original_number=1):
            self.log.warning("Var_Item_Pct discount not displayed in transaction journal!")
            return False

        journal = pos.read_transaction_journal()
        
        try:
            discount_name = journal[1][0]
            discount = journal[1][1]
        except IndexError:
            self.log.warning("Var_Item_Pct did not show up correctly in the transaction journal!")

        if pos.read_transaction_journal(only_selected=True) == None:
            self.log.warning("No item selected after adding Var_Item_Pct discount!")
            return False
        elif not discount_name == "1% Var_Item_Pct":
            self.log.warning("Discount should say 1% Var_Item_Pct.  Instead it says " + discount_name)
            return False
        elif not discount == "-$" + format(round(price * 0.01, 2), '.2f'):
            self.log.warning("Var_Item_Pct discount should be -$" + format(round(price * 0.01, 2), '.2f') + ".  Instead it was " + discount)
            return False

        if not pos.read_balance()["Total"] == "$" + format(round(total_price - (price * 0.01), 2), '.2f'):
            self.log.warning("Total should be $" + format(round(total_price - (price * 0.01), 2), '.2f') + " after Var_Item_Pct discount.  Instead, it was " + pos.read_balance()["Total"] + "!")
            return False
        else:
            discount_total += price * 0.01
            total_price -= (price * 0.01)

        self.log.info("Var_Item_Pct discount added...")
            
        # Var_Item_Amt
        pos.click("discount")
        if not self._list_loaded("Var_Item_Amt"):
            self._return_to_main_screen()
            tc_fail("'Var_Item_Amt' was not in the selection list.")
        pos.select_list_item("Var_Item_Amt")
        pos.click('enter')

        if not pos.read_status_line() == "":
            pos.enter_keypad("1", after="enter")
        else:
            self.log.warning("Failed to add Var_Item_Amt discount!")
            return False

        self._on_transaction_screen()

        if not self._journal_updated(original_number=2):
            self.log.warning("Var_Item_Amt discount not displayed in transaction journal!")
            return False

        journal = pos.read_transaction_journal()

        try:
            discount_name = journal[2][0]
            discount = journal[2][1]
        except IndexError:
            self.log.warning("Var_Item_Amt did not show up correctly in the transaction journal!")
            return False

        if pos.read_transaction_journal(only_selected=True) == None:
            self.log.warning("No item selected after adding Var_Item_Amt discount!")
            return False
        elif not discount_name == "Var_Item_Amt":
            self.log.warning("Discount should say Var_Item_Amt.  Instead it says " + discount_name)
            return False
        elif not discount == "-$0.01":
            self.log.warning("Var_Item_Amt discount should be -$0.01.  Instead it was " + discount)
            return False

        if not pos.read_balance()["Total"] == "$" + format(round(total_price - 0.01, 2), '.2f'):
            self.log.warning("Total should be $" + format(round(total_price - 0.01, 2), '.2f') + " after Var_Item_Amt discount.  Instead, it was " + pos.read_balance()["Total"] + "!")
            return False
        else:
            discount_total += 0.01
            total_price -= 0.01

        self.log.info("Var_Item_Amt discount added...")

        # Std_Item_Price
        pos.click("discount")
        if not self._list_loaded("Std_Item_Price"):
            self._return_to_main_screen()
            tc_fail("'Std_Item_Price' was not in the selection list.")
        pos.select_list_item("Std_Item_Price")
        pos.click('enter')

        self._on_transaction_screen()

        if not self._journal_updated(original_number=3):
            self.log.warning("Std_Item_Price discount not displayed in transaction journal!")
            return False

        journal = pos.read_transaction_journal()

        try:
            discount_name = journal[3][0]
            discount = journal[3][1]
        except IndexError:
            self.log.warning("Std_Item_Price did not show up correctly in the transaction journal!")
            return False

        if pos.read_transaction_journal(only_selected=True) == None:
            self.log.warning("No item selected after adding Std_Item_Price discount!")
            return False
        elif not discount_name == "Std_Item_Price":
            self.log.warning("Discount should say Std_Item_Price.  Instead it says " + discount_name)
            return False
        elif not discount == "-$1.00":
            self.log.warning("Std_Item_Price discount should be -$1.00.  Instead it was " + discount)
            return False

        if not pos.read_balance()["Total"] == "$" + format(round(total_price - 1.00, 2), '.2f'):
            self.log.warning("Total should be $" + format(round(total_price - 1.00, 2), '.2f') + " after Std_Item_Price discount.  Instead, it was " + pos.read_balance()["Total"] + "!")
            return False
        else:
            discount_total += 1.00
            total_price -= 1.00

        self.log.info("Std_Item_Price discount added...")

        # Std_Item_Pct
        pos.click("discount")
        if not self._list_loaded("Std_Item_Pct"):
            self._return_to_main_screen()
            tc_fail("'Std_Item_Pct' was not in the selection list.")
        pos.select_list_item("Std_Item_Pct")
        pos.click('enter')

        self._on_transaction_screen()

        if not self._journal_updated(original_number=4):
            self.log.warning("Std_Item_Pct discount not displayed in transaction journal!")
            return False

        journal = pos.read_transaction_journal()

        try:
            discount_name = journal[4][0]
            discount = journal[4][1]
        except IndexError:
            self.log.warning("Std_Item_Pct did not show up correctly in the transaction journal!")
            return False

        if pos.read_transaction_journal(only_selected=True) == None:
            self.log.warning("No item selected after adding Std_Item_Pct discount!")
            return False
        elif not discount_name == "Std_Item_Pct":
            self.log.warning("Discount should say Std_Item_Pct.  Instead it says " + discount_name)
            return False
        elif not discount == "-$" + format(round(price * 0.10, 2), '.2f'):
            self.log.warning("Std_Item_Pct discount should be -$" + format(round(price * 0.10, 2), '.2f') + ".  Instead it was " + discount)
            return False

        if not pos.read_balance()["Total"] == "$" + format(round(total_price - (price * 0.10), 2), '.2f'):
            self.log.warning("Total should be $" + format(round(total_price - (price * 0.10), 2), '.2f') + " after Std_Item_Pct discount.  Instead, it was " + pos.read_balance()["Total"] + "!")
            return False
        else:
            discount_total += (price * 0.10)
            total_price -= (price * 0.10)

        self.log.info("Std_Item_Pct discount added...")

        # Std_Item_Amt
        pos.click("discount")
        if not self._list_loaded("Std_Item_Amt"):
            self._return_to_main_screen()
            tc_fail("'Std_Item_Amt' was not in the selection list.")
        pos.select_list_item("Std_Item_Amt")
        pos.click('enter')

        self._on_transaction_screen()

        if not self._journal_updated(original_number=5):
            self.log.warning("Std_Item_Amt discount not displayed in transaction journal!")
            return False

        journal = pos.read_transaction_journal()

        try:
            discount_name = journal[5][0]
            discount = journal[5][1]
        except IndexError:
            self.log.warning("Std_Item_Amt did not show up correctly in the transaction journal!")
            return False

        if pos.read_transaction_journal(only_selected=True) == None:
            self.log.warning("No item selected after adding Std_Item_Amt discount!")
            return False
        elif not discount_name == "Std_Item_Amt":
            self.log.warning("Discount should say Std_Item_Amt.  Instead it says " + discount_name)
            return False
        elif not discount == "-$1.00":
            self.log.warning("Std_Item_Amt discount should be -$1.00.  Instead it was " + discount)
            return False

        if not pos.read_balance()["Total"] == "$" + format(round(total_price - 1.00, 2), '.2f'):
            self.log.warning("Total should be $" + format(round(total_price - 1.00, 2), '.2f') + " after Std_Item_Amt discount.  Instead, it was " + pos.read_balance()["Total"] + "!")
            return False
        else:
            discount_total += 1.00
            total_price -= 1.00

        self.log.info("Std_Item_Amt discount added...")
        
        # Std_Item_Free
        pos.click("discount")
        if not self._list_loaded("Std_Item_Free"):
            self._return_to_main_screen()
            tc_fail("'Std_Item_Free' was not in the selection list.")
        pos.select_list_item("Std_Item_Free")
        pos.click('enter')

        self._on_transaction_screen()

        if not self._journal_updated(original_number=6):
            self.log.warning("Std_Item_Free discount not displayed in transaction journal!")
            return False

        journal = pos.read_transaction_journal()

        try:
            discount_name = journal[6][0]
            discount = journal[6][1]
        except IndexError:
            self.log.warning("Std_Item_Free did not show up correctly in the transaction journal!")
            return False

        if pos.read_transaction_journal(only_selected=True) == None:
            self.log.warning("No item selected after adding Std_Item_Free discount!")
            return False
        elif not discount_name == "Std_Item_Free":
            self.log.warning("Discount should say Std_Item_Free.  Instead it says " + discount_name)
            return False
        elif not discount == "-$" + format(round(price - discount_total, 2), '.2f'):
            self.log.warning("Std_Item_Free discount should be -$" + format(round(price - discount_total, 2), '.2f') + ".  Instead it was " + discount)
            return False

        if not pos.read_balance()["Total"] == "$" + format(round(total_price - (price - discount_total), 2), '.2f'):
            self.log.warning("Total should be $" + format(round(total_price - (price - discount_total), 2), '.2f') + " after Std_Item_Free discount.  Instead, it was " + pos.read_balance()["Total"] + "!")
            return False

        self.log.info("Std_Item_Free discount added...")
        self.log.info("All item discounts successfully added...")

        return True



    def _on_main_screen(self, timeout=default_timeout):
        """
        Helper function to determine if HTML POS is on the main screen
        """
        return pos.is_element_present(pos.controls['function keys']['paid in'], timeout=timeout)


    def _on_transaction_screen(self, timeout=default_timeout):
        """
        Helper function to determine if HTML POS is in a transaction
        on the main transaction screen (i.e. the one with all the function keys)
        """
        return pos.is_element_present(pos.controls['function keys']['void transaction'], timeout=timeout)

    
    def _return_to_main_screen(self):
        """
        Helper function for getting back to the main screen
        of HTML POS, especially in cases of failure
        """
        self.log.info("Attempting to return to main screen...")
        if self._on_main_screen():
            self.log.info("On main screen...")
            return True
        elif pos.is_element_present(pos.controls['function keys']['void transaction'], self.short_wait_time):
            pos.void_transaction()
            if self._on_main_screen(timeout=self.long_wait_time):
                self.log.info("Returned to main screen...")
                return True
            else:
                self.log.info("Failed to return to main screen...")
                return False
        elif pos.read_status_line(self.short_wait_time):
            pos.click('cancel')
            pos.void_transaction()
            if self._on_main_screen(timeout=self.long_wait_time):
                self.log.info("Returned to main screen...")
                return True
            else:
                self.log.info("Failed to return to main screen...")
                return False
        else:
            self.log.info("Unknown screen state.  Failed to return to main screen...")
            return False
        

    def _status_line_blank(self, timeout=default_timeout):
        """
        Helper function for detecting whether the status line
        is blank faster
        """
        start_time = time.time()
        while time.time() - start_time <= timeout:
            if pos.read_status_line(timeout/20.0) == '':
                return True
        else:
            return False


    def _is_discountable_item(self, timeout=default_timeout):
        """
        Helper function for determining if an item is discountable
        for the purpose of the visibility of the item/finalize buttons
        on the keypad
        """
        # Make sure keypad is loaded
        pos.is_element_present(pos.controls['keypad']['cancel'], timeout=timeout)

        # Check whether transaction button is there
        return pos.is_element_present(pos.controls['keypad']['transaction'], timeout=0.25)


    def _number_of_journal_items(self, number=0, timeout=default_timeout):
        """
        Helper function to give the transaction journal time to update
        and check the number of items in it
        """
        start_time = time.time()
        while time.time() - start_time <= timeout:
            if len(pos.read_transaction_journal(timeout=timeout/20.0)) == number:
                return True
            time.sleep(timeout/20.0)
        else:
            return False


    def _journal_updated(self, original_number, timeout=default_timeout):
        """
        Helper function for checking whether the transaction journal has updated
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if len(pos.read_transaction_journal(timeout=timeout/20.0)) > original_number:
                return True
        else:
            return False

    
    def _all_prices_present(self, timeout=default_timeout):
        """
        Helper function to deter index errors from occuring on account
        of issues reading the transaction journal too early without a price
        for something being present
        """
        journal = pos.read_transaction_journal()
        important_index = 0
        start_time = time.time()
        while time.time() - start_time <= timeout:
            for i in range(important_index, len(journal)):
                if not len(journal[i]) == 2:
                    important_index = i
                    time.sleep(timeout/20.0)
                    break
                elif i == len(journal) - 1:
                    return True
        else:
            self.log.warning("The following item: " + str(journal[important_index]) + " at index " + str(important_index) + " did not contain both the item name and price.")
            return False


    def _list_loaded(self, text, timeout=default_timeout):
        """
        Helper function to make sure that the selection list has changed/
        loaded so there won't be the ocassional incorrect failure of select_list_item
        """
        start_time = time.time()
        while time.time() - start_time <= timeout:
            try:
                items = pos._find_elements(pos.controls['selection list']['options'], timeout=timeout/20.0, visible_only=False)
                for item in items:
                    if text in item.text:
                        return True
            except:
                continue
            time.sleep(timeout/20.0)
        else:
            return False

        
