import sys
sys.path.append('.')
from hardware.hmc8043 import HMC8043
# from hardware.picoscope4626 import PicoScope
from hardware.sim928 import SIM928
from hardware.field_sensor_noise_new import FieldSensor 
from hardware.dummy_field_sensor_iv import DummyFieldSensor
from hardware.zurich import Zurich
from logic.fit_parameters_to_file import fit_parameters_to_file, fit_parameters_from_file
from logic.vbiascalibration import vbiascalibration, calculationbias, func, linear_func
from time import sleep
import numpy as np
class LockinField():
    def __init__(self, field_sensor=0, vbias=0):
        self.vbias = SIM928(vbias,timeout = 25000, baud_rate = 9600) 
        self.lockin = Zurich()
        #self.field = DAQ("6124/ao0")
        self.field_sensor = FieldSensor(field_sensor)

    def init(self):                     
      
  
        self.vbias.voltage_setpoint(0)
        self.vbias.disabled()
        sleep(0.3)
        self.lockin.oscillatorfreq(0,0) 
        self.lockin.oscillatorfreq(1,0)
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
        self.lockin.daq.sync() 

   
    def set_ac_field(self, value=0, freq=1): # TO DO
        self.lockin.oscillatorfreq(1,freq)
        self.lockin.outputamplitude(1,value)
        self.lockin.daq.sync()
    
    def set_dc_field(self, value=0):
        self.lockin.outputoffset(0,value)
        self.lockin.daq.sync()
      
    
    def set_constant_vbias(self, value=0):
        self.vbias.voltage_setpoint(value)
        self.vbias.enabled()

    
    def lockin_measure_point(self,demod, averaging_rate):
        results = []
        avg = 0
        for samp in range(averaging_rate):
           sample = self.lockin.getsample(demod)
           avg += np.abs(sample['x'][0] + 1j * sample['y'][0])/np.sqrt(2)
        results = avg/averaging_rate
        return results

    def shutdown(self):
        self.vbias.run_to_zero()
        self.lockin.outputamplitude(0,0)
        self.lockin.outputoffset(0,0)    
        self.lockin.outputon(0,0)
        


# loc = LockinField()
# loc.init()
# loc.set_ac_field(0.3,100)
# loc.set_dc_field(0.6)
# for i in range(0,10):
#     print(loc.lockin_measure_point(0,10))
#     sleep(1)