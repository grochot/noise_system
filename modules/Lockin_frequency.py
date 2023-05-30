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
class LockinFrequency():
    def __init__(self, field_sensor=0, vbias=0):
        self.lockin = Zurich()
        self.field_sensor = FieldSensor(field_sensor)

    def init(self):
        self.lockin.setadc(0,0) # 0 - voltage, 1 - current
        self.lockin.siginfloat(0,1)
        self.lockin.oscillatorfreq(0,0)
        self.lockin.settimeconst(0, 0.3)
        self.lockin.setorder(0, 2)
        self.lockin.setharmonic(0, 1)
        self.lockin.outputon(0,0)
        self.lockin.siginrange(0,10)
        self.lockin.aux_set_manual(0)
        self.lockin.aux_set_manual(1)
        self.lockin.enabledemod(0,1)
        self.lockin.auxout(0,0)
        self.lockin.auxout(1,0)
        self.lockin.daq.sync() 

   
    def set_constant_field(self, value=0):
        self.lockin.auxout(0,value)
        

    def set_constant_vbias(self, value=0):
        self.lockin.auxout(1,value)
        

    def set_lockin_freq(self,freq):
        self.lockin.oscillatorfreq(0, freq)

    def lockin_measure_point(self,demod, averaging_rate):
        results = []
        avg = 0
        for samp in range(averaging_rate):
           sample = self.lockin.getsample(demod)
           avg += np.abs(sample['x'][0] + 1j * sample['y'][0])/np.sqrt(2)
        results = avg/averaging_rate
        return results

    def shutdown(self):
        self.lockin.auxout(1,0)
        self.lockin.auxout(0,0)


# loc = LockinFrequency()
# loc.init()
# loc.set_constant_field(5)
# loc.set_constant_vbias(1)
# loc.set_lockin_freq(1000)
