from app import mws
import logging
from pywinauto.application import Application
import time
# In house modules
from app.util import constants

class FeatureActivate:
    def __init__(self):
        mws.create_connection()
        self.log = logging.getLogger()
        self.activation_tool = constants.TESTING_TOOLS + r'\hdpassportactivation.exe'
        self.timeout = 30
        self.wait_msg = "Please Wait...."
        self.done_msg = "New Passport features have been activated. "\
            "You will be signed off once you click ok. Please use "\
            "Security Group Maintenance to update security groups."


    def feature_activate(self, skiplist = ['Tablet POS', 'Express Lane']):
        self.log.info("Feature Activation started:")
        site_key = [
            mws.get_text("Site Key 1"),
            mws.get_text("Site Key 2"),
            mws.get_text("Site Key 3")
        ]
        #Open the hdpassportactivation tool
        hdpassportactivation=Application().start(self.activation_tool)
        main=hdpassportactivation['Passport Activation Utility'].wait(
            'ready',5
            )
                
        edit_arr = []
        for child in main.children():
            if child.friendly_class_name() == "Edit":
                edit_arr.append(child)

        #reversing the array
        final_arr = []
        for child in reversed(edit_arr):
            final_arr.append(child)

        radio_arr = []
        for child in main.children():
            if child.friendly_class_name() == "SSOptionWndClass":
                radio_arr.append(child)

        try:
            radio_arr[1].click()
        except:
            self.log.debug("Failed to click the radio button")

        #Setting Edits to the values of the site key
        final_arr[0].set_text(site_key[0])
        final_arr[1].set_text(site_key[1])
        final_arr[2].set_text(site_key[2])

        #Checking all of the listview items
        listview = None
        for child in main.children():
            if child.friendly_class_name() == 'ListView':
                listview = child
                break
        for i in range(len(listview.items())):
            item = listview.items()[i]
            text = item.text() 
            if text == "":
                continue
            elif text not in skiplist:
                item.check()
            else:
                self.log.info('Skipped activating feature ' + text)

        #Clicking the generate site code button
        button_arr=[]
        for child in main.children():
            if child.friendly_class_name() == 'Button':
                button_arr.append(child)
        try:
            button_arr[1].click_input()
        except:
            self.log.debug("Failed to click the button. Trying the old app")
            button_arr[0].click_input()

        #Getting the Site Code from the GUI and Placing in Passport
        time.sleep(.5)
        if final_arr[3] == '':
            self.log.error("The site code was not generated in time")
            return False
        mws.set_text("Site Code 1", final_arr[3].texts()[0])
        mws.set_text("Site Code 2", final_arr[4].texts()[0])
        mws.set_text("Site Code 3", final_arr[5].texts()[0])
        mws.set_text("Site Code 4", final_arr[6].texts()[0])
        hdpassportactivation.kill()

        # Clicking the 'Activate' button.
        mws.search_click_ocr("ACTIVATE")

        start_time = time.time()
        while time.time() - start_time < self.timeout:
            if mws.verify_top_bar_text(self.wait_msg):
                self.log.debug("Waiting for feature activation")
            elif mws.verify_top_bar_text(self.done_msg):
                self.log.debug("Done waiting for feature activation")
                mws.click_toolbar("OK")
                mws.sign_on()
                self.log.info('Feature Activation completed.')                                        
                return True
        
        self.log.error("Failed to finish Feature Activation")
        return False
