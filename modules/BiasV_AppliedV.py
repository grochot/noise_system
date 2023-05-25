# from hardware.hmc8043 import HMC8043
# from hardware.picoscope4626 import PicoScope
# from hardware.sim928 import SIM928
# from hardware.field_sensor_noise_new import FieldSensor 
# from hardware.dummy_field_sensor_iv import DummyFieldSensor
# from logic.fit_parameters_to_file import fit_parameters_to_file, fit_parameters_from_file
# from logic.vbiascalibration import vbiascalibration, calculationbias, func, linear_func
# class MeanNoise():

#     def __init__(self, voltage_adress, current_adress, field_adress, oscilloscope_adress):
#         self.voltage_adress = voltage_adress
#         self.current_adress = current_adress
#         self.field_adress = field_adress
#         self.oscilloscope_adress = oscilloscope_adress 

#     def init(self): 
#           self.oscilloscope = PicoScope()
#           self.voltage = SIM928(self.voltage_adress,timeout = 25000, baud_rate = 9600) #connect to voltagemeter
          
#           self.no_samples = int(self.period_time/(((1/self.sampling_interval))))
#           if self.no_samples % 2 == 1:
#              self.no_samples = self.no_samples + 1
#         ##Field Sensor:
            
#           if self.field_sensor_adress == "none":
#                 print(self.field.sensor_adress)
#                 self.field = DummyFieldSensor()
              
            
#           else:
#                 self.field = FieldSensor(self.field_sensor_adress)
#                 self.field.read_field_init()
   
#      ##Bias voltage:
            
#           try:
#                 fit_parameters = fit_parameters_from_file()
#                 a = fit_parameters[0]
#                 b = fit_parameters[1]
#                 print(a,b)
#                 set_vol = calculationbias(self.bias_voltage, a,b,0, "linear")
#                 print(set_vol)
#                 self.voltage.voltage_setpoint(set_vol) #set bias voltage  
#                 sleep(0.5)
#                 self.voltage.enabled() #enable channel 
#                 sleep(2)
                    
#           except Exception:
#                 traceback.print_exc()
                
                 

            
#     ##Picoscope:
            
        
#           self.oscilloscope.setChannelA(self.channelA_coupling_type, self.channelA_range )
#             #self.oscilloscope.setChannelB(self.channelB_coupling_type, self.channelB_range )
#           self.oscilloscope.setTrigger()
            
        
        

            
#           sleep(0.5)
   
   
   
   
   
   
#     def run(self):
#         pass 

#     def shutdown(self):
#         pass