import pyvisa 
from time import sleep
from pyvisa.constants import StopBits, Parity
from pyvisa import constants
rm = pyvisa.ResourceManager() 
print(rm.list_resources()) 
inst = rm.open_resource('ASRL/dev/ttyS0::INSTR',baud_rate=110, data_bits=8, flow_control=constants.VI_ASRL_FLOW_RTS_CTS, parity = Parity.none, stop_bits=StopBits.one)  

#inst = rm.open_resource('ASRL/dev/ttyUSB0::INSTR')
inst.timeout = 25000

sleep(2)
#inst.write('*IDN?')
# inst.write('*RST')
#sleep(2)
inst.write('VOLT 4')
sleep(2)
# inst.write('OPON 1')
# sleep(2)
inst.write("VOLT?")
sleep(2)
print(inst.read())
# sleep(2)
# #print(inst.read())

# print(inst.query('*IDN?'))
inst.close()
