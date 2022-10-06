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
        self.resource = resourceName
        super().__init__(
            resourceName,
            "FieldSensor",
            includeSCPI=True,
            **kwargs
            
        )
     
    
    def read_field(self): 
        self.address = self.resource[4:16]
        ser = serial.Serial(self.address, 115200, timeout=1) 
        try:
            ser.write("d".encode())
            out = ''

            
            out += str(ser.readline().decode())

            if out:
                print(out)
        except:
            pass

        x, y, z = out.split(',')
        x = float(x)
        y = float(y)
        z = float(z)
        #field = np.sqrt(x**2+y**2+z**2)
       
        return x,y,z
