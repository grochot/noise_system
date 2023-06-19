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

from hardware.field_sensor_noise_new import FieldSensor 
from hardware.dummy_field_sensor_iv import DummyFieldSensor
from logic.generate_headers import GenerateHeader
from logic.fft_mean import FFT_mean
from logic.vbiascalibration import vbiascalibration, calculationbias, func, linear_func
from logic.fit_parameters_to_file import fit_parameters_to_file, fit_parameters_from_file

log = logging.getLogger(__name__) 
log.addHandler(logging.NullHandler()) 



class NoiseProcedure(Procedure):
    licznik = 0
    find_instruments = FindInstrument()
    finded_instruments = find_instruments.find_instrument()
    finded_instrumnets = finded_instruments.append("none")
    
################# PARAMETERS###################
#Noise mode:
    period_time = FloatParameter('Period of Time', units='s', default=1, group_by='mode', group_condition=lambda v: v =='Mean' or v=='One Shot' or v == 'Mean + Raw')
    mode = ListParameter("Mode",  default='Mean', choices=['Mean', 'One Shot', 'Mean + Raw', 'Vbias calibration', "Vbias"])
    no_time = IntegerParameter('Number of times', default=1, group_by='mode', group_condition=lambda v: v =='Mean' or v=='Mean + Raw')
    sampling_interval =FloatParameter('Sampling frequency', units='Hz', default=100, group_by='mode', group_condition=lambda v: v =='Mean' or v=='Mean + Raw' or v=='One Shot')
    bias_voltage = FloatParameter('Bias Voltage', units='mV', default=100,group_by='mode', group_condition=lambda v: v =='Mean' or v=='One Shot' or v == 'Mean + Raw')
    bias_field = FloatParameter('Bias Field Current', units='mA', default=0,group_by='mode',group_condition=lambda v: v =='Mean' or v=='Mean + Raw')
    voltage_adress = ListParameter("SIM928 adress", choices=finded_instruments,group_by='mode', group_condition=lambda v: v =='Mean' or v=='One Shot' or v == 'Mean + Raw' or v == 'Vbias calibration' or v == 'Vbias')
    field_adress = ListParameter("E3600a adress",  choices=finded_instruments,group_by='mode', group_condition=lambda v: v =='Mean' or v=='Mean + Raw')
    field_sensor_adress = ListParameter("Field_sensor",  choices=finded_instruments,group_by='mode', group_condition=lambda v: v =='Mean' or v=='Mean + Raw')
    channelA_coupling_type = ListParameter("Channel A Coupling Type",  default='DC', choices=['DC','AC'],group_by='mode',group_condition=lambda v: v =='Mean' or v=='Mean + Raw' or v =='Vbias calibration' or v == 'Vbias' )
    channelA_range = ListParameter("Channel A Range",  default="200mV", choices=["10mV", "20mV", "50mV", "100mV", "200mV", "500mV", "1V", "2V", "5V", "10V", "20V", "50V", "100V"],group_condition=lambda v: v =='Mean' or v=='Mean + Raw' or v == 'V bias calibration' or v == 'Vbias')
    sample_name = Parameter("Sample Name", default="Noise Measurement",group_by='mode', group_condition=lambda v: v =='Mean' or v=='Mean + Raw')
    treshold = FloatParameter("Treshold", units='mV',group_by='mode', group_condition=lambda v: v =='Mean' or v=='Mean + Raw')
    divide = FloatParameter("Divide number", units = 'mV',group_by='mode', group_condition=lambda v: v =='Mean' or v=='Mean + Raw')
    
#Bias mode:
    start = FloatParameter("Start",units='mV', group_by='mode', group_condition=lambda v: v =='Vbias calibration' or v == 'Vbias')
    stop = FloatParameter("Stop", units='mV', group_by='mode', group_condition=lambda v: v =='Vbias calibration' or v == 'Vbias')
    no_points = IntegerParameter("No Points", group_by='mode', group_condition=lambda v: v =='Vbias calibration' or v == 'Vbias')
    reverse_voltage = BooleanParameter("Reverse voltage", default=False, group_by='mode', group_condition=lambda v: v =='Vbias calibration' or v == 'Vbias')
    delay = FloatParameter("Delay", units = "ms", default = 1000, group_by='mode', group_condition=lambda v: v =='Vbias calibration' or v == 'Vbias')
   


   
    DATA_COLUMNS = ['time (s)','Bias voltage (mV)', 'Sense Voltage (mV)', 'X field (Oe)', 'Y field (Oe)', 'Z field (Oe)', 'frequency (Hz)', 'FFT (mV)', 'log[frequency] (Hz)' ,'log[FFT] (mV)' , 'treshold_time (s)', 'treshold_voltage (mV)', 'divide_voltage (mV)'] #data columns
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
        if self.mode == 'Mean' or self.mode == 'Mean + Raw':
            if self.mode == 'Mean + Raw':
                self.header = GenerateHeader()
                self.header_columns = self.prepare_columns(self.DATA_COLUMNS)
            self.oscilloscope = PicoScope()
            if self.voltage_adress == 'none':
                from hardware.sim928_dummy import SIM928 
                self.voltage = SIM928()
            else:
                from hardware.sim928 import SIM928 
                self.voltage = SIM928(self.voltage_adress,timeout = 25000, baud_rate = 9600) #connect to voltagemeter
    
            sleep(0.1)
            log.info("Finding instrument done")
        
        
            self.no_samples = int(self.period_time/(((1/self.sampling_interval))))
            if self.no_samples % 2 == 1:
                self.no_samples = self.no_samples + 1
          

    ##Field Sensor:
            
            if self.field_sensor_adress == "none":
                print(self.field.sensor_adress)
                self.field = DummyFieldSensor()
                log.warning("Use DummyFieldSensor")
            
            else:
                self.field = FieldSensor(self.field_sensor_adress)
                self.field.read_field_init()
               

    ##Bias field:
            try:
                self.field_coil = E3600a(self.field_adress) #connction to field controller
                self.field_coil.remote()
                self.field_coil.current(self.bias_field/1000) #set field 
                self.field_coil.enabled()
                sleep(1)
                log.info("Set bias field to %g V" %self.bias_field)
            except:
                log.error("Could not connect to field controller")
                
        
    ##Bias voltage:
            log.info("read calibration parameters from file")
            try:
                fit_parameters = fit_parameters_from_file()
                a = fit_parameters[0]
                b = fit_parameters[1]
                print(a,b)
                set_vol = calculationbias(self.bias_voltage, a,b,0, "linear")
                print(set_vol)
                self.voltage.voltage_setpoint(set_vol) #set bias voltage  
                log.info("read parameters succesfull")
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
            self.oscilloscope = PicoScope()
            self.voltage = SIM928(self.voltage_adress,timeout = 25000, baud_rate = 9600) #connect to voltagemeter
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
            self.voltage = SIM928(self.voltage_adress,timeout = 25000, baud_rate = 9600) #connect to voltage 
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
            print("main loop")
            self.voltage.enabled() #enable channel 
            print("enabled outlput")
           
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
            
            self.voltage.voltage_setpoint(0) #set bias voltage to 0
            self.voltage.disabled() #disable channel
            ##Fitting data:
            
            log.info("Fitting data start")
            self.fit_parameters = vbiascalibration(vbias_list, vs_list, "linear")
            log.info("Fitting data end")
            ##Save to file:
            log.info("Saving data to file start")
            fit_parameters_to_file(self.fit_parameters)
            print(self.fit_parameters)
            log.info("Saving data to file end")
            for l in vbias_list:
                vs_fit.append(linear_func(l, self.fit_parameters[0],self.fit_parameters[1]))
            print(vs_fit)
        
                

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
            self.voltage.voltage_setpoint(0) #set bias voltage to 0
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
                self.voltage.voltage_setpoint(0)
                sleep(0.5)
                self.voltage.disabled()
                self.field_coil.disabled(self.bias_field/1000)
                NoiseProcedure.licznik = 0
            NoiseProcedure.licznik += 1
         
        

        
      
class MainWindow(ManagedWindow):
    last = False
    wynik = 0
    wynik_list = []
    def __init__(self):
        super().__init__(
            procedure_class= NoiseProcedure,
            inputs=['mode','sample_name','voltage_adress','field_adress', 'field_sensor_adress', 'period_time', 'no_time', 'sampling_interval','bias_voltage', 'bias_field', 'channelA_range', 'channelA_coupling_type', 'treshold', 'divide', 'start', 'stop', 'no_points', 'reverse_voltage', 'delay'],
            displays=['bias_voltage', 'period_time', 'no_time','sampling_interval', 'sample_name'],
            x_axis='time (s)',
            y_axis='Sense Voltage (mV)',
            directory_input=True,  
            sequencer=True,                                      
            sequencer_inputs=['bias_voltage','bias_field'],    
            inputs_in_scrollarea=True,
            
        )
        self.setWindowTitle('Noise Measurement System v.1.21 beta')
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
