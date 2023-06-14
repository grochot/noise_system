from logic.measure_field import measure_field
from time import sleep
class LockinCalibration:
    def __init__(self, lockin, field, ac_frequency, dc_field):
        self.lockin = lockin
        self.field = field
        self.ac_frequency = ac_frequency
        self.dc_field = dc_field
     
    
    def calibrate(self):
        self.lockin.set_dc_field(self.dc_field/0.6)
        sleep(0.1)
        self.lockin.set_ac_field(1,self.ac_frequency)
        sleep(1)
        self.v_ac =self.lockin.lockin_measure_point(0,3)
        self.field_value = measure_field(2,self.field, False)
        self.hac = self.field_value[0] - self.dc_field
        self.calib_ac = self.hac/(self.v_ac)
        return self.calib_ac
        
        
        
        
    

