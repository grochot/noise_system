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
class LockinField():
    def __init__(self, server=""):
        self.lockin = Zurich(server)


    def init(self):                     
        self.lockin.oscillatorfreq(0,0) 
        self.lockin.oscillatorfreq(1,0)
        self.lockin.siginscaling(0,1)
        self.lockin.siginfloat(0,1)
        self.lockin.setosc(0,0)
        self.lockin.setosc(1,1)
        self.lockin.setadc(0,0) # 0 - voltage, 1 - current
        self.lockin.settimeconst(0, 0.3)
        self.lockin.setorder(0, 2)
        self.lockin.setharmonic(0, 1)
        self.lockin.setharmonic(1, 1)
        self.lockin.outputamplitude(0,0)
        self.lockin.enableoutput(1,1)
        self.lockin.outputoffset(0,0)
        self.lockin.outputon(0,1)
        self.lockin.siginrange(0,10)
        self.lockin.outputrange(0,10)
        self.lockin.enabledemod(0,1)
        self.lockin.aux_set_manual(1)
        self.lockin.auxout(1,0)
        self.lockin.daq.sync() 

   

    
    def set_voltage(self, value=0):
        self.lockin.outputoffset(0,value/1000)
        self.lockin.daq.sync()
    
    def lockin_measure_point(self,demod, averaging_rate):
        results = []
        avg = 0
        for samp in range(averaging_rate):
           sample = self.lockin.getsample(demod)
           avg += np.abs(sample['x'][0] + 1j * sample['y'][0])/np.sqrt(2)
        results = avg/averaging_rate
        return results*1000

    def shutdown(self):
        self.lockin.auxout(1,0)
        self.lockin.outputamplitude(0,0)
        self.lockin.outputoffset(0,0)    
        self.lockin.outputon(0,0)
        
# ########################### Test ###########
# import matplotlib.pyplot as plt
# import matplotlib.animation as animation
# from matplotlib import style
# # style.use('fivethirtyeight')
# # fig = plt.figure()
# # ax1 = fig.add_subplot(1,1,1)
# loc = LockinField()

# loc.init()

# start = 0.5
# stop =  1
# no_points = 10

# vector_to = np.linspace(start, stop, no_points)

# for k in vector_to: 
#     loc.set_ac_field(k,4)
#     sleep(1)
#     loc.set_dc_field(1)
#     sleep(1)
#     loc.set_constant_vbias(2)
#     sleep(3) ### uzaleznic od czestotliwosci 
#     y = loc.lockin_measure_point(0,10)
#     x = k
#     plt.scatter(x, y, color = 'red', marker = 'x')
#     plt.title("Real Time plot")
#     plt.xlabel("x")
#     plt.pause(0.05)
    
# plt.show()



    