from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set
from time import sleep

import time
import logging

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())
import PyDAQmx 



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
        task = PyDAQmx.Task()
        task.CreateAOVoltageChan(self.adapter,"",-10.0,10.0,PyDAQmx.DAQmx_Val_Volts,None) 
        task.StartTask()
        task.WriteAnalogScalarF64(1,10.0,value,None)
        task.StopTask()

    

    def shutdown(self):
        """ Disable output, call parent function"""
        self.set_voltage(0)
        super().shutdown()






