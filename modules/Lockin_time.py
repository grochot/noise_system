import sys
sys.path.append('..')

from hardware.zurich import Zurich
import sys
sys.path.append('.')
from hardware.hmc8043 import HMC8043
# from hardware.picoscope4626 import PicoScope
from hardware.field_sensor_noise_new import FieldSensor 
from hardware.dummy_field_sensor_iv import DummyFieldSensor
from hardware.zurich import Zurich
from logic.fit_parameters_to_file import fit_parameters_to_file, fit_parameters_from_file
from logic.vbiascalibration import vbiascalibration, calculationbias, func, linear_func
from time import sleep
import numpy as np
from time import sleep
import numpy as np
class LockinTime():
    def __init__(self, server=""):
        self.lockin_device = Zurich(server)

    
    def init_scope(self, av:int = 1, input_sel: int = 1, rate: float = 0, length:float = 16348 ):
        self.lockin_device.scope_init(av, input_sel, rate, length)
        
    def init_lockin(self, input_type = 0, differential =False, siginrange_value=1, imp50=False, ac = False, autorange=False):
                      
        if autorange == True:            
            self.lockin_device.siginautorange(0,autorange)
        else:
            self.lockin_device.siginrange(0, siginrange_value)
        self.lockin_device.siginac(0,ac)
        if autorange == True:
            self.lockin_device.currinautorange(0,autorange)
        else:
            self.lockin_device.currinrange(0,siginrange_value) 
        self.lockin_device.siginac(0,ac)                 
        self.lockin_device.oscillatorfreq(0,0) 
        self.lockin_device.oscillatorfreq(1,0)
        self.lockin_device.siginscaling(0,1)
        self.lockin_device.siginfloat(0,1)
        self.lockin_device.siginimp50(0,imp50)
        self.lockin_device.sigindiff(0,differential)
        self.lockin_device.setosc(0,0)
        self.lockin_device.setosc(1,1)
        self.lockin_device.setadc(0,input_type) # 0 - voltage, 1 - current
        self.lockin_device.settimeconst(0, 0.3)
        self.lockin_device.setorder(0, 2)
        self.lockin_device.setharmonic(0, 1)
        self.lockin_device.setharmonic(1, 1)
        self.lockin_device.outputamplitude(0,0)
        self.lockin_device.enableoutput(1,1)
        self.lockin_device.outputoffset(0,0)
        self.lockin_device.outputon(0,1)
        self.lockin_device.outputrange(0,10)
        self.lockin_device.enabledemod(0,1)
        self.lockin_device.aux_set_manual(1)
        self.lockin_device.auxout(1,0)
         

   
    def get_wave(self):
        value = self.lockin_device.get_wave()
        time = self.lockin_device.to_timestamp(value)

        return time, value[0]['wave'][0]

    def set_ac_field(self, value=0, freq=1): # TO DO
        self.lockin_device.oscillatorfreq(1,freq)
        self.lockin_device.outputamplitude(1,value)
       
    def set_dc_field(self, value=0):
        self.lockin_device.outputoffset(0,value)
      
    def lockin_measure_R(self,demod, averaging_rate):
        results = []
        avg = 0
        for samp in range(averaging_rate):
           sample = self.lockin_device.getsample(demod)
           avg += np.sqrt(sample['x'][0]**2+sample['y'][0]**2)
        results = avg/averaging_rate
        return results
    
    def set_constant_vbias(self, value=0):
         self.lockin_device.auxout(1,value/1000)
    
    def set_lockin_freq(self,freq):
        self.lockin_device.oscillatorfreq(0, freq)


    def shutdown(self):
        self.lockin_device.auxout(1,0)
        self.lockin_device.outputamplitude(0,0)
        self.lockin_device.outputoffset(0,0)    
        self.lockin_device.outputon(0,0)
    
    def set_field(self, value_dc=0, value_ac=0, freq=1, calib_dc=1, calib_ac = 1):
        self.dc_value = (value_dc*50)/calib_dc
        self.set_dc_field(self.dc_value)
        self.ac_value = (value_ac*50)/calib_ac
        self.set_ac_field(self.ac_value, freq)
        
# ########################### Test ###########################3
# import matplotlib.pyplot as plt
# import matplotlib.animation as animation
# from matplotlib import style
# style.use('fivethirtyeight')
# fig = plt.figure()
# ax1 = fig.add_subplot(1,1,1)
# loc = LockinTime('192.168.66.202')

# loc.init_scope(1,1,0,16348)

# data = loc.get_wave()

# import matplotlib.pyplot as plt
# plt.plot(data[0], data[1])
# plt.show()


########################### Test ###########
# import matplotlib.pyplot as plt
# import matplotlib.animation as animation
# from matplotlib import style
# style.use('fivethirtyeight')
# fig = plt.figure()
# ax1 = fig.add_subplot(1,1,1)
# loc = LockinTime("192.168.66.202")

# loc.init_lockin_device(1)
# loc.init_scope(1,1,9,1000)




# loc.set_constant_vbias(50)

# y = loc.get_wave()
# plt.plot(y[0], y[1], "ro-")
# plt.title("Real Time plot")
# plt.xlabel("x")

    
# plt.show()

   
  
    


  


    