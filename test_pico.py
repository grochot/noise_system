import pyvisa 
from time import sleep
from pyvisa.constants import StopBits, Parity
from pyvisa import constants
rm = pyvisa.ResourceManager() 
print(rm.list_resources()) 
inst = rm.open_resource("ASRL/dev/ttyUSB0::INSTR",baud_rate=115200, data_bits=7, flow_control=constants.VI_ASRL_FLOW_RTS_CTS, parity = Parity.none, stop_bits=StopBits.one)  
inst.timeout = 25000

#inst.write('*CLS')
#inst.write('*RST')
#inst.write('VOLT 1')
sleep(2)
#print(inst.read())

print(inst.query('VOLT?'))
#inst.close()
