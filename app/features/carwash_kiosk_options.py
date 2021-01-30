from app import mws, Navi
import logging

class CarWashKioskOptions:

    def __init__(self):
        self.log = logging.getLogger()
        CarWashKioskOptions.navigate_to()
        self.RCPT_HDR_ALIGN_KEY = "Receipt Header Align"
        self.RCPT_TRLR_ALIGN_KEY = "Receipt Trailer Align"

    @staticmethod
    def navigate_to():
        return Navi.navigate_to("Car Wash Kiosk Options")

    def configure(self, config):
        """
        Configure settings in Car Wash Kiosk Options.
        Args:
            config: (dict) A dictionary describing how to configure the menu. See example.
        Returns: (bool) True/False for success/failure.
        Example:
            >>> cfg = { "Kiosk":
                            { "1":
                                { "Enable Kiosk": True,
                                  "Enable Bill Acceptor": True,
                                  "Enable Coin Acceptor": True,
                                  "Enable Change Back": True,
                                  "Enable Voice Prompt": False,
                                  "Wash Bay": "1",
                                  "End of Transaction Instructions": ["Thank you", "Have a nice day"] },
                              "2": { "Enable Kiosk": False }
                            },
                        "Receipt":
                            { "Use CRIND Receipt Header": True,
                              "Use CRIND Receipt Trailer": False,
                              "Receipt Trailer": ["Thank you for", "using our car wash"],
                              "Receipt Header Align": "Left",
                              "Receipt Trailer Align": "Center"
                            },
                        "Cash":
                            { "Max cash accepted per transaction": "2500",
                              "Total number of bills in vault exceeds": "600",
                              "$20": True,
                              "$2": False
                            },
                        "General":
                            { "Use CRIND Promotional Display": False,
                              "Promotional Display": ["Welcome to", "the car wash"]
                            }
                      }
            >>> CarWashKioskOptions().configure(cfg)
            True
        """
        for tab, settings in config.items():
            mws.select_tab(tab)
            if tab == "Kiosk":
                for kiosk_num, kiosk_cfg in config[tab].items():
                    if not mws.set_value("Kiosks", kiosk_num, tab):
                        return False
                    mws.search_click_ocr("Change")
                    for field, value in kiosk_cfg.items():
                        if field == "End of Transaction Instructions":
                            if not self._config_text_list("End of Transaction Instructions edit", "End of Transaction Instructions list", value):
                                return False
                        else:
                            mws.set_value(field, value, tab)
                    mws.search_click_ocr("Update List")
            else:
                for field, value in settings.items():
                    if type(value) == list:
                        if not self._config_text_list(f"{field} edit", f"{field} list", value):
                            return False
                    elif field == self.RCPT_HDR_ALIGN_KEY:
                        if not mws.search_click_ocr(value):
                            return False
                    elif field == self.RCPT_TRLR_ALIGN_KEY:
                        if not mws.search_click_ocr(value, instance=2):
                            return False
                    elif not mws.set_value(field, value, tab):
                        return False

        try:
            mws.click_toolbar("Save", main=True)
        except ConnException:
            self.log.error(f"Unable to save Car Wash Kiosk Options. Top bar message: {mws.get_top_bar_text()}")
            mws.recover()
            return False
        return True

    def _config_text_list(self, edit_control, list_control, lines):
        """
        Configure a field such as End of Transaction Instructions.
        """
        mws.get_control(list_control).send_keystrokes("{HOME}")
        for line in lines:
            if not mws.set_value(edit_control, line):
                return False
            mws.get_control(edit_control).send_keystrokes("{ENTER}")
        return True               
