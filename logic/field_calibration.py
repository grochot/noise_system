
from hardware.daq import DAQ

class FieldCalibration(): 
    def __init__(self):
        self.daq = DAQ("/TestDevice/ao0")

    def field_cal(self, value):
        self.calibration_constant = 2 
        self.daq.set_voltage(value/self.calibration_constant)


        
