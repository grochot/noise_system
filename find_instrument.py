import pyvisa 


class FindInstrument(): 
    def __init__(self): 
        rm = pyvisa.ResourceManager() 
        print(rm.list_resources()) 
        inst = rm.open_resource('/dev/ttyS0::INSTR')
        print(inst.query("*IDN?"))



inst = FindInstrument() 


