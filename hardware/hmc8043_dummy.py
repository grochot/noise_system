from pymeasure.instruments import Instrument
from time import sleep, time
from pymeasure.instruments.validators import truncated_range, strict_discrete_set


import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class HMC8043Dummy(Instrument):

    def __init__(self, resourceName, **kwargs):
         pass

    def set_channel(self, channel): 
        pass
        
    
    def enable_channel(self): 
         pass 

    def reset(self): 
         pass

    def enable_channel_master(self): 
         pass
        

    def disable_channel(self): 
         pass
        

    def set_voltage(self, voltage): 
         pass
        

    def shutdown(self):
         pass


# zasilacz = HMC8043('USB0::2733::309::032163928::0::INSTR') 
# sleep(1)

# #zasilacz.reset()
# zasilacz.set_voltage(4)
# zasilacz.set_voltage(4)

# zasilacz.enable_channel()
# zasilacz.enable_channel_master()
# sleep(2)
#zasilacz.set_channel(1)
#zasilacz.disable_channel()



