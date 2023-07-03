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
        
    def shutdown(self, vol=1):
        self.vec = np.linspace(vol,0,5)
        for i in self.vec:  
            self.write(':SOURce:CURRent:LEVel:IMMediate:AMPLitude %G' % i)
            sleep(0.4)
        self.write(':OUTPut:STATe 0')
    
    def set_field(self, vol = 0): 
        if vol < 0:
            print(vol)
            self.write(':INSTrument:NSELect 1')
            self.write(':SOURce:CURRent:LEVel:IMMediate:AMPLitude 0')
            self.write(':OUTPut:STATe 0')
            self.write(':INSTrument:NSELect 2')
            self.write(':SOURce:CURRent:LEVel:IMMediate:AMPLitude %G' % abs(vol))
            self.write(':OUTPut:STATe 1')
        else: 
            self.write(':INSTrument:NSELect 2')
            self.write(':SOURce:CURRent:LEVel:IMMediate:AMPLitude 0')
            self.write(':OUTPut:STATe 0')
            self.write(':INSTrument:NSELect 1')
            self.write(':SOURce:CURRent:LEVel:IMMediate:AMPLitude %G' % vol)
            self.write(':OUTPut:STATe 1')
    
    def disable_now(self):
        self.write(':OUTPut:STATe 0')

    def reset(self):
        self.write("*CLS")
    
    
# field = E3600a('COM9')    
# field.remote()
# # field.reset()
# sleep(0.2)
# field.set_field(0.004)
# sleep(1)
# #field.enabled()


#field.disable_now()


