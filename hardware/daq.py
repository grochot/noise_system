from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set
from time import sleep
import nidaqmx
import numpy as np  

import time
import logging

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())




class DAQ():
    def __init__(self, adapter):
        self.adapter = adapter
        
   
    def set_field (self, value =1):
        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan(self.adapter)
            task.write(value)
        return value

    def set_ac_field(self, amp, f, fs):
        amp = 4         # 1V        (Amplitude)
        f = 40000       # 40kHz      (Frequency)
        fs = 2000000     # 200kHz    (Sample Rate)
        T = 1/f
        Ts = 1/fs

        x = np.arange(fs)
        y = [ amp*np.sin(2*np.pi*f * (i/fs)) for i in x]
        y_new = np.tile(y,1)

        x1 = x[:100]/2000000
        y1 = y[:100]

        test_Task = nidaqmx.Task()
        test_Task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
        test_Task.timing.cfg_samp_clk_timing(rate= 2000000, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)

        test_Writer = nidaqmx.stream_writers.AnalogSingleChannelWriter(test_Task.out_stream, auto_start=True)

        samples = y_new

        test_Writer.write_many_sample(samples)
        test_Task.wait_until_done()
        test_Task.stop()
        test_Task.close()
    

    def shutdown(self):
        """ Disable output, call parent function"""
        self.set_field(0)




