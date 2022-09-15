from pymeasure.instruments import Instrument
from time import sleep, time
from pymeasure.instruments.validators import truncated_range, strict_discrete_set
import serial
import numpy as np


import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class FieldSensor(Instrument):

    def __init__(self, resourceName, **kwargs):
        kwargs.setdefault('read_termination', '\n')
        super().__init__(
            resourceName,
            "FieldSensor",
            includeSCPI=True,
            **kwargs
        )
     
    
    def read_field(self, adress): 
        ser = serial.Serial(adress, 115200, timeout=1) 
        x, y, z = ser.readline().decode("utf-8").split(',')    
        #field = np.sqrt(x**2+y**2+z**2)
        return x,y,z