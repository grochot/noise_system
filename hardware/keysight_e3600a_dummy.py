from pymeasure.instruments import Instrument 
import pyvisa 

class E3600aDummy(Instrument):
    def __init__(self, adapter, read_termination="\n", **kwargs):
        super().__init__(
            adapter,
            "Keysight E3600a" ,
            read_termination=read_termination,
            **kwargs
        )

    def enabled(self):
        pass
    
    def disabled(self):
        pass
    
    def voltage(self, vol = 0): 
        pass
    
    
    