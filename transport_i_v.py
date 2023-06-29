from ast import Num
from email.policy import default
import logging
import pandas as pd 

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
    Procedure, FloatParameter, BooleanParameter, IntegerParameter, Parameter,ListParameter, Results, VectorParameter
)
from logic.unique_name import unique_name

from hardware.keithley2400 import Keithley2400
from modules.compute_diff import ComputeDiff
from modules.computer_resisrance import ComputerResistance

from hardware.field_sensor_iv import FieldSensor
from hardware.dummy_field_sensor_iv import DummyFieldSensor

log = logging.getLogger(__name__) 
log.addHandler(logging.NullHandler()) 



class IVTransfer(Procedure):
    licznik = 1
    find_instruments = FindInstrument()
    finded_instruments = find_instruments.show_instrument() 
    print(finded_instruments)
    ################# PARAMETERS ###################
    mode = ListParameter("Mode",  default='Standard', choices=['Standard', 'Fast Resistance'])
    acquire_type = ListParameter("Acquire type", choices = ['I(Hmb) | set Vb', 'V(Hmb) |set Ib', 'I(Vb) | set Hmb', 'V(Ib) | set Hmb'],group_by='mode', group_condition=lambda v: v =='Standard')
    keithley_adress = ListParameter("Keithley2400 adress", choices=["GPIB1::24::INSTR"])
    field_sensor_adress = Parameter("Field_sensor",  default="COM8",group_by='mode', group_condition=lambda v: v =='Standard' )
    #keithley_source_type = ListParameter("Source type", default = "Current", choices = ['Current', 'Voltage'])
    keithley_compliance_current = FloatParameter('Compliance current', units='A', default=0.1, group_by={'acquire_type':lambda v: v =='I(Hmb) | set Vb' or v == 'I(Vb) | set Hmb', 'mode':lambda v: v =='Standard'})
    keithley_compliance_voltage = FloatParameter('Compliance voltage', units='V', default=1,group_by={'acquire_type': lambda v: v =='V(Hmb) |set Ib' or v == 'V(Ib) | set Hmb', 'mode':lambda v: v =='Standard'})
    keithley_current_bias = FloatParameter('Current bias', units='A', default=0, group_by={'acquire_type':'V(Hmb) |set Ib', 'mode':lambda v: v =='Standard'})
    keithley_voltage_bias = FloatParameter('Volage bias', units='V', default=0.1, group_by={'acquire_type':'I(Hmb) | set Vb', 'mode':lambda v: v =='Standard' or v == 'Fast Resistance'})
    agilent_adress = Parameter("Agilent E3648A adress", default="COM2",group_by={'field_device':lambda v: v =='Agilent E3648A'} )
    field_device = ListParameter("Field device", choises = ["DAQ", "Agilent E3648A"])
    field_bias = FloatParameter('Field bias', units='Oe', default=10, group_by={'acquire_type':lambda v: v =='I(Vb) | set Hmb' or v == 'V(Ib) | set Hmb', 'mode':lambda v: v =='Standard'})
    coil = ListParameter("Coil",  choices=["Large", "Small"], group_by='mode', group_condition=lambda v: v =='Standard')
    start = FloatParameter("Start", group_by='mode', group_condition=lambda v: v =='Standard')
    stop = FloatParameter("Stop", group_by='mode', group_condition=lambda v: v =='Standard')
    no_points = IntegerParameter("No Points", group_by='mode', group_condition=lambda v: v =='Standard')
    reverse_field = BooleanParameter("Reverse field", default=False, group_by='mode', group_condition=lambda v: v =='Standard')
    delay = FloatParameter("Delay", units = "ms", default = 1000, group_by='mode', group_condition=lambda v: v =='Standard')
    sample_name = Parameter("Sample Name", default="sample name", group_by='mode', group_condition=lambda v: v =='Standard')
 
    DATA_COLUMNS = ['Voltage (V)',  'Current (A)', 'Resistance (Ohm)', 'dX/dH', 'dR/dH', 'diff_I', 'diff_V', 'X field (Oe)', 'Y field (Oe)', 'Z field (Oe)','Field set (Oe)'] #data columns

    path_file = SaveFilePath() 
   
    
    ################ STARTUP ##################3
    def startup(self):
        if self.mode == 'Standard':
            log.info("Finding instruments...")
            sleep(0.1)
            log.info("Finded: {}".format(self.finded_instruments))
            
            
        ### Init field device 
            if self.field_device == "DAQ":
                log.info('Start config DAQ') 
                try:
                    from hardware.daq import DAQ
                    self.field = DAQ("6124/ao0")
                    log.info("Config DAQ done")
                except:
                    log.error("Config DAQ failed")
                try:
                    if self.reverse_field == True: 
                        self.vector_to = np.linspace(self.start, self.stop,self.no_points)
                        self.vector_rev = self.vector_to[::-1]
                        self.vector = np.append(self.vector_to[0:-1], self.vector_rev)
                    else: 
                        self.vector = np.linspace(self.start, self.stop,self.no_points)
                except:
                    log.error("Vector set failed")
            else: 
                log.info('Start config Agilent E3648A')
                ##Bias field:
                try:
                    from hardware.keisight_e3600a import E3600a
                    self.field = E3600a(self.field_adress) #connction to field controller
                    self.field.remote()
                    sleep(1)
                except:
                    log.error("Could not connect to field controller")
            


            
            
            ############## KEITHLEY CONFIG ###############
            log.info("Start config Keithley")
            try:
                self.keithley = Keithley2400(self.keithley_adress)
                if self.acquire_type == 'I(Hmb) | set Vb': 
                    self.keithley.apply_voltage()
                    self.keithley.source_voltage_range = 20
                    self.keithley.compliance_current = self.keithley_compliance_current
                    self.keithley.source_voltage = self.keithley_voltage_bias             # Sets the source current to 0 mA
                    self.keithley.enable_source()                # Enables the source output
                    self.keithley.measure_current()  
                elif self.acquire_type == 'V(Hmb) |set Ib': 
                    self.keithley.apply_current()
                    self.keithley.source_current_range = 0.1
                    self.keithley.compliance_voltage = self.keithley_compliance_voltage
                    self.keithley.source_current= self.keithley_current_bias            # Sets the source current to 0 mA
                    self.keithley.enable_source()                # Enables the source output
                    self.keithley.measure_voltage()         
                elif self.acquire_type == 'I(Vb) | set Hmb': 
                    self.keithley.apply_voltage()
                    self.keithley.source_voltage_range = 20
                    self.keithley.compliance_current = self.keithley_compliance_current
                    self.keithley.source_voltage =  0         # Sets the source current to 0 mA
                    self.keithley.enable_source()                # Enables the source output
                    self.keithley.measure_current()
                    if self.coil == "Large":
                        self.field_const = 5
                    else:
                        self.field_const = 10

                    
                    self.set_field = self.field.set_field(self.field_bias/self.field_const)
                elif self.acquire_type == 'V(Ib) | set Hmb': 
                    self.keithley.apply_current()
                    self.keithley.source_current_range = 0.1
                    self.keithley.compliance_voltage = self.keithley_compliance_voltage
                    self.keithley.source_current=  0         # Sets the source current to 0 mA
                    self.keithley.enable_source()                # Enables the source output
                    self.keithley.measure_voltage()
                    if self.coil == "Large":
                        self.field_const = 5
                    else:
                        self.field_const = 10 
                    self.set_field = self.field.set_field(self.field_bias/self.field_const)
                log.info("Config Keithley done")

            except:
                log.error("Config Keithley failed")

        
            
            ####### Config FieldSensor ######## 
            log.info("Config Field Sensor")
            try:
                self.field_sensor = FieldSensor(self.field_sensor_adress)
                self.field_sensor.read_field_init()
                log.info("Config FieldSensor done")
            except:
                log.error("Config FieldSensor failed")
                self.field_sensor = DummyFieldSensor()
                log.info("Use DummyFieldSensor")

        elif self.mode == "Fast Resistance": 
            
            ############## KEITHLEY CONFIG ###############
           
            try:
                self.keithley = Keithley2400(self.keithley_adress)
                self.keithley.apply_voltage()
                self.keithley.source_voltage_range = 1
                self.keithley.compliance_current = 0.1
                self.keithley.source_voltage = self.keithley_voltage_bias             # Sets the source current to 0 mA
                self.keithley.enable_source()                # Enables the source output
                self.keithley.measure_resistance()  

            except:
                log.error("Config Keithley failed")

    ##### PROCEDURE ######
    def execute(self):
        diff = ComputeDiff()
        res = ComputerResistance()
        tmp_voltage = []
        tmp_current = []
        tmp_field_x = []
        tmp_field_y = []
        tmp_field_z = []
        tmp_resistance = []
        tmp_field_set = []
        tmp_diff_x = []
        tmp_diff_R = []
        tmp_diff_I = []
        tmp_diff_V = []

        if self.mode == "Standard":
            if self.acquire_type == 'I(Hmb) | set Vb':
                log.info("Starting to sweep through field")
                if self.coil == "Large":
                    self.field_const = 5
                else:
                    self.field_const = 10 
                w = 0
                for i in self.vector:
                    self.field.set_field(i/self.field_const)
                    tmp_field_set.append(i)
                    sleep(self.delay*0.001)
                    self.tmp_field = self.field_sensor.read_field()
                    tmp_field_x.append(self.tmp_field[0])
                    tmp_field_y.append(self.tmp_field[1])
                    tmp_field_z.append(self.tmp_field[2])
                    sleep(self.delay*0.001)
                    self.tmp_current = self.keithley.current
                    tmp_current.append(self.tmp_current)
                    tmp_voltage.append(self.keithley_voltage_bias)
                    tmp_resistance.append(res.resistance(self.keithley_voltage_bias, self.tmp_current))
                    self.emit('progress', 100 * w / len(self.vector))
                    w = w + 1
                
                tmp_diff_x = diff.diff(tmp_current, tmp_field_set)
                tmp_diff_R = diff.diff(tmp_resistance, tmp_field_set)
                tmp_diff_I = diff.diffIV(tmp_current)
                tmp_diff_V = diff.diffIV(tmp_voltage)

                
                for k in range(len(tmp_field_set)):
                    data = {
                        'Voltage (V)':  tmp_voltage[k],
                        'Current (A)':  tmp_current[k],
                        'Resistance (Ohm)': tmp_resistance[k],
                        'X field (Oe)': tmp_field_x[k],
                        'Y field (Oe)': tmp_field_y[k],
                        'Z field (Oe)': tmp_field_z[k],
                        'Field set (Oe)': tmp_field_set[k],
                        'dX/dH': tmp_diff_x[k] if k < len(tmp_diff_x) else np.nan,
                        'dR/dH': tmp_diff_R[k] if k < len(tmp_diff_R) else np.nan,
                        'diff_I': tmp_diff_I[k] if k < len(tmp_diff_I) else np.nan,
                        'diff_V': tmp_diff_V[k] if k < len(tmp_diff_V) else np.nan

                        }
                        
                    self.emit('results', data) 



            elif self.acquire_type == 'V(Hmb) |set Ib':
                if self.coil == "Large":
                        self.field_const = 5
                else:
                        self.field_const = 10 
                w = 0
                log.info("Starting to sweep through field")
                for i in self.vector:
                    self.set_field = self.field.set_field(i/self.field_const)
                    tmp_field_set.append(i)
                    sleep(self.delay*0.001)
                    self.tmp_field = self.field_sensor.read_field()
                    tmp_field_x.append(self.tmp_field[0])
                    tmp_field_y.append(self.tmp_field[1])
                    tmp_field_z.append(self.tmp_field[2])
                    sleep(self.delay*0.001)
                    self.tmp_volatege = self.keithley.voltage
                    tmp_current.append(self.keithley_current_bias)
                    tmp_voltage.append(self.tmp_volatege)
                    tmp_resistance.append(res.resistance(self.tmp_volatege, self.keithley_current_bias))
                    self.emit('progress', 100 * w / len(self.vector))
                    w = w + 1
                
                tmp_diff_x = diff.diff(tmp_voltage, tmp_field_set)
                tmp_diff_R = diff.diff(tmp_resistance, tmp_field_set)
                tmp_diff_I = diff.diffIV(tmp_current)
                tmp_diff_V = diff.diffIV(tmp_voltage)



                for k in range(len(tmp_field_set)):
                    data = {
                        'Voltage (V)':  tmp_voltage[k],
                        'Current (A)':  tmp_current[k],
                        'Resistance (Ohm)': tmp_resistance[k],
                        'X field (Oe)': tmp_field_x[k],
                        'Y field (Oe)': tmp_field_y[k],
                        'Z field (Oe)': tmp_field_z[k],
                        'Field set (Oe)': tmp_field_set[k],
                        'dX/dH': tmp_diff_x[k] if k < len(tmp_diff_x) else np.nan,
                        'dR/dH': tmp_diff_R[k] if k < len(tmp_diff_R) else np.nan,
                        'diff_I': tmp_diff_I[k] if k < len(tmp_diff_I) else np.nan,
                        'diff_V': tmp_diff_V[k] if k < len(tmp_diff_V) else np.nan

                        }
                        
                    self.emit('results', data) 
                    
            elif self.acquire_type == 'I(Vb) | set Hmb':
                log.info("Starting to sweep through voltage")
                w = 0


                for i in self.vector:
                    tmp_field_set.append(self.field_bias)
                    self.keithley.source_voltage =  i
                    sleep(self.delay*0.001)
                    self.tmp_current = self.keithley.current
                    sleep(self.delay*0.001)
                    self.tmp_field = self.field_sensor.read_field()
                    tmp_field_x.append(self.tmp_field[0])
                    tmp_field_y.append(self.tmp_field[1])
                    tmp_field_z.append(self.tmp_field[2])
                    tmp_current.append(self.tmp_current)
                    tmp_voltage.append(i)
                    tmp_resistance.append(res.resistance(i, self.tmp_current))
                    self.emit('progress', 100 * w / len(self.vector))
                    w = w + 1
                
                tmp_diff_x = diff.diff(tmp_current, tmp_field_set)
                tmp_diff_R = diff.diff(tmp_resistance, tmp_field_set)
                tmp_diff_I = diff.diffIV(tmp_current)
                tmp_diff_V = diff.diffIV(tmp_voltage)




                for k in range(len(tmp_field_set)):
                    data = {
                            'Voltage (V)':  tmp_voltage[k],
                            'Current (A)':  tmp_current[k],
                            'Resistance (Ohm)': tmp_resistance[k],
                            'X field (Oe)': tmp_field_x[k],
                            'Y field (Oe)': tmp_field_y[k],
                            'Z field (Oe)': tmp_field_z[k],
                            'Field set (Oe)': tmp_field_set[k],
                            'dX/dH': tmp_diff_x[k] if k < len(tmp_diff_x) else np.nan,
                            'dR/dH': tmp_diff_R[k] if k < len(tmp_diff_R) else np.nan,
                            'diff_I': tmp_diff_I[k] if k < len(tmp_diff_I) else np.nan,
                            'diff_V': tmp_diff_V[k] if k < len(tmp_diff_V) else np.nan

                            }
                    
                    self.emit('results', data) 
                
            elif self.acquire_type == 'V(Ib) | set Hmb':
                log.info("Starting to sweep through current")
                w = 0
                for i in self.vector:
                    tmp_field_set.append(self.field_bias)
                    self.keithley.source_current =  i
                    sleep(self.delay*0.001)
                    self.tmp_volatage = self.keithley.voltage
                    sleep(self.delay*0.001)
                    self.tmp_field = self.field_sensor.read_field()
                    tmp_field_x.append(self.tmp_field[0])
                    tmp_field_y.append(self.tmp_field[1])
                    tmp_field_z.append(self.tmp_field[2])
                    tmp_current.append(i)
                    tmp_voltage.append(self.tmp_volatage)
                    tmp_resistance.append(res.resistance(tmp_voltage, tmp_current))
                    self.emit('progress', 100 * w / len(self.vector))
                    w = w + 1
                
                tmp_diff_x = diff.diff(tmp_voltage, tmp_field_set)
                tmp_diff_R = diff.diff(tmp_resistance, tmp_field_set)
                tmp_diff_I = diff.diffIV(tmp_current)
                tmp_diff_V = diff.diffIV(tmp_voltage)





                for k in range(len(tmp_field_set)):
                    data = {
                            'Voltage (V)':  tmp_voltage[k],
                            'Current (A)':  tmp_current[k],
                            'Resistance (Ohm)': tmp_resistance[k],
                            'X field (Oe)': tmp_field_x[k],
                            'Y field (Oe)': tmp_field_y[k],
                            'Z field (Oe)': tmp_field_z[k],
                            'Field set (Oe)': tmp_field_set[k],
                            'dX/dH': tmp_diff_x[k] if k < len(tmp_diff_x) else np.nan,
                            'dR/dH': tmp_diff_R[k] if k < len(tmp_diff_R) else np.nan,
                            'diff_I': tmp_diff_I[k] if k < len(tmp_diff_I) else np.nan,
                            'diff_V': tmp_diff_V[k] if k < len(tmp_diff_V) else np.nan

                            }
                    
                    self.emit('results', data) 
        elif self.mode == "Fast Resistance":
            self.tmp_resistance = self.keithley.resistance
            log.info(self.tmp_resistance)
            # self.emit('results',  data = {
            #             'Voltage (V)':  0,
            #             'Current (A)':  0,
            #             'X field (Oe)': 0,
            #             'Y field (Oe)': 0,
            #             'Z field (Oe)': 0,
            #             'Field set (Oe)': 0,
            #             })

    def shutdown(self):

        if MainWindow.last == True or IVTransfer.licznik == MainWindow.wynik:
            if self.mode != "Fast Resistance":
                if self.field_device == "DAQ":
                    self.field.shutdown()
                else: 
                    self.field.shutdown(self.field_bias/self.field_const)
            sleep(0.2)
            self.keithley.shutdown()
            print("keithley shutdown done")
            IVTransfer.licznik = 0
        else:
            self.keithley.shutdown()
            print("keithley shutdown done")
            print("go next loop...")
        IVTransfer.licznik += 1
        print(IVTransfer.licznik)
        

class MainWindow(ManagedWindow):
    last = False
    wynik = 0
    wynik_list = []
    def __init__(self):
        super().__init__(
            procedure_class= IVTransfer,
            inputs=['mode','sample_name','coil','acquire_type','keithley_adress','field_sensor_adress', 'keithley_compliance_current', 'keithley_compliance_voltage',
            'keithley_current_bias', 'keithley_voltage_bias', 'field_device', 'field_bias', 'agilent_adress', 'delay', 'start', 'stop', 'no_points', 'reverse_field'],
            displays=['sample_name', 'acquire_type', 'field_bias', 'keithley_current_bias', 'keithley_voltage_bias'],
            x_axis='Current (A)',
            y_axis='Voltage (V)',
            directory_input=True,  
            sequencer=True,                                      
            sequencer_inputs=['field_bias', 'keithley_current_bias', 'keithley_voltage_bias'],
            inputs_in_scrollarea=True,
            
        )
        self.setWindowTitle('IV Measurement System v.0.95')
        self.directory = self.procedure_class.path_file.ReadFile()
        

    def queue(self, procedure=None):
        directory = self.directory  # Change this to the desired directory
        self.procedure_class.path_file.WriteFile(directory)
        
        if procedure is None:
            procedure = self.make_procedure()
       
        name_of_file = procedure.sample_name
        filename = unique_name(directory, prefix="{}_".format(name_of_file))
        results = Results(procedure, filename)
        experiment = self.new_experiment(results)
        self.manager.queue(experiment)
        
        
        

        try:
            
            MainWindow.wynik =  procedure.seq
            MainWindow.wynik_list.append(procedure.seq)
            MainWindow.wynik = max(MainWindow.wynik_list)
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
