from pymeasure.instruments import Instrument
import zhinst.core
from time import sleep

class Zurich(Instrument):

    def __init__(self):
        
        self.daq = zhinst.core.ziDAQServer('192.168.66.202', 8004, 6)
        # self.API_LEVEL = 6
        self.device = 'dev4274'
        # self.ERR_MSG = 'ERR'
        # (self.daq, self.device, _) = zhinst.utils.create_api_session(self.DEVICE_ID,
        #                                                    self.API_LEVEL, required_devtype='.*LI|.*IA',
        #                                                    required_err_msg=self.ERR_MSG)
        # zhinst.utils.api_server_version_check(self.daq)
        # self.daq.setInt(f"/{self.device}/sigouts/0/on", 0)  # disable signal output
        # self.daq.setInt(f"/{self.device}/auxouts/0/outputselect", -1)  # AUX output 1 = manual
        # self.daq.setDouble(f"/{self.device}/auxouts/0/offset", 0.0)  # AUX output 1 offset = 0 V

    ##### SET INPUT SIGNAL #####

    def siginautorange(self, signal, auto=1):
        self.daq.setInt(f"/{self.device}/sigins/{signal}/autorange",auto)

    def siginrange(self, signal, range=1):
        self.daq.setDouble(f"/{self.device}/sigins/{signal}/range",range)

    def siginscaling(self, signal, scaling=1):
        self.daq.setDouble(f"/{self.device}/sigins/{signal}/scaling",scaling)

    def siginac(self, signal, ac=0):
        self.daq.setInt(f"/{self.device}/sigins/{signal}/ac", ac)

    def sigindiff(self, diff=0):
        self.daq.setInt(f"/{self.device}/sigins/0/diff", diff)

    def siginfloat(self, signal, float=1):
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
    
    def aux_set_manual(self, out):
        self.daq.setInt(f'/dev4274/auxouts/{out}/outputselect', -1)
    
    def auxout(self, out, offset = 0): 
        self.daq.setDouble(f"/{self.device}/auxouts/{out}/offset",  offset)

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
        self.daq.setInt(f'/{self.device}/demods/{demod_id}/sinc', sinc) #sinc filter on



    ##### GET SAMPLE ########

    def getsample(self, demod):
        sample = self.daq.getSample(f"/{self.device}/demods/{demod}/sample")
        return sample
    

