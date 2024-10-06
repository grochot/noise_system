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
# from pymeasure.display.windows.managed_dock_window import ManagedDockWindow
from pymeasure.experiment import (
    Procedure,
    FloatParameter,
    BooleanParameter,
    IntegerParameter,
    Parameter,
    ListParameter,
    Results,
    VectorParameter,
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
    licznik = 0  # licznik
    stop_flag = False
    find_instruments = FindInstrument()
    finded_instruments = list(find_instruments.show_instrument())
    finded_instruments.append("None")
    save_parameter = SaveParameters()
    used_parameters_list = [
        "mode",
                "mode_lockin",
                "sample_name",
                "vector_param",
                "lockin_vector",
                "coil",
                "coil_constant",
                "acquire_type",
                "keithley_adress",
                "agilent",
                "agilent34401a_adress",
                "field_sensor_adress",
                "keithley_compliance_current",
                "keithley_compliance_voltage",
                "keithley_current_bias",
                "keithley_voltage_bias",
                "field_device",
                "field_bias",
                "agilent_adress",
                "delay",
                "reverse_field",
                "lockin_adress",
                "sigin_imp",
                
                "currins_range",
                "currins_autorange",
                "sigin_range",
                "sigin_autorange",
                "sigin_ac",
                "differential_signal",
                "kepco",
                "dc_field",
                "dc_field_time",
                "bias_voltage",
                "ac_field_amplitude",
                "ac_field_frequency",
                "ac_field_amplitude_time",
                "ac_field_frequency_time",
                "lockin_frequency",
                "avergaging_rate",
                "scope_rate",
                "scope_time",
                "amplitude_vec",
                "external_ref", 
                "sigin_float", 
                "currin_float", 
                "timeconstant", 
                "order",
                "ac_voltage_frequency",
                "ac_voltage_amplitude",
                "Hr", 
                "sweep_by",
                "field_angle",
                "Field2DController_address", 
                "Field2DController_average"
    ]
    parameters_from_file = save_parameter.ReadFile()
    parameters = {}
    # print(finde_instruments)

    # Define parameters
    mode = ListParameter(
        "Mode",
        default=parameters_from_file["mode"],
        choices=["HDCMode", "Fast Resistance", "HDC-ACModeLockin", "TimeMode"],
    )
    mode_lockin = ListParameter(
        "Lockin mode",
        default=parameters_from_file["mode_lockin"],
        choices=["Sweep field", "Sweep frequency", "Sweep voltage"],
        group_by="mode",
        group_condition=lambda v: v == "HDC-ACModeLockin",
    )
    agilent = BooleanParameter(
        "Agilent",
        default=parameters_from_file["agilent"],
        group_by="mode",
        group_condition=lambda v: v == "HDCMode",
    )
    agilent34401a_adress = ListParameter(
        "Agilent34401a adress",
        default=(
            parameters_from_file["agilent34401a_adress"]
            if parameters_from_file["agilent34401a_adress"] in finded_instruments
            else "None"
        ),
        choices=finded_instruments,
        group_by="agilent",
        group_condition=lambda v: v == True,
    )
    acquire_type = ListParameter(
        "Acquisition type",
        default=parameters_from_file["acquire_type"],
        choices=[
            "I(Hdc) | set Vb",
            "V(Hdc) | set Vb",
            "V(Hdc) |set Ib",
            "I(Vb) | set Hdc",
            "V(Ib) | set Hdc",
        ],
        group_by="mode",
        group_condition=lambda v: v == "HDCMode",
    )
    keithley_adress = ListParameter(
        "Keithley2400 adress",
        default=(
            parameters_from_file["keithley_adress"]
            if parameters_from_file["keithley_adress"] in finded_instruments
            else "None"
        ),
        choices=finded_instruments,
        group_by="mode",
        group_condition=lambda v: v == "HDCMode",
    )
    field_sensor_adress = Parameter(
        "Field_sensor", default=parameters_from_file["field_sensor_adress"]
    )
    # keithley_source_type = ListParameter("Source type", default = "Current", choices = ['Current', 'Voltage'])
    keithley_compliance_current = FloatParameter(
        "Compliance current",
        units="A",
        default=parameters_from_file["keithley_compliance_current"],
        group_by={
            "acquire_type": lambda v: v == "I(Hdc) | set Vb" or v == "I(Vb) | set Hdc" or v == "V(Hdc) | set Vb",
            "mode": lambda v: v == "HDCMode",
        },
    )
    keithley_compliance_voltage = FloatParameter(
        "Compliance voltage",
        units="V",
        default=parameters_from_file["keithley_compliance_voltage"],
        group_by={
            "acquire_type": lambda v: v == "V(Hdc) |set Ib" or v == "V(Ib) | set Hdc",
            "mode": lambda v: v == "HDCMode",
        },
    )
    keithley_current_bias = FloatParameter(
        "Current bias",
        units="A",
        default=parameters_from_file["keithley_current_bias"],
        group_by={"acquire_type": "V(Hdc) |set Ib", "mode": lambda v: v == "HDCMode"},
    )
    keithley_voltage_bias = FloatParameter(
        "Voltage bias",
        units="V",
        default=parameters_from_file["keithley_voltage_bias"],
        group_by={
            "acquire_type": lambda v: v == "I(Hdc) | set Vb" or v == "V(Hdc) | set Vb",
            "mode": lambda v: v == "HDCMode" or v == "Fast Resistance",
        },
    )
    agilent_adress = ListParameter(
        "Agilent E3648A adress",
        default=(
            parameters_from_file["agilent_adress"]
            if parameters_from_file["agilent_adress"] in finded_instruments
            else "None"
        ),
        choices=finded_instruments,
        group_by=[
        "mode", 
        "field_device"
                 ],

        group_condition=[ lambda v: v == "HDCMode", lambda v: v == "Agilent E3648A"],
    )
    
    field_device = ListParameter(
        "Field device",
        choices=["DAQ", "Agilent E3648A", "2D Controller"],
        default=parameters_from_file["field_device"],
        group_by="mode",
        group_condition=lambda v: v == "HDCMode",
    )
    field_bias = FloatParameter(
        "Field bias",
        units="Oe",
        default=parameters_from_file["field_bias"],
        group_by={
            "mode": lambda v: v == "HDCMode",
        },
    ) 

    field_angle = FloatParameter( 
        "Field angle",
        units="deg",
        default=parameters_from_file["field_angle"],
        group_by={
            "mode": lambda v: v == "HDCMode",
            "field_device": lambda v: v == "2D Controller"
        },
    ) 
    coil = ListParameter(
        "Coil",
        default=parameters_from_file["coil"],
        choices=["Large", "Small"],
        group_by="mode",
        group_condition=lambda v: v == "HDCMode",
    )
    vector_param = Parameter(
        "Vector",
        group_by="mode",
        default=parameters_from_file["vector_param"],
        group_condition=lambda v: v == "HDCMode",
    )
    # stop = FloatParameter("Stop", group_by='mode', group_condition=lambda v: v =='HDCMode')
    # no_points = IntegerParameter("No Points", group_by='mode', group_condition=lambda v: v =='HDCMode')
    reverse_field = BooleanParameter(
        "Reverse field",
        default=parameters_from_file["reverse_field"],
        group_by="mode",
        group_condition=lambda v: v == "HDCMode",
    )
    delay = FloatParameter(
        "Delay",
        units="ms",
        default=parameters_from_file["delay"],
        group_by="mode",
        group_condition=lambda v: v == "HDCMode",
    )
    sample_name = Parameter("Sample Name", default=parameters_from_file["sample_name"])
    bias_voltage = FloatParameter(
        "Bias Voltage",
        units="mV",
        default=parameters_from_file["bias_voltage"],
        group_by=["mode", "mode_lockin"],
        group_condition=[lambda v: v == "HDC-ACModeLockin" or v == "TimeMode", lambda v: v != "Sweep voltage",],
    )

    # Lockin mode:
    lockin_adress = Parameter(
        "Lockin adress",
        default=parameters_from_file["lockin_adress"],
        group_by="mode",
        group_condition=lambda v: v == "HDC-ACModeLockin" or v == "TimeMode",
    )

    Field2DController_address = Parameter(
         "2D Controller adress",
        default=parameters_from_file["Field2DController_address"],
        group_by="field_device",
        group_condition=lambda v: v =="2D Controller",
    )

    Field2DController_average = IntegerParameter(
        "2D Field Controller average", 
         default=parameters_from_file["Field2DController_average"],
         group_by="field_device",
        group_condition=lambda v: v =="2D Controller",

    )
    # input_type = ListParameter(
    #     "Signal input",
    #     default=parameters_from_file["input_type"],
    #     choices=["Voltage input", "Current input"],
    #     group_by=["mode", "mode_lockin"],
    #     group_condition=[lambda v: v == "HDC-ACModeLockin" or v == "TimeMode", "Sweep field"],
    # )
    dc_field = FloatParameter(
        "DC Field",
        units="Oe",
        default=parameters_from_file["dc_field"],
        group_by="mode",
        group_condition=lambda v: v == "HDC-ACModeLockin",
    )
    dc_field_time = FloatParameter(
        "DC Field",
        units="Oe",
        default=parameters_from_file["dc_field_time"],
        group_by="mode",
        group_condition=lambda v: v == "TimeMode",
    )
    ac_field_amplitude = FloatParameter(
        "AC Field Amplitude",
        units="Oe",
        default=parameters_from_file["ac_field_amplitude"],
        group_by=["mode", 'amplitude_vec', "mode_lockin" ],
        group_condition=[lambda v: v == "HDC-ACModeLockin", False, "Sweep field"],
    )
    ac_field_frequency = FloatParameter(
        "AC Field Frequency",
        units="Hz",
        default=parameters_from_file["ac_field_frequency"],
        group_by=["mode", "amplitude_vec", "mode_lockin"],
        group_condition=[lambda v: v == "HDC-ACModeLockin", True, "Sweep field"],
    )
    ac_voltage_amplitude = FloatParameter(
        "AC Voltage Amplitude",
        units="V",
        default=parameters_from_file["ac_voltage_amplitude"],
        group_by=["mode", "mode_lockin" ],
        group_condition=[lambda v: v == "HDC-ACModeLockin", "Sweep voltage"],
    )
    ac_voltage_frequency = FloatParameter(
        "AC Voltage Frequency",
        units="Hz",
        default=parameters_from_file["ac_voltage_frequency"],
        group_by=["mode",  "mode_lockin"],
        group_condition=[lambda v: v == "HDC-ACModeLockin", "Sweep voltage"],
    )
    ac_field_amplitude_time = FloatParameter(
        "AC Field Amplitude",
        units="Oe",
        default=parameters_from_file["ac_field_amplitude_time"],
        group_by=["mode" ],
        group_condition=[lambda v: v == "TimeMode"],
    )
    ac_field_frequency_time = FloatParameter(
        "AC Field Frequency",
        units="Hz",
        default=parameters_from_file["ac_field_frequency_time"],
        group_by=["mode"],
        group_condition=[lambda v: v == "TimeMode"],
    )
    differential_signal = BooleanParameter(
        "Differential voltage input",
        default=parameters_from_file["differential_signal"],
        group_by=["mode", "mode_lockin"],
        group_condition=[
            lambda v: v == "HDC-ACModeLockin" or v == "TimeMode",
            lambda v: v != "Sweep voltage",
        ],
    )
    sigin_float = BooleanParameter(
        "Signal Input Float",
        default=parameters_from_file["sigin_float"],
        group_by=["mode", "mode_lockin"],
        group_condition=[
            lambda v: v == "HDC-ACModeLockin" or v == "TimeMode",
            lambda v: v != "Sweep voltage",
        ],
    )
    currin_float = BooleanParameter(
        "Current Input Float",
        default=parameters_from_file["currin_float"],
        group_by=["mode"],
        group_condition=[
            lambda v: v == "HDC-ACModeLockin" or v == "TimeMode",
        ],
    )
    external_ref = BooleanParameter(
        "Use external ref",
        default=parameters_from_file["external_ref"],
        group_by=["mode"],
        group_condition=[
            lambda v:  v == "TimeMode"
        ],
    )
    lockin_frequency = FloatParameter(
        "Lockin frequency",
        units="Hz",
        default=parameters_from_file["lockin_frequency"],
        group_by=["mode", "external_ref"],
        group_condition=[
            lambda v: v == "TimeMode", False
        ],
    )
    avergaging_rate = IntegerParameter(
        "Avergaging rate",
        default=parameters_from_file["avergaging_rate"],
        group_by="mode",
        group_condition=lambda v: v == "HDC-ACModeLockin" or v == "TimeMode",
    )
    scope_rate = ListParameter(
        "Scope Rate",
        choices=[
            "60MHz",
            "30MHz",
            "15MHz",
            "7.5MHz",
            "3.75MHz",
            "1.88MHz",
            "938kHz",
            "469kHz",
            "234kHz",
            "117kHz",
            "58.6kHz",
            "29.3kHz",
            "14.6kHz",
            "7.32kHz",
            "3.66kHz",
            "1.83kHz",
            "916Hz",
        ],
        default=parameters_from_file["scope_rate"],
        group_by="mode",
        group_condition=lambda v: v == "TimeMode",
    )
    scope_time = FloatParameter(
        "Scope Length [pts] (max 16384)",
        default=parameters_from_file["scope_time"],
        group_by="mode",
        group_condition=lambda v: v == "TimeMode",
    )

    timeconstant = FloatParameter(
        "Lockin TimeConstant",
        units="s",
        default=parameters_from_file["timeconstant"],
        group_by="mode",
        group_condition=lambda v: v == "HDC-ACModeLockin",
    )

    order = IntegerParameter(
        "Lockin Filter order",
        default=parameters_from_file["order"],
        group_by="mode",
        group_condition=lambda v: v == "HDC-ACModeLockin",
    )

    kepco = BooleanParameter(
        "Kepco?",
        default=parameters_from_file["kepco"],
        group_by="mode",
        group_condition=lambda v: v == "HDC-ACModeLockin" or v == "TimeMode",
    )
    coil_constant = FloatParameter(
        "Coil constant",
        units="Oe/V",
        group_by="mode",
        default=parameters_from_file["coil_constant"],
        group_condition=lambda v: v == "HDC-ACModeLockin" or v == "TimeMode",
    )
    amplitude_vec = BooleanParameter(
        "Amplitude/Frequency AC Field",
        default=parameters_from_file["amplitude_vec"],
        group_by=["mode", "mode_lockin"],
        group_condition=[lambda v: v == "HDC-ACModeLockin", "Sweep field"],
    )

    sigin_imp = BooleanParameter(
        "50 Ohm",
        default=parameters_from_file["sigin_imp"],
        group_by=["mode", "mode_lockin"],
        group_condition=[
            lambda v: v == "HDC-ACModeLockin" or v == "TimeMode",
            lambda v: v != "Sweep voltage",
        ],
    )
    sigin_ac = BooleanParameter(
        "AC ON",
        default=parameters_from_file["sigin_ac"],
        group_by=["mode", "mode_lockin"],
        group_condition=[
            lambda v: v == "HDC-ACModeLockin" or v == "TimeMode",
            lambda v: v != "Sweep voltage",
        ],
    )

    sigin_range = FloatParameter(
        "SigIN Range",
        units="V",
        default=parameters_from_file["sigin_range"],
        decimals=9,
        step=None,
        group_by=["mode", "sigin_autorange"],
        group_condition=[lambda v: v == "HDC-ACModeLockin" or v == "TimeMode", False],
    )
    sigin_autorange = BooleanParameter(
        "SigIN Autorange ON",
        default=parameters_from_file["sigin_autorange"],
        group_by=["mode", "mode_lockin"],
        group_condition=[lambda v: v == "HDC-ACModeLockin" or v == "TimeMode", lambda v: v != "Sweep voltage",],
    )
    currins_range = FloatParameter(
        "CurrIN Range",
        units="A",
        default=parameters_from_file["currins_range"],
        decimals=9,
        step=None,
        group_by=["mode", "currins_autorange"],
        group_condition=[lambda v: v == "HDC-ACModeLockin" or v == "TimeMode", False],
    )
    currins_autorange = BooleanParameter(
        "CurrIN Autorange ON",
        default=parameters_from_file["currins_autorange"],
        group_by=["mode"],
        group_condition=[lambda v: v == "HDC-ACModeLockin" or v == "TimeMode"],
    )
    lockin_vector = Parameter(
        "Vector",
        default=parameters_from_file["lockin_vector"],
        group_by="mode",
        group_condition=lambda v: v == "HDC-ACModeLockin",
    )

    Hr = FloatParameter("Hr", default = parameters_from_file["Hr"])
    sweep_by = ListParameter("Sweep by", choices=["Angle", "Field Value", "acquire_mode"], default = parameters_from_file["sweep_by"], group_by=["mode", "field_device"],
        group_condition=[lambda v: v == "HDCMode", "2D Controller", (lambda v: v != "I(Vb) | set Hdc") or (lambda k: k !="V(Ib) | set Hdc")] )
    ##############################################################################################################################################################

    DEBUG = 1
    DATA_COLUMNS = [
        "time (s)",
        "V (V)",
        "f (Hz)",
        "AHac (Oe)",
        "Vsense (V)",
        "Vbias (V)",
        "I (A)",
        "Phase",
        "R (ohm)",
        "dI/dH",
        "dR/dH",
        "dI",
        "dV",
        "X field (Oe)",
        "Y field (Oe)",
        "Z field (Oe)",
        "Hset (Oe)",
        "G",
        "I/Phase",
        "V/Phase",
        "I/Ax",
        "dG",
        "dR",
        "dI/dV",
        "dV/dI",
        "dG/dH",
        "NdR",
        "NdG",
        "NdI",
        "HdIS",
        "HdVS",
        "dV/dH",
        "SPdI",
        "HdIS",
        "HdRS",
        "HdGS",
        "G(t)",
        "R(t)"


    ]  # data columns

    path_file = SaveFilePath()

    def value_function(self, lista, iter):
        try:
            wynik = lista[iter]
            return wynik
        except:
            return np.nan

######################################################### INIT #################################################
    def startup(self):
        for i in self.used_parameters_list:
            self.param = eval("self." + i)
            self.parameters[i] = self.param

        self.save_parameter.WriteFile(self.parameters)
        self.vector_obj = Vector()
        if self.mode == "HDCMode":
            sleep(0.1)


            ### Init field device
            if self.field_device == "DAQ":
                try:
                    from hardware.daq import DAQ

                    self.field = DAQ("6124/ao0")
                except Exception as e:
                    log.error("Config DAQ failed")
                    self.stop_flag = True
                try:
                    if self.reverse_field == True and 'Hr' not in self.vector_obj.generate_vector_input(self.vector_param):
                        self.vector_to = self.vector_obj.generate_vector(
                            self.vector_param
                        )
                        self.vector_rev = self.vector_to[::-1]
                        self.vector = np.append(self.vector_to[0:-1], self.vector_rev)
                        
                    else:
                        if 'Hr' not in self.vector_obj.generate_vector_input(self.vector_param):
                            self.vector = self.vector_obj.generate_vector(self.vector_param)
                            
                        else: 
                            self.vector = self.vector_obj.generate_vector(self.vector_param, self.Hr)
                           
                        print(self.vector)
                except Exception as e:
                    log.error("Vector set failed")
                    self.stop_flag = True
                
            elif self.field_device == "Agilent E3648A":
                ##Bias field:
                try:
                    from hardware.keisight_e3600a import E3600a

                    self.field = E3600a(
                        self.agilent_adress
                    )  # connction to field controller
                    self.field.remote()
                    sleep(1)
                except Exception as e:
                    log.error("Config Keisight E3648A failed")
                    self.stop_flag = True
                try:
                    if self.reverse_field == True:
                        self.vector_to = self.vector_obj.generate_vector(
                            self.vector_param,self.Hr
                        )
                        self.vector_rev = self.vector_to[::-1]
                        self.vector = np.append(self.vector_to[0:-1], self.vector_rev)
                    else:
                        self.vector = self.vector_obj.generate_vector(self.vector_param, self.Hr)
                except Exception as e:
                    log.error("Vector set failed")
                    self.stop_flag = True
            else: 
                try: 
                    from hardware.rzeszut_driver import RzeszutField 
                    self.field = RzeszutField(self.Field2DController_address)
                    if self.field.get_pid_status(1)[1] == "R": 
                        pass 
                    else: 
                        self.field.set_pid_on(1)
                    if self.field.get_pid_status(2)[1] == "R": 
                        pass 
                    else: 
                        self.field.set_pid_on(2)
                    self.field.set_sample_number(str(self.Field2DController_average))
                except: 
                    log.error("Config 2D Controller failed")
                    self.stop_flag = True
                try:
                    if self.reverse_field == True and 'Hr' not in self.vector_obj.generate_vector_input(self.vector_param):
                        self.vector_to = self.vector_obj.generate_vector(
                            self.vector_param
                        )
                        self.vector_rev = self.vector_to[::-1]
                        self.vector = np.append(self.vector_to[0:-1], self.vector_rev)
                        
                    else:
                        if 'Hr' not in self.vector_obj.generate_vector_input(self.vector_param):
                            self.vector = self.vector_obj.generate_vector(self.vector_param)
                            
                        else: 
                            self.vector = self.vector_obj.generate_vector(self.vector_param, self.Hr)
                           
                        print("Vector: {}".format(self.vector))
                except Exception as e:
                    log.error("Vector set failed")
                    self.stop_flag = True
            ############## KEITHLEY CONFIG ###############
            try:

                self.keithley = Keithley2400(self.keithley_adress)
                if self.acquire_type == "I(Hdc) | set Vb":
                    self.keithley.apply_voltage()
                    self.keithley.source_voltage_range = 20
                    self.keithley.compliance_current = self.keithley_compliance_current
                    self.keithley.source_voltage = (
                        self.keithley_voltage_bias
                    )  # Sets the source current to 0 mA
                    self.keithley.enable_source()  # Enables the source output
                    self.keithley.measure_current()

                if self.acquire_type == "V(Hdc) | set Vb":
                    self.keithley.apply_voltage()
                    self.keithley.source_voltage_range = 20
                    self.keithley.compliance_current = self.keithley_compliance_current
                    self.keithley.source_voltage = (
                        self.keithley_voltage_bias
                    )  # Sets the source current to 0 mA
                    self.keithley.enable_source()  # Enables the source output
                    self.keithley.measure_current()


                elif self.acquire_type == "V(Hdc) |set Ib":
                    self.keithley.apply_current()
                    self.keithley.source_current_range = 0.1
                    self.keithley.compliance_voltage = self.keithley_compliance_voltage
                    self.keithley.source_current = (
                        self.keithley_current_bias
                    )  # Sets the source current to 0 mA
                    self.keithley.enable_source()  # Enables the source output
                    self.keithley.measure_voltage()
                
                elif self.acquire_type == "I(Vb) | set Hdc":
                    self.keithley.apply_voltage()
                    self.keithley.source_voltage_range = 20
                    self.keithley.compliance_current = self.keithley_compliance_current
                    self.keithley.source_voltage = 0  # Sets the source current to 0 mA
                    self.keithley.enable_source()  # Enables the source output
                    self.keithley.measure_current()

                    if self.field_device == "2D Controller":
                        self.field.set_field_value(self.field_angle, self.field_bias)
                    else:   
                        if self.coil == "Large":
                            self.field_const = 5
                        else:
                            self.field_const = 10
                        self.set_field = self.field.set_field(
                            self.field_bias / self.field_const
                        )
                
                elif self.acquire_type == "V(Ib) | set Hdc":
                    self.keithley.apply_current()
                    self.keithley.source_current_range = 0.1
                    self.keithley.compliance_voltage = self.keithley_compliance_voltage
                    self.keithley.source_current = 0  # Sets the source current to 0 mA
                    self.keithley.enable_source()  # Enables the source output
                    self.keithley.measure_voltage()
                    if self.field_device == "2D Controller":
                        self.field.set_field_value(self.field_angle, self.field_bias)
                    else:   
                        if self.coil == "Large":
                            self.field_const = 5
                        else:
                            self.field_const = 10
                        self.set_field = self.field.set_field(
                            self.field_bias / self.field_const
                        )
             
            except:
                log.error("Config Keithley 2400 failed")
                self.stop_flag = True
          

          


            ####### Config FieldSensor ########
            if self.field_device == "2D Controller":
                    log.info("Use 2D Controller ")
            else:   
                try:
                    self.field_sensor = FieldSensor(self.field_sensor_adress)
                    self.field_sensor.read_field_init()

                except:
                    log.error("Config FieldSensor failed")
                    self.field_sensor = DummyFieldSensor()
                    log.info("Use DummyFieldSensor")


            ####### Config Agilent 34410A ########
            if self.agilent == True:
                try:
                    self.agilent_34410 = Agilent34410A(self.agilent34401a_adress)

                    if self.coil == "Large":
                        self.field_const = 5
                    else:
                        self.field_const = 10
                    if self.acquire_type == "I(Vb) | set Hdc":
                        self.set_field = self.field.set_field(
                            self.field_bias / self.field_const
                        )
                    elif self.acquire_type == "V(Ib) | set Hdc":
                        self.set_field = self.field.set_field(
                            self.field_bias / self.field_const
                        )
                  
                except:
                    log.error("Config Agilent 34410A failed")
                    self.stop_flag = True

        elif self.mode == "Fast Resistance":

            ############## KEITHLEY CONFIG ###############

            try:
                self.keithley = Keithley2400(self.keithley_adress)
                self.keithley.apply_voltage()
                self.keithley.source_voltage_range = 1
                self.keithley.compliance_current = 0.1
                self.keithley.source_voltage = (
                    self.keithley_voltage_bias
                )  # Sets the source current to 0 mA
                self.keithley.enable_source()  # Enables the source output
                self.keithley.measure_resistance()

            except:
                log.error("Config Keithley 2400 failed")
                self.stop_flag = True

        elif self.mode == "HDC-ACModeLockin":

            if self.mode_lockin == "Sweep field":
                try:
                    self.field_sensor = FieldSensor(self.field_sensor_adress)
                    self.field_sensor.read_field_init()
                except:
                    log.error("Config FieldSensor failed")
                    self.field_sensor = DummyFieldSensor()
                    log.info("Use DummyFieldSensor")
                try:
                    self.lockin = LockinField(self.lockin_adress)
                  
                    if self.differential_signal == True:
                        self.lockin.init(
                            0,
                            True,
                            float(self.sigin_range),
                            self.sigin_imp,
                            self.sigin_ac,
                            self.sigin_autorange,
                            self.currins_range,
                            self.currins_autorange,
                            self.sigin_float, 
                            self.currin_float, 
                            self.timeconstant, 
                            self.order
                        )
                    else:
                        self.lockin.init(
                            0,
                            False,
                            float(self.sigin_range),
                            self.sigin_imp,
                            self.sigin_ac,
                            self.sigin_autorange,
                            self.currins_range,
                            self.currins_autorange,
                            self.sigin_float, 
                            self.currin_float, 
                            self.timeconstant, 
                            self.order
                        )

                  

                except Exception as a:
                    log.error("Lockin init failed: {}".format(a))
                    self.stop_flag = True

                self.vector = self.vector_obj.generate_vector(self.lockin_vector)

                self.lockin.set_constant_vbias(self.bias_voltage)
                sleep(1)

            elif self.mode_lockin == "Sweep voltage":
                try:
                    self.field_sensor = FieldSensor(self.field_sensor_adress)
                    self.field_sensor.read_field_init()
                except:
                    log.error("Config FieldSensor failed")
                    self.field_sensor = DummyFieldSensor()
                    log.info("Use DummyFieldSensor")
                try:
                    self.lockin = LockinField(self.lockin_adress)
                    
                    self.lockin.init(
                        1,
                        False,
                        float(self.sigin_range),
                        self.sigin_imp,
                        self.sigin_ac,
                        self.sigin_autorange,
                        self.currins_range,
                        self.currins_autorange,
                        self.sigin_float, 
                        self.currin_float, 
                        self.timeconstant, 
                        self.order
                    )

                except Exception as a:
                    log.error("Lockin init failed: {}".format(a))
                    self.stop_flag = True

                self.vector = self.vector_obj.generate_vector(self.lockin_vector)

                self.lockin.set_constant_vbias(self.dc_field/(1/self.coil_constant))  ##AUX1 - SET CONSTANT FIELD
                sleep(1)

            elif self.mode_lockin == "Sweep frequency":

                try:
                    self.field_sensor = FieldSensor(self.field_sensor_adress)
                    self.field_sensor.read_field_init()
             
                except:
                    log.error("Config FieldSensor failed")
                    self.field_sensor = DummyFieldSensor()
                    log.info("Use DummyFieldSensor")

                self.lockin = LockinFrequency(self.lockin_adress)
           
             
                if self.differential_signal == True:
                    self.lockin.init(
                        0,
                        True,
                        float(self.sigin_range),
                        self.sigin_imp,
                        self.sigin_ac,
                        self.sigin_autorange,
                        self.currins_range,
                        self.currins_autorange,
                        self.sigin_float, 
                        self.currin_float, 
                        self.timeconstant, 
                        self.order
                    )
                else:
                    self.lockin.init(
                        0,
                        False,
                        float(self.sigin_range),
                        self.sigin_imp,
                        self.sigin_ac,
                        self.sigin_autorange,
                        self.currins_range,
                        self.currins_autorange,
                        self.sigin_float, 
                        self.currin_float, 
                        self.timeconstant, 
                        self.order
                    )
                self.vector = self.vector_obj.generate_vector(self.lockin_vector)
                self.dc_field = self.lockin.set_constant_field(self.dc_field / 0.6)
                sleep(1)
                self.vbias = self.lockin.set_constant_vbias(self.bias_voltage)
                sleep(1)

            elif self.mode == "Lockin calibration":
                pass

        elif self.mode == "TimeMode":
            self.rate_index = scope_rate(self.scope_rate)
            ####### Field sensor ########
            try:
                self.field_sensor = FieldSensor(self.field_sensor_adress)
                self.field_sensor.read_field_init()
            except:
                log.error("Config FieldSensor failed.")
                self.field_sensor = DummyFieldSensor()
                log.info("Use DummyFieldSensor")
            ########### Lockin #############
            try:
                self.lockin = LockinTime(self.lockin_adress)
               
               
                if self.differential_signal == True:
                    self.lockin.init_lockin(
                        0,
                        True,
                        float(self.sigin_range),
                        self.sigin_imp,
                        self.sigin_ac,
                        self.sigin_autorange,
                        self.currins_range,
                        self.currins_autorange,
                        self.external_ref,
                        self.sigin_float, 
                        self.currin_float, 
                        self.timeconstant, 
                        self.order
                    )
                else:
                    self.lockin.init_lockin(
                        0,
                        False,
                        float(self.sigin_range),
                        self.sigin_imp,
                        self.sigin_ac,
                        self.sigin_autorange,
                        self.currins_range,
                        self.currins_autorange,
                        self.external_ref,
                        self.sigin_float, 
                        self.currin_float, 
                        self.timeconstant, 
                        self.order
                    )
                self.lockin.init_scope(
                    self.avergaging_rate, 0, self.rate_index, self.scope_time
                )

            except Exception as a:
                log.error("Lockin init failed")
                self.stop_flag = True

            self.lockin.set_constant_vbias(self.bias_voltage)
            sleep(1)

############################################## RUN ###############################################
    def execute(self):
        if self.stop_flag == False:    
            diff = ComputeDiff()
            res = ComputerResistance()
            tmp_voltage = []
            tmp_current = []
            tmp_field_x = []
            tmp_field_y = []
            tmp_field_z = []
            tmp_resistance = []
            tmp_conductance = []
            tmp_field_set = []
            tmp_diff_x = []
            tmp_field_angle = []
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
             
                if IVTransfer.licznik == 0 and 'Hr' in self.vector_obj.generate_vector_input(self.vector_param): 

                    vector_to_saturation = self.vector_obj.generate_vector_input(self.vector_param)
                 
                    vector_to_saturation_list = list(np.linspace(0.0, float(vector_to_saturation[0]), 5))
                   
                    vector_to_saturation_list_2 = list(np.linspace(float(vector_to_saturation[0]), self.Hr, 5))
                    
                    vector_to_saturation_list.extend(vector_to_saturation_list_2)

                   
                    print("DEBUG: vector to saturation: {}".format(vector_to_saturation_list))
                if self.acquire_type == "I(Hdc) | set Vb":
                    if self.coil == "Large":
                        self.field_const = 5
                    else:
                        self.field_const = 10
                    w = 0
                    if IVTransfer.licznik == 0 and 'Hr' in self.vector_obj.generate_vector_input(self.vector_param): 
                        for k in vector_to_saturation_list:
                            if self.field_device == "2D Controller": 
                                self.field.set_field_value(self.field_angle, k)
                                sleep(self.delay * 0.001)
                            else:
                                self.field.set_field(k / self.field_const)
                                sleep(self.delay * 0.001)
                            print("DEBUG:set field to saturation: {}".format(k))
                    print("Mesure vector: {}".format(self.vector))

                    for i in self.vector:
                        self.last_value = i
                        if self.field_device == "2D Controller":
                            if self.sweep_by == "Angle":
                                self.field.set_field_value(i, self.field_bias)
                                tmp_field_angle.append(i)
                                tmp_field_set.append(self.field_bias)
                            else: 
                                self.field.set_field_value(self.field_angle, i)
                                tmp_field_angle.append(self.field_angle)
                                tmp_field_set.append(i)


                            
                        else:
                            self.field.set_field(i / self.field_const)
                            tmp_field_set.append(i)  # surowe pole
                        sleep(self.delay * 0.001)
                        print("DEBUG:set field measure: {}".format(i))
                        
                        
                        if self.field_device == "2D Controller":
                            self.tmp_field = self.field.get_field()
                            print("RAW field value:{}".format(self.tmp_field))
                            tmp_field_x.append(float(self.tmp_field[-3][7:]))
                            tmp_field_y.append(float(self.tmp_field[-2]))
                            tmp_field_z.append(float(self.tmp_field[-1]))


                        else:
                            self.tmp_field = self.field_sensor.read_field()
                            tmp_field_x.append(self.tmp_field[0])
                            tmp_field_y.append(self.tmp_field[1])
                            tmp_field_z.append(self.tmp_field[2])
                        sleep(self.delay * 0.001)
                        print("DEBUG: field masured:  {}".format(self.tmp_field))
                        if self.agilent == True:
                            self.tmp_current = self.agilent_34410.current_dc
                        else:
                            self.tmp_current = self.keithley.current
                        # surowe dane:
                        tmp_current.append(self.tmp_current)  # surowy prąd
                        tmp_voltage.append(self.keithley_voltage_bias)  # surowe napiecie
                        tmp_resistance.append(
                            float(self.keithley_voltage_bias) / float(self.tmp_current)
                            if self.tmp_current != 0
                            else np.nan
                        )  # surowa rezystancja
                        tmp_conductance.append(
                            1
                            / (float(self.keithley_voltage_bias) / float(self.tmp_current))
                            if self.tmp_current != 0
                            else np.nan
                        )  # surowa konduktancja

                        self.emit("progress", 100 * w / len(self.vector))
                        w = w + 1
                        if self.should_stop():
                            log.warning("USER STOP")
                            break
                    print(
                        "DEBUG:\n current: {} \n voltage: {} \n resistance: {} \n conductance: {}".format(
                            tmp_current, tmp_voltage, tmp_resistance, tmp_conductance
                        )
                    )
                    # opracowanie:
                    tmp_dI_dH = diff.diffs(tmp_field_set, tmp_current)
                    tmp_dR_dH = diff.diffs(tmp_field_set, tmp_resistance)
                    tmp_dG_dH = diff.diffs(tmp_field_set, tmp_conductance)
                    tmp_dI = diff.diffIV(tmp_current)
                    tmp_NdI = diff.NormalizedDiff(tmp_current)
                    tmp_SPdI = diff.SlopeDiff(tmp_current, self.vector)
                    tmp_HdIS = diff.HdIS(tmp_dI_dH, tmp_resistance)
                    tmp_HdR = diff.diffs(tmp_field_set, tmp_resistance)
                    tmp_HdG = diff.diffs(tmp_field_set, tmp_conductance)
                    tmp_dR = diff.diffIV(tmp_resistance)
                    tmp_dG = diff.diffIV(tmp_conductance)
                    tmp_NdR = diff.NormalizedDiff(tmp_resistance)
                    tmp_NdG = diff.NormalizedDiff(tmp_conductance)
                    tmp_HdRS = diff.HdIS(tmp_HdR, tmp_current)
                    tmp_HdGS = diff.HdIS(tmp_HdG, tmp_voltage)

                    for l in range(len(tmp_voltage)):
                        data = {
                            "V (V)": self.value_function(tmp_voltage, l),
                            "I (A)": self.value_function(tmp_current, l),
                            "R (ohm)": self.value_function(tmp_resistance, l),
                            "G": self.value_function(tmp_conductance, l),
                            "X field (Oe)": self.value_function(tmp_field_x, l),
                            "Y field (Oe)": self.value_function(tmp_field_y, l),
                            "Z field (Oe)": self.value_function(tmp_field_z, l),
                            "Hset (Oe)": self.value_function(tmp_field_set, l),
                            "dR/dH": self.value_function(tmp_dR_dH, l),
                            "dG/dH": self.value_function(tmp_dG_dH, l),
                            "dI": self.value_function(tmp_dI, l),
                            "dI/dH": self.value_function(tmp_dI_dH, l),
                            "NdI": self.value_function(tmp_NdI, l),
                            "SPdI": self.value_function(tmp_SPdI, l),
                            "HdIS": self.value_function(tmp_HdIS, l),
                            "HdR": self.value_function(tmp_HdR, l),
                            "HdG": self.value_function(tmp_HdG, l),
                            "dR": self.value_function(tmp_dR, l),
                            "dG": self.value_function(tmp_dG, l),
                            "NdR": self.value_function(tmp_NdR, l),
                            "NdG": self.value_function(tmp_NdG, l),
                            "HdRS": self.value_function(tmp_HdRS, l),
                            "HdGS": self.value_function(tmp_HdGS, l),
                            "Phase": self.value_function(tmp_field_angle, l)
                        }
                        self.emit("results", data)
                        self.stop_flag = False
                    #Sweep field to next value or 0 
                    if 'Hr' in self.vector_obj.generate_vector_input(self.vector_param):
                        if window.get_sequencer_len() == 0 or window.get_sequencer_len() == IVTransfer.licznik+1:
                            vector_to_zero_list = list(np.linspace(float(self.vector_obj.generate_vector_input(self.vector_param)[0]), 0, 5))
                            for p in vector_to_zero_list:
                                if self.field_device == "2D Controller":
                                    self.field.set_field_value(self.field_angle, p)
                                    sleep(self.delay * 0.001)
                                else:
                                    self.field.set_field(p / self.field_const)
                                    sleep(self.delay * 0.001)
                                print("DEBUG:set field to zero: {}".format(p))

                        else:
                            vector_to_zero_list = list(np.linspace(float(self.vector_obj.generate_vector_input(self.vector_param)[0]), self.Hr, 5))
                            for p in vector_to_zero_list:
                                if self.field_device == "2D Controller":
                                    self.field.set_field_value(self.field_angle, p)
                                    sleep(self.delay * 0.001)
                                else: 
                                    self.field.set_field(p / self.field_const)
                                    sleep(self.delay * 0.001)
                                print("DEBUG:set field to next value: {}".format(p))
                    else: 
                        if self.reverse_field == False:
                            vector_to_zero_list = list(np.linspace(float(self.vector_obj.generate_vector_input(self.vector_param)[2]), 0, 5))
                        else: 
                            vector_to_zero_list = list(np.linspace(float(self.vector_obj.generate_vector_input(self.vector_param)[0]), 0, 5))
                        for p in vector_to_zero_list:
                            if self.field_device == "2D Controller":
                                self.field.set_field_value(self.field_angle, p)
                            else: 
                                self.field.set_field(p / self.field_const)
                            sleep(self.delay * 0.001)
                            print("DEBUG:set field to zero: {}".format(p))
                        
                elif self.acquire_type == "V(Hdc) | set Vb":
         
                    if self.coil == "Large":
                        self.field_const = 5
                    else:
                        self.field_const = 10
                    w = 0
                    if IVTransfer.licznik == 0 and 'Hr' in self.vector_obj.generate_vector_input(self.vector_param): 
                        for k in vector_to_saturation_list:
                            for k in vector_to_saturation_list:
                                if self.field_device == "2D Controller": 
                                    self.field.set_field_value(self.field_angle, k)
                                    sleep(self.delay * 0.001)
                                else:
                                    self.field.set_field(k / self.field_const)
                                    sleep(self.delay * 0.001)
                            print("DEBUG:set field to saturation: {}".format(k))
                    
                    for i in self.vector:
                        self.last_value = i
                        if self.field_device == "2D Controller":
                            if self.sweep_by == "Angle":
                                self.field.set_field_value(i, self.field_bias)
                                tmp_field_angle.append(i)
                                tmp_field_set.append(self.field_bias)
                            else: 
                                self.field.set_field_value(self.field_angle, i)
                                tmp_field_angle.append(self.field_angle)
                                tmp_field_set.append(i)
                        
                        else:
                            self.field.set_field(i / self.field_const)
                            tmp_field_set.append(i)  # surowe pole
                        sleep(self.delay * 0.001)
                        print("DEBUG:set field measure: {}".format(i))
                        
                        if self.field_device == "2D Controller":
                            self.tmp_field = self.field.get_field()
                            print("RAW field value:{}".format(self.tmp_field))
                            tmp_field_x.append(float(self.tmp_field[-3][7:]))
                            tmp_field_y.append(float(self.tmp_field[-2]))
                            tmp_field_z.append(float(self.tmp_field[-1]))
                        else:
                            self.tmp_field = self.field_sensor.read_field()
                            tmp_field_x.append(self.tmp_field[0])
                            tmp_field_y.append(self.tmp_field[1])
                            tmp_field_z.append(self.tmp_field[2])
                        sleep(self.delay * 0.001)
                        print("DEBUG: field masured:  {}".format(self.tmp_field))


                        try:
                            if self.agilent == True:
                                self.tmp_volatage = self.agilent_34410.voltage_dc
                            else: 
                                self.tmp_volatage = math.nan
                            
                            self.tmp_current = self.keithley.current
                        except Exception as exception: 
                            log.error(f"Measurement failed")
                            break

                        
                        
                        
                        
                        # surowe dane:
                        tmp_current.append(self.tmp_current)  # surowy prąd
                        tmp_voltage.append(self.tmp_volatage)  # surowe napiecie
                        tmp_resistance.append(
                            float(self.keithley_voltage_bias) / float(self.tmp_current)
                            if self.tmp_current != 0
                            else np.nan
                        )  # surowa rezystancja
                        tmp_conductance.append(
                            1
                            / (float(self.keithley_voltage_bias) / float(self.tmp_current))
                            if self.tmp_current != 0
                            else np.nan
                        )  # surowa konduktancja

                        self.emit("progress", 100 * w / len(self.vector))
                        w = w + 1
                        if self.should_stop():
                            log.warning("USER STOP")
                            break
                    print(
                        "DEBUG:\n current: {} \n voltage: {} \n resistance: {} \n conductance: {}".format(
                            tmp_current, tmp_voltage, tmp_resistance, tmp_conductance
                        )
                    )
                    # opracowanie:
                    tmp_dI_dH = diff.diffs(tmp_field_set, tmp_current)
                    tmp_dR_dH = diff.diffs(tmp_field_set, tmp_resistance)
                    tmp_dG_dH = diff.diffs(tmp_field_set, tmp_conductance)
                    tmp_dI = diff.diffIV(tmp_current)
                    tmp_NdI = diff.NormalizedDiff(tmp_current)
                    tmp_SPdI = diff.SlopeDiff(tmp_current, self.vector)
                    tmp_HdIS = diff.HdIS(tmp_dI_dH, tmp_resistance)
                    tmp_HdR = diff.diffs(tmp_field_set, tmp_resistance)
                    tmp_HdG = diff.diffs(tmp_field_set, tmp_conductance)
                    tmp_dR = diff.diffIV(tmp_resistance)
                    tmp_dG = diff.diffIV(tmp_conductance)
                    tmp_NdR = diff.NormalizedDiff(tmp_resistance)
                    tmp_NdG = diff.NormalizedDiff(tmp_conductance)
                    tmp_HdRS = diff.HdIS(tmp_HdR, tmp_current)
                    tmp_HdGS = diff.HdIS(tmp_HdG, tmp_voltage)

                    for l in range(len(tmp_voltage)):
                        data = {
                            "Vsense (V)": self.value_function(tmp_voltage, l),
                            "I (A)": self.value_function(tmp_current, l),
                            "Vbias (V)": self.keithley_voltage_bias,
                            "R (ohm)": self.value_function(tmp_resistance, l),
                            "G": self.value_function(tmp_conductance, l),
                            "X field (Oe)": self.value_function(tmp_field_x, l),
                            "Y field (Oe)": self.value_function(tmp_field_y, l),
                            "Z field (Oe)": self.value_function(tmp_field_z, l),
                            "Hset (Oe)": self.value_function(tmp_field_set, l),
                            "dR/dH": self.value_function(tmp_dR_dH, l),
                            "dG/dH": self.value_function(tmp_dG_dH, l),
                            "dI": self.value_function(tmp_dI, l),
                            "dI/dH": self.value_function(tmp_dI_dH, l),
                            "NdI": self.value_function(tmp_NdI, l),
                            "SPdI": self.value_function(tmp_SPdI, l),
                            "HdIS": self.value_function(tmp_HdIS, l),
                            "HdR": self.value_function(tmp_HdR, l),
                            "HdG": self.value_function(tmp_HdG, l),
                            "dR": self.value_function(tmp_dR, l),
                            "dG": self.value_function(tmp_dG, l),
                            "NdR": self.value_function(tmp_NdR, l),
                            "NdG": self.value_function(tmp_NdG, l),
                            "HdRS": self.value_function(tmp_HdRS, l),
                            "HdGS": self.value_function(tmp_HdGS, l),
                            "Phase": self.value_function(tmp_field_angle, l)
                        }
                        self.emit("results", data)
                        stop_flag = False
                     #Sweep field to next value or 0 
                    if 'Hr' in self.vector_obj.generate_vector_input(self.vector_param):
                        if window.get_sequencer_len() == 0 or window.get_sequencer_len() == IVTransfer.licznik+1:
                            vector_to_zero_list = list(np.linspace(float(self.vector_obj.generate_vector_input(self.vector_param)[0]), 0, 5))
                            for p in vector_to_zero_list:
                                if self.field_device == "2D Controller":
                                    self.field.set_field_value(self.field_angle, p)
                                    sleep(self.delay * 0.001)
                                else:
                                    self.field.set_field(p / self.field_const)
                                    sleep(self.delay * 0.001)
                                print("DEBUG:set field to zero: {}".format(p))

                        else:
                            vector_to_zero_list = list(np.linspace(float(self.vector_obj.generate_vector_input(self.vector_param)[0]), self.Hr, 5))
                            for p in vector_to_zero_list:
                                if self.field_device == "2D Controller":
                                    self.field.set_field_value(self.field_angle, p)
                                    sleep(self.delay * 0.001)
                                else: 
                                    self.field.set_field(p / self.field_const)
                                    sleep(self.delay * 0.001)
                                print("DEBUG:set field to next value: {}".format(p))
                    else: 
                        if self.reverse_field == False:
                            vector_to_zero_list = list(np.linspace(float(self.vector_obj.generate_vector_input(self.vector_param)[2]), 0, 5))
                        else: 
                            vector_to_zero_list = list(np.linspace(float(self.vector_obj.generate_vector_input(self.vector_param)[0]), 0, 5))
                        for p in vector_to_zero_list:
                            if self.field_device == "2D Controller":
                                self.field.set_field_value(self.field_angle, p)
                            else: 
                                self.field.set_field(p / self.field_const)
                            sleep(self.delay * 0.001)
                            print("DEBUG:set field to zero: {}".format(p))

                elif self.acquire_type == "V(Hdc) |set Ib":
                    if self.coil == "Large":
                        self.field_const = 5
                    else:
                        self.field_const = 10
                    w = 0
                    if IVTransfer.licznik == 0 and 'Hr' in self.vector_obj.generate_vector_input(self.vector_param): 
                        for k in vector_to_saturation_list:
                            if self.field_device == "2D Controller": 
                                self.field.set_field_value(self.field_angle, k)
                                sleep(self.delay * 0.001)
                            else:
                                self.field.set_field(k / self.field_const)
                                sleep(self.delay * 0.001)
                            print("DEBUG:set field to saturation: {}".format(k))
                    print("Mesure vector: {}".format(self.vector))
                    
                    for i in self.vector:
                        self.last_value = i
                        if self.field_device == "2D Controller":
                            if self.sweep_by == "Angle":
                                self.field.set_field_value(i, self.field_bias)
                                tmp_field_angle.append(i)
                                tmp_field_set.append(self.field_bias)
                            else: 
                                self.field.set_field_value(self.field_angle, i)
                                tmp_field_angle.append(self.field_angle)
                                tmp_field_set.append(i)
                        else:
                            self.field.set_field(i / self.field_const)
                            tmp_field_set.append(i)  # surowe pole
                        sleep(self.delay * 0.001)
                        print("DEBUG:set field measure: {}".format(i))
                        if self.field_device == "2D Controller":
                            self.tmp_field = self.field.get_field()
                            print("RAW field value:{}".format(self.tmp_field))
                            tmp_field_x.append(float(self.tmp_field[-3][7:]))
                            tmp_field_y.append(float(self.tmp_field[-2]))
                            tmp_field_z.append(float(self.tmp_field[-1]))


                        else:
                            self.tmp_field = self.field_sensor.read_field()
                            tmp_field_x.append(self.tmp_field[0])
                            tmp_field_y.append(self.tmp_field[1])
                            tmp_field_z.append(self.tmp_field[2])
                        sleep(self.delay * 0.001)
                        print("DEBUG: field masured:  {}".format(self.tmp_field))
                        
                        
                        if self.agilent == True:
                            self.tmp_volatage = self.agilent_34410.voltage_dc
                        else:
                            self.tmp_volatage = self.keithley.voltage
                        # surowe dane:

                        tmp_current.append(self.keithley_current_bias)
                        tmp_voltage.append(self.tmp_volatage)
                        tmp_resistance.append(
                            float(self.tmp_volatage) / float(self.keithley_current_bias)
                            if self.keithley_current_bias != 0
                            else np.nan
                        )
                        tmp_conductance.append(
                            1
                            / (float(self.tmp_volatage) / float(self.keithley_current_bias))
                            if self.keithley_current_bias != 0
                            else np.nan
                        )  # surowa konduktancja
                        self.emit("progress", 100 * w / len(self.vector))
                        w = w + 1
                        if self.should_stop():
                            log.warning("USER STOP")
                            break
                    print(
                        "DEBUG:\n current: {} \n voltage: {} \n resistance: {} \n conductance: {}".format(
                            tmp_current, tmp_voltage, tmp_resistance, tmp_conductance
                        )
                    )                
                    # opracowanie:
                    tmp_dV_dH = diff.diffs(tmp_field_set, tmp_voltage)
                    tmp_dR_dH = diff.diffs(tmp_field_set, tmp_resistance)
                    tmp_dG_dH = diff.diffs(tmp_field_set, tmp_conductance)
                    tmp_dV = diff.diffIV(tmp_voltage)
                    tmp_NdV = diff.NormalizedDiff(tmp_voltage)
                    tmp_SPdV = diff.SlopeDiff(tmp_voltage, self.vector)
                    tmp_HdVS = diff.HdIS(tmp_dV_dH, tmp_resistance)
                    tmp_HdR = diff.diffs(tmp_field_set, tmp_resistance)
                    tmp_HdG = diff.diffs(tmp_field_set, tmp_conductance)
                    tmp_dR = diff.diffIV(tmp_resistance)
                    tmp_dG = diff.diffIV(tmp_conductance)
                    tmp_NdR = diff.NormalizedDiff(tmp_resistance)
                    tmp_NdG = diff.NormalizedDiff(tmp_conductance)
                    tmp_HdRS = diff.HdIS(tmp_HdR, tmp_current)
                    tmp_HdGS = diff.HdIS(tmp_HdG, tmp_voltage)

                    for l in range(len(tmp_voltage)):
                        data = {
                            "V (V)": self.value_function(tmp_voltage, l),
                            "R (ohm)": self.value_function(tmp_resistance, l),
                            "G": self.value_function(tmp_conductance, l),
                            "X field (Oe)": self.value_function(tmp_field_x, l),
                            "Y field (Oe)": self.value_function(tmp_field_y, l),
                            "Z field (Oe)": self.value_function(tmp_field_z, l),
                            "Hset (Oe)": self.value_function(tmp_field_set, l),
                            "dR/dH": self.value_function(tmp_dR_dH, l),
                            "dG/dH": self.value_function(tmp_dG_dH, l),
                            "dV": self.value_function(tmp_dV, l),
                            "dV/dH": self.value_function(tmp_dV_dH, l),
                            "NdV": self.value_function(tmp_NdV, l),
                            "SPdV": self.value_function(tmp_SPdV, l),
                            "HdVS": self.value_function(tmp_HdVS, l),
                            "HdR": self.value_function(tmp_HdR, l),
                            "HdG": self.value_function(tmp_HdG, l),
                            "dR": self.value_function(tmp_dR, l),
                            "dG": self.value_function(tmp_dG, l),
                            "NdR": self.value_function(tmp_NdR, l),
                            "NdG": self.value_function(tmp_NdG, l),
                            "HdRS": self.value_function(tmp_HdRS, l),
                            "HdGS": self.value_function(tmp_HdGS, l),
                            "Phase": self.value_function(tmp_field_angle, l)
                        }
                        self.emit("results", data)
                        stop_flag = False
                    if 'Hr' in self.vector_obj.generate_vector_input(self.vector_param):
                        if window.get_sequencer_len() == 0 or window.get_sequencer_len() == IVTransfer.licznik+1:
                            vector_to_zero_list = list(np.linspace(float(self.vector_obj.generate_vector_input(self.vector_param)[0]), 0, 5))
                            for p in vector_to_zero_list:
                                if self.field_device == "2D Controller":
                                    self.field.set_field_value(self.field_angle, p)
                                    sleep(self.delay * 0.001)
                                else:
                                    self.field.set_field(p / self.field_const)
                                    sleep(self.delay * 0.001)
                                print("DEBUG:set field to zero: {}".format(p))

                        else:
                            vector_to_zero_list = list(np.linspace(float(self.vector_obj.generate_vector_input(self.vector_param)[0]), self.Hr, 5))
                            for p in vector_to_zero_list:
                                if self.field_device == "2D Controller":
                                    self.field.set_field_value(self.field_angle, p)
                                    sleep(self.delay * 0.001)
                                else: 
                                    self.field.set_field(p / self.field_const)
                                    sleep(self.delay * 0.001)
                                print("DEBUG:set field to next value: {}".format(p))
                    
                    else: 
                        if self.reverse_field == False:
                            vector_to_zero_list = list(np.linspace(float(self.vector_obj.generate_vector_input(self.vector_param)[2]), 0, 5))
                        else: 
                            vector_to_zero_list = list(np.linspace(float(self.vector_obj.generate_vector_input(self.vector_param)[0]), 0, 5))
                        for p in vector_to_zero_list:
                            if self.field_device == "2D Controller":
                                self.field.set_field_value(self.field_angle, p)
                            else: 
                                self.field.set_field(p / self.field_const)
                            sleep(self.delay * 0.001)
                            print("DEBUG:set field to zero: {}".format(p))

                elif self.acquire_type == "I(Vb) | set Hdc":
                  
                    w = 0

                    for i in self.vector:
                        tmp_field_set.append(self.field_bias)
                        tmp_field_angle.append(self.field_angle)

                        self.keithley.source_voltage = i
                        sleep(self.delay * 0.001)
                        if self.agilent == True:
                            self.tmp_current = self.agilent_34410.current_dc
                        else:
                            self.tmp_current = self.keithley.current
                        sleep(self.delay * 0.001)
                        
                        if self.field_device == "2D Controller":
                            self.tmp_field = self.field.get_field()
                            print("RAW field value:{}".format(self.tmp_field))
                            tmp_field_x.append(float(self.tmp_field[-3][7:]))
                            tmp_field_y.append(float(self.tmp_field[-2]))
                            tmp_field_z.append(float(self.tmp_field[-1]))

                        else:
                            self.tmp_field = self.field_sensor.read_field()
                            tmp_field_x.append(self.tmp_field[0])
                            tmp_field_y.append(self.tmp_field[1])
                            tmp_field_z.append(self.tmp_field[2])
                        
                        
                        
                        # surowe
                        tmp_current.append(self.tmp_current)
                        tmp_voltage.append(i)
                        tmp_resistance.append(
                            float(i) / float(self.tmp_current)
                            if self.tmp_current != 0
                            else math.nan
                        )
                        tmp_conductance.append(
                            1 / (float(i) / float(self.tmp_current))
                            if self.tmp_current != 0 and i != 0
                            else math.nan
                        )

                        self.emit("progress", 100 * w / len(self.vector))
                        w = w + 1
                        if self.should_stop():
                            log.warning("USER STOP")
                            break

                    # opracowanie:
                    tmp_dI_dV = diff.diffs(tmp_voltage, tmp_current)
                    tmp_dI = diff.diffIV(tmp_current)
                    tmp_dR = diff.diffIV(tmp_resistance)
                    tmp_dG = diff.diffIV(tmp_conductance)

                    for l in range(len(tmp_voltage)):
                        data = {
                            "V (V)": self.value_function(tmp_voltage, l),
                            "I (A)": self.value_function(tmp_current, l),
                            "R (ohm)": self.value_function(tmp_resistance, l),
                            "G": self.value_function(tmp_conductance, l),
                            "X field (Oe)": self.value_function(tmp_field_x, l),
                            "Y field (Oe)": self.value_function(tmp_field_y, l),
                            "Z field (Oe)": self.value_function(tmp_field_z, l),
                            "Hset (Oe)": self.value_function(tmp_field_set, l),
                            "dI": self.value_function(tmp_dI, l),
                            "dI/dV": self.value_function(tmp_dI_dV, l),
                            "dR": self.value_function(tmp_dR, l),
                            "dG": self.value_function(tmp_dG, l),
                            "Phase": self.value_function(tmp_field_angle, l)
                        }
                        self.emit("results", data)
                        stop_flag = False

                elif self.acquire_type == "V(Ib) | set Hdc":
               
                    w = 0
                    for i in self.vector:
                        tmp_field_set.append(self.field_bias)
                        tmp_field_angle.append(self.field_angle)

                        self.keithley.source_current = i
                        sleep(self.delay * 0.001)
                        if self.agilent == True:
                            self.tmp_volatage = self.agilent_34410.voltage_dc
                        else:
                            self.tmp_volatage = self.keithley.voltage
                        sleep(self.delay * 0.001)

                        if self.field_device == "2D Controller":
                            self.tmp_field = self.field.get_field()
                            tmp_field_x.append(self.tmp_field[0])
                            tmp_field_y.append(self.tmp_field[1])
                            tmp_field_z.append(self.tmp_field[2])


                        else:
                            self.tmp_field = self.field_sensor.read_field()
                            tmp_field_x.append(self.tmp_field[0])
                            tmp_field_y.append(self.tmp_field[1])
                            tmp_field_z.append(self.tmp_field[2])

                        tmp_current.append(i)
                        tmp_voltage.append(self.tmp_volatage)
                        tmp_resistance.append(
                            float(self.tmp_volatage) / (i if i != 0 else 1e-9)
                        )
                        tmp_conductance.append((float(i) / float(self.tmp_volatage)))
                        self.emit("progress", 100 * w / len(self.vector))
                        w = w + 1
                        if self.should_stop():
                            log.warning("USER STOP")
                            break

                    # opracowanie:
                    tmp_dV_dI = diff.diffs(tmp_current, tmp_voltage)
                    tmp_dV = diff.diffIV(tmp_voltage)
                    tmp_dR = diff.diffIV(tmp_resistance)
                    tmp_dG = diff.diffIV(tmp_conductance)

                    for l in range(len(tmp_voltage)):
                        data = {
                            "V (V)": self.value_function(tmp_voltage, l),
                            "I (A)": self.value_function(tmp_current, l),
                            "R (ohm)": self.value_function(tmp_resistance, l),
                            "G": self.value_function(tmp_conductance, l),
                            "X field (Oe)": self.value_function(tmp_field_x, l),
                            "Y field (Oe)": self.value_function(tmp_field_y, l),
                            "Z field (Oe)": self.value_function(tmp_field_z, l),
                            "Hset (Oe)": self.value_function(tmp_field_set, l),
                            "dV": self.value_function(tmp_dV, l),
                            "dV/dI": self.value_function(tmp_dV_dI, l),
                            "dR": self.value_function(tmp_dR, l),
                            "dG": self.value_function(tmp_dG, l),
                            "Phase": self.value_function(tmp_field_angle, l)
                        }
                        self.emit("results", data)
                        stop_flag = False

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

            elif self.mode == "HDC-ACModeLockin": 
                if self.mode_lockin == "Sweep field":
                    if self.kepco == False:
                        # self.calibration_field = LockinCalibration(
                        #     self.lockin,
                        #     self.ac_field_frequency,
                        #     self.dc_field,
                        #     self.coil_constant,
                        # )
                        # self.cal_field_const = self.calibration_field.calibrate()
                        self.lockin.set_dc_field(self.dc_field / (1/self.coil_constant))
                    else:
                        self.lockin.set_dc_field(self.dc_field / (1/self.coil_constant))

                    # self.lockin.set_lockin_freq(self.lockin_frequency)
                    self.counter = 0

                    for i in self.vector:
                        if self.amplitude_vec == True:
                            self.lockin.set_ac_field( 
                                i / (1/self.coil_constant), self.ac_field_frequency)
                        else:
                            self.lockin.set_ac_field(
                                self.ac_field_amplitude / (1/self.coil_constant), i)
                        if i != 0:
                            sleep(2 / i)
                        else:
                            sleep(1)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          

                        r = self.lockin.lockin_measure_R(0, self.avergaging_rate)
                        theta = self.lockin.lockin_measure_phase(0, self.avergaging_rate)
                        r2 = self.lockin.lockin_measure_R(1, self.avergaging_rate)
                        theta2 = self.lockin.lockin_measure_phase(1, self.avergaging_rate)
                
                        self.counter = self.counter + 1

                        self.emit("progress", 100 * self.counter / len(self.vector))

                        try:

                            data_lockin = {
                                "f (Hz)": (
                                    i
                                    if self.amplitude_vec == False
                                    else self.ac_field_frequency
                                ),
                                "AHac (Oe)": (
                                    i
                                    if self.amplitude_vec == True
                                    else self.ac_field_amplitude
                                ),
                                "Vsense (V)": r,
                                "Vbias (V)": self.bias_voltage / 1000,
                                "Hset (Oe)": (
                                    i + self.dc_field
                                    if self.amplitude_vec == True
                                    else self.ac_field_amplitude + self.dc_field
                                ),
                                "I (A)": r2,
                                "Phase": theta,
                                "I/Phase": r2 / theta,
                                "V/Phase": r / theta,
                                "I/Ax": (
                                    r2 / self.ac_field_amplitude
                                   
                                ),
                            }

                            self.emit("results", data_lockin)
                        except Exception as e:
                            print(e)
                            self.should_stop()
                        if self.should_stop():
                            log.warning("USER STOP")
                            break

                elif self.mode_lockin == "Sweep voltage":
                    # if self.kepco == False:
                    #     # self.calibration_field = LockinCalibration(
                    #     #     self.lockin,
                    #     #     self.ac_field_frequency,
                    #     #     self.dc_field,
                    #     #     self.coil_constant,
                    #     # )
                    #     # self.cal_field_const = self.calibration_field.calibrate()
                    #     self.lockin.set_dc_field(self.bias_voltage)                     # OUTPUT: SET DC VOLTAGE
                    # else:
                    #     self.lockin.set_dc_field(self.bias_voltage)

                    # self.lockin.set_lockin_freq(self.lockin_frequency)
                    self.lockin.set_ac_field(self.ac_voltage_amplitude , self.ac_voltage_frequency)
                    self.counter = 0

                    for i in self.vector:
                        self.lockin.set_dc_field(i)  # OUTPUT: SET DC VOLTAGE
                        if i != 0:
                            sleep(2 / i)
                        else:
                            sleep(1)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          

                        r = self.lockin.lockin_measure_R(2, self.avergaging_rate)
                        theta = self.lockin.lockin_measure_phase(2, self.avergaging_rate)
                        r2 = self.lockin.lockin_measure_R(0, self.avergaging_rate)
                        theta2 = self.lockin.lockin_measure_phase(0, self.avergaging_rate)
                        self.counter = self.counter + 1

                        self.emit("progress", 100 * self.counter / len(self.vector))

                        try:

                            data_lockin = {
                                "f (Hz)": (
                                   self.ac_voltage_frequency
                                ),

                                "Vsense (V)": (
                                    self.ac_voltage_amplitude
                                ),
                                "Vbias (V)": i,
                                "X field (Oe)": (
                                    i + self.dc_field
                                    if self.amplitude_vec == True
                                    else self.ac_field_amplitude + self.dc_field
                                ),
                                "Y field (Oe)": 0,
                                "Z field (Oe)": 0,
                                "I (A)": r2,
                                "Phase": theta,
                            }

                            self.emit("results", data_lockin)
                        except Exception as e:
                            print(e)
                            self.should_stop()
                        if self.should_stop():
                            log.warning("USER STOP")
                            break

                elif self.mode_lockin == "Sweep frequency":
                    self.field_value = measure_field(1, self.field_sensor, self.should_stop)
                    sleep(2)
                    self.factor_period = 5
                    self.time_first_loop = 3
                    self.counter = 0
                    for i in self.vector:
                        if self.counter ==0:
                            self.iter = 2 
                        else: 
                            self.iter = 1
                        for w in range(self.iter):
                            self.lockin.set_lockin_freq(i)
                            if self.counter == 0:
                                sleep(self.time_first_loop)

                            if i != 0:
                                sleep(self.factor_period*(1/i))
                            else:
                                sleep(self.time_first_loop)
                            r = self.lockin.lockin_measure_R(0, self.avergaging_rate)
                            if self.counter == 0:
                                sleep(self.time_first_loop)
                            if i != 0:
                                sleep(self.factor_period*(1/i))
                            else:
                                sleep(self.time_first_loop)
                            theta = self.lockin.lockin_measure_phase(0, self.avergaging_rate)
                            if self.counter == 0:
                                sleep(self.time_first_loop)
                            if i != 0:
                                sleep(self.factor_period*(1/i))
                            else:
                                sleep(self.time_first_loop)
                            r2 = self.lockin.lockin_measure_R(1, self.avergaging_rate)
                            if self.counter == 0:
                                sleep(self.time_first_loop)
                            if i != 0:
                                sleep(self.factor_period*(1/i))
                            else:
                                sleep(self.time_first_loop)
                            theta2 = self.lockin.lockin_measure_phase(1, self.avergaging_rate)
                            self.counter = self.counter + 1

     
                        self.emit("progress", 100 * self.counter / len(self.vector))
                        try:
                            data_lockin = {
                                "f (Hz)": i,
                                "Vsense (V)": (
                                    r 
                                ),
                                "Vbias (V)": self.bias_voltage,
                                "Hset (Oe)": self.dc_field,
                                "X field (Oe)": self.field_value[0],
                                "Y field (Oe)": self.field_value[1],
                                "Z field (Oe)": self.field_value[2],
                                "I (A)": r2,
                                "Phase": theta,
                                "I/Phase": r2 / theta,
                                "V/Phase": r/theta,
                                "I/Ax": (
                                    r2 / self.ac_field_amplitude
                                ),
                            }

                            self.emit("results", data_lockin)
                        except:
                            self.should_stop()
                        if self.should_stop():
                            log.warning("USER STOP")
                            break

            elif self.mode == "TimeMode":
                if self.kepco == False:
                    # self.calibration_field = LockinCalibration(
                    #     self.lockin,
                    #     self.ac_field_frequency_time,
                    #     self.dc_field_time,
                    #     self.coil_constant,
                    # )
                    # self.cal_field_const = self.calibration_field.calibrate()
                    self.lockin.set_dc_field(self.dc_field_time / (1/self.coil_constant))
                else:
                    self.lockin.set_dc_field(self.dc_field_time / (1/self.coil_constant))

                self.lockin.set_lockin_freq(self.lockin_frequency)
                self.lockin.set_ac_field(
                    self.ac_field_amplitude_time / (1/self.coil_constant), self.ac_field_frequency_time
                )
                sleep(2)
                scope_signal = self.lockin.get_wave()
                self.emit("progress", 100)
                try:
                    for w in range(len(scope_signal[0])):
                        data_lockin = {
                            "time (s)": scope_signal[0][w],
                            "f (Hz)": self.ac_field_frequency_time,
                            "AHac (Oe)": self.ac_field_amplitude_time,
                            "Vsense (V)": (
                                float(scope_signal[1][w])
                            ),
                            "Vbias (V)": self.bias_voltage,
                            "X field (Oe)": 0,
                            "Y field (Oe)": 0,
                            "Z field (Oe)": 0,
                            "I (A)": (
                                float(scope_signal[2][w])
                               
                            ),
                            "Hset (Oe)": self.ac_field_amplitude_time + self.dc_field_time,
                            "G(t)": (
                                float(scope_signal[1][w]) / self.bias_voltage
                                
                            ),
                            "R(t)": (
                                self.bias_voltage / float(scope_signal[1][w])
                                
                            ),
                        }

                        self.emit("results", data_lockin)
                except Exception as e:
                    print(e)
                    self.should_stop()
                if self.should_stop():
                    log.warning("USER STOP")
        else: 
            raise Exception("Device error, please check connections")

    def shutdown(self):

        if self.stop_flag == False:
            print("LICZNIK:{}".format(IVTransfer.licznik))
            if window.get_sequencer_len() == 0 or window.get_sequencer_len() == IVTransfer.licznik+1:
                print("last loop")
                if self.mode == "HDCMode":
                    if self.field_device == "DAQ":
                        self.field.shutdown()
                        print("pole wyłączone")
                    elif self.field_device == "2D Controller":
                        self.field.shutdown()
                        print("pole wyłączone")
                    else: 
                        if (
                            self.acquire_type == "I(Hdc) | set Vb"
                            or self.acquire_type == "V(Hdc) |set Ib" or self.acquire_type == "V(Hdc) |set Vb" ):
                            self.field.shutdown(self.last_value / self.field_const)
                            print("pole wyłączone")
                        else:
                            self.field.shutdown(self.field_bias / self.field_const)
                            print("pole wyłączone")
                    sleep(0.2)
                    
                    self.keithley.shutdown()
                    print("keithley shutdown done")
                    IVTransfer.licznik = 0
                elif self.mode == "HDC-ACModeLockin":
                    self.lockin.shutdown()
                elif self.mode == "TimeMode":
                    self.lockin.shutdown()
            else:
                if self.mode == "HDCMode":
                    self.keithley.shutdown()
                    print("go next loop...")
                    IVTransfer.licznik += 1
            
        else: 
            pass


class MainWindow(ManagedWindow):
    last = False

    def __init__(self):
        super().__init__(
            procedure_class=IVTransfer,
            inputs=[
                "mode",
                "mode_lockin",
                "sample_name",
                "vector_param",
                "lockin_vector",
                "coil",
                "coil_constant",
                "acquire_type",
                "keithley_adress",
                "agilent",
                "agilent34401a_adress",
                "field_sensor_adress",
                "keithley_compliance_current",
                "keithley_compliance_voltage",
                "keithley_current_bias",
                "keithley_voltage_bias",
                "field_device",
                "sweep_by",
                "field_angle",
                "Field2DController_address",
                "Field2DController_average",
                "field_bias",
                "agilent_adress",
                "delay",
                "reverse_field",
                "lockin_adress",
                "sigin_imp",
                "timeconstant", 
                "order", 
                "currins_range",
                "currins_autorange",
                "sigin_range",
                "sigin_autorange",
                "sigin_ac",
                "differential_signal",
                "sigin_float",
                "currin_float",
                "kepco",
                "dc_field",
                "dc_field_time",
                "bias_voltage",
                "ac_field_amplitude",
                "ac_field_frequency",
                "ac_voltage_frequency",
                "ac_voltage_amplitude",
                "ac_field_amplitude_time",
                "ac_field_frequency_time",
                "external_ref",
                "lockin_frequency",
                "avergaging_rate",
                "scope_rate",
                "scope_time",
                "amplitude_vec",
            ],
            displays=[
                "sample_name",
                "mode",
                "dc_field",
                "bias_voltage",
                "ac_field_amplitude",
                "ac_field_frequency",
                "lockin_frequency",
            ],
            x_axis="I (A)",
            y_axis="V (V)",
            directory_input=True,
            sequencer=True,
            sequencer_inputs=[
                "Hr",
                "field_bias",
                "keithley_current_bias",
                "keithley_voltage_bias",
                "ac_field_amplitude",
                "ac_field_frequency",
            ],
            inputs_in_scrollarea=True,
        )

        self.setWindowTitle("IV Measurement System v.0.99.9")
        self.directory = self.procedure_class.path_file.ReadFile()

    def get_sequencer_len(self):
        return self.sequencer.get_sequence_lenght()

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



if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
