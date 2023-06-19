import pyvisa 
from time import sleep
from pyvisa.constants import StopBits, Parity
from pyvisa import constants
pyvisa.ResourceManager('@py')
rm = pyvisa.ResourceManager()
print(rm.list_resources()) 


inst = rm.open_resource('ASRL/dev/ttyUSB0::INSTR')  

# inst = rm.open_resource('ASRL/dev/ttyS0::INSTR')
# inst.write_termination = "\n"
# inst.read_termination = "\n"
inst.write("*IDN?")
inst.read_bytes(1000, break_on_termchar='\r\n')
# inst.timeout = 2000

# sleep(2)
# inst.write('*VOLT?')
# sleep(2)
# print(inst.read())
# # inst.write('*RST')
# #sleep(2)
# inst.write('VOLT 4')
# sleep(2)
# # inst.write('OPON 1')
# # sleep(2)
# inst.write("*IDN?")
# sleep(2)#
# print(inst.read())
# # sleep(2)
# # #print(inst.read())

#print(inst.query('*IDN?'))
# inst.close()
