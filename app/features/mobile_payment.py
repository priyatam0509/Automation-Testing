from app import mws
from app import Navi, system
import logging, time

log = logging.getLogger()


class MobilePaymentConfiguration:

    def __init__(self):
        MobilePaymentConfiguration.navigate_to()

    @staticmethod
    def navigate_to():
        """
        Navigates to the Mobile Payment Configuration feature module.
        Args: None
        Returns: Returns the result of execution of Navi.navigate_to()
        """
        
        return Navi.navigate_to("Mobile Payment Configuration")   

    def configure(self, config, default_discount = None, QR_list = None, EMVCo_QR = False):
        """
        Description: Configures the fields, Local discounts and QR codes in the Mobile Payment Configuration menu.
        Args:
            config:(dictionary) A dictionary of controls specifying what to set each field in the General tab and local fuel discount. 
            default_discount(str): name of defeault discount
            QR_list:(list) A list of strings specifying what QR code prefixes to add to the list.
            EMVCo_QR: (str/bool) Whether or not to allow EMVCo QR Codes. Can be True/False or "Yes"/"No"


        Returns:
            bool: Success/Failure
        Example: 
           mpc_info = {
            "General": {
                "Page 1": {
                    "Provider Name": "Connexus",
				    "Enabled": "Yes",
				    "Merchant ID": "0146-2380",
				    "Site ID": "01462380",
				    "Host Address": "10.5.48.6",
				    "Port Number": "9052",
				    "Settlement Software Version": "1",
				    "Settlement Passcode": "Passcode",
				    "Settlement Employee": "Employee",
				    "Schema Version": "2.0"
                },
                "Page 2": {
                    "Use TLS": "Yes",
                    "OCSP Mode": "Strict",
                    "TLS Certificate Name": "TLSCertificateName"
                }
		    },
		    "Local Fuel Discounts": {
			    "Mobile Local Discount Code": "Provider Automated",
			    "Mobile Local Discount Description": "test Automated",
			    "Fuel Discount Group": "Discount 1"
		    }
	    }
        mpc = mobile_payment.MobilePaymentConfiguration()
        mpc.configure(mpc_info, ["prefix1","prefix2"], EMVCo_QR = True)
        
        """
        mws.click_toolbar("add")
        if mws.verify_top_bar_text("Cannot add any more Mobile Providers. Maximum number of Mobile Providers configured", timeout=30):
            log.warning(f"5 Providers Configured")
            mws.click_toolbar("Ok")
            return False

        mws.set_value("Mobile Provider Name", config["Mobile Provider Name"])
        mws.click_toolbar("Save")
        if mws.verify_top_bar_text("Cannot add another mobile provider with the same name.", timeout=30):
            log.warning(f"A provider with the name {config['Mobile Provider Name']} already exists.")
            mws.click_toolbar("Ok")
            return False

        log.info("Waiting for page load before moving forward")

        if not mws.verify_top_bar_text("The Mobile provider name", timeout=300):
                
            log.error("Mobile payment screen was not load in 5 minutes")
            return False
            
        mws.select_tab("General")
        mws.select_tab("Page 1")
        # Force "Mobile Provider Name" control first
        if "Provider Name" in config["General"]["Page 1"]:
            mws.set_value("Provider Name", config["General"]["Page 1"]["Provider Name"])
        # Check if Provider is Disabled
        if config["General"]["Page 1"]["Enabled"] == "No":
            log.debug(f"Provider disabled")
        else:
            #fill page 1
            for key, value in config["General"]["Page 1"].items():
                if key == "Provider Name":
                    continue
                elif not mws.set_value(key, value):
                    log.error(f"Failed setting '{key}' to '{value}' on General tab.")
                    return False            
            #fill page 2
            mws.select_tab("Page 2") 
            for key, value in config["General"]["Page 2"].items():
                if not mws.set_value(key, value):
                    log.error(f"Failed setting '{key}' to '{value}' on General tab.")
                    return False
        mws.select_tab("Conexxus QR Code Prefixes")
        if QR_list != None: # makes QR list optional
            log.debug("Configuring QR codes...")
            # Add QR code prefixes
            for code in QR_list:
                if not mws.set_value("QR Code List", code):
                    log.debug(f"Adding '{code}'...")
                    mws.click_toolbar("Add")
                    if not mws.set_value("Conexxus QR Code Prefixes", code, "Conexxus QR Code Prefixes"):
                        log.error(f"Failed adding '{code}' to QR code list.")
                        return False
                else:
                    log.warning(f"'{code}' already exists in list. Skipping...")
        
        mws.select_tab("EMVCo QR Codes")
        # Convert EMVCo from bool to string if necessary
        if type(EMVCo_QR) is bool:
            EMVCo_QR = "Yes" if EMVCo_QR else "No"
        elif EMVCo_QR != "Yes" and EMVCo_QR != "No":
            log.error(f"Input: '{EMVCo_QR}' not recognized for EMVCo_QR variable.")
            return False
        if not mws.set_value("Allow EMVCo QR Codes", EMVCo_QR):
            log.error("Failed setting EMVCo combobox.")
            return False    
        mws.select_tab("Default Local Fuel Discount")
        # Set default discount
        if default_discount != None:
            if not mws.set_value("Default Fuel Discount Group", default_discount, "Default Local Fuel Discount"):
                log.error(f"Could not find {default_discount} in list of discounts.")
                return False
        mws.select_tab("Local Fuel Discounts")
        # Iterate over each local discount and check existence

        if "Local Fuel Discounts" in config:
            localdiscount = config["Local Fuel Discounts"]
        
            mws.click_toolbar("Add")
            for key, value in config["Local Fuel Discounts"].items():
            # Begin setting values
                if not mws.set_value(key, value):
                    log.error(f"Failed setting '{key}' to '{value}' while configuring '{localdiscount}'.")
                    return False     
                else:
                    log.debug(f"'{localdiscount}' already exists in list. Editing...")

        mws.click_toolbar("Save")

        # Check for errors
        errorcode = mws.get_top_bar_text()
        if errorcode:
            if "conflict in qr code prefix" in errorcode.lower() or "cannot be blank" in errorcode.lower() or "correct invalid QR code" in errorcode.lower():
                log.error(errorcode)
                mws.click_toolbar("Cancel")
                mws.click_toolbar("No")
                log.error("Some part of your configuration was incorrect.")
                return False
        
        return True
    
    def check_values(self, config):
        """
            Description: Verify default values hydrates on the Mobile Payment Configuration menu when a new provider is added.
            Args:
                config:(str) A dictionary of controls specifying what to get each field in Page 1 on General Tab.
                Returns:
                bool: Success/Failure
            Example: 
                mpc_info = {
                    "Mobile Provider Name":'SpeedPass+',
                    "General": {
                        "Page 1": {
                            "Provider Name": "SpeedPass+",
                            "Site ID": "EXXONMOBIL_GVR_US",
				            "Host Address": "204.194.139.242",
				            "Port Number": "9060",
				            "Schema Version": "2.0",
                            "Enabled": "No"
                        }
                    }
	            }
                mpc = mobile_payment.MobilePaymentConfiguration()
                mpc.check_values(mpc_info)
                True
        """
        mws.click_toolbar("add")
        name = mws.get_value("Mobile Provider Name")
        if not (name == config["Mobile Provider Name"]):
            log.error(f"the provider name has different'{name}'.")
            return False
        mws.click_toolbar("Save")
        mws.select_tab("Page 1") #Go to tab
        for key, intended_value in config["General"]["Page 1"].items():
            current_value = mws.get_value(key)
            if type(current_value) != list:
                current_value = [current_value] #force to list so next line works correctly                    
                # Combo box controls return a list of possible values with the
                # currently selected option as the first index
            if current_value[0] != intended_value:
                log.error(f" this'{key}' is diferent than default configuration provider")
                return False
        mws.click_toolbar("Save")

        return True

    def change_provider(self, config, name, default_discount = None,QR_list = None, EMVCo_QR = False):
        """
        Description: Changes the fields and QR codes in the Mobile Payment Configuration menu.
        Args:
            config:(str) A dictionary of controls specifying what to set each field in the General tab and local fuel discount.
            name:(str) Name of a provider who MWS used to search a provider created before 
            default_discount(str): name of defeault discount
            QR_list:(list) A list of strings specifying what QR code prefixes to add to the list.
            EMVCo_QR: (str/bool) Whether or not to allow EMVCo QR Codes. Can be True/False or "Yes"/"No"
        Returns:
            bool: Success/Failure
        Example: 
             mpc_info= {
                "General": {
                    "Page 1": {
                        "Provider Name": "Paypal",
                        "Enabled": "Yes",
                        "Merchant ID": "0146-2380",
				        "Site ID": "01462380",
				        "Host Address": "10.28.120.62",
				        "Port Number": "9052",
				        "Settlement Software Version": "1",
				        "Settlement Passcode": "Passcode",
				        "Settlement Employee": "Employee",
				        "Schema Version": "2.0"
                    },
                    "Page 2": {
                        "Use TLS": "Yes",
                        "OCSP Mode": "Strict",
                        "TLS Certificate Name": "TLSCertificateName"
                    }
		        }
	        }
            mpc = mobile_payment.MobilePaymentConfiguration()
            mpc.change_provider(mpc_info,name,default_discount ["prefix1","prefix2"], EMVCo_QR = True)
            True
        """
        if not mws.set_value("Mobile Providers", name):
            log.warning(f"Couldn't select provider {name}.")
            return False
        mws.click_toolbar("change")

        if not mws.verify_top_bar_text("The Mobile provider name", timeout=300):
                
            log.error("Mobile payment screen was not load in 5 minutes")
            return False

        mws.select_tab("General")
        mws.select_tab("Page 1")
        # Force "Mobile Provider Name" control first
        if "Provider Name" in config["General"]["Page 1"]:
            mws.set_value("Provider Name", config["General"]["Page 1"]["Provider Name"])
        # Check if Provider is Disabled
        if config["General"]["Page 1"]["Enabled"] == "No":
            mws.set_value("Enabled", config["General"]["Page 1"]["Enabled"])
            log.debug(f"Provider disabled")
        else:
            #fill page 1
            for key, value in config["General"]["Page 1"].items():
                if key == "Provider Name":
                    continue
                elif not mws.set_value(key, value):
                    log.error(f"Failed setting '{key}' to '{value}' on General tab.")
                    return False            
            #fill page 2
            mws.select_tab("Page 2") 
            for key, value in config["General"]["Page 2"].items():
                if not mws.set_value(key, value):
                    log.error(f"Failed setting '{key}' to '{value}' on General tab.")
                    return False
        mws.select_tab("Conexxus QR Code Prefixes")
        if QR_list != None: # makes QR list optional
            log.debug("Configuring QR codes...")
            # Add QR code prefixes
            for code in QR_list:
                if not mws.set_value("QR Code List", code):
                    log.debug(f"Adding '{code}'...")
                    mws.click_toolbar("Add")
                    if not mws.set_value("Conexxus QR Code Prefixes", code, "Conexxus QR Code Prefixes"):
                        log.error(f"Failed adding '{code}' to QR code list.")
                        return False
                else:
                    log.warning(f"'{code}' already exists in list. Skipping...")
        
        mws.select_tab("EMVCo QR Codes")
        # Convert EMVCo from bool to string if necessary
        if type(EMVCo_QR) is bool:
            EMVCo_QR = "Yes" if EMVCo_QR else "No"
        elif EMVCo_QR != "Yes" and EMVCo_QR != "No":
            log.error(f"Input: '{EMVCo_QR}' not recognized for EMVCo_QR variable.")
            return False
        if not mws.set_value("Allow EMVCo QR Codes", EMVCo_QR):
            log.error("Failed setting EMVCo combobox.")
            return False    
        mws.select_tab("Default Local Fuel Discount")
        # Set default discount
        if default_discount != None:
            if not mws.set_value("Default Fuel Discount Group", default_discount, "Default Local Fuel Discount"):
                log.error(f"Could not find {default_discount} in list of discounts.")
                return False
        mws.select_tab("Local Fuel Discounts")
        # Iterate over each local discount and check existence

        if "Local Fuel Discounts" in config:
            localdiscount = config["Local Fuel Discounts"]
        
            mws.click_toolbar("Add")
            for key, value in config["Local Fuel Discounts"].items():
             # Begin setting values
                if not mws.set_value(key, value):
                    log.error(f"Failed setting '{key}' to '{value}' while configuring '{localdiscount}'.")
                    return False     
                else:
                    log.debug(f"'{localdiscount}' already exists in list. Editing...")

        mws.click_toolbar("Save")

        # Check for errors
        errorcode = mws.get_top_bar_text()
        if errorcode:
            if "conflict in qr code prefix" in errorcode.lower() or "cannot be blank" in errorcode.lower() or "correct invalid QR code" in errorcode.lower():
                log.error(errorcode)
                mws.click_toolbar("Cancel")
                mws.click_toolbar("No")
                log.error("Some part of your configuration was incorrect.")
                return False
        
        return True


    def delete_provider(self, name):
        """
        Delete an existing Mobile provider.
        Args:
            name: (str) The name of the Mobile provider to delete
        Examples:
            >>> delete_provider("Tank Bank")
            True
        """
        if not mws.set_value("Mobile Providers", name):
            log.warning(f"Couldn't select provider {name}.")
            return False
        mws.click_toolbar("Delete")
        if not mws.verify_top_bar_text(f"WARNING! Deleting {name} will cause you to lose all configuration, transaction data,"\
            f" and reports for this mobile provider. Are you sure you want to delete {name}?", timeout=30):
            log.warning(f"Didn't get delete confirmation for provider {name}.")
            return False
        mws.click_toolbar("Yes",timeout=5)
        if mws.verify_top_bar_text(f"{name} Enabled field is set to Yes in Configuration", timeout=30):
            log.warning(f"{name} Enabled field id det to Yes in Configuration.")
            mws.click_toolbar("OK")
            return False
        if mws.set_value("Mobile Providers", name):
            log.warning(f"Provider {name} was still in the list after deletion.")
            return False
        return True
    
    def deleteQr(self, QR_list,name):
        """
        Description: Deletes specified codes from the QR Code Prefixes list. Must be called
                     from within the Mobile Payment Configuration menu.
        Args:
            QR_list: A list of strings specifying which entries to delete from
            the QR Code Prefixes list.
        Returns:
            bool: Success/Failure
        Example: 
            mpc = mobile_payment.MobilePaymentConfiguration()
            mpc.deleteQr(["prefix1","prefix2"])
            True
        """
        if not mws.set_value("Mobile Providers", name):
            log.warning(f"Couldn't select provider {name}.")
            return False
        mws.click_toolbar("change")

        if not mws.verify_top_bar_text("The Mobile provider name", timeout=300):
                
            log.error("Mobile payment screen was not load in 5 minutes")
            return False

        mws.select_tab("Prefixes")
        
        # Delete each entry
        for code in QR_list:
            if not mws.set_value("QR Code List", code):
                log.error(f"Could not find '{code}' in QR Code list.")
                return False
            mws.click_toolbar("Delete")
            mws.click_toolbar("Yes")
        
        mws.click_toolbar("Save")
        # No error checking necessary since deleting QR codes never creates errors
        return True

    def deleteDiscount(self, discount_list,name):
        """
        Description: Deletes specified discounts from the Local Fuel Discounts list. Must be called
                     from within the Fuel Discount Configuration Tab.
        Args:
            discount_list: A list of strings specifying which entries to delete from
            the Local Fuel Discounts list.
        Returns:
            bool: Success/Failure
        Example: 
            fdc = mobile_payment.FuelDiscountConfiguration()
            fdc.deldeleteDiscount(["NewLocalDiscount1","NewLocalDiscount2"])
            True
        """
        if not mws.set_value("Mobile Providers", name):
            log.warning(f"Couldn't select provider {name}.")
            return False
        mws.click_toolbar("change")
        
        if not mws.verify_top_bar_text("The Mobile provider name", timeout=300):
                
            log.error("Mobile payment screen was not load in 5 minutes")
            return False

        mws.select_tab("Local Fuel Discounts")
        # Delete each entry
        for localdiscount in discount_list:
            if not mws.set_value("Discount List", localdiscount):
                log.error(f"Could not find '{localdiscount}' in discount list.")
                return False
            mws.click_toolbar("Delete")
            mws.click_toolbar("Yes")
        
        # Check successful deletion
        for localdiscount in discount_list:
            if mws.set_value("Discount List", localdiscount):
                log.error(f"Could not successfully delete '{localdiscount}' from discount list.")
                return False
        
        mws.click_toolbar("Save")
        # No error checking necessary since deleting discounts never creates errors
        return True
                

        