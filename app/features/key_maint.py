from app.framework import mws, Navi
import logging, pywinauto
from app.framework import OCR

log = logging.getLogger()

LAST_PAGE = -1
DELETE = "delete"

class KeyMaintenance:
    """
    Base class that is inherited by Speed/Department/Coupon Key Maintenance. Don't instantiate this class directly.
    """

    def __init__(self, key_type):
        """
        Args:
            key_type: (str) The type of keys for the menu - Speed, Department, or Coupon.
        """
        if key_type == "Speed":
            KeyMaintenance.navigate_to(f"{key_type}key Maintenance")
        else:
            KeyMaintenance.navigate_to(f"{key_type} Key Maintenance")
        self.key_type = key_type
        self.keys = mws.get_control("Keys").children()
        self.valid_key_args = ["Code", "Caption", "Icon"]

    @staticmethod
    def navigate_to(menu):
        Navi.navigate_to(menu)

    def configure(self, config):
        """
        Configure multiple keys at once.
        Args:
            config: (dict) Describes the configuration of pages and keys to apply. See below example for format.
        Returns: (bool) Success/failure
        Example:
            >>> cfg = { 
                        1: {
                            1: {    
                                "Code": "123",
				                "Caption": "Thingy"
                               },
		                    5: {  	
                                "Code: "555",
				                "Caption": "Mabob" 
                               }
                           },
                        3: {
                            12: { 	
                                "Code": "1"
                                },
		                    3:  "delete" 
                           },
                        2: "delete"
                      }
            >>> configure(cfg) # Configures positions 1 and 5 on page 1, positions 12 and 3 on page 3, then deletes page 2
            True
        """
        for key, value in config.items():
            if value == DELETE:
                self.delete_page(key)
                continue

            # Navigate to the correct page, creating page(s) if needed
            while not self.goto_page(key): 
                self.goto_page(LAST_PAGE)
                self.add_page()

            # Configure keys on the page
            for key2, value2, in value.items():
                position = int(key2)
                if value2 == DELETE:
                    self.delete(position)
                    continue

                # Build args to pass to change/add
                key_args = {}
                for key3, value3 in value2.items():
                    if key3 not in self.valid_key_args:
                        log.warning(f"{key3} is not a valid field.")
                        return False
                    key_args.update({key3.lower().replace(' ', '_'): value3})
                
                if self.keys[position].is_visible():
                    self.change(position, **key_args)
                else:
                    self.add(position, **key_args)

        return True # Code to save the configuration should be implemented in subclasses.


    def add(self, position, code, caption=None, icon=None):
        """
        Add a new key on the current page.
        Args:
            position: (int) Which spot to place the key in (1-16).
            code: (str) The code of the department          
            caption: (str) Caption text for the key
            icon: (str) The name of the icon for the key
        Returns:
            bool: Success/failure
        """      
        position -= 1 # Change to zero-index
        if self.keys[position].is_visible():
            log.warn(f"There is already a {self.key_type} key in position {position+1}.")
            return False
        self.keys[position].click_input()
        if not mws.search_click_ocr("Add Key"):
            return False
        if not mws.set_value("Code", code):
            return False
        mws.get_control("Code").type_keys("{ENTER}") # We have to do this to confirm the code and populate Caption field
        if caption is not None and not mws.set_value("Caption", caption):
            return False
        if icon is not None and not mws.set_value("Icon", icon):
            return False
        return True

    def delete(self, position, code=None, caption=None, icon=None):
        """
        Delete a key on the current page.
        Args:
            position: (int) The position of the key in the grid (1-16)
            code: (str) The code of the key
            caption: (str) Caption text for the key
            icon: (str) The name of the icon for the key
        Returns:
            bool: Success/failure
        """
        position -= 1 # Change to zero-index
        self.keys[position].click_input()
        if code is not None and mws.get_value("Code") != code:
            log.warn(f"{self.key_type} key in position {position+1} does not have code {code}. Aborting deletion.")
            return False
        if caption is not None and mws.get_value("Caption") != caption:
            log.warn(f"{self.key_type} key in position {position+1} does not have caption {caption}. Aborting deletion.")
            return False
        if icon is not None and mws.get_value("Icon") != icon:
            log.warn(f"{self.key_type} key in position {position+1} does not have icon {icon}. Aborting deletion.")
            return False
        mws.search_click_ocr("Delete Key") # mws.click won't work here because button IDs change based on how many speed keys are configured
        if mws.get_value("Code") != '':
            log.warn(f"The key in position {position+1} didn't delete properly.")
            return False
        return True

    def change(self, position, code=None, caption=None, icon=None):
        """
        Change an existing key on the current page.
        Args:
            position: (int) The position of the key in the grid (1-16)
            code: (str) The new code of the key
            caption: (str) The new caption text for the key
            icon: (str) The name of the new icon for the key
        Returns:
            bool: Success/failure
        """
        position -= 1 # Change to zero-index
        if not self.keys[position].is_visible():
            log.warn(f"There is no {self.key_type} key to change in position {position+1}.")
            return False
        elif code is None and caption is None and icon is None:
            log.warn(f"Please specify one or more fields of the {self.key_type} key to change.")
            return False
        self.keys[position].click_input()
        if code is not None and not mws.set_value("Code", code):
            return False
        if caption is not None and not mws.set_value("Caption", caption):
            return False
        if icon is not None and not mws.set_value("Icon", icon):
            return False
        return True

    def move(self, position, new_position):
        """
        Move an existing key to a new position.
        If there is already a key in the new position, the two will be swapped.
        Args:
            position: (int) The position of the key in the grid (1-16)
            new_position: (int) The position to move the key to (1-16)
        Returns:
            bool: Success/failure
        """
        position -= 1 # Change to zero-index
        new_position -= 1
        if not self.keys[position].is_visible():
            log.warn(f"There is no {self.key_type} key to move in position {position+1}.")
            return False

        # Check the keys in the start and end positions
        self.keys[position].click_input()
        code = mws.get_text("Code")
        code2 = None
        if self.keys[new_position].is_visible():
            self.keys[new_position].click_input()
            code2 = mws.get_text("Code")

        # Move the key via click+drag
        mws.click_toolbar("Move")
        self.keys[position].click_input(button_up=False)
        self.keys[new_position].click_input(button_down=False)
        mws.click_toolbar("Move")

        # Check that key(s) moved successfully
        self.keys[new_position].click_input()
        if mws.get_text("Code") != code:
            log.warn(f"{self.key_type} key did not move successfully from position {position+1} to {new_position+1}.")
            return False
        self.keys[position].click_input()
        if mws.get_text("Code") != code2:
            log.warn(f"{self.key_type} key in position {new_position+1} did not switch places with key in position {position+1}.")
            return False
        return True

    def add_page(self):
        """
        Add a new page of keys after the current page. Will re-add the key that is deleted
        to make way for the Next key, if needed.
        Args:
            None
        Returns:
            bool: Success/failure
        """
        self.keys[15].click_input()
        if not mws.search_click_ocr("Add Menu Page"):
            log.warn("Failed to click Add Menu Page.")
            return False
        if "This action will replace your" in mws.get_top_bar_text():
            key_to_readd = { "position": 16,
                             "code": mws.get_value("Code"),
                             "caption": mws.get_value("Caption"),
                             "icon": mws.get_value("Icon") }
            if not mws.click_toolbar("Yes"):
                log.warn("Failed to click Yes when confirming new page prompt.")
                return False
            return self.add(**key_to_readd)
        return True

    def goto_page(self, page_num):
        """
        Switch to another page of keys.
        Args:
            page_num: (int) The page number to go to. Use KeyMaintenance.LAST_PAGE to go to the last page.
        Returns:
            bool: Success/failure
        """
        current_page, total_pages = self._check_page()
        if page_num == LAST_PAGE:
            page_num = total_pages
        if page_num > total_pages:
            log.warn(f"Invalid page number {page_num}. There are only {total_pages} pages.")
            return False
        if current_page < page_num:
            # Go forward
            for _ in range(page_num-current_page):
                self.keys[15].click_input()
        elif current_page > page_num:
            # Go backward
            for _ in range(current_page-page_num):
                self.keys[14].click_input()
        return True # No need to do anything if page_num == current_page

    def delete_page(self, page_num):
        """
        Delete a page of keys.
        Args:
            page_num: (int) The page number to delete.
        Returns:
            bool: Success/failure
        """
        self.goto_page(page_num)
        if not mws.search_click_ocr("Delete Menu"):
            log.warn("Failed to click Delete Menu Page.")
            return False
        mws.click_toolbar("Yes")

    def _check_page(self):
        """
        Check what page of keys we are currently on and how many there are in total.
        Args: None
        Returns: (int tuple) The currently active page and the total number of pages.
        Example
            >>> _check_page()
            (1, 3)
        """
        # MWS text doesn't seem to be accessible via pywinauto. Use OCR to see where we are.
        page_bbox = (210, 190, 320, 220) if mws.is_high_resolution() else (210, 150, 320, 180)
        #TODO: Should this use a system function?
        page_text = OCR.OCRRead(bbox=page_bbox, psm=6)
        if page_text[1].isdigit():
            current_page = int(page_text[:2])
        else:
            current_page = int(page_text[0])
        if page_text[-2].isdigit():
            total_pages = int(page_text[-2:])
        else:
            total_pages = int(page_text[-1])
        return (current_page, total_pages)

class SpeedKeyMaintenance(KeyMaintenance):
    def __init__(self):
        super().__init__("Speed")
        self.valid_key_args += ["Menu ID"]

    @staticmethod
    def navigate_to():
        return Navi.navigate_to("Speedkey Maintenance")

    def configure(self, menu, config, rename=None, level=None):
        """
        Configure a speed key menu.
        Args:
            menu: (int) The name of the menu to configure. Will be created if it doesn't already exist.
            config: (dict) Describes the configuration of pages and keys to apply. See below example for format.
            rename: (str) The new description to set for the speedkey menu, if desired.
            level: (str) The level radio button to select, if any.
        Returns: (bool) Success/failuremws.set
        Example:
            >>> cfg = { 
                        1: {
                            1: {    
                                "Code": "123",
				                "Caption": "Thingy"
                               },
		                    5: {  	
                                "Code: "555",
				                "Caption": "Mabob" 
                               }
                           },
                        3: {
                            12: { 	
                                "Menu ID": "SubSpeedKeys"
                                },
		                    3:  "delete" 
                           },
                        2: "delete"
                      }
            >>> configure("Default", cfg) # Configures positions 1 and 5 on page 1, positions 12 and 3 on page 3, then deletes page 2
            True
            >>> configure("NotDefault", cfg, level="Secondary")
            True
        """
        if mws.set_value("Speedkeys", menu): # Change existing menu
            mws.click_toolbar("Change", submenu=True)
            if level:
                logger.warning("Can't set menu level for an already existing speedkey menu.")
                return False
        else: # Add new menu
            mws.click_toolbar("Add", submenu=True)
            mws.set_value("Key Menu Description", menu)
            if level:
                mws.set_value(level, True)

        if rename:
            mws.set_value("Key Menu Description", rename)       

        self.keys = mws.get_control("Keys").children()
        if not super().configure(config):       
            log.warning("Configuration unsuccessful. Exiting without saving.")
            mws.click_toolbar("Cancel")
            mws.click_toolbar("No", submenu=True)
            return False

        return mws.click_toolbar("Save", submenu=True)

    def add(self, *args, menu_id=None, **kwargs):
        """
        Add a new key on the current page.
        Args:
            position: (int) Which spot to place the key in (1-16).
            code: (str) The code of the department          
            caption: (str) Caption text for the key
            icon: (str) The name of the icon for the key
            menu_id: (str) The menu ID for the key
        Returns:
            bool: Success/failure
        """
        if len(args) < 2 and "code" not in kwargs.keys():
            if not menu_id:
                logger.warning("Either code or menu_id must be specified.")
                return False
            kwargs.update({"code": ""}) # Superclass method requires code arg, use empty string if not specified

        self.keys = mws.get_control("Keys").children() # Re-grab this at runtime since SKM has submenus and the reference may no longer be valid
        if not super().add(*args, **kwargs):
            return False
        if menu_id is not None and not mws.set_value("Menu ID", menu_id):
            return False
        return True

    def change(self, *args, menu_id=None, **kwargs):
        """
        Change an existing key on the current page.
        Args:
            position: (int) The position of the key in the grid (1-16)
            code: (str) The new code of the key
            caption: (str) The new caption text for the key
            icon: (str) The name of the new icon for the key
            menu_id: (str) The new menu ID for the key
        Returns:
            bool: Success/failure
        """
        self.keys = mws.get_control("Keys").children()
        if not super().change(*args, **kwargs):
            return False
        if menu_id is not None and not mws.set_value("Menu ID", menu_id):
            return False
        return True

    def add_menu(self, description):
        """
        Add a new speed key menu.
        Args:
            description: (str) The description for the menu.
        Returns:
            bool: Success/failure
        """
        self.keys = mws.get_control("Keys").children()
        mws.click_toolbar("Add")
        if not mws.set_value("Key Menu Description", description):
            return False
        return mws.click_toolbar("Save")

    def change_menu(self, description):
        """
        Navigate into a speed key menu to edit it.
        Args:
            description: (str) The name of the menu to select.
        Returns:
            bool: Success/failure
        """
        self.keys = mws.get_control("Keys").children()
        if not mws.set_value("Speedkeys", description):
            return False
        return mws.click_toolbar("Change")

    def delete_menu(self, description):
        """
        Delete a speed key menu.
        Args:
            description: (str) The name of the menu to delete.
        Returns:
            bool: Success/failure
        """
        self.keys = mws.get_control("Keys").children()
        if not mws.set_value("Speedkeys", description):
            log.warning(f"{description} menu doesn't exist. Can't delete it.")
            return False
        mws.click_toolbar("Delete")
        if "Deleting a speed key menu could have the effect" not in mws.get_top_bar_text():
            log.warning(f"Didn't get confirmation prompt for deleting {description} menu.")
            return False
        mws.click_toolbar("Yes")
        if description in mws.get_value("Speedkeys"):
            log.warning(f"{description} menu wasn't deleted properly.")
            return False
        return True

class DepartmentKeyMaintenance(KeyMaintenance):
    def __init__(self):
        super().__init__("Department")

    @staticmethod
    def navigate_to():
        return Navi.navigate_to("Department Key Maintenance")

    def configure(self, config):
        """
        Configure a department key menu.
        Args:
            config: (dict) Describes the configuration of pages and keys to apply. See below example for format.
        Returns: (bool) Success/failure
        Example:
            >>> cfg = { 
                        1: {
                            1: {    
                                "Code": "1",
				                "Caption": "Dept 1"
                               },
		                    5: {  	
                                "Code: "5",
				                "Caption": "Beer" 
                               }
                           },
                        3: {
                            12: { 	
                                "Code": "4"
                                },
		                    3:  "delete" 
                           },
                        2: "delete"
                      }
            >>> configure(cfg) # Configures positions 1 and 5 on page 1, positions 12 and 3 on page 3, then deletes page 2
            True
        """
        if not super().configure(config):       
            log.warning("Configuration unsuccessful. Exiting without saving.")
            mws.click_toolbar("Cancel")
            mws.click_toolbar("No", main=True)
            return False

        return mws.click_toolbar("Save", main=True)

class CouponKeyMaintenance(KeyMaintenance):
    def __init__(self):
        super().__init__("Coupon")

    @staticmethod
    def navigate_to():
        return Navi.navigate_to("Coupon Key Maintenance")

    def configure(self, config):
        """
        Configure a coupon key menu.
        Args:
            config: (dict) Describes the configuration of pages and keys to apply. See below example for format.
        Returns: (bool) Success/failure
        Example:
            >>> cfg = { 
                        1: {
                            1: {    
                                "Code": "1",
				                "Caption": "10% Off"
                                },
		                    5: {  	
                                "Code: "62",
				                "Caption": "Beer Sale" 
                                }
                            },
                        3: {
                            12: { 	
                                "Code": "4"
                                },
		                    3:  "delete" 
                            },
                        2: "delete"
                        }
            >>> configure(cfg) # Configures positions 1 and 5 on page 1, positions 12 and 3 on page 3, then deletes page 2
            True
        """
        if not super().configure(config):       
            log.warning("Configuration unsuccessful. Exiting without saving.")
            mws.click_toolbar("Cancel")
            mws.click_toolbar("No", main=True)
            return False

        return mws.click_toolbar("Save", main=True)
