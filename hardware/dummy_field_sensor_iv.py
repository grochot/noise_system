from pymeasure.instruments import Instrument
from time import sleep, time
from pymeasure.instruments.validators import truncated_range, strict_discrete_set
import serial
import numpy as np



import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class DummyFieldSensor(Instrument):

    def __init__(self, resourceName):
        self.resource = resourceName
     
    
    def read_field(self): 
        return 0.0 , 0.0 ,0.0

    def read_field_init(self): 
        return 0.0 , 0.0 , 0.0
    
    def set_dynamic_mode(self):
        pass

    def close(self): 
        pass
