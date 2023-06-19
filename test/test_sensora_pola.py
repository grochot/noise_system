import time
import serial
from ..hardware.field_sensor_noise_new import FieldSensor

test = FieldSensor('ASRL/dev/ttyUSB0::INSTR')

test.read_field_init()

test.read_field()
