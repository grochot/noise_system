from pymeasure.instruments import Instrument 
import pyvisa 
from time import sleep

class E3600a(Instrument):
    def __init__(self, adapter, read_termination="\n", **kwargs):
        super().__init__(
            adapter,
            "Keysight E3600a" ,
            read_termination=read_termination,
            **kwargs
        )

    def enabled(self):
        self.write(':OUTPut:STATe 1')
    
    def disabled(self):
        self.write(':OUTPut:STATe 0')
    
    def voltage(self, vol = 0): 
        self.write(':SOURce:VOLTage:LEVel:IMMediate:AMPLitude %G' % vol)
    
    
# field = E3600a('ASRL/dev/ttyUSB0::INSTR')    
# field.voltage(1)
# sleep(1)
# field.enabled()