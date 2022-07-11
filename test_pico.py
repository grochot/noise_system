import pyvisa
rm = pyvisa.ResourceManager()

# print(rm.list_resources())

inst = rm.open_resource('USB0::0x0AAD::0x0135::032163928::INSTR')
inst.write("INST:NSEL 1")
inst.write("OUTP 1")
inst.write("INST:NSEL 2")
inst.write("OUTP 0")
inst.write("INST:NSEL 3")
inst.write("OUTP 0")
inst.write('VOLT 0.3')