from logic.measure_field import measure_field
from time import sleep
class LockinCalibration:
    def __init__(self, lockin, field, averaging, dc_field, ac_field, ac_frequency, calib_const):
        self.lockin = lockin
        self.field = field
        self.averaging = averaging
        self.dc_field = dc_field
        self.ac_field = ac_field
        self.ac_frequency = ac_frequency
        self.calib_const = calib_const
    
    def calibrate(self):
        self.lockin.set_dc_field(self.dc_field)
        sleep(0.1)
        self.lockin.set_ac_field(self.ac_field,self.ac_frequency)
        sleep(1)
        self.v_ac =self.lockin.measure_point(0,3)
        self.field_value = measure_field(self.averaging, self.fied, False)
        self.hdc = ((self.dc_field/1000)/50)*self.calib_const
        self.hac = self.field_value[0] - self.hdc
        self.calib_ac = self.field_value/(self.v_ac/50)
        return self.calib_ac
        
        
        
        
    

