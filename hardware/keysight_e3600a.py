from pymeasure.instruments import Instrument 
import pyvisa 
from time import sleep
import numpy as np

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
    
    def remote(self):
        self.write(':SYSTem:REMote')    
    
    def outputselect(self,channel=1):
        self.write(':INSTrument:NSELect %G' % channel)
    
    def disabled(self, vol):
        self.vec = np.linspace(vol,0,5)
        for i in self.vec:  
            self.write(':SOURce:CURRent:LEVel:IMMediate:AMPLitude %G' % i)
            sleep(0.4)
        self.write(':OUTPut:STATe 0')
    
    def current(self, vol = 0): 
        self.write(':SOURce:CURRent:LEVel:IMMediate:AMPLitude %G' % vol)
    
    def disable_now(self):
        self.write(':OUTPut:STATe 0')
    
    def reset(self):
        self.write('*CLS')
    
    def get_current(self):
        self.write("*IDN?")
        sleep(0.3)
        answer = self.read()
        return answer 

    
#    
#field = E3600a('ASRL/dev/ttyUSB0::INSTR')    
#field.reset()
# field.remote()
# field.outputselect(1)
# field.current(0.02)
# sleep(1)
# field.enabled()
#field.get_current()