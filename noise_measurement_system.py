from ast import Num
from email.policy import default
import logging
import pandas as pd 
import json

import math
import sys
import random
from time import sleep, time
import traceback
from logic.find_instrument import FindInstrument
from logic.save_results_path import SaveFilePath

import numpy as np

from pymeasure.display.Qt import QtGui
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import (
    Procedure, FloatParameter, BooleanParameter, IntegerParameter, Parameter,ListParameter, Results
)
from logic.unique_name import unique_name
from hardware.keysight_e3600a import E3600a
from hardware.keysight_e3600a_dummy import E3600aDummy
from hardware.picoscope4626 import PicoScope
from hardware.hmc8043 import HMC8043 
from hardware.hmc8043_dummy import HMC8043Dummy 

from hardware.low_noise_ps_dummy import LowNoisePSDummy

from hardware.field_sensor_noise_new import FieldSensor 
from hardware.dummy_field_sensor_iv import DummyFieldSensor
from logic.generate_headers import GenerateHeader
from logic.fft_mean import FFT_mean
from logic.vbiascalibration import vbiascalibration, calculationbias, func, linear_func
from logic.fit_parameters_to_file import fit_parameters_to_file, fit_parameters_from_file
from logic.save_parameters import SaveParameters

log = logging.getLogger(__name__) 
log.addHandler(logging.NullHandler()) 



class NoiseProcedure(Procedure):
    parameters = {}
    save_parameter = SaveParameters()
    parameters_from_file = save_parameter.ReadFile()
    used_parameters_list= ['mode','sample_name','voltage_device', 'voltage_adress','field_device','field_adress', 'field_sensor_adress', 'period_time', 'no_time', 'sampling_interval','bias_voltage', 'bias_field_current', 'bias_field_voltage', 'channelA_range', 'channelA_coupling_type', 'treshold', 'divide', 'start', 'stop', 'no_points', 'reverse_voltage', 'delay']
    
    licznik = 0
    find_instruments = FindInstrument()
    finded_instruments = find_instruments.show_instrument()
    # finded_instruments = finded_instrument.append('none')
    print(finded_instruments)
    
################# PARAMETERS###################
#Noise mode:
    period_time = FloatParameter('Period of Time', units='s', default = parameters_from_file["period_time"], group_by='mode', group_condition=lambda v: v =='Mean' or v=='One Shot' or v == 'Mean + Raw')
    mode = ListParameter("Mode", default = parameters_from_file["mode"], choices=['Mean', 'One Shot', 'Mean + Raw', 'Vbias calibration', "Vbias"])
    no_time = IntegerParameter('Number of times', default = parameters_from_file["no_time"], group_by='mode', group_condition=lambda v: v =='Mean' or v=='Mean + Raw')
    sampling_interval =FloatParameter('Sampling frequency', units='Hz', default = parameters_from_file["sampling_interval"], group_by='mode', group_condition=lambda v: v =='Mean' or v=='Mean + Raw' or v=='One Shot')
    bias_voltage = FloatParameter('Bias Voltage', units='mV', default = parameters_from_file["bias_voltage"],group_by='mode', group_condition=lambda v: v =='Mean' or v=='One Shot' or v == 'Mean + Raw')
    bias_field_current = FloatParameter('Bias Field Current', units='mA', default = parameters_from_file["bias_field_current"],group_by={"mode": lambda v: v =='Mean' or v=='Mean + Raw'})
    bias_field_voltage = FloatParameter('Bias Field Voltage', units='mV', default = parameters_from_file["bias_field_voltage"],group_by={"mode": lambda v: v =='Mean' or v=='Mean + Raw', "field_device": lambda v: v=="HMC8043"})
    voltage_device = ListParameter('Voltage Device', choices=['SIM928', 'LowNoise', 'none'],default = parameters_from_file["voltage_device"],group_by='mode', group_condition=lambda v: v =='Mean' or v=='One Shot' or v == 'Mean + Raw' or v == 'Vbias calibration' or v == 'Vbias')
    voltage_adress = ListParameter("Voltage supply address", choices=finded_instruments, group_by='mode', default = parameters_from_file["voltage_adress"] if parameters_from_file["voltage_adress"] in finded_instruments else 'None', group_condition=lambda v: v =='Mean' or v=='One Shot' or v == 'Mean + Raw' or v == 'Vbias calibration' or v == 'Vbias')
    field_device = ListParameter("Field supply device",  choices=['HMC8043', 'E3600A', 'none'],default = parameters_from_file["field_device"],group_by='mode', group_condition=lambda v: v =='Mean' or v=='Mean + Raw')
    field_adress = ListParameter("Field supply address",  choices=finded_instruments,group_by='mode', default = parameters_from_file["field_adress"] if parameters_from_file["field_adress"] in finded_instruments else 'None', group_condition=lambda v: v =='Mean' or v=='Mean + Raw')
    field_sensor_adress = ListParameter("Field_sensor",  choices=finded_instruments,group_by='mode', default = parameters_from_file["field_sensor_adress"] if parameters_from_file["field_sensor_adress"] in finded_instruments else 'None', group_condition=lambda v: v =='Mean' or v=='Mean + Raw')
    channelA_coupling_type = ListParameter("Channel A Coupling Type",  default = parameters_from_file["channelA_coupling_type"], choices=['DC','AC'],group_by='mode',group_condition=lambda v: v =='Mean' or v=='Mean + Raw' or v =='Vbias calibration' or v == 'Vbias' )
    channelA_range = ListParameter("Channel A Range",  default = parameters_from_file["channelA_range"], choices=["10mV", "20mV", "50mV", "100mV", "200mV", "500mV", "1V", "2V", "5V", "10V", "20V", "50V", "100V"],group_condition=lambda v: v =='Mean' or v=='Mean + Raw' or v == 'V bias calibration' or v == 'Vbias')
    sample_name = Parameter("Sample Name", default = parameters_from_file["sample_name"],group_by='mode', group_condition=lambda v: v =='Mean' or v=='Mean + Raw')
    treshold = FloatParameter("Treshold", units='mV',group_by='mode', default = parameters_from_file["treshold"], group_condition=lambda v: v =='Mean' or v=='Mean + Raw')
    divide = FloatParameter("Divide number", units = 'mV',group_by='mode', default = parameters_from_file["divide"], group_condition=lambda v: v =='Mean' or v=='Mean + Raw')
    
#Bias mode:
    start = FloatParameter("Start",units='mV', group_by='mode', default = parameters_from_file["start"], group_condition=lambda v: v =='Vbias calibration' or v == 'Vbias')
    stop = FloatParameter("Stop", units='mV', group_by='mode',default = parameters_from_file["stop"], group_condition=lambda v: v =='Vbias calibration' or v == 'Vbias')
    no_points = IntegerParameter("No Points", group_by='mode', default = parameters_from_file["no_points"], group_condition=lambda v: v =='Vbias calibration' or v == 'Vbias')
    reverse_voltage = BooleanParameter("Reverse voltage", default = parameters_from_file["reverse_voltage"], group_by='mode', group_condition=lambda v: v =='Vbias calibration' or v == 'Vbias')
    delay = FloatParameter("Delay", units = "ms", default = parameters_from_file["delay"], group_by='mode', group_condition=lambda v: v =='Vbias calibration' or v == 'Vbias')
   


   
    DATA_COLUMNS = ['time (s)','Bias voltage (mV)', 'Sense Voltage (mV)', 'X field (Oe)', 'Y field (Oe)', 'Z field (Oe)', 'Field (Oe)','frequency (Hz)', 'FFT (mV)', 'log[frequency] (Hz)' ,'log[FFT] (mV)' , 'treshold_time (s)', 'treshold_voltage (mV)', 'divide_voltage (mV)'] #data columns
    path_file = SaveFilePath() 
    
    def prepare_columns(self,columns):
        columns_f = []
        columns_f.append(columns[0])
        for k in range(1,len(columns)):
            columns_f.append(","+ columns[k])
        return columns_f
######################################## INIT ########################################
    def startup(self):
#Mean mode:
        for par in self.used_parameters_list:
            self.param = eval("self."+par)
            self.parameters[par] = self.param
        self.save_parameter.WriteFile(self.parameters)
        
        if self.mode == 'Mean' or self.mode == 'Mean + Raw':
            if self.mode == 'Mean + Raw':
                self.header = GenerateHeader()
                self.header_columns = self.prepare_columns(self.DATA_COLUMNS)
            self.oscilloscope = PicoScope()
            
            if self.voltage_device == 'none':
                from hardware.sim928_dummy import SIM928 
                self.voltage = SIM928()
                log.warning("Use SIM928 Dummy")
            elif self.voltage_device == 'SIM928':
               
                from hardware.sim928 import SIM928 
                self.voltage = SIM928(self.voltage_adress,timeout = 25000, baud_rate = 9600) #connect to voltagemeter
            else: 
                from hardware.low_noise_ps import LowNoisePS 
                self.voltage = LowNoisePS(self.voltage_adress,timeout = 25000, baud_rate = 115200) #connect to voltagemeter
            sleep(1)
       
        
        
            self.no_samples = int(self.period_time/(((1/self.sampling_interval))))
            if self.no_samples % 2 == 1:
                self.no_samples = self.no_samples + 1
          

    ##Field Sensor:
            
            if self.field_sensor_adress == 'none':
                self.field = DummyFieldSensor()
                log.warning("Use FieldSensor Dummy")
            
            else:
                self.field = FieldSensor(self.field_sensor_adress)
                self.field.read_field_init()
               

    ##Bias field:
            if self.field_device == 'none':
                self.field_coil = E3600aDummy()
                log.warning("Use E3600 Dummy")
            elif self.field_device == "E3600A":
                self.field_coil = E3600a(self.field_adress) #connction to field controller
                self.field_coil.remote()
                
                if float(self.bias_field) < 0:
                    self.field_coil.outputselect(1)
                    sleep(0.3)
                    self.field_coil.disable_now()
                    sleep(0.3)
                    self.field_coil.outputselect(2)
                    sleep(0.3)
                    self.field_coil.current(abs(float(self.bias_field_current)/1000)) #set field 
                    sleep(0.3)
                    self.field_coil.enabled()
                else: 
                    self.field_coil.outputselect(2)
                    sleep(0.3)
                    self.field_coil.disable_now()
                    sleep(0.2)
                    self.field_coil.outputselect(1)
                    sleep(0.3)
                    self.field_coil.current(float(self.bias_field_current)/1000) #set field 
                    sleep(0.3)
                    self.field_coil.enabled()
                sleep(1)
                log.info("Set bias field to {} mA".format(float(self.bias_field_current)/1000))
            else: 
                flag1 = True
                while flag1 == True:
                    try:    
                        self.field_coil = HMC8043(self.field_adress) #connction to field controller
                        sleep(0.2)
                        self.field_coil.inst_out(1)
                        self.field_coil.set_voltage(10)
                        self.field_coil.set_current(self.bias_field_current/1000)
                        self.field_coil.enable_channel()
                        sleep(5)
                        flag1 = False
                    except Exception as a: 
                        log.error(a)
                        sleep(15)
                        flag1 = True
                    

        
    ##Bias voltage:
            try:
                fit_parameters = fit_parameters_from_file()
                a = fit_parameters[0]
                b = fit_parameters[1]
                print(a,b)
                set_vol = calculationbias(self.bias_voltage, a,b,0, "linear")
                print(set_vol)
                self.voltage.voltage_setpoint(set_vol) #set bias voltage  
                log.info("read parameters from file succesfull")
                sleep(0.5)
                self.voltage.enabled() #enable channel 
                sleep(2)
                    
            except Exception:
                traceback.print_exc()
                log.error("Could not connect to bias voltage source")
                
                 

            
    ##Picoscope:
            
        
            self.oscilloscope.setChannelA(self.channelA_coupling_type, self.channelA_range )
            #self.oscilloscope.setChannelB(self.channelB_coupling_type, self.channelB_range )
            self.oscilloscope.setTrigger()
            log.info("Setup instrument done")
        
        
            #log.error("Could not connect to oscilloscope")
            
            sleep(0.5)
#One shot mode:
        elif self.mode == 'One Shot':
            self.oscilloscope = PicoScope( )
            if self.voltage_device == 'none':
                from hardware.sim928_dummy import SIM928 
                self.voltage = SIM928()
                log.warning("Use SIM928 Dummy")
            elif self.voltage_device == 'SIM928':
               
                from hardware.sim928 import SIM928 
                self.voltage = SIM928(self.voltage_adress,timeout = 25000, baud_rate = 9600) #connect to voltagemeter
            else: 
                from hardware.low_noise_ps import LowNoisePS 
                self.voltage = LowNoisePS(self.voltage_adress,timeout = 25000, baud_rate = 9600) #connect to voltagemeter
            self.no_samples = int(self.period_time/(((1/self.sampling_interval))))
            if self.no_samples % 2 == 1:
                self.no_samples = self.no_samples + 1
            self.oscilloscope.setChannelA('AC', self.channelA_range )
            self.oscilloscope.setTrigger()
            try:   
                self.voltage.voltage_setpoint(self.bias_voltage) #set bias voltage
                sleep(0.1)
                self.voltage.enabled() #enable channel 
                
            except Exception:
                traceback.print_exc()
                log.error("Could not connect to bias voltage source")
#Bias mode:
        else: 
            self.oscilloscope = PicoScope()
            if self.voltage_device == 'none':
                from hardware.sim928_dummy import SIM928 
                self.voltage = SIM928()
                log.warning("Use SIM928 Dummy")
            elif self.voltage_device == 'SIM928':
               
                from hardware.sim928 import SIM928 
                self.voltage = SIM928(self.voltage_adress,timeout = 25000, baud_rate = 9600) #connect to voltagemeter
            else: 
                from hardware.low_noise_ps import LowNoisePS 
                self.voltage = LowNoisePS(self.voltage_adress,timeout = 25000, baud_rate = 9600) #connect to voltagemeter
            sleep(0.1)
            self.oscilloscope.setChannelA(self.channelA_coupling_type, self.channelA_range )
            self.oscilloscope.setTrigger()
            self.oscilloscope.set_number_samples(1000)
            self.oscilloscope.set_timebase(int((1/10000)*10000000)-1)
            log.info("Setup instrument done")
            try:
                if self.voltage == True: 
                    self.vector_to = np.linspace(self.start, self.stop,self.no_points)
                    self.vector_rev = self.vector_to[::-1]
                    self.vector = np.append(self.vector_to[0:-1], self.vector_rev)
                else: 
                    self.vector = np.linspace(self.start, self.stop,self.no_points)
            except:
                log.error("Vector set failed")

           





######################################## Procedure ########################################
    def execute(self):
#Mean mode:
        if self.mode == 'Mean' or self.mode == 'Mean + Raw':
            log.info("Start measurement")
          
            self.oscilloscope.set_number_samples(self.no_samples)
            self.oscilloscope.set_timebase(int((1/self.sampling_interval)*10000000)-1)
            self.steps = self.no_time 
            self.time = self.period_time
            self.stop_time = time()
            tmp_data_time = pd.DataFrame(columns=['time'])
            tmp_data_voltage = pd.DataFrame(columns=['voltage'])
            tmp_frequency = pd.DataFrame(columns=['frequency'])
            tmp_fft = pd.DataFrame(columns=['fft'])
            tmp_data_magnetic_field_x = []
            tmp_data_magnetic_field_y = []
            tmp_data_magnetic_field_z = []
            fft_tmp_rms_noise = []


    #Measure field: 
            for i in range(1):
                try:
                    tmp_field = self.field.read_field()
                    tmp_x = tmp_field[0]
                    tmp_y = tmp_field[1]
                    tmp_z = tmp_field[2]
                    
                
                    tmp_data_magnetic_field_x.append(float(tmp_x))
                    tmp_data_magnetic_field_y.append(float(tmp_y))
                    tmp_data_magnetic_field_z.append(float(tmp_z))
                    sleep(0.1)

        
                    tmp_data_magnetic_field_x_mean = float(sum(tmp_data_magnetic_field_x)/len(tmp_data_magnetic_field_x))/100
                    tmp_data_magnetic_field_y_mean = float(sum(tmp_data_magnetic_field_y)/len(tmp_data_magnetic_field_y))/100
                    tmp_data_magnetic_field_z_mean = float(sum(tmp_data_magnetic_field_z)/len(tmp_data_magnetic_field_z))/100

                    tmp_total_field = np.sqrt(tmp_data_magnetic_field_x_mean**2 +  tmp_data_magnetic_field_y_mean**2 + tmp_data_magnetic_field_z_mean**2)
               
                except Exception as e:
                    print(e)
                    log.error("Field sensor adress wrong!")
                    self.should_stop()
       

    #MAIN LOOP 
            for i in range(self.steps):
                if self.mode == 'Mean + Raw':
                    self.sample_name_raw = unique_name(self.path_file.ReadFile()+ "/", prefix="{}".format(str(self.sample_name) + "_raw{}".format(i)))
                    self.header.set_parameters(self.sample_name_raw, self.header_columns, self.bias_field, self.bias_voltage, self.channelA_coupling_type, self.channelA_range, self.divide, self.field_adress, self.field_sensor_adress, self.no_time, self.period_time, self.sample_name, self.sampling_interval, self.treshold, self.voltage_adress, self.delay, self.no_points, self.reverse_voltage, self.start, self.stop)
                self.oscilloscope.run_block_capture()
                self.oscilloscope.check_data_collection()
                self.oscilloscope.create_buffers()
                self.oscilloscope.set_buffer_location()
                self.oscilloscope.getValuesfromScope()
                tmp_time_list = self.oscilloscope.create_time()
                tmp_voltage_list = self.oscilloscope.convert_to_mV(self.channelA_range)

                
            
    #FFT Counting:
                smpl_freq = self.sampling_interval
                ft_tmp = np.fft.fft(tmp_voltage_list) / len(tmp_voltage_list)  # Normalize amplitude and apply the FFT
                ft_tmp = ft_tmp[range(int(len(tmp_voltage_list)/2))]   # Exclude sampling frequency ---> FFT value
                tp_cnt_tmp = len(tmp_voltage_list)
                val_tmp = np.arange(int(tp_cnt_tmp / 2))
                tm_period_tmp = tp_cnt_tmp / smpl_freq
                freq_tmp = val_tmp / tm_period_tmp        # Frequency value 
               

                tmp_data_time.insert(i,"time_{}".format(i),pd.Series(tmp_time_list))
                tmp_data_voltage.insert(i,"voltage_{}".format(i),pd.Series(tmp_voltage_list))
                tmp_frequency.insert(i,"frequency_{}".format(i),pd.Series(freq_tmp.real))
                tmp_fft.insert(i,"fft_{}".format(i),pd.Series(ft_tmp.real))

                fft_tmp_rms_noise.append(FFT_mean(ft_tmp)) #list of RMS noise FFTs

                
               
    #Mean + Raw      
                if  self.mode == 'Mean + Raw':

                    
                    # tmp_data_time_list= tmp_data_time["time_{}".format(i)].to_list()
                    # tmp_data_voltage_list = tmp_data_voltage["voltage_{}".format(i)].to_list()
                    # tmp_frequency_list = tmp_frequency["frequency_{}".format(i)].to_list()
                    # tmp_fft_list = tmp_fft["fft_{}".format(i)].to_list()
                    
                    for tmp_ele in range(len(tmp_time_list)):
                        self.data_tmp = [
                            str(tmp_time_list[tmp_ele]*1e-9),
                            ','+str(math.nan),
                            ','+str(tmp_voltage_list[tmp_ele]),
                            ','+str(tmp_data_magnetic_field_x_mean),
                            ','+str(tmp_data_magnetic_field_y_mean),
                            ','+str(tmp_data_magnetic_field_z_mean),
                            ','+str(tmp_total_field),
                            ','+ str(freq_tmp[tmp_ele] if tmp_ele < len(freq_tmp) else math.nan), 
                            ','+str(abs(ft_tmp[tmp_ele]) if tmp_ele < len(freq_tmp) else math.nan), 
                            ',' + str(math.log10(freq_tmp[tmp_ele+1]) if tmp_ele < len(freq_tmp)-1 else math.nan),
                            ','+ str(math.log10(abs(ft_tmp[tmp_ele+1])) if tmp_ele < len(freq_tmp)-1 else math.nan),
                            ',' + str((math.nan, tmp_time_list[tmp_ele]*1e-9 if tmp_voltage_list[tmp_ele] >= self.treshold or tmp_voltage_list[tmp_ele] <= -1*self.treshold else math.nan)[self.treshold != 0]),
                            ',' + str((math.nan, tmp_voltage_list[tmp_ele]  if tmp_voltage_list[tmp_ele] >= self.treshold or tmp_voltage_list[tmp_ele] <= -1*self.treshold  else math.nan)[self.treshold != 0]),
                            ',' + str(math.nan if self.divide == 0 else tmp_voltage_list[tmp_ele]/self.divide)
                            ]

                        self.header.write_data(self.sample_name_raw,self.data_tmp)
                    
                self.emit('progress', 100 * i / self.steps)

                
            tmp_data_time["average"] = tmp_data_time.mean(axis=1) #average time
            tmp_data_voltage["average"] = tmp_data_voltage.mean(axis=1) #average voltage
            tmp_fft["average"] = np.mean(fft_tmp_rms_noise, axis=0)
            tmp_frequency["average"] = np.mean(tmp_frequency, axis=1) 
            
            

            tmp_data_time_average = tmp_data_time["average"].to_list()
            tmp_data_voltage_average = tmp_data_voltage["average"].to_list()
            tmp_data_fft_average = tmp_fft["average"].to_list()
            tmp_data_frequency_average = tmp_frequency["average"].to_list()
           
        
    #Send results:
            for ele in range(len(tmp_data_time_average)):
                try:
                    data2 = {
                            'frequency (Hz)': tmp_data_frequency_average[ele] if ele < len(tmp_data_frequency_average) else math.nan, 
                            'FFT (mV)': tmp_data_fft_average[ele] if ele < len(tmp_data_frequency_average) else math.nan, 
                            'log[frequency] (Hz)': math.log10(tmp_data_frequency_average[ele+1]) if ele < len(tmp_data_frequency_average)-1 else math.nan,
                            'log[FFT] (mV)':  math.log10(abs(tmp_data_fft_average[ele+1])) if ele < len(tmp_data_frequency_average)-1 else math.nan,
                            'time (s)': tmp_data_time_average[ele]*1e-9,
                            'Sense Voltage (mV)': tmp_data_voltage_average[ele],
                            'Bias voltage (mV)': self.bias_voltage,
                            'X field (Oe)': tmp_data_magnetic_field_x_mean,
                            'Y field (Oe)': tmp_data_magnetic_field_y_mean,
                            'Z field (Oe)': tmp_data_magnetic_field_z_mean,
                            'Field (Oe)' : tmp_total_field,
                            'treshold_time (s)': (math.nan, tmp_data_time_average[ele]*1e-9 if tmp_data_voltage_average[ele] >= self.treshold or tmp_data_voltage_average[ele] <= -1*self.treshold else math.nan)[self.treshold != 0],
                            'treshold_voltage (mV)': (math.nan, tmp_data_voltage_average[ele]  if tmp_data_voltage_average[ele] >= self.treshold or tmp_data_voltage_average[ele] <= -1*self.treshold  else math.nan)[self.treshold != 0],
                            'divide_voltage (mV)': math.nan if self.divide == 0 else tmp_data_voltage_average[ele]/self.divide
                            }
                    
                

                    self.emit('results', data2) 
                except:
                    self.should_stop()
                if self.should_stop():
                    log.warning("Caught the stop flag in the procedure")
                    break


        
       
#One shot mode
        elif self.mode == 'One Shot':
            self.oscilloscope.set_number_samples(self.no_samples)
            self.oscilloscope.set_timebase(int((1/self.sampling_interval)*10000000)-1)
            self.oscilloscope.run_block_capture()
            self.oscilloscope.check_data_collection()
            self.oscilloscope.create_buffers()
            self.oscilloscope.set_buffer_location()
            self.time = self.period_time
            self.stop_time = time()
            self.oscilloscope.getValuesfromScope()
            tmp_time_list = self.oscilloscope.create_time()
            
           
            tmp_voltage_list = self.oscilloscope.convert_to_mV(self.channelA_range)  
         
            self.emit('progress', 100)
            for ele in range(len(tmp_time_list)):
                data2 = {
                        'time (s)': tmp_time_list[ele]*1e-9,
                        'Sense Voltage (mV)': tmp_voltage_list[ele],
                        'frequency (Hz)': math.nan, 
                        'FFT (mV)': math.nan,
                        'log[frequency] (Hz)': math.nan,
                        'log[FFT] (mV)': math.nan,
                        'X field (Oe)': math.nan,
                        'Y field (Oe)':math.nan,
                        'Z field (Oe)': math.nan,
                        'Field (Oe)': math.nan,
                        'treshold_time (s)':math.nan,
                        'treshold_voltage (mV)': math.nan,
                        'divide_voltage (mV)': math.nan,
                        }
                self.emit('results', data2) 
#Vbias calibration mode:
        elif self.mode == "Vbias calibration":
            log.info("Vbias calibration mode start")
            vbias_list = []
            vs_list = []
            vs_fit = []
            k=0
           
            self.voltage.enabled() #enable channel 
         
           
            for i in self.vector:  
                self.voltage.voltage_setpoint(i) #set bias voltage
                vbias_list.append(i)
                sleep(0.1)
                print(k)
                self.oscilloscope.run_block_capture()
                self.oscilloscope.check_data_collection()
                self.oscilloscope.create_buffers()
                self.oscilloscope.set_buffer_location()
                self.oscilloscope.getValuesfromScope()
                tmp_time_list = self.oscilloscope.create_time()
                tmp_vs_list = self.oscilloscope.convert_to_mV(self.channelA_range) 
                vs_list.append(np.average(tmp_vs_list))
                self.emit('progress', 100 * k / len(self.vector))
                k = k + 1
            
            self.voltage.voltage_setpoint(1) #set bias voltage to 0
            self.voltage.disabled() #disable channel
            ##Fitting data:
            
            log.info("Fitting data start")
            self.fit_parameters = vbiascalibration(vbias_list, vs_list, "linear")
            log.info("Fitting data end")
            ##Save to file:
            log.info("Saving data to file start")
            fit_parameters_to_file(self.fit_parameters)
            log.info("Linear function: a = {}, b = {}".format(self.fit_parameters[0], self.fit_parameters[1]))
            log.info("Saving data to file end")
            for l in vbias_list:
                vs_fit.append(linear_func(l, self.fit_parameters[0],self.fit_parameters[1]))
           
        
                

            #Send results:
            for ele in range(len(vbias_list)):
                try:
                    data3 = {
                            'frequency (Hz)':  math.nan, 
                            'FFT (mV)': vs_fit[ele], 
                            'log[frequency] (Hz)': math.nan,
                            'log[FFT] (mV)':   math.nan,
                            'time (s)': math.nan,
                            'Sense Voltage (mV)': vs_list[ele],
                            'Bias voltage (mV)': vbias_list[ele],
                            'X field (Oe)': math.nan,
                            'Y field (Oe)': math.nan,
                            'Z field (Oe)': math.nan,
                            'Field (Oe)': math.nan,
                            'treshold_time (s)': math.nan,
                            'treshold_voltage (mV)': math.nan,
                            'divide_voltage (mV)': math.nan
                            }
                    
                

                    self.emit('results', data3) 
                except:
                    self.should_stop()
                if self.should_stop():
                    log.warning("Caught the stop flag in the procedure")
                    break



#Vbias mode: 
        elif self.mode == "Vbias":
            log.info("Vbias mode start")
            vbias_list = []
            vs_list = []
            k = 0
            log.info("read calibration parameters from file")
            try:
                fit_parameters = fit_parameters_from_file()
            except:
                self.should_stop()
                

            log.info("read calibration parameters from file end")
            self.voltage.enabled() #enable channel 
            for i in self.vector:  
                if self.should_stop():
                    log.warning("Caught the stop flag in the procedure")
                    break
                set_vol = calculationbias(i, fit_parameters, "linear")
                self.voltage.voltage_setpoint(set_vol) #set bias voltage
                vbias_list.append(i)  #list of Vbias
                sleep(0.1)
                self.oscilloscope.run_block_capture()
                self.oscilloscope.check_data_collection()
                self.oscilloscope.create_buffers()
                self.oscilloscope.set_buffer_location()
                self.oscilloscope.getValuesfromScope()
                tmp_time_list = self.oscilloscope.create_time()
                tmp_vs_list = self.oscilloscope.convert_to_mV(self.channelA_range)

                vs_list.append(np.average(tmp_vs_list))   #list of Vs 
                self.emit('progress', 100 * k / len(self.vector))
                k = k + 1
            self.voltage.voltage_setpoint(1) #set bias voltage to 0
            self.voltage.disabled() #disable channel
        #Send results:
            for ele in range(len(vbias_list)):
                try:
                    data3 = {
                            'frequency (Hz)':  math.nan, 
                            'FFT (mV)': math.nan, 
                            'log[frequency] (Hz)': math.nan,
                            'log[FFT] (mV)':   math.nan,
                            'time (s)': math.nan,
                            'Sense Voltage (mV)': vs_list[ele],
                            'Bias voltage (mV)': vbias_list[ele],
                            'X field (Oe)': math.nan,
                            'Y field (Oe)': math.nan,
                            'Z field (Oe)': math.nan,
                            'Field (Oe)': math.nan,
                            'treshold_time (s)': math.nan,
                            'treshold_voltage (mV)': math.nan,
                            'divide_voltage (mV)': math.nan
                            }
                    
                

                    self.emit('results', data3) 
                except:
                    self.should_stop()
                if self.should_stop():
                    log.warning("Caught the stop flag in the procedure")
                    break




######################################## End ########################################

    def stop_scope(self):
        
        print("Stop_scope")
        
    
    def disconnect_scope(self): 
        
        print("disconnect_scope")

    def run_to_zero(self):
        
        print("run_to_zero")
    

    def voltage_disabled(self): 
        
        print("voltage_disabled")
    
 
    def shutdown(self):
  
        self.oscilloscope.stop_scope()
        self.oscilloscope.disconnect_scope()
        if self.mode == 'Mean' or self.mode == 'Mean + Raw':
            if MainWindow.last == True or NoiseProcedure.licznik == MainWindow.wynik: 
                self.voltage.voltage_setpoint(1)
                sleep(0.5)
                self.voltage.disabled()
                if self.field_device == "E3600A":
                    self.field_coil.disabled(abs(self.bias_field_current/1000))
                else: 
                    self.field_coil.disabled()
                    sleep(10)
                 
                NoiseProcedure.licznik = 0
            if self.field_device == "HMC8043":
                self.field_coil.close_connection()    
            NoiseProcedure.licznik += 1
         
        

        
      
class MainWindow(ManagedWindow):
    last = False
    wynik = 0
    wynik_list = []
    def __init__(self):
        super().__init__(
            procedure_class= NoiseProcedure,
            inputs=['mode','sample_name','voltage_device', 'voltage_adress','field_device','field_adress', 'field_sensor_adress', 'period_time', 'no_time', 'sampling_interval','bias_voltage', 'bias_field_current', 'channelA_range', 'channelA_coupling_type', 'treshold', 'divide', 'start', 'stop', 'no_points', 'reverse_voltage', 'delay'],
            displays=['bias_voltage', 'period_time', 'no_time','sampling_interval', 'sample_name'],
            x_axis='time (s)',
            y_axis='Sense Voltage (mV)',
            directory_input=True,  
            sequencer=True,                                      
            sequencer_inputs=['bias_voltage','bias_field_current', 'period_time', 'sampling_interval'],    
            inputs_in_scrollarea=True,
            
        )
        self.setWindowTitle('Noise Measurement System v.1.3 beta')
        self.directory = self.procedure_class.path_file.ReadFile()
        

    def queue(self, procedure=None):
        directory = self.directory  # Change this to the desired directory
        self.procedure_class.path_file.WriteFile(directory)
        
        if procedure is None:
            procedure = self.make_procedure()
       
        name_of_file = procedure.sample_name
        filename = unique_name(directory, prefix="{}".format(name_of_file))
        results = Results(procedure, filename)
        experiment = self.new_experiment(results)
        self.manager.queue(experiment)
        
        
        

        try:
            
            MainWindow.wynik =  procedure.seq
            MainWindow.wynik_list.append(procedure.seq)
            MainWindow.wynik = max(MainWindow.wynik_list)
           
            MainWindow.last = False
            

                
        except:     
            
            MainWindow.last = True
            
            # while run:
            #     sleep(0.2)
            #     run = self.manager.is_running()
            # procedure.shutdown_definetly()
            
 
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
