import pyvisa 
import serial


class FindInstrument(): 
    def __init__(self): 
        self.rm = pyvisa.ResourceManager() 
        self.hardware = {}
    def find_instrument(self):
        for i in self.rm.list_resources(): 
            print(i) 
            inst = self.rm.open_resource(i)  
            self.hardware[inst.query('*IDN?')] = i
            inst.close()
        #inst = rm.open_resource('ASRL/dev/ttyS0::INSTR')
        #2print(inst.query("*IDN?"))
        print(self.hardware)
        return self.hardware



inst = FindInstrument() 
inst.find_instrument()




