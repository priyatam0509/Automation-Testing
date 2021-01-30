# uArm Swift Pro - Python Library
# Created by: Richard Garsthagen - the.anykey@gmail.com
# V0.2 - June 2017 - Still under development

import serial
import time
import protocol_swiftpro as protocol
import threading
import sys
import math
from math import pi
from serial.tools import list_ports
import logging

UARM_HWIDS = ['0403:6001', '2341:0042']
class robot:
    serid = 100
    num_of_robots = 0
    baud = 115200
    serial_timeout = 1
    connect_timeout = 1
    debug = False
    baseThreadCount = threading.activeCount()
    delay_after_move = 0.1
    
    def __init__(self):
        self.log = logging.getLogger()
        try:
            self.serialport = self.uarm_ports()
        except Exception as e:
            print(e)
            self.serialport = "com3"
        self.connected = False
        self.connected_emv = False
        robot.num_of_robots += 1
        self.moving = False
        self.pumping = False
        self.ser = None
        self.emv = None

    def connect(self, timeout=10):
        for port in self.serialport:
            try:
                if (self.debug): print ("trying to connect to: " + port.lower())
                self.ser = serial.Serial(port.lower(), 115200, timeout=1)
                time.sleep(self.connect_timeout)
                Ready = False
                start_time = time.time()
                while (not Ready) and time.time() - start_time < timeout:
                    line = self.ser.readline()
                    if (self.debug): print (line)
                    if b"emv" in line.lower():
                        self.ser.close()
                        break
                    if line.startswith(b"@5"):
                        Ready = True
                        self.connected = True
                        if (self.debug): print ("Connected!")
                        del self.serialport[port]
                        return True
                line = self.ser.readline() # Ignore if @6 response is given
                print (line)             
            except Exception as e:
                if (self.debug): print ("Error trying to connect to: " + port.lower() + " - " + str(e))
                self.connected = False
        if not self.connected:
            return False
        else:
            return True

    def emv_connect(self, timeout=30):
        """
        @Name: emv_connect
        @Description: Attempts to try to connect to the EMV Arduino hardcoded to be at port 9600
        @Params: None
        @Return:
            >boolean: True if the EMV Arduino was connected. False otherwise.
        @Throws: None
        @Creator: Jesse Thomas
        """
        for port in self.serialport:
            try:
                if self.debug: print("trying to connect to: " + port.lower())
                self.emv = serial.Serial(port.lower(), 115200, timeout=1)
                start_time = time.time()
                while not self.connected_emv and \
                      time.time() - start_time < timeout:
                    if b"emv" in self.emv.readline().lower():
                        if self.debug: print(self.emv.readline().lower())
                        time.sleep(self.connect_timeout)
                        self.connected_emv = True
                        del self.serialport[port]
                        return True
            except Exception as e:
                if self.debug: print("Error trying to connect to: " + port.lower() + " - " + str(e))
                self.connected_emv = False
        #This is just a sanity check in case something is broken upstairs.
        if not self.connected_emv:
            return False
        else:
            return True
    
    def uarm_ports(self):
        uarm_ports = {}

        for i in list_ports.comports():
            if i.hwid[12:21] in UARM_HWIDS:
                uarm_ports[i[0]] = i.hwid[12:21]
                if self.debug: print(i.hwid[12:21])
                if self.debug: print(i.hwid)
        return uarm_ports

    def disconnect(self):
        if self.connected:
            if (self.debug): print ("Closing serial connection")
            self.connected = False
            self.ser.close()
        else:
            if (self.debug): print ("Disconnected called while not connected")

    def sendcmd(self, cmnd, waitresponse):
        if (self.connected):
            id = self.serid
            self.serid += 1
            cmnd = "#{} {}".format(id,cmnd)
            cmndString = bytes(cmnd + "\n")
            if (self.debug): print ("Serial send: {}".format(cmndString))
            self.ser.write(cmndString)
            if (waitresponse):
                line = self.ser.readline()
                while not line.startswith("$" + str(id)):
                    line = self.ser.readline()
                if (self.debug): print ("Response {}".format(line))
                if (self.moving):
                    self.moving = False
                    time.sleep(self.delay_after_move)
                return line
        else:
            if (self.debug):
                print("error, trying to send command while not connected")
                self.moving = False

    def emv_sendcmd(self, cmnd, waitresponse, timeout=30):
        start_time = time.time()
        if (self.connected_emv):
            self.emv.write(cmnd)
            if (waitresponse):
                line = self.emv.readline()
                while line == "" and time.time() - start_time < timeout:
                    line = self.emv.readline()
                return line
        else:
            print("error, trying to send command while not connected")

    def goto(self,x,y,z,speed):
        self.moving = True
        x = str(round(x, 2))
        y = str(round(y, 2))
        z = str(round(z, 2))
        s = str(round(speed, 2))
        cmd = protocol.SET_POSITION.format(x,y,z,s)
        self.sendcmd(cmd, True)

    def async_goto(self,x,y,z, speed):
        self.moving = True
        t = threading.Thread( target=self.goto , args=(x,y,z,speed) )
        t.start()

    def pump(self, state):
        self.pumping = state
        cmd = protocol.SET_PUMP.format(int(state))
        self.sendcmd(cmd,True)

    def mode(self, modeid):
        # 0= Normal
        # 1= Laser
        # 2= 3D Printer
        # 3= Universal holder
        cmd = protocol.SET_MODE.format(modeid)
        self.sendcmd(cmd,True)

    @staticmethod
    def PointsInCircum(r,n):
        return [(math.cos(2*pi/n*x)*r,math.sin(2*pi/n*x)*r) for x in range(0,n+1)]


    def drawCircle(self, centerX, centerY, Radius, Resolution, Speed, DrawingHeight, StartFinishedHeight):
        if (Resolution < 4):
            #ignore drwaing circle, to low resoution
            if (self.debug): print ("Ignoring drwaing circle, to low resolution requested")
            return
        if (self.debug): print ("Drwaing circle of {} radius in {} steps".format(Radius,Resolution))
        offsetx = centerX
        offsety = centerY 
        c = self.PointsInCircum(Radius,Resolution)
        bx,by = c[0]
        self.goto(offsetx+bx,offsety+by,StartFinishedHeight,Speed)

        for p in range(0,Resolution):
            x,y = c[p]
            self.goto(offsetx+x,offsety+y,DrawingHeight,Speed)

        self.goto(offsetx+bx,offsety+by,DrawingHeight,Speed)
        time.sleep(0.5)
        self.goto(offsetx+bx,offsety+by,StartFinishedHeight,Speed)

if __name__ == "__main__":
    r = robot()
    r.debug = True
    r.connect()
        
            

            
        

        

        



        

        
            
            
        







