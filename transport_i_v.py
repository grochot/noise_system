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
from logic.vector import Vector
from hardware.agilent_34410a import Agilent34410A
from modules.compute_diff import ComputeDiff
from modules.computer_resisrance import ComputerResistance

from hardware.field_sensor_noise_new import FieldSensor
from hardware.dummy_field_sensor_iv import DummyFieldSensor

log = logging.getLogger(__name__) 
log.addHandler(logging.NullHandler()) 



class IVTransfer(Procedure):
    licznik = 1 # licznik
    find_instruments = FindInstrument()
    finded_instruments = find_instruments.show_instrument() 
    print(finded_instruments)
    ################# PARAMETERS ###################
    mode = ListParameter("Mode",  default='HDCMode', choices=['HDCMode', 'Fast Resistance'])
    agilent = BooleanParameter("Agilent", default=False, group_by='mode', group_condition=lambda v: v =='HDCMode')
    agilent34401a_adress = Parameter("Agilent34401a adress", default="GPIB1::22::INSTR", group_by='agilent', group_condition=lambda v: v ==True)
    acquire_type = ListParameter("Acquire type", choices = ['I(Hmb) | set Vb', 'V(Hmb) |set Ib', 'I(Vb) | set Hmb', 'V(Ib) | set Hmb'],group_by='mode', group_condition=lambda v: v =='HDCMode')
    keithley_adress = ListParameter("Keithley2400 adress", choices=["GPIB1::24::INSTR"])
    field_sensor_adress = Parameter("Field_sensor",  default="COM8",group_by='mode', group_condition=lambda v: v =='HDCMode' )
    #keithley_source_type = ListParameter("Source type", default = "Current", choices = ['Current', 'Voltage'])
    keithley_compliance_current = FloatParameter('Compliance current', units='A', default=0.1, group_by={'acquire_type':lambda v: v =='I(Hmb) | set Vb' or v == 'I(Vb) | set Hmb', 'mode':lambda v: v =='HDCMode'})
    keithley_compliance_voltage = FloatParameter('Compliance voltage', units='V', default=1,group_by={'acquire_type': lambda v: v =='V(Hmb) |set Ib' or v == 'V(Ib) | set Hmb', 'mode':lambda v: v =='HDCMode'})
    keithley_current_bias = FloatParameter('Current bias', units='A', default=0, group_by={'acquire_type':'V(Hmb) |set Ib', 'mode':lambda v: v =='HDCMode'})
    keithley_voltage_bias = FloatParameter('Volage bias', units='V', default=0.1, group_by={'acquire_type':'I(Hmb) | set Vb', 'mode':lambda v: v =='HDCMode' or v == 'Fast Resistance'})
    agilent_adress = Parameter("Agilent E3648A adress", default="COM9",group_by={'field_device':lambda v: v =='Agilent E3648A'} )
    field_device = ListParameter("Field device", choices = ["DAQ", "Agilent E3648A"], default = "DAQ")
    field_bias = FloatParameter('Field bias', units='Oe', default=10, group_by={'acquire_type':lambda v: v =='I(Vb) | set Hmb' or v == 'V(Ib) | set Hmb', 'mode':lambda v: v =='HDCMode'})
    coil = ListParameter("Coil",  choices=["Large", "Small"], group_by='mode', group_condition=lambda v: v =='HDCMode')
    vector_param = Parameter("Vector", group_by='mode', group_condition=lambda v: v =='HDCMode')
    # stop = FloatParameter("Stop", group_by='mode', group_condition=lambda v: v =='HDCMode')
    # no_points = IntegerParameter("No Points", group_by='mode', group_condition=lambda v: v =='HDCMode')
    reverse_field = BooleanParameter("Reverse field", default=False, group_by='mode', group_condition=lambda v: v =='HDCMode')
    delay = FloatParameter("Delay", units = "ms", default = 1000, group_by='mode', group_condition=lambda v: v =='HDCMode')
    sample_name = Parameter("Sample Name", default="sample name", group_by='mode', group_condition=lambda v: v =='HDCMode')
 
    DATA_COLUMNS = ['Voltage (V)',  'Current (A)', 'Resistance', 'dX/dH', 'dR/dH', 'diff_I', 'diff_V', 'X field (Oe)', 'Y field (Oe)', 'Z field (Oe)','Field set (Oe)'] #data columns

    path_file = SaveFilePath() 
   
    
    ################ STARTUP ##################3
    def startup(self):
        self.vector_obj = Vector()
        if self.mode == 'HDCMode':
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
                except Exception as e:
                    print(e)
                    log.error("Config DAQ failed")
                try:
                    if self.reverse_field == True: 
                        self.vector_to = self.vector_obj.generate_vector(self.vector_param)
                        self.vector_rev = self.vector_to[::-1]
                        vector = np.append(self.vector_to[0:-1], self.vector_rev)
                    else: 
                        self.vector = self.vector_obj.generate_vector(self.vector_param)
                except Exception as e:
                    print(e)
                    log.error("Vector set failed")
            else: 
                log.info('Start config Keisight E3648A')
                ##Bias field:
                try:
                    from hardware.keisight_e3600a import E3600a
                    self.field = E3600a(self.agilent_adress) #connction to field controller
                    self.field.remote()
                    sleep(1)
                except Exception as e:
                    print(e)
                    log.error("Config Keisight E3648A failed")
                try:
                    if self.reverse_field == True: 
                        self.vector_to = self.vector_obj.generate_vector(self.vector_param)
                        self.vector_rev = self.vector_to[::-1]
                        self.vector = np.append(self.vector_to[0:-1], self.vector_rev)
                    else: 
                        self.vector = self.vector_obj.generate_vector(self.vector_param)
                except Exception as e:
                    print(e)
                    log.error("Vector set failed")
            


            
            
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

            ####### Config Agilent 34410A ########
            if self.agilent == True: 
                log.info("Config Agilent 34410A")
                try:
                    self.agilent_34410 = Agilent34410A(self.agilent34401a_adress)
                    log.info("Config Agilent 34410A done")
                except:
                    log.error("Config Agilent 34410A failed")
                   
                   

        
################FAST RESISTANCE######################
        
        
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

#################################### PROCEDURE##############################################
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

        if self.mode == "HDCMode":
            if self.acquire_type == 'I(Hmb) | set Vb':
                log.info("Starting to sweep through field")
                if self.coil == "Large":
                    self.field_const = 5
                else:
                    self.field_const = 10 
                w = 0
                for i in self.vector:
                    self.last_value = i
                    self.field.set_field(i/self.field_const)
                    tmp_field_set.append(i)
                    sleep(self.delay*0.001)
                    self.tmp_field = self.field_sensor.read_field()
                    tmp_field_x.append(self.tmp_field[0])
                    tmp_field_y.append(self.tmp_field[1])
                    tmp_field_z.append(self.tmp_field[2])
                    sleep(self.delay*0.001)
                    if self.agilent == True:
                        tmp_current.append(self.agilent_34410.current_dc)
                    else:
                        self.tmp_current = self.keithley.current
                    tmp_current.append(self.tmp_current)
                    tmp_voltage.append(self.keithley_voltage_bias)
                    tmp_resistance.append(res.resistance(self.keithley_voltage_bias, self.tmp_current))
                    self.emit('progress', 100 * w / len(self.vector))
                    
                    if i == 0:
                        tmp_diff_x = np.nan #diff.diff(tmp_current, tmp_field_set)
                        tmp_diff_R = np.nan # diff.diff(tmp_resistance, tmp_field_set)
                        tmp_diff_I = np.nan #diff.diffIV(tmp_current)
                        tmp_diff_V = np.nan #diff.diffIV(tmp_voltage)
                    else: 
                        tmp_diff_x = diff.diff(tmp_current[w-1], tmp_current[w],tmp_field_set[w-1], tmp_field_set[w])
                        tmp_diff_R = diff.diff(tmp_resistance[w-1], tmp_resistance[w], tmp_field_set[w-1], tmp_field_set[w])
                        tmp_diff_I = diff.diffIV(tmp_current[w-1],tmp_current[w])
                        tmp_diff_V = diff.diffIV(tmp_voltage[w-1], tmp_voltage[w])
                    

                    data = {
                        'Voltage (V)':  tmp_voltage[w],
                        'Current (A)':  tmp_current[w],
                        'Resistance (Ohm)': tmp_resistance[w],
                        'X field (Oe)': tmp_field_x[w],
                        'Y field (Oe)': tmp_field_y[w],
                        'Z field (Oe)': tmp_field_z[w],
                        'Field set (Oe)': tmp_field_set[w],
                        'dX/dH': tmp_diff_x,
                        'dR/dH': tmp_diff_R,
                        'diff_I': tmp_diff_I,
                        'diff_V': tmp_diff_V,

                        }
                    w = w + 1
                    self.emit('results', data) 
               
                   



            elif self.acquire_type == 'V(Hmb) |set Ib':
                if self.coil == "Large":
                        self.field_const = 5
                else:
                        self.field_const = 10 
                w = 0
                log.info("Starting to sweep through field")
                for i in vector:
                    self.last_value = i
                    self.set_field = self.field.set_field(i/self.field_const)
                    tmp_field_set.append(i)
                    sleep(self.delay*0.001)
                    self.tmp_field = self.field_sensor.read_field()
                    tmp_field_x.append(self.tmp_field[0])
                    tmp_field_y.append(self.tmp_field[1])
                    tmp_field_z.append(self.tmp_field[2])
                    sleep(self.delay*0.001)
                    if self.agilent == True:
                        self.tmp_volatage = self.agilent_34410.voltage_dc
                    else:
                        self.tmp_volatege = self.keithley.voltage
                    tmp_current.append(self.keithley_current_bias)
                    tmp_voltage.append(self.tmp_volatege)
                    tmp_resistance.append(res.resistance(self.tmp_volatege, self.keithley_current_bias))
                    self.emit('progress', 100 * w / len(self.vector))
                    if i == 0:
                        tmp_diff_x = np.nan #diff.diff(tmp_current, tmp_field_set)
                        tmp_diff_R = np.nan # diff.diff(tmp_resistance, tmp_field_set)
                        tmp_diff_I = np.nan #diff.diffIV(tmp_current)
                        tmp_diff_V = np.nan #diff.diffIV(tmp_voltage)
                    else: 
                        tmp_diff_x = diff.diff(tmp_current[w-1], tmp_current[w],tmp_field_set[w-1], tmp_field_set[w])
                        tmp_diff_R = diff.diff(tmp_resistance[w-1], tmp_resistance[w], tmp_field_set[w-1], tmp_field_set[w])
                        tmp_diff_I = diff.diffIV(tmp_current[w-1],tmp_current[w])
                        tmp_diff_V = diff.diffIV(tmp_voltage[w-1], tmp_voltage[w])
                    

                    data = {
                        'Voltage (V)':  tmp_voltage[w],
                        'Current (A)':  tmp_current[w],
                        'Resistance (Ohm)': tmp_resistance[w],
                        'X field (Oe)': tmp_field_x[w],
                        'Y field (Oe)': tmp_field_y[w],
                        'Z field (Oe)': tmp_field_z[w],
                        'Field set (Oe)': tmp_field_set[w],
                        'dX/dH': tmp_diff_x,
                        'dR/dH': tmp_diff_R,
                        'diff_I': tmp_diff_I,
                        'diff_V': tmp_diff_V,

                        }
                    w = w + 1
                    self.emit('results', data) 
               
                    
            elif self.acquire_type == 'I(Vb) | set Hmb':
                log.info("Starting to sweep through voltage")
                w = 0


                for i in vector:
                    tmp_field_set.append(self.field_bias)
                    self.keithley.source_voltage =  i
                    sleep(self.delay*0.001)
                    if self.agilent == True:
                        self.tmp_current = self.agilent_34410.current_dc
                    else:
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
                    if i == 0:
                        tmp_diff_x = np.nan #diff.diff(tmp_current, tmp_field_set)
                        tmp_diff_R = np.nan # diff.diff(tmp_resistance, tmp_field_set)
                        tmp_diff_I = np.nan #diff.diffIV(tmp_current)
                        tmp_diff_V = np.nan #diff.diffIV(tmp_voltage)
                    else: 
                        tmp_diff_x = diff.diff(tmp_current[w-1], tmp_current[w],tmp_field_set[w-1], tmp_field_set[w])
                        tmp_diff_R = diff.diff(tmp_resistance[w-1], tmp_resistance[w], tmp_field_set[w-1], tmp_field_set[w])
                        tmp_diff_I = diff.diffIV(tmp_current[w-1],tmp_current[w])
                        tmp_diff_V = diff.diffIV(tmp_voltage[w-1], tmp_voltage[w])
                    

                    data = {
                        'Voltage (V)':  tmp_voltage[w],
                        'Current (A)':  tmp_current[w],
                        'Resistance (Ohm)': tmp_resistance[w],
                        'X field (Oe)': tmp_field_x[w],
                        'Y field (Oe)': tmp_field_y[w],
                        'Z field (Oe)': tmp_field_z[w],
                        'Field set (Oe)': tmp_field_set[w],
                        'dX/dH': tmp_diff_x,
                        'dR/dH': tmp_diff_R,
                        'diff_I': tmp_diff_I,
                        'diff_V': tmp_diff_V,

                        }
                    w = w + 1
                    self.emit('results', data) 
               
                
            elif self.acquire_type == 'V(Ib) | set Hmb':
                log.info("Starting to sweep through current")
                w = 0
                for i in vector:
                    tmp_field_set.append(self.field_bias)
                    self.keithley.source_current =  i
                    sleep(self.delay*0.001)
                    if self.agilent == True:
                        self.tmp_volatage = self.agilent_34410.voltage_dc
                    else:
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
                    if i == 0:
                        tmp_diff_x = np.nan #diff.diff(tmp_current, tmp_field_set)
                        tmp_diff_R = np.nan # diff.diff(tmp_resistance, tmp_field_set)
                        tmp_diff_I = np.nan #diff.diffIV(tmp_current)
                        tmp_diff_V = np.nan #diff.diffIV(tmp_voltage)
                    else: 
                        tmp_diff_x = diff.diff(tmp_current[w-1], tmp_current[w],tmp_field_set[w-1], tmp_field_set[w])
                        tmp_diff_R = diff.diff(tmp_resistance[w-1], tmp_resistance[w], tmp_field_set[w-1], tmp_field_set[w])
                        tmp_diff_I = diff.diffIV(tmp_current[w-1],tmp_current[w])
                        tmp_diff_V = diff.diffIV(tmp_voltage[w-1], tmp_voltage[w])
                    

                    data = {
                        'Voltage (V)':  tmp_voltage[w],
                        'Current (A)':  tmp_current[w],
                        'Resistance (Ohm)': tmp_resistance[w],
                        'X field (Oe)': tmp_field_x[w],
                        'Y field (Oe)': tmp_field_y[w],
                        'Z field (Oe)': tmp_field_z[w],
                        'Field set (Oe)': tmp_field_set[w],
                        'dX/dH': tmp_diff_x,
                        'dR/dH': tmp_diff_R,
                        'diff_I': tmp_diff_I,
                        'diff_V': tmp_diff_V,

                        }
                    w = w + 1
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
                    #self.field.shutdown()
                    pass
                else: 
                    if self.acquire_type == 'I(Hmb) | set Vb' or self.acquire_type == 'V(Hmb) |set Ib':         
                        self.field.shutdown(self.last_value/self.field_const)
                    else:
                        self.field.shutdown(self.field_bias/self.field_const)
            sleep(0.2)
            #self.keithley.shutdown()
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
            inputs=['mode','sample_name','vector_param','coil','acquire_type','keithley_adress','agilent','agilent34401a_adress','field_sensor_adress', 'keithley_compliance_current', 'keithley_compliance_voltage',
            'keithley_current_bias', 'keithley_voltage_bias', 'field_device', 'field_bias', 'agilent_adress', 'delay', 'reverse_field'],
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