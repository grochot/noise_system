from hardware import daq 
import math
import time
import logging

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

class DAQ_2_channels(): 

    def __init__(self):
        self.daq0 = daq.DAQ("6124/ao0") 
        self.daq1 = daq.DAQ("6124/ao1")
    
    def set_field_2channels(self, angle:float, value:float, channel_1_const:float, channel_2_const:float):
        # Konwersja kąta ze stopni na radiany
        kat_rad = math.radians(angle)
    
    
        x = value * math.cos(kat_rad)
        y = value * math.sin(kat_rad)
        self.daq0.set_field(x/channel_1_const)
        time.sleep(0.2)
        self.daq1.set_field(y/channel_2_const)
        log.info("X: {} Oe ; Y: {} Oe".format(round(x,3),round(y,3)))

        return 1
    def shutdown(self): 
        self.daq0.set_field(0)
        time.sleep(0.2)
        self.daq1.set_field(0)
    
       


   

    



