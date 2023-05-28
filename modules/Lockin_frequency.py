from hardware.hmc8043 import HMC8043
# from hardware.picoscope4626 import PicoScope
from hardware.sim928 import SIM928
from hardware.field_sensor_noise_new import FieldSensor 
from hardware.dummy_field_sensor_iv import DummyFieldSensor
from hardware.zurich import Zurich
from hardware.daq import DAQ
from logic.fit_parameters_to_file import fit_parameters_to_file, fit_parameters_from_file
from logic.vbiascalibration import vbiascalibration, calculationbias, func, linear_func
from time import sleep
import numpy as np
class LockinFrequency():
    def __init__(self, field_sensor, field, vbias):
        self.vbias = SIM928(vbias,timeout = 25000, baud_rate = 9600) #connect to voltagemeter
        self.lockin = Zurich()
        self.field = DAQ("6124/ao0")
        self.field_sensor = FieldSensor(field_sensor)

    def init(self):
        self.lockin.initalsett()
        self.lockin.daq.sync()
        self.vbias.voltage_setpoint(0)
        self.vbias.disabled()
        sleep(0.3)
        self.lockin.setadc(0,0)
        self.lockin.currinfloat(0,1)
        self.lockin.oscillatorfreq(0, 1)
        self.lockin.currinautorange(0, 1)
        self.lockin.settimeconst(0, 0.3)
        self.lockin.setorder(0, 2)
        self.lockin.setosc(0,0)
        self.lockin.setharmonic(0, 1)
        self.lockin.daq.sync()

   
    def set_constant_field(self, value=0):
        self.field.set_field(value)
        

    def set_constant_vbias(self, value=0):
        self.vbias.voltage_setpoint(value)
        self.vbias.enabled()

    def set_lockin_freq(self,freq):
        self.lockin.oscillatorfreq(0, freq)

    def lockin_measure_point(self,demod, averaging_rate):
        results = []
        avg = 0
        for samp in range(averaging_rate):
           sample = self.lockin.getsample(demod)
           avg += np.abs(sample['x'][0] + 1j * sample['y'][0])
        results = avg/averaging_rate
        return results

    def shutdown(self):
        self.vbias.run_to_zero()
        self.field.shutdown()  


        
