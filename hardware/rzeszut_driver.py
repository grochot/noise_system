from pymeasure.instruments import Instrument
from time import sleep, time
from pymeasure.instruments.validators import truncated_range, strict_discrete_set
import serial
import numpy as np
import re


import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Rzeszut(Instrument):

    def __init__(self, resourceName):
        self.resource = resourceName
        self.address = self.resource
        self.serial_port = serial.Serial(self.address, 115200, timeout=1)

    def version(self):
        self.serial_port.write(b"V?")
        sleep(0.3)
        text = ""
        text += str(self.serial_port.readline())
        self.serial_port.read()
        return text

    def get_field(self):
        self.serial_port.write(b"FCC")
        sleep(0.3)
        text = ""
        text += str(self.serial_port.readline())
        self.serial_port.read()
        return text

    def get_field_xy(self):
        self.serial_port.write(b"FXY")
        sleep(0.3)
        text = ""
        text += str(self.serial_port.readline())
        self.serial_port.read()
        return text
    
    def get_field_xz(self):
        self.serial_port.write(b"FXZ")
        sleep(0.3)
        text = ""
        text += str(self.serial_port.readline())
        self.serial_port.read()
        return text
    
    def get_field_yz(self):
        self.serial_port.write(b"FYZ")
        sleep(0.3)
        text = ""
        text += str(self.serial_port.readline())
        self.serial_port.read()
        return text
    
    def get_field_all(self):
        self.serial_port.write(b"FTT")
        sleep(0.3)
        text = ""
        text += str(self.serial_port.readline())
        self.serial_port.read()
        return text
    
    def get_angle_yz(self):
        self.serial_port.write(b"FPX")
        sleep(0.3)
        text = ""
        text += str(self.serial_port.readline())
        self.serial_port.read()
        return text
    
    def get_angle_xz(self):
        self.serial_port.write(b"FPY")
        sleep(0.3)
        text = ""
        text += str(self.serial_port.readline())
        self.serial_port.read()
        return text
    
    def get_angle_xy(self):
        self.serial_port.write(b"FPZ")
        sleep(0.3)
        text = ""
        text += str(self.serial_port.readline())
        self.serial_port.read()
        return text
    
    def get_sample_number(self): 
        self.serial_port.write(b"AV?")
        sleep(0.3)
        text = ""
        text += str(self.serial_port.readline())
        self.serial_port.read()
        return text
    
    def set_sample_number(self, number=int): 
        message = "AVS;"+str(number)
        self.serial_port.write(message.encode())
       
    def set_voltage(self, channel = int, voltage = float): 
        message = "WV;"+str(channel)+";"+str(voltage)
        self.serial_port.write(message.encode())    


    def set_pid(self, channel = int, p = float, i = float, d = float, mean = int, step = float, i_max = float, rezerwa = float, preskaler = int): 
        message = "PID;"+str(channel)+";"+str(p)+";"+str(d)+";"+str(i)+";"+str(mean)+";"+str(step)+";"+str(i_max)+";"+str(rezerwa)+";"+str(preskaler)
        self.serial_port.write(message.encode())
    

    def get_pid(self, channel = int): 
        
        message = "WPG;"+str(channel) 
        self.serial_port.write(message.encode())
        sleep(0.3)
        text = ""
        text += str(self.serial_port.readline())
        self.serial_port.read()
        return text
    
    def get_pid_status(self, channel = int): 
        
        message = "WPC;"+str(channel) 
        self.serial_port.write(message.encode())
        sleep(0.3)
        text = ""
        text += str(self.serial_port.readline())
        self.serial_port.read()
        return text

    def set_pid_on(self, channel = int): 
        message = "WPS;"+str(channel)
        self.serial_port.write(message.encode())

    def set_pid_off(self, channel = int): 
        message = "WPL;"+str(channel)
        self.serial_port.write(message.encode())
    
    def sef_pid_value(self, channel = int, value = float): 
        message = "WPV;"+str(channel)+";"+str(value)
        self.serial_port.write(message.encode())
    
    
    
    
    # def read_field(self): 
    #     self.address = self.resource
    #     serial_port = serial.Serial(self.address, 115200, timeout=1)
    #     serial_port.write(b"READ_SINGLE")
    #     sleep(0.5)
    #     text = ""
    #     text += str(serial_port.readline())
    #     serial_port.read()
    #     text = text.replace("b'", "")
    #     text = text.replace("'", "")
    #     pattern = "X: (?P<x>[0-9,.,-]+) Y: (?P<y>[0-9,.,-]+) Z: (?P<z>[0-9,.,-]+)"
    #     result = re.match(pattern, text)
    #     #print(np.sqrt(float(result["x"])**2+float(result["y"])**2+float(result["z"])**2))
    #     return float(result["x"]) ,float(result["y"]) ,float(result["z"])

    # def read_field_init(self):
    #     self.address = self.resource
    #     serial_port = serial.Serial(self.address, 115200, timeout=1)
    #     serial_port.write(b"READ_SINGLE")
    #     sleep(0.5)
    #     text = ""
    #     text += str(serial_port.readline())
    #     serial_port.read()
    #     text = text.replace("b'", "")
    #     text = text.replace("'", "")
    #     pattern = "X: (?P<x>[0-9,.,-]+) Y: (?P<y>[0-9,.,-]+) Z: (?P<z>[0-9,.,-]+)"
    #     result = re.match(pattern, text)
    #     print(np.sqrt(float(result["x"])**2+float(result["y"])**2+float(result["z"])**2))
    #     return float(result["x"]) ,float(result["y"]) ,float(result["z"])



if __name__ == "__main__":
    
    # test = FieldSensor('COM3')

    # test.read_field_init()

    # test.read_field()
    # test.read_field()
    # test.read_field()
    # test.read_field()
    # test.read_field()
    `