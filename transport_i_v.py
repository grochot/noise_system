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
from logic.scope_rate import scope_rate

from pymeasure.display.Qt import QtGui
from pymeasure.display.Qt import QtWidgets
from pymeasure.display.windows import ManagedWindow
from pymeasure.display.windows import ManagedWindowBase
# from pymeasure.display.widgets import TableWidget, LogWidget, PlotWidget
#from pymeasure.display.windows.managed_dock_window import ManagedDockWindow
from pymeasure.experiment import (
    Procedure, FloatParameter, BooleanParameter, IntegerParameter, Parameter,ListParameter, Results, VectorParameter
)
from logic.unique_name import unique_name

from hardware.keithley2400 import Keithley2400
from logic.vector import Vector
from hardware.agilent_34410a import Agilent34410A
from modules.compute_diff import ComputeDiff
from modules.computer_resisrance import ComputerResistance
from modules.Lockin_calibration import LockinCalibration
from modules.Lockin_field import LockinField 
from modules.Lockin_frequency import LockinFrequency
from modules.Lockin_time import LockinTime
from logic.measure_field import measure_field
from hardware.field_sensor_noise_new import FieldSensor
from hardware.dummy_field_sensor_iv import DummyFieldSensor
from logic.save_parameters import SaveParameters


log = logging.getLogger(__name__) 
log.addHandler(logging.NullHandler()) 



class IVTransfer(Procedure):
    licznik = 1 # licznik
    find_instruments = FindInstrument()
    finded_instruments = find_instruments.show_instrument()
    save_parameter = SaveParameters()
    used_parameters_list=['mode','mode_lockin','sample_name','vector_param','lockin_vector','coil','coil_constant', 'acquire_type','keithley_adress','agilent','agilent34401a_adress','field_sensor_adress', 'keithley_compliance_current', 'keithley_compliance_voltage',
            'keithley_current_bias', 'keithley_voltage_bias', 'field_device', 'field_bias', 'agilent_adress', 'delay', 'reverse_field', 'lockin_adress','input_type','sigin_imp','sigin_autorange', 'sigin_ac','differential_signal', 'kepco', 'dc_field','bias_voltage', 'ac_field_amplitude', 'ac_field_frequency', 'sigin_range', 'lockin_frequency', 'avergaging_rate','scope_rate', 'scope_time', 'amplitude_vec']
    parameters_from_file = save_parameter.ReadFile()
    parameters = {}


#################################################################### PARAMETERS #####################################################################
    mode = ListParameter("Mode",  default = parameters_from_file["mode"], choices=['HDCMode', 'Fast Resistance', 'HDC-ACModeLockin', 'TimeMode'])
    mode_lockin = ListParameter("Lockin mode", default = parameters_from_file["mode_lockin"],  choices = ['Sweep field', 'Sweep frequency'],group_by='mode', group_condition=lambda v: v =='HDC-ACModeLockin')
    agilent = BooleanParameter("Agilent", default = parameters_from_file["agilent"], group_by='mode', group_condition=lambda v: v =='HDCMode')
    agilent34401a_adress = ListParameter("Agilent34401a adress", default = parameters_from_file["agilent34401a_adress"] if parameters_from_file["agilent34401a_adress"] in finded_instruments else 'None', choices=finded_instruments, group_by='agilent', group_condition=lambda v: v ==True)
    acquire_type = ListParameter("Acquisition type", default = parameters_from_file["acquire_type"], choices = ['I(Hdc) | set Vb', 'V(Hdc) |set Ib', 'I(Vb) | set Hdc', 'V(Ib) | set Hdc'],group_by='mode', group_condition=lambda v: v =='HDCMode')
    keithley_adress = ListParameter("Keithley2400 adress", default = parameters_from_file["keithley_adress"] if parameters_from_file["keithley_adress"] in finded_instruments else 'None', choices=finded_instruments, group_by='mode', group_condition=lambda v: v =='HDCMode')
    field_sensor_adress = Parameter("Field_sensor",  default = parameters_from_file["field_sensor_adress"]) 
    #keithley_source_type = ListParameter("Source type", default = "Current", choices = ['Current', 'Voltage'])
    keithley_compliance_current = FloatParameter('Compliance current', units='A', default = parameters_from_file["keithley_compliance_current"], group_by={'acquire_type':lambda v: v =='I(Hdc) | set Vb' or v == 'I(Vb) | set Hdc', 'mode':lambda v: v =='HDCMode'})
    keithley_compliance_voltage = FloatParameter('Compliance voltage', units='V', default = parameters_from_file["keithley_compliance_voltage"],group_by={'acquire_type': lambda v: v =='V(Hdc) |set Ib' or v == 'V(Ib) | set Hdc', 'mode':lambda v: v =='HDCMode'})
    keithley_current_bias = FloatParameter('Current bias', units='A', default = parameters_from_file["keithley_current_bias"], group_by={'acquire_type':'V(Hdc) |set Ib', 'mode':lambda v: v =='HDCMode'})
    keithley_voltage_bias = FloatParameter('Volage bias', units='V', default = parameters_from_file["keithley_voltage_bias"], group_by={'acquire_type':'I(Hdc) | set Vb', 'mode':lambda v: v =='HDCMode' or v == 'Fast Resistance'})
    agilent_adress = ListParameter("Agilent E3648A adress", default = parameters_from_file["agilent_adress"] if parameters_from_file["agilent_adress"] in finded_instruments else 'None' , choices=finded_instruments, group_by={'field_device':lambda v: v =='Agilent E3648A'} )
    field_device = ListParameter("Field device", choices = ["DAQ", "Agilent E3648A"], default = "DAQ", group_by='mode', group_condition=lambda v: v =='HDCMode')
    field_bias = FloatParameter('Field bias', units='Oe', default = parameters_from_file["field_bias"], group_by={'acquire_type':lambda v: v =='I(Vb) | set Hdc' or v == 'V(Ib) | set Hdc', 'mode':lambda v: v =='HDCMode'})
    coil = ListParameter("Coil", default = parameters_from_file["coil"],  choices=["Large", "Small"], group_by='mode', group_condition=lambda v: v =='HDCMode')
    vector_param = Parameter("Vector",  group_by='mode', default = parameters_from_file["vector_param"], group_condition=lambda v: v =='HDCMode')
    # stop = FloatParameter("Stop", group_by='mode', group_condition=lambda v: v =='HDCMode')
    # no_points = IntegerParameter("No Points", group_by='mode', group_condition=lambda v: v =='HDCMode')
    reverse_field = BooleanParameter("Reverse field", default = parameters_from_file["reverse_field"], group_by='mode', group_condition=lambda v: v =='HDCMode')
    delay = FloatParameter("Delay", units = "ms", default = parameters_from_file["delay"], group_by='mode', group_condition=lambda v: v =='HDCMode')
    sample_name = Parameter("Sample Name", default = parameters_from_file["sample_name"])
    bias_voltage = FloatParameter('Bias Voltage', units='mV', default = parameters_from_file["bias_voltage"],group_by='mode', group_condition=lambda v: v =='HDC-ACModeLockin' or v =="TimeMode")


#Lockin mode: 
    lockin_adress = Parameter("Lockin adress", default = parameters_from_file["lockin_adress"], group_by='mode', group_condition=lambda v: v =='HDC-ACModeLockin' or v == "TimeMode")
    input_type = ListParameter("Input type", default = parameters_from_file["input_type"], choices=["Voltage input", "Current input"], group_by='mode', group_condition=lambda v: v=="HDC-ACModeLockin" or v == "TimeMode")
    dc_field = FloatParameter('DC Field', units='Oe', default = parameters_from_file["dc_field"],group_by='mode', group_condition=lambda v: v =='HDC-ACModeLockin' or v == "TimeMode")
    ac_field_amplitude = FloatParameter('AC Field Amplitude', units='Oe', default = parameters_from_file["ac_field_amplitude"],group_by=['mode'], group_condition=lambda v: v =='HDC-ACModeLockin' or v == "TimeMode")   
    ac_field_frequency = FloatParameter('AC Field Frequency', units='Hz', default = parameters_from_file["ac_field_frequency"],group_by=['mode'], group_condition=lambda v: v =='HDC-ACModeLockin'or v == "TimeMode")
    differential_signal = BooleanParameter('Differential voltage input', default = parameters_from_file["differential_signal"], group_by=['mode','input_type'], group_condition=[lambda v: v =='HDC-ACModeLockin'or v == "TimeMode", lambda v: v == "Voltage input"])
    lockin_frequency = FloatParameter('Lockin frequency', units='Hz', default = parameters_from_file["lockin_frequency"],group_by=['mode', 'mode_lockin'], group_condition=[lambda v: v =='HDC-ACModeLockin'or v == "TimeMode",'Sweep field'])
    avergaging_rate = IntegerParameter("Avergaging rate", default = parameters_from_file["avergaging_rate"],group_by='mode', group_condition=lambda v: v =='HDC-ACModeLockin'or v == "TimeMode" )
    scope_rate = ListParameter("Scope Rate", choices = ["60MHz", "30MHz", "15MHz", "7.5MHz", "3.75MHz", "1.88MHz", "938kHz", "469kHz", "234kHz", "117kHz", "58.6kHz", "29.3kHz", "14.6kHz", "7.32kHz", "3.66kHz", "1.83kHz", "916Hz"], default = parameters_from_file["scope_rate"], group_by='mode', group_condition=lambda v: v =='TimeMode' )
    scope_time = FloatParameter("Scope Length [pts] (max 16384)",  default = parameters_from_file["scope_time"], group_by='mode', group_condition=lambda v: v =='TimeMode' )
    kepco = BooleanParameter("Kepco?", default = parameters_from_file["kepco"], group_by='mode', group_condition=lambda v: v =='HDC-ACModeLockin'or v == "TimeMode")
    coil_constant = FloatParameter("Coil constant",units='Oe/A', group_by='mode', default = parameters_from_file["coil_constant"], group_condition=lambda v: v =='HDC-ACModeLockin'or v == "TimeMode")
    amplitude_vec = BooleanParameter("Sweep field", default = parameters_from_file["amplitude_vec"], group_by=['mode', 'mode_lockin'], group_condition=[lambda v: v =='HDC-ACModeLockin','Sweep field'])
    
    sigin_imp = BooleanParameter("50 Ohm", default = parameters_from_file["sigin_imp"], group_by=['mode','input_type'], group_condition=[lambda v: v =='HDC-ACModeLockin'or v == "TimeMode", lambda v: v == "Voltage input"])
    sigin_ac = BooleanParameter("AC ON", default = parameters_from_file["sigin_ac"], group_by=['mode','input_type'], group_condition=[lambda v: v =='HDC-ACModeLockin'or v == "TimeMode", lambda v: v == "Voltage input"])
   
    sigin_range = FloatParameter("SigIn Range", units = 'V', default = parameters_from_file["sigin_range"], decimals=9, step= None ,group_by=['mode'], group_condition=[lambda v: v =='HDC-ACModeLockin' or v == "TimeMode"] )
    sigin_autorange = BooleanParameter("Autorange ON", default = parameters_from_file["sigin_autorange"], group_by=['mode'], group_condition=[lambda v: v =='HDC-ACModeLockin' or v == "TimeMode"])
    lockin_vector = Parameter("Vector", default = parameters_from_file["lockin_vector"], group_by='mode', group_condition=lambda v: v =='HDC-ACModeLockin')
##############################################################################################################################################################


    DEBUG = 1
    DATA_COLUMNS = ['time (s)','V (V)', 'f (Hz)','AHac (Oe)', 'Vsense (V)','Vbias (V)','I (A)','Phase', 'R (ohm)', 'dI/dH', 'dR/dH', 'dI', 'dV', 'X field (Oe)', 'Y field (Oe)', 'Z field (Oe)','Hset (Oe)', 'G', 'I/Phase', 'V/Phase', 'I/Ax','dG', "dR", 'dI/dV', 'dV/dI', 'dG/dH', 'NdR', 'NdG', 'NdI', 'HdIS', 'HdVS', 'dV/dH', 'SPdI', 'HdIS', 'HdRS', 'HdGS', "G(t)", "R(t)"] #data columns

    path_file = SaveFilePath() 
    
    def value_function(self,lista,iter):
        try:
            wynik = lista[iter]
            return wynik
        except:
            return np.nan
    
    ################ STARTUP ##################3
    def startup(self):
        for i in self.used_parameters_list:
            self.param = eval("self."+i)
            self.parameters[i] = self.param
        
        self.save_parameter.WriteFile(self.parameters)
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
                        self.vector = np.append(self.vector_to[0:-1], self.vector_rev)
                    else: 
                        self.vector = self.vector_obj.generate_vector(self.vector_param)
                except Exception as e:
                    print(e)
                    log.error("Vector set failed")
                print(self.vector)
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
                if self.acquire_type == 'I(Hdc) | set Vb': 
                    self.keithley.apply_voltage()
                    self.keithley.source_voltage_range = 20
                    self.keithley.compliance_current = self.keithley_compliance_current
                    self.keithley.source_voltage = self.keithley_voltage_bias             # Sets the source current to 0 mA
                    self.keithley.enable_source()                # Enables the source output
                    self.keithley.measure_current()  
                elif self.acquire_type == 'V(Hdc) |set Ib': 
                    self.keithley.apply_current()
                    self.keithley.source_current_range = 0.1
                    self.keithley.compliance_voltage = self.keithley_compliance_voltage
                    self.keithley.source_current= self.keithley_current_bias            # Sets the source current to 0 mA
                    self.keithley.enable_source()                # Enables the source output
                    self.keithley.measure_voltage()         
                elif self.acquire_type == 'I(Vb) | set Hdc': 
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
                elif self.acquire_type == 'V(Ib) | set Hdc': 
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
                    if self.coil == "Large":
                        self.field_const = 5
                    else:
                        self.field_const = 10
                    if self.acquire_type == 'I(Vb) | set Hdc': 
                        self.set_field = self.field.set_field(self.field_bias/self.field_const)
                    elif self.acquire_type == 'V(Ib) | set Hdc':
                        self.set_field = self.field.set_field(self.field_bias/self.field_const)
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

################ LOCKIN MODE ######################
        elif self.mode =="HDC-ACModeLockin":

            if self.mode_lockin == "Sweep field":

                
                try:
                    self.field_sensor = FieldSensor(self.field_sensor_adress)
                    self.field_sensor.read_field_init()
                    log.info("Config FieldSensor done")
                except:
                    log.error("Config FieldSensor failed")
                    self.field_sensor = DummyFieldSensor()
                    log.info("Use DummyFieldSensor")
                try:
                    self.lockin = LockinField(self.lockin_adress)
                    if self.input_type == "Current input":
                        self.lockin.init(1, False, float(self.sigin_range), self.sigin_imp, self.sigin_ac, self.sigin_autorange) 
                    else: 
                        if self.differential_signal == True:
                            self.lockin.init(0, True, float(self.sigin_range), self.sigin_imp, self.sigin_ac, self.sigin_autorange)
                        else:
                            self.lockin.init(0, False, float(self.sigin_range), self.sigin_imp, self.sigin_ac, self.sigin_autorange)
                    log.info("Lockin initialized")
                except: 
                    log.error("Lockin init failed")
                self.vector = self.vector_obj.generate_vector(self.lockin_vector)
                
                self.lockin.set_constant_vbias(self.bias_voltage)
                sleep(1)
                

                
            elif self.mode_lockin == "Sweep frequency": 
                 
                try:
                    self.field_sensor = FieldSensor(self.field_sensor_adress)
                    self.field_sensor.read_field_init()
                    log.info("Config FieldSensor done")
                except:
                    log.error("Config FieldSensor failed")
                    self.field_sensor = DummyFieldSensor()
                    log.info("Use DummyFieldSensor")
                
                self.lockin = LockinFrequency(self.lockin_adress)
                if self.input_type == "Current input":
                        self.lockin.init(1, False, float(self.sigin_range), self.sigin_imp, self.sigin_ac, self.sigin_autorange) 
                else: 
                        if self.differential_signal == True:
                            self.lockin.init(0, True, float(self.sigin_range), self.sigin_imp, self.sigin_ac, self.sigin_autorange)
                        else:
                            self.lockin.init(0, False, float(self.sigin_range), self.sigin_imp, self.sigin_ac, self.sigin_autorange)
                self.vector = self.vector_obj.generate_vector(self.lockin_vector)
                self.lockin.set_constant_field(self.dc_field/0.6)
                sleep(1)
                self.lockin.set_constant_vbias(self.bias_voltage)
                sleep(1)
               
            elif self.mode == "Lockin calibration":
                pass
########################### TIME MODE ###########################3

        elif self.mode == "TimeMode":
            self.rate_index = scope_rate(self.scope_rate)
            ####### Field sensor ########
            try:
                self.field_sensor = FieldSensor(self.field_sensor_adress)
                self.field_sensor.read_field_init()
                log.info("Config FieldSensor done")
            except:
                log.error("Config FieldSensor failed.")
                self.field_sensor = DummyFieldSensor()
                log.info("Use DummyFieldSensor")
            ########### Lockin #############
            try:
                self.lockin = LockinTime(self.lockin_adress)
                if self.input_type == "Current input":
                    self.lockin.init_lockin(1, False, float(self.sigin_range), self.sigin_imp, self.sigin_ac, self.sigin_autorange)
                    self.lockin.init_scope(self.avergaging_rate, 1, self.rate_index, self.scope_time)
                else: 
                    if self.differential_signal == True:
                        self.lockin.init_lockin(0, True, float(self.sigin_range), self.sigin_imp, self.sigin_ac, self.sigin_autorange)
                    else:
                        self.lockin.init_lockin(0, False, float(self.sigin_range), self.sigin_imp, self.sigin_ac, self.sigin_autorange)
                    self.lockin.init_scope(self.avergaging_rate, 0, self.rate_index, self.scope_time)

                log.info("Lockin initialized")
            except Exception as a: 
                log.error(a)
                log.error("Lockin init failed")
            
            self.lockin.set_constant_vbias(self.bias_voltage)
            sleep(1)
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
        tmp_conductance =[]
        tmp_field_set = []
        tmp_diff_x = []
        tmp_dR = []
        tmp_dI = []
        tmp_dV = []
        tmp_dI_dH = []
        tmp_dV_dH = []
        tmp_dR_dH = []
        tmp_dG_dH = []
        tmp_NdI = []
        tmp_SPdI = []
        tmp_HdIS = []
        tmp_HdR = []
        tmp_HdG = [] 
        tmp_dR = [] 
        tmp_dG = [] 
        tmp_NdR = []
        tmp_NdG = [] 
        tmp_HdRS = [] 
        tmp_HdGS = []     
        tmp_NdV = []
        tmp_SPdV = []
        tmp_HdVS = []
        tmp_dI_dV = []
        tmp_dV_dI = []

        if self.mode == "HDCMode":
            if self.acquire_type == 'I(Hdc) | set Vb':
                log.info("Starting to sweep through field")
                if self.coil == "Large":
                    self.field_const = 5
                else:
                    self.field_const = 10 
                w = 0
                for i in self.vector:
                    self.last_value = i
                    self.field.set_field(i/self.field_const)
                    tmp_field_set.append(i)   # surowe pole 
                    sleep(self.delay*0.001)
                    self.tmp_field = self.field_sensor.read_field()
                    tmp_field_x.append(self.tmp_field[0])
                    tmp_field_y.append(self.tmp_field[1])
                    tmp_field_z.append(self.tmp_field[2])
                    sleep(self.delay*0.001)
                    if self.agilent == True:
                        self.tmp_current = self.agilent_34410.current_dc
                    else:
                        self.tmp_current= self.keithley.current
                    #surowe dane:
                    tmp_current.append(self.tmp_current)   #surowy prąd
                    tmp_voltage.append(self.keithley_voltage_bias) #surowe napiecie
                    tmp_resistance.append(float(self.keithley_voltage_bias)/float(self.tmp_current) if self.tmp_current != 0 else np.nan) #surowa rezystancja
                    tmp_conductance.append(1/(float(self.keithley_voltage_bias)/float(self.tmp_current)) if self.tmp_current != 0 else np.nan) #surowa konduktancja

                    self.emit('progress', 100 * w / len(self.vector))
                    w = w + 1
                    if self.should_stop():
                        log.warning("Caught the stop flag in the procedure")
                        break
                    
                #opracowanie: 
                tmp_dI_dH = diff.diffs(tmp_field_set, tmp_current)
                tmp_dR_dH = diff.diffs(tmp_field_set, tmp_resistance)
                tmp_dG_dH = diff.diffs(tmp_field_set, tmp_conductance)
                tmp_dI = diff.diffIV(tmp_current)
                tmp_NdI = diff.NormalizedDiff(tmp_current)
                tmp_SPdI = diff.SlopeDiff(tmp_current, self.vector)
                tmp_HdIS = diff.HdIS(tmp_dI_dH,tmp_resistance)
                tmp_HdR = diff.diffs(tmp_field_set, tmp_resistance)
                tmp_HdG = diff.diffs(tmp_field_set, tmp_conductance) 
                tmp_dR = diff.diffIV(tmp_resistance)
                tmp_dG = diff.diffIV(tmp_conductance)
                tmp_NdR = diff.NormalizedDiff(tmp_resistance)
                tmp_NdG = diff.NormalizedDiff(tmp_conductance) 
                tmp_HdRS = diff.HdIS(tmp_HdR,tmp_current) 
                tmp_HdGS = diff.HdIS(tmp_HdG, tmp_voltage)
                    
                for l in range(len(tmp_voltage)):        
                    data = {
                        'V (V)':  self.value_function(tmp_voltage,l),
                        'I (A)':  self.value_function(tmp_current, l),
                        'R (ohm)': self.value_function(tmp_resistance, l),
                        'G': self.value_function(tmp_conductance, l),
                        'X field (Oe)': self.value_function(tmp_field_x, l),
                        'Y field (Oe)': self.value_function(tmp_field_y, l),
                        'Z field (Oe)': self.value_function(tmp_field_z, l),
                        'Hset (Oe)': self.value_function(tmp_field_set, l),
                        'dR/dH': self.value_function(tmp_dR_dH, l),
                        'dG/dH': self.value_function(tmp_dG_dH, l),
                        'dI': self.value_function(tmp_dI, l),
                        'dI/dH': self.value_function(tmp_dI_dH, l), 
                        'NdI': self.value_function(tmp_NdI, l), 
                        'SPdI': self.value_function(tmp_SPdI, l), 
                        'HdIS': self.value_function(tmp_HdIS, l),
                        'HdR':self.value_function(tmp_HdR, l), 
                        'HdG': self.value_function(tmp_HdG, l), 
                        'dR': self.value_function(tmp_dR, l), 
                        'dG': self.value_function(tmp_dG, l), 
                        'NdR': self.value_function(tmp_NdR, l),
                        'NdG': self.value_function(tmp_NdG, l), 
                        'HdRS': self.value_function(tmp_HdRS, l),
                        'HdGS': self.value_function(tmp_HdGS, l),
                        }
                    self.emit('results', data) 
                
               
                   



            elif self.acquire_type == 'V(Hdc) |set Ib':
                if self.coil == "Large":
                        self.field_const = 5
                else:
                        self.field_const = 10 
                w = 0
                log.info("Starting to sweep through field")
                for i in self.vector:
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
                        self.tmp_volatage = self.keithley.voltage
                    #surowe dane: 

                    tmp_current.append(self.keithley_current_bias)
                    tmp_voltage.append(self.tmp_volatage)
                    tmp_resistance.append(float(self.tmp_volatage)/float(self.keithley_current_bias) if self.keithley_current_bias != 0 else np.nan )
                    tmp_conductance.append(1/(float(self.tmp_volatage)/float(self.keithley_current_bias)) if self.keithley_current_bias != 0  else np.nan) #surowa konduktancja
                    self.emit('progress', 100 * w / len(self.vector))
                    w = w + 1
                    if self.should_stop():
                        log.warning("Caught the stop flag in the procedure")
                        break
                   
                #opracowanie: 
                tmp_dV_dH = diff.diffs(tmp_field_set, tmp_voltage)
                tmp_dR_dH = diff.diffs(tmp_field_set, tmp_resistance)
                tmp_dG_dH = diff.diffs(tmp_field_set, tmp_conductance)
                tmp_dV = diff.diffIV(tmp_voltage)
                tmp_NdV = diff.NormalizedDiff(tmp_voltage)
                tmp_SPdV = diff.SlopeDiff(tmp_voltage, self.vector)
                tmp_HdVS = diff.HdIS(tmp_dV_dH,tmp_resistance)
                tmp_HdR = diff.diffs(tmp_field_set, tmp_resistance)
                tmp_HdG = diff.diffs(tmp_field_set, tmp_conductance) 
                tmp_dR = diff.diffIV(tmp_resistance)
                tmp_dG = diff.diffIV(tmp_conductance)
                tmp_NdR = diff.NormalizedDiff(tmp_resistance)
                tmp_NdG = diff.NormalizedDiff(tmp_conductance) 
                tmp_HdRS = diff.HdIS(tmp_HdR,tmp_current) 
                tmp_HdGS = diff.HdIS(tmp_HdG, tmp_voltage)     

                for l in range(len(tmp_voltage)):        
                    data = {
                        'V (V)':  self.value_function(tmp_voltage,l),
                        'R (ohm)': self.value_function(tmp_resistance, l),
                        'G': self.value_function(tmp_conductance, l),
                        'X field (Oe)': self.value_function(tmp_field_x, l),
                        'Y field (Oe)': self.value_function(tmp_field_y, l),
                        'Z field (Oe)': self.value_function(tmp_field_z, l),
                        'Hset (Oe)': self.value_function(tmp_field_set, l),
                        'dR/dH': self.value_function(tmp_dR_dH, l),
                        'dG/dH': self.value_function(tmp_dG_dH, l),
                        'dV': self.value_function(tmp_dV, l),
                        'dV/dH': self.value_function(tmp_dV_dH, l), 
                        'NdV': self.value_function(tmp_NdV, l), 
                        'SPdV': self.value_function(tmp_SPdV, l), 
                        'HdVS': self.value_function(tmp_HdVS, l),
                        'HdR':self.value_function(tmp_HdR, l), 
                        'HdG': self.value_function(tmp_HdG, l), 
                        'dR': self.value_function(tmp_dR, l), 
                        'dG': self.value_function(tmp_dG, l), 
                        'NdR': self.value_function(tmp_NdR, l),
                        'NdG': self.value_function(tmp_NdG, l), 
                        'HdRS': self.value_function(tmp_HdRS, l),
                        'HdGS': self.value_function(tmp_HdGS, l),
                        }
                    self.emit('results', data) 
               


                    
            elif self.acquire_type == 'I(Vb) | set Hdc':
                log.info("Starting to sweep through voltage")
                w = 0


                for i in self.vector:
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
                    # surowe
                    tmp_current.append(self.tmp_current)
                    tmp_voltage.append(i)
                    tmp_resistance.append(float(i)/float(self.tmp_current) if self.tmp_current != 0 else math.nan)
                    tmp_conductance.append(1/(float(i)/float(self.tmp_current)) if self.tmp_current != 0 and i !=0 else math.nan)
                    
                    self.emit('progress', 100 * w / len(self.vector))
                    w = w + 1
                    if self.should_stop():
                        log.warning("Caught the stop flag in the procedure")
                        break

                #opracowanie: 
                tmp_dI_dV = diff.diffs(tmp_voltage, tmp_current)
                tmp_dI = diff.diffIV(tmp_current)
                tmp_dR = diff.diffIV(tmp_resistance)
                tmp_dG = diff.diffIV(tmp_conductance)
             
            
                    
                for l in range(len(tmp_voltage)):        
                    data = {
                        'V (V)':  self.value_function(tmp_voltage,l),
                        'I (A)':  self.value_function(tmp_current, l),
                        'R (ohm)': self.value_function(tmp_resistance, l),
                        'G': self.value_function(tmp_conductance, l),
                        'X field (Oe)': self.value_function(tmp_field_x, l),
                        'Y field (Oe)': self.value_function(tmp_field_y, l),
                        'Z field (Oe)': self.value_function(tmp_field_z, l),
                        'Hset (Oe)': self.value_function(tmp_field_set, l),
                        'dI': self.value_function(tmp_dI, l),
                        'dI/dV': self.value_function(tmp_dI_dV, l), 
                        'dR': self.value_function(tmp_dR, l), 
                        'dG': self.value_function(tmp_dG, l), 
                        }
                    self.emit('results', data) 
               
                
            elif self.acquire_type == 'V(Ib) | set Hdc':
                log.info("Starting to sweep through current")
                w = 0
                for i in self.vector:
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
                    tmp_resistance.append(float(self.tmp_volatage)/(i if i != 0 else 1e-9)) 
                    tmp_conductance.append((float(i)/float(self.tmp_volatage)))
                    self.emit('progress', 100 * w / len(self.vector))
                    w = w + 1
                    if self.should_stop():
                        log.warning("Caught the stop flag in the procedure")
                        break
                    

                   #opracowanie: 
                tmp_dV_dI = diff.diffs(tmp_current, tmp_voltage)
                tmp_dV = diff.diffIV(tmp_voltage)
                tmp_dR = diff.diffIV(tmp_resistance)
                tmp_dG = diff.diffIV(tmp_conductance)
             
            
                    
                for l in range(len(tmp_voltage)):        
                    data = {
                        'V (V)':  self.value_function(tmp_voltage,l),
                        'I (A)':  self.value_function(tmp_current, l),
                        'R (ohm)': self.value_function(tmp_resistance, l),
                        'G': self.value_function(tmp_conductance, l),
                        'X field (Oe)': self.value_function(tmp_field_x, l),
                        'Y field (Oe)': self.value_function(tmp_field_y, l),
                        'Z field (Oe)': self.value_function(tmp_field_z, l),
                        'Hset (Oe)': self.value_function(tmp_field_set, l),
                        'dV': self.value_function(tmp_dV, l),
                        'dV/dI': self.value_function(tmp_dV_dI, l), 
                        'dR': self.value_function(tmp_dR, l), 
                        'dG': self.value_function(tmp_dG, l), 
                        }
                    self.emit('results', data) 
               
        elif self.mode == "Fast Resistance":
            self.tmp_resistance = self.keithley.resistance
            log.info(self.tmp_resistance)
            # self.emit('results',  data = {
            #             'V (V)':  0,
            #             'I (A)':  0,
            #             'X field (Oe)': 0,
            #             'Y field (Oe)': 0,
            #             'Z field (Oe)': 0,
            #             'Hset (Oe)': 0,
        
        #Lockin mode:
        
        elif self.mode == 'HDC-ACModeLockin':
            if self.mode_lockin == "Sweep field":
              
                if self.kepco == False:
                    self.calibration_field = LockinCalibration(self.lockin, self.ac_field_frequency,self.dc_field, self.coil_constant)
                    self.cal_field_const = self.calibration_field.calibrate()
                    self.lockin.set_dc_field(self.dc_field/0.6)
                else: 
                    self.cal_field_const = 15
                    self.lockin.set_dc_field(self.dc_field/15)
               
                self.lockin.set_lockin_freq(self.lockin_frequency)
                self.counter = 0
                
                for i in self.vector:
                    if self.amplitude_vec == True:
                        self.lockin.set_ac_field(i/self.cal_field_const,self.ac_field_frequency)
                    else:
                        self.lockin.set_ac_field(self.ac_field_amplitude/self.cal_field_const,i)
                    if i != 0:
                        sleep(2/i)
                    else: 
                        sleep(1)
                    
                    r = self.lockin.lockin_measure_R(0,self.avergaging_rate)
                    theta = self.lockin.lockin_measure_phase(0,self.avergaging_rate)
                    self.counter = self.counter + 1
                        
                    self.emit('progress', 100 * self.counter / len(self.vector))
                   
                    try:
              
                        data_lockin = {
                            'f (Hz)': i if self.amplitude_vec == False else self.ac_field_frequency, 
                            'AHac (Oe)': i if self.amplitude_vec == True else self.ac_field_amplitude,
                            'Vsense (V)': r if self.input_type == "Voltage input" else math.nan,
                            'Vbias (V)': self.bias_voltage,
                            'X field (Oe)': i+self.dc_field if self.amplitude_vec == True else self.ac_field_amplitude+self.dc_field,
                            'Y field (Oe)':0,
                            'Z field (Oe)': 0,
                            'I (A)':  r if self.input_type == "Current input" else math.nan,
                            'Phase': theta,
                            'I/Phase' : r/theta if self.input_type == "Current input" else math.nan,
                            'V/Phase': r/theta if self.input_type == "Voltage input" else math.nan,
                            'I/Ax': r/self.ac_field_amplitude if self.input_type == "Current input" and  self.amplitude_vec == True else math.nan,
                            }
                            
                        
                     
                        self.emit('results', data_lockin) 
                    except Exception as e:
                        print(e)
                        self.should_stop()
                    if self.should_stop():
                        log.warning("Caught the stop flag in the procedure")
                        break




            #####SWEEP FREQUENCY ########



            elif self.mode_lockin == "Sweep frequency":
                self.field_value = measure_field(1,self.field_sensor, self.should_stop )
                self.counter = 0
                for i in self.vector:
                    self.lockin.set_lockin_freq(i) 
                    if i != 0:
                        sleep(3)
                    else: 
                        sleep(0.5)
                    r = self.lockin.lockin_measure_R(0,self.avergaging_rate)
                    sleep(1)
                    theta = self.lockin.lockin_measure_phase(0,self.avergaging_rate)
                    self.counter = self.counter + 1
                    self.emit('progress', 100 * self.counter / len(self.vector))
                    try:
                        data_lockin = {
                            'f (Hz)': i,  
                            'Vsense (V)':  r if self.input_type == "Voltage input" else math.nan,
                            'Vbias (V)': self.bias_voltage,
                            'X field (Oe)':self.field_value[0],
                            'Y field (Oe)':self.field_value[1],
                            'Z field (Oe)': self.field_value[2],
                            'I (A)':   r if self.input_type == "Current input" else math.nan,
                            'Phase': theta,
                            'I/Phase' : r/theta if self.input_type == "Current input" else math.nan,
                            'V/Phase': r/theta if self.input_type == "Voltage input" else math.nan,
                            'I/Ax': r/self.ac_field_amplitude if self.input_type == "Current input" and  self.amplitude_vec == True else math.nan,
                            }
                    

                        self.emit('results', data_lockin) 
                    except:
                        self.should_stop()
                    if self.should_stop():
                        log.warning("Caught the stop flag in the procedure")
                        break   
        




        elif self.mode == "TimeMode":
            if self.kepco == False:
                self.calibration_field = LockinCalibration(self.lockin, self.ac_field_frequency,self.dc_field, self.coil_constant)
                self.cal_field_const = self.calibration_field.calibrate()
                self.lockin.set_dc_field(self.dc_field/0.6)
            else: 
                self.cal_field_const = 15
                self.lockin.set_dc_field(self.dc_field/15)
           
            self.lockin.set_lockin_freq(self.lockin_frequency)
            self.lockin.set_ac_field(self.ac_field_amplitude/self.cal_field_const,self.ac_field_frequency)
            sleep(2)
            scope_signal = self.lockin.get_wave()
            self.emit('progress', 100)
            try:
                for w in range(len(scope_signal[0])):
                    data_lockin = {
                        'time (s)': scope_signal[0][w],
                        'f (Hz)': self.ac_field_frequency, 
                        'AHac (Oe)':self.ac_field_amplitude,
                        'Vsense (V)': float(scope_signal[1][w]) if self.input_type == "Voltage input" else math.nan,
                        'Vbias (V)': self.bias_voltage,
                        'X field (Oe)': 0,
                        'Y field (Oe)':0,
                        'Z field (Oe)': 0,
                        'I (A)':  float(scope_signal[1][w]) if self.input_type == "Current input" else math.nan,
                        'Hset (Oe)': self.ac_field_amplitude+self.dc_field,
                        "G(t)": float(scope_signal[1][w])/self.bias_voltage if self.input_type == "Current input" else math.nan, 
                        "R(t)": self.bias_voltage/float(scope_signal[1][w]) if self.input_type == "Current input" else math.nan,
                        }
                    
                 
                    self.emit('results', data_lockin) 
            except Exception as e:
                print(e)
                self.should_stop()
            if self.should_stop():
                log.warning("Caught the stop flag in the procedure")
                

    def shutdown(self):

        if MainWindow.last == True or IVTransfer.licznik == MainWindow.wynik:
            if self.mode == "HDCMode":
                if self.field_device == "DAQ":
                    self.field.shutdown()
                    pass
                else: 
                    if self.acquire_type == 'I(Hdc) | set Vb' or self.acquire_type == 'V(Hdc) |set Ib':         
                        self.field.shutdown(self.last_value/self.field_const)
                    else:
                        self.field.shutdown(self.field_bias/self.field_const)
                sleep(0.2)
            
                self.keithley.shutdown()
                print("keithley shutdown done")
                IVTransfer.licznik = 0
            elif self.mode == "HDC-ACModeLockin": 
                self.lockin.shutdown()
        else:
            if self.mode == "HDCMode":
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
            inputs=['mode','mode_lockin','sample_name','vector_param','lockin_vector','coil','coil_constant', 'acquire_type','keithley_adress','agilent','agilent34401a_adress','field_sensor_adress', 'keithley_compliance_current', 'keithley_compliance_voltage',
            'keithley_current_bias', 'keithley_voltage_bias', 'field_device', 'field_bias', 'agilent_adress', 'delay', 'reverse_field', 'lockin_adress','input_type','sigin_imp','sigin_autorange', 'sigin_ac','differential_signal', 'kepco', 'dc_field','bias_voltage', 'ac_field_amplitude', 'ac_field_frequency', 'sigin_range', 'lockin_frequency', 'avergaging_rate','scope_rate', 'scope_time', 'amplitude_vec'],
            displays=['sample_name', 'acquire_type', 'field_bias', 'keithley_current_bias', 'keithley_voltage_bias'],
            x_axis='I (A)',
            y_axis='V (V)',
            directory_input=True,  
            sequencer=True,                                  
            sequencer_inputs=['field_bias', 'keithley_current_bias', 'keithley_voltage_bias','ac_field_amplitude', 'ac_field_frequency'],
            inputs_in_scrollarea=True,
            
        )
       
        self.setWindowTitle('IV Measurement System v.0.99')
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