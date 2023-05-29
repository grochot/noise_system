from pymeasure.instruments import Instrument
import zhinst.utils

class Zurich(Instrument):

    def initalsett(self):
        self.API_LEVEL = 6
        self.DEVICE_ID = 'dev4274'
        self.ERR_MSG = 'ERR'
        (self.daq, self.device, _) = zhinst.utils.create_api_session(self.DEVICE_ID,
                                                           self.API_LEVEL, required_devtype='.*LI|.*IA',
                                                           required_err_msg=self.ERR_MSG)
        zhinst.utils.api_server_version_check(self.daq)
        # self.daq.setInt(f"/{self.device}/sigouts/0/on", 0)  # disable signal output
        # self.daq.setInt(f"/{self.device}/auxouts/0/outputselect", -1)  # AUX output 1 = manual
        # self.daq.setDouble(f"/{self.device}/auxouts/0/offset", 0.0)  # AUX output 1 offset = 0 V

    ##### SET INPUT SIGNAL #####

    def siginautorange(self, signal, auto=1):
        self.daq.setInt(f"/{self.device}/sigins/{signal}/autorange",auto)

    def siginrange(self, signal, range=1):
        self.daq.setDouble(f"/{self.device}/sigins/{signal}/autorange",range)

    def siginscaling(self, signal, scaling=1):
        self.daq.setDouble(f"/{self.device}/sigins/{signal}/autorange",scaling)

    def siginac(self, signal, ac=0):
        self.daq.setInt(f"/{self.device}/sigins/{signal}/ac", ac)

    def sigindiff(self, diff=0):
        self.daq.setInt(f"/{self.device}/sigins/0/diff", diff)

    def siginfloat(self, signal, float=0):
        self.daq.setInt(f"/{self.device}/sigins/{signal}/float", float)

    def siginimp50(self, signal, imp50=0):
        self.daq.setInt(f"/{self.device}/sigins/{signal}/ac", imp50)

    ##### SET INPUT CURRENT #####

    def currinautorange(self, signal, auto=1):
        self.daq.setInt(f"/{self.device}/currins/{signal}/autorange", auto)

    def currinrange(self, signal, range=1):
        self.daq.setDouble(f"/{self.device}/currins/{signal}/range", range)

    def currinscaling(self, signal, scaling=1):
        self.daq.setDouble(f"/{self.device}/currins/{signal}/scaling", scaling)

    def currinfloat(self, signal, float=0):
        self.daq.setInt(f"/{self.device}/currins/{signal}/float", float)

    ##### SET SIGNAL OUTPUT #####

    def outputon(self, output, on):
        self.daq.setDouble(f"/{self.device}/sigouts/{output}/on", on)

    def output50ohm(self, output, ohm):
        self.daq.setInt(f"/{self.device}/sigouts/{output}/imp50", ohm)

    def outputdiff(self,output, diff):
        self.daq.setInt(f"/{self.device}/sigouts/{output}/diff", diff)

    def outputadd(self, output, add):
        self.daq.setInt(f"/{self.device}/sigouts/{output}/add", add)

    def outputrange(self, output, range):
        self.daq.setDouble(f"/{self.device}/sigouts/{output}/range", range)

    def outputautorange(self, output, auto):
        self.daq.setInt(f"/{self.device}/sigouts/{output}/autorange", auto)

    def outputoffset(self, output, offset):
        self.daq.setDouble(f"/{self.device}/sigouts/{output}/offset", offset)
    
    def auxout(self, offset = 0): 
        self.daq.setDouble(f"/{self.device}/auxouts/0/offset",  offset)

#????????????????????????
    def enableoutput(self, demod, enable):
        self.daq.setInt(f"/{self.device}/sigouts/0/enables/{demod}", enable)

    def outputamplitude(self, output, ampli):
        self.daq.setDouble(f"/{self.device}/sigouts/0/amplitudes/{output}", ampli) # Vpp
#?????????????????????????


    ##### SET OSCILLATORS #####
    def oscillatorfreq(self, osc_id, freq):
        self.daq.setDouble(f"/{self.device}/oscs/{osc_id}/freq", freq)

    ##### SET DEMODULATORS #####
    def setosc(self, demod_id, osc_id):
        self.daq.setInt(f"/{self.device}/demods/{demod_id}/oscselect", osc_id)  # connect to oscilator

    def setextrefs(self, demod_id, extrefs):
        self.daq.setInt(f"/{self.device}/extrefs/{extrefs}/enable", demod_id)  # input select demod
        self.daq.setInt(f"/{self.device}/extrefs/{extrefs}/demodselect", demod_id)

    def setharmonic(self, demod_id, harm):
        self.daq.setDouble(f"/{self.device}/demods/{demod_id}/harmonic", harm)  # select harmonic

    def settimeconst(self, demod_id, timeconst):
        self.daq.setDouble(f"/{self.device}/demods/{demod_id}/timeconstant", timeconst)  # set timeconstant

    def setadc(self, demod_id, adc):
        if(adc == 10):
            adc = 174
        self.daq.setInt(f"/{self.device}/demods/{demod_id}/adcselect", adc)  # input select demod

    def setorder(self, demod_id, order):
        self.daq.setInt(f"/{self.device}/demods/{demod_id}/order", order)  # select the filter roll off between 6 and 48 dB/oct

    def enabledemod(self, demod_id, enable):
        self.daq.setInt(f"/{self.device}/demods/{demod_id}/enable", enable)  # enable demodulator

    def rate(self, demod_id, rate):
        self.daq.setInt(f"/{self.device}/demods/{demod_id}/rate", rate)  # sampling rate

    def sinc(self, demod_id, sinc):
        self.daq.setInt(f'/{self.device}/demods/{demod_id}/sinc', sinc) #filter on


    ##### SET GENERATOR #############
    def setoscfreq(self, freq, oscilator):
        self.daq.setDouble(f"/{self.device}/oscs/{oscilator}/freq", freq)

    ##### GET SAMPLE ########

    def getsample(self, demod):
        sample = self.daq.getSample(f"/{self.device}/demods/{demod}/sample")
        return sample
    





# import zhinst.utils
# from time import sleep 
# import numpy as np 
# import matplotlib.pyplot as plt 

# API_LEVEL = 6
# DEVICE_ID = 'dev4177'
# ERR_MSG = 'ERR'
# VOLTAGE_FIELD_CONSTANT = 590 # Oersted/Volt
# FIELD_DELAY = 1.5 # delay after each step of the field
# NAZWA_PLIKU = "results2.txt" #nazwa pliku 

# if __name__ == "__main__":
#     (daq, device, _) = zhinst.utils.create_api_session(DEVICE_ID,
#             API_LEVEL, required_devtype='.*LI|.*IA',
#             required_err_msg=ERR_MSG)
#     zhinst.utils.api_server_version_check(daq)
    
#     daq.setInt(f"/{device}/imps/0/enable", 0) # disable impednace analyser
#     daq.setInt(f"/{device}/sigouts/0/on", 0) # disable signal output 
#     daq.setInt(f"/{device}/auxouts/0/outputselect", -1) # AUX output 1 = manual
#     daq.setDouble(f"/{device}/auxouts/0/offset",  0.0) # AUX output 1 offset = 0 V

#     """
#     BELOW: 
#     setup for LOCKIN measurement
#     """
#     daq.setInt(f"/{device}/demods/0/adcselect", 0) # input select demod 1
#     daq.setInt(f"/{device}/demods/1/adcselect", 0) # input select demod 2
#     daq.setInt(f"/{device}/sigins/0/diff", 0) 
#     daq.setInt(f"/{device}/sigins/0/float", 1) 
#     daq.setInt(f"/{device}/sigins/0/ac", 1) 
#     daq.setDouble(f"/{device}/oscs/0/freq", 284) 
#     daq.setDouble(f"/{device}/sigouts/0/range", 10) 
#     daq.setDouble(f"/{device}/sigouts/0/amplitudes/0", 1.41421356) 
#     daq.setInt(f"/{device}/sigouts/0/on", 1) # signal select
#     daq.setInt(f"/{device}/sigins/0/autorange", 1) 
#     #daq.setDouble(f"/{device}//sigins/0/range", 0.000002)
#     daq.setDouble(f"/{device}/demods/0/timeconstant", 0.3)
#     daq.setDouble(f"/{device}/demods/1/timeconstant", 0.3)
#     daq.setInt(f"/{device}/demods/0/order", 2)
#     daq.setInt(f"/{device}/demods/0/oscselect", 0) 
#     daq.setInt(f"/{device}/demods/1/oscselect", 0) 
#     daq.setDouble(f"/{device}/demods/0/harmonic", 1) 
#     daq.setDouble(f"/{device}/demods/1/harmonic", 2) 
#     daq.setInt(f"/{device}/sigouts/0/enables/0", 1)
#     daq.setInt(f"/{device}/sigouts/0/enables/1", 0)
 
 
#     daq.sync()
#     """
#     VT input 
#     """
#     start_H = -3500
#     stop_H = 3500
#     step_H = 20
#     averaging_rate = 10

#     stimulus_H = np.concatenate([np.arange(start_H,stop_H,step_H), np.arange(stop_H,start_H,-step_H)], axis = 0)
#     results = [] 
#     results2 = [] 
#     stimulus_H_graph=[]
#     fig = plt.figure()
#     ax = fig.add_subplot(211)
#     ax2 = fig.add_subplot(212)
#     ax.set_xlabel('Field [Oe]')
#     ax.set_ylabel('Amplitude R [V]')
#     ax2.set_xlabel('Field [Oe]')
#     ax2.set_ylabel('Amplitude R [V]')

#     daq.setDouble(f"/{device}/auxouts/0/offset",  start_H/VOLTAGE_FIELD_CONSTANT)
#     sleep(3)
#     results_file = open(NAZWA_PLIKU, "w") 
#     results_file.write("Field [Oe]")
#     for step in stimulus_H:
#         daq.setDouble(f"/{device}/auxouts/0/offset",  step/VOLTAGE_FIELD_CONSTANT) # AUX output 1 offset = step V
#         daq.sync()
#         sleep(FIELD_DELAY)
#         avg = 0
#         avg2 = 0
#         for samp in range(averaging_rate):
#             sample = daq.getSample(f"/{device}/demods/0/sample") # first harmonic
#             sample2 = daq.getSample(f"/{device}/demods/1/sample") # second harmonic
#             avg += np.abs(sample['x'] + 1j*sample['y'])
#             avg2 += np.abs(sample2['x'] + 1j*sample2['y'])
#         results.append(avg/averaging_rate)
#         results2.append(avg2/averaging_rate)
#         stimulus_H_graph.append(step)
#         ax.plot(stimulus_H_graph, np.array(results), "-bo" )
#         ax2.plot(stimulus_H_graph, np.array(results2), "-go")
#         results_file.write(str(avg/averaging_rate))
#         plt.pause(0.6)

#     daq.setDouble(f"/{device}/auxouts/0/offset",  0.0) # AUX output 1 offset = 0 V - reset
#     daq.setInt(f"/{device}/sigouts/0/on", 0)
#     results_file.close()
#     plt.show()
# 
# #########################################################################    

# zurich = Zurich()
#
# zurich.initalsett()
# zurich.daq.sync()
#
# results = []
# results1 = []
# avg = 0
# avg1 = 0
# x = []
# fig = plt.figure()
# ax = fig.add_subplot(211)
# ax2 = fig.add_subplot(212)
# ax.set_xlabel('Field [Oe]')
# ax.set_ylabel('Amplitude R [V]')
# ax2.set_xlabel('Field [Oe]')
# ax2.set_ylabel('Amplitude R [V]')
# for i in range(1,200):
#     sample = zurich.getsample(0)
#     sample1 = zurich.getsample(1)
#     avg = np.abs(sample['x'][0] + 1j * sample['y'][0])
#     avg1 = np.abs(sample1['x'][0] + 1j * sample1['y'][0])
#     results.append(avg)
#     results1.append(avg1)
#     x.append(i)
#     time.sleep(0.01)
#     ax.plot(x, results, "-bo")
#     ax2.plot(x, results1, "-go")
#     plt.pause(0.01)
#
#
# plt.show()