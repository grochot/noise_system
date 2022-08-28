import pyvisa 


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
        return self.hardware






