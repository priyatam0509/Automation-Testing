from tkinter import Tk, Toplevel, StringVar, Label, N, S, E, W
from threading import Thread, Lock
import time
import random
import json

__author__ = "Jesse Thomas"


"""
Instructions:
    Step 1: Have a JSON file created at the specified path (default is 
            C:\\automation\\test_info.json)
    Step 2: Have the following information set to what you need it to:
            "gui position" : true or false
            "test count" : 0 (Number of test cases executed.)
            "expected test number" : n (The number of expected test cases. Not n)
            "current test name" : "" The name of the current test case
    Step 3: When you need to change the position of the GUI set gui position to true for the 
            top left corner of the screen, and false of the middle left of the screen.
    Step 4: When you need to change the test case information please change the following for
            file: 
                test count -> increment by 1
                current test name -> whatever name is the NEW current test case
                last result -> what the result was for the last test case. True for Pass.
                               False for failure.
    
"""

class Overlay(Thread):
    """
    Description: A GUI overlay that will update test case information
    based off of what the test harness gives to the corresponding JSON file.
    """
    def __init__(self, thread_lock, json_path = "C:\\automation\\test_info.json"):
        Thread.__init__(self)
        self.TOP_LEFT = True
        self.MIDDLE_LEFT = False
        self.PASS = True
        self.FAIL = False

        #Creating initial values for the overlay.
        self.thread_lock = thread_lock
        self.done = False
        self.test_info_path = json_path
        with open(self.test_info_path) as f:
            self.test_info = json.load(f)
        self.root = Tk()
        self.gui = Toplevel(self.root)
        self.total = self.test_info["expected test number"]
        self.position = self.test_info["gui position"]
        self.counter = self.test_info["test count"]
        self.passCounter = self.test_info["pass count"]
        self.failCounter = self.test_info["fail count"]
        self.test_name = self.test_info["current test name"]
        self.progressText = StringVar()
        self.statusText = StringVar()
        self.buttonText = StringVar()
        self.passesText = StringVar()
        self.failsText = StringVar()
        self.testCaseText = StringVar()

        self.root.withdraw()
        self.gui.overrideredirect(1)
        self.gui.attributes("-topmost", True)
        self.gui.config(bg = "snow")

        self.w = 127
        self.h = 75
        self.gui.columnconfigure(0, minsize = 63)
        self.gui.columnconfigure(1, minsize = 63)

        #Setting initial values to the GUI pieces.
        self.guiPosition(self.position)
        self.progressText.set("Completed: {}/{}".format(self.counter, self.total))
        self.statusText.set("? / ?")
        self.passesText.set("Passed: {}".format(self.passCounter))
        self.failsText.set("Failed: {}".format(self.failCounter))
        self.testCaseText.set("{}".format(self.test_name))
        
        #Making the final GUI pieces and placing them onto the initial form.
        self.Progress = Label(self.gui, textvariable = self.progressText, bg = "light sky blue")
        self.Passes = Label(self.gui, textvariable = self.passesText, bg = "chartreuse")
        self.Fails = Label(self.gui, textvariable = self.failsText, bg = "tomato")
        self.TestCase = Label(self.gui, textvariable = self.testCaseText, wraplength=127, bg  = "light sky blue")
        self.Progress.grid(columnspan = 2, sticky = N+S+E+W)
        self.Passes.grid(row = 1, column = 0, sticky = N+S+E+W)
        self.Fails.grid(row = 1, column = 1, sticky = N+S+E+W)
        self.TestCase.grid(columnspan = 2, row=2, sticky = N+S+E+W)
        self.update_gui()
        
    
    def run(self):
        """
        Description: An overridden run method from Thread. This is the main loop that will run
                    everything needed for the overlay.
        """
        while not self.done:
            try:
                #Opening the JSON file path and loading its information.
                with self.thread_lock:
                    with open(self.test_info_path) as f:
                        self.test_info = json.load(f)
                #Updating the GUI with the recent test information.
                if self.position != self.test_info["gui position"]:
                    self.guiPosition(self.test_info["gui position"])
                    self.position = not self.position
                if self.test_name != self.test_info["current test name"]:
                    self.test_name = self.test_info["current test name"]
                    self.update_gui()
                if self.test_info["test count"] > self.counter:
                    self.counter = self.test_info["test count"]
                    self.test_name = self.test_info["current test name"]
                    if self.test_info["last result"] == True:
                        self.test_info["pass count"] = self.test_info["pass count"] + 1
                        self.passCounter = self.test_info["pass count"]
                        print(self.test_info["pass count"])
                    else:
                        self.test_info["fail count"] = self.test_info["fail count"] + 1
                        self.failCounter = self.test_info["fail count"]
                    self.update_gui()
                    #Writing any new test information back into the JSON file.
                    with self.thread_lock:
                        with open(self.test_info_path, 'w') as f:
                            f.write(json.dumps(self.test_info))
            except Exception as e:
                print(e)
                continue
            self.root.update()
            # added a sleep here such that we can actually get access to the file at some point :)
            time.sleep(5)

    def end(self):
        """
        Description: Checks to see if this is a root Thread. If it is, the thread will 
                     be destroyed and then the program will exit.
        """
        if self.root:
            self.root.destroy()
        exit()

    
    def guiPosition(self, position):
        """
        Description: Checks to see where the GUI should be. There are two positions: Top left
                     corner and middle left of the monitor. Currently hard coded for a 600x800
                     monitor.
        Params:
            position: (boolean) the position of the Overlay GUI. True for the top left corner,
                      false for the middle left of the screen.
        """
        if position:
            posX = 2
            posY = 2
        else:
            posX = 2
            posY = 388

        self.gui.geometry('%dx%d+%d+%d' % (self.w, self.h, posX, posY))
        self.root.minsize(self.w, self.h)
    
    #update gui texts and colors, if something weird is passed in it will press pause
    def update_gui(self):
        """
        @Description: Updates the look of the GUI. This makes sure that the information that 
                      user sees is accurate to the information that is really there.
        Params: None
        """
        self.progressText.set("Completed: {}/{}".format(self.counter, self.total))
        self.passesText.set("Passed: {}".format(self.passCounter))
        self.failsText.set("Failed: {}".format(self.failCounter))
        self.testCaseText.set("{}".format(self.test_name))
        self.Progress.config(fg = "black")
        self.Passes.config(bg = "chartreuse")
        self.Fails.config(bg = "tomato")
            
############# TEST CODE ###############     
if __name__ == "__main__":
    l = Lock()
    overlay = Overlay(l)
    overlay.run()
    pass