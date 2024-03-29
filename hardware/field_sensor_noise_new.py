from pymeasure.instruments import Instrument
from time import sleep, time
from pymeasure.instruments.validators import truncated_range, strict_discrete_set
import serial
import numpy as np
import re


import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class FieldSensor(Instrument):

    def __init__(self, resourceName):
        self.resource = resourceName
     
    
    def read_field(self): 
        self.address = self.resource[4:16]
        print(self.address)
        serial_port = serial.Serial(self.address, 115200, timeout=1)
        serial_port.write(b"READ_SINGLE")
        sleep(0.5)
        text = ""
        text += str(serial_port.readline())
        serial_port.read()
        text = text.replace("b'", "")
        text = text.replace("'", "")
        pattern = "X: (?P<x>[0-9,.,-]+) Y: (?P<y>[0-9,.,-]+) Z: (?P<z>[0-9,.,-]+)"
        result = re.match(pattern, text)
        print(float(result["x"]) ,float(result["y"]) ,float(result["z"]))
        return float(result["x"]) ,float(result["y"]) ,float(result["z"])

    def read_field_init(self):
        self.address = self.resource[4:16]
        ser = serial.Serial(self.address, 115200, timeout=1)
        ser.write("READ_SINGLE".encode())
        ser.readline()
