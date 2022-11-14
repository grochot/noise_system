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
    field_sensor_adress = ListParameter("Field_sensor",  choices=["COM6"] )
    keithley_source_type = ListParameter("Source type", default = "Current", choices = ['Current', 'Voltage'])
    keithley_compliance_current = FloatParameter('Compliance current', units='A', default=0.1, group_by='keithley_source_type', group_condition='Voltage')
    keithley_compliance_voltage = FloatParameter('Compliance voltage', units='V', default=1,group_by='keithley_source_type', group_condition='Current')
    keithley_current_bias = FloatParameter('Current bias', units='A', default=0.01, group_by='acquire_type', group_condition='V(Hmb) |set Ib')
    keithley_voltage_bias = FloatParameter('Volage bias', units='V', default=0.1, group_by='acquire_type', group_condition='I(Hmb) | set Vb')
    field_bias = FloatParameter('Field bias', units='Oe', default=1, group_by='acquire_type', group_condition=lambda v: v =='I(Vb) | set Hmb' or v == 'V(Ib) | set Hmb')
    start = FloatParameter("Start")
    stop = FloatParameter("Stop")
    no_points = IntegerParameter("No Points")
    delay = FloatParameter("Delay", units = "ms", default = 100)
    sample_name = Parameter("Sample Name", default="sample name")
 
    DATA_COLUMNS = ['Voltage (V)', 'Current (A)', 'X field (Oe)', 'Y field (Oe)', 'Z field (Oe)'] #data columns

    path_file = SaveFilePath() 
   
    
    ################ STARTUP ##################3
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



    ##### PROCEDURE ######
    def execute(self):
        
        if self.acquire_type == 'I(Hmb) | set Vb':
            log.info("Starting to sweep through field")
            for i in self.vector:
                self.field.set_field(i)
                sleep(self.delay*0.001)
                self.tmp_field = self.field_sensor.read_field()
                self.tmp_x = self.tmp_field[0]
                self.tmp_y = self.tmp_field[1]
                self.tmp_z = self.tmp_field[2]
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
                self.tmp_field = self.field_sensor.read_field()
                self.tmp_x = self.tmp_field[0]
                self.tmp_y = self.tmp_field[1]
                self.tmp_z = self.tmp_field[2]
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
                self.tmp_field = self.field_sensor.read_field()
                self.tmp_x = self.tmp_field[0]
                self.tmp_y = self.tmp_field[1]
                self.tmp_z = self.tmp_field[2]
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
                self.tmp_field = self.field_sensor.read_field()
                self.tmp_x = self.tmp_field[0]
                self.tmp_y = self.tmp_field[1]
                self.tmp_z = self.tmp_field[2]
                data = {
                      'Voltage (V)':  self.tmp_volatage,
                      'Current (A)':  i,
                      'X field (Oe)': self.tmp_x,
                      'Y field (Oe)': self.tmp_y,
                      'Z field (Oe)': self.tmp_z,
                    }
                self.emit('results', data) 
      
    
    def shutdown(self):
        self.field.shutdown()
        

        

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
        self.setWindowTitle('IV Measurement System v.0.2')
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
