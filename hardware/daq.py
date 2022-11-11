from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set
from time import sleep
import nidaqmx

import time
import logging

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())




class DAQ(Instrument):
    def __init__(self, adapter, read_termination="\n", **kwargs):
        super().__init__(
            adapter,
            "NI DAQ" ,
            read_termination=read_termination,
            **kwargs
            
        )
        self.adapter = adapter 
   
    def set_voltage (self, value =1) :
        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan(self.adapter)
            task.write(value)


    

    def shutdown(self):
        """ Disable output, call parent function"""
        self.set_voltage(0)
        super().shutdown()






