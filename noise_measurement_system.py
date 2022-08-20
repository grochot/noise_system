from email.policy import default
import logging
import pandas as pd 
import sys
from time import sleep, time
import matplotlib.pyplot as plt
import traceback
import random
#from typing import no_type_check
#from argon2 import Parameters
#from more_itertools import sample
import numpy as np

from pymeasure.display.Qt import QtGui
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import (
    Procedure, FloatParameter, BooleanParameter, IntegerParameter, Parameter,ListParameter, unique_filename, Results
)

from hardware.hmc8043 import HMC8043
from hardware.picoscope4626 import PicoScope
from hardware.sim928 import SIM928

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class NoiseProcedure(Procedure):
    ################# PARAMETERS ###################
    period_time = FloatParameter('Period of Time', units='s', default=1)
    no_time = IntegerParameter('Number of times', default=3)
    sampling_interval =FloatParameter('Sampling interval', units='s', default=0.01)
    bias_voltage = FloatParameter('Bias Voltage', units='V', default=1)
    bias_field = FloatParameter('Bias Field Voltage', units='V', default=0)
    #channelB_enabled = BooleanParameter("Channel B Enabled", default=False)
    channelA_coupling_type = ListParameter("Channel A Coupling Type",  default='AC', choices=['DC','AC'])
    #channelB_coupling_type = ListParameter("Channel B Coupling Type",  default='AC', choices=['DC','AC'])
    channelA_range = ListParameter("Channel A Range",  default="200mV", choices=["10mV", "20mV", "50mV", "100mV", "200mV", "500mV", "1V", "2V", "5V", "10V", "20V", "50V", "100V"])
    #channelB_range = ListParameter("Channel B Range", default="10mV", choices=["10mV", "20mV", "50mV", "100mV", "200mV", "500mV", "1V", "2V", "5V", "10V", "20V", "50V", "100V"])
    #sizeBuffer = IntegerParameter('Size of Buffer', default=10)
    #noBuffer = IntegerParameter('Numbers of Buffer', default=1)
    #field_constant = FloatParameter("Field constatnt", default=0)
    sample_name = Parameter("Sample Name", default="Noise Measurement")
    


    DATA_COLUMNS = ['time (s)', 'Voltage (V)', 'Magnetic field (T)'] #data columns



    def startup(self):
        
        log.info("Setting up instruments") 
        self.no_samples = int(self.period_time/((self.sampling_interval)))
        if self.no_samples % 2 == 1:
            self.no_samples = self.no_samples + 1
        log.info("Number of samples: %g" %self.no_samples)
        ################# BIAS FIELD ###################
        #try:
            #self.field = HMC8043("ASRL1::INSTR") #connction to field controller
            #self.field.set_channel(0) #set channnel 1
            #self.field.enable_channel(1) #enable channel
            #self.field.set_voltage(self.bias_field) #set field 
            #sleep(1)
            #log.info("Set bias field to %g V" %self.bias_field)
        #except:
            #log.error("Could not connect to field controller")
            #log.info("Set bias field to %g V" %self.bias_field)
       
       ################# BIAS VOLTAGE ###################
        try:   
            self.voltage = SIM928("ASRL/dev/ttyUSB0::INSTR",timeout = 25000, baud_rate = 115200) #connect to voltagemeter
            self.voltage.enabled() #enable channel 
            sleep(0.3)
            self.voltage.voltage_setpoint(self.bias_voltage) #set bias voltage
            sleep(0.2)
            log.info("Set bias voltage to %g V" %self.bias_voltage)
        except Exception:
            traceback.print_exc()
            log.error("Could not connect to bias voltage source")
             #log.info("Set bias voltage to %g V" %self.bias_voltage)
       
       ################# PICOSCOPE ###################
        
        self.oscilloscope = PicoScope()
        self.oscilloscope.setChannelA(self.channelA_coupling_type, self.channelA_range )
        #self.oscilloscope.setChannelB(self.channelB_coupling_type, self.channelB_range )
        self.oscilloscope.setTrigger()
        log.info("setup oscilloscope done")
        
        #log.error("Could not connect to oscilloscope")
        
        sleep(2)


    ##### PROCEDURE ######
    def execute(self):
        log.info("Starting to sweep through time")
        ######### set oscilloscope #########
        self.oscilloscope.set_number_samples(self.no_samples)
        self.oscilloscope.set_timebase(int(self.sampling_interval*10000000)-1)
        self.oscilloscope.run_block_capture()
        self.oscilloscope.check_data_collection()
        self.oscilloscope.create_buffers()
        self.oscilloscope.set_buffer_location()
        self.steps = self.no_time 
        self.time = self.period_time
        self.stop_time = time()
        tmp_data_time = pd.DataFrame(columns=['time'])
        tmp_data_voltage = pd.DataFrame(columns=['voltage'])
        tmp_data_magnetic_field = pd.DataFrame(columns=['field'])

        ########### measure field ########### 

        tmp_magnetic_field_list = 5
        #########################################
        for i in range(self.steps):
            ######### run oscilloscope #########
            self.oscilloscope.getValuesfromScope()
            tmp_time_list = self.oscilloscope.create_time()
            tmp_voltage_list = self.oscilloscope.convert_to_mV(self.channelA_range)
        
            tmp_data_time.insert(i,"time_{}".format(i),pd.Series(tmp_time_list))
            tmp_data_voltage.insert(i,"voltage_{}".format(i),pd.Series(tmp_voltage_list))
            tmp_data_magnetic_field.insert(i,"field_{}".format(i),pd.Series(tmp_magnetic_field_list))
            self.emit('progress', 100. * (i / self.steps))
       
            if self.should_stop():
                self.oscilloscope.stop_scope()
                self.oscilloscope.disconnect_scope()
                log.warning("Catch stop command in procedure")
                break
            
        tmp_data_time["average"] = tmp_data_time.mean(axis=1) #average time
        tmp_data_voltage["average"] = tmp_data_voltage.mean(axis=1) #average voltage
        tmp_data_magnetic_field["average"] = tmp_data_magnetic_field.mean(axis=1) #average magnetic field

        tmp_data_time_average = tmp_data_time["average"].to_list()
        tmp_data_voltage_average = tmp_data_voltage["average"].to_list()
        tmp_data_magnetic_field_average = tmp_data_magnetic_field["average"].to_list()
        for elem in range(len(tmp_data_time_average)):
            data = {
                    'time (s)': tmp_data_time_average[elem]*1e-9,
                    'Voltage (V)': tmp_data_voltage_average[elem],
                    'Magnetic field (T)': tmp_data_magnetic_field_average[0]
                    }
            self.emit('results', data) 
            
        

    
    
    def shutdown(self):
        self.oscilloscope.stop_scope()
        self.oscilloscope.disconnect_scope()
        self.voltage.run_to_zero()
        log.info("Finished")


class MainWindow(ManagedWindow):

    def __init__(self):
        super().__init__(
            procedure_class= NoiseProcedure,
            inputs=['sample_name','period_time', 'no_time', 'sampling_interval','bias_voltage', 'bias_field', 'channelA_range', 'channelA_coupling_type'],
            displays=['period_time', 'no_time','sampling_interval', 'bias_voltage', 'bias_field', 'sample_name'],
            x_axis='time (s)',
            y_axis='Voltage (V)',
            directory_input=True,  
            sequencer=True,                                      # Added line
            sequencer_inputs=['bias_field', 'bias_voltage'],    # Added line
            inputs_in_scrollarea=True,
            
        )
        self.setWindowTitle('Noise Measurement System v.0.9')
        self.directory = "/"
       

    def queue(self, procedure=None):
        directory = self.directory  # Change this to the desired directory
        if procedure is None:
            procedure = self.make_procedure()
        name_of_file = procedure.sample_name
        filename = unique_filename(directory, prefix="{}_".format(name_of_file))
        results = Results(procedure, filename)
        experiment = self.new_experiment(results)

        self.manager.queue(experiment)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
