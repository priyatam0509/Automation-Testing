from app.framework import mws, Navi
import logging

log = logging.getLogger()

class LoyaltyInterface:
    def __init__(self):
        LoyaltyInterface.navigate_to()

    @staticmethod
    def navigate_to():
        return Navi.navigate_to("Loyalty Interface")

    def configure_fields(self, config, tab=[]):
        """
        Configure data fields in the current menu. Uses recursion to handle tabs and subtabs.
        Helper function to add_provider and change_provider.
        Args:
            config: (dict) A dictionary of all of the controls that the user wants to setup. 
                    This will need to be setup according to the schema in controls.json.
                    tab: (list) The tab to configure.
        Examples:
            >>> cfg = {'General': {'Enabled': 'Yes', 'Host IP Address': '10.5.48.6', 'Port Number': '7900', 'Site Identifier': '1', 'Page2': {'Loyalty Vendor': 'Kickback Points'}}, 'Receipts': {'Outside offline receipt line 2': 'a receipt line'}}
            >>> configure_fields(**cfg)
            True
        """
        # This logic is menu agnostic! Let's reuse it?
        if tab != []:
            if type(tab) is not list:
                tab = [tab]
            mws.select_tab(tab[-1])
        for key, value in config.items():
            if type(value) is dict:
                tab.append(key)
                if not self.configure_fields(value, tab):
                    return False
                tab.remove(key)
            elif not mws.set_value(key, value, tab):
                log.error(f"Could not set {key} with {value} on the {tab} tab.")
                return False
        return True

    def add_provider(self, config, name, provider_type="Generic", cards=()):
        """
        Add a new loyalty provider.
        Args:
            config: (dict) A dictionary of all of the controls that the user wants to setup. 
            This will need to be setup according to the schema in controls.json.
            name: (str) The name of the new loyalty provider
            provider_type: (str) The type of the new loyalty provider
            cards: (tuple/list) Strings representing card masks to add for this provider
        Examples:
            >>> cfg = {'General': {'Enabled': 'Yes', 'Host IP Address': '10.5.48.6', 'Port Number': '7900', 'Site Identifier': '1', 'Page2': {'Loyalty Vendor': 'Kickback Points'}}, 'Receipts': {'Outside offline receipt line 2': 'a receipt line'}}
            >>> add_provider("Tank Bank", cards=['6800', '6801'], **cfg)
            True
        """
        mws.click_toolbar("Add")
        mws.set_value("Loyalty Provider Name", name)
        mws.set_value("Loyalty Provider Type", provider_type)
        mws.click_toolbar("Save")
        if mws.verify_top_bar_text("Cannot add another loyalty provider with the same name"):
            log.warning(f"A provider with the name {name} already exists.")
            return False
        if not self.configure_fields(config):
            return False
        if not self.add_cards(cards):
            return False
        mws.click_toolbar("Save")
        msg = mws.get_top_bar_text()
        if msg:
            self.log.error(f"Unable to save loyalty provider {name}. Passport message: {msg}")
            return False
        mws.click_toolbar("Exit", main=True)
        Navi.navigate_to("Loyalty Interface")
        if [name, provider_type] not in mws.get_value("Loyalty Providers"):
            log.warning(f"{name} was not found in the list of loyalty providers after saving.")
            return False
        return True

    def change_provider(self, config, name, cards_to_add=(), cards_to_delete=()):
        """
        Change the configuration of an existing loyalty provider.
        Args:
            config: (dict) A dictionary of all of the controls that the user wants to change. 
            This will need to be setup according to the schema in controls.json.
            name: (str) The name of the loyalty provider to change
            cards_to_add: (tuple/list) Strings representing card masks to add to this provider
            cards_to_delete: (tuple/list) Strings representing card masks to delete from this provider
            ## Is there a better way to distinguish adding and deleting masks...? ##
        Examples:
            >>> cfg = {'General': {'Enabled': 'Yes', 'Host IP Address': '10.5.48.7', 'Port Number': '7901', 'Site Identifier': '2'}, 'Receipts': {'Outside offline receipt line 2': 'a different receipt line'}}
            >>> change_provider("Tank Bank", ['6802'], ['6800', '6801'], **cfg)
        """
        if not mws.set_value("Loyalty Providers", name):
            log.warning(f"Couldn't select provider {name}.")
            return False
        mws.click_toolbar("Change")
        if not self.configure_fields(config):
            return False
        if not self.add_cards(cards_to_add):
            return False
        if not self.delete_cards(cards_to_delete):
            return False
        mws.click_toolbar("Save")
        msg = mws.get_top_bar_text()
        if msg:
            self.log.error(f"Got an unexpected message when saving loyalty. Passport message: {msg}")
            return False
        return True

    def delete_provider(self, name):
        """
        Delete an existing loyalty provider.
        Args:
            name: (str) The name of the loyalty provider to delete
        Examples:
            >>> delete_provider("Tank Bank")
            True
        """
        if not mws.set_value("Loyalty Providers", name):
            log.warning(f"Couldn't select provider {name}.")
            return False
        mws.click_toolbar("Delete")
        if not mws.verify_top_bar_text(f"WARNING! Deleting {name} will cause you to lose all configuration, transaction data,"\
            f" and reports for this loyalty provider. Are you sure you want to delete {name}?"):
            log.warning(f"Didn't get delete confirmation for provider {name}.")
            return False
        mws.click_toolbar("Yes")
        if mws.verify_top_bar_text(f"{name} Enabled field is set to Yes in Configuration"):
            log.warning(f"Loyalty provider {name} is still enabled. Please disable it using change_provider before deleting it.")
            mws.click_toolbar("OK")
            return False
        if mws.set_value("Loyalty Providers", name):
            log.warning(f"Provider {name} was still in the list after deletion.")
            return False
        return True

    def add_cards(self, cards):
        """
        Add card masks to the loyalty program being edited. Helper for add_provider and change_provider.
        Args:
            cards: (tuple/list) Strings representing card masks to add
        Examples:
            >>> add_cards(('6800', '6801'))
            True
        """
        if cards == []:
            return True
        mask_ctrl_name = "Mask"
        mws.select_tab("Loyalty Card Mask")
        existing_cards = mws.get_value("List")
        for card in cards:
            if (self._check_card_before_add(card, existing_cards)):
                mws.click_toolbar("Add")
                try:
                    mws.get_control(mask_ctrl_name).type_keys(card) # We have to type here for the card # to appear in the list of masks.
                except AttributeError:
                    mask_ctrl_name = "Mask Alt" # If the program did not already have at least one mask configured, the ctrl id is different, so we have to use a different mapping
                    mws.get_control(mask_ctrl_name).type_keys(card) 

        added_cards = mws.get_value("List")
        for card in cards:
            if card not in added_cards:
                log.warning(f"{card} was not found in the list of card masks after adding.")
                return False
        return True

    def _check_card_before_add(self, new_card, cards):
        """
        Check before adding a new card in existing Cards List
        Args:   new_card (string)
                cards (tuple/list) Strings representing existing card masks
        Returns: True/ False
        True - proceed to add the new_card
        False - Already exists in the added card list
        """
        proceed = False
        if new_card not in cards:
            log.warning(f"[{new_card}] was not found in the list of card masks.")
            proceed = True
        return proceed

    def delete_cards(self, cards):
        """
        Delete card masks from the loyalty program being edited. Helper for change_provider.
        Args:
            cards: (tuple/list) Strings representing card masks to delete
        Examples:
            >>> delete_cards(('6802'))
            True
        """
        for card in cards:
            mws.set_value("List", card)
            mws.click_toolbar("Delete")
            if not mws.verify_top_bar_text("Are you sure you want to delete it?"):
                log.warning(f"Didn't get a confirmation prompt when trying to delete mask {card}.")
                return False
            mws.click_toolbar("Yes")
        return True



