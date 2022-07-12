from email.policy import default
import logging
import sys
from time import sleep
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
#from hardware.picoscope4626 import PicoScope
from hardware.sim928 import SIM928

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class NoiseProcedure(Procedure):


    ################# PARAMETERS ###################
    period_time = IntegerParameter('Period of Time', units='ms', default=10)
    no_time = IntegerParameter('Number of times', default=10)
    bias_voltage = FloatParameter('Bias Voltage', units='V', default=0.1)
    bias_field = FloatParameter('Bias Field', units='Oe', default=10)
    channelB_enabled = BooleanParameter("Channel B Enabled", default=False)
    channelA_coupling_type = ListParameter("Channel A Coupling Type",  default='AC', choices=['DC','AC'])
    channelB_coupling_type = ListParameter("Channel B Coupling Type",  default='AC', choices=['DC','AC'])
    channelA_range = ListParameter("Channel A Range",  default="10mV", choices=["10mV", "20mV", "50mV", "100mV", "200mV", "500mV", "1V", "2V", "5V", "10V", "20V", "50V", "100V"])
    channelB_range = ListParameter("Channel B Range", default="10mV", choices=["10mV", "20mV", "50mV", "100mV", "200mV", "500mV", "1V", "2V", "5V", "10V", "20V", "50V", "100V"])
    sizeBuffer = IntegerParameter('Size of Buffer', default=10)
    noBuffer = IntegerParameter('Numbers of Buffer', default=1)
    field_constant = FloatParameter("Field constatnt", default=0)
    sample_name = Parameter("Sample Name", default="Noise Measurement")


    DATA_COLUMNS = ['time', 'Voltage (V)', 'Magnetic field (T)'] #data columns



    def startup(self):
        log.info("Setting up instruments") 

        ################# BIAS FIELD ###################
        try:
            self.field = HMC8043("ASRL1::INSTR") #connction to field controller
            self.field.set_channel(0) #set channnel 1
            self.field.enable_channel(1) #enable channel
            self.field_to_volatage = self.bias_voltage/self.field_constant
            self.field.set_voltage(self.field_to_volatage) #set field 
            log.info("Set bias field to %g" %self.field_to_volatage)
        except:
            log.error("Could not connect to field controller")
       
       ################# BIAS VOLTAGE ###################
        try:   
            self.voltage = SIM928("ASRL1::INSTR") #connect to voltagemeter
            self.voltage.enabled("ON") #enable channel 
            self.voltage.voltage_setpoint(self.bias_voltage) #set bias voltage
            log.info("Set bias voltage to %g" %self.bias_voltage)
        except: 
             log.error("Could not connect to bias voltage source")
       
       ################# PICOSCOPE ###################
        try: 
            self.oscilloscope = PicoScope("ASRL1::INSTR")
            self.oscilloscope.setChannelA(self.channelA_coupling_type, self.channelA_range )
            self.oscilloscope.setChannelB(self.channelB_coupling_type, self.channelB_range )
            self.oscilloscope.setSizeCapture(self.sizeBuffer, self.noBuffer)
            log.info("setup oscilloscope done")
        except: 
             log.error("Could not connect to oscilloscope")
        
        sleep(2)

    def execute(self):
        
        log.info("Starting to sweep through time")
        self.steps = self.no_time 
    
        for i in range(self.steps):
            
            voltage = random.random()
            magnetic_field = random.random()
            data = {
            'time': i,
            'Voltage (V)': voltage,
            'Magnetic field (T)': magnetic_field
            }
            self.emit('results', data)
            self.emit('progress', 100. * i / self.steps)
            #sleep(self.delay)
            if self.should_stop():
                log.warning("Catch stop command in procedure")
                break
        

    
    
    def shutdown(self):
        #self.source.shutdown()
        log.info("Finished")


class MainWindow(ManagedWindow):

    def __init__(self):
        super().__init__(
            procedure_class= NoiseProcedure,
            inputs=['period_time', 'no_time', 'bias_voltage', 'bias_field', 'channelB_enabled', 'channelA_coupling_type', 'channelB_coupling_type', 'channelA_range', 'channelB_range', 'sizeBuffer', 'noBuffer', 'field_constant', 'sample_name'],
            displays=['period_time', 'no_time', 'bias_voltage', 'bias_field', 'sample_name'],
            x_axis='time',
            y_axis='Voltage (V)',
            directory_input=True,  
            sequencer=True,                                      # Added line
            sequencer_inputs=['bias_field', 'bias_voltage'],    # Added line
            inputs_in_scrollarea=True,
            
        )
        self.setWindowTitle('Noise Measurement System')
       

    def queue(self, procedure=None):
        directory = "./"  # Change this to the desired directory
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