from ast import Num
from email.policy import default
import logging
import pandas as pd 

import math
import sys
import random
from time import sleep, time
import traceback
from find_instrument import FindInstrument
from save_results_path import SaveFilePath

import numpy as np

from pymeasure.display.Qt import QtGui
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import (
    Procedure, FloatParameter, BooleanParameter, IntegerParameter, Parameter,ListParameter, unique_filename, Results, VectorParameter
)

from pymeasure.instruments.keithley import Keithley2400
from hardware.daq import DAQ
from hardware.field_sensor import FieldSensor 

log = logging.getLogger(__name__) 
log.addHandler(logging.NullHandler()) 



class IVTransfer(Procedure):
    licznik = 0
    find_instruments = FindInstrument()
    finded_instruments = find_instruments.show_instrument() 
    print(finded_instruments)
    ################# PARAMETERS ###################
    acquire_type = ListParameter("Acquire type", choices = ['I(Hmb) | set Vb', 'V(Hmb) |set Ib', 'I(Vb) | set Hmb', 'V(Ib) | set Hmb'])
    keithley_adress = ListParameter("Keithley2400 adress", choices=finded_instruments)
    field_sensor_adress = ListParameter("Field_sensor",  choices=finded_instruments )
    keithley_source_type = ListParameter("Source type", default = "Current", choices = ['Current', 'Voltage'])
    keithley_compliance_current = FloatParameter('Compliance current', units='A', default=0.1, group_by='keithley_source_type', group_condition='Voltage')
    keithley_compliance_voltage = FloatParameter('Compliance voltage', units='V', default=1,group_by='keithley_source_type', group_condition='Current')
    keithley_current_bias = FloatParameter('Current bias', units='A', default=0.01, group_by='acquire_type', group_condition='V(Hmb) |set Ib')
    keithley_voltage_bias = FloatParameter('Volage bias', units='V', default=0.1, group_by='acquire_type', group_condition='I(Hmb) | set Vb')
    field_bias = FloatParameter('Field bias', units='Oe', default=1, group_by='acquire_type', group_condition=lambda v: v =='I(Vb) | set Hmb' or v == 'V(Ib) | set Hmb')
    #voltage_vector = VectorParameter('Voltage', units='V', group_by='acquire_type', group_condition='I(Vb) | set Hmb')
    #current_vector = VectorParameter('Current', units='A', group_by='acquire_type', group_condition='V(Ib) | set Hmb')
    #field_vector = VectorParameter('Field', units='Oe', group_by='acquire_type', group_condition=lambda v: v =='V(Hmb) |set Ib' or v == 'I(Hmb) | set Vb')
    start = FloatParameter("Start")
    stop = FloatParameter("Stop")
    no_points = IntegerParameter("No Points")
    delay = FloatParameter("Delay", units = "ms", default = 100)

    # field_adress = ListParameter("HMC8043 adress",  choices=finded_instruments)
    
    # #channelB_enabled = BooleanParameter("Channel B Enabled", default=False)
    # channelA_coupling_type = ListParameter("Channel A Coupling Type",  default='AC', choices=['DC','AC'])
    # #channelB_coupling_type = ListParameter("Channel B Coupling Type",  default='AC', choices=['DC','AC'])
    # channelA_range = ListParameter("Channel A Range",  default="200mV", choices=["10mV", "20mV", "50mV", "100mV", "200mV", "500mV", "1V", "2V", "5V", "10V", "20V", "50V", "100V"])
    # #channelB_range = ListParameter("Channel B Range", default="10mV", choices=["10mV", "20mV", "50mV", "100mV", "200mV", "500mV", "1V", "2V", "5V", "10V", "20V", "50V", "100V"])
    # #sizeBuffer = IntegerParameter('Size of Buffer', default=10)
    # #noBuffer = IntegerParameter('Numbers of Buffer', default=1)
    # #field_constant = FloatParameter("Field constatnt", default=0)
    sample_name = Parameter("Sample Name", default="sample name")
    # treshold = FloatParameter("Treshold", units='mV')
    # divide = FloatParameter("Divide number", units = 'mV')
    



    DATA_COLUMNS = ['Voltage (V)', 'Current (A)', 'X field (Oe)', 'Y field (Oe)', 'Z field (Oe)'] #data columns

    path_file = SaveFilePath() 
   
    
    
    def startup(self):

        log.info("Finding instruments...")
        sleep(0.1)
        log.info("Finded: {}".format(self.finded_instruments))
         ####### Config DAQ ############
        log.info('Start config DAQ') 
        try:
            self.field = DAQ("6124/ao0")
            log.info("Config DAQ done")
        except:
            log.error("Config DAQ failed")
        
        self.vector = np.linspace(self.start, self.stop,self.no_points)
        
        ############## KEITHLEY CONFIG ###############
        log.info("Start config Keithley")
        try:
            self.keithley = Keithley2400(self.keithley_adress)
            if self.acquire_type == 'I(Hmb) | set Vb': 
                self.keithley.apply_voltage()
                self.keithley.compliance_current = self.keithley_compliance_current
                self.keithley.source_voltage = self.keithley_voltage_bias             # Sets the source current to 0 mA
                self.keithley.enable_source()                # Enables the source output
                self.keithley.measure_current()  
            elif self.acquire_type == 'V(Hmb) |set Ib': 
                self.keithley.apply_current()
                self.keithley.compliance_voltage = self.keithley_compliance_voltage
                self.keithley.source_current= self.keithley_current_bias            # Sets the source current to 0 mA
                self.keithley.enable_source()                # Enables the source output
                self.keithley.measure_voltage()         
            elif self.acquire_type == 'I(Vb) | set Hmb': 
                self.keithley.apply_voltage()
                self.keithley.compliance_current = self.keithley_compliance_current
                self.keithley.source_voltage =  0         # Sets the source current to 0 mA
                self.keithley.enable_source()                # Enables the source output
                self.keithley.measure_current()
                self.field.set_field(self.field_bias)
            elif self.acquire_type == 'V(Ib) | set Hmb': 
                self.keithley.apply_current()
                self.keithley.compliance_voltage = self.keithley_compliance_voltage
                self.keithley.source_current=  0         # Sets the source current to 0 mA
                self.keithley.enable_source()                # Enables the source output
                self.keithley.measure_voltage()
                self.field.set_field(self.field_bias)
            log.info("Config Keithley done")

        except:
            log.error("Config Keithley failed")

       
        
        ####### Config FieldSensor ######## 
        log.info("Config Field Sensor")
        try:
            self.field_sensor = FieldSensor(self.field_sensor_adress)

            log.info("Config FieldSensor done")
        except:
            log.error("Config FieldSensor failed")





        # self.oscilloscope = PicoScope()
        # self.voltage = SIM928(self.voltage_adress,timeout = 25000, baud_rate = 9600) #connect to voltagemeter
        #################FIND INSTRUMENTS#################
        
        ##################################################
        
        # self.no_samples = int(self.period_time/(((1/self.sampling_interval))))
        # if self.no_samples % 2 == 1:
        #     self.no_samples = self.no_samples + 1
        # log.info("Number of samples: %g" %self.no_samples)

        ################# FIELD SENSOR #################

        # self.field_sensor = FieldSensor(self.field_sensor_adress)

        ################# BIAS FIELD ###################
        # try:
        #     self.field = HMC8043("ASRL1::INSTR") #connction to field controller
        #     self.field.set_channel(0) #set channnel 1
        #     self.field.enable_channel(1) #enable channel
        #     self.field.set_voltage(self.bias_field) #set field 
        #     sleep(1)
        #     log.info("Set bias field to %g V" %self.bias_field)
        # except:
        #     log.error("Could not connect to field controller")
            
       
       ################ BIAS VOLTAGE ###################
        # try:   
           
        #     self.voltage.voltage_setpoint(self.bias_voltage) #set bias voltage
        #     sleep(1)
        #     self.voltage.enabled() #enable channel 
        #     log.info("Set bias voltage to %g V" %self.bias_voltage)
        # except Exception:
        #     traceback.print_exc()
        #     log.error("Could not connect to bias voltage source")
        
       ################ PICOSCOPE ###################
        
       
        # self.oscilloscope.setChannelA(self.channelA_coupling_type, self.channelA_range )
        # #self.oscilloscope.setChannelB(self.channelB_coupling_type, self.channelB_range )
        # self.oscilloscope.setTrigger()
        # log.info("setup oscilloscope done")
    
       
        # #log.error("Could not connect to oscilloscope")
        
        # sleep(2)


    ##### PROCEDURE ######
    def execute(self):
        
        if self.acquire_type == 'I(Hmb) | set Vb':
            log.info("Starting to sweep through field")
            for i in self.vector:
                self.field.set_field(i)
                sleep(self.delay*0.001)
                self.tmp_x = self.field_sensor.read_field()[0]
                self.tmp_y = self.field_sensor.read_field()[1]
                self.tmp_z = self.field_sensor.read_field()[2]
                sleep(self.delay*0.001)
                self.tmp_current = self.keithley.current
                data = {
                      'Voltage (V)':  self.keithley_voltage_bias,
                      'Current (A)':  self.tmp_current,
                      'X field (Oe)': self.tmp_x,
                      'Y field (Oe)': self.tmp_y,
                      'Z field (Oe)': self.tmp_z,
                    }
                self.emit('results', data) 



        elif self.acquire_type == 'V(Hmb) |set Ib':
            log.info("Starting to sweep through field")
            for i in self.vector:
                self.field.set_field(i)
                print(i)
                sleep(self.delay*0.001)
                self.tmp_x = 1#self.field_sensor.read_field()[0]
                self.tmp_y = 1#self.field_sensor.read_field()[1]
                self.tmp_z = 1#self.field_sensor.read_field()[2]
                sleep(self.delay*0.001)
                self.tmp_volatege = self.keithley.voltage
                data = {
                      'Voltage (V)':  self.tmp_volatege,
                      'Current (A)':  self.keithley_current_bias,
                      'X field (Oe)': self.tmp_x,
                      'Y field (Oe)': self.tmp_y,
                      'Z field (Oe)': self.tmp_z,
                    }
                self.emit('results', data) 
                 
        elif self.acquire_type == 'I(Vb) | set Hmb':
            log.info("Starting to sweep through voltage")
            for i in self.vector:
                self.keithley.source_voltage =  i
                sleep(self.delay*0.001)
                self.tmp_current = self.keithley.current
                sleep(self.delay*0.001)
                self.tmp_x = self.field_sensor.read_field()[0]
                self.tmp_y = self.field_sensor.read_field()[1]
                self.tmp_z = self.field_sensor.read_field()[2]
                data = {
                      'Voltage (V)':  i,
                      'Current (A)':  self.tmp_current,
                      'X field (Oe)': self.tmp_x,
                      'Y field (Oe)': self.tmp_y,
                      'Z field (Oe)': self.tmp_z,
                    }
                self.emit('results', data) 
            
        elif self.acquire_type == 'V(Ib) | set Hmb':
            log.info("Starting to sweep through current")
            for i in self.vector:
                self.keithley.source_current =  i
                sleep(self.delay*0.001)
                self.tmp_volatage = self.keithley.voltage
                sleep(self.delay*0.001)
                self.tmp_x = self.field_sensor.read_field()[0]
                self.tmp_y = self.field_sensor.read_field()[1]
                self.tmp_z = self.field_sensor.read_field()[2]
                data = {
                      'Voltage (V)':  self.tmp_volatage,
                      'Current (A)':  i,
                      'X field (Oe)': self.tmp_x,
                      'Y field (Oe)': self.tmp_y,
                      'Z field (Oe)': self.tmp_z,
                    }
                self.emit('results', data) 
            
        ######## set oscilloscope #########
    #     self.oscilloscope.set_number_samples(self.no_samples)
    #     self.oscilloscope.set_timebase(int((1/self.sampling_interval)*10000000)-1)
    #     self.oscilloscope.run_block_capture()
    #     self.oscilloscope.check_data_collection()
    #     self.oscilloscope.create_buffers()
    #     self.oscilloscope.set_buffer_location()
    #     self.steps = self.no_time 
    #     self.time = self.period_time
    #     self.stop_time = time()
    #     tmp_data_time = pd.DataFrame(columns=['time'])
    #     tmp_data_voltage = pd.DataFrame(columns=['voltage'])
    #     tmp_data_magnetic_field_x = []
    #     tmp_data_magnetic_field_y = []
    #     tmp_data_magnetic_field_z = []

    #     ########## measure field ########### 
        
        
    #     for i in range(5):
    #         tmp_x = self.field_sensor.read_field()[0]
    #         tmp_y = self.field_sensor.read_field()[1]
    #         tmp_z = self.field_sensor.read_field()[2]
            
            
    #         tmp_data_magnetic_field_x.append(float(tmp_x))
    #         tmp_data_magnetic_field_y.append(float(tmp_y))
    #         tmp_data_magnetic_field_z.append(float(tmp_z))
    #         sleep(1)
        
       
    #     tmp_data_magnetic_field_x_mean = float(sum(tmp_data_magnetic_field_x)/len(tmp_data_magnetic_field_x))/100
    #     tmp_data_magnetic_field_y_mean = float(sum(tmp_data_magnetic_field_y)/len(tmp_data_magnetic_field_y))/100
    #     tmp_data_magnetic_field_z_mean = float(sum(tmp_data_magnetic_field_z)/len(tmp_data_magnetic_field_z))/100
    #     #########################################
    #     for i in range(self.steps):
    #         ####### run oscilloscope #########
    #         self.oscilloscope.getValuesfromScope()
    #         tmp_time_list = self.oscilloscope.create_time()
    #         tmp_voltage_list = self.oscilloscope.convert_to_mV(self.channelA_range)
    #         print("pomiar")
        
    #         tmp_data_time.insert(i,"time_{}".format(i),pd.Series(tmp_time_list))
    #         tmp_data_voltage.insert(i,"voltage_{}".format(i),pd.Series(tmp_voltage_list))
    #         self.emit('progress', 100 * int(i / self.steps))

    #         # if self.should_stop():
    #         #     self.oscilloscope.stop_scope()
    #         #     self.oscilloscope.disconnect_scope()
    #         #     log.warning("Catch stop command in procedure")
    #         #     break
            
    #     tmp_data_time["average"] = tmp_data_time.mean(axis=1) #average time
    #     tmp_data_voltage["average"] = tmp_data_voltage.mean(axis=1) #average voltage
        

    #     tmp_data_time_average = tmp_data_time["average"].to_list()
    #     tmp_data_voltage_average = tmp_data_voltage["average"].to_list()
    #    ########################## FFT Counting ##########################
    #     smpl_freq = self.sampling_interval
    #     ft_ = np.fft.fft(tmp_data_voltage_average) / len(tmp_data_voltage_average)  # Normalize amplitude and apply the FFT
    #     ft_ = ft_[range(int(len(tmp_data_voltage_average)/2))]   # Exclude sampling frequency
    #     tp_cnt = len(tmp_data_voltage_average)
    #     val_ = np.arange(int(tp_cnt / 2))
    #     tm_period_ = tp_cnt / smpl_freq
    #     freq_ = val_ / tm_period_
    #     print("zmierzone!")
    #    ########################## Send results#############################
    #     for ele in range(len(tmp_data_time_average)):
    #         data2 = {
    #                   'frequency (Hz)': freq_[ele] if ele < len(freq_) else math.nan, 
    #                   'FFT (mV)': abs(ft_[ele]) if ele < len(freq_) else math.nan, 
    #                   'time (s)': tmp_data_time_average[ele]*1e-9,
    #                   'Voltage (mV)': tmp_data_voltage_average[ele],
    #                   'X field (Oe)': tmp_data_magnetic_field_x_mean,
    #                   'Y field (Oe)': tmp_data_magnetic_field_y_mean,
    #                   'Z field (Oe)': tmp_data_magnetic_field_z_mean,
    #                   'treshold_time (s)': (math.nan, tmp_data_time_average[ele]*1e-9 if tmp_data_voltage_average[ele] >= self.treshold or tmp_data_voltage_average[ele] <= -1*self.treshold else math.nan)[self.treshold != 0],
    #                   'treshold_voltage (mV)': (math.nan, tmp_data_voltage_average[ele]  if tmp_data_voltage_average[ele] >= self.treshold or tmp_data_voltage_average[ele] <= -1*self.treshold  else math.nan)[self.treshold != 0],
    #                   'divide_voltage (mV)': math.nan if self.divide == 0 else tmp_data_voltage_average[ele]/self.divide
    #                 }
    #         self.emit('results', data2) 
    

    # def stop_scope(self):
        
    #     print("Stop_scope")
        
    
    # def disconnect_scope(self): 
        
    #     print("disconnect_scope")

    # def run_to_zero(self):
        
    #     print("run_to_zero")
    

    # def voltage_disabled(self): 
        
    #     print("voltage_disabled")

    
 
    def shutdown(self):
        pass
        # print("funkcja_shutdown")
        # self.oscilloscope.stop_scope()
        # self.oscilloscope.disconnect_scope()
        
        # if MainWindow.last == True or NoiseProcedure.licznik == MainWindow.wynik: 
        #     self.voltage.voltage_setpoint(0)
        #     sleep(1)
        #     self.voltage.disabled()
        #     NoiseProcedure.licznik = 0
        # NoiseProcedure.licznik += 1
        # print(NoiseProcedure.licznik)
        

        

class MainWindow(ManagedWindow):
    last = False
    wynik = 0
    wynik_list = []
    def __init__(self):
        super().__init__(
            procedure_class= IVTransfer,
            inputs=['sample_name','acquire_type','keithley_adress','field_sensor_adress','keithley_source_type', 'keithley_compliance_current', 'keithley_compliance_voltage',
            'keithley_current_bias', 'keithley_voltage_bias', 'field_bias', 'delay', 'start', 'stop', 'no_points'],
            displays=['sample_name', 'acquire_type'],
            x_axis='Current (A)',
            y_axis='Voltage (V)',
            directory_input=True,  
            sequencer=True,                                      
            sequencer_inputs=['field_bias'],    
            inputs_in_scrollarea=True,
            
        )
        self.setWindowTitle('IV Measurement System v.0.1')
        self.directory = self.procedure_class.path_file.ReadFile()
        

    def queue(self, procedure=None):
        directory = self.directory  # Change this to the desired directory
        self.procedure_class.path_file.WriteFile(directory)
        
        if procedure is None:
            procedure = self.make_procedure()
       
        name_of_file = procedure.sample_name
        filename = unique_filename(directory, prefix="{}_".format(name_of_file))
        results = Results(procedure, filename)
        experiment = self.new_experiment(results)
        self.manager.queue(experiment)
        
        
        

        try:
            
            MainWindow.wynik =  procedure.seq
            MainWindow.wynik_list.append(procedure.seq)
            MainWindow.wynik = max(MainWindow.wynik_list)
            print(MainWindow.wynik)
            MainWindow.last = False
            

                
        except:     
            print("No procedure")
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
