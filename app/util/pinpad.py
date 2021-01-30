from uArmRobot import robot
import time
import pyodbc
import socket
import os
import runas
import json
import logging

#Paths and script name.
script_path = os.path.dirname(os.path.realpath(__file__))
test_script_name = os.path.basename(__file__)

class PinPadException(Exception):
    def __init__(self, arg):
        self.log = logging.getLogger()
        try:
            self.log.info(arg)
        except:
            print(arg)
        self.message = arg

class _PinPad(robot):

    def __init__(self):
        robot.__init__(self)
        self.log = logging.getLogger()
        try:
            self.log.info(f"Arm COM Port: {self.serialport}")
        except:
            print("Arm COM Port: %s" %self.serialport)
        robot.debug = False
        robot.connect(self)
        robot.emv_connect(self)
        robot.mode(self,0)
        self.pinpad = self.get_pinpad_type()
        if not self.pinpad:
            raise PinPadException("There is no PIN Pad connected to this machine.")
        with open("%s\\..\\data\\pinpad.json"%(script_path)) as f:
            self.json_obj = json.load(f)
        self.pinpad = self.json_obj[self.pinpad]
        self.current_pos = self.pinpad["origin"]
        self.move_arm(self.current_pos, 100000)
        return

    def move_arm(self,coords, speed = 100000):
        """
        @Name: move_arm
        @Description: Moves the robotic arm (with a 10 unit precision) to the 
                      user defined coordinates.
        @Params:
            > coords: (List) A List of floating points (x,y,z) to move the arm.
            > speed: (float) A floating point that represents the arm's 
                     movement speed.
        @Return:
            > None: For now we are assuming that everything went well. This 
                    will be visited again in the future.
        @Throws:
            > None: For now, there is no need to throw an error. This will
                    be revisited in the future.
        @Creator: Jesse Thomas
        """
        if len(coords) < 3:
            self.log.info("Please enter a list of 3 "
                          "elements for the coordinates.")
        x,y,z = coords[:3]
        x2,y2,z2 = self.current_pos[:3]
        if z > z2:
            robot.goto(self,x2, y2, z+12, speed)
            robot.goto(self, x, y, z+12, speed)
            robot.goto(self, x,y,z, speed)
        else:
            robot.goto(self, x2, y2, z2+12, speed)
            robot.goto(self, x, y, z2+12, speed)
            robot.goto(self, x, y, z, speed)
        self.current_pos = coords
        return

    def enter_num(self,num, speed = 100000):
        """
        @Name: enter_num
        @Description: Enters the number on the PIN Pad.
        @Params:
            >num: (Int) The number that should be entered on the PIN Pad
            >speed: (Int) The speed at which the arm will move.
        @Return:
            >None
        @Throws:
            >None
        @Creator: Jesse Thomas
        """
        for number in num:
            self.move_arm(self.pinpad[number], speed)
        self.move_arm(self.pinpad['enter'], speed)
        self.reset_arm(100000)
        return

    def get_pinpad_type(self):
        """
        @Description: Goes into the database of the machine that this code
                      is being run off of and the network database on the EDH
                      to retrieve what PIN Pad the machine is currently using.
        @Params: None
        @returns: The PIN Pad Type (mx915 or iSC250)
        """
        #Getting machine's Register ID
        db = pyodbc.connect('DRIVER={SQL Server};SERVER=POSSERVER01;'
                            'DATABASE=GlobalSTORE;Trusted_Connection=yes')
        cursor = db.cursor()
        cursor.execute("SELECT RGST_ID FROM dbo.REGISTER WHERE MACHINE_NAME = '%s'"
                    %(socket.gethostname()))
        table = cursor.fetchall()
        #Getting the PIN Pad that was setup with that specific machine.
        output=runas.run_sqlcmd("USE Network SELECT PINPadInstalled FROM "
                                "dbo.REGISTER_DEVICES WHERE rgst_id = %s"
                                %(table[0][0]), cmdshell=False)['output']
        output_list = output.split("\n")
        result = []
        for item in output_list:
            item = item.strip()
            if item.isdigit():
                result.append(item)
        if len(result) == 1:
            with open("%s\\..\\data\\pinpad.json"%(script_path)) as f:
                data = json.load(f)
            pinpad_type = data["pinpad type"]
            return pinpad_type[result[0]]
        else:
            #There was only supposed to be one PIN Pad per machine
            return None

    def reset_arm(self, speed = 50000):
        """
        @Name: reset_arm
        @Description: Resets the Robotic arm back to its defined initial
                      position.
        @Params:
            >speed: (Int) The speed in which the arm moves.
        @Return:
            >None
        @Throws:
            >None
        @Creator: Jesse Thomas
        """
        self.move_arm(self.pinpad['origin'])
        return

    def pinpad_message(self):
        """
        @Name: pinpad_message
        @Description: Retrieves the message that is currently displayed on the
                      PIN Pad. At this moment this is using the Status Line 
                      on the POS.
        @Params:
            >None
        @Return:
            >(String)
        @Throws:
            >None
        @Creator: Jesse Thomas
        """
        return

#The object that is essentially the pinpad singleton.
_pinpad = None

#If the _pinpad object is None, instantiate and create a pinpad object.
#Else, leave it alone.
if _pinpad is None:
    _pinpad = _PinPad()

#returns the pinpad singleton whenever this function is called.
def PinPad(): return _pinpad

#############################TEST CODE###################################

if __name__ == '__main__': 
    pass
