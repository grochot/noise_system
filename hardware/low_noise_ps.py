from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set
from time import sleep

import time
import logging
import re 
import serial

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class LowNoisePS():
    def __init__(self, adapter, **kwargs):
        self.ser = serial.Serial(adapter[4:16],9600, timeout=1)

    def enabled(self):
        pass
   
    def disabled(self):
        pass

    def voltage_setpoint(self, vol = 0): 
        sleep(0.1)
        print("VOLT:{} mV".format(vol))
        self.ser.write("SETV {}".format(vol).encode())
        sleep(4)
    
    def read_voltage(self):
        self.ser.write(b'GETV\r')
        self.ser.read(36).decode()
        sleep(1) 
        self.ser.write(b'GETV\r')
        data = self.ser.read(100).decode()
        reg= 'MEASURED: \\d+ mV'
        x = re.findall(reg, data)
        splited = x[0].split()
        print(data)
        return splited[1]



    def run_to_zero(self): 
        self.voltage_setpoint(0)
        sleep(0.3)
        self.disabled()



    @property
    def error(self):
        """ Returns a tuple of an error code and message from a
        single error. """
        err = self.values(":system:error?")
        if len(err) < 2:
            err = self.read()  # Try reading again
        code = err[0]
        message = err[1].replace('"', "")
        return (code, message)

    def check_errors(self):
        """ Logs any system errors reported by the instrument.
        """
        code, message = self.error
        while code != 0:
            t = time.time()
            log.info("SIM928 reported error: %d, %s" % (code, message))
            code, message = self.error
            if (time.time() - t) > 10:
                log.warning("Timed out for SIM 928 error retrieval.")

    def shutdown(self):
        """ Disable output, call parent function"""
        self.enabled = False
        super().shutdown()

################## TEST ################## 

# k = LowNoisePS('ASRL/dev/ttyACM1::INSTR') 
# k.voltage_setpoint(24)
# sleep(1)
# print(k.read_voltage())

# print(k.read_voltage())