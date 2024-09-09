import sys

sys.path.append(".")
from hardware.hmc8043 import HMC8043
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


class LockinField:
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
        currin_float = False, 
        timeconstat = 1, 
        order = 1
    ):  
        
        if input_type == 0: #voltage 
            VOLTAGE_DEMOD = 0 
            CURRENT_DEMOD = 2
        else: 
            VOLTAGE_DEMOD = 2 
            CURRENT_DEMOD = 0
        #set ranges:
        
        if autorange == True:
            self.lockin.siginautorange(0, autorange)
        else:
            self.lockin.siginrange(0, siginrange_value)
        self.lockin.siginac(0, ac)
        
        if currins_autorange == True:
            self.lockin.currinautorange(2, currins_autorange)
        else:
            self.lockin.currinrange(2, currins_range)
        
        #set input type to demodulators
        self.lockin.setadc(0, 0)  # SIG V - pomiar na cewkach
        self.lockin.setadc(1, 174)  #SIG OUT - cewki
        self.lockin.setadc(2, 2) # SIG I - sample
        self.lockin.setadc(3,174)  #non-use
        
        #Set oscillators freq to 0
        self.lockin.oscillatorfreq(0, 0)
        self.lockin.oscillatorfreq(1, 0)
        self.lockin.oscillatorfreq(2, 0)
        self.lockin.oscillatorfreq(3, 0)
        
        #set sigin voltage\current parametes
        self.lockin.siginscaling(0, 1)
        self.lockin.currinscaling(2, 1)
        self.lockin.sigindiff(0, differential)
        self.lockin.siginimp50(2, imp50)
        
        #set oscillators to demodulators
        self.lockin.setosc(2, 1) # SIGI - oscylator 1
        self.lockin.setextrefs(2,1,1) #demodulatorze ustawiamy external refs 2
        self.lockin.setosc(1, 0) # OUTPUT - osculator 0 
        self.lockin.setosc(0, 0) # SIGV - oscylator 0   
        
        # set sigin parameters
        self.lockin.settimeconst(0, 0.3)
        self.lockin.settimeconst(2, 0.3)
        self.lockin.setorder(0, 2)
        self.lockin.setorder(2, 2)
        self.lockin.setharmonic(0, 1)
        self.lockin.setharmonic(2, 1)

        # włączanie demodulatorów - odczyt
        self.lockin.enabledemod(0, 1) # włączony SIGV
        self.lockin.enabledemod(1, 0) # wyłączony OUTPUT
        self.lockin.enabledemod(2, 1) # włączony SIGI 
        self.lockin.enabledemod(3, 0) #wyłączony nieużywany

        self.lockin.outputamplitude(1, 0) #ustaw aplitudę OUT na 0

        #ustawianie wyjść 
        self.lockin.enableoutput(0, 0) #off
        self.lockin.enableoutput(1, 1) #on
        self.lockin.enableoutput(2, 0) #off
        self.lockin.enableoutput(3, 0) #off
        self.lockin.outputoffset(0, 0) # offset na 0
        self.lockin.outputon(0, 1)     #włącz wyjście
        self.lockin.outputrange(0, 10) #range na 10 V
        
        #bias voltage - AUX
        self.lockin.aux_set_manual(1)
        self.lockin.auxout(1, 0)


        self.lockin.siginfloat(1 if sigin_float==True else 0) 
        self.lockin.currinfloat(1 if currin_float==True else 0)
        self.lockin.settimeconst(0,timeconstat)
        self.lockin.settimeconst(2,timeconstat)
        self.lockin.setorder(0,order)
        self.lockin.setorder(2,order)

    def set_ac_field(self, value, freq):  
        self.lockin.oscillatorfreq(0, freq)  # oscilator 0
        self.lockin.outputamplitude(1, value) #demodulator 1

    def set_dc_field(self, value=0.0):
        self.lockin.outputoffset(0, value)   #offset na wyjsciu 

    def set_constant_vbias(self, value=0):
        self.lockin.auxout(1, value / 1000)  #vbias na AUX2


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
        self.lockin.outputamplitude(1, 0)
        self.lockin.outputoffset(0, 0)
        self.lockin.outputon(0, 0)

    def set_field(self, value_dc=0, value_ac=0, freq=1, calib_dc=1, calib_ac=1):
        self.dc_value = (value_dc * 50) / calib_dc
        self.set_dc_field(self.dc_value)
        self.ac_value = (value_ac * 50) / calib_ac
        self.set_ac_field(self.ac_value, freq)


