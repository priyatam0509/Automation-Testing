from app import mws, Navi
import logging, time

class AuxiliaryNetworkCardConfig:
    def __init__(self):
        self.log = logging.getLogger()
        AuxiliaryNetworkCardConfig.navigate_to()

    @staticmethod
    def navigate_to():
        """
        Navigates to the Auxiliary Network Card Configuration feature module.
        Args: None
        Returns: Returns the result of execution of Navi.navigate_to()
        """
        return Navi.navigate_to("Auxiliary Network Card Configuration")

    def configure(self, config):
        """
        Configures fields in the Auxiliary Network Card Configuration feature module.
        Args:
            config: A dictionary of controls so the user can add the information that
                    they need to. This is according to the schema in controls.json.
        Returns:
            bool: Success/Failure
        Example: 
            ancc_info = {
                "Issuer_Name_1": {
                    "ISO Number": "123",
                    "Print Account Number On Aux Network Sales Report": "No",
                    "Beginning Position of Account Number": "0",
                    "Number of Characters in Account Number": "1",
                    "Discount Group": "NONE"
                }
                "Issuer_Name_2": {
                    "ISO Number": "456"
                }
            }

            ancc = aux_network_card.AuxiliaryNetworkCardConfig()
            ancc.configure(ancc_info)
            True
        """
        # Iterate over each issuer dictionary
        for issuer in config:
            # Check existence
            if mws.set_value("Issuers", issuer): # if issuer exists:
                self.log.debug(f"Found '{issuer}' in list, editing...")
            else:  #else add
                self.log.debug(f"Adding {issuer}...")
                mws.click_toolbar("Add")

            # Use name in list as Issuer Name
            config[issuer]['Issuer Name'] = issuer
            # Set other values
            for key, value in config[issuer].items():
                if not mws.set_value(key, value):
                    self.log.error(f"Could not '{key}' to '{value}' for issuer: '{issuer}'.")
                    return False
        
        mws.click_toolbar("Save")
        # Check for error messages during timeout
        starttime = time.time()
        while time.time() - starttime < 5:
            top_text = mws.get_top_bar_text()
            if top_text:
                if "cannot be blank" in top_text.lower():
                    self.log.error(top_text)
                    self.log.error("Some part of your configuration is incorrect.")
                    return False
                if "is duplicated" in top_text.lower():
                    self.log.error(top_text)
                    self.log.error("This error may occur when the entirety of one ISO number matches the beginning of another ISO number.")
                    return False
        return True

    def delete(self, issuer_list):
        """
        Deletes specified issuers from the list in Auxiliary Network Card Config.
        Args:
            issuer_list: a string or list of strings containing the names of the issuer(s) to delete.
        Returns:
            bool: Success/Failure
        Example: 
            issuers_list = ["Issuer_Name_1","Issuer_Name_2"]

            ancc.delete_issuer(issuers_list)
            True
        """
        # Select and delete each issuer
        for issuer in issuer_list:
            if not mws.set_value("Issuers", issuer):
                self.log.error(f"Could not find {issuer} in list. Skipping...")
                continue
            mws.click_toolbar("Delete")
            mws.click_toolbar("Yes")

        # Check for successful deletion
        for issuer in issuer_list:
            if issuer in mws.get_value("Issuers"):
                self.log.error(f"Could not successfully delete {issuer} from list.")
                return False

        mws.click_toolbar("Save")
        return True
        