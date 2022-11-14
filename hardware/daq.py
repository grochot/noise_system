from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set
from time import sleep
import nidaqmx

import time
import logging

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())




class DAQ():
    def __init__(self, adapter):
        self.adapter = adapter
        
   
    def set_field (self, value =1):
        self.constant_field = 1
        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan(self.adapter)
            task.write(value/self.constant_field)


    

    def shutdown(self):
        """ Disable output, call parent function"""
        self.set_voltage(0)




