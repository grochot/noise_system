import sys

sys.path.append(".")
from hardware.hmc8043 import HMC8043

# from hardware.picoscope4626 import PicoScope
from hardware.field_sensor_noise_new import FieldSensor
from hardware.dummy_field_sensor_iv import DummyFieldSensor
from hardware.zurich import Zurich
from logic.fit_parameters_to_file import (
    fit_parameters_to_file,
    fit_parameters_from_file,
)
from logic.vbiascalibration import vbiascalibration, calculationbias, func, linear_func
from time import sleep
import numpy as np


class LockinFrequency:
    def __init__(self, server=""):
        self.lockin = Zurich(server)

    def init(
        self,
        input_type=0,
        differential=False,
        siginrange_value=1.0,
        imp50=False,
        ac=False,
        autorange=False,
        currins_range=1.0,
        currins_autorange=False,
        sigin_float = False, 
        currin_float= False, 
        timeconstat = 1, 
        order = 1
    ):



        if autorange == True:
            self.lockin.siginautorange(0, autorange)
        else:
            self.lockin.siginrange(0, siginrange_value)
        
        self.lockin.siginac(0, ac)
        
        if currins_autorange == True:
            self.lockin.currinautorange(2, currins_autorange)
        else:
            self.lockin.currinrange(2, currins_range)
        
        #Set oscillators freq to 0
        self.lockin.oscillatorfreq(0, 0)
        self.lockin.oscillatorfreq(1, 0)
        self.lockin.oscillatorfreq(2, 0)
        self.lockin.oscillatorfreq(3, 0)

        #set sigin voltage\current parametes
        self.lockin.siginscaling(0, 1)
       
        self.lockin.currinscaling(1, 1)
      
        self.lockin.sigindiff(0, differential)
        self.lockin.siginimp50(0, imp50)

        #set input type to demodulators
        self.lockin.setadc(1, 1)  #0 demodulators to voltage/current
        self.lockin.setadc(0, 0)  #1 demodulators to current/voltage 
        self.lockin.setadc(2,174)  #2 demodulators to constant
        self.lockin.setadc(3,174)  #2 demodulators to constant
        self.lockin.extrefsoff()
        
        #set oscillators to demodulators
        # self.lockin.setextrefs(0,0,0)
        self.lockin.setosc(2, 0) 
        self.lockin.setosc(3, 0)
        self.lockin.setosc(0, 0) 
        self.lockin.setosc(1, 0)
        

        # set sigin parameters
        self.lockin.settimeconst(0, 0.3)
        self.lockin.settimeconst(1, 0.3)
        self.lockin.setorder(0, 2)
        self.lockin.setorder(1, 2)
        self.lockin.setharmonic(0, 1)
        self.lockin.setharmonic(1, 1)
        self.lockin.enabledemod(0, 1)
        self.lockin.enabledemod(1, 1)
        self.lockin.enabledemod(2, 0)
        self.lockin.enabledemod(3, 0)

        #set output
        self.lockin.enableoutput(0, 0)
        self.lockin.enableoutput(1, 0)
        self.lockin.enableoutput(2, 0)
        self.lockin.enableoutput(3, 0)
        self.lockin.outputon(0, 0)
      

        #set AUX
        self.lockin.aux_set_manual(0)

        self.lockin.auxout(0, 0)
       

        self.lockin.siginfloat(1 if sigin_float==True else 0) 
        self.lockin.currinfloat(1 if currin_float==True else 0)
        self.lockin.settimeconst(0,timeconstat)
        self.lockin.settimeconst(1,timeconstat)
        self.lockin.setorder(0,order)
        self.lockin.setorder(1,order)


        #set Vbias output: 
        self.lockin.setosc(2, 3)
        self.lockin.oscillatorfreq(3, 0)
        self.lockin.enableoutput(2, 1)
        self.lockin.outputamplitude(2,0)
        self.lockin.outputoffset(0, 0)
        self.lockin.outputon(0, 1)


    def set_constant_field(self, value=0):
        self.lockin.auxout(0, value)

    def set_constant_vbias(self, value=0):
        self.lockin.outputoffset(2, value)

        # self.lockin.auxout(1, value / 1000)

    def set_lockin_freq(self, freq):
        self.lockin.oscillatorfreq(0, freq)

    def lockin_measure_R(self, demod, averaging_rate):
        results = []
        avg = 0
        for samp in range(averaging_rate):
            sample = self.lockin.getsample(demod)
            avg += np.sqrt(sample["x"][0] ** 2 + sample["y"][0] ** 2)
        results = avg / averaging_rate
        return results

    def lockin_measure_phase(self, demod, averaging_rate):
        results = []
        avg = 0
        for samp in range(averaging_rate):
            sample = self.lockin.getsample(demod)
            avg += np.arctan(sample["y"][0] / sample["x"][0])
        results = avg / averaging_rate
        return results

    def shutdown(self):
        self.lockin.auxout(1, 0)
        self.lockin.auxout(0, 0)
        self.lockin.outputon(0, 0)

if __name__ == "__main__":
    import matplotlib.pyplot as plt 
    lockin = LockinFrequency('192.168.66.202')
    lockin.init_lockin()
    sample = lockin.getsample()
    plt.plot(sample[0], sample[1], sample[0],  sample[2])
    plt.show()
    # print(sample)
    