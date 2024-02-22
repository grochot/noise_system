from pymeasure.instruments import Instrument
from time import sleep, time
from pymeasure.instruments.validators import truncated_range, strict_discrete_set
import pyvisa

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class HMC8043():

    def __init__(self, resourceName, **kwargs):
        rm = pyvisa.ResourceManager()
        self.inst = rm.open_resource(resourceName)

    def set_channel(self, channel): 
        self.inst.write("INST:NSEL {}".format(channel))
    
    def inst_out(self,channel):
        for i in range(1):
            self.inst.write("INST:OUT {}".format(channel))
            sleep(0.1)

    
    def enable_channel(self): 
        for i in range(1):
            self.inst.write("OUTP ON") 
            sleep(0.1)

    def reset(self): 
        self.inst.write("*RST") 
    
    def apply(self,voltage,current, out):
        for i in range(1):
            self.inst.write("APPLY {},{},{}".format(voltage,current, out)) 
            sleep(0.1)


    def enable_channel_master(self): 
        self.inst.write("OUTP:MAST ON") 
        

    def disable_channel(self): 
        # self.write("OUTP:CHAN OFF") 
        # sleep(0.2)
        for i in range(4):
            self.inst.write("OUTP OFF") 
            sleep(0.1)
        

    def set_voltage(self, voltage): 
        self.inst.write("VOLT {}".format(voltage))
    
    def set_current(self, current): 
        for i in range(1):
            self.inst.write("CURR {}".format(current))
            sleep(0.1)
        
    def disabled(self):
        """ Turns on the persistent switch,
        ramps down the current to zero, and turns off the persistent switch.
        """
        # for i in range(2):
        #     self.opc()
        #     self.disable_channel()
        #     sleep(0.1)
        
        self.disable_channel()
        sleep(1)
        self.inst.close()

    def shutdown(self):
        """ Turns on the persistent switch,
        ramps down the current to zero, and turns off the persistent switch.
        """
        self.disable_channel()
    
    def opc(self):
        self.inst.write("*OPC")
    


# zasilacz = HMC8043('USB0::2733::309::032163928::0::INSTR', timeout=50000) 
# # # sleep(3)
# zasilacz.disabled()

# #zasilacz.reset()
# # zasilacz.opc()

# # # sleep(2)
#zasilacz.apply(0.8,0.3,"OUT1")
# # # zasilacz.opc()
# # sleep(1)
# zasilacz.inst_out(1)
# zasilacz.set_current(0.002)
# zasilacz.enable_channel()
#zasilacz.disabled()
# zasilacz.opc()
# # sleep(2)



# zasilacz.inst_out(1)
# sleep(3)
# # zasilacz.enable_channel()
# # sleep(4)
# zasilacz.disable_channel()
# sleep(0.5)
# zasilacz.apply(0.2,0.3)
# sleep(0.5)
# zasilacz.enable_channel()
# sleep(0.5)
# zasilacz.enable_channel_master()


#zasilacz.reset()
#zasilacz.set_voltage(0.2)
# #zasilacz.set_voltage(4)
# zasilacz.set_channel(1)
# zasilacz.enable_channel()
# zasilacz.enable_channel_master()
# # sleep(2)
# #zasilacz.set_channel(1)
# #zasilacz.disable_channel()



