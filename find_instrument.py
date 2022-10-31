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
            file = open("finded_instruments.txt", "r")
            content = file.read()
            file.close()
            content_tab = content.split(",") 
            for k in self.hardware.keys(): 
                if k in content_tab: 
                    pass 
                else: 
                    file.open("finded_instruments.txt", 'a')
                    save_data = k + ","
                    file.write(save_data)
                    file.close()

            file.open("finded_instrumnets.txt", 'r') 
            instruments = file.read().split(',')

            return instruments

    
    def show_instrument(self): 
    	return self.rm.list_resources()


dd = FindInstrument()

dd.find_instrument()